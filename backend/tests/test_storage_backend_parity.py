"""Switching STORAGE_BACKEND must not change any API response."""

from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import AppSettings
from backend.app.core.container import get_container
from backend.app.main import app
from backend.app.repositories.factory import build_repositories


def _client_for(backend: str, tmp_path: Path) -> TestClient:
    """Build a client whose repositories use the given backend."""
    client = TestClient(app)
    client.__enter__()
    settings = AppSettings(storage_backend=backend)
    profiles, plans, feedback = build_repositories(settings, data_dir=tmp_path)
    isolated = replace(
        app.state.container,
        user_profiles=profiles,
        meal_history=plans,
        meal_feedback=feedback,
    )
    app.dependency_overrides[get_container] = lambda: isolated
    return client


@pytest.mark.parametrize("backend", ["json", "sqlite"])
def test_feedback_roundtrip_is_identical(backend: str, tmp_path: Path) -> None:
    client = _client_for(backend, tmp_path)
    try:
        saved = client.post(
            "/meal-feedback",
            json={
                "user_id": "parity_user",
                "request_id": "abcdefgh",
                "meal_name": "Parity Meal",
                "liked": True,
                "saved": True,
            },
        )
        assert saved.status_code == 200
        listed = client.get("/meal-feedback/parity_user").json()
        assert [item["meal_name"] for item in listed["items"]] == ["Parity Meal"]
        only_saved = client.get("/saved-meals/parity_user").json()
        assert all(item["saved"] for item in only_saved["items"])
        assert len(only_saved["items"]) == 1
    finally:
        app.dependency_overrides.clear()
        client.__exit__(None, None, None)


@pytest.mark.parametrize("backend", ["json", "sqlite"])
def test_meal_plan_history_roundtrip_is_identical(backend: str, tmp_path: Path) -> None:
    client = _client_for(backend, tmp_path)
    try:
        generated = client.post(
            "/generate-meal-plan", json={"user_id": "parity_user", "craving": "pasta"}
        )
        assert generated.status_code == 200
        history = client.get("/meal-plans/parity_user").json()
        assert history["items"], "the generated plan should be listed"
        assert history["items"][0]["request"]["user_id"] == "parity_user"
    finally:
        app.dependency_overrides.clear()
        client.__exit__(None, None, None)
