"""Put streamlit_app/ on sys.path so tests import modules the way the app does.

Streamlit inserts the main script's directory at sys.path[0] at runtime, which is
why app.py says `from api import request_json`. Replicating that here means the
tests exercise the real import mechanism rather than a test-only one. Adding
streamlit_app/__init__.py instead would make the app's own sibling imports
resolve differently from how Streamlit resolves them.
"""

import sys
from pathlib import Path

import pytest

STREAMLIT_APP_DIR = Path(__file__).resolve().parents[1]

if str(STREAMLIT_APP_DIR) not in sys.path:
    sys.path.insert(0, str(STREAMLIT_APP_DIR))


@pytest.fixture(autouse=True)
def _isolate_demo_storage(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Point demo-mode storage at a per-test temp directory.

    local_demo_request persists meal plans and feedback under DEMO_DATA_DIR,
    which defaults to the repo's database/ - the same files a developer's real
    demo history lives in. Without this, every test run appended synthetic
    records there. DEMO_DATA_DIR is read at call time, and AppTest reuses the
    already-imported demo module, so this covers the harness too.

    Args:
        monkeypatch: Used to swap the module attribute for the test's duration.
        tmp_path: The per-test temporary directory.
    """
    import demo

    monkeypatch.setattr(demo, "DEMO_DATA_DIR", tmp_path)
