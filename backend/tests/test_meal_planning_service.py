"""Tests for the meal planning orchestrator."""

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureAgent
from backend.app.agents.meal_recommendation_agent import (
    MealDefinition,
    MealPlanPayload,
    MealRecommendationAgent,
    PortionScalingMetadata,
    UserContext,
)
from backend.app.agents.nutrition_verification_agent import (
    MealNutrition,
    NutritionVerificationAgent,
)
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.core.config import AppSettings
from backend.app.repositories.json_store import UserProfileRepository
from backend.app.schemas.common import AgentMetadata, MealAgentMetadata
from backend.app.schemas.requests import Ingredient, MealRequest
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


def test_reconciliation_metadata_is_always_reported() -> None:
    """Every plan reports how the estimate compared with verified nutrition."""
    result = _service().generate(MealRequest(craving="high-protein burger"))
    rec = result.reconciliation
    assert rec is not None
    assert rec.tolerance == 0.15
    assert rec.target_meal_calories > 0
    assert rec.verified_calories_before > 0
    assert rec.deviation_before >= 0


def test_reconciliation_retries_at_most_once() -> None:
    """A rescale happens at most one time, never in a loop."""
    result = _service().generate(MealRequest(craving="pasta"))
    rec = result.reconciliation
    assert rec is not None
    if rec.rescaled:
        assert rec.verified_calories_after is not None
        assert rec.deviation_after is not None
        # One retry only: after-values exist, and no third figure is reported.
        assert rec.deviation_after <= rec.deviation_before
    else:
        assert rec.verified_calories_after is None
        assert rec.within_tolerance is True


def test_reconciliation_rescale_moves_nutrition_toward_the_target() -> None:
    """When a rescale happens, the returned nutrition reflects the rescaled portions."""
    result = _service().generate(MealRequest(craving="high-protein burger"))
    rec = result.reconciliation
    assert rec is not None
    if rec.rescaled:
        assert result.nutrition.total_calories == rec.verified_calories_after


def test_reconciliation_reports_the_compounded_scale_factor() -> None:
    """After a rescale, scale_factor must report both stages, not just the first.

    The meal agent's first-stage factor alone understates the true scaling once
    reconciliation rescales a second time; the reported figure must be the
    product of both stages.
    """

    class _StubNutritionAgent:
        """Always reports the same verified nutrition, for a deterministic rescale."""

        def calculate_meal_macros(self, ingredients: list[Ingredient]) -> MealNutrition:
            return MealNutrition(
                ingredients_macros=[],
                total_calories=950.0,
                total_protein=60.0,
                total_carbs=80.0,
                total_fat=30.0,
                metadata=AgentMetadata(agent_name="stub", source="stub", confidence=1.0),
            )

    service = MealPlanningService(
        meal_agent=None,
        nutrition_agent=_StubNutritionAgent(),
        supermarket_agent=None,
        calorie_agent=None,
        profile_repo=None,
    )

    original_scale_factor = 1.6
    meal_plan = MealPlanPayload(
        user_context=UserContext(caloric_target=2000, dietary_restrictions=[]),
        meal_definition=MealDefinition(
            craving_input="burger",
            structured_meal_name="Burger",
            ingredients=[Ingredient(item_name="beef patty", base_quantity_grams=200)],
        ),
        metadata=MealAgentMetadata(agent_name="meal", source="template", confidence=0.9),
        portion_scaling=PortionScalingMetadata(
            target_meal_calories=1200,
            estimated_template_calories=750.0,
            scale_factor=original_scale_factor,
        ),
    )
    verified_calories_before = 1000.0
    nutrition_before = MealNutrition(
        ingredients_macros=[],
        total_calories=verified_calories_before,
        total_protein=50.0,
        total_carbs=70.0,
        total_fat=20.0,
        metadata=AgentMetadata(agent_name="nutrition", source="stub", confidence=1.0),
    )

    updated_plan, _updated_nutrition, rec = service._reconcile(meal_plan, nutrition_before)

    assert rec is not None
    assert rec.rescaled is True
    expected_factor = max(0.65, min(1.6, rec.target_meal_calories / verified_calories_before))
    expected_scale_factor = round(original_scale_factor * expected_factor, 2)
    assert updated_plan.portion_scaling is not None
    assert updated_plan.portion_scaling.scale_factor == expected_scale_factor
    # PortionScalingMetadata.scale_factor has gt=0 validation; confirm the
    # compounded value still satisfies it.
    assert updated_plan.portion_scaling.scale_factor > 0
