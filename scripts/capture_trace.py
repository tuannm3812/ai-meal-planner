"""Capture one meal-plan trace as JSON, for docs/assets/sample_trace.json (G10b).

Runs the API in-process with an in-memory span exporter, sends one default
meal-plan request, and writes each span's name, parent, duration and
attributes. Nothing is sent anywhere, and hosted mode keeps it from writing
history.

    uv run python scripts/capture_trace.py
"""

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "docs" / "assets" / "sample_trace.json"
REQUEST = {"craving": "pasta"}


def main() -> None:
    """Send one request through a traced app and write its spans."""
    # Hosted mode stores nothing; the JSON backend only reads profiles, so neither
    # an existing database file nor its schema matters here.
    os.environ.update(
        {
            "SKIP_DOTENV": "1",
            "API_KEYS": "",
            "HOSTED_MODE": "true",
            "STORAGE_BACKEND": "json",
            "TRACING_EXPORTER": "none",
        }
    )
    sys.path.insert(0, str(REPO))
    from fastapi.testclient import TestClient
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    from backend.app.core import telemetry
    from backend.app.main import app

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    with TestClient(app) as client:
        telemetry.set_provider(provider)
        client.post("/generate-meal-plan", json=REQUEST).raise_for_status()
    telemetry.set_provider(None)

    spans = sorted(exporter.get_finished_spans(), key=lambda span: span.start_time)
    names = {span.context.span_id: span.name for span in spans}
    trace = {
        "captured_with": "scripts/capture_trace.py",
        "request": REQUEST,
        "spans": [
            {
                "name": span.name,
                "parent": names.get(span.parent.span_id) if span.parent else None,
                "duration_ms": round((span.end_time - span.start_time) / 1e6, 1),
                "attributes": dict(span.attributes),
            }
            for span in spans
        ],
    }
    OUTPUT.write_text(json.dumps(trace, indent=2) + "\n")
    print(f"wrote {len(spans)} spans to {OUTPUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
