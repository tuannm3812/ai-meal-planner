"""DEC-43: what only the Firestore backend needs, on the local emulator.

The shared behaviour is in ``test_repository_contract.py``. These cover id
escaping, payloads Firestore could not hold natively, and the factory.
"""

import os
from uuid import uuid4

import pytest

pytestmark = [
    pytest.mark.skipif(
        not os.environ.get("FIRESTORE_EMULATOR_HOST"),
        reason="needs the Firestore emulator (FIRESTORE_EMULATOR_HOST); CI runs it",
    ),
    pytest.mark.allow_network,
]


@pytest.fixture(name="client")
def _client():  # noqa: ANN202 - a google.cloud.firestore.Client
    from google.cloud import firestore

    return firestore.Client(project=f"store-{uuid4().hex[:12]}")


def test_a_slash_in_a_user_id_cannot_reach_another_path(client) -> None:  # noqa: ANN001
    from backend.app.repositories.firestore_store import FirestoreMealPlanRepository

    store = FirestoreMealPlanRepository(client)
    store.save({"request": {"user_id": "a/plans/x"}, "n": 1}, client_id="local")
    store.save({"request": {"user_id": "a"}, "n": 2}, client_id="local")

    assert [i["n"] for i in store.list_for_user("a/plans/x", client_id="local")] == [1]
    assert [i["n"] for i in store.list_for_user("a", client_id="local")] == [2]


def test_reserved_looking_ids_are_stored(client) -> None:  # noqa: ANN001
    from backend.app.repositories.firestore_store import FirestoreMealFeedbackRepository

    store = FirestoreMealFeedbackRepository(client)
    for user_id in ["", ".", "..", "__name__"]:
        store.save({"user_id": user_id, "n": user_id}, client_id="__c__")

    for user_id in ["", ".", "..", "__name__"]:
        assert [i["n"] for i in store.list_for_user(user_id, client_id="__c__")] == [user_id]


def test_a_payload_firestore_cannot_hold_natively_round_trips(client) -> None:  # noqa: ANN001
    from backend.app.repositories.firestore_store import FirestoreMealPlanRepository

    store = FirestoreMealPlanRepository(client)
    payload = {
        "request": {"user_id": "u1"},
        "request_id": "req/1",
        "grid": [[1, 2], [3.5, None]],
        "unicode": "phở",
    }
    store.save(payload, client_id="local")

    found = store.find_by_request_id("req/1", client_id="local")
    assert found is not None
    assert found["grid"] == [[1, 2], [3.5, None]]
    assert found["unicode"] == "phở"


def test_the_factory_builds_firestore_repositories(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.core.config import AppSettings
    from backend.app.repositories.factory import build_repositories
    from backend.app.repositories.firestore_store import (
        FirestoreMealFeedbackRepository,
        FirestoreMealPlanRepository,
        FirestoreUserProfileRepository,
    )

    settings = AppSettings(
        _env_file=None, storage_backend="firestore", firebase_project_id="demo-factory"
    )
    profiles, plans, feedback = build_repositories(settings)

    assert isinstance(profiles, FirestoreUserProfileRepository)
    assert isinstance(plans, FirestoreMealPlanRepository)
    assert isinstance(feedback, FirestoreMealFeedbackRepository)
    assert plans.client.project == "demo-factory"
