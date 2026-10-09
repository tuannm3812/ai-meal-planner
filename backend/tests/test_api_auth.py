"""G4 acceptance: authentication and ownership on every route that takes input.

From the agreed contract (portfolio log, 2026-10-07/08): anonymous,
wrong-scope, guessed-user_id and another-principal's-meal-id cases; rotation
keeps the namespace; a revoked key is refused by every instance; the
per-instance rate limit; and the X-Gemini-Api-Key pass-through removed.
"""

import json
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.app.agents import meal_recommendation_agent
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
KEYS = {
    "key-a": ("app-a", ALL),
    "key-a-rotated": ("app-a", ALL),
    "key-b": ("app-b", ALL),
    "key-read-only": ("app-c", ["history:read"]),
    "key-plans-only": ("app-d", ["plans:write"]),
}

# Every route that takes input, with a valid body and the scope it needs.
PROTECTED = [
    ("post", "/generate-meal-plan", {"craving": "pasta"}, "plans:write"),
    (
        "post",
        "/calorie-expenditure/predict",
        {
            "age": 30,
            "sex": "male",
            "height_cm": 175,
            "weight_kg": 75,
            "duration_minutes": 30,
            "heart_rate_bpm": 120,
            "body_temp_c": 37.5,
        },
        "plans:write",
    ),
    (
        "post",
        "/meal-feedback",
        {"user_id": "user_123", "request_id": "abcdefgh", "meal_name": "Meal", "liked": True},
        "feedback:write",
    ),
    ("get", "/meal-plans/user_123", None, "history:read"),
    ("get", "/meal-feedback/user_123", None, "history:read"),
    ("get", "/saved-meals/user_123", None, "history:read"),
]
ROUTE_IDS = [path for _, path, _, _ in PROTECTED]


def _auth(keys: dict[str, tuple[str, list[str]]]) -> AuthConfig:
    records = [
        {"client_id": client_id, "key_sha256": hash_key(key), "scopes": scopes}
        for key, (client_id, scopes) in keys.items()
    ]
    return AuthConfig.from_settings(AppSettings(_env_file=None, api_keys=json.dumps(records)))


def _keyed(container: Container, tmp_path: Path, **overrides: Any) -> Container:
    isolated = with_repositories(
        container,
        UserProfileRepository(tmp_path),
        MealPlanRepository(tmp_path),
        MealFeedbackRepository(tmp_path),
    )
    return replace(isolated, auth=_auth(KEYS), rate_limiter=RateLimiter(1000), **overrides)


