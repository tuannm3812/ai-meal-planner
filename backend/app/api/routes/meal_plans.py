"""Meal plan generation and history endpoints."""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Header
from fastapi.concurrency import run_in_threadpool

from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.core.container import ContainerDep
from backend.app.schemas.requests import MealRequest
from backend.app.schemas.responses import MealPlanListResponse, MealPlanResponse
from backend.app.services.meal_planning_service import MealPlanningService

router = APIRouter()


@router.post("/generate-meal-plan", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: MealRequest,
    container: ContainerDep,
    x_gemini_api_key: str | None = Header(default=None),
) -> MealPlanResponse:
    """Generate a meal plan, verify its nutrition, and price a shopping list.

    Args:
        request: The craving, dietary constraints, and optional biometrics.
        container: The application's dependency container.
        x_gemini_api_key: An optional per-request Gemini key that overrides
            the server's own configuration when the server has none.

    Returns:
        The assembled meal plan response, which is also persisted to history.
    """
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

    response = MealPlanResponse(
        status="success",
        request_id=request_id,
        generated_at=generated_at,
        request=request.model_dump(),
        calorie_budget=result.calorie_budget,
        meal_plan=result.meal_plan,
        nutrition=result.nutrition,
        shopping_list=result.shopping_list,
        reconciliation=result.reconciliation,
    )
    await run_in_threadpool(container.meal_history.save, response.model_dump())
    return response


@router.get("/meal-plans/{user_id}", response_model=MealPlanListResponse)
async def list_meal_plans(
    user_id: str,
    container: ContainerDep,
    limit: int = 20,
) -> MealPlanListResponse:
    """List stored meal plans for one user, most recent first.

    Args:
        user_id: The user whose meal-plan history to fetch.
        container: The application's dependency container.
        limit: Requested page size, clamped to the range [1, 50].

    Returns:
        The clamped limit and the matching stored meal-plan records.
    """
    safe_limit = max(1, min(limit, 50))
    items = await run_in_threadpool(
        container.meal_history.list_for_user, user_id=user_id, limit=safe_limit
    )
    return MealPlanListResponse(
        user_id=user_id,
        limit=safe_limit,
        items=items,
    )
