"""Meal feedback and saved-meals endpoints."""

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from backend.app.api.auth import FeedbackWrite, HistoryEnabled, HistoryRead
from backend.app.api.errors import AUTH_ERRORS, error_responses
from backend.app.core.container import ContainerDep
from backend.app.core.exceptions import FeedbackSignalRequired, HistoryDisabled, MealPlanNotFound
from backend.app.schemas.requests import MealFeedbackRequest
from backend.app.schemas.responses import FeedbackListResponse, FeedbackResponse
from backend.app.services.feedback import record_feedback

router = APIRouter()


@router.post(
    "/meal-feedback",
    response_model=FeedbackResponse,
    responses=error_responses(
        *AUTH_ERRORS, FeedbackSignalRequired, MealPlanNotFound, HistoryDisabled
    ),
)
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
        FeedbackSignalRequired: 400 if none of liked, rating, or saved is provided.
        MealPlanNotFound: 404 if the caller has no plan with that request_id.

    Returns:
        The persisted feedback record.
    """
    # The same rules the in-process Streamlit demo applies (services/feedback.py).
    record = await run_in_threadpool(
        record_feedback,
        request,
        meal_history=container.meal_history,
        meal_feedback=container.meal_feedback,
        client_id=principal.client_id,
    )
    return FeedbackResponse(
        status="success",
        item=record,
    )


@router.get(
    "/meal-feedback/{user_id}",
    response_model=FeedbackListResponse,
    responses=error_responses(*AUTH_ERRORS, HistoryDisabled),
)
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


@router.get(
    "/saved-meals/{user_id}",
    response_model=FeedbackListResponse,
    responses=error_responses(*AUTH_ERRORS, HistoryDisabled),
)
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
