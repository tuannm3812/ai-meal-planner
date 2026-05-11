import logging
from datetime import UTC, datetime
from typing import Any, Dict
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .agents.calorie_expenditure_agent import (
        CalorieExpenditureAgent,
        CalorieExpenditureRequest,
    )
    from .agents.meal_recommendation_agent import MealRecommendationAgent
    from .agents.nutrition_verification_agent import NutritionVerificationAgent
    from .agents.supermarket_agent import SupermarketAgent
    from .core.config import AppSettings
    from .repositories.storage import MealPlanRepository, UserProfileRepository
except ImportError:
    from backend.app.agents.calorie_expenditure_agent import (
        CalorieExpenditureAgent,
        CalorieExpenditureRequest,
    )
    from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
    from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
    from backend.app.agents.supermarket_agent import SupermarketAgent
    from backend.app.core.config import AppSettings
    from backend.app.repositories.storage import MealPlanRepository, UserProfileRepository


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MealRequest(BaseModel):
    user_id: str = Field(default="user_123", min_length=3, max_length=80)
    craving: str = Field(min_length=2, max_length=180)
    location: str = Field(default="Earlwood, NSW", min_length=2, max_length=160)


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
meal_recommendation_agent = MealRecommendationAgent(
    db_connection=user_profiles,
    gemini_api_key=settings.gemini_api_key,
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
calorie_expenditure_agent = CalorieExpenditureAgent()


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
        },
    }


@app.post("/generate-meal-plan")
async def generate_meal_plan(request: MealRequest) -> Dict[str, Any]:
    request_id = str(uuid4())
    generated_at = datetime.now(UTC).isoformat()

    try:
        meal_payload = meal_recommendation_agent.generate_meal_payload(
            craving=request.craving.strip(),
            user_id=request.user_id.strip(),
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


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
