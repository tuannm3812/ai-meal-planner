# Phase 4b — Streamlit Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the 685-line `streamlit_app/app.py` into focused modules, changing no behaviour.

**Architecture:** Harness first, then bottom-up. Streamlit ships `AppTest`, which runs the app headlessly and exposes its rendered widgets — so Task 1 writes that harness against the **current** file, and every later task must keep it passing unchanged. Then the stateless helpers move (`api.py`, `demo.py`), then the sidebar becomes a function returning a config object, then the three tabs become view modules, and `app.py` is left as the shell.

**Tech Stack:** Streamlit 1.63 (`streamlit.testing.v1.AppTest`), pytest, requests.

**Spec:** `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md` §9 (Streamlit half)
**Branches from:** `refactor/phase-4a-react` (PR #5, not yet merged). Its PR targets that branch.

## Scope: what §9 still asks for, and one thing it gets wrong

§9's Streamlit half says: "delete `local_demo_request` and `is_meal_like_input` (D4, DEC-2). Demo mode calls a shared agent factory, the same one the DI container uses… `app.py` splits into `app.py`, `api.py`, `demo.py` and `views/`."

Status, measured 2026-09-14:

| §9 item | Status |
| --- | --- |
| Demo mode must not reimplement the backend | **Already done in Phase 1.** `local_demo_request` routes through `MealPlanningService`; it went from ~250 lines of duplicated meal/macro/pricing logic to a 137-line request router |
| Delete `local_demo_request` | **Do not delete it.** It is no longer duplication — it is the demo-mode request router that makes the zero-setup demo work with no API server, which DEC-2 explicitly preserved. It moves to `demo.py` |
| Delete `is_meal_like_input` | **Do not delete it.** §9 groups it with the duplication cleanup, but it is a client-side guard (`app.py:480`) rejecting polite-only input ("thanks", "hello", "ok", "test") before a request is made. Deleting it would let those reach the API. It moves with the meal-plan view |
| Split into `app.py`, `api.py`, `demo.py`, `views/` | **This phase** |
| No file over ~200 lines | **This phase** |

## Verified Starting State

| Check | Result |
| --- | --- |
| `streamlit_app/app.py` | **685 lines**, the only file in the directory |
| `streamlit_app/` is a package? | **No `__init__.py`.** It is run as a script: `streamlit run streamlit_app/app.py` |
| `AppTest` on the current app | **Works.** Runs with no exception and exposes 3 tabs, 4 buttons (`Generate meal`, `Predict expenditure`, `Load history`, `Load saved meals`), 5 text inputs, and 6 subheaders (`Request`, `Response`, `Calorie Expenditure`, `Meal History`, `Saved Meals`, `Run Mode`) |
| `pytest` `testpaths` | `["backend/tests"]` — a test under `streamlit_app/` would not be collected |
| Backend suite | 222 tests; frontend 36. Neither is affected by this phase |

### Current layout of `app.py`

| Lines | Content | Destination |
| --- | --- | --- |
| 1-16 | stdlib/third-party imports, `REPO_ROOT` `sys.path` insert, `st.set_page_config` | `app.py` |
| 19-41 | `get_secret` | `config.py` |
| 79-89 | `request_json` | `api.py` |
| 92-107 | `render_api_error` | `api.py` |
| 110-111 | `parse_extra_items` | `api.py` |
| 114-128 | `is_meal_like_input` | `views/meal_plan.py` |
| 131-151 | `StreamlitUserProfileRepository` | `demo.py` |
| 154-290 | `local_demo_request` | `demo.py` |
| 293 | `st.title` | `app.py` |
| 298-466 | the whole `with st.sidebar:` block — Run Mode and Profile | `views/sidebar.py` |
| 451-464 | `call_demo_or_api` | `app.py` (see Critical Facts) |
| 467 | `st.tabs([...])` | `app.py` |
| 469-596 | meal tab body | `views/meal_plan.py` |
| 597-649 | calorie tab body | `views/calories.py` |
| 650-685 | history tab body | `views/history.py` |

## Global Constraints

- **No behaviour may change.** The `AppTest` harness from Task 1 must pass **unchanged** after every task. Do not edit it after Task 1 except where a task explicitly says to.
- **The deployed demo must keep working with no API server.** §9's "done when" requires it. Verify in demo mode, not just API-client mode.
- **No file in `streamlit_app` may exceed ~200 lines** at the end. Report the largest.
- **`uv run pytest` must pass** — run it **without** `-q` (`addopts` supplies it; a second becomes `-qq` and hides the summary). The backend's 222 tests must stay green; this phase must not touch them.
- **No new dependencies.** `streamlit`, `requests` and pytest are all that is needed.
- **Do not touch** `backend/`, `frontend/`, `notebooks/`, `.github/`, or `.gitignore`.
- **Never `git add -A`.** `git status --short`, review every path, stage explicitly. Master standard §10.1. `.coverage` and `database/ai_meal_planner.db` are gitignored local artifacts — leave them.
- Commit format `<type>(<scope>): <imperative summary>`; the `(scope)` is mandatory. Every body ends with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- Ruff clean: `uv run ruff check .` and `uv run ruff format --check .`.
- Match the existing style: type hints on every function, Google-style docstrings on anything new, `st.*` calls copied verbatim.
- Work on branch `refactor/phase-4b-streamlit`. Do not push or open PRs.

## Critical Facts

### Flat sibling imports work — no package, no `sys.path` juggling

Streamlit inserts the main script's directory at `sys.path[0]`, in two places:
`streamlit/web/bootstrap.py:73` and `streamlit/runtime/scriptrunner/exec_code.py:63`.
So from `app.py`, `from api import request_json` and `from views.meal_plan import render`
both resolve with **no `__init__.py` in `streamlit_app/`** and no path manipulation.
`views/` **does** need its own `__init__.py` to be a package.

Consequence: do **not** add `streamlit_app/__init__.py` and do **not** write
`from streamlit_app.api import ...` — that would depend on `REPO_ROOT` already being on
`sys.path`, forcing local imports below the bootstrap block and tripping ruff's `E402`.

Verified 2026-09-14: the repo root is already on `sys.path` (hatchling editable install),
which is why `backend.app.*` resolves in the existing tests — but `streamlit_app` has no
`__init__.py`, so the dotted `streamlit_app.api` form fails regardless. A `conftest.py`
under `streamlit_app/tests/` that prepends `streamlit_app/` was probed against a throwaway
test and works; `import app` under it succeeds, meaning importing the script outside a
Streamlit runtime does not raise.

**Hazard that insert creates:** `api`, `config` and `demo` are generic module names, and
prepending `streamlit_app/` to `sys.path` makes them shadow any same-named module for the
rest of the pytest session, including for the 222 backend tests. The backend imports
everything fully qualified (`backend.app.core.config`), so it is safe today — but add the
guard test in Task 2 Step 2 so a future collision fails loudly instead of silently binding
the wrong module.

### `REPO_ROOT` stays in `app.py`, and backend imports stay deferred

`app.py:12-14` inserts `REPO_ROOT` so `backend.*` is importable. `demo.py` needs
`backend.app.services.meal_planning_service` — but it must **keep importing it inside its
functions**, as the current code does, not at module top. At `demo.py` import time the
bootstrap in `app.py` has already run, so a deferred import resolves; a top-level one in
`demo.py` would also work today but couples module-import order to the bootstrap. Keep the
existing deferred pattern and the `RuntimeError` wrapper around its `ImportError`.

### `call_demo_or_api` closes over four module globals — this is the central design problem

```python
def call_demo_or_api(method, path, payload=None, headers=None):
    if use_demo_mode:                       # global, set by the sidebar
        return local_demo_request(path=path, payload=payload,
                                  profile=streamlit_profile,   # global
                                  api_key=gemini_api_key)      # global
    return request_json(method, api_base_url, path, payload, headers)  # global
```

All four (`use_demo_mode`, `streamlit_profile`, `gemini_api_key`, `api_base_url`) are
assigned inside the sidebar block, which runs before the tabs use them. **A view module
cannot read them.** So:

- `views/sidebar.py` renders the sidebar and **returns** a config object carrying them.
- `app.py` receives that config and builds the request callable from it.
- Each view takes that callable as a parameter — it never reaches for a global.

Define the config as a frozen dataclass in `config.py` so every module can type against
it. **Do not pass the four values around individually** and do not have views import from
`app.py` — that would be circular.

### Session state: `latest_meal_result` belongs entirely to the meal tab

`app.py` initialises it at line 295, outside any tab:

```python
if "latest_meal_result" not in st.session_state:
    st.session_state.latest_meal_result = None
```

But the only write (line 501) and the only read (line 551) are both inside the meal tab
body. So **move the guard to the top of `views/meal_plan.py`'s `render()`**, not into
`app.py`. Streamlit reruns the script top to bottom on every interaction, and `render()`
runs before its own reads, so the guard is still in place first.

Dropping this guard is the most likely single mistake in Task 4: the read at the old line
551 becomes an `AttributeError`. The Task 1 harness already catches it — its `app` fixture
runs the app with no meal generated, so `test_the_app_runs_without_raising` fails
immediately. **No extra test is needed; do not add one.** Just do not skip the move.

### `is_meal_like_input` is a guard, not duplication

`app.py:114-128` returns `False` for `{"thank you","thanks","hello","hi","hey","ok","okay","test"}`
and for anything under 3 characters. The meal tab calls it at line 480 before requesting.
It moves to `views/meal_plan.py` and keeps its behaviour. Give it a unit test — nothing
currently covers it.

---

## File Structure

**Created:**

| File | Responsibility |
| --- | --- |
| `streamlit_app/config.py` | `get_secret`, the `AppConfig` frozen dataclass, and demo-mode/base-URL resolution |
| `streamlit_app/api.py` | `request_json`, `render_api_error`, `parse_extra_items` |
| `streamlit_app/demo.py` | `StreamlitUserProfileRepository`, `local_demo_request` |
| `streamlit_app/views/__init__.py` | Package marker |
| `streamlit_app/views/sidebar.py` | Renders Run Mode + Profile, returns an `AppConfig` |
| `streamlit_app/views/meal_plan.py` | The meal tab, plus `is_meal_like_input` |
| `streamlit_app/views/calories.py` | The calorie tab |
| `streamlit_app/views/history.py` | The history tab |
| `streamlit_app/tests/test_app_harness.py` | The `AppTest` regression harness |
| `streamlit_app/tests/test_demo.py` | `local_demo_request` and the profile repository |
| `streamlit_app/tests/test_api_helpers.py` | `request_json`, `parse_extra_items`, `is_meal_like_input` |

**Modified:** `streamlit_app/app.py` — shrinks to the shell; `pyproject.toml` — `testpaths`.

---

## Task 1: Build the AppTest harness, before touching anything

**Files:**
- Create: `streamlit_app/tests/test_app_harness.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: a harness every later task must keep green **unchanged**.

- [ ] **Step 1: Extend `testpaths` so the tests are collected**

In `pyproject.toml` under `[tool.pytest.ini_options]`, change:
```toml
testpaths = ["backend/tests", "streamlit_app/tests"]
```

- [ ] **Step 2: Write the harness**

Create `streamlit_app/tests/test_app_harness.py`:

```python
"""Regression harness for the Streamlit app.

These assertions are written against the 685-line app.py BEFORE it is split, so
they describe observable behaviour rather than structure. Phase 4b must keep
every one of them passing unchanged - that is the evidence the decomposition
changed nothing a user sees.
"""

from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

APP = "streamlit_app/app.py"
TIMEOUT = 90


@pytest.fixture(name="app")
def _app(monkeypatch: pytest.MonkeyPatch) -> AppTest:
    """Run the app in demo mode, so no API server is required.

    Args:
        monkeypatch: Used to force demo mode via the environment.

    Returns:
        A run AppTest instance.
    """
    monkeypatch.setenv("STREAMLIT_DEMO_MODE", "1")
    harness = AppTest.from_file(APP, default_timeout=TIMEOUT)
    harness.run()
    return harness


def _by_label(elements: Any, label: str) -> Any:
    """Find a rendered widget by its visible label.

    No widget in app.py sets a key=, so AppTest's key lookup is unavailable and
    index lookup would silently shift if a widget is ever reordered. Labels are
    what a user actually sees, so they are what these tests address.

    Args:
        elements: An AppTest element sequence, e.g. app.button.
        label: The exact visible label.

    Returns:
        The matching element.

    Raises:
        AssertionError: If no element carries that label.
    """
    for element in elements:
        if element.label == label:
            return element
    raise AssertionError(f"no element labelled {label!r}; saw {[e.label for e in elements]}")


def test_the_app_runs_without_raising(app: AppTest) -> None:
    """A script exception here means the app is broken for every user."""
    assert not app.exception, [str(item.value) for item in app.exception]


def test_the_three_tabs_exist(app: AppTest) -> None:
    assert len(app.tabs) == 3


def test_the_expected_subheaders_render(app: AppTest) -> None:
    """Pins the section headings a user navigates by."""
    rendered = {item.value for item in app.subheader}
    for expected in {
        "Request",
        "Response",
        "Calorie Expenditure",
        "Meal History",
        "Saved Meals",
        "Run Mode",
    }:
        assert expected in rendered, f"missing subheader: {expected}"


def test_the_four_action_buttons_exist(app: AppTest) -> None:
    """One per workflow: meal plan, calories, history, saved meals."""
    labels = {item.label for item in app.button}
    for expected in {
        "Generate meal",
        "Predict expenditure",
        "Load history",
        "Load saved meals",
    }:
        assert expected in labels, f"missing button: {expected}"


def test_the_expected_text_inputs_exist(app: AppTest) -> None:
    labels = {item.label for item in app.text_input}
    for expected in {"Craving or meal goal", "Location", "User ID"}:
        assert expected in labels, f"missing text input: {expected}"


def test_generating_a_meal_in_demo_mode_produces_a_response(app: AppTest) -> None:
    """The end-to-end demo workflow, with no API server running.

    This is spec section 9's "done when" clause: the deployed Streamlit demo must
    still work with no backend. If the decomposition breaks the wiring between
    the sidebar's config and the views, this is the test that catches it.
    """
    _by_label(app.text_input, "Craving or meal goal").set_value("high-protein burger")
    _by_label(app.button, "Generate meal").click().run(timeout=TIMEOUT)
    assert not app.exception, [str(item.value) for item in app.exception]
    assert any("Response" == item.value for item in app.subheader)
```

Two facts this harness depends on, both verified against the current `app.py`:

- **No widget in `app.py` sets a `key=`** (`grep -n "key=" streamlit_app/app.py` returns
  only keyword arguments to backend calls). So `AppTest`'s `key` lookup is unavailable and
  `_by_label` is the addressing mechanism. **Do not add keys to widgets to make testing
  easier** — that is a behaviour change to the app in service of the test.
- **The demo toggle reads the environment**: `app.py:302` is
  `value=get_secret("STREAMLIT_DEMO_MODE", "0") == "1"`, so the fixture's `monkeypatch.setenv`
  genuinely starts the app in demo mode. Keep that wiring intact through the refactor — if
  the sidebar stops reading `STREAMLIT_DEMO_MODE`, this whole harness silently starts
  testing API-client mode against a server that is not running.

The craving input already defaults to `value="high-protein burger"` (`app.py:473`), so the
`set_value` call is belt-and-braces; it makes the test independent of that default.

- [ ] **Step 3: Run the harness against the unmodified app**

```bash
uv run pytest streamlit_app/tests/test_app_harness.py -v
```
Expected: **all pass**. They are written against the current code, so a failure means an
assertion is wrong about the app as it exists — **fix the assertion to match reality and
report what differed.** Do not change `app.py` in this task.

- [ ] **Step 4: Confirm the backend suite is unaffected**

```bash
uv run pytest
```
Expected: 222 backend tests plus your new ones, all passing. Report the total.

- [ ] **Step 5: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add pyproject.toml streamlit_app/tests
git commit -F - <<'MSG'
test(streamlit): add an AppTest harness before decomposing app.py

The Streamlit app had no tests at all, so there was nothing to prove a 685-line
split changed no behaviour. Streamlit ships AppTest, which runs the script
headlessly and exposes its rendered widgets, so the harness is written first,
against the unmodified file.

It pins what a user navigates by - three tabs, six subheaders, four action
buttons, the text inputs - and runs the end-to-end demo workflow with no API
server, which is spec section 9's "done when" clause. Every later task in this
phase must keep these passing unchanged.

testpaths gains streamlit_app/tests so they are collected.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 2: Extract the stateless helpers into `config.py`, `api.py` and `demo.py`

These three carry no module-level state, so they move without touching the sidebar/globals
problem.

**Files:**
- Create: `streamlit_app/config.py`, `streamlit_app/api.py`, `streamlit_app/demo.py`,
  `streamlit_app/tests/test_api_helpers.py`, `streamlit_app/tests/test_demo.py`
- Modify: `streamlit_app/app.py`

**Interfaces:**
- Produces:
  - `config.get_secret(name: str, default: str = "") -> str`
  - `api.request_json(method: str, base_url: str, path: str, payload: dict | None = None, headers: dict | None = None) -> dict`
  - `api.render_api_error(exc: Exception) -> None`
  - `api.parse_extra_items(raw_value: str) -> list[str]`
  - `demo.StreamlitUserProfileRepository(age, sex, height_cm, weight_kg, activity_multiplier, dietary_restrictions)` with `fetch_user_profile(user_id) -> dict`
  - `demo.local_demo_request(path: str, payload: dict | None, profile: dict, api_key: str = "") -> dict`
  Tasks 3-5 import these.

- [ ] **Step 1: Move the code**

Move each symbol **verbatim** from `app.py` into its new home, adding the imports each
needs. Locate them by name, not line number.

- `config.py`: `get_secret` (it reads `os.getenv` then Streamlit secrets — keep both paths).
- `api.py`: `request_json`, `render_api_error`, `parse_extra_items`.
- `demo.py`: `StreamlitUserProfileRepository`, `local_demo_request`. **Keep the
  `from backend.app... import` statements inside the functions**, wrapped in the existing
  `try/except ImportError` that raises `RuntimeError` — see Critical Facts.

Then in `app.py` replace the definitions with:
```python
from api import parse_extra_items, render_api_error, request_json
from config import get_secret
from demo import StreamlitUserProfileRepository, local_demo_request
```
These go **above** the `REPO_ROOT` bootstrap if ruff's import ordering allows; if `E402`
or `I001` fires, put them with the other imports and report what ruff required.

- [ ] **Step 2: Write unit tests for the helpers**

Create `streamlit_app/tests/test_api_helpers.py`:

```python
"""Unit tests for the Streamlit app's stateless helpers."""

import pytest

from streamlit_app.api import parse_extra_items


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a, b", ["a", "b"]),
        (" a ,, b ", ["a", "b"]),
        ("", []),
        ("   ", []),
    ],
)
def test_parse_extra_items_splits_trims_and_drops_blanks(raw: str, expected: list[str]) -> None:
    assert parse_extra_items(raw) == expected


