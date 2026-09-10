"""Meal feedback and saved-meals endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from backend.app.core.container import ContainerDep
from backend.app.schemas.requests import MealFeedbackRequest

router = APIRouter()


@router.post("/meal-feedback")
async def save_meal_feedback(
    request: MealFeedbackRequest,
    container: ContainerDep,
) -> dict[str, Any]:
    if request.liked is None and request.rating is None and not request.saved:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one feedback signal: liked, rating, or saved.",
        )

    record = await run_in_threadpool(container.meal_feedback.save, request.model_dump())
    return {
        "status": "success",
        "item": record,
    }


@router.get("/meal-feedback/{user_id}")
async def list_meal_feedback(
    user_id: str,
    container: ContainerDep,
    limit: int = 20,
) -> dict[str, Any]:
    safe_limit = max(1, min(limit, 100))
    items = await run_in_threadpool(
        container.meal_feedback.list_for_user, user_id=user_id, limit=safe_limit
    )
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": items,
    }


@router.get("/saved-meals/{user_id}")
async def list_saved_meals(
    user_id: str,
    container: ContainerDep,
    limit: int = 20,
) -> dict[str, Any]:
    safe_limit = max(1, min(limit, 100))
    items = await run_in_threadpool(
        container.meal_feedback.list_for_user,
        user_id=user_id,
        limit=safe_limit,
        saved_only=True,
    )
    return {
        "user_id": user_id,
        "limit": safe_limit,
        "items": items,
    }
