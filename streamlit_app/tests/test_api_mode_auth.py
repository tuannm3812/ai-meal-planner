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
    status_code = 200
    is_redirect = False

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


# --- Codex P1 (2026-10-10): the key must only ever reach the operator's backend ---


def test_an_edited_base_url_never_receives_the_server_key(
    monkeypatch: pytest.MonkeyPatch, sent: list[tuple[str, dict[str, str]]]
) -> None:
    """A visitor can type any Base URL; the key must not follow it there."""
    monkeypatch.setenv("MEAL_PLANNER_API_KEY", "streamlit-key")
    monkeypatch.setenv("STREAMLIT_DEMO_MODE", "0")
    app = AppTest.from_file(APP, default_timeout=TIMEOUT)
    app.run()

    next(t for t in app.text_input if t.label == "Base URL").set_value("https://attacker.example")
    next(b for b in app.button if b.label == "Generate meal").click().run(timeout=TIMEOUT)

    to_attacker = [h for url, h in sent if url.startswith("https://attacker.example")]
    assert to_attacker, "precondition: the edited URL was actually called"
    assert all("X-API-Key" not in headers for headers in to_attacker)


@pytest.mark.parametrize(
    ("target", "trusted", "keyed"),
    [
        ("http://localhost:8000", "http://localhost:8000", True),
        ("http://localhost:8000/", "http://localhost:8000", True),
        ("http://LOCALHOST:8000", "http://localhost:8000", True),
        ("http://api.example", "http://api.example:80", True),
        ("https://attacker.example", "http://localhost:8000", False),
        ("http://localhost:8001", "http://localhost:8000", False),
        ("https://localhost:8000", "http://localhost:8000", False),
        ("http://localhost:8000@attacker.example", "http://localhost:8000", False),
        ("http://user:pw@localhost:8000", "http://localhost:8000", False),
        ("ftp://localhost:8000", "ftp://localhost:8000", False),
        ("not a url", "http://localhost:8000", False),
    ],
    ids=[
        "same",
        "trailing-slash",
        "host-case",
        "default-port",
        "other-host",
        "other-port",
        "other-scheme",
        "userinfo-trick",
        "userinfo-on-trusted-host",
        "non-http",
        "garbage",
    ],
)
def test_the_key_is_bound_to_the_configured_origin(
    monkeypatch: pytest.MonkeyPatch, target: str, trusted: str, keyed: bool
) -> None:
    from api import with_api_key

    monkeypatch.setenv("MEAL_PLANNER_API_KEY", "k")
    monkeypatch.setenv("API_BASE_URL", trusted)

    headers = with_api_key(target, {"Accept": "application/json"}) or {}

    assert ("X-API-Key" in headers) is keyed
    assert headers.get("Accept") == "application/json"


def test_backend_calls_never_follow_a_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    """requests strips only Authorization on a cross-host redirect, so a custom
    X-API-Key header would follow a 30x to another host. Refuse redirects."""
    import requests
    from api import request_json

    seen: dict[str, Any] = {}

    class _Redirect:
        status_code = 307
        is_redirect = True
        text = ""

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return {}

    def _request(method: str, url: str, **kwargs: Any) -> _Redirect:
        seen.update(kwargs)
        return _Redirect()

    monkeypatch.setattr(requests, "request", _request)

    with pytest.raises(requests.HTTPError):
        request_json("GET", "http://localhost:8000", "/health", headers={"X-API-Key": "k"})
    assert seen["allow_redirects"] is False
