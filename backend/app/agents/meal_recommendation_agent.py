import logging
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel, Field

from ..rag.retriever import MealRetrievalResult, MealVectorRetriever


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
    explanation: str | None = None


class RetrievalCandidate(BaseModel):
    meal_id: str
    name: str
    score: float = Field(ge=0)
    rank: int = Field(ge=1)
    matched_terms: list[str] = Field(default_factory=list)


class AppliedSubstitution(BaseModel):
    original_name: str
    replacement_name: str
    replacement_grams: int = Field(gt=0)
    reason: str


class RetrievalMetadata(BaseModel):
    query: str
    retriever: str
    selected_meal_id: str
    selected_score: float = Field(ge=0)
    matched_terms: list[str] = Field(default_factory=list)
    candidates: list[RetrievalCandidate] = Field(default_factory=list)
    substitutions: list[AppliedSubstitution] = Field(default_factory=list)


class PortionScalingMetadata(BaseModel):
    target_meal_calories: int = Field(gt=0)
    estimated_template_calories: float = Field(ge=0)
    scale_factor: float = Field(gt=0)


class MealPlanPayload(BaseModel):
    user_context: UserContext
    meal_definition: MealDefinition
    metadata: AgentMetadata
    retrieval: RetrievalMetadata | None = None
    portion_scaling: PortionScalingMetadata | None = None


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


class LlmMealExplanation(BaseModel):
    explanation: str


