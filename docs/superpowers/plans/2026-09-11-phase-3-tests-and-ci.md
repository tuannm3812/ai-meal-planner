# Phase 3 — Tests and CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cover the three modules the suite still barely touches, add frontend tests, and make CI enforce a coverage floor set from a measured number.

**Architecture:** Pure test and CI work — **no production behaviour changes**. Unit tests mock the network at `urlopen`, an autouse guard fails any test that tries to reach the internet, and the floor in CI is whatever coverage actually reaches at the end of the phase.

**Tech Stack:** pytest, pytest-cov, `unittest.mock`, vitest, React Testing Library, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md` §8
**Branches from:** `refactor/phase-2-storage` (PR #3, not yet merged). Its PR targets that branch.

## Scope: most of spec §8 is already done

Measured on 2026-09-11 before planning. Do not re-do these:

| Spec §8 item | Status |
| --- | --- |
| Endpoint tests, all 8 routes, happy + error | **Done** — `backend/tests/test_api_endpoints.py`, 9 tests (Phase 1) |
| Repository contract tests over both backends | **Done** — `backend/tests/test_repository_contract.py`, 19 functions × 2 backends (Phase 2) |
| Retrieval regression tests retained | **Done** — 3 tests, passing unchanged since before Phase 0 |
| Nutrition agent unit coverage | **Missing** — Task 2 |
| Supermarket agent unit coverage | **Missing** — Task 3 |
| `rag/rules.py` unit coverage | **Partial** — 90% via *indirect* coverage from retrieval tests, no direct tests. Task 4 |
| Frontend vitest + React Testing Library | **Missing** — Task 5 |
| Coverage reported in CI with a floor | **Missing** — Tasks 1 and 6 |
| "No network access in CI" | **Unenforced** — nothing stops a test reaching the internet. Task 1 |

## Verified Starting State

| Check | Result |
| --- | --- |
| `uv run pytest` | **130 passed, 0 skipped** |
| Overall coverage | **82%** (1337 statements, 246 missed) |
| `nutrition_verification_agent.py` | **51%** — 96 of 195 statements uncovered, the largest single gap |
| `meal_recommendation_agent.py` | 72% |
| `supermarket_agent.py` | **79%** — uncovered: 53, 91-98, 115-116, 126-133 |
| `rag/rules.py` | **90%** — uncovered: 192-193, 195, 200, 214, 220, 226 |
| `rag/embedding_index.py` | 32% — the optional sentence-transformers/FAISS path; those packages are an unlocked extra, so this is **out of scope** |

## Global Constraints

- **Run `uv run pytest`, NEVER `uv run pytest -q`** — `pyproject.toml` sets `addopts = "-q"` and a second `-q` becomes `-qq`, hiding the summary. **Counts here are collected cases; parametrization expands them. If pytest reports a different number, trust pytest and report the real figure.**
- **No production code may change in this phase.** If a test fails, that is a finding about the code — **report it, do not fix the code to make a test pass**, and do not weaken the test. The one exception is Task 6, which edits `.github/workflows/ci.yml`.
- **Never `git add -A`.** `git status --short`, review every path, stage explicitly. Master standard §10.1.
- Commit format `<type>(<scope>): <imperative summary>`; the `(scope)` is mandatory. Every body ends with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- **Dependency changes are permitted only in Tasks 1 and 5**, and only in dev groups. After any `uv add --dev`, run `uv lock` and re-export: `uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt`. Because the addition is dev-only the export should be **unchanged** — confirm that, since CI fails on drift. `scikit-learn` must stay at exactly `1.6.1`.
- **Do not modify** `.gitignore`, `notebooks/**`, or `docs/` (except Task 6's log entry).
- **Tests must never touch `database/`.** `backend/tests/conftest.py` already forces `STORAGE_BACKEND=json` for the session; verify `database/*.json` md5s are unchanged after every run.
- Google-style docstrings on helpers; every test gets a docstring saying what bug it would catch.
- Ruff clean: `uv run ruff check .` and `uv run ruff format --check .`.
- Work on branch `refactor/phase-3-tests-and-ci`. Do not push or open PRs.

## Critical Facts

### The network is reached through `urlopen`, not `requests`

`backend/app/agents/nutrition_verification_agent.py:7` does
`from urllib.request import Request, urlopen`, and calls it at lines 216, 255 and 301.
Tests must patch **`backend.app.agents.nutrition_verification_agent.urlopen`** — patching
`urllib.request.urlopen` will not intercept the already-bound name.

`urlopen` is used as a context manager (`with urlopen(...) as response:`) and the code
calls `response.read().decode("utf-8")`. A mock must therefore support
`__enter__`/`__exit__` and return bytes from `read()`.

### The provider chain has a specific order and a cooldown

`_query_macros_per_100g` tries, in order: a trusted local override → the per-process
cache → USDA (only if `api_key` set and not in cooldown) → FatSecret (only if both
credentials set and not in cooldown) → a local estimate. `_FAILURE_THRESHOLD` is **3**
and `_COOLDOWN_SECONDS` is **120**. A provider's failure counter resets to 0 on success.
**An agent constructed with no keys never touches the network at all** — which is why the
existing suite passes without mocking anything.

### `rules.py` is already at 90%, indirectly

The retrieval tests exercise it. What is uncovered is the branch logic for
vegan/vegetarian/sodium-sensitive/kidney-disease groups. Task 4 targets those branches
specifically; do not write a suite that re-covers what already passes.

---

## File Structure

**Created:**

| File | Responsibility |
| --- | --- |
| `backend/tests/test_nutrition_agent.py` | Provider chain, cooldown, cache, local overrides — all with `urlopen` mocked |
| `backend/tests/test_supermarket_agent.py` | Store lookup, pricing, confidence, unmatched items |
| `backend/tests/test_rag_rules.py` | Direct tests for the uncovered constraint-group branches |
| `frontend/vitest.config.js` | vitest + jsdom configuration |
| `frontend/src/test/setup.js` | React Testing Library setup |
| `frontend/src/api/client.test.js` *(or the nearest real path)* | API-layer tests |
| `frontend/src/App.test.jsx` | One rendering test per tab |

**Modified:** `backend/tests/conftest.py` (network guard), `pyproject.toml` + `uv.lock` (pytest-cov), `frontend/package.json` + lockfile (vitest), `.github/workflows/ci.yml` (coverage gate), `docs/5_agent_log.md` (Task 6).

---

## Task 1: Coverage tooling and a network guard

**Files:**
- Modify: `pyproject.toml`, `uv.lock`, `backend/tests/conftest.py`
- Test: `backend/tests/test_network_guard.py` (create)

**Interfaces:**
- Produces: an autouse fixture in `backend/tests/conftest.py` that fails any test performing a real `urlopen` call, and a `no_network` marker escape hatch. Tasks 2-4 rely on the guard being active. `pytest --cov` becomes available for Task 6.

- [ ] **Step 1: Record the baseline**

```bash
uv run --with pytest-cov pytest --cov=backend/app --cov-report=term | tail -5
```
Expected: `TOTAL ... 82%` and `130 passed`. Write the exact number down.

- [ ] **Step 2: Add pytest-cov to the dev group**

```bash
uv add --dev pytest-cov
uv lock
uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt
git diff --stat -- backend/requirements.txt
```
Expected: **no change** to `backend/requirements.txt` — the addition is dev-only, and that export excludes dev. If it changed, something went into the runtime set; stop and report.

Then confirm the pin held:
```bash
grep -A1 '^name = "scikit-learn"' uv.lock | grep version
```
Expected: `version = "1.6.1"`.

- [ ] **Step 3: Write the failing test**

Create `backend/tests/test_network_guard.py`:

```python
"""The guard that keeps the suite off the network."""

import pytest


def test_a_real_network_call_fails_the_test() -> None:
    """Any test reaching the internet must fail loudly, not silently succeed.

    The spec requires no network access in CI. Without this, a misconfigured
    API key would turn unit tests into flaky integration tests.
    """
    from urllib.request import urlopen

    with pytest.raises(RuntimeError, match="network access"):
        urlopen("https://example.invalid/should-never-be-called", timeout=1)
```

- [ ] **Step 4: Run to verify it fails**

Run: `uv run pytest backend/tests/test_network_guard.py`
Expected: FAIL — the call raises `URLError`, not `RuntimeError`, because no guard exists yet.

- [ ] **Step 5: Add the guard**

`backend/tests/conftest.py` **already exists** — it has a `pytest_sessionstart` hook that
forces the JSON storage backend, and it already imports `os` and `pytest`. **Append the
fixture and merge the imports**; do not duplicate an `import pytest` line, and do not
disturb the existing hook. Append:

```python
import socket

import pytest


@pytest.fixture(autouse=True)
def _block_network(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Fail any test that opens a real network connection.

    The spec requires no network access in CI. Agents reach the internet through
    ``urllib.request.urlopen``, so tests that need to exercise a provider must
    patch it themselves; anything that slips through hits this guard instead of
    silently becoming an integration test.

    Mark a test ``@pytest.mark.allow_network`` to opt out.

    Args:
        monkeypatch: Pytest's patching fixture.
        request: Used to read the opt-out marker.
    """
    if request.node.get_closest_marker("allow_network"):
        return

    def _blocked(*args: object, **kwargs: object) -> None:
        raise RuntimeError(
            "network access is blocked in tests; patch the caller instead"
        )

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
```

Register the marker in `pyproject.toml` under `[tool.pytest.ini_options]`:

```toml
markers = ["allow_network: test may open real network connections"]
```

- [ ] **Step 6: Run the whole suite**

The guard patches `socket.socket.connect`. `TestClient` uses an in-process ASGI transport
and opens no sockets, and SQLite is a local file, so neither should trip it — but if
something does, that is exactly the kind of hidden network dependency this guard exists to
surface. Report it rather than working around it.

```bash
uv run pytest
```
Expected: **131 passed** (130 + 1). **If any pre-existing test now fails, it was reaching the network** — that is a genuine finding. Report which test and what it called; do **not** add `allow_network` to make it pass without saying so.

- [ ] **Step 7: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add pyproject.toml uv.lock backend/tests/conftest.py backend/tests/test_network_guard.py
git commit -F - <<'MSG'
test(ci): add coverage tooling and block network access in tests

Spec section 8 requires no network access in CI, and nothing enforced it. An
agent configured with a USDA or FatSecret key would have turned unit tests into
flaky integration tests silently.

An autouse fixture now patches socket.connect to raise, so anything reaching the
internet fails loudly with a message pointing at the fix - patch the caller. A
pytest.mark.allow_network marker is the documented escape hatch.

Adds pytest-cov to the dev group for the coverage gate later in this phase.
Verified the dev-only addition leaves backend/requirements.txt unchanged, so the
drift job stays green, and scikit-learn is still pinned at 1.6.1.

Baseline coverage recorded at 82%.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 2: Nutrition agent coverage

The largest gap: 51%, 96 uncovered statements. **Read the Critical Facts above first** — especially that `urlopen` must be patched on the agent's own module.

**Files:**
- Create: `backend/tests/test_nutrition_agent.py`

**Interfaces:**
- Consumes: the network guard from Task 1.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Write a mock helper and the provider-chain tests**

Create `backend/tests/test_nutrition_agent.py`:

```python
"""Nutrition agent: provider chain, cooldown, caching and fallbacks.

Every test patches ``backend.app.agents.nutrition_verification_agent.urlopen``.
Patching ``urllib.request.urlopen`` would not work - the module binds the name at
import time.
"""

import json
from contextlib import contextmanager
from typing import Any

import pytest

from backend.app.agents import nutrition_verification_agent as module
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.schemas.requests import Ingredient

USDA_PAYLOAD = {
    "foods": [
        {
            "foodNutrients": [
                {"nutrientName": "Energy", "value": 165.0},
                {"nutrientName": "Protein", "value": 31.0},
                {"nutrientName": "Carbohydrate, by difference", "value": 0.0},
                {"nutrientName": "Total lipid (fat)", "value": 3.6},
            ]
        }
    ]
}


def _fake_urlopen(payload: dict[str, Any]):
    """Build a urlopen replacement returning one JSON payload.

    Args:
        payload: The object the fake endpoint should return.

    Returns:
        A callable usable as a context manager, like the real urlopen.
    """

    @contextmanager
    def _opener(*args: object, **kwargs: object):
        class _Response:
            def read(self) -> bytes:
                return json.dumps(payload).encode("utf-8")

        yield _Response()

    return _opener


def _boom(*args: object, **kwargs: object):
    """A urlopen replacement that always fails."""
    raise OSError("provider unavailable")


def test_no_keys_means_no_network_and_a_local_estimate() -> None:
    """With no credentials the agent must not attempt any provider."""
    agent = NutritionVerificationAgent()
    result = agent.calculate_meal_macros([Ingredient(item_name="chicken breast",
                                                     base_quantity_grams=100)])
    assert result.total_calories > 0
    assert result.ingredients_macros[0].data_source != "usda_fooddata_central"


def test_usda_is_used_when_a_key_is_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """A configured key must actually route through USDA."""
    monkeypatch.setattr(module, "urlopen", _fake_urlopen(USDA_PAYLOAD))
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    macros = agent._query_macros_per_100g("kale")
    assert macros["source"] == "usda_fooddata_central"
    assert macros["calories"] == 165.0
    assert macros["protein"] == 31.0


def test_a_successful_lookup_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    """The second lookup of the same ingredient must not call the provider again."""
    calls: list[str] = []

    def _counting(*args: object, **kwargs: object):
        calls.append("hit")
        return _fake_urlopen(USDA_PAYLOAD)(*args, **kwargs)

    monkeypatch.setattr(module, "urlopen", _counting)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    agent._query_macros_per_100g("kale")
    agent._query_macros_per_100g("kale")
    assert len(calls) == 1


def test_a_trusted_override_short_circuits_the_providers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Local overrides must win before any network call is considered."""
    monkeypatch.setattr(module, "urlopen", _boom)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    override = agent._trusted_local_override("olive oil")
    if override is None:
        pytest.skip("olive oil is not in the trusted override table")
    assert agent._query_macros_per_100g("olive oil") == override


def test_provider_failure_falls_back_to_a_local_estimate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing provider must degrade, not raise."""
    monkeypatch.setattr(module, "urlopen", _boom)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    macros = agent._query_macros_per_100g("some unusual ingredient")
    assert macros["calories"] > 0
    assert macros["source"] != "usda_fooddata_central"


def test_three_failures_open_the_cooldown(monkeypatch: pytest.MonkeyPatch) -> None:
    """After _FAILURE_THRESHOLD failures the provider is paused."""
    monkeypatch.setattr(module, "urlopen", _boom)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    assert agent._usda_cooldown_until == 0.0
    for index in range(NutritionVerificationAgent._FAILURE_THRESHOLD):
        agent._query_macros_per_100g(f"ingredient {index}")
    assert agent._usda_consecutive_failures >= NutritionVerificationAgent._FAILURE_THRESHOLD
    assert agent._usda_cooldown_until > 0.0


def test_a_cooled_down_provider_is_not_called(monkeypatch: pytest.MonkeyPatch) -> None:
    """While in cooldown the agent must skip the provider entirely."""
    calls: list[str] = []

    def _counting(*args: object, **kwargs: object):
        calls.append("hit")
        raise OSError("provider unavailable")

    monkeypatch.setattr(module, "urlopen", _counting)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    agent._usda_cooldown_until = module.time.time() + 120
    agent._query_macros_per_100g("anything at all")
    assert calls == []


def test_success_resets_the_failure_counter(monkeypatch: pytest.MonkeyPatch) -> None:
    """A working call must clear the path back to cooldown."""
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    monkeypatch.setattr(module, "urlopen", _boom)
    agent._query_macros_per_100g("first")
    assert agent._usda_consecutive_failures == 1
    monkeypatch.setattr(module, "urlopen", _fake_urlopen(USDA_PAYLOAD))
    agent._query_macros_per_100g("second")
    assert agent._usda_consecutive_failures == 0


def test_macros_scale_with_portion_size() -> None:
    """200 g must yield roughly twice the macros of 100 g."""
    agent = NutritionVerificationAgent()
    small = agent.calculate_meal_macros(
        [Ingredient(item_name="brown rice", base_quantity_grams=100)]
    )
    large = agent.calculate_meal_macros(
        [Ingredient(item_name="brown rice", base_quantity_grams=200)]
    )
    assert large.total_calories == pytest.approx(small.total_calories * 2, rel=0.01)


def test_metadata_reports_a_confidence_and_agent_name() -> None:
    agent = NutritionVerificationAgent()
    result = agent.calculate_meal_macros(
        [Ingredient(item_name="chicken breast", base_quantity_grams=150)]
    )
    assert 0 <= result.metadata.confidence <= 1
    assert result.metadata.agent_name
```

- [ ] **Step 2: Run them**

```bash
uv run pytest backend/tests/test_nutrition_agent.py -v
```
Expected: all pass. **If `test_a_trusted_override_short_circuits_the_providers` skips**, note it and pick an ingredient that *is* in the override table — check with
`uv run python -c "from backend.app.rag.reference_data import load_reference; print(sorted(load_reference('trusted_overrides'))[:10])"`.

- [ ] **Step 3: Measure the improvement**

```bash
uv run pytest --cov=backend/app --cov-report=term | grep -E "nutrition_verification|TOTAL"
```
Expected: nutrition agent well above its 51% baseline. **Report both numbers.**

- [ ] **Step 4: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/tests/test_nutrition_agent.py
git commit -F - <<'MSG'
test(agents): cover the nutrition agent's provider chain and cooldown

At 51% this was the least-covered module in the backend, and the untested part
was the resilience logic that exists precisely so a slow or misconfigured
provider degrades instead of stalling every request. Spec section 8.

Covers the full chain in order - trusted local override, per-process cache, USDA,
FatSecret, local estimate - plus the parts that only matter when things go wrong:
three consecutive failures opening a 120-second cooldown, a cooled-down provider
being skipped without a call, and a success resetting the counter.

Every test patches urlopen on the agent's own module. Patching
urllib.request.urlopen would not intercept it, because the module binds the name
at import.

No production code changed.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 3: Supermarket agent coverage

79%, uncovered at lines 53, 91-98, 115-116, 126-133.

**Files:**
- Create: `backend/tests/test_supermarket_agent.py`

- [ ] **Step 1: Find out what the uncovered lines do**

```bash
uv run pytest --cov=backend/app --cov-report=term-missing | grep supermarket
sed -n '45,60p;85,100p;110,135p' backend/app/agents/supermarket_agent.py
```
Read them before writing tests, and **write tests that target those branches** rather than re-covering the happy path the existing suite already exercises.

- [ ] **Step 2: Write the tests**

Create `backend/tests/test_supermarket_agent.py`:

```python
"""Supermarket agent: store lookup, pricing and unmatched ingredients."""

import pytest

from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.schemas.requests import Ingredient


def test_a_shopping_list_is_produced_for_every_ingredient() -> None:
    """Every ingredient must appear, matched or not."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[
            Ingredient(item_name="chicken breast", base_quantity_grams=200),
            Ingredient(item_name="brown rice", base_quantity_grams=150),
        ],
        user_location="Earlwood, NSW",
    )
    assert len(payload.shopping_list) == 2
    assert payload.total_estimated_cost > 0


def test_an_unknown_ingredient_still_gets_a_price() -> None:
    """An unmatched item must fall back, not vanish from the list."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="zzz unheard of item",
                                base_quantity_grams=100)],
        user_location="Earlwood, NSW",
    )
    assert len(payload.shopping_list) == 1
    assert payload.shopping_list[0].estimated_price > 0


def test_total_is_the_sum_of_the_line_items() -> None:
    """The headline number must reconcile with the lines beneath it."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[
            Ingredient(item_name="chicken breast", base_quantity_grams=200),
            Ingredient(item_name="olive oil", base_quantity_grams=20),
            Ingredient(item_name="tomato", base_quantity_grams=100),
        ],
        user_location="Earlwood, NSW",
    )
    assert payload.total_estimated_cost == pytest.approx(
        sum(item.estimated_price for item in payload.shopping_list), rel=0.01
    )


def test_an_empty_ingredient_list_is_handled() -> None:
    """Zero ingredients must not divide by zero in the confidence average."""
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(ingredients=[], user_location="Earlwood, NSW")
    assert payload.shopping_list == []
    assert payload.metadata.confidence == 0.0


def test_store_details_are_populated_for_any_location() -> None:
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="tomato", base_quantity_grams=100)],
        user_location="Somewhere Unmapped, XX",
    )
    assert payload.store_details.store_name
    assert payload.store_details.location_source


def test_confidence_stays_within_bounds() -> None:
    agent = SupermarketAgent()
    payload = agent.generate_shopping_list(
        ingredients=[Ingredient(item_name="chicken breast", base_quantity_grams=200)],
        user_location="Earlwood, NSW",
    )
    assert 0 <= payload.metadata.confidence <= 1
    assert all(0 <= item.confidence <= 1 for item in payload.shopping_list)
```

- [ ] **Step 3: Run and measure**

```bash
uv run pytest backend/tests/test_supermarket_agent.py -v
uv run pytest --cov=backend/app --cov-report=term-missing | grep -E "supermarket|TOTAL"
```
Report the before (79%) and after figures, and **which lines remain uncovered**. If a line is genuinely unreachable — a guard for a condition the type system prevents — say so rather than contorting a test to reach it.

- [ ] **Step 4: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/tests/test_supermarket_agent.py
git commit -F - <<'MSG'
test(agents): cover the supermarket agent

The agent had no direct tests - its 79% came incidentally from the meal-plan
endpoint tests, which only ever exercise the happy path. Spec section 8.

Targets the branches that were uncovered: an unmatched ingredient still getting a
fallback price, an empty ingredient list not dividing by zero in the confidence
average, and store details being populated for an unmapped location. Also pins
the invariant that the headline total reconciles with the sum of its line items.

No production code changed.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 4: Direct tests for the constraint rules

`rag/rules.py` is at 90% **indirectly**. Uncovered: 192-193, 195, 200, 214, 220, 226 — the vegan, vegetarian, sodium-sensitive and kidney-disease branches. These decide whether a meal is safe for someone with a stated condition, so they deserve direct tests.

**Files:**
- Create: `backend/tests/test_rag_rules.py`

- [ ] **Step 1: Confirm the public surface**

```bash
uv run python -c "
import backend.app.rag.rules as r
print([n for n in dir(r) if not n.startswith('_') and callable(getattr(r, n))])
"
```
Use only the names it prints. The plan expects `normalize_label`, `constraint_groups`,
`blocked_groups_for_ingredient`, `meal_is_allowed`, `substitution_plan_for_meal`,
`meal_conflicts_with_health_conditions`, `planned_substitution` — **verify before using**.

- [ ] **Step 2: Write the tests**

Create `backend/tests/test_rag_rules.py`:

```python
"""Constraint rules: which groups a label implies, and what they block.

These branches decide whether a meal is safe for a stated health condition, so
they are tested directly rather than only through retrieval.
"""

import pytest

from backend.app.rag.rules import (
    blocked_groups_for_ingredient,
    constraint_groups,
    normalize_label,
)


def test_normalize_label_lowercases_and_strips() -> None:
    assert normalize_label("  High Protein  ") == "high protein"


@pytest.mark.parametrize("label", ["vegan", "plant based", "plant-based"])
def test_vegan_implies_dairy_and_egg(label: str) -> None:
    """Vegan must imply the narrower groups, or a vegan meal could contain cheese."""
    groups = constraint_groups([label])
    assert "vegan" in groups
    assert "dairy" in groups
    assert "egg" in groups


def test_vegetarian_is_not_vegan() -> None:
    """Vegetarian must not silently imply dairy-free."""
    groups = constraint_groups(["vegetarian"])
    assert "vegetarian" in groups
    assert "dairy" not in groups


@pytest.mark.parametrize(
    "label", ["hypertension", "high blood pressure", "low sodium"]
)
def test_sodium_labels_all_map_to_one_group(label: str) -> None:
    """Three ways of saying the same thing must behave identically."""
    assert "sodium_sensitive" in constraint_groups([label])


def test_no_labels_means_no_groups() -> None:
    assert constraint_groups([]) == set()


@pytest.mark.parametrize(
    "ingredient", ["chicken breast", "salmon fillet", "whole egg"]
)
def test_vegan_blocks_animal_products(ingredient: str) -> None:
    groups = constraint_groups(["vegan"])
    assert blocked_groups_for_ingredient(ingredient, groups)


def test_vegetarian_blocks_meat_but_allows_dairy() -> None:
    """The vegetarian branch must be narrower than the vegan one."""
    groups = constraint_groups(["vegetarian"])
    assert blocked_groups_for_ingredient("chicken breast", groups)
    assert not blocked_groups_for_ingredient("greek yogurt", groups)


def test_sodium_sensitive_blocks_soy_sauce() -> None:
    groups = constraint_groups(["hypertension"])
    assert "sodium_sensitive" in blocked_groups_for_ingredient("soy sauce", groups)


def test_an_unconstrained_ingredient_is_never_blocked() -> None:
    groups = constraint_groups(["vegan", "hypertension"])
    assert blocked_groups_for_ingredient("brown rice", groups) == set()
```

- [ ] **Step 3: Run and measure**

```bash
uv run pytest backend/tests/test_rag_rules.py -v
uv run pytest --cov=backend/app --cov-report=term-missing | grep -E "rules|TOTAL"
```
**If any test fails, that is a finding about the rules, not the test.** Report the exact
behaviour — for instance if `vegetarian` turns out to block yogurt, say so; do not adjust
the assertion to match. Report which of lines 192-193, 195, 200, 214, 220, 226 are now covered.

- [ ] **Step 4: Confirm the retrieval regression suite is untouched**

```bash
uv run pytest backend/tests/test_retrieval_quality_regression.py backend/tests/test_meal_vector_rag.py
```
Expected: all pass. These are the standing guard on RAG behaviour.

- [ ] **Step 5: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/tests/test_rag_rules.py
git commit -F - <<'MSG'
test(rag): test the constraint rules directly

rules.py was at 90%, but entirely through retrieval tests exercising it
incidentally - it had no direct tests. The uncovered branches were the ones
deciding whether a meal is safe for a stated health condition, which is the last
place to rely on indirect coverage. Spec section 8.

Covers the group-expansion logic (vegan implying dairy and egg; vegetarian
deliberately not implying dairy; three sodium phrasings mapping to one group) and
the blocking logic that follows from it, including that an unconstrained
ingredient is never blocked.

No production code changed. The retrieval regression suite still passes unchanged.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 5: Frontend tests

**Files:**
- Modify: `frontend/package.json`, `frontend/package-lock.json`
- Create: `frontend/vitest.config.js`, `frontend/src/test/setup.js`, and test files

- [ ] **Step 1: Look at what there is to test**

```bash
ls -R frontend/src
wc -l frontend/src/*.jsx frontend/src/**/*.js* 2>/dev/null
grep -n "axios\|API_BASE_URL" frontend/src/App.jsx | head
```
Phase 4 splits `App.jsx` into `api/`, `components/` and `features/`; **that has not happened yet**, so `App.jsx` is still one large file. Write tests against the structure that exists — do not restructure it here, that is Phase 4's job and doing it now would collide.

- [ ] **Step 2: Install the tooling**

```bash
cd frontend
npm install --save-dev vitest @vitest/coverage-v8 jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Add to `frontend/package.json` scripts:
```json
    "test": "vitest run",
    "test:watch": "vitest"
```

