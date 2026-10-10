"""G5b: /health must report the deployment facts an operator checks first.

The gate (portfolio log, 2026-10-08) asks /health to report storage backend and
hosted mode. G5b refused HOSTED_MODE=true until its behaviour existed; G6
(test_hosted_mode.py) implements it, so enabling it now succeeds.
"""

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


def test_hosted_mode_can_be_enabled_now_that_g6_implements_it() -> None:
    """G5b refused HOSTED_MODE=true until G6; G6 replaces the refusal."""
    settings = AppSettings(_env_file=None, hosted_mode=True, storage_backend="json")

    assert build_container(settings).settings.hosted_mode is True
