"""G10b acceptance: only allowlisted metadata leaves the process.

Contract (agent log, 2026-10-10): traces and logs follow one rule. The
secret-marker test puts a unique marker in every free-text and personal field
of a request: user_id, craving, location, health conditions, dietary
preferences and the API key, plus distinctive biometrics and the USDA key. It
then drives the request down every path that logs or traces: matched,
fallback, infeasible, retrieval unavailable, a failing nutrition provider under
strict verification, a hosted-mode refusal, and an unexpected 500. No marker,
and no named health condition, may appear in any exported span (name,
attribute, event, status or resource) or in any log record at DEBUG (message,
arguments and traceback).
"""

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from backend.app.agents import nutrition_verification_agent
from backend.app.core import telemetry
from backend.app.core.container import Container, get_container, with_repositories
from backend.app.main import app
from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)

MARK = "zq7marker"
USER_ID = f"uid-{MARK}-1"
USDA_KEY = f"{MARK}-usda-key"
BIOMETRIC_TRACES = ["171.3719", "68.2917", "1.4331"]
FORBIDDEN = [MARK, "kidney", *BIOMETRIC_TRACES]
STAGES = [
    "calorie.predict",
    "meal.retrieve",
    "nutrition.verify",
    "plan.reconcile",
    "supermarket.list",
]


def _request(**overrides: object) -> dict[str, object]:
    """A meal request whose every free-text and personal field carries a marker."""
    body: dict[str, object] = {
        "user_id": USER_ID,
        "craving": f"pasta {MARK}crave",
        "location": f"{MARK}town, NSW",
        "health_conditions": [f"{MARK}-condition"],
        "dietary_preferences": [f"{MARK}-preference"],
        "age": 47,
        "sex": "female",
        "height_cm": 171.3719,
        "weight_kg": 68.2917,
        "activity_multiplier": 1.4331,
    }
    body.update(overrides)
    return body


# Real conditions, so the constraint rules engage; the markers ride alongside.
CONSTRAINED = {
    "health_conditions": ["kidney_disease", f"{MARK}-condition"],
    "dietary_preferences": ["vegan", f"{MARK}-preference"],
}
HEADERS = {"X-API-Key": f"{MARK}-api-key"}


class _EmptyRetriever:
    """A working retriever whose corpus admits no meal for the request."""

    min_score = 0.16
    active_backend = "stub"

    def retrieve(self, **_: object) -> list[object]:
        return []


@dataclass
class Harness:
    client: TestClient
    container: Container
    spans: InMemorySpanExporter
    monkeypatch: pytest.MonkeyPatch

    def use(self, container: Container) -> None:
        app.dependency_overrides[get_container] = lambda: container


@pytest.fixture(name="harness")
def _harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Harness]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    with TestClient(app, raise_server_exceptions=False) as client:
        # After startup: the app's lifespan configures telemetry from settings,
        # which with tracing off (the default) installs no provider.
        telemetry.set_provider(provider)
        container = with_repositories(
            client.app.state.container,
            UserProfileRepository(tmp_path),
            MealPlanRepository(tmp_path),
            MealFeedbackRepository(tmp_path),
        )
        harness = Harness(client, container, exporter, monkeypatch)
        harness.use(container)
        yield harness
    app.dependency_overrides.clear()
    telemetry.set_provider(None)


def _generate(h: Harness, **overrides: object) -> int:
    return h.client.post(
        "/generate-meal-plan", json=_request(**overrides), headers=HEADERS
    ).status_code


def _matched(h: Harness) -> tuple[int, str]:
    return _generate(h), '"plan_status": "matched"'


def _fallback(h: Harness) -> tuple[int, str]:
    h.monkeypatch.setattr(h.container.meal_planning_service.meal_agent, "meal_retriever", None)
    return _generate(h), '"plan_status": "fallback"'


def _infeasible(h: Harness) -> tuple[int, str]:
    agent = h.container.meal_planning_service.meal_agent
    h.monkeypatch.setattr(agent, "meal_retriever", _EmptyRetriever())
    return _generate(h, **CONSTRAINED), "infeasible"


def _retrieval_unavailable(h: Harness) -> tuple[int, str]:
    h.monkeypatch.setattr(h.container.meal_planning_service.meal_agent, "meal_retriever", None)
    return _generate(h, **CONSTRAINED), "RetrievalUnavailable"


def _provider_failure(h: Harness) -> tuple[int, str]:
    """USDA fails with an error that quotes its URL, as some HTTP libraries do."""
    nutrition = h.container.meal_planning_service.nutrition_agent
    h.monkeypatch.setattr(nutrition, "api_key", USDA_KEY)
    h.monkeypatch.setattr(nutrition, "require_verified", True)

    def _urlopen(url: object, *_: object, **__: object) -> object:
        target = getattr(url, "full_url", url)
        raise OSError(f"could not fetch {target}")

    h.monkeypatch.setattr(nutrition_verification_agent, "urlopen", _urlopen)
    return _generate(h), "USDA lookup failed"


