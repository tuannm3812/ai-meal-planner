"""TestClient coverage for every route, using dependency overrides."""

from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.container import get_container
from backend.app.main import app
from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)
from backend.app.services.meal_planning_service import MealPlanningService


@pytest.fixture(name="client")
def _client(tmp_path: Path) -> Iterator[TestClient]:
    """A client whose repositories write to a temporary directory.

    The app is started with its real container (real agents, real model),
    but the user-profile, meal-history and meal-feedback repositories are
    swapped for ones rooted at ``tmp_path`` so tests never touch the real
    ``database/*.json`` files. The orchestrator is rebuilt on top of the
    isolated profile repository too, since ``Container.meal_planning_service``
    otherwise keeps closing over the real one.
    """
    with TestClient(app) as test_client:
        real = test_client.app.state.container
        user_profiles = UserProfileRepository(tmp_path)
        isolated = replace(
            real,
            user_profiles=user_profiles,
            meal_history=MealPlanRepository(tmp_path),
            meal_feedback=MealFeedbackRepository(tmp_path),
            meal_planning_service=MealPlanningService(
                meal_agent=real.meal_agent,
                nutrition_agent=real.nutrition_agent,
                supermarket_agent=real.supermarket_agent,
                calorie_agent=real.calorie_agent,
                profile_repo=user_profiles,
            ),
        )
        app.dependency_overrides[get_container] = lambda: isolated
        yield test_client
    app.dependency_overrides.clear()


def test_root_lists_endpoints(client: TestClient) -> None:
    body = client.get("/").json()
    assert body["status"] == "ok"
    assert "meal_plan" in body["links"]


def test_health_reports_the_calorie_model(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["services"]["calorie_model_configured"] is True


def test_generate_meal_plan_returns_every_section(client: TestClient) -> None:
    response = client.post("/generate-meal-plan", json={"craving": "high-protein burger"})
    assert response.status_code == 200
    body = response.json()
    for section in (
        "calorie_budget",
        "meal_plan",
        "nutrition",
        "shopping_list",
        "reconciliation",
    ):
        assert section in body


def test_generate_meal_plan_rejects_a_too_short_craving(client: TestClient) -> None:
    assert client.post("/generate-meal-plan", json={"craving": "x"}).status_code == 422


def test_predict_calorie_expenditure(client: TestClient) -> None:
    response = client.post(
        "/calorie-expenditure/predict",
        json={"age": 28, "sex": "male", "height_cm": 180, "weight_kg": 80},
    )
    assert response.status_code == 200
    assert response.json()["estimated_daily_expenditure_kcal"] > 0


def test_meal_feedback_requires_at_least_one_signal(client: TestClient) -> None:
    response = client.post(
        "/meal-feedback",
        json={"user_id": "user_123", "request_id": "abcdefgh", "meal_name": "Test Meal"},
    )
    assert response.status_code == 400


def test_meal_feedback_roundtrips(client: TestClient) -> None:
    saved = client.post(
        "/meal-feedback",
        json={
            "user_id": "pytest_user",
            "request_id": "abcdefgh",
            "meal_name": "Test Meal",
            "liked": True,
            "saved": True,
        },
    )
    assert saved.status_code == 200
    listed = client.get("/meal-feedback/pytest_user").json()
    assert any(item["meal_name"] == "Test Meal" for item in listed["items"])
    savedonly = client.get("/saved-meals/pytest_user").json()
    assert all(item["saved"] for item in savedonly["items"])


def test_list_meal_plans_clamps_the_limit(client: TestClient) -> None:
    assert client.get("/meal-plans/user_123?limit=9999").json()["limit"] == 50


def test_container_override_is_honoured(client: TestClient) -> None:
    """The override must actually change the response, not merely be accepted.

    An earlier version of this test proxied every attribute back to the real
    container, so it passed identically whether the override was installed or
    ignored. This version swaps in a stub whose calorie agent has no model, and
    asserts /health reports that difference.
    """
    real = client.app.state.container
    baseline = client.get("/health").json()["services"]["calorie_model_configured"]
    assert baseline is True, "precondition: the real container has a loaded model"

    class _NoModelAgent:
        model = None
        model_warning = "stubbed out"

    stub = replace(real, calorie_agent=_NoModelAgent())
    app.dependency_overrides[get_container] = lambda: stub
    try:
        overridden = client.get("/health").json()["services"]
        assert overridden["calorie_model_configured"] is False
        assert overridden["calorie_model_warning"] == "stubbed out"
    finally:
        app.dependency_overrides.clear()

    # And the override is genuinely undone afterwards.
    assert client.get("/health").json()["services"]["calorie_model_configured"] is True
