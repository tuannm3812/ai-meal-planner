"""Meal plan generation and history endpoints."""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from backend.app.api.auth import HistoryEnabled, HistoryRead, PlansWrite
from backend.app.core.container import ContainerDep
from backend.app.schemas.requests import MealRequest
from backend.app.schemas.responses import MealPlanListResponse, MealPlanResponse

router = APIRouter()


@router.post("/generate-meal-plan", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: MealRequest,
    container: ContainerDep,
    principal: PlansWrite,
) -> MealPlanResponse:
    """Generate a meal plan, verify its nutrition, and price a shopping list.

    Provider credentials are server-managed only: the former X-Gemini-Api-Key
    pass-through was removed in G4.

    Args:
        request: The craving, dietary constraints, and optional biometrics.
        container: The application's dependency container.
        principal: The authenticated client; its client_id namespaces history.

    Returns:
        The assembled meal plan response. It is persisted to history unless
        ``plan_status`` is ``infeasible``, which has no meal to keep.
    """
    request_id = str(uuid4())
    generated_at = datetime.now(UTC).isoformat()
    service = container.meal_planning_service

    result = await run_in_threadpool(service.generate, request)

    response = MealPlanResponse(
        status="success",
        plan_status=result.plan_status,
        request_id=request_id,
        generated_at=generated_at,
        request=request.model_dump(),
        calorie_budget=result.calorie_budget,
        meal_plan=result.meal_plan,
        nutrition=result.nutrition,
        shopping_list=result.shopping_list,
        reconciliation=result.reconciliation,
        infeasible_reason=result.infeasible_reason,
    )
    # An infeasible result has no meal to keep, and history views expect one. A
    # hosted deployment keeps nothing: its instances share no storage (G6).
    if result.plan_status != "infeasible" and not container.settings.hosted_mode:
        await run_in_threadpool(
            container.meal_history.save, response.model_dump(), client_id=principal.client_id
        )
    return response


@router.get("/meal-plans/{user_id}", response_model=MealPlanListResponse)
async def list_meal_plans(
    user_id: str,
    container: ContainerDep,
    principal: HistoryRead,
    _history: HistoryEnabled,
    limit: int = 20,
) -> MealPlanListResponse:
    """List stored meal plans for one user, most recent first.

    Only the caller's own namespace is searched, so a guessed ``user_id`` can
    never reach another client's records.

    Args:
        user_id: The user whose meal-plan history to fetch.
        container: The application's dependency container.
        principal: The authenticated client whose namespace is read.
        limit: Requested page size, clamped to the range [1, 50].

    Returns:
        The clamped limit and the matching stored meal-plan records.
    """
    safe_limit = max(1, min(limit, 50))
    items = await run_in_threadpool(
        container.meal_history.list_for_user,
        user_id=user_id,
        limit=safe_limit,
        client_id=principal.client_id,
    )
    return MealPlanListResponse(
        user_id=user_id,
        limit=safe_limit,
        items=items,
    )
