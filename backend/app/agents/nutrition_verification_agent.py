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
        if self.api_key:
            try:
                usda_result = self._query_usda_database(item_name)
                if self._has_usable_macros(usda_result):
                    return usda_result
            except Exception as exc:
                logger.warning("USDA lookup failed for %s: %s", item_name, exc)

        if self.fatsecret_client_id and self.fatsecret_client_secret:
            try:
                fatsecret_result = self._query_fatsecret_database(item_name)
                if self._has_usable_macros(fatsecret_result):
                    return fatsecret_result
            except Exception as exc:
                logger.warning("FatSecret lookup failed for %s: %s", item_name, exc)

        return self._estimate_macros_per_100g(item_name)

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
