"""Every route must document a response schema and honour it."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(name="client")
def _client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_every_route_declares_a_response_model(client: TestClient) -> None:
    """No endpoint may fall back to an undocumented dict."""
    undocumented = [
        route.path
        for route in app.routes
        if hasattr(route, "methods")
        and getattr(route, "response_model", None) is None
        and route.path not in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
    ]
    assert undocumented == []


def test_openapi_documents_the_meal_plan_response(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    content = schema["paths"]["/generate-meal-plan"]["post"]["responses"]["200"]["content"]
    ref = content["application/json"]["schema"]["$ref"]
    assert ref.endswith("MealPlanResponse")


def test_meal_plan_response_still_carries_every_section(client: TestClient) -> None:
    body = client.post("/generate-meal-plan", json={"craving": "pasta"}).json()
    for section in (
        "status",
        "request_id",
        "generated_at",
        "request",
        "calorie_budget",
        "meal_plan",
        "nutrition",
        "shopping_list",
        "reconciliation",
    ):
        assert section in body
