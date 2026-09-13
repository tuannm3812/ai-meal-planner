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


class ProfileNotFound(MealPlanningError):
    """Raised when a requested user profile does not exist."""

    status_code = 404
    client_message = "No profile found for that user."


class RetrievalUnavailable(MealPlanningError):
    """Raised when the meal retrieval index cannot serve a query."""

    status_code = 503
    client_message = "Meal retrieval is temporarily unavailable. Please try again shortly."


class NutritionProviderError(MealPlanningError):
    """Raised when every nutrition provider fails for an ingredient."""

    status_code = 502
    client_message = "Nutrition verification is temporarily unavailable."


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the domain exception handlers to an app.

    Args:
        app: The FastAPI application to register handlers on.
    """

    @app.exception_handler(MealPlanningError)
    async def _handle_domain_error(request: Request, exc: MealPlanningError) -> JSONResponse:
        # The internal string goes to logs; the client gets the safe message only.
        logger.warning("%s on %s: %s", type(exc).__name__, request.url.path, exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error": type(exc).__name__,
                "detail": exc.client_message,
            },
        )

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
