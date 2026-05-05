import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables (API Key)
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ---------------------------------------------------------
# Pydantic Models for Strict JSON Schema Enforcement
# ---------------------------------------------------------
class Ingredient(BaseModel):
    item_name: str
    base_quantity_grams: int

class MealDefinition(BaseModel):
    craving_input: str
    structured_meal_name: str
    ingredients: List[Ingredient]

class UserContext(BaseModel):
    caloric_target: int
    dietary_restrictions: List[str]

class MealPlanPayload(BaseModel):
    user_context: UserContext
    meal_definition: MealDefinition

# ---------------------------------------------------------
# Primary Orchestrator Class
# ---------------------------------------------------------
class MealDefinitionAgent:
    def __init__(self, db_connection: Any = None):
        self.db = db_connection
        # Using Gemini 2.0 Flash for fast, structured JSON generation
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def calculate_bmr(self, age: int, gender: str, weight_kg: float, height_cm: float, activity_multiplier: float) -> int:
        """Calculates daily caloric needs using the Mifflin-St Jeor Equation."""
        if gender.lower() == 'm':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
            
        return int(bmr * activity_multiplier)

    def predict_user_preferences(self, historical_meals: Any) -> Any:
        """Predictive modeling for future optimization."""
        train_df = historical_meals.extract_to_dataframe()
        log_reg_clf = self._initialize_preference_classifier()
        log_reg_clf.fit(train_df[['protein_ratio', 'carb_ratio']], train_df['user_rating'])
        return log_reg_clf

    def generate_meal_payload(self, craving: str, user_id: str) -> MealPlanPayload:
        """
        Fetches biometrics, calculates targets, and prompts Gemini 
        to structure the meal definition payload with a graceful fallback.
        """
        # 1. Fetch biometrics from the database
        user_biometrics = self.db.fetch_user_profile(user_id)
        
        # 2. Calculate daily caloric target
        target_calories = self.calculate_bmr(
            age=user_biometrics['age'],
            gender=user_biometrics['gender'],
            weight_kg=user_biometrics['weight'],
            height_cm=user_biometrics['height'],
            activity_multiplier=user_biometrics['workout_level']
        )
        
        # 3. Formulate the prompt for Gemini
        prompt = f"""
        You are an expert culinary AI orchestrator.
        The user is craving: '{craving}'.
        Their daily caloric target is {target_calories} kcal.
        Their dietary restrictions are: {', '.join(user_biometrics['dietary_restrictions'])}.
        
        Design a structured meal that satisfies this craving while respecting their restrictions.
        Break the meal down into a list of raw ingredients with their base quantities in grams.
        """
        
        # 4. Safely call Gemini with a Fallback
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=MealPlanPayload
                )
            )
            return MealPlanPayload.model_validate_json(response.text)
            
        except Exception as e:
            print(f"⚠️ Gemini API Error (Likely 429 Quota Exceeded): {e}")
            print("🔄 Falling back to mock data to prevent development blocking...")
            
            mock_fallback = {
                "user_context": {
                    "caloric_target": target_calories,
                    "dietary_restrictions": user_biometrics['dietary_restrictions']
                },
                "meal_definition": {
                    "craving_input": craving,
                    "structured_meal_name": "API Rate Limited - Fallback Turkey Burger",
                    "ingredients": [
                        {"item_name": "ground turkey (93% lean)", "base_quantity_grams": 150},
                        {"item_name": "whole wheat hamburger bun", "base_quantity_grams": 60},
                        {"item_name": "mixed salad greens", "base_quantity_grams": 100}
                    ]
                }
            }
            return MealPlanPayload(**mock_fallback)

    def _initialize_preference_classifier(self) -> Any:
        pass