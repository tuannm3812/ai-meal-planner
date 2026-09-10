"""Meal plan generation and history endpoints."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header
from fastapi.concurrency import run_in_threadpool

from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.core.container import ContainerDep
from backend.app.schemas.requests import MealRequest
from backend.app.services.meal_planning_service import MealPlanningService

router = APIRouter()


@router.post("/generate-meal-plan")
async def generate_meal_plan(
    request: MealRequest,
    container: ContainerDep,
    x_gemini_api_key: str | None = Header(default=None),
) -> dict[str, Any]:
    settings = container.settings
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


@router.get("/meal-plans/{user_id}")
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
