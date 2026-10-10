"""G6 on the Streamlit client: hide history and feedback on a hosted API.

Contract (portfolio log, 2026-10-08, point 2): a hosted deployment refuses
history and feedback with 501, and "both clients hide those tabs when /health
reports it". Otherwise history is labelled non-persistent (owner decision E):
it lives in instance-local storage and is lost on redeploy.

These run the real app in API mode against a recording fake backend.
"""

from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 90
MEAL = {
    "status": "success",
    "plan_status": "matched",
    "request_id": "req-hosted-1",
    "meal_plan": {
        "meal_definition": {"structured_meal_name": "Pasta Bowl", "ingredients": []},
        "metadata": {"source": "local_vector_rag_meal_corpus", "confidence": 0.8},
    },
    "nutrition": {"total_calories": 600},
    "shopping_list": {},
}


class _Response:
    status_code = 200
    is_redirect = False

    def __init__(self, body: dict[str, Any]) -> None:
        self._body = body

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._body


def _fake_backend(monkeypatch: pytest.MonkeyPatch, *, hosted: bool) -> list[str]:
    import requests

    called: list[str] = []

    def _request(method: str, url: str, **_: Any) -> _Response:
        called.append(url)
        if url.endswith("/health"):
            return _Response({"status": "ok", "services": {"hosted_mode": hosted}})
        if url.endswith("/generate-meal-plan"):
            return _Response(MEAL)
        return _Response({"items": []})

    monkeypatch.setattr(requests, "request", _request)
    return called


def _app_after_generating(monkeypatch: pytest.MonkeyPatch, *, hosted: bool) -> AppTest:
    _fake_backend(monkeypatch, hosted=hosted)
    monkeypatch.setenv("STREAMLIT_DEMO_MODE", "0")
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()
    next(b for b in app.button if b.label == "Generate meal").click().run(timeout=TIMEOUT)
    assert not app.exception, [str(e.value) for e in app.exception]
    return app


def _buttons(app: AppTest) -> set[str]:
    return {button.label for button in app.button}


def _text(app: AppTest) -> str:
    return " ".join(str(e.value) for e in [*app.info, *app.caption])


def test_hosted_mode_hides_history_and_feedback(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app_after_generating(monkeypatch, hosted=True)

    assert {"Load history", "Load saved meals", "Submit feedback"}.isdisjoint(_buttons(app))
    assert "Feedback" not in {s.value for s in app.subheader}
    assert "disabled on this hosted deployment" in _text(app)


def test_local_mode_keeps_history_and_feedback_and_labels_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The control: not hosted, so history and feedback stay, labelled non-persistent."""
    app = _app_after_generating(monkeypatch, hosted=False)

    assert {"Load history", "Load saved meals", "Submit feedback"} <= _buttons(app)
    assert "not persisted" in _text(app)
