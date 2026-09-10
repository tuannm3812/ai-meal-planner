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


def owner_of_meal_plan(payload: dict[str, Any]) -> str:
    """Extract the owning user id from a meal-plan payload.

    Tolerates a missing, null or non-dict ``request`` field. Both backends use
    this so they agree on malformed input: previously the SQL backend raised
    AttributeError at write time while the JSON backend accepted the record and
    then raised on every subsequent read - for every user, not just the one whose
    record was malformed.

    Args:
        payload: A stored or about-to-be-stored meal-plan response.

    Returns:
        The user id, or an empty string when the payload does not carry one.
    """
    request = payload.get("request")
    if not isinstance(request, dict):
        return ""
    user_id = request.get("user_id")
    return str(user_id) if user_id is not None else ""


def owner_of_feedback(payload: dict[str, Any]) -> str:
    """Extract the owning user id from a feedback payload.

    Tolerates a missing or null ``user_id`` field, and coerces any other
    value to ``str``, so both backends agree on malformed input. Previously
    the SQL backend always coerced with ``str(payload.get("user_id", ""))``
    while the JSON backend compared the raw stored value, so a non-string id
    (or a missing one) could be attributed to a different owner depending on
    the backend - unreachable through the HTTP API, but reachable through
    ``scripts/migrate_json_to_sqlite.py``, which feeds legacy records
    straight into ``save()``.

    Args:
        payload: A stored or about-to-be-stored feedback record.

    Returns:
        The user id, or an empty string when the payload does not carry one.
    """
    user_id = payload.get("user_id")
    return str(user_id) if user_id is not None else ""
