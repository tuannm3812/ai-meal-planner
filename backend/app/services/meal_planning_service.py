"""Orchestrates the multi-agent meal planning workflow."""

from typing import Any

from pydantic import BaseModel

from ..agents.calorie_expenditure_agent import (
    CalorieExpenditureAgent,
    CalorieExpenditureRequest,
    CalorieExpenditureResponse,
)
from ..agents.meal_recommendation_agent import MealPlanPayload, MealRecommendationAgent
from ..agents.nutrition_verification_agent import MealNutrition, NutritionVerificationAgent
from ..agents.supermarket_agent import SupermarketAgent, SupermarketPayload
from ..repositories.base import UserProfileStore
from ..schemas.requests import Ingredient, MealRequest

DEFAULT_TOLERANCE = 0.15
"""Fractional deviation between the portion estimate and verified nutrition that
is accepted without rescaling."""


class ReconciliationMetadata(BaseModel):
    """Records how the portion estimate compared with verified nutrition."""

    target_meal_calories: int
    verified_calories_before: float
    deviation_before: float
    rescaled: bool
    verified_calories_after: float | None = None
    deviation_after: float | None = None
    within_tolerance: bool
    tolerance: float


class MealPlanResult(BaseModel):
    """Everything the meal-plan endpoint needs, assembled by the orchestrator."""

    calorie_budget: CalorieExpenditureResponse
    meal_plan: MealPlanPayload
    nutrition: MealNutrition
    shopping_list: SupermarketPayload
    reconciliation: ReconciliationMetadata | None = None


class MealPlanningService:
    """Coordinates the calorie, meal, nutrition and supermarket agents.

    The orchestrator owns the workflow so no agent needs to know about another.
    """

    def __init__(
        self,
        meal_agent: MealRecommendationAgent,
        nutrition_agent: NutritionVerificationAgent,
        supermarket_agent: SupermarketAgent,
        calorie_agent: CalorieExpenditureAgent,
        profile_repo: UserProfileStore,
        tolerance: float = DEFAULT_TOLERANCE,
    ) -> None:
        """Store the collaborating agents.

        Args:
            meal_agent: Retrieves and adapts a meal template.
            nutrition_agent: Verifies ingredient macros.
            supermarket_agent: Maps ingredients to a shopping list.
            calorie_agent: Predicts expenditure and the calorie budget.
            profile_repo: Supplies stored biometrics when the request omits them.
            tolerance: Accepted fractional deviation before portions are rescaled.
        """
        self.meal_agent = meal_agent
        self.nutrition_agent = nutrition_agent
        self.supermarket_agent = supermarket_agent
        self.calorie_agent = calorie_agent
        self.profile_repo = profile_repo
        self.tolerance = tolerance

    def generate(self, request: MealRequest) -> MealPlanResult:
        """Run the full meal planning workflow.

        Args:
            request: The validated meal-plan request.

        Returns:
            A MealPlanResult carrying every agent payload.
        """
        profile = self.profile_repo.fetch_user_profile(request.user_id.strip())
        calorie_budget = self.calorie_agent.predict(self._calorie_request(request, profile))

        meal_plan = self.meal_agent.generate_meal_payload(
            craving=request.craving.strip(),
            user_id=request.user_id.strip(),
            daily_calorie_target=int(round(calorie_budget.meal_calorie_budget_kcal)),
            health_conditions=request.health_conditions,
            dietary_preferences=request.dietary_preferences,
            profile=profile,
        )
        nutrition = self.nutrition_agent.calculate_meal_macros(
            ingredients=meal_plan.meal_definition.ingredients
        )
        meal_plan, nutrition, reconciliation = self._reconcile(meal_plan, nutrition)

        shopping_list = self.supermarket_agent.generate_shopping_list(
            ingredients=meal_plan.meal_definition.ingredients,
            user_location=request.location.strip(),
        )
        return MealPlanResult(
            calorie_budget=calorie_budget,
            meal_plan=meal_plan,
            nutrition=nutrition,
            shopping_list=shopping_list,
            reconciliation=reconciliation,
        )

    def _reconcile(
        self,
        meal_plan: MealPlanPayload,
        nutrition: MealNutrition,
    ) -> tuple[MealPlanPayload, MealNutrition, ReconciliationMetadata | None]:
        """Compare verified nutrition against the portion target, rescaling once if needed.

        Args:
            meal_plan: The plan whose portions were scaled from an estimate.
            nutrition: Verified macros for those portions.

        Returns:
            The plan, the nutrition and the reconciliation record. When portion
            scaling did not run there is nothing to reconcile against, so the
            record is None and the inputs are returned unchanged.
        """
        scaling = meal_plan.portion_scaling
        if scaling is None or nutrition.total_calories <= 0:
            return meal_plan, nutrition, None

        target = scaling.target_meal_calories
        before = nutrition.total_calories
        deviation_before = abs(before - target) / target

        if deviation_before <= self.tolerance:
            return (
                meal_plan,
                nutrition,
                ReconciliationMetadata(
                    target_meal_calories=target,
                    verified_calories_before=round(before, 1),
                    deviation_before=round(deviation_before, 4),
                    rescaled=False,
                    within_tolerance=True,
                    tolerance=self.tolerance,
                ),
            )

        factor = max(0.65, min(1.6, target / before))
        rescaled_ingredients = [
            Ingredient(
                item_name=ingredient.item_name,
                base_quantity_grams=max(
                    5, int(round(ingredient.base_quantity_grams * factor / 5) * 5)
                ),
            )
            for ingredient in meal_plan.meal_definition.ingredients
        ]
        meal_plan.meal_definition.ingredients = rescaled_ingredients
        meal_plan.portion_scaling.scale_factor = round(scaling.scale_factor * factor, 2)

        # Exactly one retry. Whatever this produces is what ships.
        nutrition = self.nutrition_agent.calculate_meal_macros(ingredients=rescaled_ingredients)
        after = nutrition.total_calories
        deviation_after = abs(after - target) / target if after > 0 else deviation_before

        meal_plan.metadata.warnings.append(
            f"Rescaled portions by {factor:.2f} after verified nutrition deviated "
            f"{deviation_before:.0%} from the {target} kcal target."
        )
        return (
            meal_plan,
            nutrition,
            ReconciliationMetadata(
                target_meal_calories=target,
                verified_calories_before=round(before, 1),
                deviation_before=round(deviation_before, 4),
                rescaled=True,
                verified_calories_after=round(after, 1),
                deviation_after=round(deviation_after, 4),
                within_tolerance=deviation_after <= self.tolerance,
                tolerance=self.tolerance,
            ),
        )

    def _calorie_request(
        self, request: MealRequest, profile: dict[str, Any]
    ) -> CalorieExpenditureRequest:
        """Build a calorie request, preferring explicit biometrics over the profile.

        Args:
            request: The meal-plan request, whose biometric fields are optional.
            profile: The pre-fetched profile, used to fill any field the request omits.

        Returns:
            A CalorieExpenditureRequest populated from the request or the profile.
        """
        return CalorieExpenditureRequest(
            age=request.age if request.age is not None else profile["age"],
            sex=request.sex if request.sex is not None else profile["gender"],
            height_cm=(request.height_cm if request.height_cm is not None else profile["height"]),
            weight_kg=(request.weight_kg if request.weight_kg is not None else profile["weight"]),
            activity_multiplier=(
                request.activity_multiplier
                if request.activity_multiplier is not None
                else profile["workout_level"]
            ),
            goal=request.goal,
            health_conditions=request.health_conditions,
        )
