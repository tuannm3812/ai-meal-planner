import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import uuid4

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureRequest
from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.core.config import AppSettings
from backend.app.core.container import Container, build_container, get_container
from backend.app.core.exceptions import register_exception_handlers
from backend.app.schemas.requests import MealFeedbackRequest, MealRequest
from backend.app.services.meal_planning_service import MealPlanningService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


settings = AppSettings.from_env()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the container once at startup and expose it on app state."""
    app.state.container = build_container(settings)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

ContainerDep = Annotated[Container, Depends(get_container)]
"""Injects the request-scoped view of the application's built container."""


@app.get("/")
async def root() -> dict[str, Any]:
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
async def health_check(container: ContainerDep) -> dict[str, Any]:
    return {
        "status": "ok",
        "environment": settings.environment,
        "services": {
            "gemini_configured": bool(settings.gemini_api_key),
            "usda_configured": bool(settings.usda_api_key),
            "fatsecret_configured": bool(
                settings.fatsecret_client_id and settings.fatsecret_client_secret
            ),
            "history_store": str(container.meal_history.history_path),
            "feedback_store": str(container.meal_feedback.feedback_path),
            "calorie_model_configured": bool(container.calorie_agent.model),
            "calorie_model_path": str(settings.calorie_model_path),
            "calorie_model_warning": container.calorie_agent.model_warning,
            "rag_backend": container.meal_agent.meal_retriever.active_backend
            if container.meal_agent.meal_retriever
            else "unavailable",
            "gemini_adaptation_enabled": settings.enable_gemini_adaptation,
        },
    }


@app.post("/generate-meal-plan")
async def generate_meal_plan(
    request: MealRequest,
    container: ContainerDep,
    x_gemini_api_key: str | None = Header(default=None),
) -> dict[str, Any]:
    request_id = str(uuid4())
    generated_at = datetime.now(UTC).isoformat()

    service = container.meal_planning_service
    if x_gemini_api_key and not settings.gemini_api_key:
        # Reuse the already-built retriever instead of re-embedding the corpus.
        service = MealPlanningService(
            meal_agent=MealRecommendationAgent(
                db_connection=container.user_profiles,
                gemini_api_key=x_gemini_api_key,
                meal_retriever=container.meal_agent.meal_retriever,
                enable_llm_adaptation=settings.enable_gemini_adaptation,
            ),
            nutrition_agent=container.nutrition_agent,
            supermarket_agent=container.supermarket_agent,
            calorie_agent=container.calorie_agent,
            profile_repo=container.user_profiles,
        )

    result = await run_in_threadpool(service.generate, request)

    response = {
        "status": "success",
        "request_id": request_id,
        "generated_at": generated_at,
        "request": request.model_dump(),
        "calorie_budget": result.calorie_budget.model_dump(),
        "meal_plan": result.meal_plan.model_dump(),
        "nutrition": result.nutrition.model_dump(),
        "shopping_list": result.shopping_list.model_dump(),
        "reconciliation": (result.reconciliation.model_dump() if result.reconciliation else None),
    }
    await run_in_threadpool(container.meal_history.save, response)
    return response


@app.post("/calorie-expenditure/predict")
async def predict_calorie_expenditure(
    request: CalorieExpenditureRequest,
    container: ContainerDep,
) -> dict[str, Any]:
    response = await run_in_threadpool(container.calorie_agent.predict, request)
    return response.model_dump()


@app.get("/meal-plans/{user_id}")
async def list_meal_plans(
    user_id: str,
    container: ContainerDep,
    limit: int = 20,
) -> dict[str, Any]:
    safe_limit = max(1, min(limit, 50))
    items = await run_in_threadpool(
        container.meal_history.list_for_user, user_id=user_id, limit=safe_limit
    )
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": items,
    }


@app.post("/meal-feedback")
async def save_meal_feedback(
    request: MealFeedbackRequest,
    container: ContainerDep,
) -> dict[str, Any]:
    if request.liked is None and request.rating is None and not request.saved:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one feedback signal: liked, rating, or saved.",
        )

    record = await run_in_threadpool(container.meal_feedback.save, request.model_dump())
    return {
        "status": "success",
        "item": record,
    }


@app.get("/meal-feedback/{user_id}")
async def list_meal_feedback(
    user_id: str,
    container: ContainerDep,
    limit: int = 20,
) -> dict[str, Any]:
    safe_limit = max(1, min(limit, 100))
    items = await run_in_threadpool(
        container.meal_feedback.list_for_user, user_id=user_id, limit=safe_limit
    )
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": items,
    }


@app.get("/saved-meals/{user_id}")
async def list_saved_meals(
    user_id: str,
    container: ContainerDep,
    limit: int = 20,
) -> dict[str, Any]:
    safe_limit = max(1, min(limit, 100))
    items = await run_in_threadpool(
        container.meal_feedback.list_for_user,
        user_id=user_id,
        limit=safe_limit,
        saved_only=True,
    )
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": items,
    }


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