class MealRecommendationAgent:
    def __init__(
        self,
        db_connection: Any,
        gemini_api_key: str | None = None,
        meal_retriever: MealVectorRetriever | None = None,
        meal_corpus_path: Path | None = None,
        enable_llm_adaptation: bool = False,
        rag_backend: str = "auto",
        rag_embedding_cache_dir: Path | None = None,
        rag_embedding_activation_size: int = 50,
    ):
        self.db = db_connection
        self.model = None
        self.types = None
        self.model_unavailable_reason = "No Gemini API key configured"
        self.meal_retriever = meal_retriever
        self.enable_llm_adaptation = enable_llm_adaptation

        if not self.meal_retriever and meal_corpus_path and meal_corpus_path.exists():
            try:
                self.meal_retriever = MealVectorRetriever(
                    meal_corpus_path,
                    backend=rag_backend,
                    embedding_cache_dir=rag_embedding_cache_dir,
                    embedding_activation_size=rag_embedding_activation_size,
                )
            except Exception as exc:
                logger.warning("Meal vector retriever failed to initialize: %s", exc)

        if gemini_api_key:
            try:
                from google import genai
                from google.genai import types

                self.model = genai.Client(api_key=gemini_api_key)
                self.types = types
                self.model_unavailable_reason = ""
            except ImportError:
                self.model_unavailable_reason = "google-genai is not installed in the active Python environment"
                logger.warning(
                    "google-genai is not installed; meal generation will use deterministic fallbacks."
                )

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

    def generate_meal_payload(
        self,
        craving: str,
        user_id: str,
        health_conditions: list[str] | None = None,
        dietary_preferences: list[str] | None = None,
    ) -> MealPlanPayload:
        user_biometrics = self.db.fetch_user_profile(user_id)
        target_calories = self.calculate_bmr(
            age=user_biometrics["age"],
            gender=user_biometrics["gender"],
            weight_kg=user_biometrics["weight"],
            height_cm=user_biometrics["height"],
            activity_multiplier=user_biometrics["workout_level"],
        )
        health_conditions = health_conditions or []
        dietary_preferences = dietary_preferences or []
        dietary_restrictions = user_biometrics["dietary_restrictions"]

        retrieval_results = self._retrieve_meals(
            craving=craving,
            dietary_restrictions=dietary_restrictions,
            health_conditions=health_conditions,
            dietary_preferences=dietary_preferences,
        )
        if retrieval_results:
            payload = self._payload_from_retrieval(
                craving=craving,
                target_calories=target_calories,
                dietary_restrictions=dietary_restrictions,
                result=retrieval_results[0],
                candidates=retrieval_results,
            )
            return self._adapt_final_payload(
                payload=payload,
                health_conditions=health_conditions,
                dietary_preferences=dietary_preferences,
            )

        warning = "No strong local RAG match found; using deterministic fallback."
        if self.model and not self.enable_llm_adaptation:
            warning += " Gemini base meal generation is disabled by design."
        return self._fallback_payload(craving, user_biometrics, target_calories, warning)

    def predict_user_preferences(self, historical_meals: Any) -> Any:
        train_df = historical_meals.extract_to_dataframe()
        log_reg_clf = self._initialize_preference_classifier()
        log_reg_clf.fit(train_df[["protein_ratio", "carb_ratio"]], train_df["user_rating"])
        return log_reg_clf

    def _build_adaptation_prompt(
        self,
        payload: MealPlanPayload,
        health_conditions: list[str] | None = None,
        dietary_preferences: list[str] | None = None,
    ) -> str:
        health_conditions = health_conditions or []
        dietary_preferences = dietary_preferences or []
        ingredients = ", ".join(
            f"{ingredient.item_name} ({ingredient.base_quantity_grams}g)"
            for ingredient in payload.meal_definition.ingredients
        )
        return f"""
        Explain why this already-selected meal fits the user's request.
        Do not invent new ingredients, calories, or medical advice.
        Meal: {payload.meal_definition.structured_meal_name}
        Ingredients: {ingredients}
        Daily caloric target: {payload.user_context.caloric_target} kcal.
        Dietary restrictions: {", ".join(payload.user_context.dietary_restrictions)}.
        Their health constraints are: {", ".join(health_conditions) or "none"}.
        Their dietary preferences are: {", ".join(dietary_preferences) or "none"}.

        Return one concise explanation sentence for the UI.
        """

    def _retrieve_meals(
        self,
        craving: str,
        dietary_restrictions: list[str],
        health_conditions: list[str],
        dietary_preferences: list[str],
    ) -> list[MealRetrievalResult]:
        if not self.meal_retriever:
            return []
        results = self.meal_retriever.retrieve(
            query=craving,
            dietary_restrictions=dietary_restrictions,
            health_conditions=health_conditions,
            dietary_preferences=dietary_preferences,
            top_k=3,
        )
        if not results or results[0].score < self.meal_retriever.min_score:
            return []
        return results

    def _payload_from_retrieval(
        self,
        craving: str,
        target_calories: int,
        dietary_restrictions: list[str],
        result: MealRetrievalResult,
        candidates: list[MealRetrievalResult],
    ) -> MealPlanPayload:
        substituted_ingredients = self._apply_substitutions(result)
        scaled_ingredients, scaling_metadata = self._scale_ingredients_to_meal_target(
            substituted_ingredients,
            target_calories,
        )
        warnings = [
            f"Retrieved meal template {result.meal.meal_id} using local vector RAG.",
            *result.warnings,
        ]
        if result.matched_terms:
            warnings.append(f"Matched terms: {', '.join(result.matched_terms)}")
        if result.substitutions:
            warnings.append(
                f"Applied {len(result.substitutions)} ingredient substitution(s) for constraints."
            )
        if scaling_metadata:
            warnings.append(
                "Scaled portions from "
                f"{scaling_metadata.estimated_template_calories:.0f} kcal toward "
                f"{scaling_metadata.target_meal_calories} kcal."
            )

        return MealPlanPayload(
            user_context=UserContext(
                caloric_target=target_calories,
                dietary_restrictions=dietary_restrictions,
            ),
            meal_definition=MealDefinition(
                craving_input=craving,
                structured_meal_name=result.meal.name,
                ingredients=scaled_ingredients,
            ),
            metadata=AgentMetadata(
                agent_name="MealRecommendationAgent",
                source="local_vector_rag_meal_corpus",
                confidence=min(round(result.score, 2), 0.95),
                warnings=warnings,
            ),
            retrieval=RetrievalMetadata(
                query=craving,
                retriever=self.meal_retriever.active_backend
                if self.meal_retriever
                else "unknown_retriever",
                selected_meal_id=result.meal.meal_id,
                selected_score=result.score,
                matched_terms=result.matched_terms,
                substitutions=[
                    AppliedSubstitution(
                        original_name=substitution.original_name,
                        replacement_name=substitution.replacement_name,
                        replacement_grams=substitution.replacement_grams,
                        reason=substitution.reason,
                    )
                    for substitution in result.substitutions
                ],
                candidates=[
                    RetrievalCandidate(
                        meal_id=candidate.meal.meal_id,
                        name=candidate.meal.name,
                        score=candidate.score,
                        rank=candidate.rank,
                        matched_terms=candidate.matched_terms,
                    )
                    for candidate in candidates
                ],
            ),
            portion_scaling=scaling_metadata,
        )

    def _adapt_final_payload(
        self,
        payload: MealPlanPayload,
        health_conditions: list[str],
        dietary_preferences: list[str],
    ) -> MealPlanPayload:
        if not self.enable_llm_adaptation or not self.model or not self.types:
            return payload

        try:
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=self._build_adaptation_prompt(
                    payload=payload,
                    health_conditions=health_conditions,
                    dietary_preferences=dietary_preferences,
                ),
                config=self.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LlmMealExplanation,
                ),
            )
            explanation = LlmMealExplanation.model_validate_json(response.text).explanation
            payload.metadata.source = f"{payload.metadata.source}+gemini_final_explanation"
            payload.metadata.explanation = explanation
            payload.metadata.warnings.append("Gemini used only for final explanation.")
        except Exception as exc:
            logger.warning("Gemini final explanation failed: %s", exc)
            payload.metadata.warnings.append(f"Gemini final explanation unavailable: {exc}")
        return payload

    def _apply_substitutions(self, result: MealRetrievalResult) -> list[Ingredient]:
        substitutions_by_name = {
            substitution.original_name.strip().lower(): substitution
            for substitution in result.substitutions
        }
        ingredients = []
        for ingredient in result.meal.ingredients:
            substitution = substitutions_by_name.get(ingredient.item_name.strip().lower())
            if substitution:
                ingredients.append(
                    Ingredient(
                        item_name=substitution.replacement_name,
                        base_quantity_grams=substitution.replacement_grams,
                    )
                )
            else:
                ingredients.append(
                    Ingredient(
                        item_name=ingredient.item_name,
                        base_quantity_grams=ingredient.base_quantity_grams,
                    )
                )
        return ingredients

    def _scale_ingredients_to_meal_target(
        self,
        ingredients: list[Ingredient],
        daily_calorie_target: int,
    ) -> tuple[list[Ingredient], PortionScalingMetadata | None]:
        estimated_template_calories = self._estimate_ingredient_calories(ingredients)
        if estimated_template_calories <= 0:
            return ingredients, None

        target_meal_calories = int(max(350, min(850, round(daily_calorie_target * 0.28))))
        scale_factor = max(0.65, min(1.6, target_meal_calories / estimated_template_calories))
        scaled_ingredients = [
            Ingredient(
                item_name=ingredient.item_name,
                base_quantity_grams=max(
                    5,
                    int(round(ingredient.base_quantity_grams * scale_factor / 5) * 5),
                ),
            )
            for ingredient in ingredients
        ]
        return scaled_ingredients, PortionScalingMetadata(
            target_meal_calories=target_meal_calories,
            estimated_template_calories=round(estimated_template_calories, 1),
            scale_factor=round(scale_factor, 2),
        )

    @staticmethod
    def _estimate_ingredient_calories(ingredients: list[Ingredient]) -> float:
        calories_per_100g = {
            "avocado": 160,
            "baby spinach": 23,
            "banana": 89,
            "black beans": 132,
            "broccoli": 35,
            "brown rice": 123,
            "chicken breast": 165,
            "chickpeas": 164,
            "coconut aminos": 60,
            "corn tortilla": 218,
            "cottage cheese": 98,
            "cucumber": 15,
            "firm tofu": 144,
            "gluten-free bread": 247,
            "gluten-free bun": 260,
            "gluten-free pasta": 350,
            "greek yogurt": 59,
            "lean beef mince": 176,
            "lean beef steak": 170,
            "lean turkey mince": 150,
            "low sodium chicken broth": 7,
            "low sodium soy sauce": 53,
            "mixed salad greens": 15,
            "mixed vegetables": 65,
            "oat milk": 43,
            "olive oil": 884,
            "peanut butter": 588,
            "rice noodles": 364,
            "rolled oats": 389,
            "salmon fillet": 208,
            "sesame oil": 884,
            "shrimp": 85,
            "soy milk": 33,
            "soy sauce": 53,
            "soy yogurt": 54,
            "sunflower seed butter": 617,
            "sweet potato": 86,
            "tomato": 18,
            "tomato passata": 33,
            "tuna": 116,
            "whole egg": 143,
            "whole wheat bread": 247,
            "whole wheat hamburger bun": 260,
            "whole wheat tortilla": 310,
            "wholemeal pasta": 348,
        }
        return sum(
            calories_per_100g.get(ingredient.item_name.strip().lower(), 120)
            * ingredient.base_quantity_grams
            / 100
            for ingredient in ingredients
        )

    def _fallback_payload(
        self,
        craving: str,
        user_biometrics: dict[str, Any],
        target_calories: int,
        warning: str,
    ) -> MealPlanPayload:
        craving_lower = craving.lower()

        if "noodle" in craving_lower or "asian" in craving_lower:
            meal_name = "High-Protein Asian Tofu Noodle Bowl"
            ingredients = [
                {"item_name": "firm tofu", "base_quantity_grams": 180},
                {"item_name": "rice noodles", "base_quantity_grams": 90},
                {"item_name": "broccoli", "base_quantity_grams": 120},
                {"item_name": "soy sauce", "base_quantity_grams": 20},
            ]
        elif "pasta" in craving_lower:
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
                agent_name="MealRecommendationAgent",
                source="deterministic_fallback",
                confidence=0.62,
                warnings=[warning],
            ),
        )

    def _initialize_preference_classifier(self) -> Any:
        raise NotImplementedError("Preference modelling is planned but not enabled yet.")
