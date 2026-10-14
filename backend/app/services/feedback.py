"""Feedback rules shared by the API route and the in-process Streamlit demo.

Both save meal feedback, and both must apply the same rules. The demo used to
save any payload straight to its repository (Codex, 2026-10-12); now both
callers go through ``record_feedback``.
"""

from typing import Any

from backend.app.core.exceptions import FeedbackSignalRequired, MealPlanNotFound
from backend.app.repositories.base import MealFeedbackStore, MealPlanStore
from backend.app.schemas.requests import MealFeedbackRequest


def record_feedback(
    feedback: MealFeedbackRequest,
    *,
    meal_history: MealPlanStore,
    meal_feedback: MealFeedbackStore,
    client_id: str,
) -> dict[str, Any]:
    """Validate one feedback record against the client's own plans, then save it.

    Args:
        feedback: The validated feedback body.
        meal_history: The client's stored meal plans.
        meal_feedback: Where feedback is saved.
        client_id: The namespace to read plans from and write feedback to.

    Returns:
        The saved feedback record.

    Raises:
        FeedbackSignalRequired: 400 when none of liked, rating or saved is given.
        MealPlanNotFound: 404 when the client has no plan with that request_id.
    """
    if feedback.liked is None and feedback.rating is None and not feedback.saved:
        raise FeedbackSignalRequired("feedback with no liked, rating or saved")
    if meal_history.find_by_request_id(feedback.request_id, client_id=client_id) is None:
        raise MealPlanNotFound(f"client {client_id!r} has no plan {feedback.request_id!r}")
    return meal_feedback.save(feedback.model_dump(), client_id=client_id)