- [ ] **Step 3: Configure vitest**

Create `frontend/vitest.config.js`:

```javascript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    css: false,
  },
})
```

Create `frontend/src/test/setup.js`:

```javascript
import '@testing-library/jest-dom'
```

- [ ] **Step 4: Write the tests**

Create `frontend/src/App.test.jsx`. Mock axios so no request is attempted:

```javascript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [] } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

import axios from 'axios'
import App from './App'

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing and shows the tab bar', () => {
    render(<App />)
    expect(screen.getByText(/meal plan/i)).toBeInTheDocument()
  })

  it('switches to the calories tab', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('button', { name: /calories/i }))
    expect(screen.getByText(/predict/i)).toBeInTheDocument()
  })

  it('switches to the history tab', async () => {
    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('button', { name: /history/i }))
    expect(screen.getByText(/history/i)).toBeInTheDocument()
  })

  it('never calls the network on first render', () => {
    render(<App />)
    expect(axios.get).not.toHaveBeenCalled()
    expect(axios.post).not.toHaveBeenCalled()
  })
})
```

**These selectors are guesses against a file this plan has not read line by line.** Run the
tests, and where a selector does not match, **fix the selector to match the real UI** — read
`frontend/src/App.jsx` and use the actual button labels and headings. Do **not** change
`App.jsx` to match the test. Report every selector you had to adjust.

