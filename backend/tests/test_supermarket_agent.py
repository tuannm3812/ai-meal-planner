"""Supermarket agent: store lookup, pricing and unmatched ingredients."""

import pytest

from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.schemas.requests import Ingredient


def test_a_shopping_list_is_produced_for_every_ingredient() -> None:
    """Every ingredient must appear, matched or not."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[
            Ingredient(item_name="chicken breast", base_quantity_grams=200),
            Ingredient(item_name="brown rice", base_quantity_grams=150),
        ],
        user_location="Earlwood, NSW",
    )
    assert len(payload.shopping_list) == 2
    assert payload.total_estimated_cost > 0


def test_an_unknown_ingredient_still_gets_a_price() -> None:
    """An unmatched item must fall back, not vanish from the list."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="zzz unheard of item", base_quantity_grams=100)],
        user_location="Earlwood, NSW",
    )
    assert len(payload.shopping_list) == 1
    assert payload.shopping_list[0].estimated_price > 0


def test_total_is_the_sum_of_the_line_items() -> None:
    """The headline number must reconcile with the lines beneath it."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[
            Ingredient(item_name="chicken breast", base_quantity_grams=200),
            Ingredient(item_name="olive oil", base_quantity_grams=20),
            Ingredient(item_name="tomato", base_quantity_grams=100),
        ],
        user_location="Earlwood, NSW",
    )
    assert payload.total_estimated_cost == pytest.approx(
        sum(item.estimated_price for item in payload.shopping_list), rel=0.01
    )


def test_an_empty_ingredient_list_is_handled() -> None:
    """Zero ingredients must not divide by zero in the confidence average."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(ingredients=[], user_location="Earlwood, NSW")
    assert payload.shopping_list == []
    assert payload.metadata.confidence == 0.0


def test_store_details_are_populated_for_any_location() -> None:
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="tomato", base_quantity_grams=100)],
        user_location="Somewhere Unmapped, XX",
    )
    assert payload.store_details.store_name
    assert payload.store_details.location_source


def test_confidence_stays_within_bounds() -> None:
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="chicken breast", base_quantity_grams=200)],
        user_location="Earlwood, NSW",
    )
    assert 0 <= payload.metadata.confidence <= 1
    assert all(0 <= item.confidence <= 1 for item in payload.shopping_list)


# -- Line 53: the "estimated grocery mapping" warning ------------------------


def test_an_unmatched_ingredient_raises_an_estimated_mapping_warning() -> None:
    """An item absent from the local inventory reference must be flagged."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="zzz unheard of item", base_quantity_grams=100)],
        user_location="Earlwood, NSW",
    )
    assert payload.metadata.warnings == ["Estimated grocery mapping for zzz unheard of item"]


def test_a_matched_ingredient_raises_no_mapping_warning() -> None:
    """An item present in the local inventory reference needs no warning."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="chicken breast", base_quantity_grams=200)],
        user_location="Earlwood, NSW",
    )
    assert payload.metadata.warnings == []


# -- Lines 91-98: the Sydney/NSW regional-estimate branch ---------------------


def test_a_sydney_nsw_location_outside_earlwood_maps_to_woolworths_metro() -> None:
    agent = SupermarketAgent()
    store = agent._locate_nearest_store("Chatswood, NSW 2067")
    assert store.store_name == "Woolworths Metro"
    assert store.address == "Near Chatswood, NSW 2067"
    assert store.location_source == "regional_estimate"


def test_a_sydney_location_without_nsw_also_maps_to_woolworths_metro() -> None:
    agent = SupermarketAgent()
    store = agent._locate_nearest_store("Sydney CBD")
    assert store.store_name == "Woolworths Metro"
    assert store.location_source == "regional_estimate"


def test_a_location_outside_nsw_falls_back_to_the_generic_store() -> None:
    agent = SupermarketAgent()
    store = agent._locate_nearest_store("Melbourne, VIC 3000")
    assert store.store_name == "Local Supermarket"
    assert store.address == "Near Melbourne, VIC 3000"
    assert store.location_source == "generic_estimate"


def test_earlwood_takes_priority_over_the_broader_nsw_branch() -> None:
    agent = SupermarketAgent()
    store = agent._locate_nearest_store("Earlwood, NSW 2206")
    assert store.store_name == "Coles Supermarket"
    assert store.location_source == "local_reference"


# -- Lines 115-116: the category_price_estimate fallback confidence ----------


def test_the_category_price_fallback_carries_confidence_0_46() -> None:
    agent = SupermarketAgent()
    result = agent._map_inventory_and_price("zzz unheard of item")
    assert result["source"] == "category_price_estimate"
    assert result["confidence"] == 0.46
    assert result["sku"] == "Generic zzz unheard of item"


def test_a_matched_ingredient_carries_confidence_0_82_and_not_the_fallback() -> None:
    agent = SupermarketAgent()
    result = agent._map_inventory_and_price("chicken breast")
    assert result["source"] == "local_inventory_reference"
    assert result["confidence"] == 0.82


# -- Lines 126-133: the four _estimate_category_and_price buckets ------------


@pytest.mark.parametrize(
    "item_name",
    ["beef mince", "chicken wings", "turkey slices", "grilled fish", "tofu skewers"],
)
def test_protein_tokens_map_to_the_protein_bucket(item_name: str) -> None:
    aisle, price = SupermarketAgent._estimate_category_and_price(item_name)
    assert (aisle, price) == ("Protein", 6.50)


@pytest.mark.parametrize(
    "item_name",
    ["basmati rice", "pasta shells", "sourdough bread", "burger bun", "egg noodles"],
)
def test_pantry_tokens_map_to_the_pantry_bucket(item_name: str) -> None:
    aisle, price = SupermarketAgent._estimate_category_and_price(item_name)
    assert (aisle, price) == ("Pantry", 3.20)


@pytest.mark.parametrize(
    "item_name",
    ["baby spinach leaves", "salad greens mix", "iceberg lettuce", "cherry tomatoes", "broccolini"],
)
def test_produce_tokens_map_to_the_produce_bucket(item_name: str) -> None:
    aisle, price = SupermarketAgent._estimate_category_and_price(item_name)
    assert (aisle, price) == ("Produce", 2.80)


def test_an_unrecognised_item_falls_back_to_the_grocery_default() -> None:
    aisle, price = SupermarketAgent._estimate_category_and_price("olive oil")
    assert (aisle, price) == ("Grocery", 3.50)
