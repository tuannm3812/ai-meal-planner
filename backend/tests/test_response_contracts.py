"""Every route must document a response schema and honour it."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.container import get_container, with_repositories
from backend.app.main import app
from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)


@pytest.fixture(name="client")
def _client(tmp_path: Path) -> Iterator[TestClient]:
    """A client whose repositories write to a temporary directory.

    ``test_meal_plan_response_still_carries_every_section`` below calls
    ``/generate-meal-plan``, which persists to meal history. Without this
    isolation it would append to the real ``database/meal_history.json``, the
    same real-data-store problem fixed for ``test_api_endpoints.py``.
    """
    with TestClient(app) as test_client:
        isolated = with_repositories(
            test_client.app.state.container,
            UserProfileRepository(tmp_path),
            MealPlanRepository(tmp_path),
            MealFeedbackRepository(tmp_path),
        )
        app.dependency_overrides[get_container] = lambda: isolated
        yield test_client
    app.dependency_overrides.clear()


def test_every_route_declares_a_response_model(client: TestClient) -> None:
    """Every application route must document a response schema in OpenAPI.

    This walks the OpenAPI document rather than ``app.routes``. This FastAPI
    version wraps included routers in ``_IncludedRouter`` objects that expose
    neither ``.path`` nor ``.methods``, so scanning ``app.routes`` sees only
    FastAPI's own four built-ins - and a test written that way passes even when
    no endpoint declares a model at all.
    """
    spec = client.get("/openapi.json").json()
    undocumented = [
        f"{verb.upper()} {path}"
        for path, operations in spec["paths"].items()
        for verb, operation in operations.items()
        if "$ref" not in operation["responses"]["200"]["content"]["application/json"]["schema"]
    ]
    assert undocumented == [], f"routes without a response schema: {undocumented}"
    assert len(spec["paths"]) == 8, f"expected 8 documented paths, got {len(spec['paths'])}"


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
