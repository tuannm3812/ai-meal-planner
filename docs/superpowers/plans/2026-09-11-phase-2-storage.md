# Phase 2 — Storage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put every repository behind a `Protocol`, make the JSON store safe, add a real SQLite backend, and prove the two are interchangeable.

**Architecture:** `repositories/base.py` defines a `Protocol` per repository. The existing JSON implementations move to `repositories/json_store/` and gain atomic writes; new SQLModel-backed implementations live in `repositories/sql/`. A `STORAGE_BACKEND` setting picks between them at container-build time, and one contract test suite runs against both, so "they behave identically" is a test result rather than a claim.

**Tech Stack:** Python 3.11/3.12, FastAPI, Pydantic v2, **pydantic-settings 2.15**, **SQLModel 0.0.42 / SQLAlchemy 2.0.52** (new), SQLite (stdlib driver), pytest, uv, ruff.

**Spec:** `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md` §7
**Branches from:** `refactor/phase-1-backend-architecture` (PR #2, not yet merged). Its PR targets that branch.

## Global Constraints

- **Baseline: 58 passing tests.** Run `uv run pytest` — **never** `uv run pytest -q`; `pyproject.toml` sets `addopts = "-q"` and a second `-q` becomes `-qq`, hiding the summary. **Counts in this plan are collected cases and parametrization expands them. If pytest reports a different number, trust pytest and report the real figure** — the Phase 1 ladder had to be re-based twice for exactly this.
- **Never `git add -A`.** Run `git status --short`, review every path, stage explicitly. Master standard §10.1.
- Commit format `<type>(<scope>): <imperative summary>`. **The `(scope)` is mandatory** — if a pre-written subject here omits it, the pre-written text is wrong. Every body ends with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`, that exact string whichever model you are.
- **This phase is the first allowed to change dependencies**, and only in Task 1. After `uv add`, you MUST run `uv lock` and re-export: `uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt`, or CI's drift job fails. **`scikit-learn` must stay pinned at exactly `1.6.1`** and `pydantic` must stay on 2.x — verify in `uv.lock` after locking.
- **Do not modify** `notebooks/**` or `.github/`.
- **`.gitignore`: exactly one addition is permitted**, `database/*.db`, because SQLite
  now writes there and the file must not be committed. Add it beside the existing
  `database/*.json` lines. **Do not touch anything else in that file** — its
  blanket-rule-plus-negation block for the model artifact is cited by the master
  standard as a correct example, and re-tidying it would break that.
- **Never delete, skip or weaken a test.** If an existing test fails, fix the calling code.
- **When you change a signature, grep the WHOLE repo for callers**, not just `backend/`: `grep -rn "<name>" --include="*.py" . | grep -v node_modules`. `streamlit_app/app.py` constructs repositories directly and has no test coverage.
- **`kill %1` does not stop uvicorn** (`uv run` spawns a child). After any live check: `pkill -f "uvicorn backend.app.main:app"` then confirm with `lsof -i :8000`.
- Google-style docstrings on every public class and function you add.
- Ruff clean: `uv run ruff check .` and `uv run ruff format --check .`.
- Work on branch `refactor/phase-2-storage`. Do not push or open PRs; the controller handles that.

## Verified Starting State

Measured on 2026-09-11 at the tip of `refactor/phase-1-backend-architecture`:

| Check | Result |
| --- | --- |
| `uv run pytest` | **58 passed** |
| `ruff check` / `format --check` | clean, 45 files |
| Existing local data | `database/meal_history.json` **44 records**, `database/meal_feedback.json` **19 records** |
| Dependency resolution | `pydantic-settings 2.15.0`, `sqlmodel 0.0.42`, `sqlalchemy 2.0.52`, plus `greenlet`. `pydantic` stays `2.13.5`, `scikit-learn` stays `1.6.1` — **verified by resolving in a scratch project** |
| SQLModel JSON column | round-trips nested dicts; `ix_meal_plans_user_id` index created — **verified** |
| pydantic-settings | reads `APP_NAME` from env, honours defaults — **verified** |
| Env vars `config.py` reads | 15, listed in Task 1 |

## Critical Facts

### The default profile is a feature, not a bug

`UserProfileRepository.fetch_user_profile` returns `profiles["default"]` when the
user is absent. Every request in this project uses `user_id="user_123"`, which is
**not** in any profiles file — so the default path is the *normal* path. **Do not
make this raise `ProfileNotFound`.** Doing so would 404 every request. The SQL
implementation must reproduce the same fallback.

### Records are heterogeneous, and old ones must stay readable

`meal_history` rows are whole API responses from *earlier versions of the code* —
a 44-record file spanning several response shapes. The SQL schema therefore stores
the payload as a JSON column, not as typed columns. Do not try to normalise it.

### `saved_at` ordering, and what `list_for_user` returns

Both JSON repositories append and then return `list(reversed(records[-limit:]))` —
i.e. **newest first**, capped at `limit`. The SQL implementation must match that
ordering exactly, or the history tab silently reorders. Note the JSON version
slices *before* reversing, so it returns the last `limit` records in reverse order.

### `MealPlanRepository.save` returns `None`; `MealFeedbackRepository.save` returns the record

They differ. Preserve both signatures.

---

## File Structure

**Created:**

| File | Responsibility |
| --- | --- |
| `backend/app/repositories/base.py` | One `Protocol` per repository; the seam everything else depends on |
| `backend/app/repositories/json_store/__init__.py` | Re-exports the JSON implementations |
| `backend/app/repositories/json_store/repositories.py` | The moved JSON implementations, with atomic writes |
| `backend/app/repositories/sql/__init__.py` | Re-exports the SQL implementations |
| `backend/app/repositories/sql/models.py` | SQLModel table definitions |
| `backend/app/repositories/sql/repositories.py` | SQLite implementations |
| `backend/app/repositories/factory.py` | `build_repositories(settings)` → the trio, chosen by `STORAGE_BACKEND` |
| `scripts/migrate_json_to_sqlite.py` | One-off import of existing JSON records into SQLite |
| `backend/tests/test_repository_contract.py` | **One suite, parameterised over both backends** |
| `backend/tests/test_storage_backend_parity.py` | Same API responses under either backend |

**Modified:** `backend/app/core/config.py` (→ pydantic-settings), `backend/app/core/container.py`, `backend/app/services/meal_planning_service.py` (typing + single profile read), `pyproject.toml`, `uv.lock`, `backend/requirements.txt`, `backend/.env.example`, `.env.example`, `docs/4_next_steps.md`.

**Deleted:** `backend/app/repositories/storage.py` (contents move to `json_store/repositories.py`).

---

## Task 1: Add the dependencies and migrate config to pydantic-settings

**Files:**
- Modify: `pyproject.toml`, `uv.lock`, `backend/requirements.txt`
- Modify: `backend/app/core/config.py`
- Modify: `backend/.env.example`, `.env.example`
- Test: `backend/tests/test_config.py` (create)

**Interfaces:**
- Produces: `AppSettings` as a `pydantic_settings.BaseSettings` subclass with all 15 existing fields **plus** `storage_backend: str = "sqlite"` and `sqlite_path: Path`. `AppSettings.from_env()` is retained as a classmethod returning `cls()`, so every existing call site keeps working unchanged.

- [ ] **Step 1: Record the exact current settings values, to compare against later**

```bash
uv run python -c "
from backend.app.core.config import AppSettings
import json
s = AppSettings.from_env()
print(json.dumps({k: str(v) for k, v in vars(s).items()}, indent=1, sort_keys=True))
" > /tmp/settings_before.json
cat /tmp/settings_before.json
```

Keep `/tmp/settings_before.json`. Step 7 diffs against it. This is the proof the
migration changed no resolved value.

- [ ] **Step 2: Add the dependencies**

```bash
uv add pydantic-settings sqlmodel
```

Then confirm the pins that matter did not move:

```bash
grep -A1 -E '^name = "(pydantic|scikit-learn|sqlmodel|pydantic-settings)"' uv.lock | grep -E "name|version" | paste - -
```

Expected: `pydantic` on `2.x`, `scikit-learn` exactly `1.6.1`. If either moved, **stop and report** — do not proceed.

- [ ] **Step 3: Re-export the requirements file**

```bash
uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt
git diff --stat -- backend/requirements.txt
```

Expected: the file gains `pydantic-settings`, `sqlmodel`, `sqlalchemy` and
`greenlet`. CI's drift job regenerates this exact command, so it must be run.

- [ ] **Step 4: Write the failing config test**

Create `backend/tests/test_config.py`:

```python
"""Settings must resolve from the environment with correct defaults."""

from pathlib import Path

import pytest

from backend.app.core.config import AppSettings


def test_defaults_are_unchanged() -> None:
    """The values the app relied on before pydantic-settings still hold."""
    settings = AppSettings()
    assert settings.app_name == "Multi-Agent Meal Planner API"
    assert settings.environment == "development"
    assert settings.rag_backend == "auto"
    assert settings.rag_embedding_activation_size == 50
    assert settings.enable_gemini_adaptation is False


def test_storage_backend_defaults_to_sqlite() -> None:
    assert AppSettings().storage_backend == "sqlite"


@pytest.mark.parametrize("value", ["json", "sqlite"])
def test_storage_backend_accepts_both_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("STORAGE_BACKEND", value)
    assert AppSettings().storage_backend == value


def test_storage_backend_rejects_anything_else(monkeypatch: pytest.MonkeyPatch) -> None:
    """A typo must fail loudly at startup, not silently pick a backend."""
    monkeypatch.setenv("STORAGE_BACKEND", "postgres")
    with pytest.raises(ValueError):
        AppSettings()


def test_allowed_origins_parses_a_comma_separated_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://a.test, http://b.test")
    assert AppSettings().allowed_origins == ["http://a.test", "http://b.test"]


def test_relative_paths_resolve_against_the_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """A relative MEAL_CORPUS_PATH must not depend on the process's cwd."""
    monkeypatch.setenv("MEAL_CORPUS_PATH", "data/meal_corpus/meals.json")
    resolved = AppSettings().meal_corpus_path
    assert resolved.is_absolute()
    assert resolved.exists()


def test_from_env_still_works() -> None:
    """Existing call sites use AppSettings.from_env(); it must keep working."""
    assert isinstance(AppSettings.from_env(), AppSettings)


def test_sqlite_path_defaults_under_the_data_dir() -> None:
    settings = AppSettings()
    assert settings.sqlite_path == settings.data_dir / "ai_meal_planner.db"
    assert isinstance(settings.sqlite_path, Path)
```

- [ ] **Step 5: Run to verify it fails**

Run: `uv run pytest backend/tests/test_config.py`
Expected: FAIL — `AppSettings() takes no arguments` / `storage_backend` missing.

- [ ] **Step 6: Rewrite `backend/app/core/config.py`**

Replace the whole file:

```python
"""Application settings, resolved from the environment."""

import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


def _resolve_repo_path(path_value: Path | str) -> Path:
    """Resolve a possibly-relative path against the repository root.

    Args:
        path_value: An absolute path, or one relative to the repo root.

    Returns:
        An absolute path. Resolving against the repo root rather than the
        process's working directory means the API behaves the same however it
        is started.
    """
    path = Path(path_value)
    return path if path.is_absolute() else BASE_DIR / path


class AppSettings(BaseSettings):
    """Every setting the application reads, with its default."""

    model_config = SettingsConfigDict(
        env_file=None if os.getenv("SKIP_DOTENV") == "1" else BASE_DIR / "backend" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Multi-Agent Meal Planner API"
    environment: str = Field(default="development", alias="APP_ENV")
    # NoDecode is required: pydantic-settings treats list[str] as a "complex" type and
    # runs json.loads() on the raw env value BEFORE any field_validator, so a
    # comma-separated ALLOWED_ORIGINS raises SettingsError. NoDecode skips that step
    # and lets _split_csv below handle it.
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    gemini_api_key: str | None = None
    usda_api_key: str | None = None
    fatsecret_client_id: str | None = None
    fatsecret_client_secret: str | None = None
    maps_api_key: str | None = None
    inventory_api_key: str | None = None

    calorie_model_path: Path = (
        BASE_DIR / "models" / "calorie_expenditure" / "calorie_expenditure_model.joblib"
    )
    calorie_model_version: str = "hist_gradient_boosting_deep_v0.1.0"
    meal_corpus_path: Path = BASE_DIR / "data" / "meal_corpus" / "meals.json"
    rag_backend: str = "auto"
    rag_embedding_cache_dir: Path = BASE_DIR / "data" / "vector_index"
    rag_embedding_activation_size: int = 50
    enable_gemini_adaptation: bool = False

    storage_backend: Literal["json", "sqlite"] = "sqlite"

    @property
    def data_dir(self) -> Path:
        """Directory holding the JSON stores and the SQLite database."""
        return BASE_DIR / "database"

    @property
    def sqlite_path(self) -> Path:
        """Filesystem location of the SQLite database."""
        return self.data_dir / "ai_meal_planner.db"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        """Accept ALLOWED_ORIGINS as a comma-separated string.

        Args:
            value: The raw environment value, or an already-parsed list.

        Returns:
            A list of origins with blanks removed, or the value unchanged when
            it is not a string.
        """
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("calorie_model_path", "meal_corpus_path", "rag_embedding_cache_dir")
    @classmethod
    def _resolve(cls, value: Path) -> Path:
        """Resolve configured paths against the repository root.

        Args:
            value: The configured path, absolute or repo-relative.

        Returns:
            An absolute path.
        """
        return _resolve_repo_path(value)

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Build settings from the environment.

        Retained so existing call sites keep working after the migration to
        pydantic-settings.

        Returns:
            A populated AppSettings.
        """
        return cls()
```

Note `data_dir` and `sqlite_path` are **properties**, not fields, so they are not
settable from the environment — matching the old hard-coded `data_dir`.

- [ ] **Step 7: Prove no resolved value changed**

```bash
uv run python -c "
from backend.app.core.config import AppSettings
import json
s = AppSettings.from_env()
keys = ['app_name','environment','allowed_origins','gemini_api_key','usda_api_key',
        'fatsecret_client_id','fatsecret_client_secret','maps_api_key','inventory_api_key',
        'data_dir','calorie_model_path','calorie_model_version','meal_corpus_path',
        'rag_backend','rag_embedding_cache_dir','rag_embedding_activation_size',
        'enable_gemini_adaptation']
print(json.dumps({k: str(getattr(s, k)) for k in keys}, indent=1, sort_keys=True))
" > /tmp/settings_after.json
diff <(uv run python -c "
import json; d=json.load(open('/tmp/settings_before.json'))
print(json.dumps({k:v for k,v in d.items() if not k.startswith('_')}, indent=1, sort_keys=True))
") /tmp/settings_after.json && echo "SETTINGS IDENTICAL"
```

Expected: `SETTINGS IDENTICAL`. If any value differs, fix the settings class —
**do not** edit the snapshot. Report every field that differed and why.

- [ ] **Step 8: Document the new setting**

Add to both `backend/.env.example` and `.env.example`, after `ENABLE_GEMINI_ADAPTATION`:

```dotenv
# json keeps the file-backed stores; sqlite uses database/ai_meal_planner.db
STORAGE_BACKEND=sqlite
```

- [ ] **Step 9: Verify and commit**

```bash
uv run pytest
```
Expected: **66 passed** (58 + 8 new). Trust pytest if it differs.

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add pyproject.toml uv.lock backend/requirements.txt backend/app/core/config.py backend/tests/test_config.py backend/.env.example .env.example
git commit -F - <<'MSG'
feat(config): migrate settings to pydantic-settings and add STORAGE_BACKEND

Replaces the hand-rolled AppSettings dataclass and its _csv_env/_resolve_repo_path
helpers with a pydantic_settings.BaseSettings subclass. Spec section 7 item 4.

Adds pydantic-settings and sqlmodel as dependencies. The spec had assumed
pydantic-settings came free with pydantic; it does not, it is a separate
distribution. sqlmodel is added here so the lockfile changes land in one commit
rather than two. Resolution verified: pydantic stays on 2.x and scikit-learn
stays pinned at 1.6.1, with sqlalchemy and greenlet arriving transitively.
backend/requirements.txt re-exported so CI's drift job stays green.

Adds STORAGE_BACKEND, typed as Literal["json", "sqlite"] and defaulting to
sqlite, so a typo fails loudly at startup instead of silently selecting a
backend. data_dir and sqlite_path are properties rather than fields, matching
the old hard-coded data_dir - they are not settable from the environment.

from_env() is retained as a classmethod so every existing call site is unchanged.

Verified: all 17 resolved settings values are byte-identical to the pre-migration
snapshot, and 66 tests pass.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 2: Repository protocols, and atomic JSON writes

**Files:**
- Create: `backend/app/repositories/base.py`
- Create: `backend/app/repositories/json_store/__init__.py`, `backend/app/repositories/json_store/repositories.py`
- Delete: `backend/app/repositories/storage.py`
- Modify: `backend/app/core/container.py`, `streamlit_app/app.py` (import path only)

**Interfaces:**
- Produces: three `Protocol` classes in `backend/app/repositories/base.py`:
  - `UserProfileStore` with `fetch_user_profile(self, user_id: str) -> dict[str, Any]`
  - `MealPlanStore` with `save(self, payload: dict[str, Any]) -> None` and `list_for_user(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]`
  - `MealFeedbackStore` with `save(self, payload: dict[str, Any]) -> dict[str, Any]` and `list_for_user(self, user_id: str, limit: int = 20, saved_only: bool = False) -> list[dict[str, Any]]`
  The concrete JSON classes keep their existing names — `UserProfileRepository`, `MealPlanRepository`, `MealFeedbackRepository` — and move to `backend.app.repositories.json_store`.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_json_store.py`:

```python
"""JSON repositories must write atomically and keep every record."""

import json
from pathlib import Path

from backend.app.repositories.base import MealFeedbackStore, MealPlanStore, UserProfileStore
from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)


def test_implementations_satisfy_the_protocols(tmp_path: Path) -> None:
    """Runtime-checkable protocols make the seam real, not decorative."""
    assert isinstance(UserProfileRepository(tmp_path), UserProfileStore)
    assert isinstance(MealPlanRepository(tmp_path), MealPlanStore)
    assert isinstance(MealFeedbackRepository(tmp_path), MealFeedbackStore)


def test_meal_plans_are_not_capped_at_200(tmp_path: Path) -> None:
    """The old implementation silently discarded everything past 200."""
    repo = MealPlanRepository(tmp_path)
    for i in range(205):
        repo.save({"request": {"user_id": "u1"}, "n": i})
    stored = json.loads((tmp_path / "meal_history.json").read_text(encoding="utf-8"))
    assert len(stored) == 205


def test_feedback_is_not_capped_at_500(tmp_path: Path) -> None:
    repo = MealFeedbackRepository(tmp_path)
    for i in range(505):
        repo.save({"user_id": "u1", "n": i})
    stored = json.loads((tmp_path / "meal_feedback.json").read_text(encoding="utf-8"))
    assert len(stored) == 505


def test_writes_leave_no_temp_file_behind(tmp_path: Path) -> None:
    repo = MealPlanRepository(tmp_path)
    repo.save({"request": {"user_id": "u1"}})
    assert sorted(p.name for p in tmp_path.iterdir()) == ["meal_history.json"]


def test_a_crash_mid_write_cannot_corrupt_the_store(tmp_path: Path, monkeypatch) -> None:
    """The original wrote in place, so a crash truncated the file."""
    repo = MealPlanRepository(tmp_path)
    repo.save({"request": {"user_id": "u1"}, "n": 0})
    good = (tmp_path / "meal_history.json").read_text(encoding="utf-8")

    def _boom(*args: object, **kwargs: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("os.replace", _boom)
    try:
        repo.save({"request": {"user_id": "u1"}, "n": 1})
    except OSError:
        pass
    # The original file must be intact and still valid JSON.
    assert (tmp_path / "meal_history.json").read_text(encoding="utf-8") == good
    assert len(json.loads(good)) == 1
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest backend/tests/test_json_store.py`
Expected: FAIL — `No module named 'backend.app.repositories.base'`.

- [ ] **Step 3: Write the protocols**

Create `backend/app/repositories/base.py`:

```python
"""Storage protocols: the seam between the app and any concrete backend."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class UserProfileStore(Protocol):
    """Supplies stored biometrics for a user."""

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        """Return the profile for a user, or the default profile.

        Args:
            user_id: The profile key to look up.

        Returns:
            The stored profile, or the built-in default when the user has none.
            Returning a default rather than raising is deliberate: the app's
            normal path uses ids that have no stored profile.
        """
        ...


@runtime_checkable
class MealPlanStore(Protocol):
    """Persists generated meal plans."""

    def save(self, payload: dict[str, Any]) -> None:
        """Append one meal-plan response.

        Args:
            payload: The full API response to store.
        """
        ...

    def list_for_user(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return a user's most recent meal plans, newest first.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.

        Returns:
            Up to ``limit`` records, newest first.
        """
        ...


@runtime_checkable
class MealFeedbackStore(Protocol):
    """Persists user feedback on meals."""

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Append one feedback record.

        Args:
            payload: The feedback to store.

        Returns:
            The stored record, including its ``saved_at`` timestamp.
        """
        ...

    def list_for_user(
        self, user_id: str, limit: int = 20, saved_only: bool = False
    ) -> list[dict[str, Any]]:
        """Return a user's most recent feedback, newest first.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.
            saved_only: Restrict to records flagged as saved.

        Returns:
            Up to ``limit`` records, newest first.
        """
        ...
```

- [ ] **Step 4: Move the JSON implementations and make writes atomic**

```bash
mkdir -p backend/app/repositories/json_store
git mv backend/app/repositories/storage.py backend/app/repositories/json_store/repositories.py
```

Create `backend/app/repositories/json_store/__init__.py`:

```python
"""File-backed repository implementations."""

from .repositories import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)

__all__ = [
    "MealFeedbackRepository",
    "MealPlanRepository",
    "UserProfileRepository",
]
```

In `json_store/repositories.py`, add a module docstring, add `import os` and
`from tempfile import NamedTemporaryFile`, then add this shared helper above the
classes:

```python
def _write_json_atomically(path: Path, records: list[dict[str, Any]]) -> None:
    """Write records to path so a crash cannot leave a truncated file.

    Writes to a temporary file in the same directory, then renames it over the
    target. ``os.replace`` is atomic on POSIX and Windows, so a reader either
    sees the old file or the new one, never a partial write.

    Args:
        path: Destination file.
        records: Records to serialise.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
        delete=False,
    ) as handle:
        json.dump(records, handle, indent=2)
        temp_name = handle.name
    try:
        os.replace(temp_name, path)
    except OSError:
        Path(temp_name).unlink(missing_ok=True)
        raise
```

Then in `MealPlanRepository.save`, replace the `with self.history_path.open("w"...)`
block with `_write_json_atomically(self.history_path, records)` — **and delete the
`[-200:]` slice**, so no record is discarded. Do the same in
`MealFeedbackRepository.save`, deleting the `[-500:]` slice.

- [ ] **Step 5: Update the two import sites**

```bash
grep -rn "repositories.storage\|repositories import storage" --include="*.py" . | grep -v node_modules
```

Change each to `from ..repositories.json_store import (...)` (in
`backend/app/core/container.py`) and
`from backend.app.repositories.json_store import (...)` (in `streamlit_app/app.py`).
Run the grep again and confirm no hit remains.

- [ ] **Step 6: Verify**

```bash
uv run pytest
```
Expected: **71 passed** (66 + 5 new). Trust pytest if it differs.

- [ ] **Step 7: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/repositories backend/tests/test_json_store.py backend/app/core/container.py streamlit_app/app.py
git commit -F - <<'MSG'
feat(repositories): add storage protocols and make JSON writes atomic

Spec section 7 items 1 and 2.

repositories/base.py defines UserProfileStore, MealPlanStore and
MealFeedbackStore as runtime-checkable Protocols. The JSON implementations move
from storage.py to json_store/repositories.py under their existing names, so
call sites change only their import path.

Two fixes to the JSON store:
- writes go to a temp file in the same directory and are renamed over the target
  with os.replace, which is atomic on POSIX and Windows. The previous code wrote
  in place, so a crash mid-write truncated the store. A test monkeypatches
  os.replace to fail and asserts the original file survives intact.
- the [-200:] and [-500:] slices are gone. They silently discarded history once a
  user passed those counts; tests assert 205 and 505 records survive.

The protocols are runtime_checkable so the isinstance assertions in the tests
make the seam real rather than decorative.

Deliberately NOT changed: fetch_user_profile still returns the default profile
for an unknown user rather than raising. Every request in this project uses an
id with no stored profile, so the default path is the normal path.

Verified: 71 tests pass, no temp file left behind after a write.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 3: The contract test suite

Written before the SQL backend exists, so it is a genuine specification of
behaviour rather than a description of whatever SQLite happened to do.

**Files:**
- Create: `backend/tests/test_repository_contract.py`

**Interfaces:**
- Consumes: the protocols and JSON implementations from Task 2.
- Produces: three pytest fixtures — `profile_store`, `plan_store`, `feedback_store` — each parameterised over backend ids `"json"` and `"sqlite"`. Task 4 adds the SQLite branch; until then the fixtures `pytest.skip` on `"sqlite"`.

- [ ] **Step 1: Write the suite**

Create `backend/tests/test_repository_contract.py`:

```python
"""One behavioural contract, run against every storage backend.

Both backends must satisfy this identically. When they diverge, this is the
file that says which one is wrong.
"""

from pathlib import Path
from typing import Any

import pytest

from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)

BACKENDS = ["json", "sqlite"]


def _skip_until_implemented(backend: str) -> None:
    """Skip the SQLite branch until Task 4 lands it."""
    if backend == "sqlite":
        try:
            import backend.app.repositories.sql  # noqa: F401
        except ImportError:
            pytest.skip("SQLite backend not implemented yet (Task 4)")


@pytest.fixture(params=BACKENDS)
def profile_store(request: pytest.FixtureRequest, tmp_path: Path) -> Any:
    _skip_until_implemented(request.param)
    if request.param == "json":
        return UserProfileRepository(tmp_path)
    from backend.app.repositories.sql import SqlUserProfileRepository, build_engine

    return SqlUserProfileRepository(build_engine(tmp_path / "t.db"))


@pytest.fixture(params=BACKENDS)
def plan_store(request: pytest.FixtureRequest, tmp_path: Path) -> Any:
    _skip_until_implemented(request.param)
    if request.param == "json":
        return MealPlanRepository(tmp_path)
    from backend.app.repositories.sql import SqlMealPlanRepository, build_engine

    return SqlMealPlanRepository(build_engine(tmp_path / "t.db"))


@pytest.fixture(params=BACKENDS)
def feedback_store(request: pytest.FixtureRequest, tmp_path: Path) -> Any:
    _skip_until_implemented(request.param)
    if request.param == "json":
        return MealFeedbackRepository(tmp_path)
    from backend.app.repositories.sql import SqlMealFeedbackRepository, build_engine

    return SqlMealFeedbackRepository(build_engine(tmp_path / "t.db"))


def test_profile_returns_the_default_for_an_unknown_user(profile_store: Any) -> None:
    """The default profile is the normal path, not an error case."""
    profile = profile_store.fetch_user_profile("nobody_at_all")
    assert profile["age"] == 28
    assert profile["gender"] == "m"
    assert profile["weight"] == 80.0
    assert profile["height"] == 180.0
    assert profile["workout_level"] == 1.55
    assert "dietary_restrictions" in profile


def test_plan_save_returns_none(plan_store: Any) -> None:
    assert plan_store.save({"request": {"user_id": "u1"}}) is None


def test_plans_come_back_newest_first(plan_store: Any) -> None:
    for i in range(3):
        plan_store.save({"request": {"user_id": "u1"}, "n": i})
    items = plan_store.list_for_user("u1")
    assert [item["n"] for item in items] == [2, 1, 0]


def test_plans_respect_the_limit(plan_store: Any) -> None:
    for i in range(5):
        plan_store.save({"request": {"user_id": "u1"}, "n": i})
    assert [item["n"] for item in plan_store.list_for_user("u1", limit=2)] == [4, 3]


def test_plans_are_isolated_per_user(plan_store: Any) -> None:
    plan_store.save({"request": {"user_id": "u1"}, "n": 1})
    plan_store.save({"request": {"user_id": "u2"}, "n": 2})
    assert [item["n"] for item in plan_store.list_for_user("u1")] == [1]
    assert [item["n"] for item in plan_store.list_for_user("u2")] == [2]


def test_plans_for_an_unknown_user_are_empty(plan_store: Any) -> None:
    assert plan_store.list_for_user("nobody") == []


def test_plan_records_carry_saved_at(plan_store: Any) -> None:
    plan_store.save({"request": {"user_id": "u1"}})
    assert "saved_at" in plan_store.list_for_user("u1")[0]


def test_plan_payloads_survive_nesting(plan_store: Any) -> None:
    """History rows are whole API responses; nesting must round-trip."""
    payload = {"request": {"user_id": "u1"}, "meal_plan": {"ingredients": [{"g": 100}]}}
    plan_store.save(payload)
    assert plan_store.list_for_user("u1")[0]["meal_plan"]["ingredients"][0]["g"] == 100


def test_feedback_save_returns_the_record(feedback_store: Any) -> None:
    record = feedback_store.save({"user_id": "u1", "meal_name": "X", "liked": True})
    assert record["meal_name"] == "X"
    assert "saved_at" in record


def test_feedback_comes_back_newest_first(feedback_store: Any) -> None:
    for i in range(3):
        feedback_store.save({"user_id": "u1", "n": i})
    assert [item["n"] for item in feedback_store.list_for_user("u1")] == [2, 1, 0]


def test_feedback_saved_only_filters(feedback_store: Any) -> None:
    feedback_store.save({"user_id": "u1", "n": 0, "saved": False})
    feedback_store.save({"user_id": "u1", "n": 1, "saved": True})
    saved = feedback_store.list_for_user("u1", saved_only=True)
    assert [item["n"] for item in saved] == [1]
    assert all(item["saved"] for item in saved)


def test_feedback_respects_the_limit(feedback_store: Any) -> None:
    for i in range(5):
        feedback_store.save({"user_id": "u1", "n": i})
    assert len(feedback_store.list_for_user("u1", limit=2)) == 2


def test_feedback_is_isolated_per_user(feedback_store: Any) -> None:
    feedback_store.save({"user_id": "u1", "n": 1})
    feedback_store.save({"user_id": "u2", "n": 2})
    assert [item["n"] for item in feedback_store.list_for_user("u1")] == [1]
```

- [ ] **Step 2: Run it**

```bash
uv run pytest backend/tests/test_repository_contract.py -v
```
Expected: the `json` parameterisations **pass**; the `sqlite` ones **skip** with
"SQLite backend not implemented yet (Task 4)". Report the actual pass/skip counts.

If any `json` case fails, that is a real behavioural difference between what the
contract says and what the JSON store does — **report it and stop**, rather than
weakening the assertion to match.

- [ ] **Step 3: Commit**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/tests/test_repository_contract.py
git commit -F - <<'MSG'
test(repositories): add the storage contract suite

One behavioural specification, parameterised over both backends, written before
the SQLite implementation exists so it specifies behaviour rather than describing
whatever SQLite happens to do. Spec section 8's contract-test requirement, landed
early because Task 4 needs something to implement against.

Covers the behaviour that actually matters and is easy to get subtly wrong:
newest-first ordering, limit handling, per-user isolation, the empty case,
saved_at presence, nested-payload round-tripping, saved_only filtering, and the
differing return types of the two save methods.

The sqlite parameterisations skip until the backend exists.

Verified: every json case passes.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 4: The SQLite backend

**Files:**
- Create: `backend/app/repositories/sql/__init__.py`, `backend/app/repositories/sql/models.py`, `backend/app/repositories/sql/repositories.py`

**Interfaces:**
- Consumes: the protocols from Task 2 and the contract suite from Task 3.
- Produces: `build_engine(path: Path) -> Engine` plus `SqlUserProfileRepository`, `SqlMealPlanRepository`, `SqlMealFeedbackRepository`, each taking an `Engine` as its only constructor argument. All are exported from `backend.app.repositories.sql`.

- [ ] **Step 1: Confirm the contract suite currently skips SQLite**

```bash
uv run pytest backend/tests/test_repository_contract.py -v 2>&1 | grep -c SKIPPED
```
Expected: a non-zero count. That is your starting failure state.

- [ ] **Step 2: Write the table models**

Create `backend/app/repositories/sql/models.py`:

```python
"""SQLModel table definitions for the SQLite backend."""

from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class MealPlanRow(SQLModel, table=True):
    """One stored meal-plan response."""

    __tablename__ = "meal_plans"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    saved_at: str
    payload: dict[str, Any] = Field(sa_column=Column(JSON))


class MealFeedbackRow(SQLModel, table=True):
    """One stored feedback record."""

    __tablename__ = "meal_feedback"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    saved: bool = Field(default=False, index=True)
    saved_at: str
    payload: dict[str, Any] = Field(sa_column=Column(JSON))
```

The payload is a JSON column because history rows are whole API responses from
earlier versions of the code; normalising them into typed columns would make old
rows unreadable. `user_id` and `saved` are real indexed columns because they are
what queries filter on.

- [ ] **Step 3: Write the repositories**

Create `backend/app/repositories/sql/repositories.py`:

```python
"""SQLite-backed repository implementations."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine, desc, select

from .models import MealFeedbackRow, MealPlanRow

DEFAULT_PROFILE: dict[str, Any] = {
    "age": 28,
    "gender": "m",
    "weight": 80.0,
    "height": 180.0,
    "workout_level": 1.55,
    "dietary_restrictions": ["dairy-free", "high-protein"],
}


def build_engine(path: Path) -> Engine:
    """Create the SQLite engine and ensure the schema exists.

    Args:
        path: Filesystem location of the database file.

    Returns:
        A ready-to-use SQLAlchemy engine.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _now() -> str:
    """Return the current UTC time in ISO-8601 form."""
    return datetime.now(UTC).isoformat()


class SqlUserProfileRepository:
    """Reads user profiles, falling back to the built-in default."""

    def __init__(self, engine: Engine) -> None:
        """Store the engine.

        Args:
            engine: The SQLite engine.
        """
        self.engine = engine

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        """Return the default profile.

        Profiles are not yet stored in SQL - the JSON backend reads a
        hand-maintained file, and nothing writes profiles at runtime. This
        returns the same default the JSON store falls back to, so the two
        backends behave identically. See docs/4_next_steps.md.

        Args:
            user_id: Accepted for protocol compatibility; unused.

        Returns:
            A copy of the default profile.
        """
        return dict(DEFAULT_PROFILE)


class SqlMealPlanRepository:
    """Stores meal plans in SQLite."""

    def __init__(self, engine: Engine) -> None:
        """Store the engine.

        Args:
            engine: The SQLite engine.
        """
        self.engine = engine

    def save(self, payload: dict[str, Any]) -> None:
        """Append one meal-plan response.

        Args:
            payload: The full API response to store.
        """
        record = {"saved_at": _now(), **payload}
        with Session(self.engine) as session:
            session.add(
                MealPlanRow(
                    user_id=str(payload.get("request", {}).get("user_id", "")),
                    saved_at=record["saved_at"],
                    payload=record,
                )
            )
            session.commit()

    def list_for_user(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return a user's most recent meal plans, newest first.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.

        Returns:
            Up to ``limit`` records, newest first.
        """
        with Session(self.engine) as session:
            rows = session.exec(
                select(MealPlanRow)
                .where(MealPlanRow.user_id == user_id)
                .order_by(desc(MealPlanRow.id))
                .limit(limit)
            ).all()
        return [row.payload for row in rows]


class SqlMealFeedbackRepository:
    """Stores meal feedback in SQLite."""

    def __init__(self, engine: Engine) -> None:
        """Store the engine.

        Args:
            engine: The SQLite engine.
        """
        self.engine = engine

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Append one feedback record.

        Args:
            payload: The feedback to store.

        Returns:
            The stored record, including its ``saved_at`` timestamp.
        """
        record = {"saved_at": _now(), **payload}
        with Session(self.engine) as session:
            session.add(
                MealFeedbackRow(
                    user_id=str(payload.get("user_id", "")),
                    saved=bool(payload.get("saved", False)),
                    saved_at=record["saved_at"],
                    payload=record,
                )
            )
            session.commit()
        return record

    def list_for_user(
        self, user_id: str, limit: int = 20, saved_only: bool = False
    ) -> list[dict[str, Any]]:
        """Return a user's most recent feedback, newest first.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.
            saved_only: Restrict to records flagged as saved.

        Returns:
            Up to ``limit`` records, newest first.
        """
        with Session(self.engine) as session:
            statement = select(MealFeedbackRow).where(MealFeedbackRow.user_id == user_id)
            if saved_only:
                statement = statement.where(MealFeedbackRow.saved is True)
            rows = session.exec(
                statement.order_by(desc(MealFeedbackRow.id)).limit(limit)
            ).all()
        return [row.payload for row in rows]
```

**Watch out:** `statement.where(MealFeedbackRow.saved is True)` is wrong — `is`
is not overloadable, so it evaluates to `False` in Python. Use
`MealFeedbackRow.saved == True  # noqa: E712` or, better,
`col(MealFeedbackRow.saved).is_(True)` imported from `sqlmodel`. **Fix this while
implementing and say in your report which form you used** — the contract test
`test_feedback_saved_only_filters` will catch it if you do not.

- [ ] **Step 4: Export them**

Create `backend/app/repositories/sql/__init__.py`:

```python
"""SQLite repository implementations."""

from .repositories import (
    SqlMealFeedbackRepository,
    SqlMealPlanRepository,
    SqlUserProfileRepository,
    build_engine,
)

__all__ = [
    "SqlMealFeedbackRepository",
    "SqlMealPlanRepository",
    "SqlUserProfileRepository",
    "build_engine",
]
```

- [ ] **Step 5: Run the contract suite against both backends**

```bash
uv run pytest backend/tests/test_repository_contract.py -v
```
Expected: **every case passes for both `json` and `sqlite`, none skipped.** Report
the counts. Any sqlite failure is a real behavioural difference — fix the SQL
implementation to match the contract, never the contract to match SQLite.

- [ ] **Step 6: Confirm the indexes exist**

```bash
uv run python -c "
from pathlib import Path
from sqlalchemy import inspect
from backend.app.repositories.sql import build_engine
import tempfile
with tempfile.TemporaryDirectory() as d:
    e = build_engine(Path(d) / 't.db')
    i = inspect(e)
    for t in ('meal_plans', 'meal_feedback'):
        print(t, '->', [x['name'] for x in i.get_indexes(t)])
"
```
Expected: `ix_meal_plans_user_id`, and both `ix_meal_feedback_user_id` and
`ix_meal_feedback_saved`. Without these, the query is a table scan and the whole
point of the backend is lost.

- [ ] **Step 7: Verify and commit**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/repositories/sql
git commit -F - <<'MSG'
feat(repositories): add the SQLite storage backend

Spec section 7 item 3. Three SQLModel-backed repositories satisfying the same
protocols as the JSON ones, with the contract suite from the previous commit now
running green against both.

Design notes:
- payload is a JSON column, not typed columns. History rows are whole API
  responses from earlier versions of the code; normalising them would make old
  rows unreadable.
- user_id and saved are real indexed columns, because they are what queries
  filter on. Verified: ix_meal_plans_user_id, ix_meal_feedback_user_id and
  ix_meal_feedback_saved all exist. This replaces the JSON store's
  load-everything-then-filter-in-Python.
- ordering is by descending id rather than saved_at, because two records written
  in the same ISO-8601 microsecond would otherwise order arbitrarily.
- SqlUserProfileRepository returns the default profile. Profiles are not stored
  in SQL: nothing writes them at runtime and the JSON backend reads a
  hand-maintained file. Both backends therefore return the same default, which
  the contract suite asserts. Tracked in docs/4_next_steps.md.

Verified: the full contract suite passes against both backends with nothing
skipped.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 5: Wire `STORAGE_BACKEND` in, and prove the API is unchanged

**Files:**
- Create: `backend/app/repositories/factory.py`
- Create: `backend/tests/test_storage_backend_parity.py`
- Create: `scripts/migrate_json_to_sqlite.py`
- Modify: `backend/app/core/container.py`

**Interfaces:**
- Consumes: everything from Tasks 1-4.
- Produces: `build_repositories(settings: AppSettings) -> tuple[UserProfileStore, MealPlanStore, MealFeedbackStore]`.

- [ ] **Step 1: Write the parity test**

Create `backend/tests/test_storage_backend_parity.py`:

```python
"""Switching STORAGE_BACKEND must not change any API response."""

from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import AppSettings
from backend.app.core.container import get_container
from backend.app.main import app
from backend.app.repositories.factory import build_repositories


def _client_for(backend: str, tmp_path: Path) -> TestClient:
    """Build a client whose repositories use the given backend."""
    client = TestClient(app)
    client.__enter__()
    settings = AppSettings(storage_backend=backend)
    profiles, plans, feedback = build_repositories(settings, data_dir=tmp_path)
    isolated = replace(
        app.state.container,
        user_profiles=profiles,
        meal_history=plans,
        meal_feedback=feedback,
    )
    app.dependency_overrides[get_container] = lambda: isolated
    return client


@pytest.mark.parametrize("backend", ["json", "sqlite"])
def test_feedback_roundtrip_is_identical(backend: str, tmp_path: Path) -> None:
    client = _client_for(backend, tmp_path)
    try:
        saved = client.post(
            "/meal-feedback",
            json={
                "user_id": "parity_user",
                "request_id": "abcdefgh",
                "meal_name": "Parity Meal",
                "liked": True,
                "saved": True,
            },
        )
        assert saved.status_code == 200
        listed = client.get("/meal-feedback/parity_user").json()
        assert [item["meal_name"] for item in listed["items"]] == ["Parity Meal"]
        only_saved = client.get("/saved-meals/parity_user").json()
        assert all(item["saved"] for item in only_saved["items"])
        assert len(only_saved["items"]) == 1
    finally:
        app.dependency_overrides.clear()
        client.__exit__(None, None, None)


@pytest.mark.parametrize("backend", ["json", "sqlite"])
def test_meal_plan_history_roundtrip_is_identical(backend: str, tmp_path: Path) -> None:
    client = _client_for(backend, tmp_path)
    try:
        generated = client.post(
            "/generate-meal-plan", json={"user_id": "parity_user", "craving": "pasta"}
        )
        assert generated.status_code == 200
        history = client.get("/meal-plans/parity_user").json()
        assert history["items"], "the generated plan should be listed"
        assert history["items"][0]["request"]["user_id"] == "parity_user"
    finally:
        app.dependency_overrides.clear()
        client.__exit__(None, None, None)
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest backend/tests/test_storage_backend_parity.py`
Expected: FAIL — `No module named 'backend.app.repositories.factory'`.

- [ ] **Step 3: Write the factory**

Create `backend/app/repositories/factory.py`:

```python
"""Selects the storage backend named by settings."""

from pathlib import Path

from ..core.config import AppSettings
from .base import MealFeedbackStore, MealPlanStore, UserProfileStore
from .json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)


def build_repositories(
    settings: AppSettings, data_dir: Path | None = None
) -> tuple[UserProfileStore, MealPlanStore, MealFeedbackStore]:
    """Build the repository trio for the configured backend.

    Args:
        settings: Resolved application settings.
        data_dir: Override for the storage location. Tests pass a temporary
            directory; production leaves it unset and uses ``settings.data_dir``.

    Returns:
        The profile, meal-plan and feedback stores, in that order.
    """
    directory = data_dir or settings.data_dir
    if settings.storage_backend == "json":
        return (
            UserProfileRepository(directory),
            MealPlanRepository(directory),
            MealFeedbackRepository(directory),
        )

    from .sql import (
        SqlMealFeedbackRepository,
        SqlMealPlanRepository,
        SqlUserProfileRepository,
        build_engine,
    )

    engine = build_engine(directory / "ai_meal_planner.db")
    return (
        SqlUserProfileRepository(engine),
        SqlMealPlanRepository(engine),
        SqlMealFeedbackRepository(engine),
    )
```

The `sql` import is inside the branch so the JSON backend never pays SQLAlchemy's
import cost. This is the one permitted function-level import in the codebase, and
it is for cost, not to dodge a cycle — say so in a comment.

- [ ] **Step 4: Use the factory in the container**

In `backend/app/core/container.py`, replace the three direct repository
constructions with:

```python
    user_profiles, meal_history, meal_feedback = build_repositories(settings)
```

and update the `Container` dataclass field annotations from the concrete classes
to the protocols — `user_profiles: UserProfileStore`, `meal_history: MealPlanStore`,
`meal_feedback: MealFeedbackStore` — importing them from `..repositories.base`.
Remove the now-unused concrete imports.

- [ ] **Step 5: Run the parity test**

```bash
uv run pytest backend/tests/test_storage_backend_parity.py -v
```
Expected: all four cases pass. If the `_client_for` helper's settings override
does not work as written, **fix the helper** — `AppSettings` may not accept
`storage_backend` as a constructor argument if the field is aliased. Report what
you had to change.

- [ ] **Step 6: Write the migration script**

There are 44 meal-plan records and 19 feedback records in the existing JSON
stores. Defaulting to SQLite makes them invisible, so provide a one-off import.

Create `scripts/migrate_json_to_sqlite.py`:

```python
"""Import existing JSON store records into the SQLite database.

Run once after switching STORAGE_BACKEND to sqlite:

    uv run python scripts/migrate_json_to_sqlite.py

Idempotency is NOT provided: running it twice imports the records twice. Check
the reported counts before re-running.
"""

import json
import sys
from pathlib import Path

from backend.app.core.config import AppSettings
from backend.app.repositories.sql import (
    SqlMealFeedbackRepository,
    SqlMealPlanRepository,
    build_engine,
)


def _load(path: Path) -> list[dict]:
    """Read a JSON store, returning an empty list when it does not exist."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    """Copy JSON records into SQLite and report the counts."""
    settings = AppSettings.from_env()
    engine = build_engine(settings.sqlite_path)

    plans = _load(settings.data_dir / "meal_history.json")
    feedback = _load(settings.data_dir / "meal_feedback.json")

    plan_repo = SqlMealPlanRepository(engine)
    feedback_repo = SqlMealFeedbackRepository(engine)
    for record in plans:
        plan_repo.save(record)
    for record in feedback:
        feedback_repo.save(record)

    print(f"imported {len(plans)} meal plans and {len(feedback)} feedback records")
    print(f"into {settings.sqlite_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 7: Prove the API behaves identically under both backends, live**

```bash
cp backend/.env.example backend/.env
for backend in json sqlite; do
  echo "=== $backend ==="
  STORAGE_BACKEND=$backend uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 >/tmp/srv_$backend.log 2>&1 &
  sleep 9
  curl -s -X POST http://127.0.0.1:8000/generate-meal-plan -H 'Content-Type: application/json' \
    -d '{"user_id":"live_parity","craving":"pasta"}' \
    | uv run python -c "import json,sys; d=json.load(sys.stdin); print('sections:', sorted(d)); print('target:', d['meal_plan']['user_context']['caloric_target'])"
  curl -s http://127.0.0.1:8000/meal-plans/live_parity \
    | uv run python -c "import json,sys; print('history items:', len(json.load(sys.stdin)['items']))"
  pkill -f "uvicorn backend.app.main:app"; sleep 2
done
lsof -i :8000 || echo "port 8000 free"
```

Expected: identical `sections` and `target` under both, and `history items: 1`
under both. **Report both outputs side by side.**

This run creates `database/ai_meal_planner.db`, which is **not** currently ignored.
Add exactly this line to `.gitignore`, beside the existing `database/*.json` entries:

```gitignore
database/*.db
```

Then confirm with `git check-ignore -v database/ai_meal_planner.db` and
`git status --short`. **Change nothing else in `.gitignore`** — its model-artifact
negation block must stay exactly as it is.

- [ ] **Step 8: Verify and commit**

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/repositories/factory.py backend/app/core/container.py backend/tests/test_storage_backend_parity.py scripts/migrate_json_to_sqlite.py
git commit -F - <<'MSG'
feat(repositories): select the storage backend from settings

Spec section 7's "done when": switching STORAGE_BACKEND changes no API behaviour.

build_repositories(settings) returns the trio for the configured backend, and the
container now depends on the protocols rather than the concrete JSON classes. The
sql import sits inside its branch so the JSON backend never pays SQLAlchemy's
import cost - the one function-level import in the codebase, and for cost rather
than to dodge a cycle.

Adds a parity suite that runs the feedback and meal-plan round trips through the
real API under both backends and asserts identical responses, plus a live check
against a running server under each.

scripts/migrate_json_to_sqlite.py imports the existing 44 meal-plan and 19
feedback records, which defaulting to SQLite would otherwise make invisible. It
is deliberately not idempotent and says so.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 6: Close the two carried Phase 1 findings

**Files:**
- Modify: `backend/app/services/meal_planning_service.py`
- Modify: `docs/4_next_steps.md`

**Interfaces:**
- Consumes: `UserProfileStore` from Task 2.

Phase 1's final review carried two Minors that belong here, because both are about
the profile repository.

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_meal_planning_service.py`:

```python
def test_the_profile_is_read_once_per_request() -> None:
    """Two full file reads per request was a Phase 1 finding."""
    service = _service()
    calls: list[str] = []
    original = service.profile_repo.fetch_user_profile

    def _counted(user_id: str) -> dict:
        calls.append(user_id)
        return original(user_id)

    service.profile_repo.fetch_user_profile = _counted  # type: ignore[method-assign]
    service.meal_agent.db = service.profile_repo
    service.generate(MealRequest(craving="pasta"))
    assert len(calls) == 1, f"profile fetched {len(calls)} times"
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest backend/tests/test_meal_planning_service.py::test_the_profile_is_read_once_per_request`
Expected: FAIL — `profile fetched 2 times`.

- [ ] **Step 3: Fetch once and pass it down**

In `backend/app/services/meal_planning_service.py`:

1. Change the constructor annotation `profile_repo: Any` to `profile_repo: UserProfileStore`, importing it from `..repositories.base`. Remove the `Any` import if it becomes unused.
2. In `generate`, fetch the profile once and pass it to both consumers. Change `_calorie_request(self, request)` to `_calorie_request(self, request, profile)` and have `generate` do:

```python
        profile = self.profile_repo.fetch_user_profile(request.user_id.strip())
        calorie_budget = self.calorie_agent.predict(self._calorie_request(request, profile))
```

3. Add an optional `profile` parameter to `MealRecommendationAgent.generate_meal_payload`:

```python
        profile: dict[str, Any] | None = None,
```
documented as "Pre-fetched profile; looked up when omitted", and inside it:
```python
        user_biometrics = profile if profile is not None else self.db.fetch_user_profile(user_id)
```
Then pass `profile=profile` from the service. **Grep the whole repo for other
`generate_meal_payload` callers** — the parameter is optional, so they keep
working, but confirm rather than assume.

- [ ] **Step 4: Verify**

```bash
uv run pytest
```
Expected: all pass, including the new single-read test. Report the count.

- [ ] **Step 5: Record what Phase 2 did not do**

In `docs/4_next_steps.md`, add these to the acknowledged-gaps section, keeping
Alembic first:

- **Alembic migrations** — Phase 2 ships `create_all`, which cannot alter an existing table. Any future column change needs a migration tool.
- **Profiles are not stored in SQL.** Both backends return the same built-in default; nothing writes profiles at runtime. Real profile storage needs a write path and an endpoint, neither of which exists.
- **The typed domain exceptions are still never raised.** `ProfileNotFound`, `RetrievalUnavailable` and `NutritionProviderError` are defined and wired to handlers but no production code raises them, so every failure still lands on the catch-all 500. Carried from Phase 1's final review.
- **`deviation_after` falls back to `deviation_before`** when a reconciliation retry verifies to 0 kcal, understating the miss. `within_tolerance` stays correct.
- **The 0.65/1.6 clamp and 5 g rounding are duplicated** between `_reconcile` and `MealRecommendationAgent._scale_ingredients_to_meal_target`.
- **`backend/app/ml/` is an empty package.** Spec §6 item 10 said to use or remove it; neither happened.

- [ ] **Step 6: Commit**

```bash
uv run ruff check . && uv run ruff format --check .
git status --short
git add backend/app/services/meal_planning_service.py backend/app/agents/meal_recommendation_agent.py backend/tests/test_meal_planning_service.py docs/4_next_steps.md
git commit -F - <<'MSG'
perf(services): read the user profile once per request

Phase 1's final review found the profile was fetched twice per
/generate-meal-plan - once in the service to build the calorie request, once in
the meal agent - each a full json.load with no caching.

The service now fetches once and passes the profile down;
generate_meal_payload takes an optional profile and looks it up only when
omitted, so its other callers are unaffected. profile_repo is typed as the
UserProfileStore protocol rather than Any, closing the second carried finding.

A test counts the fetches and asserts exactly one.

docs/4_next_steps.md records the six gaps Phase 2 knowingly leaves open, Alembic
first, including that the typed exceptions are still never raised.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Phase 2 Exit Gate

Per spec §7: done when both backends pass the same contract test suite, and
switching `STORAGE_BACKEND` changes no API behaviour.

- [ ] `uv run pytest` → all green, no test deleted, skipped or weakened. Report the real count.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` → clean
- [ ] `uv run pytest backend/tests/test_repository_contract.py -v` → every case passes for **both** `json` and `sqlite`, **none skipped**
- [ ] `uv lock --check` passes and `uv export ... && git diff --exit-code -- backend/requirements.txt` is clean
- [ ] `scikit-learn` still exactly `1.6.1` and `pydantic` still 2.x in `uv.lock`
- [ ] Indexes exist: `ix_meal_plans_user_id`, `ix_meal_feedback_user_id`, `ix_meal_feedback_saved`
- [ ] A live server under `STORAGE_BACKEND=json` and under `=sqlite` returns identical response sections and the same history behaviour
- [ ] `AppSettings` resolves every value identically to the pre-migration snapshot
- [ ] A malformed `STORAGE_BACKEND` raises at startup rather than silently choosing
- [ ] `git status --short` clean; no `.env`, `database/*.json` or `database/*.db` staged
- [ ] `.gitignore` gained exactly one line, `database/*.db`; `git diff` on it shows nothing else
- [ ] `docs/4_next_steps.md` lists the six gaps, Alembic first
- [ ] Append a Phase 2 entry to `docs/5_agent_log.md`; tick this checklist

Then write the Phase 3 plan from spec §8.
