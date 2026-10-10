"""Tracing for the meal-planning workflow: allowlisted metadata only (G10b).

Spans wrap the request and each stage of ``MealPlanningService``. They carry
only the attributes in ``ALLOWED_ATTRIBUTES``: operational metadata such as
statuses, counts and ids. Never request content: no ``user_id``, craving,
health conditions, dietary preferences, location, biometrics or values derived
from them, ingredient or meal names, or exception messages.

Only ``opentelemetry-api`` is imported at module level. It is a no-op until a
provider is configured, so with ``TRACING_EXPORTER=none`` (the default) nothing
is recorded and the SDK, from the ``tracing`` extra, is never imported.
"""

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.trace import Span, Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from backend.app.core.instance import INSTANCE_ID

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import TracerProvider

    from backend.app.core.config import AppSettings

SERVICE_NAME = "ai-meal-planner-api"
# Google's OTLP ingestion endpoint for traces (Cloud Trace, Telemetry API).
CLOUD_TRACE_ENDPOINT = "https://telemetry.googleapis.com/v1/traces"

ALLOWED_ATTRIBUTES: dict[str, type] = {
    "http.request.method": str,
    "http.route": str,  # the template, e.g. /meal-plans/{user_id}, never the path
    "http.response.status_code": int,
    "request_id": str,
    "client_id": str,  # an application, not a person (G4)
    "plan_status": str,
    "meal.source": str,
    "meal.ingredient_count": int,
    "nutrition.status": str,
    "nutrition.verified_external_count": int,
    "nutrition.trusted_local_count": int,
    "nutrition.estimated_count": int,
    "reconciliation.rescaled": bool,
    "reconciliation.within_tolerance": bool,
    "calorie.model_version": str,
    "error.type": str,
}
"""Every attribute a span may carry, with its type. Anything else is refused."""

_provider: "TracerProvider | None" = None
_TRACE_CONTEXT = TraceContextTextMapPropagator()


def set_provider(provider: "TracerProvider | None") -> None:
    """Use this provider for every span; ``None`` restores the no-op default.

    Args:
        provider: An SDK tracer provider, or None.
    """
    global _provider
    _provider = provider


def configure(settings: "AppSettings") -> None:
    """Install the provider ``TRACING_EXPORTER`` asks for; ``none`` installs nothing.

    Args:
        settings: Application settings.
    """
    set_provider(None if settings.tracing_exporter == "none" else build_provider(settings))


def shutdown() -> None:
    """Flush and drop the configured provider, if any."""
    if _provider is not None:
        _provider.shutdown()
    set_provider(None)


def build_provider(settings: "AppSettings") -> "TracerProvider":
    """Build an SDK tracer provider for the configured exporter.

    Args:
        settings: Application settings; ``tracing_exporter`` is ``console`` or
            ``cloud_trace``.

    Returns:
        The provider, sampling ``trace_sample_ratio`` of new traces.

    Raises:
        RuntimeError: For ``cloud_trace`` when no Google Cloud project can be
            found from Application Default Credentials.
    """
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )
    from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

    attributes: dict[str, str] = {
        "service.name": SERVICE_NAME,
        "service.instance.id": INSTANCE_ID,
    }
    if settings.tracing_exporter == "cloud_trace":
        exporter, project_id = _cloud_trace_exporter()
        attributes["gcp.project_id"] = project_id
        processor = BatchSpanProcessor(exporter)
    else:
        processor = SimpleSpanProcessor(ConsoleSpanExporter())

    provider = TracerProvider(
        resource=Resource.create(attributes),
        sampler=ParentBased(TraceIdRatioBased(settings.trace_sample_ratio)),
    )
    provider.add_span_processor(processor)
    return provider