- [ ] **Step 5: Run them**

```bash
cd frontend && npm test
```
Expected: all pass. Then confirm the existing gates still work:
```bash
npm run lint && npm run build
```

- [ ] **Step 6: Commit**

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
uv run ruff check .
git status --short
git add frontend/package.json frontend/package-lock.json frontend/vitest.config.js frontend/src/test frontend/src/App.test.jsx
git commit -F - <<'MSG'
test(frontend): add vitest and React Testing Library

The React dashboard had no tests at all - CI only linted and built it, so a
component could render nothing and still pass. Spec section 8.

Adds vitest with jsdom plus React Testing Library, and covers what matters at
this stage: the app renders, each tab switches, and nothing calls the network on
first render. axios is mocked, so the suite cannot become an integration test by
accident.

Tests are written against the current single-file App.jsx. Phase 4 splits it into
api/, components/ and features/; these tests move with it rather than blocking it.

No component code changed.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 6: The coverage gate

**Files:**
- Modify: `.github/workflows/ci.yml`, `pyproject.toml`
- Modify: `docs/5_agent_log.md`

- [ ] **Step 1: Measure the real post-phase number**

```bash
uv run pytest --cov=backend/app --cov-report=term | tail -3
```
Write down the exact `TOTAL` percentage. **The floor is that number rounded down to the nearest whole percent, minus 1** — high enough to catch a regression, low enough not to fail on a rounding wobble. Do not pick an aspirational number; the spec says the floor must be honest.

