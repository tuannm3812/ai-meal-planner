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
        return JSONResponse(status_code=exc.status_code, content=content)

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
