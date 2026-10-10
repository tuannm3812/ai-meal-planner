"""Meal feedback and saved-meals endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from backend.app.api.auth import FeedbackWrite, HistoryEnabled, HistoryRead
from backend.app.core.container import ContainerDep
from backend.app.core.exceptions import MealPlanNotFound
from backend.app.schemas.requests import MealFeedbackRequest
from backend.app.schemas.responses import FeedbackListResponse, FeedbackResponse

router = APIRouter()


@router.post("/meal-feedback", response_model=FeedbackResponse)
async def save_meal_feedback(
    request: MealFeedbackRequest,
    container: ContainerDep,
    principal: FeedbackWrite,
    _history: HistoryEnabled,
) -> FeedbackResponse:
    """Persist like/rating/save feedback for a previously generated meal.

    The referenced ``request_id`` must belong to a plan in the caller's own
    namespace, so one client cannot attach feedback to another client's meal.

    Args:
        request: The feedback signal(s) for one meal.
        container: The application's dependency container.
        principal: The authenticated client whose namespace is written.

    Raises:
        HTTPException: 400 if none of liked, rating, or saved is provided.
        MealPlanNotFound: 404 if the caller has no plan with that request_id.

    Returns:
        The persisted feedback record.
    """
    if request.liked is None and request.rating is None and not request.saved:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one feedback signal: liked, rating, or saved.",
        )

    plan = await run_in_threadpool(
        container.meal_history.find_by_request_id,
        request.request_id,
        client_id=principal.client_id,
    )
    if plan is None:
        raise MealPlanNotFound(f"client {principal.client_id!r} has no plan {request.request_id!r}")

    record = await run_in_threadpool(
        container.meal_feedback.save, request.model_dump(), client_id=principal.client_id
    )
    return FeedbackResponse(
        status="success",
        item=record,
    )


@router.get("/meal-feedback/{user_id}", response_model=FeedbackListResponse)
async def list_meal_feedback(
    user_id: str,
    container: ContainerDep,
    principal: HistoryRead,
    _history: HistoryEnabled,
    limit: int = 20,
) -> FeedbackListResponse:
    """List stored feedback records for one user, most recent first.

    Args:
        user_id: The user whose feedback history to fetch.
        container: The application's dependency container.
        principal: The authenticated client whose namespace is read.
        limit: Requested page size, clamped to the range [1, 100].

    Returns:
        The clamped limit and the matching stored feedback records.
    """
    safe_limit = max(1, min(limit, 100))
    items = await run_in_threadpool(
        container.meal_feedback.list_for_user,
        user_id=user_id,
        limit=safe_limit,
        client_id=principal.client_id,
    )
    return FeedbackListResponse(
        user_id=user_id,
        limit=safe_limit,
        items=items,
    )


@router.get("/saved-meals/{user_id}", response_model=FeedbackListResponse)
async def list_saved_meals(
    user_id: str,
    container: ContainerDep,
    principal: HistoryRead,
    _history: HistoryEnabled,
    limit: int = 20,
) -> FeedbackListResponse:
    """List meals the user explicitly saved, most recent first.

    Args:
        user_id: The user whose saved meals to fetch.
        container: The application's dependency container.
        principal: The authenticated client whose namespace is read.
        limit: Requested page size, clamped to the range [1, 100].

    Returns:
        The clamped limit and the matching saved-meal records.
    """
    safe_limit = max(1, min(limit, 100))
    items = await run_in_threadpool(
        container.meal_feedback.list_for_user,
        user_id=user_id,
        limit=safe_limit,
        saved_only=True,
        client_id=principal.client_id,
    )
    return FeedbackListResponse(
        user_id=user_id,
        limit=safe_limit,
        items=items,
    )