- [ ] **Step 2: Configure the floor**

Add to `pyproject.toml` under `[tool.pytest.ini_options]`, replacing the existing `addopts`:

```toml
addopts = "-q --cov=backend/app --cov-report=term-missing --cov-fail-under=<FLOOR>"
```

where `<FLOOR>` is the integer from Step 1. **Note this makes every local `uv run pytest`
run with coverage** — confirm the suite still passes and note the runtime change.

- [ ] **Step 3: Add the frontend test job to CI**

In `.github/workflows/ci.yml`, in the existing `frontend` job, add a step **between** Lint and Build:

```yaml
      - name: Test
        run: npm test
```

The backend job needs no change — coverage now runs via `addopts`, so `uv run pytest` enforces the floor automatically.

- [ ] **Step 4: Prove the gate actually fails**

A gate that has never failed is not known to work. Temporarily raise the floor above the real number:

```bash
sed -i '' "s/--cov-fail-under=<FLOOR>/--cov-fail-under=99/" pyproject.toml
uv run pytest 2>&1 | tail -3
```
Expected: FAIL with `Coverage failure: total of ... is less than fail-under=99`.

Then restore the real floor and confirm green:
```bash
sed -i '' "s/--cov-fail-under=99/--cov-fail-under=<FLOOR>/" pyproject.toml
uv run pytest 2>&1 | tail -2
```

