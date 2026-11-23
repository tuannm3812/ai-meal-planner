"""Firestore-backed repositories: storage every hosted instance shares (DEC-43).

Selected by ``STORAGE_BACKEND=firestore``. Unlike a SQLite file, which each Cloud
Run instance keeps to itself and loses on restart (DEC-10), Firestore is one
store for every instance, so a hosted deployment can keep history.

Layout, with every id escaped so no caller value can add a path segment::

    namespaces/{client}/users/{user}                     account profile
    namespaces/{client}/users/{user}/plans/{request_id}
    namespaces/{client}/users/{user}/feedback/{auto id}
    namespaces/{client}/plan_index/{request_id}          -> which user holds it

A record is stored as one JSON string (``payload_json``) beside the few fields
queries need. Firestore cannot hold every JSON shape (an array of arrays, for
one), and a stored API response must come back exactly as it went in.

``sort_key`` orders records newest first. It is nanoseconds since the epoch,
bumped by one when two writes in this process land on the same value, which is
the ordering an autoincrement id gives the SQL backend.
"""

import json
import time
from datetime import UTC, datetime
from threading import Lock
from typing import Any
from urllib.parse import quote

from google.cloud import firestore

from .base import owner_of_feedback, owner_of_meal_plan
from .sql.repositories import DEFAULT_PROFILE

NAMESPACES = "namespaces"
_BATCH_LIMIT = 400  # Firestore allows 500 writes per batch


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _doc_id(kind: str, value: str) -> str:
    """Escape a caller value into one safe document id.

    The prefix keeps the id clear of Firestore's reserved forms (empty, ``.``,
    ``..`` and ``__name__``-style ids), and ``quote`` turns ``/`` into ``%2F``.
    """
    return f"{kind}:{quote(value, safe='')}"


class _SortKeys:
    """Strictly increasing nanosecond keys within this process."""

    def __init__(self) -> None:
        self._last = 0
        self._lock = Lock()

    def next(self) -> int:
        with self._lock:
            self._last = max(time.time_ns(), self._last + 1)
            return self._last


_SORT_KEYS = _SortKeys()


class _Namespaced:
    """Shared path helpers for the three repositories."""

    def __init__(self, client: firestore.Client) -> None:
        """Store the client.

        Args:
            client: A Firestore client. It honours ``FIRESTORE_EMULATOR_HOST``.
        """
        self.client = client

    def _namespace(self, client_id: str) -> firestore.DocumentReference:
        return self.client.collection(NAMESPACES).document(_doc_id("c", client_id))

    def _user(self, client_id: str, user_id: str) -> firestore.DocumentReference:
        return self._namespace(client_id).collection("users").document(_doc_id("u", user_id))


def _load(snapshot: Any) -> dict[str, Any]:
    return json.loads(snapshot.get("payload_json"))


class FirestoreUserProfileRepository(_Namespaced):
    """Reads user profiles, falling back to the built-in default."""

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        """Return the default profile, as the SQL backend does.

        The planner's stored-biometrics profile is not written by any route.
        A signed-in user's own profile is the separate account record below
        (``get_account``), which the React app sends with each plan.

        Args:
            user_id: Accepted for protocol compatibility; unused.

        Returns:
            A copy of the default profile.
        """
        return dict(DEFAULT_PROFILE)

    def get_account(self, user_id: str, *, client_id: str) -> dict[str, Any] | None:
        """Return the user's saved profile and location, or None if never saved.

        Args:
            user_id: The account's uid.
            client_id: The namespace, ``accounts`` for signed-in users.

        Returns:
            ``{"profile", "location", "updated_at"}``, or None.
        """
        snapshot = self._user(client_id, user_id).get()
        if not snapshot.exists or snapshot.get("account_json") is None:
            return None
        return json.loads(snapshot.get("account_json"))

    def save_account(
        self, user_id: str, profile: dict[str, Any], location: str | None, *, client_id: str
    ) -> dict[str, Any]:
        """Replace the user's saved profile and location.

        Args:
            user_id: The account's uid.
            profile: The app's profile fields.
            location: Where the person shops, if given.
            client_id: The namespace, ``accounts`` for signed-in users.

        Returns:
            The stored record, as ``get_account`` would return it.
        """
        record = {"profile": profile, "location": location, "updated_at": _now()}
        self._user(client_id, user_id).set({"account_json": json.dumps(record)})
        return record

    def delete_user(self, user_id: str, *, client_id: str) -> dict[str, int]:
        """Delete the user's profile, plans, plan index entries and feedback.

        Firestore does not delete subcollections with their parent, so each
        record is deleted by name, in batches under Firestore's 500-write limit.

        Args:
            user_id: The account's uid.
            client_id: The namespace, ``accounts`` for signed-in users.

        Returns:
            How many plans and feedback records were deleted.
        """
        user = self._user(client_id, user_id)
        index = self._namespace(client_id).collection("plan_index")
        writes: list[Any] = []
        plans = 0
        for snapshot in user.collection("plans").stream():
            plans += 1
            writes.append(snapshot.reference)
            request_id = _load(snapshot).get("request_id")
            if isinstance(request_id, str):
                entry = index.document(_doc_id("r", request_id))
                held = entry.get()
                # The index names the latest holder; leave another user's entry.
                if held.exists and held.get("user_id") == user_id:
                    writes.append(entry)
        feedback = 0
        for snapshot in user.collection("feedback").stream():
            feedback += 1
            writes.append(snapshot.reference)
        writes.append(user)
        for start in range(0, len(writes), _BATCH_LIMIT):
            batch = self.client.batch()
            for reference in writes[start : start + _BATCH_LIMIT]:
                batch.delete(reference)
            batch.commit()
        return {"plans": plans, "feedback": feedback}


