"""The API contract is a reviewed file, docs/openapi.json (direction item G).

Production-readiness direction, 2026-10-07, item G: the OpenAPI document sits
beside the brief and the architecture as a reviewable file, and CI fails when
the code drifts from it. A contract change then shows up in review as a diff to
that file, never silently. To accept a deliberate change, regenerate it:

    uv run python scripts/export_openapi.py
"""

import json
from pathlib import Path

from backend.app.main import app

CONTRACT = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
REGENERATE = "regenerate it with: uv run python scripts/export_openapi.py"


def test_the_committed_contract_matches_the_code() -> None:
    assert CONTRACT.exists(), f"docs/openapi.json is missing; {REGENERATE}"
    committed = json.loads(CONTRACT.read_text())

    assert committed == app.openapi(), f"the API contract changed; review it, then {REGENERATE}"


def test_the_contract_documents_every_route() -> None:
    """Not vacuous: the committed file is the real, complete contract."""
    paths = json.loads(CONTRACT.read_text())["paths"]

    assert set(paths) == {
        "/",
        "/health",
        "/generate-meal-plan",
        "/meal-plans/{user_id}",
        "/calorie-expenditure/predict",
        "/meal-feedback",
        "/meal-feedback/{user_id}",
        "/saved-meals/{user_id}",
    }
