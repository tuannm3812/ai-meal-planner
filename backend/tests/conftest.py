"""Pytest configuration shared by the whole backend test session.

Isolates the suite from the developer's real application data.
"""

import os

import pytest


def pytest_sessionstart(session: pytest.Session) -> None:
    """Force the real FastAPI app onto the JSON backend before collection.

    ``backend.app.main`` resolves its module-level ``settings`` - and so
    which storage backend the FastAPI lifespan builds when ``TestClient(app)``
    starts it - exactly once, the first time the module is imported. Several
    test modules do ``from backend.app.main import app`` at their own module
    level, so that import happens during collection, before any ordinary
    fixture (even an autouse, session-scoped one) gets a chance to run -
    pytest fully collects the session before executing the first test.
    ``pytest_sessionstart`` fires before collection begins, so this is the
    one place that reliably lands early enough.

    With ``sqlite`` now the default backend, without this the real app would
    build a real engine against ``database/ai_meal_planner.db`` - creating
    the file and its schema via ``mkdir`` + ``create_all`` - the moment any
    test enters ``TestClient(app)``, even though every such fixture
    immediately overrides the container with a ``tmp_path``-rooted one
    before making a request. Forcing ``json`` avoids that: JSON's
    repositories only ``mkdir`` a directory that already exists and is
    already tracked, so no new file appears.

    The environment variable is restored immediately afterwards, so it
    cannot affect any other ``AppSettings()`` construction later in the
    session - including the tests in test_config.py that assert
    ``storage_backend`` defaults to ``sqlite``, and the storage-backend
    parity tests, which build their own repositories explicitly for both
    backends via ``build_repositories(settings, data_dir=tmp_path)``.

    Args:
        session: The pytest session about to collect tests.
    """
    original_storage_backend = os.environ.get("STORAGE_BACKEND")
    os.environ["STORAGE_BACKEND"] = "json"
    try:
        import backend.app.main  # noqa: F401  (binds `main.settings` to json)
    finally:
        if original_storage_backend is None:
            os.environ.pop("STORAGE_BACKEND", None)
        else:
            os.environ["STORAGE_BACKEND"] = original_storage_backend
