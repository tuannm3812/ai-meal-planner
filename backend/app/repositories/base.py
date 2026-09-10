"""Storage protocols: the seam between the app and any concrete backend."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class UserProfileStore(Protocol):
    """Supplies stored biometrics for a user."""

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        """Return the profile for a user, or the default profile.

        Args:
            user_id: The profile key to look up.

        Returns:
            The stored profile, or the built-in default when the user has none.
            Returning a default rather than raising is deliberate: the app's
            normal path uses ids that have no stored profile.
        """
        ...


@runtime_checkable
class MealPlanStore(Protocol):
    """Persists generated meal plans."""

    def save(self, payload: dict[str, Any]) -> None:
        """Append one meal-plan response.

        Args:
            payload: The full API response to store.
        """
        ...

    def list_for_user(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return a user's most recent meal plans, newest first.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.

        Returns:
            Up to ``limit`` records, newest first.
        """
        ...


@runtime_checkable
class MealFeedbackStore(Protocol):
    """Persists user feedback on meals."""

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Append one feedback record.

        Args:
            payload: The feedback to store.

        Returns:
            The stored record, including its ``saved_at`` timestamp.
        """
        ...

    def list_for_user(
        self, user_id: str, limit: int = 20, saved_only: bool = False
    ) -> list[dict[str, Any]]:
        """Return a user's most recent feedback, newest first.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.
            saved_only: Restrict to records flagged as saved.

        Returns:
            Up to ``limit`` records, newest first.
        """
        ...
