"""Rebalance one meal's portions so its macro split sits inside the adult AMDR.

Portion scaling multiplies every ingredient by one factor, which hits a calorie
target but leaves the macro split exactly as the template has it. Here each
ingredient gets its own factor. Both the calorie total and each macro's share
of energy are linear in those factors, so finding factors that satisfy them is
a small linear programme:

- each factor stays within ``[MIN_FACTOR, MAX_FACTOR]`` of the current portion;
- calories land within ``CALORIE_BAND`` of the meal target;
- protein, carbohydrate and fat each sit inside AMDR, ``SHARE_MARGIN`` in from
  each bound so rounding to 5 g does not push a share back out;
- the total change, the sum of ``|factor - 1|``, plus ``CALORIE_WEIGHT`` times
  the calorie deviation, is as small as possible. So a meal changes as little
  as it must, and lands as close to its calorie target as the bounds allow.

The per-gram figures come from verified nutrition, so the balance uses whatever
source verification used. The owner set AMDR as the target on 2026-10-17 (DEC-25).
"""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

AMDR_PERCENT = {"protein": (10.0, 35.0), "carbs": (45.0, 65.0), "fat": (20.0, 35.0)}
"""Adult AMDR, as a percentage of energy: macro -> (low, high)."""

KCAL_PER_GRAM = {"protein": 4.0, "carbs": 4.0, "fat": 9.0}

CALORIE_TARGET = 0.10
"""The owner's acceptance target (DEC-25): shipped calories within 10% of the meal
target. A meal inside it, with every macro inside AMDR, is not rebalanced."""

MIN_FACTOR = 0.5
MAX_FACTOR = 2.0
CALORIE_BAND = 0.05
SHARE_MARGIN = 1.0
CALORIE_WEIGHT = 10.0
"""A 10% calorie miss costs as much as changing one portion by its whole size."""


@dataclass(frozen=True)
class IngredientEnergy:
    """One ingredient's calories and macro grams at its current portion."""

    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


def macro_percentages(protein_g: float, carbs_g: float, fat_g: float) -> dict[str, float]:
    """Each macro's share of the calories the three macros supply.

    Args:
        protein_g: Grams of protein.
        carbs_g: Grams of carbohydrate.
        fat_g: Grams of fat.

    Returns:
        Percentages keyed by macro, at full precision so a share just outside
        a range is not rounded into it; all zero when the macros supply no
        energy.
    """
    energy = {
        "protein": protein_g * KCAL_PER_GRAM["protein"],
        "carbs": carbs_g * KCAL_PER_GRAM["carbs"],
        "fat": fat_g * KCAL_PER_GRAM["fat"],
    }
    total = sum(energy.values())
    if total <= 0:
        return {macro: 0.0 for macro in energy}
    return {macro: 100 * kcal / total for macro, kcal in energy.items()}


def in_amdr(percentages: dict[str, float]) -> dict[str, bool]:
    """Whether each macro's share falls inside its AMDR range, inclusive."""
    return {
        macro: AMDR_PERCENT[macro][0] <= percentages[macro] <= AMDR_PERCENT[macro][1]
        for macro in AMDR_PERCENT
    }


def balance_factors(
    ingredients: Sequence[IngredientEnergy], target_calories: float
) -> list[float] | None:
    """Find per-ingredient factors that put the meal on target and inside AMDR.

    Args:
        ingredients: Each ingredient's energy at its current portion.
        target_calories: The meal's calorie target.

    Returns:
        One factor per ingredient, in order, or None when no factors within
        the bounds satisfy every constraint.
    """
    count = len(ingredients)
    if count == 0 or target_calories <= 0:
        return None
    calories = np.array([item.calories for item in ingredients]) / target_calories
    macro_kcal = {
        "protein": np.array([item.protein_g for item in ingredients]) * KCAL_PER_GRAM["protein"],
        "carbs": np.array([item.carbs_g for item in ingredients]) * KCAL_PER_GRAM["carbs"],
        "fat": np.array([item.fat_g for item in ingredients]) * KCAL_PER_GRAM["fat"],
    }
    energy = sum(macro_kcal.values())

    # Variables: the factors f, slacks d_i >= |f_i - 1|, and u >= the calorie
    # deviation as a fraction of the target. Calories are scaled by the target.
    rows: list[np.ndarray] = []
    upper: list[float] = []

    def add(row_f: np.ndarray, bound: float, row_d: np.ndarray | None = None, u: float = 0.0):
        row_d = np.zeros(count) if row_d is None else row_d
        rows.append(np.concatenate([row_f, row_d, [u]]))
        upper.append(bound)

    add(calories, 1 + CALORIE_BAND)
    add(-calories, -(1 - CALORIE_BAND))
    add(calories, 1.0, u=-1.0)  # deviation above the target <= u
    add(-calories, -1.0, u=-1.0)  # deviation below the target <= u
    for macro, (low, high) in AMDR_PERCENT.items():
        low_share = (low + SHARE_MARGIN) / 100
        high_share = (high - SHARE_MARGIN) / 100
        add(macro_kcal[macro] - high_share * energy, 0.0)  # share <= high
        add(low_share * energy - macro_kcal[macro], 0.0)  # share >= low
    identity = np.eye(count)
    for index in range(count):
        add(identity[index], 1.0, -identity[index])  # f - d <= 1
        add(-identity[index], -1.0, -identity[index])  # -f - d <= -1

    result = linprog(
        c=np.concatenate([np.zeros(count), np.ones(count), [CALORIE_WEIGHT]]),
        A_ub=np.vstack(rows),
        b_ub=np.array(upper),
        bounds=[(MIN_FACTOR, MAX_FACTOR)] * count + [(0, None)] * (count + 1),
        method="highs",
    )
    if not result.success:
        return None
    return [float(factor) for factor in result.x[:count]]
