"""Constraint rules: which groups a label implies, and what they block.

These branches decide whether a meal is safe for a stated health condition, so
they are tested directly rather than only through retrieval.
"""

import pytest

from backend.app.rag.meal_corpus import CorpusIngredient, MealCorpusItem
from backend.app.rag.rules import (
    PlannedSubstitution,
    blocked_groups_for_ingredient,
    constraint_groups,
    meal_conflicts_with_health_conditions,
    meal_is_allowed,
    normalize_label,
    substitution_plan_for_meal,
)


def test_normalize_label_lowercases_and_strips() -> None:
    assert normalize_label("  High Protein  ") == "high protein"


@pytest.mark.parametrize("label", ["vegan", "plant based", "plant-based"])
def test_vegan_implies_dairy_and_egg(label: str) -> None:
    """Vegan must imply the narrower groups, or a vegan meal could contain cheese."""
    groups = constraint_groups([label])
    assert "vegan" in groups
    assert "dairy" in groups
    assert "egg" in groups


def test_vegetarian_is_not_vegan() -> None:
    """Vegetarian must not silently imply dairy-free."""
    groups = constraint_groups(["vegetarian"])
    assert "vegetarian" in groups
    assert "dairy" not in groups


@pytest.mark.parametrize("label", ["hypertension", "high blood pressure", "low sodium"])
def test_sodium_labels_all_map_to_one_group(label: str) -> None:
    """Three ways of saying the same thing must behave identically."""
    assert "sodium_sensitive" in constraint_groups([label])


def test_no_labels_means_no_groups() -> None:
    assert constraint_groups([]) == set()


@pytest.mark.parametrize("ingredient", ["chicken breast", "salmon fillet", "whole egg"])
def test_vegan_blocks_animal_products(ingredient: str) -> None:
    groups = constraint_groups(["vegan"])
    assert blocked_groups_for_ingredient(ingredient, groups)


def test_vegetarian_blocks_meat_but_allows_dairy() -> None:
    """The vegetarian branch must be narrower than the vegan one."""
    groups = constraint_groups(["vegetarian"])
    assert blocked_groups_for_ingredient("chicken breast", groups)
    assert not blocked_groups_for_ingredient("greek yogurt", groups)


def test_sodium_sensitive_blocks_soy_sauce() -> None:
    groups = constraint_groups(["hypertension"])
    assert "sodium_sensitive" in blocked_groups_for_ingredient("soy sauce", groups)


def test_an_unconstrained_ingredient_is_never_blocked() -> None:
    groups = constraint_groups(["vegan", "hypertension"])
    assert blocked_groups_for_ingredient("brown rice", groups) == set()


# --- kidney disease branch (previously only indirectly covered) ---


def test_kidney_disease_label_maps_to_its_own_group() -> None:
    groups = constraint_groups(["kidney disease"])
    assert groups == {"kidney_disease"}


@pytest.mark.parametrize(
    "ingredient", ["kidney beans", "lentils", "chickpeas", "tofu", "soy sauce"]
)
def test_kidney_disease_blocks_high_potassium_or_phosphorus_ingredients(
    ingredient: str,
) -> None:
    groups = constraint_groups(["kidney disease"])
    assert "kidney_disease" in blocked_groups_for_ingredient(ingredient, groups)


def test_kidney_disease_does_not_block_unrelated_ingredients() -> None:
    groups = constraint_groups(["kidney disease"])
    assert blocked_groups_for_ingredient("chicken breast", groups) == set()


# --- meal-level checks (meal_is_allowed, substitution_plan_for_meal) ---


def _meal(
    item_name: str,
    grams: int = 100,
    avoid_conditions: list[str] | None = None,
) -> MealCorpusItem:
    return MealCorpusItem(
        meal_id="test-meal",
        name="Test Meal",
        description="A meal built for a rules test.",
        avoid_conditions=avoid_conditions or [],
        ingredients=[CorpusIngredient(item_name=item_name, base_quantity_grams=grams)],
    )


def test_meal_conflicts_with_health_conditions_matches_case_and_separator_insensitively() -> None:
    meal = _meal("chicken breast", avoid_conditions=["kidney_disease"])
    assert meal_conflicts_with_health_conditions(meal, ["Kidney Disease"])


def test_meal_conflicts_with_health_conditions_false_when_no_overlap() -> None:
    meal = _meal("chicken breast", avoid_conditions=["kidney_disease"])
    assert not meal_conflicts_with_health_conditions(meal, ["hypertension"])


def test_meal_is_allowed_false_when_health_condition_conflicts_regardless_of_ingredients() -> None:
    """A meal flagged for a condition is disallowed even with an empty constraint set."""
    meal = _meal("chicken breast", avoid_conditions=["kidney_disease"])
    assert meal_is_allowed(meal, set(), ["Kidney Disease"]) is False


def test_meal_is_allowed_true_when_a_blocked_ingredient_has_a_substitution() -> None:
    """A vegan meal with egg is still allowed because egg has a defined substitution."""
    meal = _meal("whole egg")
    groups = constraint_groups(["vegan"])
    assert meal_is_allowed(meal, groups, []) is True


def test_meal_is_allowed_false_when_kidney_disease_blocked_ingredient_has_no_substitution() -> None:
    """Kidney-disease blocking has no substitution rules defined for it at all, so any
    meal containing a blocked ingredient is disallowed outright for that condition."""
    meal = _meal("lentils")
    groups = constraint_groups(["kidney disease"])
    assert meal_is_allowed(meal, groups, []) is False


def test_substitution_plan_for_meal_returns_the_matching_substitution() -> None:
    meal = _meal("whole egg")
    groups = constraint_groups(["vegan"])
    plan = substitution_plan_for_meal(meal, groups)
    assert plan == [
        PlannedSubstitution(
            original_name="whole egg",
            replacement_name="firm tofu",
            replacement_grams=80,
            reason="replaced egg for egg-free or vegan constraint",
        )
    ]


def test_substitution_plan_for_meal_empty_when_nothing_needs_substitution() -> None:
    meal = _meal("brown rice")
    groups = constraint_groups(["vegan", "hypertension"])
    assert substitution_plan_for_meal(meal, groups) == []
