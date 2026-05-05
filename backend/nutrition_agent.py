import logging
from typing import List, Dict, Any
from pydantic import BaseModel

# ---------------------------------------------------------
# Pydantic Models for Macro Enforcement
# ---------------------------------------------------------
class IngredientMacro(BaseModel):
    item_name: str
    base_quantity_grams: int
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float

class MealNutrition(BaseModel):
    ingredients_macros: List[IngredientMacro]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float

# ---------------------------------------------------------
# Nutrition Sub-Agent Class
# ---------------------------------------------------------
class NutritionAgent:
    def __init__(self, usda_api_key: str):
        """
        Initializes the agent with credentials for the USDA FoodData Central API.
        In a full MCP setup, this integrates with the MCP server tool.
        """
        self.api_key = usda_api_key
        self.base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        logging.basicConfig(level=logging.INFO)

    def _query_usda_database(self, item_name: str) -> Dict[str, float]:
        """
        Simulated MCP tool call to the USDA database. 
        Searches for the ingredient and extracts macronutrients per 100g.
        """
        # In production, this uses `requests.get()` to hit the self.base_url
        # For now, we mock the vector search retrieval response
        logging.info(f"Querying USDA database for: {item_name}")
        
        mock_usda_database = {
            "ground turkey (93% lean)": {"cal": 150, "pro": 20, "carb": 0, "fat": 8},
            "whole wheat hamburger bun": {"cal": 260, "pro": 10, "carb": 44, "fat": 4},
            "mixed salad greens": {"cal": 15, "pro": 1.5, "carb": 3, "fat": 0.2}
        }
        
        # Default fallback if item is not found
        return mock_usda_database.get(item_name.lower(), {"cal": 0, "pro": 0, "carb": 0, "fat": 0})

    def calculate_meal_macros(self, ingredients: List[Any]) -> MealNutrition:
        """
        Takes the structured ingredients list from the Primary Agent, 
        fetches USDA data, and mathematically scales the macros based on grams.
        """
        processed_ingredients = []
        totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

        for ingredient in ingredients:
            # The ingredient object comes from our MealDefinitionAgent payload
            name = ingredient.item_name
            grams = ingredient.base_quantity_grams
            
            # Fetch base macros (per 100g)
            base_macros = self._query_usda_database(name)
            
            # Scale macros by the actual portion size
            scale_factor = grams / 100.0
            item_macros = IngredientMacro(
                item_name=name,
                base_quantity_grams=grams,
                calories_kcal=round(base_macros["cal"] * scale_factor, 1),
                protein_g=round(base_macros["pro"] * scale_factor, 1),
                carbs_g=round(base_macros["carb"] * scale_factor, 1),
                fat_g=round(base_macros["fat"] * scale_factor, 1)
            )
            
            processed_ingredients.append(item_macros)
            
            # Add to running totals
            totals["calories"] += item_macros.calories_kcal
            totals["protein"] += item_macros.protein_g
            totals["carbs"] += item_macros.carbs_g
            totals["fat"] += item_macros.fat_g

        return MealNutrition(
            ingredients_macros=processed_ingredients,
            total_calories=round(totals["calories"], 1),
            total_protein=round(totals["protein"], 1),
            total_carbs=round(totals["carbs"], 1),
            total_fat=round(totals["fat"], 1)
        )