Do the same for the frontend: break a `frontend/src/App.test.jsx` assertion, confirm
`npm test` exits non-zero, and restore.

- [ ] **Step 5: Append the Phase 3 log entry**

Append a dated entry to `docs/5_agent_log.md` recording: the coverage before (82%) and
after; which modules moved and by how much; that the network guard now enforces the
spec's "no network access in CI"; the frontend suite; the floor and why it was set where
it was; and anything still uncovered on purpose — notably `rag/embedding_index.py` at 32%,
whose sentence-transformers/FAISS path is an unlocked optional extra.

- [ ] **Step 6: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add pyproject.toml .github/workflows/ci.yml docs/5_agent_log.md
git commit -F - <<'MSG'
ci(workflows): enforce a coverage floor and run the frontend tests

Spec section 8's "done when": CI enforces the coverage floor.

The floor is set from the measured post-phase number rather than an aspiration,
so it catches a regression without failing on a rounding wobble. It lives in
pyproject.toml's addopts, so a local pytest run enforces exactly what CI does.

The frontend job now runs npm test between lint and build, so a component that
renders nothing can no longer pass CI.

Both gates were proved to fail before being trusted: raising the floor to 99 made
the backend job fail with a coverage message, and breaking an assertion made the
frontend job exit non-zero. Both reverted.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Phase 3 Exit Gate

