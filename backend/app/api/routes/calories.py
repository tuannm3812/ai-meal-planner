"""Calorie expenditure prediction endpoint."""

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from backend.app.agents.calorie_expenditure_agent import (
    CalorieExpenditureRequest,
    CalorieExpenditureResponse,
)
from backend.app.api.auth import PlansWrite
from backend.app.core.container import ContainerDep

router = APIRouter()


@router.post("/calorie-expenditure/predict", response_model=CalorieExpenditureResponse)
async def predict_calorie_expenditure(
    request: CalorieExpenditureRequest,
    container: ContainerDep,
    principal: PlansWrite,
) -> CalorieExpenditureResponse:
    """Predict daily energy expenditure and the resulting meal calorie budget.

    Args:
        request: The user's biometrics and activity level.
        container: The application's dependency container.
        principal: The authenticated client; required for the plans:write scope.

    Returns:
        The predicted expenditure, meal calorie budget, and model metadata.
    """
    return await run_in_threadpool(container.calorie_agent.predict, request)