def _cloud_trace_exporter() -> tuple[object, str]:
    """An OTLP/HTTP exporter authenticated with Application Default Credentials."""
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    credentials, project_id = google.auth.default()
    if not project_id:
        raise RuntimeError(
            "TRACING_EXPORTER=cloud_trace needs a Google Cloud project; none was found "
            "from Application Default Credentials (set GOOGLE_CLOUD_PROJECT)."
        )
    exporter = OTLPSpanExporter(
        endpoint=CLOUD_TRACE_ENDPOINT, session=AuthorizedSession(credentials)
    )
    return exporter, project_id


def inbound_context(headers: Mapping[str, str]) -> Context:
    """Continue a caller's trace from its ``traceparent`` header, and nothing else.

    ``traceparent`` holds fixed-format hex ids and flags, which link this span
    to the caller's trace (on Cloud Run, the platform's request trace). The
    other context headers, ``tracestate`` and ``baggage``, carry free text the
    caller chooses. ``tracestate`` would ride on every exported span's context,
    outside the attribute allowlist (Codex, P2 on PR #18), so neither is read.

    Args:
        headers: The request headers.

    Returns:
        A context holding the remote parent, or an empty one.
    """
    traceparent = headers.get("traceparent")
    return _TRACE_CONTEXT.extract({"traceparent": traceparent} if traceparent else {})


def tracer() -> trace.Tracer:
    """The tracer for this service, from the configured provider or the no-op default."""
    provider = _provider or trace.get_tracer_provider()
    return provider.get_tracer(SERVICE_NAME)


@contextmanager
def stage(name: str, **kwargs: object) -> Iterator[Span]:
    """Run a block inside a span that never records an exception's message.

    OpenTelemetry's default records the exception as an event with its message
    and traceback, which can quote request data. Here a failure sets the span's
    status to ERROR and ``error.type`` to the exception's class name only.

    Args:
        name: The span name, e.g. ``nutrition.verify``.
        **kwargs: Passed to ``start_as_current_span`` (e.g. ``context``, ``kind``).

    Yields:
        The span.
    """
    with tracer().start_as_current_span(
        name, record_exception=False, set_status_on_exception=False, **kwargs
    ) as span:
        try:
            yield span
        except BaseException as exc:
            span.set_status(Status(StatusCode.ERROR))
            span.set_attribute("error.type", type(exc).__name__)
            raise


def annotate(attributes: Mapping[str, object], span: Span | None = None) -> None:
    """Set allowlisted attributes on a span (the current one by default).

    Args:
        attributes: Attribute names and values; each must be in
            ``ALLOWED_ATTRIBUTES`` with the listed type.
        span: The span to annotate; defaults to the current span.

    Raises:
        ValueError: For an attribute that is not on the allowlist.
        TypeError: For a value of the wrong type.
    """
    target = span or trace.get_current_span()
    for key, value in attributes.items():
        expected = ALLOWED_ATTRIBUTES.get(key)
        if expected is None:
            raise ValueError(f"span attribute {key!r} is not on the telemetry allowlist")
        if not isinstance(value, expected):
            raise TypeError(f"span attribute {key!r} must be {expected.__name__}")
        target.set_attribute(key, value)


def route_template(scope: Mapping[str, object]) -> str:
    """The matched route's template, e.g. ``/meal-plans/{user_id}``.

    Logs and spans name a request by this, never by its path, which carries
    ``user_id``.

    Args:
        scope: The ASGI scope, after routing.

    Returns:
        The template, or ``unmatched`` when no route matched.
    """
    return getattr(scope.get("route"), "path", None) or "unmatched"


def describe_failure(exc: BaseException) -> str:
    """Name a failure for a log line: its type, plus an HTTP status if it has one.

    Exception messages are left out because they can quote request data or, for
    the USDA lookup, a URL carrying the API key.

    Args:
        exc: The exception.

    Returns:
        For example ``TimeoutError`` or ``HTTPError 429``.
    """
    code = getattr(exc, "code", None)
    name = type(exc).__name__
    return f"{name} {code}" if isinstance(code, int) else name
