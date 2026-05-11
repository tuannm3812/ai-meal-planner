import json
import logging
import re
import time
from typing import Any, Dict, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class IngredientMacro(BaseModel):
    item_name: str
    base_quantity_grams: int
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    data_source: str
    confidence: float = Field(ge=0, le=1)


class AgentMetadata(BaseModel):
    agent_name: str
    source: str
    confidence: float = Field(ge=0, le=1)
    warnings: List[str] = Field(default_factory=list)


class MealNutrition(BaseModel):
    ingredients_macros: List[IngredientMacro]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    metadata: AgentMetadata


class NutritionVerificationAgent:
    def __init__(
        self,
        usda_api_key: str | None = None,
        fatsecret_client_id: str | None = None,
        fatsecret_client_secret: str | None = None,
    ):
        self.api_key = usda_api_key
        self.base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        self.fatsecret_client_id = fatsecret_client_id
        self.fatsecret_client_secret = fatsecret_client_secret
        self.fatsecret_token: str | None = None
        self.fatsecret_token_expires_at = 0.0

    def calculate_meal_macros(self, ingredients: List[Any]) -> MealNutrition:
        processed_ingredients = []
        totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        warnings = []

        for ingredient in ingredients:
            name = ingredient.item_name
            grams = ingredient.base_quantity_grams
            base_macros = self._query_macros_per_100g(name)

            if base_macros["source"] not in {"usda_fooddata_central", "fatsecret_platform"}:
                warnings.append(f"Estimated nutrition for {name}")

            scale_factor = grams / 100.0
            item_macros = IngredientMacro(
                item_name=name,
                base_quantity_grams=grams,
                calories_kcal=round(base_macros["calories"] * scale_factor, 1),
                protein_g=round(base_macros["protein"] * scale_factor, 1),
                carbs_g=round(base_macros["carbs"] * scale_factor, 1),
                fat_g=round(base_macros["fat"] * scale_factor, 1),
                data_source=base_macros["source"],
                confidence=base_macros["confidence"],
            )

            processed_ingredients.append(item_macros)
            totals["calories"] += item_macros.calories_kcal
            totals["protein"] += item_macros.protein_g
            totals["carbs"] += item_macros.carbs_g
            totals["fat"] += item_macros.fat_g

        confidence = self._average_confidence(processed_ingredients)
        return MealNutrition(
            ingredients_macros=processed_ingredients,
            total_calories=round(totals["calories"], 1),
            total_protein=round(totals["protein"], 1),
            total_carbs=round(totals["carbs"], 1),
            total_fat=round(totals["fat"], 1),
            metadata=AgentMetadata(
                agent_name="NutritionVerificationAgent",
                source="usda_fatsecret_or_estimated",
                confidence=confidence,
                warnings=warnings,
            ),
        )

    def _query_macros_per_100g(self, item_name: str) -> Dict[str, Any]:
        local_override = self._trusted_local_override(item_name)
        if local_override:
            return local_override

        search_name = self._normalize_search_name(item_name)
        if self.api_key:
            try:
                usda_result = self._query_usda_database(search_name)
                if self._has_usable_macros(usda_result):
                    return usda_result
            except Exception as exc:
                logger.warning("USDA lookup failed for %s: %s", item_name, exc)

        if self.fatsecret_client_id and self.fatsecret_client_secret:
            try:
                fatsecret_result = self._query_fatsecret_database(search_name)
                if self._has_usable_macros(fatsecret_result):
                    return fatsecret_result
            except Exception as exc:
                logger.warning("FatSecret lookup failed for %s: %s", item_name, exc)

        return self._estimate_macros_per_100g(item_name)

    @staticmethod
    def _trusted_local_override(item_name: str) -> Dict[str, Any] | None:
        lookup = {
            "whole egg": {"calories": 143, "protein": 12.6, "carbs": 0.7, "fat": 9.5},
            "egg": {"calories": 143, "protein": 12.6, "carbs": 0.7, "fat": 9.5},
            "mixed vegetables": {"calories": 65, "protein": 3.3, "carbs": 13, "fat": 0.2},
            "sesame oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100},
            "cooked quinoa": {"calories": 120, "protein": 4.4, "carbs": 21.3, "fat": 1.9},
            "chickpeas": {"calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6},
            "lentils": {"calories": 116, "protein": 9.0, "carbs": 20.1, "fat": 0.4},
            "kidney beans": {"calories": 127, "protein": 8.7, "carbs": 22.8, "fat": 0.5},
            "black beans": {"calories": 132, "protein": 8.9, "carbs": 23.7, "fat": 0.5},
            "rolled oats": {"calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9},
            "banana": {"calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3},
            "chia seeds": {"calories": 486, "protein": 16.5, "carbs": 42.1, "fat": 30.7},
            "soy milk": {"calories": 33, "protein": 2.9, "carbs": 1.7, "fat": 1.8},
            "sweet potato": {"calories": 86, "protein": 1.6, "carbs": 20.1, "fat": 0.1},
            "cucumber": {"calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1},
            "peanut butter": {"calories": 588, "protein": 25.1, "carbs": 20.0, "fat": 50.0},
            "coconut aminos": {"calories": 60, "protein": 0, "carbs": 12.0, "fat": 0},
            "corn tortilla": {"calories": 218, "protein": 5.7, "carbs": 44.6, "fat": 2.9},
            "gluten-free bread": {"calories": 247, "protein": 4.3, "carbs": 50.0, "fat": 4.3},
            "gluten-free bun": {"calories": 260, "protein": 5.0, "carbs": 49.0, "fat": 5.0},
            "gluten-free pasta": {"calories": 350, "protein": 6.0, "carbs": 77.0, "fat": 1.5},
            "oat milk": {"calories": 43, "protein": 0.8, "carbs": 6.7, "fat": 1.5},
            "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100},
            "soy yogurt": {"calories": 54, "protein": 3.5, "carbs": 5.7, "fat": 1.8},
            "sunflower seed butter": {
                "calories": 617,
                "protein": 17.3,
                "carbs": 23.0,
                "fat": 55.0,
            },
        }
        macros = lookup.get(item_name.strip().lower())
        if not macros:
            return None
        return {**macros, "source": "trusted_local_reference", "confidence": 0.82}

    @staticmethod
    def _normalize_search_name(item_name: str) -> str:
        lookup = {
            "egg": "whole egg raw",
            "whole egg": "whole egg raw",
            "chicken breast": "chicken breast raw skinless boneless",
            "cooked white rice": "white rice cooked",
            "mixed vegetables": "mixed vegetables frozen",
            "low sodium soy sauce": "soy sauce low sodium",
            "tuna": "tuna canned in water",
            "salmon fillet": "salmon raw",
            "cooked quinoa": "quinoa cooked",
            "shrimp": "shrimp raw",
            "chickpeas": "chickpeas cooked",
            "lentils": "lentils cooked",
            "kidney beans": "kidney beans cooked",
            "black beans": "black beans cooked",
            "rolled oats": "oats rolled",
            "greek yogurt": "greek yogurt plain nonfat",
            "soy milk": "soy milk unsweetened",
            "sweet potato": "sweet potato raw",
            "lean beef steak": "beef steak lean raw",
            "lean beef mince": "ground beef lean raw",
            "coconut aminos": "coconut aminos sauce",
            "corn tortilla": "corn tortilla",
            "gluten-free bread": "gluten free bread",
            "gluten-free bun": "gluten free hamburger bun",
            "gluten-free pasta": "gluten free pasta",
            "oat milk": "oat milk unsweetened",
            "olive oil": "olive oil",
            "soy yogurt": "soy yogurt plain",
            "sunflower seed butter": "sunflower seed butter",
        }
        return lookup.get(item_name.strip().lower(), item_name)

    def _query_usda_database(self, item_name: str) -> Dict[str, Any] | None:
        query = urlencode({"api_key": self.api_key, "query": item_name, "pageSize": 1})
        with urlopen(f"{self.base_url}?{query}", timeout=6) as response:
            payload = json.loads(response.read().decode("utf-8"))

        foods = payload.get("foods", [])
        if not foods:
            return None

        nutrients = foods[0].get("foodNutrients", [])
        by_name = {nutrient.get("nutrientName", "").lower(): nutrient for nutrient in nutrients}

        return {
            "calories": self._nutrient_value(by_name, "energy", "Energy"),
            "protein": self._nutrient_value(by_name, "protein", "Protein"),
            "carbs": self._nutrient_value(by_name, "carbohydrate", "Carbohydrate, by difference"),
            "fat": self._nutrient_value(by_name, "total lipid", "Total lipid (fat)"),
            "source": "usda_fooddata_central",
            "confidence": 0.9,
        }

    def _query_fatsecret_database(self, item_name: str) -> Dict[str, Any] | None:
        token = self._get_fatsecret_token()
        request_body = urlencode(
            {
                "method": "foods.search",
                "search_expression": item_name,
                "format": "json",
                "max_results": 1,
            }
        ).encode("utf-8")
        request = Request(
            "https://platform.fatsecret.com/rest/server.api",
            data=request_body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )

        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if "error" in payload:
            error = payload["error"]
            raise RuntimeError(f"FatSecret API error {error.get('code')}: {error.get('message')}")

        foods = payload.get("foods", {}).get("food", [])
        if isinstance(foods, dict):
            foods = [foods]
        if not foods:
            return None

        description = foods[0].get("food_description", "")
        macros = self._parse_fatsecret_description(description)
        if not macros:
            return None

        return {
            **macros,
            "source": "fatsecret_platform",
            "confidence": 0.84,
        }

    def _get_fatsecret_token(self) -> str:
        if self.fatsecret_token and time.time() < self.fatsecret_token_expires_at:
            return self.fatsecret_token

        request_body = urlencode(
            {
                "grant_type": "client_credentials",
                "scope": "basic",
            }
        ).encode("utf-8")
        request = Request(
            "https://oauth.fatsecret.com/connect/token",
            data=request_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        credentials = f"{self.fatsecret_client_id}:{self.fatsecret_client_secret}"
        request.add_header(
            "Authorization",
            f"Basic {self._basic_auth_token(credentials)}",
        )

        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.fatsecret_token = payload["access_token"]
        self.fatsecret_token_expires_at = time.time() + int(payload.get("expires_in", 3600)) - 60
        return self.fatsecret_token

    def _parse_fatsecret_description(self, description: str) -> Dict[str, float] | None:
        if "per 100g" not in description.lower():
            return None

        patterns = {
            "calories": r"Calories:\s*([0-9.]+)\s*kcal",
            "fat": r"Fat:\s*([0-9.]+)\s*g",
            "carbs": r"Carbs:\s*([0-9.]+)\s*g",
            "protein": r"Protein:\s*([0-9.]+)\s*g",
        }
        values = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, description, flags=re.IGNORECASE)
            if not match:
                return None
            values[key] = float(match.group(1))

        return values

    def _estimate_macros_per_100g(self, item_name: str) -> Dict[str, Any]:
        name = item_name.lower()
        lookup = {
            "lean turkey mince": {"calories": 150, "protein": 22, "carbs": 0, "fat": 7},
            "ground turkey (93% lean)": {"calories": 150, "protein": 20, "carbs": 0, "fat": 8},
            "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
            "firm tofu": {"calories": 144, "protein": 17, "carbs": 3, "fat": 9},
            "whole wheat hamburger bun": {"calories": 260, "protein": 10, "carbs": 44, "fat": 4},
            "wholemeal pasta": {"calories": 348, "protein": 14, "carbs": 70, "fat": 2.5},
            "rice noodles": {"calories": 364, "protein": 6, "carbs": 80, "fat": 0.6},
            "brown rice": {"calories": 123, "protein": 2.7, "carbs": 25.6, "fat": 1},
            "mixed salad greens": {"calories": 15, "protein": 1.5, "carbs": 3, "fat": 0.2},
            "baby spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
            "broccoli": {"calories": 35, "protein": 2.4, "carbs": 7.2, "fat": 0.4},
            "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
            "tomato passata": {"calories": 33, "protein": 1.6, "carbs": 5.5, "fat": 0.2},
            "avocado": {"calories": 160, "protein": 2, "carbs": 8.5, "fat": 14.7},
            "soy sauce": {"calories": 53, "protein": 8, "carbs": 4.9, "fat": 0.6},
            "low sodium soy sauce": {"calories": 53, "protein": 8, "carbs": 4.9, "fat": 0.6},
            "whole egg": {"calories": 143, "protein": 12.6, "carbs": 0.7, "fat": 9.5},
            "egg": {"calories": 143, "protein": 12.6, "carbs": 0.7, "fat": 9.5},
            "cooked white rice": {"calories": 130, "protein": 2.7, "carbs": 28.2, "fat": 0.3},
            "mixed vegetables": {"calories": 65, "protein": 3.3, "carbs": 13, "fat": 0.2},
            "sesame oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100},
            "whole wheat tortilla": {"calories": 310, "protein": 9, "carbs": 50, "fat": 8},
            "tuna": {"calories": 116, "protein": 25.5, "carbs": 0, "fat": 0.8},
            "salmon fillet": {"calories": 208, "protein": 20.4, "carbs": 0, "fat": 13.4},
            "shrimp": {"calories": 85, "protein": 20.1, "carbs": 0.2, "fat": 0.5},
            "lean beef steak": {"calories": 170, "protein": 26, "carbs": 0, "fat": 7},
            "lean beef mince": {"calories": 176, "protein": 20, "carbs": 0, "fat": 10},
            "greek yogurt": {"calories": 59, "protein": 10.3, "carbs": 3.6, "fat": 0.4},
            "cottage cheese": {"calories": 98, "protein": 11.1, "carbs": 3.4, "fat": 4.3},
            "whole wheat bread": {"calories": 247, "protein": 13, "carbs": 41, "fat": 4.2},
            "low sodium chicken broth": {"calories": 7, "protein": 1, "carbs": 0.4, "fat": 0.2},
            "coconut aminos": {"calories": 60, "protein": 0, "carbs": 12.0, "fat": 0},
            "corn tortilla": {"calories": 218, "protein": 5.7, "carbs": 44.6, "fat": 2.9},
            "gluten-free bread": {"calories": 247, "protein": 4.3, "carbs": 50.0, "fat": 4.3},
            "gluten-free bun": {"calories": 260, "protein": 5.0, "carbs": 49.0, "fat": 5.0},
            "gluten-free pasta": {"calories": 350, "protein": 6.0, "carbs": 77.0, "fat": 1.5},
            "oat milk": {"calories": 43, "protein": 0.8, "carbs": 6.7, "fat": 1.5},
            "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100},
            "soy yogurt": {"calories": 54, "protein": 3.5, "carbs": 5.7, "fat": 1.8},
            "sunflower seed butter": {
                "calories": 617,
                "protein": 17.3,
                "carbs": 23.0,
                "fat": 55.0,
            },
        }

        if name in lookup:
            return {**lookup[name], "source": "local_reference_table", "confidence": 0.78}

        if any(token in name for token in ["chicken", "turkey", "beef", "fish", "tuna"]):
            estimate = {"calories": 175, "protein": 24, "carbs": 0, "fat": 8}
        elif any(token in name for token in ["rice", "pasta", "bun", "bread", "noodle"]):
            estimate = {"calories": 250, "protein": 7, "carbs": 48, "fat": 3}
        elif any(token in name for token in ["spinach", "greens", "lettuce", "tomato", "broccoli"]):
            estimate = {"calories": 25, "protein": 2, "carbs": 5, "fat": 0.3}
        else:
            estimate = {"calories": 120, "protein": 4, "carbs": 14, "fat": 5}

        return {**estimate, "source": "category_estimate", "confidence": 0.45}

    @staticmethod
    def _nutrient_value(by_name: Dict[str, Any], partial_key: str, fallback_key: str) -> float:
        for nutrient_name, nutrient in by_name.items():
            if partial_key in nutrient_name:
                return float(nutrient.get("value", 0))
        return float(by_name.get(fallback_key.lower(), {}).get("value", 0))

    @staticmethod
    def _basic_auth_token(credentials: str) -> str:
        import base64

        return base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _has_usable_macros(macros: Dict[str, Any] | None) -> bool:
        if not macros:
            return False
        return any(float(macros.get(key, 0)) > 0 for key in ["calories", "protein", "carbs", "fat"])

    @staticmethod
    def _average_confidence(items: List[IngredientMacro]) -> float:
        if not items:
            return 0.0
        return round(sum(item.confidence for item in items) / len(items), 2)
