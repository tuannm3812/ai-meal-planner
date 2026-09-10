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
from ..schemas.requests import MealRequest


class MealPlanResult(BaseModel):
    """Everything the meal-plan endpoint needs, assembled by the orchestrator."""

    calorie_budget: CalorieExpenditureResponse
    meal_plan: MealPlanPayload
    nutrition: MealNutrition
    shopping_list: SupermarketPayload


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
        profile_repo: Any,
    ) -> None:
        """Store the collaborating agents.

        Args:
            meal_agent: Retrieves and adapts a meal template.
            nutrition_agent: Verifies ingredient macros.
            supermarket_agent: Maps ingredients to a shopping list.
            calorie_agent: Predicts expenditure and the calorie budget.
            profile_repo: Supplies stored biometrics when the request omits them.
        """
        self.meal_agent = meal_agent
        self.nutrition_agent = nutrition_agent
        self.supermarket_agent = supermarket_agent
        self.calorie_agent = calorie_agent
        self.profile_repo = profile_repo

    def generate(self, request: MealRequest) -> MealPlanResult:
        """Run the full meal planning workflow.

        Args:
            request: The validated meal-plan request.

        Returns:
            A MealPlanResult carrying every agent payload.
        """
        calorie_budget = self.calorie_agent.predict(self._calorie_request(request))

        meal_plan = self.meal_agent.generate_meal_payload(
            craving=request.craving.strip(),
            user_id=request.user_id.strip(),
            daily_calorie_target=int(round(calorie_budget.meal_calorie_budget_kcal)),
            health_conditions=request.health_conditions,
            dietary_preferences=request.dietary_preferences,
        )
        nutrition = self.nutrition_agent.calculate_meal_macros(
            ingredients=meal_plan.meal_definition.ingredients
        )
        shopping_list = self.supermarket_agent.generate_shopping_list(
            ingredients=meal_plan.meal_definition.ingredients,
            user_location=request.location.strip(),
        )
        return MealPlanResult(
            calorie_budget=calorie_budget,
            meal_plan=meal_plan,
            nutrition=nutrition,
            shopping_list=shopping_list,
        )

    def _calorie_request(self, request: MealRequest) -> CalorieExpenditureRequest:
        """Build a calorie request, preferring explicit biometrics over the profile.

        Args:
            request: The meal-plan request, whose biometric fields are optional.

        Returns:
            A CalorieExpenditureRequest populated from the request or the profile.
        """
        profile = self.profile_repo.fetch_user_profile(request.user_id.strip())
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
