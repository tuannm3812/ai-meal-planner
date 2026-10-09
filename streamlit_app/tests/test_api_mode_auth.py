"""G4 on the Streamlit client: what API mode actually sends.

API mode talks to a real FastAPI server. After G4 it must authenticate with
X-API-Key, held server-side in the MEAL_PLANNER_API_KEY secret (never in a
browser bundle), and must no longer send the removed X-Gemini-API-Key
pass-through. Demo mode stays in-process and holds no key.
"""

from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 90


class _FakeResponse:
    def __init__(self, body: dict[str, Any]) -> None:
        self._body = body

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._body


@pytest.fixture(name="sent")
def _sent(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, dict[str, str]]]:
    """Replace the HTTP layer with a recorder; no request leaves the process."""
    import requests

    calls: list[tuple[str, dict[str, str]]] = []

    def _request(method: str, url: str, **kwargs: Any) -> _FakeResponse:
        calls.append((url, dict(kwargs.get("headers") or {})))
        if url.endswith("/health"):
            return _FakeResponse({"status": "ok", "services": {}})
        return _FakeResponse(
            {
                "status": "success",
                "plan_status": "infeasible",
                "infeasible_reason": "No meal fits.",
                "meal_plan": None,
            }
        )

    monkeypatch.setattr(requests, "request", _request)
    return calls


def _generate_in_api_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STREAMLIT_DEMO_MODE", "0")
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()
    next(b for b in app.button if b.label == "Generate meal").click().run(timeout=TIMEOUT)
    assert not app.exception, [str(e.value) for e in app.exception]


def _generate_headers(sent: list[tuple[str, dict[str, str]]]) -> dict[str, str]:
    matching = [headers for url, headers in sent if url.endswith("/generate-meal-plan")]
    assert matching, f"no generate call was made; saw {[url for url, _ in sent]}"
    return matching[-1]


def test_api_mode_sends_the_server_side_api_key(
    monkeypatch: pytest.MonkeyPatch, sent: list[tuple[str, dict[str, str]]]
) -> None:
    monkeypatch.setenv("MEAL_PLANNER_API_KEY", "streamlit-key")

    _generate_in_api_mode(monkeypatch)

    assert _generate_headers(sent).get("X-API-Key") == "streamlit-key"


def test_api_mode_no_longer_sends_a_gemini_key(
    monkeypatch: pytest.MonkeyPatch, sent: list[tuple[str, dict[str, str]]]
) -> None:
    """The pass-through was removed in G4; the client must not offer the key."""
    monkeypatch.setenv("GEMINI_API_KEY", "user-gemini-key")

    _generate_in_api_mode(monkeypatch)

    headers = {name.lower() for name in _generate_headers(sent)}
    assert "x-gemini-api-key" not in headers


def test_api_mode_without_a_configured_key_sends_none(
    monkeypatch: pytest.MonkeyPatch, sent: list[tuple[str, dict[str, str]]]
) -> None:
    """Against an API in open local mode, no key is needed or invented."""
    _generate_in_api_mode(monkeypatch)

    assert "X-API-Key" not in _generate_headers(sent)
