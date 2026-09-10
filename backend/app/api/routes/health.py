"""Health and root informational endpoints."""

from typing import Any

from fastapi import APIRouter

from backend.app.core.container import ContainerDep

router = APIRouter()


@router.get("/")
async def root(container: ContainerDep) -> dict[str, Any]:
    settings = container.settings
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


@router.get("/health")
async def health_check(container: ContainerDep) -> dict[str, Any]:
    settings = container.settings
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