def test_the_helper_modules_resolve_inside_streamlit_app() -> None:
    """Guard against the generic module names binding to something else.

    conftest.py prepends streamlit_app/ to sys.path, so `api`, `config` and
    `demo` shadow any same-named module for the whole pytest session. If a
    dependency ever ships one of these names, this fails loudly instead of the
    tests silently exercising the wrong module.
    """
    import api
    import config
    import demo

    for module in (api, config, demo):
        assert module.__file__ is not None
        assert Path(module.__file__).parent.name == "streamlit_app", module.__file__
```

**That import is wrong** — `streamlit_app` is deliberately not a package, so the
dotted form raises `ModuleNotFoundError` even though the repo root is on `sys.path`. Use
the flat import, enabled by a `conftest.py`. Both halves are verified working (see
Critical Facts):

```python
"""Unit tests for the Streamlit app's stateless helpers."""

from pathlib import Path

import pytest

from api import parse_extra_items
```

Create `streamlit_app/tests/conftest.py`:

```python
"""Put streamlit_app/ on sys.path so tests import modules the way the app does.

Streamlit inserts the main script's directory at sys.path[0] at runtime, which is
why app.py says `from api import request_json`. Replicating that here means the
tests exercise the real import mechanism rather than a test-only one. Adding
streamlit_app/__init__.py instead would make the app's own sibling imports
resolve differently from how Streamlit resolves them.
"""

