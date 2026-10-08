"""Response models, so /docs documents contracts instead of free-form dicts.

``items`` on the list endpoints (``MealPlanListResponse`` and
``FeedbackListResponse``) stays ``list[dict[str, Any]]`` on purpose: history
and feedback records are whole stored responses from earlier versions of the
API, and typing them strictly would make old rows unreadable once the schema
evolves.
"""

from typing import Any

from pydantic import BaseModel

from ..agents.calorie_expenditure_agent import CalorieExpenditureResponse
from ..agents.meal_recommendation_agent import MealPlanPayload
from ..agents.nutrition_verification_agent import MealNutrition
from ..agents.supermarket_agent import SupermarketPayload
from ..services.meal_planning_service import ReconciliationMetadata


class RootResponse(BaseModel):
    """Service banner and endpoint links."""

    name: str
    status: str
    message: str
    links: dict[str, str]


class HealthResponse(BaseModel):
    """Service health and external provider configuration."""

    status: str
    environment: str
    services: dict[str, Any]


class MealPlanResponse(BaseModel):
    """A generated meal plan with its verification and reconciliation metadata."""

    status: str
    request_id: str
    generated_at: str
    request: dict[str, Any]
    calorie_budget: CalorieExpenditureResponse
    meal_plan: MealPlanPayload
    nutrition: MealNutrition
    shopping_list: SupermarketPayload
    reconciliation: ReconciliationMetadata | None = None


class MealPlanListResponse(BaseModel):
    """Stored meal plans for one user."""

    user_id: str
    limit: int
    items: list[dict[str, Any]]


class FeedbackResponse(BaseModel):
    """The persisted feedback record."""

    status: str
    item: dict[str, Any]


class FeedbackListResponse(BaseModel):
    """Feedback or saved meals for one user."""

    user_id: str
    limit: int
    items: list[dict[str, Any]]
