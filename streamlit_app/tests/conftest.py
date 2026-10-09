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
import streamlit.runtime.secrets as st_secrets

STREAMLIT_APP_DIR = Path(__file__).resolve().parents[1]

if str(STREAMLIT_APP_DIR) not in sys.path:
    sys.path.insert(0, str(STREAMLIT_APP_DIR))

# Real secret env vars get_secret() would otherwise happily forward to a live
# Gemini/USDA/FatSecret call.
_SECRET_ENV_VARS = (
    "USDA_API_KEY",
    "FATSECRET_CLIENT_ID",
    "FATSECRET_CLIENT_SECRET",
    "ENABLE_GEMINI_ADAPTATION",
    "GEMINI_API_KEY",
    "MEAL_PLANNER_API_KEY",
    # Not a secret, but a developer's strict-mode setting would make every test
    # that relies on the default offline demo fail with NutritionProviderError.
    "REQUIRE_VERIFIED_NUTRITION",
)


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


@pytest.fixture(autouse=True)
def _isolate_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stop a developer's real API keys from reaching a Streamlit test.

    A developer running these tests may have real keys in their shell
    environment, or in a `.streamlit/secrets.toml` they use for local
    `streamlit run` sessions. Either would make local_demo_request's agents
    call the real Gemini/USDA/FatSecret APIs (see test_demo.py's module
    docstring for why they are normally no-network).

    Clearing the env vars only covers get_secret()'s first lookup. It also
    tries `st.secrets` and a `.streamlit/secrets.toml` read relative to the
    process cwd - config.py::get_secret, verified experimentally (a real
    file there is read even with the env var unset). `monkeypatch.chdir`
    would block the file read too, but it would also break every relative
    path demo.py depends on (the model artifact, the meal corpus), so
    instead this patches the two lookups narrowly: `Secrets.get` always
    misses, and `Path.exists` only fakes a miss for a path that ends in
    `.streamlit/secrets.toml`, leaving every other relative-path check
    (`models/...`, `data/meal_corpus/...`) untouched. Does not change
    get_secret's own code or its behaviour outside tests.

    Args:
        monkeypatch: Used to clear env vars and patch lookups for the test's
            duration only.
    """
    for name in _SECRET_ENV_VARS:
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setattr(st_secrets.Secrets, "get", lambda self, key, default=None: default)

    real_exists = Path.exists

    def _fake_exists(self: Path, *args: object, **kwargs: object) -> bool:
        if self.as_posix().endswith(".streamlit/secrets.toml"):
            return False
        return real_exists(self, *args, **kwargs)

    monkeypatch.setattr(Path, "exists", _fake_exists)
