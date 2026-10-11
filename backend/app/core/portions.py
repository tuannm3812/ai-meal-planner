"""Portion arithmetic shared by first-pass scaling and reconciliation.

Two places rescale a meal's ingredients: ``MealRecommendationAgent`` scales a
template to the meal's calorie target, and ``MealPlanningService._reconcile``
rescales once more if verified nutrition misses it. Each keeps its own policy:
which target, when to retry, how the scale factor is reported. Only the
arithmetic is shared here, so the two cannot drift apart (§7.5).
"""

from backend.app.schemas.requests import Ingredient

MIN_SCALE = 0.65
MAX_SCALE = 1.6
GRAM_STEP = 5


def clamp_scale(ratio: float) -> float:
    """Limit one rescale to [0.65, 1.6], so no single pass distorts a meal too far.

    Args:
        ratio: The target-to-estimate ratio.

    Returns:
        The ratio, clamped.
    """
    return max(MIN_SCALE, min(MAX_SCALE, ratio))


def scale_grams(grams: int, factor: float) -> int:
    """Scale a quantity and round it to the nearest 5 g, never below 5 g.

    ``round()`` sends an exact half step to the even neighbour (2.5 steps
    becomes 2, 7.5 becomes 8). That is the behaviour both callers always had,
    and it is kept.

    Args:
        grams: The quantity before scaling.
        factor: The scale factor.

    Returns:
        The scaled quantity in grams.
    """
    return max(GRAM_STEP, int(round(grams * factor / GRAM_STEP) * GRAM_STEP))


def scale_ingredients(ingredients: list[Ingredient], factor: float) -> list[Ingredient]:
    """Scale every ingredient by one factor, keeping names and order.

    Args:
        ingredients: The ingredients to scale.
        factor: The scale factor.

    Returns:
        New ingredients with scaled quantities.
    """
    return [
        Ingredient(
            item_name=ingredient.item_name,
            base_quantity_grams=scale_grams(ingredient.base_quantity_grams, factor),
        )
        for ingredient in ingredients
    ]
