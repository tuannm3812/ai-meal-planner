"""Domain exceptions and the handlers that map them to HTTP responses."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class MealPlanningError(Exception):
    """Base class for failures the API can describe to a client.

    Args:
        *args: Positional arguments forwarded to ``Exception``. The first
            argument is conventionally the internal detail, which is safe to
            log but must never be echoed back to a client verbatim.
    """

    status_code = 500
    client_message = "Meal plan generation failed. Please try again."
    # A stable, machine-readable code for clients, returned as "code" when set.
    error_code: str | None = None
    # Extra response headers, for example Retry-After on a rate-limited request.
    headers: dict[str, str] = {}  # noqa: RUF012 - read-only class default


class ProfileNotFound(MealPlanningError):
    """Raised when a requested user profile does not exist."""

    status_code = 404
    client_message = "No profile found for that user."


class RetrievalUnavailable(MealPlanningError):
    """Raised when the meal retrieval index cannot serve a query."""

    status_code = 503
    client_message = "Meal retrieval is temporarily unavailable. Please try again shortly."


class NutritionProviderError(MealPlanningError):
    """Raised when verified nutrition is required but cannot be met.

    This is G3's ``unverified_required`` outcome: ``REQUIRE_VERIFIED_NUTRITION``
    is on and at least one ingredient could only be estimated, because no
    provider is configured or every configured provider failed for it.
    """

    status_code = 502
    client_message = "Nutrition verification is temporarily unavailable."
    error_code = "unverified_required"


class NoFeasibleMeal(MealPlanningError):
    """Raised when no meal can satisfy the request's hard constraints.

    Serving a meal that breaks an allergy or a health condition is worse than
    serving none, so the agent refuses instead. An interim contract: the G3
    production-readiness work plans to report this as ``plan_status:
    infeasible`` on a successful response.
    """

    status_code = 422
    client_message = (
        "No meal satisfies these dietary and health constraints. "
        "Try relaxing a preference or changing the craving."
    )


class AuthenticationRequired(MealPlanningError):
    """Raised when keys are configured and the request has no valid key (G4)."""

    status_code = 401
    client_message = "A valid X-API-Key header is required."
    error_code = "missing_or_invalid_api_key"


class InsufficientScope(MealPlanningError):
    """Raised when the key is valid but lacks the route's scope (G4)."""

    status_code = 403
    client_message = "This API key is not allowed to perform this operation."
    error_code = "insufficient_scope"


class RateLimited(MealPlanningError):
    """Raised when a client exceeds its per-instance request limit (G4)."""

    status_code = 429
    client_message = "Too many requests. Retry after the time in the Retry-After header."
    error_code = "rate_limited"

    def __init__(self, detail: str, retry_after: float) -> None:
        """Record when the client may retry.

        Args:
            detail: Internal detail for the log.
            retry_after: Seconds until the client's window resets.
        """
        super().__init__(detail)
        self.headers = {"Retry-After": str(max(1, round(retry_after)))}


class MealPlanNotFound(MealPlanningError):
    """Raised when feedback references a plan the caller does not own (G4).

    Deliberately indistinguishable from a request_id that never existed, so it
    reveals nothing about other clients' plans.
    """

    status_code = 404
    client_message = "No meal plan with that request_id exists for this client."
    error_code = "meal_not_found"


class HistoryDisabled(MealPlanningError):
    """Raised for history and feedback routes on a hosted deployment (G6).

    A hosted deployment runs several instances, each with its own SQLite file,
    so history written on one would be invisible on another. Rather than offer
    reads that cannot be described honestly, hosted mode refuses them.
    """

    status_code = 501
    client_message = (
        "History and feedback are disabled on this hosted deployment, which keeps "
        "no state between requests."
    )
    error_code = "history_disabled_stateless"


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the domain exception handlers to an app.

    Args:
        app: The FastAPI application to register handlers on.
    """

    @app.exception_handler(MealPlanningError)
    async def _handle_domain_error(request: Request, exc: MealPlanningError) -> JSONResponse:
        # The internal string goes to logs; the client gets the safe message only.
        logger.warning("%s on %s: %s", type(exc).__name__, request.url.path, exc)
        content = {"status": "error", "error": type(exc).__name__}
        if exc.error_code:
            content["code"] = exc.error_code
        content["detail"] = exc.client_message
        return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "InternalServerError",
                "detail": "An unexpected error occurred.",
            },
        )
