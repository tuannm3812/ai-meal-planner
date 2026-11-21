"""Constraint rules: which groups a label implies, and what they block.

These branches decide whether a meal is safe for a stated health condition, so
they are tested directly rather than only through retrieval.
"""

import json
from pathlib import Path

import pytest

from backend.app.rag.meal_corpus import CorpusIngredient, MealCorpusItem
from backend.app.rag.rules import (
    GROUP_TAGS,
    SUBSTITUTION_RULES,
    UNTAGGED,
    PlannedSubstitution,
    blocked_groups_for_ingredient,
    constraint_groups,
    ingredient_tags,
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
    assert "high_sodium" in blocked_groups_for_ingredient("soy sauce", groups)


def test_an_unconstrained_ingredient_is_never_blocked() -> None:
    groups = constraint_groups(["vegan", "hypertension"])
    assert blocked_groups_for_ingredient("brown rice", groups) == set()


# --- kidney disease branch (previously only indirectly covered) ---


def test_kidney_disease_label_maps_to_its_own_group() -> None:
    groups = constraint_groups(["kidney disease"])
    assert groups == {"kidney_disease"}


@pytest.mark.parametrize(
    "ingredient", ["kidney beans", "lentils", "chickpeas", "firm tofu", "soy sauce"]
)
def test_kidney_disease_blocks_high_potassium_or_phosphorus_ingredients(
    ingredient: str,
) -> None:
    groups = constraint_groups(["kidney disease"])
    assert "kidney_caution" in blocked_groups_for_ingredient(ingredient, groups)


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


def test_meal_is_allowed_false_when_the_substitution_fixes_only_one_blocked_group() -> None:
    """Firm tofu under soy allergy plus kidney disease must not be "fixed".

    The soy rule swaps tofu for chickpeas, which resolves the allergy but is itself
    blocked for kidney disease. Found by probing the retrieval path on 2026-10-08:
    the corpus served chickpeas to exactly this user.
    """
    meal = _meal("firm tofu")
    groups = constraint_groups(["soy allergy", "kidney disease"])
    assert meal_is_allowed(meal, groups, []) is False
    assert substitution_plan_for_meal(meal, groups) == []


def test_meal_is_allowed_false_when_the_replacement_breaks_another_constraint() -> None:
    """Egg allergy swaps whole egg for firm tofu, which kidney disease forbids."""
    meal = _meal("whole egg")
    groups = constraint_groups(["egg allergy", "kidney disease"])
    assert meal_is_allowed(meal, groups, []) is False


def test_a_replacement_is_not_judged_by_its_own_group() -> None:
    """Keyword rules match "pasta" in "gluten-free pasta"; the gluten swap must still hold."""
    meal = _meal("wholemeal pasta")
    groups = constraint_groups(["gluten-free"])
    assert meal_is_allowed(meal, groups, []) is True
    assert [s.replacement_name for s in substitution_plan_for_meal(meal, groups)] == [
        "gluten-free pasta"
    ]


# --- plant foods whose names hold a dairy keyword ---


@pytest.mark.parametrize(
    "ingredient", ["soy milk", "oat milk", "soy yogurt", "peanut butter", "sunflower seed butter"]
)
@pytest.mark.parametrize("label", ["dairy-free", "vegan"])
def test_plant_foods_named_like_dairy_are_not_dairy(ingredient: str, label: str) -> None:
    """ "milk" and "butter" inside a plant food's name must not block it as dairy."""
    assert "dairy" not in blocked_groups_for_ingredient(ingredient, constraint_groups([label]))


@pytest.mark.parametrize("ingredient", ["cottage cheese", "greek yogurt"])
def test_dairy_is_still_blocked_for_dairy_free(ingredient: str) -> None:
    groups = constraint_groups(["dairy-free"])
    assert blocked_groups_for_ingredient(ingredient, groups) == {"dairy"}


# --- the tag table (DEC-34) ---


def _servable_ingredients() -> set[str]:
    """Every ingredient a meal can hold: corpus, fallbacks, guardrails and swaps."""
    root = Path(__file__).resolve().parents[2]
    names: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("item_name"), str):
                names.add(node["item_name"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for path in [
        "data/meal_corpus/meals.json",
        "data/reference/fallback_meals.json",
        "backend/app/evaluation/guardrail_meals.json",
    ]:
        walk(json.loads((root / path).read_text(encoding="utf-8")))
    names.update(rule.replacement_name for rule in SUBSTITUTION_RULES)
    return names


def test_every_servable_ingredient_is_tagged() -> None:
    """A new recipe ingredient must be added to data/reference/ingredient_allergens.json."""
    tags = ingredient_tags()
    missing = sorted(name for name in _servable_ingredients() if normalize_label(name) not in tags)
    assert missing == []


def test_the_table_uses_only_known_tags() -> None:
    known = set().union(*GROUP_TAGS.values())
    assert set().union(*ingredient_tags().values()) <= known


def test_every_swap_is_written_for_tags_a_group_refuses() -> None:
    known = set().union(*GROUP_TAGS.values())
    assert all(rule.blocked_groups <= known for rule in SUBSTITUTION_RULES)


@pytest.mark.parametrize("label", ["dairy-free", "peanut allergy", "vegan", "kidney disease"])
def test_an_unlisted_ingredient_is_refused_under_any_diet_rule(label: str) -> None:
    """Fail closed: an ingredient nobody tagged cannot be shown to be safe."""
    groups = constraint_groups([label])
    assert blocked_groups_for_ingredient("mystery sauce", groups) == {UNTAGGED}
    assert not meal_is_allowed(_meal("mystery sauce"), groups, [])


def test_an_unlisted_ingredient_is_fine_without_a_diet_rule() -> None:
    assert blocked_groups_for_ingredient("mystery sauce", set()) == set()


@pytest.mark.parametrize(
    "ingredient", ["gluten-free bun", "gluten-free pasta", "gluten-free bread"]
)
def test_gluten_free_foods_are_not_gluten(ingredient: str) -> None:
    """The name rules read "bun", "pasta" and "bread" inside these as gluten."""
    assert blocked_groups_for_ingredient(ingredient, constraint_groups(["celiac"])) == set()


def test_a_tree_nut_allergy_is_now_checked() -> None:
    """The name rules had no tree-nut keywords, so this group refused nothing."""
    groups = constraint_groups(["tree nut allergy"])
    assert groups == {"tree_nut"}
    assert blocked_groups_for_ingredient("mystery nut mix", groups) == {UNTAGGED}


def test_soy_milk_is_still_soy() -> None:
    groups = constraint_groups(["dairy-free", "soy allergy"])
    assert blocked_groups_for_ingredient("soy milk", groups) == {"soy"}


def test_a_peanut_allergy_on_a_dairy_free_profile_gets_sunflower_seed_butter() -> None:
    """The replacement's "butter" once read as dairy, so the swap was refused."""
    meal = _meal("peanut butter", grams=20)
    groups = constraint_groups(["dairy-free", "peanut allergy"])
    assert meal_is_allowed(meal, groups, []) is True
    assert [s.replacement_name for s in substitution_plan_for_meal(meal, groups)] == [
        "sunflower seed butter"
    ]


@pytest.mark.parametrize("ingredient", ["soy sauce", "low sodium soy sauce"])
@pytest.mark.parametrize("label", ["celiac", "coeliac", "gluten-free"])
def test_gluten_constraints_block_soy_sauce(label: str, ingredient: str) -> None:
    """Soy sauce is normally brewed with wheat, so its name alone does not make it safe."""
    assert "gluten" in blocked_groups_for_ingredient(ingredient, constraint_groups([label]))


@pytest.mark.parametrize("ingredient", ["soy sauce", "low sodium soy sauce"])
def test_gluten_swap_replaces_soy_sauce_with_coconut_aminos(ingredient: str) -> None:
    meal = _meal(ingredient)
    plan = substitution_plan_for_meal(meal, constraint_groups(["celiac"]))
    assert [item.replacement_name for item in plan] == ["coconut aminos"]


@pytest.mark.parametrize("ingredient", ["rolled oats", "oat milk"])
def test_gluten_constraints_block_oats(ingredient: str) -> None:
    """Oats carry no wheat but are often cross-contaminated, so coeliac plans avoid them."""
    assert "gluten" in blocked_groups_for_ingredient(ingredient, constraint_groups(["celiac"]))


def test_a_meal_built_on_rolled_oats_is_not_allowed_for_celiac() -> None:
    groups = constraint_groups(["celiac"])
    assert not meal_is_allowed(_meal("rolled oats"), groups, ["celiac"])


def test_oats_stay_allowed_without_a_gluten_constraint() -> None:
    assert not blocked_groups_for_ingredient("rolled oats", constraint_groups(["vegan"]))