import sys
from pathlib import Path

STREAMLIT_APP_DIR = Path(__file__).resolve().parents[1]

if str(STREAMLIT_APP_DIR) not in sys.path:
    sys.path.insert(0, str(STREAMLIT_APP_DIR))
```

**Do not add `streamlit_app/__init__.py`.**

Create `streamlit_app/tests/test_demo.py` covering `local_demo_request`:
- `/health` returns a dict with `status == "ok"` and a `services` key.
- `/generate-meal-plan` with a craving returns the sections the API returns —
  `status`, `request_id`, `meal_plan`, `nutrition`, `shopping_list`, `calorie_budget`,
  `reconciliation`. **Read the function first and assert what it actually returns.**
- `StreamlitUserProfileRepository.fetch_user_profile` returns the six keys the backend
  expects: `age`, `gender`, `height`, `weight`, `workout_level`, `dietary_restrictions`,
  and maps `sex="male"` to `gender="m"`.

- [ ] **Step 3: Verify**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
wc -l streamlit_app/app.py streamlit_app/*.py
```
Expected: everything passes, **including the Task 1 harness unchanged**. `app.py` should
drop by roughly 190 lines. Report the real numbers.

- [ ] **Step 4: Commit**

```bash
git status --short
git add streamlit_app/config.py streamlit_app/api.py streamlit_app/demo.py streamlit_app/tests streamlit_app/app.py
git commit -F - <<'MSG'
refactor(streamlit): extract config, api and demo helpers

The three groups of stateless helpers move out of app.py first, because none of
them touches the module-level globals the sidebar defines: get_secret to
config.py, the request/error/parse helpers to api.py, and the demo-mode request
router plus its profile repository to demo.py.

demo.py keeps its backend imports inside its functions, wrapped in the existing
ImportError-to-RuntimeError guard - moving them to module top would couple import
order to app.py's sys.path bootstrap.

local_demo_request is NOT deleted, despite spec section 9 listing it with the
duplication cleanup. Phase 1 already removed the duplication: it no longer
reimplements meal selection, macros or pricing, it routes through
MealPlanningService. What remains is the router that makes the zero-setup demo
work with no API server, which DEC-2 explicitly preserved.

Adds the first unit tests for these helpers. The AppTest harness passes
unchanged.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 3: Turn the sidebar into a function that returns a config

**This is the task that solves the globals problem. Read the Critical Facts entry on
`call_demo_or_api` before starting.**

**Files:**
- Create: `streamlit_app/views/__init__.py`, `streamlit_app/views/sidebar.py`
- Modify: `streamlit_app/config.py`, `streamlit_app/app.py`

**Interfaces:**
- Produces:
  - In `config.py`: a frozen dataclass `AppConfig` with fields
    `use_demo_mode: bool`, `api_base_url: str`, `gemini_api_key: str`, `user_id: str`,
    `profile: dict[str, Any]`, `health_conditions: list[str]`, `dietary_preferences: list[str]`.
    **Read the sidebar block and include every value the tabs consume — those seven are
    the expected set, but verify and widen if the tabs use more.**
  - In `views/sidebar.py`: `render_sidebar() -> AppConfig`.
  Tasks 4-5 consume `AppConfig`.

- [ ] **Step 1: Inventory exactly what the tabs read**

```bash
sed -n '298,466p' streamlit_app/app.py   # the sidebar block, as it stands now
grep -n "use_demo_mode\|streamlit_profile\|gemini_api_key\|api_base_url\|user_id\|selected_health_conditions\|dietary_preferences" streamlit_app/app.py
```
Every name the tab bodies read but the sidebar assigns must become an `AppConfig` field.
**List them in your report** — a missed one becomes a `NameError` at runtime that the
harness may or may not reach.

- [ ] **Step 2: Add the dataclass**

In `config.py`:

```python
@dataclass(frozen=True)
class AppConfig:
    """Everything the sidebar resolves that the tabs need.

    The tabs previously read these as module globals, which no view module can
    do. The sidebar returns this instead and app.py threads it through.
    """

    use_demo_mode: bool
    api_base_url: str
    gemini_api_key: str
    user_id: str
    profile: dict[str, Any]
    health_conditions: list[str]
    dietary_preferences: list[str]
