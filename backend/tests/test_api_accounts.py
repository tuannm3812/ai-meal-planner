"""DEC-43: signed-in users reach only their own records, by token uid.

A fake verifier maps token strings to uids, so these tests cover the routes'
rules; ``test_firebase_auth.py`` covers the token checks themselves.
"""

import json
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.auth import AuthConfig, RateLimiter, hash_key
from backend.app.core.config import AppSettings
from backend.app.core.container import Container, get_container, with_repositories
from backend.app.main import app
from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)

ALL = ["plans:write", "feedback:write", "history:read"]
TOKENS = {"token-alice": "uid-alice", "token-bob": "uid-bob"}


class _FakeVerifier:
    def verify(self, token: str | None) -> str | None:
        return TOKENS.get(token or "")


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _keyed_auth() -> AuthConfig:
    records = [{"client_id": "app-a", "key_sha256": hash_key("key-a"), "scopes": ALL}]
    return AuthConfig.from_settings(AppSettings(_env_file=None, api_keys=json.dumps(records)))


def _container(base: Container, tmp_path: Path, **overrides: object) -> Container:
    isolated = with_repositories(
        base,
        UserProfileRepository(tmp_path),
        MealPlanRepository(tmp_path),
        MealFeedbackRepository(tmp_path),
    )
    defaults: dict[str, object] = {
        "auth": _keyed_auth(),
        "rate_limiter": RateLimiter(1000),
        "token_verifier": _FakeVerifier(),
    }
    return replace(isolated, **{**defaults, **overrides})


