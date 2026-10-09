"""G5b: /health must report the deployment facts an operator checks first.

The gate (portfolio log, 2026-10-08) asks /health to report storage backend and
hosted mode. Hosted mode's behaviour - history and feedback refused with 501 -
is G6. Until G6 implements it, enabling the switch must fail at startup rather
than let an operator believe history is disabled when it is not.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import AppSettings
from backend.app.core.container import build_container
from backend.app.main import app


def test_health_reports_storage_backend_and_hosted_mode() -> None:
    with TestClient(app) as client:
        services = client.get("/health").json()["services"]

    assert services["storage_backend"] in {"json", "sqlite"}
    assert services["hosted_mode"] is False
    for provider in ("gemini_configured", "usda_configured"):
        assert isinstance(services[provider], bool)


def test_hosted_mode_defaults_off() -> None:
    assert AppSettings(_env_file=None).hosted_mode is False


def test_hosted_mode_cannot_be_enabled_before_g6_implements_it() -> None:
    settings = AppSettings(_env_file=None, hosted_mode=True, storage_backend="json")

    with pytest.raises(RuntimeError, match="HOSTED_MODE"):
        build_container(settings)
