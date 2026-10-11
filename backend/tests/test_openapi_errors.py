"""The contract documents authentication and every domain error response.

Codex, 2026-10-11 (item G review): the generated contract had no security
scheme and listed only 200 and 422, not the authentication and domain errors
the API returns. They are now declared through FastAPI's own generation. The
security scheme comes from the X-API-Key dependency, and each route's error
responses are built from the domain exception classes. No hand-maintained
specification is involved.

These tests read the committed docs/openapi.json, which
test_openapi_contract.py ties to the code.
"""

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.errors import error_responses
from backend.app.core.exceptions import (
    AuthenticationRequired,
    HistoryDisabled,
    InsufficientScope,
    MealPlanningError,
    MealPlanNotFound,
    NutritionProviderError,
    RateLimited,
    RetrievalUnavailable,
    register_exception_handlers,
)
from backend.app.schemas.responses import ErrorResponse

CONTRACT = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
SCHEME = "ApiKeyAuth"
AUTH = {"401", "403", "429"}
EXPECTED: dict[tuple[str, str], set[str]] = {
    ("get", "/"): set(),
    ("get", "/health"): set(),
    ("post", "/generate-meal-plan"): AUTH | {"502", "503"},
    ("post", "/calorie-expenditure/predict"): AUTH,
    ("get", "/meal-plans/{user_id}"): AUTH | {"501"},
    ("post", "/meal-feedback"): AUTH | {"400", "404", "501"},
    ("get", "/meal-feedback/{user_id}"): AUTH | {"501"},
    ("get", "/saved-meals/{user_id}"): AUTH | {"501"},
}
PUBLIC = {("get", "/"), ("get", "/health")}
# The one error not raised as a domain error: the route's own HTTPException,
# whose body is FastAPI's {"detail": ...}.
PLAIN_DETAIL = {("post", "/meal-feedback", "400")}


@pytest.fixture(name="contract", scope="module")
def _contract() -> dict[str, object]:
    return json.loads(CONTRACT.read_text())


def test_the_api_key_is_a_declared_security_scheme(contract: dict) -> None:
    assert contract["components"]["securitySchemes"] == {
        SCHEME: {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "A client application's API key (README §8.1).",
        }
    }


@pytest.mark.parametrize(("method", "path"), sorted(EXPECTED))
def test_each_route_declares_its_security_and_error_responses(
    contract: dict, method: str, path: str
) -> None:
    operation = contract["paths"][path][method]
    errors = {status for status in operation["responses"] if status not in {"200", "422"}}

    assert errors == EXPECTED[(method, path)]
    if (method, path) in PUBLIC:
        assert "security" not in operation
    else:
        assert operation["security"] == [{SCHEME: []}]
    for status in errors:
        schema = operation["responses"][status]["content"]["application/json"]["schema"]
        model = "DetailResponse" if (method, path, status) in PLAIN_DETAIL else "ErrorResponse"
        assert schema == {"$ref": f"#/components/schemas/{model}"}, (path, status)


def test_a_rate_limited_response_documents_retry_after(contract: dict) -> None:
    response = contract["paths"]["/generate-meal-plan"]["post"]["responses"]["429"]

    assert "Retry-After" in response["headers"]


def test_each_documented_error_is_described_by_its_client_message() -> None:
    documented = error_responses(AuthenticationRequired, HistoryDisabled)

    assert documented[401]["description"] == AuthenticationRequired.client_message
    assert documented[501]["description"] == HistoryDisabled.client_message


def test_two_errors_with_one_status_are_refused() -> None:
    """One status, one description: a clash would silently hide one error."""
    with pytest.raises(ValueError, match="404"):
        error_responses(MealPlanNotFound, MealPlanNotFound)


ERRORS = [
    AuthenticationRequired("internal"),
    InsufficientScope("internal"),
    RateLimited("internal", 30),
    MealPlanNotFound("internal"),
    HistoryDisabled("internal"),
    NutritionProviderError("internal"),
    RetrievalUnavailable("internal"),
]


@pytest.mark.parametrize("exc", ERRORS, ids=lambda exc: type(exc).__name__)
def test_the_handler_body_matches_the_documented_schema(exc: MealPlanningError) -> None:
    """The documented ErrorResponse is what the real handler sends."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise")
    def _raise() -> None:
        raise exc

    response = TestClient(app).get("/raise")
    body = response.json()

    assert response.status_code == exc.status_code
    assert ErrorResponse.model_validate(body).model_dump(exclude_none=True) == body
    assert body.get("code") == exc.error_code
