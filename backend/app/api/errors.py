"""Documented error responses, generated from the domain exceptions themselves.

Each entry's status, description and body come from the exception class and
``ErrorResponse``, so the published contract (``docs/openapi.json``) cannot
disagree with what the exception handler sends.
"""

from typing import Any

from backend.app.core.exceptions import (
    AuthenticationRequired,
    InsufficientScope,
    MealPlanningError,
    RateLimited,
)
from backend.app.schemas.responses import ErrorResponse

AUTH_ERRORS = (AuthenticationRequired, InsufficientScope, RateLimited)
"""What every route behind an X-API-Key scope can return."""


def error_responses(*errors: type[MealPlanningError]) -> dict[int | str, dict[str, Any]]:
    """The OpenAPI ``responses`` entries for the domain errors a route can return.

    Args:
        *errors: Domain exception classes, each with a distinct status code.

    Returns:
        A ``responses`` mapping for a route decorator.

    Raises:
        ValueError: When two errors share a status code, which would document
            only one of them.
    """
    responses: dict[int | str, dict[str, Any]] = {}
    for error in errors:
        if error.status_code in responses:
            raise ValueError(f"two documented errors share status {error.status_code}")
        entry: dict[str, Any] = {"model": ErrorResponse, "description": error.client_message}
        if error is RateLimited:
            entry["headers"] = {
                "Retry-After": {
                    "description": "Seconds until this client may retry.",
                    "schema": {"type": "integer"},
                }
            }
        responses[error.status_code] = entry
    return responses
