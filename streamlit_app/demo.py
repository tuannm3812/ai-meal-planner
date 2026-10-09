"""Self-contained demo-mode request routing for the Streamlit app.

Runs the same agents and orchestrator as the FastAPI service, so the deployed
Streamlit demo works end to end with no backend process and no paid API keys.
"""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from config import get_bool_secret, get_secret

DEMO_DATA_DIR = Path("/tmp/ai_meal_planner") if os.getenv("STREAMLIT_SHARING") else Path("database")
DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)


class StreamlitUserProfileRepository:
    def __init__(
        self,
        age: int,
        sex: str,
        height_cm: float,
        weight_kg: float,
        activity_multiplier: float,
        dietary_restrictions: list[str],
    ):
        self.profile = {
            "age": age,
            "gender": "m" if sex.lower().startswith("male") else "f",
            "height": height_cm,
            "weight": weight_kg,
            "workout_level": activity_multiplier,
            "dietary_restrictions": dietary_restrictions,
        }

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        return self.profile


def local_demo_request(
    path: str,
    payload: dict[str, Any] | None,
    profile: dict[str, Any],
    api_key: str = "",
) -> dict[str, Any]:
    payload = payload or {}
    if path == "/health":
        return {
            "status": "ok",
            "environment": "streamlit_demo",
            "services": {
                "mode": "self_contained_streamlit",
                "gemini_configured": bool(api_key),
                "usda_configured": bool(get_secret("USDA_API_KEY")),
                "fatsecret_configured": bool(get_secret("FATSECRET_CLIENT_ID"))
                and bool(get_secret("FATSECRET_CLIENT_SECRET")),
                "calorie_model_configured": Path(
                    "models/calorie_expenditure/calorie_expenditure_model.joblib"
                ).exists(),
                "rag_backend": "lazy_loaded_local",
            },
        }

    # Deferred, not module-top: app.py adds the repo root to sys.path only after
    # importing this module, so a top-level `backend` import here could work under
    # pytest and `uv run` (where the project is installed and already on
    # sys.path) but fail on Streamlit Cloud, where app.py's bootstrap runs first.
    try:
        from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
        from backend.app.agents.supermarket_agent import SupermarketAgent
        from backend.app.repositories.base import LOCAL_CLIENT_ID
        from backend.app.repositories.json_store import MealFeedbackRepository, MealPlanRepository
    except ImportError as exc:
        raise RuntimeError(f"Local demo mode cannot import backend storage modules: {exc}") from exc

    user_repository = StreamlitUserProfileRepository(
        age=int(profile["age"]),
        sex=str(profile["sex"]),
        height_cm=float(profile["height_cm"]),
        weight_kg=float(profile["weight_kg"]),
        activity_multiplier=float(profile["activity_multiplier"]),
        dietary_restrictions=profile["dietary_restrictions"],
    )

    if path == "/generate-meal-plan":
        try:
            # Deferred for the same sys.path reason as the block above.
            from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureAgent
            from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
            from backend.app.schemas.requests import MealRequest
            from backend.app.services.meal_planning_service import MealPlanningService
        except ImportError as exc:
            raise RuntimeError(f"Local demo mode cannot import meal agent: {exc}") from exc

        request_id = str(uuid4())
        meal_agent = MealRecommendationAgent(
            db_connection=user_repository,
            gemini_api_key=api_key or None,
            meal_corpus_path=Path("data/meal_corpus/meals.json"),
            enable_llm_adaptation=get_bool_secret("ENABLE_GEMINI_ADAPTATION"),
        )
        nutrition_agent = NutritionVerificationAgent(
            usda_api_key=get_secret("USDA_API_KEY") or None,
            fatsecret_client_id=get_secret("FATSECRET_CLIENT_ID") or None,
            fatsecret_client_secret=get_secret("FATSECRET_CLIENT_SECRET") or None,
            require_verified=get_bool_secret("REQUIRE_VERIFIED_NUTRITION"),
        )
        supermarket_agent = SupermarketAgent()
        calorie_agent = CalorieExpenditureAgent(
            model_path=Path("models/calorie_expenditure/calorie_expenditure_model.joblib"),
            model_version=get_secret("CALORIE_MODEL_VERSION", "hist_gradient_boosting_deep_v0.1.0"),
        )
        # Demo mode runs the same orchestrator as the API, so the two cannot drift.
        service = MealPlanningService(
            meal_agent=meal_agent,
            nutrition_agent=nutrition_agent,
            supermarket_agent=supermarket_agent,
            calorie_agent=calorie_agent,
            profile_repo=user_repository,
        )
        result = service.generate(
            MealRequest(
                craving=payload["craving"],
                user_id=payload.get("user_id", "user_123"),
                location=payload.get("location", "Earlwood, NSW"),
                health_conditions=payload.get("health_conditions", []),
                dietary_preferences=payload.get("dietary_preferences", []),
            )
        )
        # Mirrors the API's MealPlanResponse, including plan_status; on
        # "infeasible" the meal sections are None and nothing is saved.
        response = {
            "status": "success",
            "request_id": request_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "request": payload,
            **result.model_dump(),
        }
        if result.plan_status != "infeasible":
            MealPlanRepository(DEMO_DATA_DIR).save(response, client_id=LOCAL_CLIENT_ID)
        return response

    if path == "/calorie-expenditure/predict":
        try:
            # Deferred for the same sys.path reason as the block above.
            from backend.app.agents.calorie_expenditure_agent import (
                CalorieExpenditureAgent,
                CalorieExpenditureRequest,
            )
        except ImportError as exc:
            raise RuntimeError(f"Local demo mode cannot import calorie agent: {exc}") from exc

        agent = CalorieExpenditureAgent(
            model_path=Path("models/calorie_expenditure/calorie_expenditure_model.joblib"),
            model_version="hist_gradient_boosting_deep_v0.1.0",
        )
        request = CalorieExpenditureRequest.model_validate(payload)
        return agent.predict(request).model_dump()

    if path == "/meal-feedback":
        record = MealFeedbackRepository(DEMO_DATA_DIR).save(payload, client_id=LOCAL_CLIENT_ID)
        return {"status": "success", "item": record}

    if path.startswith("/meal-plans/"):
        user_id = path.split("/", 2)[2].split("?", 1)[0]
        return {
            "user_id": user_id,
            "items": MealPlanRepository(DEMO_DATA_DIR).list_for_user(
                user_id=user_id, client_id=LOCAL_CLIENT_ID
            ),
        }

    if path.startswith("/saved-meals/"):
        user_id = path.split("/", 2)[2].split("?", 1)[0]
        return {
            "user_id": user_id,
            "items": MealFeedbackRepository(DEMO_DATA_DIR).list_for_user(
                user_id=user_id,
                saved_only=True,
                client_id=LOCAL_CLIENT_ID,
            ),
        }

    raise ValueError(f"Unsupported local demo path: {path}")
