"""scripts/new_api_key.py must emit a key whose record the API actually accepts."""

import json
import subprocess
import sys
from pathlib import Path

from backend.app.core.auth import AuthConfig
from backend.app.core.config import AppSettings

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "new_api_key.py"


def _run(*args: str) -> dict[str, object]:
    out = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=True
    ).stdout
    return json.loads(out)


def test_the_generated_record_authenticates_the_generated_key() -> None:
    result = _run("partner-app", "plans:write", "history:read")
    settings = AppSettings(_env_file=None, api_keys=json.dumps([result["record"]]))

    principal = AuthConfig.from_settings(settings).authenticate(str(result["key"]))

    assert principal is not None
    assert principal.client_id == "partner-app"
    assert principal.scopes == frozenset({"plans:write", "history:read"})


def test_scopes_default_to_all_three() -> None:
    record = _run("app")["record"]

    assert isinstance(record, dict)
    assert record["scopes"] == ["plans:write", "feedback:write", "history:read"]


def test_two_runs_never_produce_the_same_key() -> None:
    assert _run("app")["key"] != _run("app")["key"]


def test_an_unknown_scope_is_refused() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "app", "admin"], capture_output=True, text=True
    )

    assert result.returncode != 0
    assert "admin" in result.stderr
