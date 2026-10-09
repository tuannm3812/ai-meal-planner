"""Storage protocols: the seam between the app and any concrete backend."""

from typing import Any, Protocol, runtime_checkable

LOCAL_CLIENT_ID = "local"
"""The namespace of open local mode, and of records written before G4."""


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

    def save(self, payload: dict[str, Any], *, client_id: str) -> None:
        """Append one meal-plan response.

        Args:
            payload: The full API response to store.
            client_id: The client application that owns the record.
        """
        ...

    def list_for_user(
        self, user_id: str, limit: int = 20, *, client_id: str
    ) -> list[dict[str, Any]]:
        """Return a user's most recent meal plans within one client, newest first.

        ``client_id`` is required and keyword-only: a ``user_id`` is unique only
        within one client, so omitting it must fail loudly, never default.

        Args:
            user_id: Owner of the records within the client's namespace.
            limit: Maximum records to return.
            client_id: The client application whose namespace to read.

        Returns:
            Up to ``limit`` records, newest first.
        """
        ...

    def find_by_request_id(self, request_id: str, *, client_id: str) -> dict[str, Any] | None:
        """Return the client's meal plan with this request id, if any.

        Args:
            request_id: The id returned when the plan was generated.
            client_id: The client application whose namespace to search.

        Returns:
            The stored record, or None if this client has no such plan.
        """
        ...


@runtime_checkable
class MealFeedbackStore(Protocol):
    """Persists user feedback on meals."""

    def save(self, payload: dict[str, Any], *, client_id: str) -> dict[str, Any]:
        """Append one feedback record.

        Args:
            payload: The feedback to store.
            client_id: The client application that owns the record.

        Returns:
            The stored record, including its ``saved_at`` timestamp.
        """
        ...

    def list_for_user(
        self, user_id: str, limit: int = 20, saved_only: bool = False, *, client_id: str
    ) -> list[dict[str, Any]]:
        """Return a user's most recent feedback within one client, newest first.

        Args:
            user_id: Owner of the records within the client's namespace.
            limit: Maximum records to return.
            saved_only: Restrict to records flagged as saved.
            client_id: The client application whose namespace to read.

        Returns:
            Up to ``limit`` records, newest first.
        """
        ...


def client_of(record: dict[str, Any]) -> str:
    """Return the client namespace a stored record belongs to.

    Records written before G4 carry no ``client_id`` and belong to the open
    local mode's namespace.

    Args:
        record: A stored meal-plan or feedback record.

    Returns:
        The record's client_id, or ``LOCAL_CLIENT_ID`` when absent.
    """
    client_id = record.get("client_id")
    return str(client_id) if client_id else LOCAL_CLIENT_ID


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