@pytest.fixture(name="client")
def _client(tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        container = _container(test_client.app.state.container, tmp_path)
        app.dependency_overrides[get_container] = lambda: container
        yield test_client
    app.dependency_overrides.clear()


def _plan(client: TestClient, token: str, user_id: str = "user_123") -> dict:
    response = client.post(
        "/generate-meal-plan",
        json={"craving": "pasta", "user_id": user_id},
        headers=_bearer(token),
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_a_plan_is_stored_under_the_token_uid_not_the_body_user_id(client: TestClient) -> None:
    plan = _plan(client, "token-alice", user_id="uid-bob")

    assert plan["request"]["user_id"] == "uid-alice"
    mine = client.get("/meal-plans/uid-alice", headers=_bearer("token-alice")).json()
    bobs = client.get("/meal-plans/uid-bob", headers=_bearer("token-bob")).json()
    assert [item["request_id"] for item in mine["items"]] == [plan["request_id"]]
    assert bobs["items"] == []


@pytest.mark.parametrize(
    "path", ["/meal-plans/uid-bob", "/meal-feedback/uid-bob", "/saved-meals/uid-bob"]
)
def test_a_signed_in_user_cannot_read_another_users_history(client: TestClient, path: str) -> None:
    response = client.get(path, headers=_bearer("token-alice"))

    assert response.status_code == 403
    assert response.json()["code"] == "insufficient_scope"


def test_feedback_is_stored_under_the_token_uid(client: TestClient) -> None:
    request_id = _plan(client, "token-alice")["request_id"]
    feedback = {
        "user_id": "uid-bob",
        "request_id": request_id,
        "meal_name": "Pasta",
        "saved": True,
    }

    saved = client.post("/meal-feedback", json=feedback, headers=_bearer("token-alice"))

    assert saved.status_code == 200, saved.text
    assert saved.json()["item"]["user_id"] == "uid-alice"
    mine = client.get("/saved-meals/uid-alice", headers=_bearer("token-alice")).json()
    assert [item["request_id"] for item in mine["items"]] == [request_id]


def test_one_user_cannot_attach_feedback_to_another_users_meal(client: TestClient) -> None:
    request_id = _plan(client, "token-alice")["request_id"]
    feedback = {"user_id": "x" * 3, "request_id": request_id, "meal_name": "Pasta", "liked": True}

    stolen = client.post("/meal-feedback", json=feedback, headers=_bearer("token-bob"))

    assert stolen.status_code == 404
    assert stolen.json()["code"] == "meal_not_found"


def test_accounts_and_api_key_clients_have_separate_namespaces(client: TestClient) -> None:
    _plan(client, "token-alice")

    keyed = client.get("/meal-plans/uid-alice", headers={"X-API-Key": "key-a"}).json()

    assert keyed["items"] == []


@pytest.mark.parametrize(
    "headers",
    [
        _bearer("token-unknown"),
        {"Authorization": "Basic dXNlcjpwYXNz"},
        {**_bearer("token-alice"), "X-API-Key": "key-a"},
    ],
    ids=["unknown-token", "not-bearer", "both-credentials"],
)
def test_a_bad_or_ambiguous_credential_is_refused(
    client: TestClient, headers: dict[str, str]
) -> None:
    response = client.get("/meal-plans/uid-alice", headers=headers)

    assert response.status_code == 401
    assert response.json()["code"] == "missing_or_invalid_api_key"


def test_a_token_is_refused_when_accounts_are_off(tmp_path: Path) -> None:
    with TestClient(app) as test_client:
        container = _container(test_client.app.state.container, tmp_path, token_verifier=None)
        app.dependency_overrides[get_container] = lambda: container
        try:
            response = test_client.get("/meal-plans/uid-alice", headers=_bearer("token-alice"))
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 401


def test_the_rate_limit_counts_each_user_apart(tmp_path: Path) -> None:
    with TestClient(app) as test_client:
        container = _container(
            test_client.app.state.container, tmp_path, rate_limiter=RateLimiter(1)
        )
        app.dependency_overrides[get_container] = lambda: container
        try:
            first = test_client.get("/meal-plans/uid-alice", headers=_bearer("token-alice"))
            again = test_client.get("/meal-plans/uid-alice", headers=_bearer("token-alice"))
            other = test_client.get("/meal-plans/uid-bob", headers=_bearer("token-bob"))
        finally:
            app.dependency_overrides.clear()

    assert (first.status_code, again.status_code, other.status_code) == (200, 429, 200)


def test_accounts_are_rate_limited_even_in_open_local_mode(tmp_path: Path) -> None:
    with TestClient(app) as test_client:
        container = _container(
            test_client.app.state.container,
            tmp_path,
            auth=AuthConfig(),
            rate_limiter=RateLimiter(1),
        )
        app.dependency_overrides[get_container] = lambda: container
        try:
            first = test_client.get("/meal-plans/uid-alice", headers=_bearer("token-alice"))
            again = test_client.get("/meal-plans/uid-alice", headers=_bearer("token-alice"))
            local = test_client.get("/meal-plans/user_123")
        finally:
            app.dependency_overrides.clear()

    assert (first.status_code, again.status_code, local.status_code) == (200, 429, 200)


def test_no_api_key_may_claim_the_accounts_namespace() -> None:
    records = [{"client_id": "accounts", "key_sha256": hash_key("k"), "scopes": ALL}]

    with pytest.raises(ValueError, match="reserved"):
        AuthConfig.from_settings(AppSettings(_env_file=None, api_keys=json.dumps(records)))


# --- Slice 3: account routes and hosted history ---------------------------------

PROFILE = {
    "profile": {
        "goal": "lose",
        "age": "41",
        "sex": "female",
        "heightCm": "165",
        "weightKg": "70",
        "activity": "1.375",
        "workout": "rest",
        "workoutMinutes": "30",
        "heartRate": "",
        "avoid": ["dairy-free"],
    },
    "location": "Earlwood, NSW",
}


@pytest.mark.parametrize(
    ("method", "path"), [("get", "/me/profile"), ("put", "/me/profile"), ("delete", "/me")]
)
def test_an_api_key_client_has_no_account(client: TestClient, method: str, path: str) -> None:
    response = client.request(method, path, json=PROFILE, headers={"X-API-Key": "key-a"})

    assert response.status_code == 403
    assert response.json()["code"] == "insufficient_scope"


@pytest.mark.parametrize(
    ("method", "path"), [("get", "/me/profile"), ("put", "/me/profile"), ("delete", "/me")]
)
def test_account_routes_need_firestore(client: TestClient, method: str, path: str) -> None:
    response = client.request(method, path, json=PROFILE, headers=_bearer("token-alice"))

    assert response.status_code == 501
    assert response.json()["code"] == "accounts_unavailable"


@pytest.mark.parametrize(
    "body",
    [
        {**PROFILE, "extra": 1},
        {**PROFILE, "profile": {**PROFILE["profile"], "email": "a@b.c"}},
        {**PROFILE, "profile": {**PROFILE["profile"], "age": "1" * 9}},
        {**PROFILE, "profile": {**PROFILE["profile"], "avoid": ["x"] * 17}},
    ],
    ids=["unknown-top-level", "unknown-profile-field", "long-value", "too-many-avoids"],
)
def test_a_profile_outside_the_apps_fields_is_refused(client: TestClient, body: dict) -> None:
    response = client.put("/me/profile", json=body, headers=_bearer("token-alice"))

    assert response.status_code == 422


def test_hosted_mode_on_firestore_keeps_history_and_says_so() -> None:
    from backend.app.core.config import AppSettings

    sqlite = AppSettings(_env_file=None, hosted_mode=True)
    firestore = AppSettings(_env_file=None, hosted_mode=True, storage_backend="firestore")
    local = AppSettings(_env_file=None)

    assert (sqlite.keeps_history, firestore.keeps_history, local.keeps_history) == (
        False,
        True,
        True,
    )


def test_health_reports_whether_history_is_kept(client: TestClient) -> None:
    services = client.get("/health").json()["services"]

    assert services["history_enabled"] is True