class FirestoreMealPlanRepository(_Namespaced):
    """Stores meal plans in Firestore."""

    def save(self, payload: dict[str, Any], *, client_id: str) -> None:
        """Append one meal-plan response, and index it by request id.

        Args:
            payload: The full API response to store.
            client_id: The client application that owns the record.
        """
        record = {"saved_at": _now(), **payload, "client_id": client_id}
        user_id = owner_of_meal_plan(payload)
        request_id = payload.get("request_id")
        plans = self._user(client_id, user_id).collection("plans")
        plan = (
            plans.document(_doc_id("r", request_id))
            if isinstance(request_id, str)
            else plans.document()
        )
        batch = self.client.batch()
        batch.set(
            plan,
            {
                "user_id": user_id,
                "sort_key": _SORT_KEYS.next(),
                "payload_json": json.dumps(record),
            },
        )
        if isinstance(request_id, str):
            batch.set(
                self._namespace(client_id)
                .collection("plan_index")
                .document(_doc_id("r", request_id)),
                {"user_id": user_id},
            )
        batch.commit()

    def list_for_user(
        self, user_id: str, limit: int = 20, *, client_id: str
    ) -> list[dict[str, Any]]:
        """Return a user's most recent meal plans within one client, newest first.

        Args:
            user_id: Owner of the records within the client's namespace.
            limit: Maximum records to return.
            client_id: The client application whose namespace to read.

        Returns:
            Up to ``limit`` records, newest first.
        """
        query = (
            self._user(client_id, user_id)
            .collection("plans")
            .order_by("sort_key", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        return [_load(snapshot) for snapshot in query.stream()]

    def find_by_request_id(self, request_id: str, *, client_id: str) -> dict[str, Any] | None:
        """Return the client's meal plan with this request id, if any.

        Args:
            request_id: The id returned when the plan was generated.
            client_id: The client application whose namespace to search.

        Returns:
            The stored record, or None if this client has no such plan.
        """
        index = (
            self._namespace(client_id)
            .collection("plan_index")
            .document(_doc_id("r", request_id))
            .get()
        )
        if not index.exists:
            return None
        plan = (
            self._user(client_id, index.get("user_id"))
            .collection("plans")
            .document(_doc_id("r", request_id))
            .get()
        )
        return _load(plan) if plan.exists else None


class FirestoreMealFeedbackRepository(_Namespaced):
    """Stores meal feedback in Firestore."""

    def save(self, payload: dict[str, Any], *, client_id: str) -> dict[str, Any]:
        """Append one feedback record.

        Args:
            payload: The feedback to store.
            client_id: The client application that owns the record.

        Returns:
            The stored record, including its ``saved_at`` timestamp.
        """
        record = {"saved_at": _now(), **payload, "client_id": client_id}
        self._user(client_id, owner_of_feedback(payload)).collection("feedback").document().set(
            {
                "saved": bool(payload.get("saved", False)),
                "sort_key": _SORT_KEYS.next(),
                "payload_json": json.dumps(record),
            }
        )
        return record

    def list_for_user(
        self, user_id: str, limit: int = 20, saved_only: bool = False, *, client_id: str
    ) -> list[dict[str, Any]]:
        """Return a user's most recent feedback within one client, newest first.

        ``saved_only`` is a query filter, applied before the limit. On the real
        service it uses the composite index in ``firestore.indexes.json``.

        Args:
            user_id: Owner of the records within the client's namespace.
            limit: Maximum records to return.
            saved_only: Restrict to records flagged as saved.
            client_id: The client application whose namespace to read.

        Returns:
            Up to ``limit`` records, newest first.
        """
        query: Any = self._user(client_id, user_id).collection("feedback")
        if saved_only:
            query = query.where(filter=firestore.FieldFilter("saved", "==", True))
        query = query.order_by("sort_key", direction=firestore.Query.DESCENDING).limit(limit)
        return [_load(snapshot) for snapshot in query.stream()]