Per spec §8: done when every endpoint has a test, the contract suite runs green against both
storage backends, and CI enforces the coverage floor.

- [x] `uv run pytest` green, with the coverage floor active. Report the real count and percentage
- [x] `uv run ruff check .` and `uv run ruff format --check .` clean
- [x] Every endpoint has a test — 8 routes covered by `test_api_endpoints.py` (delivered in Phase 1)
- [x] The contract suite passes against **both** backends with **zero skips**
- [x] The coverage floor was **proved to fail** when raised above the real number, then restored
- [x] `npm test` passes, and was **proved to fail** on a broken assertion, then restored
- [x] `npm run lint` and `npm run build` still pass
- [x] The network guard is active: a test making a real connection fails
- [x] `nutrition_verification_agent.py` is well above its 51% baseline — report the figure
- [x] The retrieval regression suite passes unchanged
- [x] `uv lock --check` passes and `backend/requirements.txt` is unchanged (dev-only additions)
- [x] `scikit-learn` still exactly `1.6.1`
- [x] `git status --short` clean; `database/*.json` md5-unchanged; no `.env` or `.db` staged
- [x] **No production code changed** — `git diff <merge-base> HEAD -- backend/app streamlit_app frontend/src/App.jsx` shows nothing but the new test files
- [x] Phase 3 entry appended to `docs/5_agent_log.md`; this checklist ticked

Then write the Phase 4 plan from spec §9.
