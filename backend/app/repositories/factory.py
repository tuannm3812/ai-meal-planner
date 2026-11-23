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
    if settings.storage_backend == "firestore":
        return _firestore_repositories(settings)
    directory = data_dir or settings.data_dir
    if settings.storage_backend == "json":
        return (
            UserProfileRepository(directory),
            MealPlanRepository(directory),
            MealFeedbackRepository(directory),
        )

    # Imported here, inside the branch, so the JSON backend never pays
    # SQLAlchemy's import cost. These function-level imports (here and
    # in _firestore_repositories) are for cost, not to dodge a cycle.
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


def _firestore_repositories(
    settings: AppSettings,
) -> tuple[UserProfileStore, MealPlanStore, MealFeedbackStore]:
    """Build the Firestore trio (DEC-43), shared by every hosted instance.

    Imported here for the same cost reason as SQL above, and because the
    Firestore client is an optional extra.
    """
    from google.cloud import firestore

    from .firestore_store import (
        FirestoreMealFeedbackRepository,
        FirestoreMealPlanRepository,
        FirestoreUserProfileRepository,
    )

    client = firestore.Client(project=settings.firebase_project_id.strip() or None)
    return (
        FirestoreUserProfileRepository(client),
        FirestoreMealPlanRepository(client),
        FirestoreMealFeedbackRepository(client),
    )
