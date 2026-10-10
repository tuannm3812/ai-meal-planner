"""G10b: the telemetry module exports allowlisted metadata only.

Contract (agent log, 2026-10-10 proposal; owner decisions the same day):
OpenTelemetry spans around the workflow's stages, exported to Cloud Trace over
OTLP when TRACING_EXPORTER=cloud_trace, and a no-op otherwise. A span carries
only attributes on a fixed allowlist, and a failing span records the exception
type, never its message.
"""

import os
import subprocess
import sys
from collections.abc import Iterator
from urllib.error import HTTPError

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

from backend.app.core import telemetry
from backend.app.core.config import AppSettings
from backend.app.core.instance import INSTANCE_ID


@pytest.fixture(name="spans")
def _spans() -> Iterator[InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    telemetry.set_provider(provider)
    yield exporter
    telemetry.set_provider(None)


def _settings(**values: object) -> AppSettings:
    return AppSettings(_env_file=None, **values)


def test_a_stage_records_allowlisted_attributes(spans: InMemorySpanExporter) -> None:
    with telemetry.stage("nutrition.verify") as span:
        telemetry.annotate({"nutrition.status": "mixed", "nutrition.estimated_count": 2}, span)

    (finished,) = spans.get_finished_spans()
    assert finished.name == "nutrition.verify"
    assert dict(finished.attributes) == {
        "nutrition.status": "mixed",
        "nutrition.estimated_count": 2,
    }


def test_annotate_defaults_to_the_current_span(spans: InMemorySpanExporter) -> None:
    with telemetry.stage("meal.retrieve"):
        telemetry.annotate({"plan_status": "fallback"})

    (finished,) = spans.get_finished_spans()
    assert finished.attributes["plan_status"] == "fallback"


@pytest.mark.parametrize("key", ["craving", "user_id", "location", "health_conditions"])
def test_an_attribute_off_the_allowlist_is_refused(key: str, spans: InMemorySpanExporter) -> None:
    with telemetry.stage("meal.retrieve") as span, pytest.raises(ValueError, match=key):
        telemetry.annotate({key: "anything"}, span)


def test_an_attribute_of_the_wrong_type_is_refused(spans: InMemorySpanExporter) -> None:
    with telemetry.stage("meal.retrieve") as span, pytest.raises(TypeError):
        telemetry.annotate({"meal.ingredient_count": "seven"}, span)


def test_a_failing_stage_records_the_exception_type_only(spans: InMemorySpanExporter) -> None:
    """OpenTelemetry's default would export the message and traceback as an event."""
    with pytest.raises(ValueError), telemetry.stage("meal.retrieve"):
        raise ValueError("internal detail naming the user's constraints")

    (finished,) = spans.get_finished_spans()
    assert finished.status.status_code is StatusCode.ERROR
    assert not finished.status.description
    assert dict(finished.attributes) == {"error.type": "ValueError"}
    assert not finished.events
    assert "internal detail" not in finished.to_json()


@pytest.mark.parametrize(
    ("exc", "described"),
    [
        (TimeoutError("timed out after 6s"), "TimeoutError"),
        (OSError("failed https://example.invalid/?api_key=k"), "OSError"),
        (
            HTTPError("https://example.invalid/?api_key=k", 429, "Too Many", None, None),
            "HTTPError 429",
        ),
    ],
    ids=["timeout", "message-dropped", "http-status-kept"],
)
def test_a_failure_is_described_without_its_message(exc: Exception, described: str) -> None:
    assert telemetry.describe_failure(exc) == described


def test_the_default_configuration_exports_nothing() -> None:
    telemetry.configure(_settings())
    try:
        with telemetry.stage("calorie.predict") as span:
            assert not span.is_recording()
    finally:
        telemetry.shutdown()


def test_the_console_exporter_records_spans() -> None:
    telemetry.configure(_settings(tracing_exporter="console", trace_sample_ratio=1.0))
    try:
        with telemetry.stage("calorie.predict") as span:
            assert span.is_recording()
    finally:
        telemetry.shutdown()


def test_cloud_trace_exports_over_otlp_with_google_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Google's documented ingestion: OTLP/HTTP to the Telemetry API, sent through
    an AuthorizedSession built from Application Default Credentials."""
    import google.auth
    import requests
    from google.auth.credentials import AnonymousCredentials
    from google.auth.transport.requests import AuthorizedSession

    monkeypatch.setattr(
        google.auth, "default", lambda *_, **__: (AnonymousCredentials(), "demo-project")
    )
    sent: list[tuple[str, str]] = []

    def _request(self: AuthorizedSession, method: str, url: str, *_: object, **__: object):
        sent.append((method, url))
        response = requests.Response()
        response.status_code = 200
        response._content = b""
        return response

    monkeypatch.setattr(AuthorizedSession, "request", _request)

    provider = telemetry.build_provider(_settings(tracing_exporter="cloud_trace"))
    try:
        with provider.get_tracer("test").start_as_current_span("calorie.predict"):
            pass
        assert provider.force_flush()
        resource = dict(provider.resource.attributes)
    finally:
        provider.shutdown()

    assert sent == [("POST", telemetry.CLOUD_TRACE_ENDPOINT)]
    assert resource["gcp.project_id"] == "demo-project"
    assert resource["service.name"] == "ai-meal-planner-api"
    assert resource["service.instance.id"] == INSTANCE_ID


def test_new_traces_are_sampled_at_the_configured_ratio() -> None:
    provider = telemetry.build_provider(
        _settings(tracing_exporter="console", trace_sample_ratio=0.25)
    )
    try:
        assert "TraceIdRatioBased{0.25}" in provider.sampler.get_description()
    finally:
        provider.shutdown()


def test_cloud_trace_without_a_project_refuses_to_start(monkeypatch: pytest.MonkeyPatch) -> None:
    import google.auth
    from google.auth.credentials import AnonymousCredentials

    monkeypatch.setattr(google.auth, "default", lambda *_, **__: (AnonymousCredentials(), None))

    with pytest.raises(RuntimeError, match="project"):
        telemetry.build_provider(_settings(tracing_exporter="cloud_trace"))


@pytest.mark.parametrize("ratio", [-0.1, 1.5])
def test_the_sample_ratio_must_be_a_probability(ratio: float) -> None:
    with pytest.raises(ValueError):
        _settings(trace_sample_ratio=ratio)


def test_the_app_never_imports_the_sdk_when_tracing_is_off() -> None:
    """ "App unchanged without it": a default request needs only the API package."""
    probe = (
        "import sys\n"
        "from fastapi.testclient import TestClient\n"
        "from backend.app.main import app\n"
        "with TestClient(app) as c:\n"
        "    assert c.post('/generate-meal-plan', json={'craving': 'pasta'}).status_code == 200\n"
        "print(sorted(m for m in sys.modules if m.startswith('opentelemetry.sdk')))\n"
    )
    env = {
        **os.environ,
        "STORAGE_BACKEND": "json",
        "SKIP_DOTENV": "1",
        "API_KEYS": "",
        "HOSTED_MODE": "true",  # stores nothing, so the real database is untouched
        "REQUIRE_VERIFIED_NUTRITION": "0",
        "TRACING_EXPORTER": "none",
    }
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=True,
        timeout=180,
        env=env,
    )

    assert result.stdout.strip().splitlines()[-1] == "[]"
