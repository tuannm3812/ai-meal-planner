import logging
from datetime import UTC, datetime
from typing import Any, Dict
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from .agents.calorie_expenditure_agent import (
        CalorieExpenditureAgent,
        CalorieExpenditureRequest,
    )
    from .agents.meal_recommendation_agent import MealRecommendationAgent
    from .agents.nutrition_verification_agent import NutritionVerificationAgent
    from .agents.supermarket_agent import SupermarketAgent
    from .core.config import AppSettings
    from .repositories.storage import (
        MealFeedbackRepository,
        MealPlanRepository,
        UserProfileRepository,
    )
    from .schemas.requests import MealFeedbackRequest, MealRequest
except ImportError:
    from backend.app.agents.calorie_expenditure_agent import (
        CalorieExpenditureAgent,
        CalorieExpenditureRequest,
    )
    from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
    from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
    from backend.app.agents.supermarket_agent import SupermarketAgent
    from backend.app.core.config import AppSettings
    from backend.app.repositories.storage import (
        MealFeedbackRepository,
        MealPlanRepository,
        UserProfileRepository,
    )
    from backend.app.schemas.requests import MealFeedbackRequest, MealRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


settings = AppSettings.from_env()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_profiles = UserProfileRepository(settings.data_dir)
meal_history = MealPlanRepository(settings.data_dir)
meal_feedback = MealFeedbackRepository(settings.data_dir)
meal_recommendation_agent = MealRecommendationAgent(
    db_connection=user_profiles,
    gemini_api_key=settings.gemini_api_key,
    meal_corpus_path=settings.meal_corpus_path,
    enable_llm_adaptation=settings.enable_gemini_adaptation,
    rag_backend=settings.rag_backend,
    rag_embedding_cache_dir=settings.rag_embedding_cache_dir,
    rag_embedding_activation_size=settings.rag_embedding_activation_size,
)
nutrition_verification_agent = NutritionVerificationAgent(
    usda_api_key=settings.usda_api_key,
    fatsecret_client_id=settings.fatsecret_client_id,
    fatsecret_client_secret=settings.fatsecret_client_secret,
)
supermarket_agent = SupermarketAgent(
    maps_api_key=settings.maps_api_key,
    inventory_api_key=settings.inventory_api_key,
)
calorie_expenditure_agent = CalorieExpenditureAgent(
    model_path=settings.calorie_model_path,
    model_version=settings.calorie_model_version,
)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "name": settings.app_name,
        "status": "ok",
        "message": "AI Meal Planner API is running. Open /docs for interactive API docs.",
        "links": {
            "health": "/health",
            "docs": "/docs",
            "meal_plan": "/generate-meal-plan",
            "calorie_prediction": "/calorie-expenditure/predict",
            "meal_history": "/meal-plans/{user_id}",
            "meal_feedback": "/meal-feedback",
            "saved_meals": "/saved-meals/{user_id}",
        },
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "environment": settings.environment,
        "services": {
            "gemini_configured": bool(settings.gemini_api_key),
            "usda_configured": bool(settings.usda_api_key),
            "fatsecret_configured": bool(
                settings.fatsecret_client_id and settings.fatsecret_client_secret
            ),
            "history_store": str(meal_history.history_path),
            "feedback_store": str(meal_feedback.feedback_path),
            "calorie_model_configured": bool(calorie_expenditure_agent.model),
            "calorie_model_path": str(settings.calorie_model_path),
            "calorie_model_warning": calorie_expenditure_agent.model_warning,
            "rag_backend": meal_recommendation_agent.meal_retriever.active_backend
            if meal_recommendation_agent.meal_retriever
            else "unavailable",
            "gemini_adaptation_enabled": settings.enable_gemini_adaptation,
        },
    }


@app.post("/generate-meal-plan")
async def generate_meal_plan(
    request: MealRequest,
    x_gemini_api_key: str | None = Header(default=None),
) -> Dict[str, Any]:
    request_id = str(uuid4())
    generated_at = datetime.now(UTC).isoformat()

    try:
        active_meal_agent = meal_recommendation_agent
        if x_gemini_api_key and not settings.gemini_api_key:
            active_meal_agent = MealRecommendationAgent(
                db_connection=user_profiles,
                gemini_api_key=x_gemini_api_key,
                meal_corpus_path=settings.meal_corpus_path,
                enable_llm_adaptation=settings.enable_gemini_adaptation,
                rag_backend=settings.rag_backend,
                rag_embedding_cache_dir=settings.rag_embedding_cache_dir,
                rag_embedding_activation_size=settings.rag_embedding_activation_size,
            )

        meal_payload = active_meal_agent.generate_meal_payload(
            craving=request.craving.strip(),
            user_id=request.user_id.strip(),
            health_conditions=request.health_conditions,
            dietary_preferences=request.dietary_preferences,
        )
        nutrition_payload = nutrition_verification_agent.calculate_meal_macros(
            ingredients=meal_payload.meal_definition.ingredients,
        )
        supermarket_payload = supermarket_agent.generate_shopping_list(
            ingredients=meal_payload.meal_definition.ingredients,
            user_location=request.location.strip(),
        )

        response = {
            "status": "success",
            "request_id": request_id,
            "generated_at": generated_at,
            "request": request.model_dump(),
            "meal_plan": meal_payload.model_dump(),
            "nutrition": nutrition_payload.model_dump(),
            "shopping_list": supermarket_payload.model_dump(),
        }
        meal_history.save(response)
        return response
    except Exception as exc:
        logger.exception("Meal plan generation failed for request %s", request_id)
        raise HTTPException(status_code=500, detail=f"Meal plan generation failed: {exc}") from exc


@app.post("/calorie-expenditure/predict")
async def predict_calorie_expenditure(request: CalorieExpenditureRequest) -> Dict[str, Any]:
    return calorie_expenditure_agent.predict(request).model_dump()


@app.get("/meal-plans/{user_id}")
async def list_meal_plans(user_id: str, limit: int = 20) -> Dict[str, Any]:
    safe_limit = max(1, min(limit, 50))
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": meal_history.list_for_user(user_id=user_id, limit=safe_limit),
    }


@app.post("/meal-feedback")
async def save_meal_feedback(request: MealFeedbackRequest) -> Dict[str, Any]:
    if request.liked is None and request.rating is None and not request.saved:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one feedback signal: liked, rating, or saved.",
        )

    record = meal_feedback.save(request.model_dump())
    return {
        "status": "success",
        "item": record,
    }


@app.get("/meal-feedback/{user_id}")
async def list_meal_feedback(user_id: str, limit: int = 20) -> Dict[str, Any]:
    safe_limit = max(1, min(limit, 100))
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": meal_feedback.list_for_user(user_id=user_id, limit=safe_limit),
    }


@app.get("/saved-meals/{user_id}")
async def list_saved_meals(user_id: str, limit: int = 20) -> Dict[str, Any]:
    safe_limit = max(1, min(limit, 100))
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": meal_feedback.list_for_user(
            user_id=user_id,
            limit=safe_limit,
            saved_only=True,
        ),
    }


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
