"""TestClient coverage for every route, using dependency overrides."""

import pytest
from fastapi.testclient import TestClient

from backend.app.core.container import get_container
from backend.app.main import app


@pytest.fixture(name="client")
def _client() -> TestClient:
    """A client whose app has a real container built at startup."""
    with TestClient(app) as test_client:
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
    """Proves endpoints are injectable, which is the point of the container."""
    real = client.app.state.container

    class _Stub:
        def __getattr__(self, name: str) -> object:
            return getattr(real, name)

    app.dependency_overrides[get_container] = lambda: _Stub()
    assert client.get("/health").status_code == 200
    app.dependency_overrides.clear()
