"""G6: every response names the process that served it, without revealing anything.

Cloud Run routes one URL across instances and, unlike the nginx rehearsal,
says nothing about which instance answered. The two-instance acceptance check
needs that, so each process generates one random id at import and returns it
as X-Instance-Id on every response - errors included. It is a UUID: no host
name, IP or other environment detail.
"""

import os
import re
import subprocess
import sys

from fastapi.testclient import TestClient

from backend.app.core.container import get_container
from backend.app.main import app

UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def test_every_response_carries_the_same_instance_id() -> None:
    with TestClient(app) as client:
        ids = {
            client.get("/health").headers.get("X-Instance-Id"),
            client.get("/").headers.get("X-Instance-Id"),
            client.post("/generate-meal-plan", json={"craving": "x"}).headers.get(
                "X-Instance-Id"
            ),  # a 422 validation error still carries it
        }

    assert len(ids) == 1
    (instance_id,) = ids
    assert instance_id is not None and UUID.match(instance_id), instance_id


def _unexpected_failure() -> None:
    raise RuntimeError("an unexpected internal failure")


def test_an_unexpected_500_carries_the_same_instance_id() -> None:
    """Codex P3 (2026-10-10): the catch-all 500 had no X-Instance-Id.

    Starlette builds that response in ServerErrorMiddleware, which sits outside
    every middleware the app adds, so a header stamped by middleware never
    reaches it.
    """
    with TestClient(app, raise_server_exceptions=False) as client:
        healthy = client.get("/health").headers.get("X-Instance-Id")
        app.dependency_overrides[get_container] = _unexpected_failure
        try:
            failed = client.get("/health")
        finally:
            app.dependency_overrides.pop(get_container, None)

    assert failed.status_code == 500
    assert failed.json()["detail"] == "An unexpected error occurred."
    assert healthy is not None
    assert failed.headers.get("X-Instance-Id") == healthy


def test_separate_processes_have_different_instance_ids() -> None:
    """Two processes stand in for two Cloud Run instances."""
    probe = (
        "from fastapi.testclient import TestClient\n"
        "from backend.app.main import app\n"
        "with TestClient(app) as c: print(c.get('/health').headers['X-Instance-Id'])\n"
    )
    # Isolated: JSON storage (the developer's pre-G4 SQLite file would be refused),
    # no dotenv, no keys, so each process starts in open local mode.
    env = {
        **os.environ,
        "STORAGE_BACKEND": "json",
        "SKIP_DOTENV": "1",
        "API_KEYS": "",
        "HOSTED_MODE": "false",
        "REQUIRE_VERIFIED_NUTRITION": "0",
    }
    ids = {
        subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
            env=env,
        ).stdout.strip()
        for _ in range(2)
    }

    assert len(ids) == 2, ids
