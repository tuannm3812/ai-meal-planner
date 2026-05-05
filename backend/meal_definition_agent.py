import logging
from typing import Any, List

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class Ingredient(BaseModel):
    item_name: str = Field(min_length=2)
    base_quantity_grams: int = Field(gt=0, le=2000)


class MealDefinition(BaseModel):
    craving_input: str
    structured_meal_name: str
    ingredients: List[Ingredient]


class UserContext(BaseModel):
    caloric_target: int
    dietary_restrictions: List[str]


class AgentMetadata(BaseModel):
    agent_name: str
    source: str
    confidence: float = Field(ge=0, le=1)
    warnings: List[str] = Field(default_factory=list)


class MealPlanPayload(BaseModel):
    user_context: UserContext
    meal_definition: MealDefinition
    metadata: AgentMetadata


class LlmIngredient(BaseModel):
    item_name: str
    base_quantity_grams: int


class LlmMealDefinition(BaseModel):
    craving_input: str
    structured_meal_name: str
    ingredients: List[LlmIngredient]


class LlmUserContext(BaseModel):
    caloric_target: int
    dietary_restrictions: List[str]


class LlmMealPlanPayload(BaseModel):
    user_context: LlmUserContext
    meal_definition: LlmMealDefinition


class MealDefinitionAgent:
    def __init__(self, db_connection: Any, gemini_api_key: str | None = None):
        self.db = db_connection
        self.model = None

        if gemini_api_key:
            self.model = genai.Client(api_key=gemini_api_key)

    def calculate_bmr(
        self,
        age: int,
        gender: str,
        weight_kg: float,
        height_cm: float,
        activity_multiplier: float,
    ) -> int:
        if gender.lower() == "m":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

        return int(bmr * activity_multiplier)

    def generate_meal_payload(self, craving: str, user_id: str) -> MealPlanPayload:
        user_biometrics = self.db.fetch_user_profile(user_id)
        target_calories = self.calculate_bmr(
            age=user_biometrics["age"],
            gender=user_biometrics["gender"],
            weight_kg=user_biometrics["weight"],
            height_cm=user_biometrics["height"],
            activity_multiplier=user_biometrics["workout_level"],
        )

        if not self.model:
            return self._fallback_payload(craving, user_biometrics, target_calories, "No Gemini API key configured")

        prompt = self._build_prompt(craving, target_calories, user_biometrics["dietary_restrictions"])

        try:
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LlmMealPlanPayload,
                ),
            )
            llm_payload = LlmMealPlanPayload.model_validate_json(response.text)
            return MealPlanPayload(
                user_context=UserContext.model_validate(llm_payload.user_context.model_dump()),
                meal_definition=MealDefinition.model_validate(llm_payload.meal_definition.model_dump()),
                metadata=AgentMetadata(
                    agent_name="MealDefinitionAgent",
                    source="gemini-2.0-flash",
                    confidence=0.86,
                ),
            )
        except Exception as exc:
            logger.warning("Gemini meal generation failed; using deterministic fallback: %s", exc)
            return self._fallback_payload(craving, user_biometrics, target_calories, str(exc))

    def predict_user_preferences(self, historical_meals: Any) -> Any:
        train_df = historical_meals.extract_to_dataframe()
        log_reg_clf = self._initialize_preference_classifier()
        log_reg_clf.fit(train_df[["protein_ratio", "carb_ratio"]], train_df["user_rating"])
        return log_reg_clf

    def _build_prompt(
        self,
        craving: str,
        target_calories: int,
        dietary_restrictions: List[str],
    ) -> str:
        return f"""
        You are an expert culinary AI orchestrator.
        The user is craving: {craving}.
        Their daily caloric target is {target_calories} kcal.
        Their dietary restrictions are: {", ".join(dietary_restrictions)}.

        Design one practical meal that satisfies the craving while respecting
        all restrictions. Use raw grocery ingredients only. Keep ingredient
        names plain and searchable, and provide gram quantities.
        """

    def _fallback_payload(
        self,
        craving: str,
        user_biometrics: dict[str, Any],
        target_calories: int,
        warning: str,
    ) -> MealPlanPayload:
        craving_lower = craving.lower()

        if "pasta" in craving_lower:
            meal_name = "High-Protein Tomato Turkey Pasta"
            ingredients = [
                {"item_name": "lean turkey mince", "base_quantity_grams": 160},
                {"item_name": "wholemeal pasta", "base_quantity_grams": 90},
                {"item_name": "tomato passata", "base_quantity_grams": 160},
                {"item_name": "baby spinach", "base_quantity_grams": 60},
            ]
        elif "salad" in craving_lower:
            meal_name = "Chicken Avocado Power Salad"
            ingredients = [
                {"item_name": "chicken breast", "base_quantity_grams": 170},
                {"item_name": "mixed salad greens", "base_quantity_grams": 120},
                {"item_name": "avocado", "base_quantity_grams": 70},
                {"item_name": "brown rice", "base_quantity_grams": 80},
            ]
        elif "tofu" in craving_lower or "vegan" in craving_lower:
            meal_name = "Tofu Rice Bowl"
            ingredients = [
                {"item_name": "firm tofu", "base_quantity_grams": 180},
                {"item_name": "brown rice", "base_quantity_grams": 90},
                {"item_name": "broccoli", "base_quantity_grams": 120},
                {"item_name": "soy sauce", "base_quantity_grams": 20},
            ]
        else:
            meal_name = "High-Protein Turkey Burger Bowl"
            ingredients = [
                {"item_name": "lean turkey mince", "base_quantity_grams": 160},
                {"item_name": "whole wheat hamburger bun", "base_quantity_grams": 60},
                {"item_name": "mixed salad greens", "base_quantity_grams": 100},
                {"item_name": "tomato", "base_quantity_grams": 80},
            ]

        return MealPlanPayload(
            user_context=UserContext(
                caloric_target=target_calories,
                dietary_restrictions=user_biometrics["dietary_restrictions"],
            ),
            meal_definition=MealDefinition(
                craving_input=craving,
                structured_meal_name=meal_name,
                ingredients=[Ingredient(**ingredient) for ingredient in ingredients],
            ),
            metadata=AgentMetadata(
                agent_name="MealDefinitionAgent",
                source="deterministic_fallback",
                confidence=0.62,
                warnings=[warning],
            ),
        )

    def _initialize_preference_classifier(self) -> Any:
        raise NotImplementedError("Preference modelling is planned but not enabled yet.")
