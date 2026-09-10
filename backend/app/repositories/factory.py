"""Selects the storage backend named by settings."""

from pathlib import Path

from ..core.config import AppSettings
from .base import MealFeedbackStore, MealPlanStore, UserProfileStore
from .json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)


def build_repositories(
    settings: AppSettings, data_dir: Path | None = None
) -> tuple[UserProfileStore, MealPlanStore, MealFeedbackStore]:
    """Build the repository trio for the configured backend.

    Args:
        settings: Resolved application settings.
        data_dir: Override for the storage location. Tests pass a temporary
            directory; production leaves it unset and uses ``settings.data_dir``.

    Returns:
        The profile, meal-plan and feedback stores, in that order.
    """
    directory = data_dir or settings.data_dir
    if settings.storage_backend == "json":
        return (
            UserProfileRepository(directory),
            MealPlanRepository(directory),
            MealFeedbackRepository(directory),
        )

    # Imported here, inside the branch, so the JSON backend never pays
    # SQLAlchemy's import cost. This is the one permitted function-level
    # import in the codebase, and it is for cost, not to dodge a cycle.
    from .sql import (
        SqlMealFeedbackRepository,
        SqlMealPlanRepository,
        SqlUserProfileRepository,
        build_engine,
    )

    engine = build_engine(directory / "ai_meal_planner.db")
    return (
        SqlUserProfileRepository(engine),
        SqlMealPlanRepository(engine),
        SqlMealFeedbackRepository(engine),
    )
