import json
import logging
import re
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field

from ..rag.reference_data import load_reference
from ..schemas.common import AgentMetadata, average_confidence
from ..schemas.requests import Ingredient

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


class MealNutrition(BaseModel):
    ingredients_macros: list[IngredientMacro]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    metadata: AgentMetadata


class NutritionVerificationAgent:
    _FAILURE_THRESHOLD = 3
    _COOLDOWN_SECONDS = 120

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

        # Successful API lookups are cached per normalized ingredient name for the
        # process lifetime; estimates/local-table results are cheap and not cached.
        self._macro_cache: dict[str, dict[str, Any]] = {}
        self._usda_consecutive_failures = 0
        self._usda_cooldown_until = 0.0
        self._fatsecret_consecutive_failures = 0
        self._fatsecret_cooldown_until = 0.0

    def calculate_meal_macros(self, ingredients: list[Ingredient]) -> MealNutrition:
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

        confidence = average_confidence(processed_ingredients)
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

    def _query_macros_per_100g(self, item_name: str) -> dict[str, Any]:
        local_override = self._trusted_local_override(item_name)
        if local_override:
            return local_override

        search_name = self._normalize_search_name(item_name)
        cached = self._macro_cache.get(search_name)
        if cached:
            return cached

        if self.api_key and not self._in_cooldown(self._usda_cooldown_until):
            try:
                usda_result = self._query_usda_database(search_name)
                self._usda_consecutive_failures = 0
                if self._has_usable_macros(usda_result):
                    self._macro_cache[search_name] = usda_result
                    return usda_result
            except Exception as exc:
                logger.warning("USDA lookup failed for %s: %s", item_name, exc)
                self._register_failure("usda")

        if (
            self.fatsecret_client_id
            and self.fatsecret_client_secret
            and not self._in_cooldown(self._fatsecret_cooldown_until)
        ):
            try:
                fatsecret_result = self._query_fatsecret_database(search_name)
                self._fatsecret_consecutive_failures = 0
                if self._has_usable_macros(fatsecret_result):
                    self._macro_cache[search_name] = fatsecret_result
                    return fatsecret_result
            except Exception as exc:
                logger.warning("FatSecret lookup failed for %s: %s", item_name, exc)
                self._register_failure("fatsecret")

        return self._estimate_macros_per_100g(item_name)

    @staticmethod
    def _in_cooldown(cooldown_until: float) -> bool:
        return time.time() < cooldown_until

    def _register_failure(self, backend: str) -> None:
        if backend == "usda":
            self._usda_consecutive_failures += 1
            if self._usda_consecutive_failures >= self._FAILURE_THRESHOLD:
                self._usda_cooldown_until = time.time() + self._COOLDOWN_SECONDS
                logger.warning(
                    "USDA lookups paused for %ss after %d consecutive failures.",
                    self._COOLDOWN_SECONDS,
                    self._usda_consecutive_failures,
                )
        else:
            self._fatsecret_consecutive_failures += 1
            if self._fatsecret_consecutive_failures >= self._FAILURE_THRESHOLD:
                self._fatsecret_cooldown_until = time.time() + self._COOLDOWN_SECONDS
                logger.warning(
                    "FatSecret lookups paused for %ss after %d consecutive failures.",
                    self._COOLDOWN_SECONDS,
                    self._fatsecret_consecutive_failures,
                )

    @staticmethod
    def _trusted_local_override(item_name: str) -> dict[str, Any] | None:
        lookup = load_reference("trusted_overrides")
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

    def _query_usda_database(self, item_name: str) -> dict[str, Any] | None:
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

    def _query_fatsecret_database(self, item_name: str) -> dict[str, Any] | None:
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

    def _parse_fatsecret_description(self, description: str) -> dict[str, float] | None:
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

    def _estimate_macros_per_100g(self, item_name: str) -> dict[str, Any]:
        name = item_name.lower()
        lookup = load_reference("macro_fallbacks")

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
    def _nutrient_value(by_name: dict[str, Any], partial_key: str, fallback_key: str) -> float:
        for nutrient_name, nutrient in by_name.items():
            if partial_key in nutrient_name:
                return float(nutrient.get("value", 0))
        return float(by_name.get(fallback_key.lower(), {}).get("value", 0))

    @staticmethod
    def _basic_auth_token(credentials: str) -> str:
        import base64

        return base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _has_usable_macros(macros: dict[str, Any] | None) -> bool:
        if not macros:
            return False
        return any(float(macros.get(key, 0)) > 0 for key in ["calories", "protein", "carbs", "fat"])
