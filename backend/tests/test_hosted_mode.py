"""G6: hosted mode refuses instance-local history instead of pretending to keep it.

Contract (portfolio log, 2026-10-08, point 2): instance-local SQLite is not
shared across instances, so a hosted deployment refuses history and feedback
reads and writes with 501 and the stable code history_disabled_stateless,
behind one setting reported by /health. Best-effort reads are not offered.
Local, non-hosted mode keeps serving history as before.
"""

import json
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path
from typing import Any

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

KEY = "hosted-key"
HEADERS = {"X-API-Key": KEY}
HISTORY_ROUTES = [
    ("get", "/meal-plans/user_123", None),
    ("get", "/meal-feedback/user_123", None),
    ("get", "/saved-meals/user_123", None),
    (
        "post",
        "/meal-feedback",
        {"user_id": "user_123", "request_id": "abcdefgh", "meal_name": "Meal", "liked": True},
    ),
]


def _instance(real: Container, data_dir: Path, *, hosted: bool) -> Container:
    """One API instance: its own instance-local storage, as on a real host."""
    records = [
        {
            "client_id": "app",
            "key_sha256": hash_key(KEY),
            "scopes": ["plans:write", "feedback:write", "history:read"],
        }
    ]
    settings = AppSettings(
        _env_file=None, hosted_mode=hosted, api_keys=json.dumps(records), storage_backend="json"
    )
    isolated = with_repositories(
        real,
        UserProfileRepository(data_dir),
        MealPlanRepository(data_dir),
        MealFeedbackRepository(data_dir),
    )
    return replace(
        isolated,
        settings=settings,
        auth=AuthConfig.from_settings(settings),
        rate_limiter=RateLimiter(1000),
    )


def _use(container: Container) -> None:
    app.dependency_overrides[get_container] = lambda: container


@pytest.fixture(name="client")
def _client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _call(client: TestClient, method: str, path: str, body: Any, headers: dict[str, str]) -> Any:
    if method == "get":
        return client.get(path, headers=headers)
    return client.post(path, json=body, headers=headers)


@pytest.mark.parametrize(("method", "path", "body"), HISTORY_ROUTES, ids=lambda v: str(v))
def test_two_hosted_instances_both_refuse_history_and_feedback(
    client: TestClient, tmp_path: Path, method: str, path: str, body: Any
) -> None:
    """Every history read and write, routed to either instance, is refused."""
    instances = [
        _instance(client.app.state.container, tmp_path / name, hosted=True)
        for name in ("instance-1", "instance-2")
    ]

    for instance in instances:
        _use(instance)
        response = _call(client, method, path, body, HEADERS)
        assert response.status_code == 501, response.text
        assert response.json()["code"] == "history_disabled_stateless"


def test_hosted_mode_still_authenticates_first(client: TestClient, tmp_path: Path) -> None:
    """An anonymous caller learns nothing more than it would from /health."""
    _use(_instance(client.app.state.container, tmp_path, hosted=True))

    assert client.get("/meal-plans/user_123").status_code == 401


def test_hosted_mode_still_plans_meals_but_stores_nothing(
    client: TestClient, tmp_path: Path
) -> None:
    hosted = _instance(client.app.state.container, tmp_path, hosted=True)
    _use(hosted)

    generated = client.post("/generate-meal-plan", json={"craving": "pasta"}, headers=HEADERS)

    assert generated.status_code == 200
    assert generated.json()["plan_status"] in {"matched", "fallback"}
    assert hosted.meal_history.list_for_user("user_123", client_id="app") == []


def test_health_is_public_and_reports_hosted_mode(client: TestClient, tmp_path: Path) -> None:
    _use(_instance(client.app.state.container, tmp_path, hosted=True))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["services"]["hosted_mode"] is True


def test_local_mode_still_serves_history(client: TestClient, tmp_path: Path) -> None:
    _use(_instance(client.app.state.container, tmp_path, hosted=False))

    request_id = client.post(
        "/generate-meal-plan", json={"craving": "pasta"}, headers=HEADERS
    ).json()["request_id"]
    history = client.get("/meal-plans/user_123", headers=HEADERS).json()

    assert [item["request_id"] for item in history["items"]] == [request_id]