@pytest.fixture(name="client")
def _client(tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        keyed = _keyed(test_client.app.state.container, tmp_path)
        app.dependency_overrides[get_container] = lambda: keyed
        yield test_client
    app.dependency_overrides.clear()


def _provider(container: Container) -> Any:
    """A zero-argument override; a defaulted lambda parameter would become a query param."""
    return lambda: container


def _call(client: TestClient, method: str, path: str, body: Any, key: str | None) -> Any:
    headers = {"X-API-Key": key} if key else {}
    if method == "get":
        return client.get(path, headers=headers)
    return client.post(path, json=body, headers=headers)


@pytest.mark.parametrize(("method", "path", "body", "scope"), PROTECTED, ids=ROUTE_IDS)
@pytest.mark.parametrize("key", [None, "wrong-key"], ids=["anonymous", "unknown-key"])
def test_every_protected_route_refuses_a_missing_or_unknown_key(
    client: TestClient, method: str, path: str, body: Any, scope: str, key: str | None
) -> None:
    response = _call(client, method, path, body, key)

    assert response.status_code == 401, response.text
    assert response.json()["code"] == "missing_or_invalid_api_key"


@pytest.mark.parametrize(("method", "path", "body", "scope"), PROTECTED, ids=ROUTE_IDS)
def test_every_protected_route_refuses_a_key_without_its_scope(
    client: TestClient, method: str, path: str, body: Any, scope: str
) -> None:
    key = "key-plans-only" if scope != "plans:write" else "key-read-only"

    response = _call(client, method, path, body, key)

    assert response.status_code == 403, response.text
    assert response.json()["code"] == "insufficient_scope"


@pytest.mark.parametrize("path", ["/", "/health"])
def test_root_and_health_stay_public(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 200


def test_a_guessed_user_id_only_reaches_the_callers_own_namespace(client: TestClient) -> None:
    generated = client.post(
        "/generate-meal-plan", json={"craving": "pasta"}, headers={"X-API-Key": "key-a"}
    )
    assert generated.status_code == 200

    mine = client.get("/meal-plans/user_123", headers={"X-API-Key": "key-a"}).json()
    theirs = client.get("/meal-plans/user_123", headers={"X-API-Key": "key-b"}).json()

    assert [i["request_id"] for i in mine["items"]] == [generated.json()["request_id"]]
    assert theirs["items"] == []


def test_feedback_on_another_clients_meal_is_not_found(client: TestClient) -> None:
    request_id = client.post(
        "/generate-meal-plan", json={"craving": "pasta"}, headers={"X-API-Key": "key-a"}
    ).json()["request_id"]
    feedback = {
        "user_id": "user_123",
        "request_id": request_id,
        "meal_name": "Pasta",
        "saved": True,
    }

    stolen = client.post("/meal-feedback", json=feedback, headers={"X-API-Key": "key-b"})
    own = client.post("/meal-feedback", json=feedback, headers={"X-API-Key": "key-a"})

    assert stolen.status_code == 404
    assert stolen.json()["code"] == "meal_not_found"
    assert own.status_code == 200
    saved_b = client.get("/saved-meals/user_123", headers={"X-API-Key": "key-b"}).json()
    assert saved_b["items"] == []


def test_feedback_on_an_unknown_request_id_is_not_found(client: TestClient) -> None:
    response = client.post(
        "/meal-feedback",
        json={
            "user_id": "user_123",
            "request_id": "never-generated",
            "meal_name": "Meal",
            "liked": True,
        },
        headers={"X-API-Key": "key-a"},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "meal_not_found"


def test_rotation_keeps_the_namespace(client: TestClient) -> None:
    request_id = client.post(
        "/generate-meal-plan", json={"craving": "pasta"}, headers={"X-API-Key": "key-a"}
    ).json()["request_id"]

    rotated = client.get("/meal-plans/user_123", headers={"X-API-Key": "key-a-rotated"}).json()

    assert [i["request_id"] for i in rotated["items"]] == [request_id]


def test_a_revoked_key_is_refused_by_every_instance(client: TestClient, tmp_path: Path) -> None:
    """Revocation: drop the key from API_KEYS and redeploy. Each instance builds
    its own AuthConfig from the redeployed settings; none may accept the old key."""
    redeployed = {k: v for k, v in KEYS.items() if k != "key-a"}
    real = client.app.state.container
    instances = [
        replace(_keyed(real, tmp_path / name), auth=_auth(redeployed))
        for name in ("instance-1", "instance-2")
    ]

    for instance in instances:
        app.dependency_overrides[get_container] = _provider(instance)
        old = client.get("/meal-plans/user_123", headers={"X-API-Key": "key-a"})
        new = client.get("/meal-plans/user_123", headers={"X-API-Key": "key-a-rotated"})
        assert old.status_code == 401
        assert new.status_code == 200


def test_the_rate_limit_is_per_client_and_says_when_to_retry(
    client: TestClient, tmp_path: Path
) -> None:
    limited = replace(_keyed(client.app.state.container, tmp_path), rate_limiter=RateLimiter(2))
    app.dependency_overrides[get_container] = lambda: limited

    statuses = [
        client.get("/meal-plans/user_123", headers={"X-API-Key": "key-a"}).status_code
        for _ in range(3)
    ]
    blocked = client.get("/meal-plans/user_123", headers={"X-API-Key": "key-a"})

    assert statuses == [200, 200, 429]
    assert blocked.json()["code"] == "rate_limited"
    assert 0 < float(blocked.headers["Retry-After"]) <= 60
    other = client.get("/meal-plans/user_123", headers={"X-API-Key": "key-b"})
    assert other.status_code == 200


def test_the_gemini_key_pass_through_is_gone(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No per-request agent is built from a caller-supplied provider key."""
    built: list[Any] = []
    original = meal_recommendation_agent.MealRecommendationAgent.__init__

    def _spy(self: Any, *args: Any, **kwargs: Any) -> None:
        built.append(kwargs.get("gemini_api_key"))
        original(self, *args, **kwargs)

    monkeypatch.setattr(meal_recommendation_agent.MealRecommendationAgent, "__init__", _spy)

    response = client.post(
        "/generate-meal-plan",
        json={"craving": "pasta"},
        headers={"X-API-Key": "key-a", "X-Gemini-Api-Key": "caller-supplied"},
    )

    assert response.status_code == 200
    assert built == []
    parameters = client.get("/openapi.json").json()["paths"]["/generate-meal-plan"]["post"]
    assert all(p["name"].lower() != "x-gemini-api-key" for p in parameters.get("parameters", []))
