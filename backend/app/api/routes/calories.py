"""Calorie expenditure prediction endpoint."""

from typing import Any

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureRequest
from backend.app.core.container import ContainerDep

router = APIRouter()


@router.post("/calorie-expenditure/predict")
async def predict_calorie_expenditure(
    request: CalorieExpenditureRequest,
    container: ContainerDep,
) -> dict[str, Any]:
    response = await run_in_threadpool(container.calorie_agent.predict, request)
    return response.model_dump()
