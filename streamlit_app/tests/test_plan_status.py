"""The Streamlit client's side of G3's plan_status contract.

An infeasible request is a successful response with null meal sections. Before
this, the meal view called `.get()` on `meal_plan` and would have raised inside
its click handler - surfacing as a confusing "Unexpected API error" instead of
the reason. Demo-mode domain errors also rendered `str(exc)`, the internal
detail, rather than the exception's client-safe message (Codex, 2026-10-08).
"""

from pathlib import Path
from typing import Any

import pytest
from demo import local_demo_request
from streamlit.testing.v1 import AppTest

from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.core.exceptions import NoFeasibleMeal, RetrievalUnavailable

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 90
INTERNAL_DETAIL = "INTERNAL-DETAIL groups=['kidney_disease', 'vegan']"
PROFILE = {
    "age": 30,
    "sex": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "activity_multiplier": 1.4,
    "dietary_restrictions": [],
}


@pytest.fixture(name="infeasible")
def _infeasible(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every in-process meal search exhaust the corpus and the templates."""

    def _raise(*_: Any, **__: Any) -> None:
        raise NoFeasibleMeal(INTERNAL_DETAIL)

    monkeypatch.setattr(MealRecommendationAgent, "generate_meal_payload", _raise)


def test_demo_reports_plan_status_for_a_normal_meal() -> None:
    payload = {"craving": "high-protein burger"}
    response = local_demo_request("/generate-meal-plan", payload, PROFILE)

    assert response["plan_status"] in {"matched", "fallback"}
    assert response["infeasible_reason"] is None


@pytest.mark.usefixtures("infeasible")
def test_demo_infeasible_response_is_typed_safe_and_not_saved() -> None:
    response = local_demo_request("/generate-meal-plan", {"craving": "tofu"}, PROFILE)

    assert response["status"] == "success"
    assert response["plan_status"] == "infeasible"
    assert response["infeasible_reason"] == NoFeasibleMeal.client_message
    for section in ("meal_plan", "nutrition", "shopping_list", "reconciliation"):
        assert response[section] is None, section
    assert "INTERNAL-DETAIL" not in str(response)
    assert local_demo_request("/meal-plans/user_123", None, PROFILE)["items"] == []


def test_render_api_error_shows_the_client_message_for_domain_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """In demo mode the backend runs in-process, so its exceptions reach the UI."""
    import api

    shown: list[str] = []

    class _St:
        @staticmethod
        def error(message: str) -> None:
            shown.append(message)

    monkeypatch.setattr(api, "st", _St)

    api.render_api_error(RetrievalUnavailable(INTERNAL_DETAIL))

    assert shown == [RetrievalUnavailable.client_message]


@pytest.mark.usefixtures("infeasible")
def test_the_meal_view_shows_the_reason_instead_of_a_meal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STREAMLIT_DEMO_MODE", "1")
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()

    next(b for b in app.button if b.label == "Generate meal").click().run(timeout=TIMEOUT)

    assert not app.exception, [str(item.value) for item in app.exception]
    assert [e.value for e in app.error] == []
    assert any(NoFeasibleMeal.client_message in str(w.value) for w in app.warning)
    assert "Calories" not in {m.label for m in app.metric}
    assert "Feedback" not in {s.value for s in app.subheader}
