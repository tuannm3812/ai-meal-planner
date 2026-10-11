"""Portion arithmetic shared by first-pass scaling and reconciliation (§7.5).

docs/4_next_steps.md §7.5: the 0.65/1.6 clamp and the 5 g rounding were
written twice, in MealRecommendationAgent._scale_ingredients_to_meal_target and
MealPlanningService._reconcile. They now live in core/portions.py.

Codex (2026-10-12) asked that the exact rounding be preserved, half steps
included. Python's round() rounds a half to the even neighbour, so 2.5 steps
becomes 2 and 7.5 becomes 8. A grid below compares the helper with the
expression both sites used before.
"""

import pytest

from backend.app.core.portions import clamp_scale, scale_grams, scale_ingredients
from backend.app.schemas.requests import Ingredient


def _original(grams: int, factor: float) -> int:
    """The expression both call sites used before the extraction."""
    return max(5, int(round(grams * factor / 5) * 5))


@pytest.mark.parametrize(
    ("ratio", "clamped"), [(0.1, 0.65), (0.65, 0.65), (1.0, 1.0), (1.6, 1.6), (9.0, 1.6)]
)
def test_the_scale_is_clamped_to_its_range(ratio: float, clamped: float) -> None:
    assert clamp_scale(ratio) == clamped


@pytest.mark.parametrize(
    ("grams", "factor", "scaled"),
    [
        (10, 1.25, 10),  # 2.5 steps: a half rounds to even (2), not up
        (30, 1.25, 40),  # 7.5 steps: a half rounds to even (8)
        (3, 0.65, 5),  # below one step: never less than 5 g
        (200, 1.0, 200),
        (123, 1.0, 125),
    ],
)
def test_grams_round_to_5_g_with_half_to_even(grams: int, factor: float, scaled: int) -> None:
    assert scale_grams(grams, factor) == scaled


def test_the_helper_matches_the_original_expression_everywhere() -> None:
    factors = [0.65, 0.7, 0.75, 0.8, 0.9, 1.0, 1.1, 1.2, 1.25, 1.3, 1.4, 1.5, 1.6]
    factors += [round(0.65 + step * 0.0137, 4) for step in range(70)]
    for grams in range(1, 601):
        for factor in factors:
            assert scale_grams(grams, factor) == _original(grams, factor), (grams, factor)


def test_ingredients_keep_their_names_and_order() -> None:
    ingredients = [
        Ingredient(item_name="beef patty", base_quantity_grams=200),
        Ingredient(item_name="bun", base_quantity_grams=10),
    ]

    scaled = scale_ingredients(ingredients, 1.25)

    assert [(i.item_name, i.base_quantity_grams) for i in scaled] == [
        ("beef patty", 250),
        ("bun", 10),
    ]
