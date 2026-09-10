"""Tests for the meal planning orchestrator."""

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureAgent
from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.core.config import AppSettings
from backend.app.repositories.storage import UserProfileRepository
from backend.app.schemas.requests import MealRequest
from backend.app.services.meal_planning_service import MealPlanningService


def _service() -> MealPlanningService:
    settings = AppSettings.from_env()
    return MealPlanningService(
        meal_agent=MealRecommendationAgent(
            db_connection=UserProfileRepository(settings.data_dir),
            meal_corpus_path=settings.meal_corpus_path,
        ),
        nutrition_agent=NutritionVerificationAgent(),
        supermarket_agent=SupermarketAgent(),
        calorie_agent=CalorieExpenditureAgent(
            model_path=settings.calorie_model_path,
            model_version=settings.calorie_model_version,
        ),
        profile_repo=UserProfileRepository(settings.data_dir),
    )


def test_service_uses_calorie_agent_budget_as_the_meal_target() -> None:
    """The meal plan's caloric target must come from the calorie agent, not a local BMR."""
    result = _service().generate(
        MealRequest(user_id="user_123", craving="high-protein burger", location="Earlwood, NSW")
    )

    assert result.calorie_budget.meal_calorie_budget_kcal > 0
    # The meal agent receives the DAILY budget; user_context echoes exactly that.
    assert result.meal_plan.user_context.caloric_target == int(
        round(result.calorie_budget.meal_calorie_budget_kcal)
    )


def test_service_prefers_request_biometrics_over_the_stored_profile() -> None:
    """Explicit biometrics on the request override the stored profile."""
    light = _service().generate(
        MealRequest(
            craving="salad",
            age=25,
            sex="female",
            height_cm=160,
            weight_kg=55,
            activity_multiplier=1.2,
        )
    )
    heavy = _service().generate(
        MealRequest(
            craving="salad",
            age=25,
            sex="male",
            height_cm=195,
            weight_kg=100,
            activity_multiplier=1.9,
        )
    )
    assert heavy.calorie_budget.estimated_daily_expenditure_kcal > (
        light.calorie_budget.estimated_daily_expenditure_kcal
    )


def test_service_goal_shifts_the_budget() -> None:
    """A cutting goal must produce a lower budget than bulking, all else equal."""
    cut = _service().generate(MealRequest(craving="salad", goal="cut"))
    bulk = _service().generate(MealRequest(craving="salad", goal="bulk"))
    assert cut.calorie_budget.meal_calorie_budget_kcal < (
        bulk.calorie_budget.meal_calorie_budget_kcal
    )


def test_service_returns_every_section() -> None:
    """The orchestrator returns all four agent payloads."""
    result = _service().generate(MealRequest(craving="pasta"))
    assert result.meal_plan.meal_definition.ingredients
    assert result.nutrition.total_calories > 0
    assert result.shopping_list.shopping_list
