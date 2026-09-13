"""Guards that extracting the reference tables changed no values."""

import pytest

from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.rag.reference_data import load_reference
from backend.app.schemas.requests import Ingredient


@pytest.mark.parametrize(
    ("item_name", "expected_kcal"),
    [("chicken breast", 165.0), ("olive oil", 884.0), ("brown rice", 123.0)],
)
def test_known_ingredient_calories_are_unchanged(item_name: str, expected_kcal: float) -> None:
    got = MealRecommendationAgent._estimate_ingredient_calories(
        [Ingredient(item_name=item_name, base_quantity_grams=100)]
    )
    assert got == pytest.approx(expected_kcal)


def test_unknown_ingredient_still_falls_back_to_120() -> None:
    """The default for an unlisted ingredient must not change."""
    got = MealRecommendationAgent._estimate_ingredient_calories(
        [Ingredient(item_name="nonexistent food", base_quantity_grams=100)]
    )
    assert got == pytest.approx(120.0)


def test_every_reference_table_loads() -> None:
    for name in (
        "ingredient_calories",
        "macro_fallbacks",
        "trusted_overrides",
        "supermarket_prices",
        "fallback_meals",
    ):
        assert load_reference(name)


def test_fallback_meals_end_with_an_unconditional_default() -> None:
    """The last entry matches anything, replacing the old else branch."""
    assert load_reference("fallback_meals")[-1]["keywords"] == []


def test_supermarket_prices_cover_the_priced_ingredients() -> None:
    agent = SupermarketAgent()
    priced = agent._map_inventory_and_price("chicken breast")
    assert priced["price"] > 0


def test_macro_fallbacks_still_produce_usable_macros() -> None:
    macros = NutritionVerificationAgent()._estimate_macros_per_100g("chicken breast")
    assert macros["calories"] > 0