def _hosted_refusal(h: Harness) -> tuple[int, str]:
    settings = h.container.settings.model_copy(update={"hosted_mode": True})
    h.use(replace(h.container, settings=settings))
    return h.client.get(f"/meal-plans/{USER_ID}", headers=HEADERS).status_code, "HistoryDisabled"


def _unexpected_500(h: Harness) -> tuple[int, str]:
    def _broken() -> Container:
        raise RuntimeError("an unexpected internal failure")

    app.dependency_overrides[get_container] = _broken
    return h.client.get(f"/meal-plans/{USER_ID}", headers=HEADERS).status_code, "Unhandled error"


SCENARIOS: dict[str, tuple[Callable[[Harness], tuple[int, str]], int]] = {
    "matched": (_matched, 200),
    "fallback": (_fallback, 200),
    "infeasible": (_infeasible, 200),
    "retrieval-unavailable": (_retrieval_unavailable, 503),
    "provider-failure": (_provider_failure, 502),
    "hosted-refusal": (_hosted_refusal, 501),
    "unexpected-500": (_unexpected_500, 500),
}


def _exported(spans: tuple[ReadableSpan, ...]) -> str:
    return "\n".join(span.to_json() for span in spans)


def _logged(records: list[logging.LogRecord]) -> str:
    """Every app log record, formatted with its traceback.

    The ``httpx`` records are the TestClient's own: the caller logging the
    request it sent. In production that role is the platform's request log,
    which records URLs whatever the app does (owner decision B: user_id must be
    an opaque id).
    """
    formatter = logging.Formatter("%(name)s %(levelname)s %(message)s")
    return "\n".join(formatter.format(r) for r in records if r.name != "httpx")


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_no_request_data_reaches_a_span_or_a_log(
    scenario: str, harness: Harness, caplog: pytest.LogCaptureFixture
) -> None:
    run, expected_status = SCENARIOS[scenario]
    with caplog.at_level(logging.DEBUG):
        status, signal = run(harness)

    spans = harness.spans.get_finished_spans()
    exported, logged = _exported(spans), _logged(caplog.records)
    assert status == expected_status
    assert spans, "precondition: the request was traced"
    # Not vacuous: the path's own operational signal is still there.
    assert signal in exported + logged, f"{signal!r} missing from spans and logs"
    for forbidden in FORBIDDEN:
        assert forbidden not in exported, f"{forbidden!r} exported in a span"
        assert forbidden not in logged, f"{forbidden!r} logged:\n{logged}"


def test_a_meal_plan_is_one_trace_with_a_span_per_stage(harness: Harness) -> None:
    response = harness.client.post("/generate-meal-plan", json=_request(), headers=HEADERS)
    assert response.status_code == 200

    spans = {span.name: span for span in harness.spans.get_finished_spans()}
    request_span = spans.pop("POST /generate-meal-plan")
    assert sorted(spans) == sorted(STAGES)
    for stage in spans.values():
        assert stage.parent is not None and stage.parent.span_id == request_span.context.span_id
        assert stage.context.trace_id == request_span.context.trace_id

    assert dict(request_span.attributes) == {
        "http.request.method": "POST",
        "http.route": "/generate-meal-plan",
        "http.response.status_code": 200,
        "request_id": response.json()["request_id"],
        "client_id": "local",
        "plan_status": "matched",
    }
    assert spans["nutrition.verify"].attributes["nutrition.status"] in {"verified", "mixed"}
    assert spans["meal.retrieve"].attributes["meal.ingredient_count"] > 0


def test_every_exported_attribute_is_on_the_allowlist(harness: Harness) -> None:
    for scenario in ("matched", "infeasible"):
        SCENARIOS[scenario][0](harness)

    keys = {key for span in harness.spans.get_finished_spans() for key in span.attributes}
    assert keys, "precondition: spans carry attributes"
    assert keys <= set(telemetry.ALLOWED_ATTRIBUTES), keys - set(telemetry.ALLOWED_ATTRIBUTES)


def test_a_history_route_is_named_by_its_template(harness: Harness) -> None:
    _hosted_refusal(harness)

    (request_span,) = harness.spans.get_finished_spans()
    assert request_span.name == "GET /meal-plans/{user_id}"
    assert request_span.attributes["http.route"] == "/meal-plans/{user_id}"
    assert request_span.attributes["http.response.status_code"] == 501
