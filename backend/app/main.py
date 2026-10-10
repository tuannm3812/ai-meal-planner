"""FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import calories, feedback, health, meal_plans
from backend.app.core.config import AppSettings
from backend.app.core.container import build_container
from backend.app.core.exceptions import register_exception_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = AppSettings.from_env()

INSTANCE_ID = str(uuid4())
"""Random per-process id, returned as X-Instance-Id (G6).

Lets a client tell which instance answered when one URL is spread across
several, as on Cloud Run. It is random, so it reveals no host name, IP or other
environment detail."""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the container once at startup and expose it on app state."""
    app.state.container = build_container(settings)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)


@app.middleware("http")
async def _instance_id_header(request: Request, call_next: Any) -> Response:
    """Stamp every response with this process's INSTANCE_ID.

    Args:
        request: The incoming request.
        call_next: The rest of the application.

    Returns:
        The response, with X-Instance-Id set.
    """
    response = await call_next(request)
    response.headers["X-Instance-Id"] = INSTANCE_ID
    return response


app.include_router(health.router)
app.include_router(meal_plans.router)
app.include_router(calories.router)
app.include_router(feedback.router)


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