```

- [ ] **Step 3: Move the sidebar**

Move the whole `with st.sidebar:` block into `views/sidebar.py` as `render_sidebar()`,
**keeping every `st.*` call, label, default and help string verbatim**, and return an
`AppConfig` built from the locals it computes. Create `views/__init__.py` with a one-line
docstring.

- [ ] **Step 4: Build the request callable in `app.py`**

Replace `call_demo_or_api`'s closure over globals with a factory that closes over the
config explicitly:

```python
def make_request(config: AppConfig) -> Callable[..., dict[str, Any]]:
    """Build the request function the views use, bound to the current config.

    Args:
        config: The sidebar's resolved configuration.

    Returns:
        A callable with the same signature the tabs already use.
    """

    def call_demo_or_api(
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if config.use_demo_mode:
            return local_demo_request(
                path=path,
                payload=payload,
                profile=config.profile,
                api_key=config.gemini_api_key,
            )
        return request_json(method, config.api_base_url, path, payload, headers)

    return call_demo_or_api
```

The tab bodies stay in `app.py` for now and keep calling `call_demo_or_api(...)` — bind it
as `call_demo_or_api = make_request(config)` so the existing call sites are untouched.
Task 4 moves them.

- [ ] **Step 5: Verify**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
wc -l streamlit_app/app.py streamlit_app/views/*.py
```
Expected: all pass, **harness unchanged**. This is the riskiest task in the phase — a
missed config field surfaces as a `NameError`. If the harness passes but you are unsure,
also launch the app and confirm both modes:

```bash
STREAMLIT_DEMO_MODE=1 uv run streamlit run streamlit_app/app.py --server.headless true --server.port 8598 >/tmp/st4b.log 2>&1 &
sleep 12; curl -s -o /dev/null -w "health %{http_code}\n" http://127.0.0.1:8598/_stcore/health
pkill -f "streamlit run streamlit_app/app.py"; sleep 1; lsof -i :8598 || echo "port free"
grep -iE "traceback|nameerror" /tmp/st4b.log || echo "(no traceback)"
```

- [ ] **Step 6: Commit**

```bash
git status --short
git add streamlit_app/config.py streamlit_app/views streamlit_app/app.py
git commit -F - <<'MSG'
refactor(streamlit): make the sidebar a function returning an AppConfig

The tabs read use_demo_mode, streamlit_profile, gemini_api_key and api_base_url
as module globals that the sidebar block assigned. No view module can do that, so
this is the change the rest of the split depends on.

views/sidebar.py renders the same Run Mode and Profile controls verbatim and
returns a frozen AppConfig carrying everything the tabs consume. app.py builds
the request callable from that config through a make_request factory, so
call_demo_or_api closes over an explicit argument instead of four globals, and
every existing call site is unchanged.

The AppTest harness passes unchanged, and the app was launched in demo mode to
confirm no NameError from a missed config field.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 4: Move the three tabs into `views/`

**Files:**
- Create: `streamlit_app/views/meal_plan.py`, `streamlit_app/views/calories.py`, `streamlit_app/views/history.py`
- Modify: `streamlit_app/app.py`

**Interfaces:**
- Consumes: `AppConfig`, `render_sidebar`, `api.*`, `demo.*` from Tasks 2-3.
- Produces: `render(config: AppConfig, call_api: Callable[..., dict[str, Any]]) -> None`
  in each of the three modules — **the same signature in all three**, so `app.py` calls
  them uniformly.

- [ ] **Step 1: Move each tab body verbatim**

Take each `with <x>_tab:` body and move it into its module's `render(config, call_api)`,
dedenting one level. **`is_meal_like_input` moves into `views/meal_plan.py`** — it is a
guard the meal tab calls, not duplication (see Critical Facts). Keep every `st.*` call,
label, `help=` string and `st.subheader` text byte-identical: the harness asserts on the
subheaders and buttons.

Replace reads of the old globals with `config.<field>`, and `call_demo_or_api(...)` with
`call_api(...)`.

**Move the `latest_meal_result` session-state guard from `app.py:295` to the top of
`views/meal_plan.py`'s `render()`** — see Critical Facts. It must not stay in `app.py`, and
it must not be dropped.

- [ ] **Step 2: Rewire `app.py`**

The tab labels are `["Meal Plan", "Calories", "History"]`, verified at `app.py:465` — keep
them exactly.

```python
from views import calories, history, meal_plan
from views.sidebar import render_sidebar

config = render_sidebar()
call_api = make_request(config)

meal_tab, calorie_tab, history_tab = st.tabs(["Meal Plan", "Calories", "History"])

with meal_tab:
    meal_plan.render(config, call_api)
with calorie_tab:
    calories.render(config, call_api)
with history_tab:
    history.render(config, call_api)
```

- [ ] **Step 3: Add a unit test for the guard**

Append to `streamlit_app/tests/test_api_helpers.py`, using whatever import mechanism you
established in Task 2:

```python
@pytest.mark.parametrize(
    "polite", ["thank you", "thanks", "hello", "hi", "hey", "ok", "okay", "test"]
)
def test_is_meal_like_input_rejects_polite_only_input(polite: str) -> None:
    """These must not reach the API. Spec section 9 wrongly called this duplication."""
    from views.meal_plan import is_meal_like_input

    assert is_meal_like_input(polite) is False


@pytest.mark.parametrize("value", ["ab", " a ", ""])
def test_is_meal_like_input_rejects_anything_under_three_characters(value: str) -> None:
    from views.meal_plan import is_meal_like_input

    assert is_meal_like_input(value) is False


@pytest.mark.parametrize("value", ["burger", "high-protein burger", "pasta"])
def test_is_meal_like_input_accepts_a_real_craving(value: str) -> None:
    from views.meal_plan import is_meal_like_input

    assert is_meal_like_input(value) is True
```

- [ ] **Step 4: Verify**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
wc -l streamlit_app/app.py streamlit_app/views/*.py
```
Expected: all pass, **harness unchanged** — including its end-to-end demo-mode meal
generation, which now exercises the full sidebar → config → view → demo path.

- [ ] **Step 5: Commit**

```bash
git status --short
git add streamlit_app/views streamlit_app/app.py streamlit_app/tests
git commit -F - <<'MSG'
refactor(streamlit): move the three tabs into views/

Each tab body becomes render(config, call_api) in its own module, with the same
signature in all three so app.py calls them uniformly. Every st.* call, label,
help string and subheader is byte-identical - the harness asserts on the
subheaders and buttons, and its end-to-end demo-mode generation now exercises the
full sidebar-to-config-to-view path.

is_meal_like_input moves with the meal tab and gains its first tests. Spec
section 9 listed it for deletion alongside the duplicated backend logic, but it
is not that: it is a client-side guard rejecting polite-only input ("thanks",
"hello", "ok") before a request is made. Deleting it would let those reach the
API.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 5: Reduce `app.py` to a shell, check the target, and log the phase

**Files:**
- Modify: `streamlit_app/app.py`, `docs/superpowers/plans/2026-09-14-phase-4b-streamlit-decomposition.md`, `docs/5_agent_log.md`

- [ ] **Step 1: Trim what is left**

`app.py` should contain only: the imports, the `REPO_ROOT` bootstrap, `st.set_page_config`,
`st.title`, the `make_request` factory, the `render_sidebar()` call, the `st.tabs(...)`
call and the three `render(...)` calls. Remove anything ruff reports as unused.

- [ ] **Step 2: Check the size target**

```bash
wc -l streamlit_app/app.py streamlit_app/*.py streamlit_app/views/*.py streamlit_app/tests/*.py | sort -rn
```
§9's "done when" is no file in `streamlit_app` over ~200 lines. **Report the largest.** If
one is still over, say which and by how much — do not split further just to hit a number
without saying so.

- [ ] **Step 3: Prove the demo still works with no API server**

This is §9's other "done when". With **no backend running**:

```bash
lsof -i :8000 && echo "STOP - something is on 8000, kill it first" || echo "port 8000 free, good"
STREAMLIT_DEMO_MODE=1 uv run streamlit run streamlit_app/app.py --server.headless true --server.port 8598 >/tmp/st4b.log 2>&1 &
sleep 12
curl -s -o /dev/null -w "health %{http_code}\n" http://127.0.0.1:8598/_stcore/health
pkill -f "streamlit run streamlit_app/app.py"; sleep 1; lsof -i :8598 || echo "port free"
grep -iE "traceback|error" /tmp/st4b.log | head -5 || echo "(no errors)"
```
The harness's end-to-end test already covers the logic; this confirms the real server
boots. Report both.

- [ ] **Step 4: Confirm nothing outside `streamlit_app` moved**

```bash
git diff refactor/phase-4a-react HEAD --stat -- backend frontend notebooks .github .gitignore
```
Expected: empty. `pyproject.toml` legitimately changed in Task 1 (`testpaths`).

- [ ] **Step 5: Tick the exit gate and append the log entry**

Tick the checklist below for every item you verified. Then append a dated entry to
`docs/5_agent_log.md` — **that file is append-only; never edit an existing entry** —
recording: `app.py` 685 → its final size and what now lives where; that the harness was
written first and passed unchanged throughout; the `AppConfig` change that replaced four
module globals; that `local_demo_request` and `is_meal_like_input` were **kept**, with the
reason §9 was wrong about each; the final test count; and that spec §9 is now complete,
closing the refactor.

- [ ] **Step 6: Commit**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
git status --short
git add streamlit_app/app.py docs/superpowers/plans/2026-09-14-phase-4b-streamlit-decomposition.md docs/5_agent_log.md
git commit -F - <<'MSG'
refactor(streamlit): reduce app.py to a shell and close spec section 9

app.py now holds only the bootstrap, page config, title, the request factory and
the sidebar and tab wiring. It was 685 lines.

Verified against spec section 9's two "done when" clauses: no file in
streamlit_app exceeds roughly 200 lines, and the demo still works with no API
server - confirmed both by the harness's end-to-end demo-mode generation and by
booting the real server with port 8000 empty.

This completes Phase 4 and with it the whole refactor specified in
docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Phase 4b Exit Gate

§9's Streamlit half is done when `app.py` is a shell, no file in `streamlit_app` exceeds
~200 lines, and the demo still works with no API server.

- [ ] `uv run pytest` passes; report the real count (222 backend at the phase start, plus the new Streamlit tests)
- [ ] **The Task 1 harness is byte-identical to when it was written** — `git diff <task-1-commit> HEAD -- streamlit_app/tests/test_app_harness.py` is empty
- [ ] `uv run ruff check .` and `uv run ruff format --check .` clean
- [ ] No file in `streamlit_app` exceeds ~200 lines — report the largest
- [ ] `app.py` contains no view logic and no `with st.sidebar:` block
- [ ] The demo runs with **no API server**: harness end-to-end test passes and the real server boots clean with port 8000 empty
- [ ] `local_demo_request` still exists and still routes through `MealPlanningService`
- [ ] The `latest_meal_result` session-state guard lives in `views/meal_plan.py`, and the meal tab renders clean before any meal is generated
- [ ] `is_meal_like_input` still exists, still rejects the eight polite-only inputs, and has tests
- [ ] `streamlit_app/__init__.py` was **not** created — flat sibling imports still resolve
- [ ] No new dependency: `git diff <base> HEAD -- pyproject.toml` shows only the `testpaths` change
- [ ] Backend and frontend untouched: `git diff <base> HEAD --stat -- backend frontend` empty
- [ ] `git status --short` clean
- [ ] Phase 4b entry appended to `docs/5_agent_log.md`; this checklist ticked

That closes spec §9 and the refactor.
