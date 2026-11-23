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


# --- Slice 3: the account routes end to end on the emulator ---------------------


@pytest.fixture(name="api")
def _api(client, tmp_path):  # noqa: ANN001, ANN202
    from dataclasses import replace

    from fastapi.testclient import TestClient

    from backend.app.core.auth import AuthConfig, RateLimiter
    from backend.app.core.config import AppSettings
    from backend.app.core.container import get_container, with_repositories
    from backend.app.main import app
    from backend.app.repositories.firestore_store import (
        FirestoreMealFeedbackRepository,
        FirestoreMealPlanRepository,
        FirestoreUserProfileRepository,
    )

    class _Verifier:
        def verify(self, token: str | None) -> str | None:
            return {"token-alice": "uid-alice", "token-bob": "uid-bob"}.get(token or "")

    with TestClient(app) as test_client:
        base = with_repositories(
            test_client.app.state.container,
            FirestoreUserProfileRepository(client),
            FirestoreMealPlanRepository(client),
            FirestoreMealFeedbackRepository(client),
        )
        # A hosted deployment on Firestore: history is kept (DEC-43).
        hosted = AppSettings(_env_file=None, hosted_mode=True, storage_backend="firestore")
        container = replace(
            base,
            settings=hosted,
            auth=AuthConfig(),
            rate_limiter=RateLimiter(1000),
            token_verifier=_Verifier(),
        )
        app.dependency_overrides[get_container] = lambda: container
        yield test_client
    app.dependency_overrides.clear()


ALICE = {"Authorization": "Bearer token-alice"}
BOB = {"Authorization": "Bearer token-bob"}
PROFILE = {"profile": {"goal": "lose", "age": "41", "avoid": ["vegan"]}, "location": "Ashfield"}


def test_a_profile_is_saved_and_read_back_per_user(api) -> None:  # noqa: ANN001
    assert api.get("/me/profile", headers=ALICE).json()["code"] == "profile_not_found"

    saved = api.put("/me/profile", json=PROFILE, headers=ALICE)
    read = api.get("/me/profile", headers=ALICE)

    assert saved.status_code == 200, saved.text
    assert read.json()["profile"]["goal"] == "lose"
    assert read.json()["profile"]["avoid"] == ["vegan"]
    assert read.json()["location"] == "Ashfield"
    assert api.get("/me/profile", headers=BOB).status_code == 404


def test_a_hosted_deployment_on_firestore_keeps_history(api) -> None:  # noqa: ANN001
    plan = api.post("/generate-meal-plan", json={"craving": "pasta"}, headers=ALICE).json()
    saved = api.post(
        "/meal-feedback",
        json={
            "user_id": "ignored",
            "request_id": plan["request_id"],
            "meal_name": "Pasta",
            "saved": True,
        },
        headers=ALICE,
    )

    assert saved.status_code == 200, saved.text
    history = api.get("/meal-plans/uid-alice", headers=ALICE).json()["items"]
    assert [item["request_id"] for item in history] == [plan["request_id"]]
    assert len(api.get("/saved-meals/uid-alice", headers=ALICE).json()["items"]) == 1


def test_deleting_an_account_removes_only_that_users_records(api) -> None:  # noqa: ANN001
    mine = api.post("/generate-meal-plan", json={"craving": "pasta"}, headers=ALICE).json()
    theirs = api.post("/generate-meal-plan", json={"craving": "pasta"}, headers=BOB).json()
    api.post(
        "/meal-feedback",
        json={"request_id": mine["request_id"], "meal_name": "Pasta", "liked": True},
        headers=ALICE,
    )
    api.put("/me/profile", json=PROFILE, headers=ALICE)
    api.put("/me/profile", json=PROFILE, headers=BOB)

    deleted = api.delete("/me", headers=ALICE)

    assert deleted.json() == {"status": "deleted", "deleted": {"plans": 1, "feedback": 1}}
    assert api.get("/meal-plans/uid-alice", headers=ALICE).json()["items"] == []
    assert api.get("/meal-feedback/uid-alice", headers=ALICE).json()["items"] == []
    assert api.get("/me/profile", headers=ALICE).status_code == 404
    # Feedback can no longer find the deleted plan through the request-id index.
    again = api.post(
        "/meal-feedback",
        json={"request_id": mine["request_id"], "meal_name": "Pasta", "liked": True},
        headers=ALICE,
    )
    assert again.status_code == 404
    # Bob is untouched.
    bobs = api.get("/meal-plans/uid-bob", headers=BOB).json()["items"]
    assert [item["request_id"] for item in bobs] == [theirs["request_id"]]
    assert api.get("/me/profile", headers=BOB).status_code == 200


def test_deleting_an_account_with_nothing_stored_succeeds(api) -> None:  # noqa: ANN001
    response = api.delete("/me", headers=ALICE)

    assert response.json() == {"status": "deleted", "deleted": {"plans": 0, "feedback": 0}}
