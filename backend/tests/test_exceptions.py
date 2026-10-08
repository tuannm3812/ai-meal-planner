"""Domain exceptions must map to sane statuses and leak nothing internal."""

import pytest

from backend.app.core.exceptions import (
    MealPlanningError,
    NutritionProviderError,
    ProfileNotFound,
    RetrievalUnavailable,
)


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (ProfileNotFound("nope"), 404),
        (RetrievalUnavailable("index down"), 503),
        (NutritionProviderError("usda timeout"), 502),
        (MealPlanningError("generic"), 500),
    ],
)
def test_status_codes(exc: MealPlanningError, status: int) -> None:
    assert exc.status_code == status


def test_client_message_never_contains_internal_detail() -> None:
    """The message sent to a client must not echo the internal string."""
    exc = NutritionProviderError("postgres://user:password@host/db timed out")
    assert "password" not in exc.client_message
    assert "postgres" not in exc.client_message
    # The internal detail is still available for logs.
    assert "password" in str(exc)
