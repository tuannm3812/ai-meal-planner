# Phase 0 — Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repository runnable in one command, self-enforcing of the master coding standard, and gated by CI — before any refactor touches application logic.

**Architecture:** No application behaviour changes in this phase. Work is confined to dependency management (`uv` as the single source of truth), lint/format compliance, CI gates, documentation reshaping to Shape B, and the two agent-instruction files. The one structural change is packaging `backend` with hatchling so `from backend.app...` resolves without path hacks — a prerequisite for Phase 1's DI refactor and Phase 4's in-process Streamlit import.

**Tech Stack:** Python 3.11/3.12, uv 0.11.29, hatchling, ruff 0.16.4, pytest, GitHub Actions, Node 20 + npm, Vite, ESLint.

**Spec:** `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md` §5

## Global Constraints

- `requires-python = ">=3.11,<3.13"` — do not widen; `scikit-learn==1.6.1` is pinned against the shipped model artifact.
- `scikit-learn==1.6.1` stays exactly pinned. Changing it invalidates `models/calorie_expenditure/calorie_expenditure_model.joblib` and will trip `test_calorie_model_artifact_loads_and_predicts`.
- Ruff config: `line-length = 100`, `target-version = "py311"`, `select = ["E", "F", "I", "B", "UP"]`.
- uv pinned to `0.11.29` in CI — `uv export` output is deterministic per uv version, so an unpinned version would make the requirements-drift check fail on version skew.
- **Do not modify `.gitignore`.** It already implements the §8 blanket-rule-plus-negation pattern for the model artifact, and the master standard cites this repo as a correct example.
- **Baseline to preserve: 19 passing tests.** Every task must end with `uv run pytest` reporting 19 passed. No test may be deleted, skipped, or weakened in this phase.
- Commit messages follow §9: `<type>(<scope>): <imperative summary>`, one coherent
  change per commit, material detail in the body. **The `(scope)` is mandatory.**
  If a task's pre-written commit message in this plan omits it, the pre-written text
  is wrong and this constraint governs — add a scope. Every commit body ends with
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- Root `requirements.txt` stays the one-line `-r backend/requirements.txt`. Only `backend/requirements.txt` is generated.
- API port is **8000** everywhere after Task 6.
- **Never `git add -A`.** Master standard §10.1 requires reviewing every path
  before staging. Run `git status --short` first, then stage explicitly — `git add -u`
  for tracked-only modifications, or named paths. This ruling overrides any
  `git add -A` that survives elsewhere in this plan.
- All work lands on the branch `refactor/phase-0-foundation`, never on `main`.
- **Run `uv run pytest`, never `uv run pytest -q`.** `pyproject.toml` sets
  `addopts = "-q"`, so an explicit `-q` stacks into pytest's `-qq` mode and
  suppresses the `19 passed` summary line entirely — leaving you unable to verify
  the count, and any CI grep for `passed` matching nothing. Confirmed by running
  both forms on 2026-09-10.

---

## Verified Starting State

Measured on 2026-09-10 at commit `aedcea0`, macOS, Python 3.11:

| Check | Result |
| --- | --- |
| `uv run pytest` | **19 passed** (13 test functions; parametrization expands them) |
| `ruff check .` | **94 errors** — 48 `UP006`, 22 `E501`, 14 `I001`, 9 `UP035`, 1 `F401`. 63 auto-fixable |
| `ruff format --check .` | **10 files would be reformatted**, 34 already formatted |
| `npm run lint` | **clean** |
| `npm run build` | **succeeds** (252 kB JS, 12.5 kB CSS) |
| Ruff errors in `notebooks/` | 7 — 1 `F401` plus 6 `E501` |
| Available tooling | uv 0.11.29, node v24.18.0, npm 11.16.0 |
| `python` on PATH | **absent** — only `python3` (3.9, too old for `X \| None` at `rag/rules.py:10`) |

The missing `python` is why the README's documented setup cannot run on macOS as written, and why Task 1 comes first.

## File Structure

**Created:**

| File | Responsibility |
| --- | --- |
| `uv.lock` | Resolved dependency graph; single source of truth for both requirements exports |
| `AGENTS.md` | §13 layer 2 — repo identity, deltas, evidence locations, open risks |
| `CLAUDE.md` | One line: `@AGENTS.md`. Exists so Claude Code and Codex read the same source |
| `docs/0_coding_standards.md` | Project-specific rules and declared deltas only |
| `docs/1_brief.md` | What is being built, for whom, what done looks like |
| `docs/2_architecture.md` | Components, data flow, contracts, target structure |
| `docs/3_decisions.md` | Dated decision log, seeded with DEC-1..DEC-6 |
| `docs/4_next_steps.md` | Prioritised remaining work, including out-of-scope items |
| `docs/5_agent_log.md` | Append-only record of agent work |
| `frontend/.env.example` | Documents `VITE_API_URL` |

**Modified:** `pyproject.toml`, `backend/requirements.txt` (becomes generated), `.github/workflows/ci.yml`, `README.md`, `frontend/src/App.jsx` (port strings only), `backend/.env.example`, and every `.py` file touched by the ruff autofix.

**Moved:** `docs/product/backend_first_roadmap.md` → `docs/1_brief.md`; `docs/architecture/system_architecture.md` → `docs/2_architecture.md`; `docs/engineering/repo_structure_conventions.md` → split between `docs/0_coding_standards.md` and `docs/2_architecture.md`.

**Deleted:** `docs/engineering/coding_standards.md` (master-duplicating), `docs/product/react_frontend.md` (superseded — React is built).

**Retained unchanged:** `docs/agents/` (4 files, so §2's two-file rule justifies the subfolder), `docs/architecture/vector_rag.md` and `docs/architecture/ai_meal_planner_architecture.excalidraw` (2 files, subfolder justified).

---

## Task 1: uv-managed dependencies and an importable backend package

**Files:**
- Modify: `pyproject.toml`
- Modify: `backend/requirements.txt` (becomes generated output)
- Create: `uv.lock`

**Interfaces:**
- Produces: a working `uv sync --all-groups` / `uv run pytest` workflow that every later task and phase depends on; an importable `backend` package; the exact `uv export` command the CI drift check in Task 3 reruns.

- [ ] **Step 1: Record the baseline before changing anything**

```bash
uv venv --python 3.11
uv pip install -r backend/requirements.txt
uv run --no-project python -m pytest
```

Expected: `19 passed`. Write the number down — it is the invariant for every later step.

- [ ] **Step 2: Rewrite `pyproject.toml`**

Replace the whole file with this. It removes both dead `[tool.poetry]` blocks, adds a build backend so `backend` becomes importable, moves `pytest` out of the runtime set into a dev group, adds `ruff`, and adds the notebook `E501` carve-out that master §3 already permits for "notebook display/print calls where wrapping hurts readability".

```toml
[project]
name = "ai-meal-planner"
version = "0.1.0"
description = "Backend-first AI meal planner with calorie prediction and local meal RAG."
readme = "README.md"
requires-python = ">=3.11,<3.13"
dependencies = [
  "fastapi",
  "google-genai",
  "joblib>=1.4,<2",
  "numpy>=1.26,<3",
  "pandas>=2.2,<3",
  "pydantic",
  "python-dotenv",
  "requests",
  "scikit-learn==1.6.1",
  "streamlit",
  "uvicorn",
]

[project.optional-dependencies]
semantic-rag = [
  "faiss-cpu>=1.8,<2",
  "sentence-transformers>=3,<4",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["backend"]

[dependency-groups]
dev = [
  "pytest>=8",
  "ruff==0.16.4",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
ignore = []

[tool.ruff.lint.per-file-ignores]
"*.ipynb" = ["E501"]

[tool.pytest.ini_options]
testpaths = ["backend/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-q"
```

Note: `streamlit` stays a runtime dependency — Streamlit Cloud installs from the exported requirements and `streamlit_app/app.py` needs it. `ruff` is pinned exactly so local and CI results cannot disagree.

- [ ] **Step 3: Lock and sync**

```bash
rm -rf .venv
uv lock
uv sync --all-groups
```

Expected: `uv.lock` created; sync installs the dependency set plus `ai-meal-planner` itself as an editable/local package.

- [ ] **Step 4: Verify the backend is now importable without path hacks**

```bash
uv run python -c "import backend.app.rag.rules as r; print(r.normalize_label('High Protein'))"
```

Expected: `high protein`. This proves the `from backend.app...` import path resolves from a clean interpreter — the precondition for deleting the dual-import block in Phase 1.

- [ ] **Step 5: Verify the test baseline is unchanged**

```bash
uv run pytest
```

Expected: `19 passed`. If the count differs, stop and investigate before continuing — do not proceed with a changed baseline.

- [ ] **Step 6: Regenerate `backend/requirements.txt` from the lock**

```bash
uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt
```

Then confirm the root file is still the one-line include and that Render's and Streamlit Cloud's install paths both remain valid:

```bash
cat requirements.txt
```

Expected: `-r backend/requirements.txt` — leave it exactly as is.

The generated `backend/requirements.txt` opens with a header uv writes itself:

```text
# This file was autogenerated by uv via the following command:
#    uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt
```

Leave that header in place — it tells the next reader the file is generated and
exactly how to regenerate it. Verified: this command was run end to end against a
scratch project on 2026-09-10 and produced a `pytest`-free export.

- [ ] **Step 7: Confirm `pytest` is no longer in the runtime export**

```bash
grep -c "^pytest" backend/requirements.txt
```

Expected: `0`. `pytest` belongs to the dev group now and must not ship to Render or Streamlit Cloud.

- [ ] **Step 8: Confirm the export is reproducible**

Run the same export a second time and check nothing changed. The CI drift job in Task 3 depends on this being byte-stable.

```bash
uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt
git diff --stat -- backend/requirements.txt
```

Expected: no diff on the second run beyond what Step 6 already produced.

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml uv.lock backend/requirements.txt
git commit -F - <<'MSG'
build(deps): consolidate dependencies under uv with a committed lockfile

Dependencies were declared three times - root requirements.txt,
backend/requirements.txt, [project].dependencies and a [tool.poetry] block -
with no lockfile and mostly unpinned versions.

pyproject.toml is now the only hand-edited source:
- both dead [tool.poetry] blocks removed
- pytest moved out of the runtime set into a dev group; ruff pinned to 0.16.4
- hatchling added as build backend with packages = ["backend"], so
  from backend.app... resolves without the dual-import block in main.py
- notebooks carve out E501 only, which master standard section 3 already
  permits for notebook display and print calls

backend/requirements.txt is now generated by uv export and must not be hand
edited; root requirements.txt stays the one-line include that Streamlit Cloud
reads. Render's buildCommand and the Streamlit Cloud install path are both
unchanged.

Verified: uv sync --all-groups succeeds, backend.app imports from a clean
interpreter, uv run pytest reports 19 passed (unchanged baseline), and the
export is byte-stable across two runs.
MSG
```

---

## Task 2: Bring the codebase to zero ruff findings

**Files:**
- Modify: `backend/app/**/*.py`, `backend/main.py`, `backend/tests/*.py`, `streamlit_app/app.py`, `notebooks/calorie_expenditure_kaggle_training.ipynb`

**Interfaces:**
- Consumes: the `uv run ruff` entry point and ruff config from Task 1.
- Produces: a clean lint baseline, without which the CI gate in Task 3 cannot be added.

This is a large mechanical diff (48 `UP006` alone). It is deliberately its own commit so a reviewer can see it is mechanical and separate from any behavioural change.

- [ ] **Step 1: Confirm the failure state**

```bash
uv run ruff check . 2>&1 | tail -3
```

Expected: `Found 94 errors.` / `[*] 63 fixable with the --fix option.`

- [ ] **Step 2: Apply the safe autofixes**

```bash
uv run ruff check . --fix
```

This resolves `UP006` (`typing.Dict`/`List` → `dict`/`list`), `UP035` (deprecated `typing` imports), `I001` (import ordering) and the single `F401` unused `RandomForestRegressor` import in the notebook.

- [ ] **Step 3: Verify the baseline survived the autofix**

```bash
uv run pytest
```

Expected: `19 passed`. `UP006` rewrites type annotations only, so behaviour must be identical. If any test fails, revert with `git checkout -- .` and fix the offending file by hand.

- [ ] **Step 4: Apply formatting**

```bash
uv run ruff format .
```

Expected: `10 files reformatted, 34 files left unchanged`. This also wraps most of the 22 `E501` long lines.

- [ ] **Step 5: Verify the baseline again**

```bash
uv run pytest
```

Expected: `19 passed`.

- [ ] **Step 6: Resolve any remaining findings by hand**

```bash
uv run ruff check . --output-format concise
```

Expected: no output. Any survivor is a long line that the formatter could not split — typically a long string literal. Fix by extracting the string to a module-level constant or splitting it across implicit-concatenation lines. **Do not add `# noqa`** and do not raise `line-length`; both hide the finding rather than fixing it.

- [ ] **Step 7: Verify both gates are clean and the baseline holds**

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest
```

Expected: no lint output, `50 files already formatted` (or similar with zero to reformat), `19 passed`.

- [ ] **Step 8: Review every path, then stage only tracked modifications**

Per master standard §10.1, review the paths before staging — never blind
`git add -A`. Ruff modifies existing tracked files only, so `-u` is both
sufficient and safer than `-A`:

```bash
git status --short
```

Expected: only ` M` entries, no `??` untracked entries. If anything untracked
appears, stop and investigate — ruff should not have created files.

```bash
git add -u
git diff --cached --stat
```

- [ ] **Step 9: Commit**

```bash
git commit -F - <<'MSG'
style(lint): resolve all ruff findings and apply ruff format

Ruff was configured in pyproject.toml but had never been run in CI, leaving
94 findings: 48 UP006, 22 E501, 14 I001, 9 UP035 and 1 F401. Ten files were
also unformatted.

Applied ruff check --fix then ruff format. The UP006/UP035 fixes replace
typing.Dict and typing.List with the builtin generics, which is annotation-only
and matches the master standard's typing guidance. The F401 removed an unused
sklearn import from the training notebook.

No behavioural change. Verified: ruff check and ruff format --check both
clean, uv run pytest reports 19 passed - unchanged from the pre-change
baseline.

Mechanical change, kept in its own commit so it stays separable from the
architecture work in Phase 1.
MSG
```

---

## Task 3: Add CI gates

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `uv.lock` and the `uv export` command from Task 1; the clean lint state from Task 2.
- Produces: the gates that protect every subsequent task and phase.

- [ ] **Step 1: Confirm the current major version of `astral-sh/setup-uv`**

The workflow below pins `astral-sh/setup-uv@v5`. That major was **not verified** —
this plan was written without network access to check it. Confirm the current major
at `https://github.com/astral-sh/setup-uv` (or via
`gh api repos/astral-sh/setup-uv/releases/latest --jq .tag_name`) and use it in the
workflow. Pinning a stale major will fail the workflow at the install step with an
unresolvable-action error. Everything else in the file is version independent.

- [ ] **Step 2: Replace `.github/workflows/ci.yml` entirely**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          version: "0.11.29"
          enable-cache: true

      - name: Sync dependencies
        run: uv sync --all-groups --python ${{ matrix.python-version }}

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Run tests
        run: uv run pytest

  requirements-drift:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          version: "0.11.29"

      - name: Regenerate backend requirements from the lockfile
        run: >-
          uv export --no-dev --no-hashes --no-emit-project
          --format requirements.txt -o backend/requirements.txt

      - name: Fail if the committed export has drifted
        run: git diff --exit-code -- backend/requirements.txt

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Build
        run: npm run build
```

The `compileall` step is dropped — `ruff check` and `pytest` both subsume it.

- [ ] **Step 3: Reproduce every gate locally before pushing**

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest
uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt && git diff --exit-code -- backend/requirements.txt
(cd frontend && npm ci && npm run lint && npm run build)
```

Expected: all succeed; the `git diff --exit-code` produces no output and exit code 0.

- [ ] **Step 4: Verify the lint gate actually fails on a bad change**

A gate that has never failed is not known to work. Introduce a deliberate violation:

```bash
printf '\nimport os\n' >> backend/app/rag/rules.py
uv run ruff check backend/app/rag/rules.py
```

Expected: FAIL with `F401 [*] \`os\` imported but unused`.

- [ ] **Step 5: Revert the deliberate violation**

```bash
git checkout -- backend/app/rag/rules.py
uv run ruff check . 
```

Expected: no output.

- [ ] **Step 6: Verify the drift gate actually fails**

```bash
printf 'somepackage==1.0.0\n' >> backend/requirements.txt
git diff --exit-code -- backend/requirements.txt
```

Expected: FAIL (exit code 1) with the added line shown — proving the drift check would catch a hand-edited export.

- [ ] **Step 7: Revert the deliberate drift**

```bash
git checkout -- backend/requirements.txt
git diff --exit-code -- backend/requirements.txt
```

Expected: no output, exit code 0.

- [ ] **Step 8: Commit**

```bash
git add .github/workflows/ci.yml
git commit -F - <<'MSG'
ci(workflows): gate on ruff, both Python versions, drift and the frontend

CI previously ran compileall plus pytest on Python 3.11 only. Ruff was
configured and never executed; the frontend lint and build scripts existed
and never ran.

Adds three jobs:
- backend: uv sync, ruff check, ruff format --check and pytest across a
  3.11/3.12 matrix, matching requires-python
- requirements-drift: regenerates backend/requirements.txt from uv.lock and
  fails on any diff, so the generated export cannot be hand edited
- frontend: npm ci, npm run lint, npm run build

uv is pinned to 0.11.29 because uv export output is deterministic per uv
version; an unpinned version would fail the drift check on version skew.
compileall dropped as ruff and pytest subsume it.

Verified: all gates reproduced locally and pass. The lint gate was confirmed
to fail on a deliberately added unused import, and the drift gate on a
deliberately hand-edited requirements line; both reverted.
MSG
```

---

## Task 4: Reshape docs to Shape B

**Files:**
- Create: `docs/0_coding_standards.md`, `docs/1_brief.md`, `docs/2_architecture.md`, `docs/3_decisions.md`, `docs/4_next_steps.md`, `docs/5_agent_log.md`
- Delete: `docs/engineering/coding_standards.md`, `docs/engineering/repo_structure_conventions.md`, `docs/product/backend_first_roadmap.md`, `docs/product/react_frontend.md`, `docs/architecture/system_architecture.md`
- Modify: `README.md` (§5 structure block and the doc links in §5/§10)

**Interfaces:**
- Produces: `docs/0_coding_standards.md`, which `AGENTS.md` imports in Task 5. That file must exist before Task 5.

Per DEC-5 this is **one atomic commit** — every doc path changes at once, so splitting it would leave the README pointing at moved files.

- [ ] **Step 1: Move the files that carry forward, preserving history**

```bash
git mv docs/product/backend_first_roadmap.md docs/1_brief.md
git mv docs/architecture/system_architecture.md docs/2_architecture.md
git mv docs/engineering/repo_structure_conventions.md docs/0_coding_standards.md
git rm docs/engineering/coding_standards.md docs/product/react_frontend.md
```

`docs/engineering/coding_standards.md` is deleted outright: its PEP 8 and typing content duplicates the master standard (forbidden by §13), its "Model Context Protocol (MCP) tools" claim is false, and its `train_df`/`log_reg_clf` rules are notebook conventions that do not apply to a FastAPI service. `docs/product/react_frontend.md` is deleted as superseded — it plans a React frontend that now exists, and its only live detail is a stale `localhost:8000/generate-meal-plan` reference.

- [ ] **Step 2: Rewrite `docs/0_coding_standards.md`**

Keep, verbatim from the moved file, these sections — they are genuinely project-specific and are exactly what layer 3 is for: **Naming**, **API Conventions**, **Data & Model Conventions**, **Testing Conventions**, **Streamlit Convention**.

Delete from it the **Target Structure** and **Current-to-Target Migration** sections; those move to `2_architecture.md` (Step 4) and `4_next_steps.md` (Step 6) respectively.

Then prepend this header and deltas section:

```markdown
# Project Coding Standards — ai-meal-planner

The shared baseline is the master standard at
`~/Documents/GitHub/coding-standards/coding_standards.md`. This file records
**only** what is specific to this project or deliberately different. Per master
§13 it must never restate the master; if a rule here also appears there, delete
it here.

## 1. Doc shape

This repo uses **Shape B** (app/product), per master §2: `0_coding_standards.md`,
`1_brief.md`, `2_architecture.md`, `3_decisions.md`, `4_next_steps.md`, then
numbered by need. Its centre of gravity is a service and two clients, not a
modelling workflow — the one trained model is a single promoted artifact, not the
subject of the repo.

## 2. Deltas from the master

- **`line-length = 100`, not 79.** FastAPI and Pydantic signatures with typed
  keyword arguments do not fit 79 characters without wrapping that hurts
  readability. Enforced by `ruff format`, so it is a ceiling and not a target.
- **Not notebook-first.** Master §1 defaults to a notebook-first layout. This is a
  service: `backend/` is the executable source of truth and `notebooks/` holds one
  training notebook that produced the shipped model artifact.
- **`data/` and `models/` exist deliberately.** Master §1 says to avoid them absent
  a real local-execution need; this project serves a model at runtime.
  `backend/app/core/config.py` loads
  `models/calorie_expenditure/calorie_expenditure_model.joblib` as its default path
  and `test_calorie_model_artifact_loads_and_predicts` asserts against it. The
  `.gitignore` uses the master §8 blanket-rule-plus-negation pattern so the
  exception is visible rather than accidental. Do not "tidy" this.
- **Notebooks ignore `E501` only.** Set in `[tool.ruff.lint.per-file-ignores]`,
  using the slack master §3 already grants notebook display and print calls. Every
  other rule still applies to notebooks.
- **`scikit-learn` is pinned exactly to `1.6.1`.** The shipped model artifact was
  trained under it; unpinning silently risks load-time incompatibility warnings and
  changed predictions.
```

- [ ] **Step 3: Rewrite `docs/1_brief.md`**

The moved `backend_first_roadmap.md` already answers "what is being built and for whom" through its Product Direction, Agent Responsibilities and MVP Scope sections. Retitle it `# Project Brief — ai-meal-planner` and make three edits:

1. Move its **Later Scope** section out to `4_next_steps.md` (Step 6) and delete it here.
2. Add a **Positioning** section directly after Product Direction, stating: self-directed portfolio project first, with an intended path to real users; no rubric or external marking criteria apply.
3. Add a **What done looks like** section listing the MVP exit criteria, drawn from its existing MVP Scope bullets, phrased as checkable statements.

Keep its **Workflow** numbered list verbatim — Phase 1 implements steps 2, 5 and 6 of it, so it is the contract being built against.

- [ ] **Step 4: Rewrite `docs/2_architecture.md`**

The moved `system_architecture.md` keeps its High-Level Overview, Technology Stack, Multi-Agent Orchestration and Data Flow Protocol sections. Add:

1. The **Target Structure** tree removed from `0_coding_standards.md` in Step 2, as a new "Package layout" section.
2. A **Detail references** section linking the retained subfolder docs with relative paths:
   - `docs/agents/calorie_expenditure_agent.md`
   - `docs/agents/meal_recommendation_agent.md`
   - `docs/agents/nutrition_verification_agent.md`
   - `docs/agents/supermarket_agent.md`
   - `docs/architecture/vector_rag.md`
   - `docs/architecture/ai_meal_planner_architecture.excalidraw`
3. A dated **Known divergence** note stating that as of 2026-09-10 the orchestrator described in §3 does not exist, and Data Flow Protocol steps 3, 6 and 8 are unimplemented — pointing at `4_next_steps.md` and the Phase 1 plan. This keeps the document honest about describing a target rather than the current build.

- [ ] **Step 5: Create `docs/3_decisions.md`**

```markdown
# Decision Log

Dated, append-only. Each entry records what was chosen and what it ruled out.
Correct an entry by adding a new one, never by rewriting it.

## 2026-09-10 — Refactor and standards alignment

Source: `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md`

### DEC-1 — Portfolio-first, built for a later transition to real users

Chosen so no work is thrown away when the project takes real users. Ruled out
both shortcuts that assume it stays a demo, and full production hardening
(auth, managed Postgres) that no current user justifies.

### DEC-2 — Streamlit demo mode imports the real backend in-process

`streamlit_app/app.py` reimplemented meal selection, macros and pricing in
`local_demo_request` — a second source of truth. Demo mode will instead build the
real agents through the shared factory the DI container uses. Ruled out deleting
demo mode (the deployed demo would need a live backend, and Render's free tier
cold-starts) and dropping Streamlit entirely (loses the zero-setup demo link).

### DEC-3 — Foundation-first sequencing, with the calorie wiring pulled forward

Phase 0 lands tooling, CI and standards before any refactor, so later phases are
gated and verifiable. The one exception: wiring `CalorieExpenditureAgent` into
meal planning is the first task of Phase 1 rather than buried mid-phase, because
a trained model that is never used is a story-level flaw, not a style one. Ruled
out correctness-first (refactors would land before CI gates existed) and
vertical slices (fragments the cross-cutting dependency and CI work).

### DEC-4 — Repository Protocol plus a SQLite implementation

Gives real SQL and indexed queries with zero infra to run, and makes Postgres
later a config change plus one class. JSON implementations are retained for demo
mode. Ruled out staying on JSON (leaves the portfolio story at "file-backed
prototype") and going straight to Postgres (adds infra to every dev setup and to
CI for a project with no users).

### DEC-5 — Docs reshaped to Shape B in one atomic commit

Master §2 forbids renumbering existing repos except those "being substantially
reworked anyway", which this refactor is. Done in a single commit because every
doc path changes at once and a split would leave the README pointing at moved
files.

### DEC-6 — Both requirements files become generated artifacts

`pyproject.toml` plus `uv.lock` is the single source. Neither requirements file
can be deleted: Streamlit Cloud reads the root one and Render's `buildCommand`
reads `backend/requirements.txt`. The root file stays a one-line `-r` include;
only the backend file is exported, and CI fails on drift.
```

- [ ] **Step 6: Create `docs/4_next_steps.md`**

Assemble from four existing sources plus the deferred items, ordered by priority, each with a one-line rationale:

1. The **Phase 1–4 summaries** from spec §6–§9, each linking the spec section.
2. The **Later Scope** list moved out of `1_brief.md` in Step 3.
3. The **Current-to-Target Migration** numbered list moved out of `0_coding_standards.md` in Step 2, with items already completed marked as done.
4. The README §11 roadmap bullets.
5. The spec §12 out-of-scope items, recorded as acknowledged gaps rather than omissions — **Alembic migrations** first among them, since Phase 2 ships `create_all` with no migration path.

Deduplicate where these overlap; several roadmap and migration items say the same thing.

- [ ] **Step 7: Create `docs/5_agent_log.md`**

```markdown
# Agent Collaboration Log

Append-only, per master §13. Append after meaningful work: what changed, what was
verified, what is still open. Correct a past entry by adding a new one — never by
rewriting it. Findings that did not hold up are recorded alongside those that did.

## 2026-09-10 — Claude Opus 5 — refactor scoping and Phase 0

**Scope reviewed:** whole repository at `d9ce89e`, audited against the master
standard at `~/Documents/GitHub/coding-standards/`.

**Produced:** `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md`
and `docs/superpowers/plans/2026-09-10-phase-0-foundation.md`.

**Verified by running, not asserted:** baseline `uv run pytest` = 19 passed on
Python 3.11; `ruff check .` = 94 findings (48 UP006, 22 E501, 14 I001, 9 UP035,
1 F401); `ruff format --check` = 10 files would be reformatted; `npm run lint`
clean; `npm run build` succeeds. All spec line citations were checked against the
working tree.

**Corrected during review:** five line references in the first draft of the spec
were wrong (`calculate_bmr` is at `meal_recommendation_agent.py:120`, not 113;
the bare `except` is at `main.py:175`, not 170) and were fixed before commit. The
test count was first reported as 13 from a `grep` of `def test`; the real figure
is 19 because of parametrization.

**Open:** Phases 1–4 unplanned. `docs/2_architecture.md` describes an orchestrator
that does not exist yet — the divergence note added in this phase must be removed
when Phase 1 lands it.
```

- [ ] **Step 8: Update README references**

Update the `docs/` portion of the §5 Project Structure tree to the new Shape B layout, and repoint the §5 closing sentence, which currently reads "See `docs/architecture/system_architecture.md` and `docs/engineering/repo_structure_conventions.md` for deeper design notes", to `docs/2_architecture.md` and `docs/0_coding_standards.md`.

- [ ] **Step 9: Verify no dangling links remain**

```bash
grep -rn "engineering/coding_standards\|engineering/repo_structure_conventions\|product/backend_first_roadmap\|product/react_frontend\|architecture/system_architecture" --include="*.md" . | grep -v docs/superpowers/
```

Expected: no output. Hits under `docs/superpowers/` are the spec and this plan citing the pre-refactor state and are correct to leave.

Then confirm every relative link in the new docs resolves:

```bash
for f in docs/*.md; do
  grep -oE '\]\(([^)]+\.md)\)' "$f" 2>/dev/null | sed -E 's/^\]\(//; s/\)$//' | while read -r link; do
    case "$link" in
      http*) continue ;;
    esac
    target="$(dirname "$f")/$link"
    [ -f "$target" ] || echo "BROKEN in $f -> $link"
  done
done
```

Expected: no output.

- [ ] **Step 10: Verify nothing else broke**

```bash
uv run ruff check . && uv run pytest
```

Expected: no lint output, `19 passed`. Docs-only changes must not affect either, but confirm rather than assume.

- [ ] **Step 11: Review every path, then stage the docs and README explicitly**

Per master standard §10.1, review the paths before staging — never blind
`git add -A`. This task adds, moves and deletes files, so name the paths:

```bash
git status --short
```

Expected: renames/deletions under `docs/engineering/`, `docs/product/` and
`docs/architecture/system_architecture.md`, new `docs/[0-5]_*.md` files, and a
modified `README.md`. Nothing outside `docs/` and `README.md`.

```bash
git add docs/ README.md
git status --short
```

Expected: no remaining unstaged or untracked entries. If any appear, they are
outside this task's scope — do not stage them.

- [ ] **Step 12: Commit**

```bash
git commit -F - <<'MSG'
docs(structure): reshape documentation to Shape B

Master standard section 2 defines Shape B for app and product repos and
permits reshaping repos that are being substantially reworked anyway, which
this refactor is. Done as one commit because every doc path changes at once.

- 0_coding_standards.md: from repo_structure_conventions.md, keeping only the
  genuinely project-specific sections (naming, API, data/model, testing,
  Streamlit) and adding the declared deltas - line-length 100, not
  notebook-first, why data/ and models/ exist, notebook E501 carve-out,
  the scikit-learn pin
- 1_brief.md: from backend_first_roadmap.md, plus positioning and exit criteria
- 2_architecture.md: from system_architecture.md, plus the package layout and a
  dated note that the orchestrator it describes does not exist yet
- 3_decisions.md: new, seeded with DEC-1..DEC-6
- 4_next_steps.md: new, consolidating the roadmap, later scope, remaining
  migration items and the acknowledged out-of-scope gaps, Alembic first
- 5_agent_log.md: new, append-only

Deleted engineering/coding_standards.md: it duplicated master content, which
section 13 forbids, claimed an MCP integration that does not exist, and
prescribed notebook variable naming irrelevant to a FastAPI service. Deleted
product/react_frontend.md as superseded.

Retained docs/agents/ (4 files) and docs/architecture/ (2 files) as subfolders,
per the two-file rule.

Verified: no dangling doc references outside docs/superpowers/, every relative
link in docs/*.md resolves, ruff clean, 19 tests still passing.
MSG
```

---

## Task 5: Add AGENTS.md and CLAUDE.md

**Files:**
- Create: `AGENTS.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: `docs/0_coding_standards.md` from Task 4 — the `@` import target must already exist.
- Produces: the layer 2 entry point that makes every future session in this repo standard-aware.

- [ ] **Step 1: Create `AGENTS.md`**

Per master §13 this stays 20–40 lines, references the master standard and never restates it.

```markdown
# ai-meal-planner

A backend-first multi-agent meal planner: a FastAPI service that predicts calorie
expenditure from a trained model, retrieves meals from a local vector RAG corpus,
verifies nutrition against USDA, and estimates a shopping list. Two clients cover
the same three workflows — a deployed Streamlit demo and a React dashboard.

It is **not** a modelling repo. The one trained artifact was produced by
`notebooks/calorie_expenditure_kaggle_training.ipynb` and promoted; the repo's
centre of gravity is the service, so it follows Shape B.

## Standards

Follow the master standard at `~/Documents/GitHub/coding-standards/`.
Project-specific rules and deliberate overrides: @docs/0_coding_standards.md

## Deltas from the master

- `line-length = 100`, not 79 — FastAPI and Pydantic signatures.
- Not notebook-first: `backend/` is the executable source of truth.
- `data/` and `models/` exist deliberately — a model is served at runtime, and
  `.gitignore` uses the §8 negation pattern to make the shipped artifact explicit.
  **Do not "tidy" this**; the master standard cites this repo as a correct example.
- `scikit-learn` pinned exactly to `1.6.1` — the shipped artifact was trained on it.

## Evidence locations

- `docs/3_decisions.md` — every architectural decision, dated; claims trace here
- `docs/5_agent_log.md` — append-only record of agent work and what was verified
- `docs/4_next_steps.md` — prioritised remaining work and acknowledged gaps
- `models/calorie_expenditure/metrics.json` — the shipped model's actual numbers

## Current state

- 2026-09-10: Phase 0 of the refactor in
  `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md`.
  Baseline is 19 passing tests; ruff and the frontend build gate CI.

## Open risks

- `docs/2_architecture.md` describes an orchestrator that **does not exist yet**;
  it carries a dated divergence note. Phase 1 builds it.
- The trained calorie model is not yet used for meal planning — the meal agent
  computes BMR itself. First task of Phase 1.
- `backend/requirements.txt` is **generated** by `uv export`; edit `pyproject.toml`
  and re-export instead. CI fails on drift.
- Storage is file-backed JSON, rewritten whole and non-atomically. Phase 2.
```

- [ ] **Step 2: Create `CLAUDE.md`**

Exactly one line, so there is one source rather than two that drift. Codex reads `AGENTS.md`; Claude Code reads `CLAUDE.md`.

```markdown
@AGENTS.md
```

- [ ] **Step 3: Verify the import target exists and the line budget holds**

```bash
test -f docs/0_coding_standards.md && echo "import target OK"
wc -l AGENTS.md CLAUDE.md
```

Expected: `import target OK`; `AGENTS.md` between 20 and 45 lines; `CLAUDE.md` exactly 1.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md CLAUDE.md
git commit -F - <<'MSG'
docs(agents): add AGENTS.md and CLAUDE.md per master standard section 13

Layers 2 and 3 of the three-layer agent setup were both missing, so every
session in this repo started with no knowledge of the master standard.

AGENTS.md carries repo identity, the four real deltas, evidence locations,
current state and the open risks a fresh session would otherwise rediscover -
notably that backend/requirements.txt is generated, that the architecture doc
describes an orchestrator that does not exist yet, and that the .gitignore
model-artifact exception is deliberate.

CLAUDE.md is the single line @AGENTS.md so Codex and Claude Code read one
source. The master standard is referenced, never restated.
MSG
```

---

## Task 6: Unify the API port and complete the env examples

**Files:**
- Modify: `README.md:114`, `:120`, `:126`, `:141`, `:246`
- Modify: `frontend/src/App.jsx:235`, `:461`, `:635`, `:653` (message strings only)
- Modify: `backend/.env.example`
- Create: `frontend/.env.example`

**Interfaces:**
- Produces: a single documented port, 8000, matching what `App.jsx:4`, `streamlit_app/app.py:45`, `.streamlit/secrets.example.toml:1` and `backend/app/main.py:240` already default to.

Only the README uses 8010; everything else already uses 8000. So the fix is to correct the README, not the code.

- [ ] **Step 1: Confirm the mismatch**

```bash
grep -rn "8010" --include="*.md" --include="*.py" --include="*.jsx" --include="*.toml" --include="*.yaml" . | grep -v node_modules | grep -v docs/superpowers/
```

Expected: five hits, all in `README.md`.

- [ ] **Step 2: Repoint the README to 8000**

```bash
sed -i '' 's/8010/8000/g' README.md
grep -rn "8010" README.md
```

Expected: no output from the grep.

- [ ] **Step 3: Verify the whole repo now agrees on one port**

```bash
grep -rn "800[0-9]\|801[0-9]" --include="*.md" --include="*.py" --include="*.jsx" --include="*.toml" --include="*.yaml" . | grep -v node_modules | grep -v docs/superpowers/ | grep -oE "80[0-9][0-9]" | sort -u
```

Expected: exactly `8000`.

- [ ] **Step 4: Create `frontend/.env.example`**

`VITE_API_URL` is read at `frontend/src/App.jsx:4` and was undocumented.

```dotenv
# Base URL of the FastAPI backend. Vite only exposes vars prefixed with VITE_.
# Copy to frontend/.env.local for local development.
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 5: Complete `backend/.env.example`**

`backend/app/core/config.py` loads `backend/.env`, but `backend/.env.example` is missing four settings that the root `.env.example` documents, so copying it yields an incomplete config. Add the absent keys so the file the README tells you to copy is complete:

```dotenv
APP_NAME=Multi-Agent Meal Planner API
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8501
GEMINI_API_KEY=
USDA_API_KEY=
FATSECRET_CLIENT_ID=
FATSECRET_CLIENT_SECRET=
MAPS_API_KEY=
INVENTORY_API_KEY=
CALORIE_MODEL_PATH=models/calorie_expenditure/calorie_expenditure_model.joblib
CALORIE_MODEL_VERSION=hist_gradient_boosting_deep_v0.1.0
MEAL_CORPUS_PATH=data/meal_corpus/meals.json
RAG_BACKEND=auto
RAG_EMBEDDING_CACHE_DIR=data/vector_index
RAG_EMBEDDING_ACTIVATION_SIZE=50
ENABLE_GEMINI_ADAPTATION=0
```

Note `ALLOWED_ORIGINS` includes `http://localhost:8501` so the local Streamlit client is not blocked by CORS — the previous `backend/.env.example` omitted it.

- [ ] **Step 6: Verify the documented setup actually works end to end**

```bash
cp backend/.env.example backend/.env
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
sleep 8
curl -s http://127.0.0.1:8000/health | head -c 400
kill %1
```

Expected: JSON with `"status":"ok"` and `"calorie_model_configured":true`. This is the first time the README's own quick start has been executed against the port it documents.

- [ ] **Step 7: Confirm the local `.env` was not staged**

```bash
git status --short backend/.env
```

Expected: no output — `.env` is gitignored. If it appears, stop and do not commit it.

- [ ] **Step 8: Verify nothing else broke, then commit**

```bash
uv run ruff check . && uv run pytest
git add README.md frontend/.env.example backend/.env.example
git commit -F - <<'MSG'
fix(config): unify the API port on 8000 and complete the env examples

The README instructed running uvicorn on 8010 while App.jsx, streamlit_app,
.streamlit/secrets.example.toml and main.py's __main__ block all defaulted to
8000, so the React dashboard could not reach the API with the documented setup.
Only the README was wrong; corrected there rather than changing four defaults.

Also:
- adds frontend/.env.example documenting VITE_API_URL, read at App.jsx:4 and
  previously undocumented
- completes backend/.env.example, which the README tells you to copy but which
  omitted APP_NAME, the three model and corpus paths, and localhost:8501 in
  ALLOWED_ORIGINS - so a local Streamlit client hit CORS

Verified: no 8010 references remain outside the superpowers specs, the repo
agrees on a single port, and the documented start command serves /health with
status ok and calorie_model_configured true. Ruff clean, 19 tests passing.
MSG
```

Note: `frontend/src/App.jsx` needs no change — its four "running on port 8000" strings are already correct.

---

## Task 7: Rewrite the README quick start for uv and macOS/Linux

**Files:**
- Modify: `README.md` §6 (Quick Start), §9 (Development), §5 (Project Structure)

**Interfaces:**
- Consumes: the `uv` workflow from Task 1, the port from Task 6, the doc layout from Task 4.

The current quick start is PowerShell-only, uses `python -m venv` plus `pip`, and cannot run on macOS — `python` is not on PATH.

- [ ] **Step 1: Replace §6.1 Prerequisites**

```markdown
### 6.1 Prerequisites

- [uv](https://docs.astral.sh/uv/) — manages the Python version and dependencies
- Optional: Node.js 20+ and npm for the React dashboard
- Optional: Gemini, USDA, and FatSecret API keys for live external integrations

`uv` installs and pins Python 3.11 itself, so no system Python is required.
```

- [ ] **Step 2: Replace §6.2 Backend API with a uv-based, cross-platform block**

```markdown
### 6.2 Backend API

Run these commands from the project root. They work identically on macOS, Linux
and Windows.

```bash
uv sync --all-groups
cp backend/.env.example backend/.env
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

On Windows PowerShell, substitute the copy step:

```powershell
Copy-Item backend/.env.example backend/.env
```

The API runs at `http://127.0.0.1:8000`, with interactive docs at
`http://127.0.0.1:8000/docs`.
```

- [ ] **Step 3: Update §6.3 and §6.4 to use `uv run` and env vars portably**

For Streamlit, replace the PowerShell-only `$env:` lines with a cross-platform form:

```bash
STREAMLIT_DEMO_MODE=1 uv run streamlit run streamlit_app/app.py
```

and for API-client mode:

```bash
API_BASE_URL=http://127.0.0.1:8000 uv run streamlit run streamlit_app/app.py
```

Keep the existing PowerShell `$env:` variants beneath each, labelled for Windows.
For §6.4, add a line before `npm install` telling the reader to copy
`frontend/.env.example` to `frontend/.env.local` if the backend is not on
`localhost:8000`.

- [ ] **Step 4: Replace §9 Development**

```markdown
## 9. Development

Run the backend checks — the same gates CI enforces:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Build and lint the React dashboard:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

Health smoke test, with the backend running:

```bash
curl http://127.0.0.1:8000/health
```

**Dependencies:** `pyproject.toml` is the only file to edit by hand. After
changing it, run `uv lock` and regenerate the export that Render installs from:

```bash
uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o backend/requirements.txt
```

CI fails if `backend/requirements.txt` drifts from `uv.lock`.
```

- [ ] **Step 5: Update §5 Project Structure**

Add `AGENTS.md`, `CLAUDE.md` and `uv.lock` to the tree, and confirm the `docs/`
subtree matches the Shape B layout written in Task 4.

- [ ] **Step 6: Execute every command in the README as written**

A quick start that has not been run is not known to work. From a clean clone in a
temporary directory:

```bash
cd "$(mktemp -d)"
git clone "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner" fresh
cd fresh
uv sync --all-groups
cp backend/.env.example backend/.env
uv run pytest
uv run ruff check .
```

Expected: `uv sync` succeeds without a preinstalled Python, `19 passed`, and no
lint output. Then confirm the server starts:

```bash
uv run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
sleep 8
curl -s http://127.0.0.1:8000/health | head -c 200
kill %1
```

Expected: JSON with `"status":"ok"`. Delete the temporary clone afterwards.

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -F - <<'MSG'
docs(readme): rewrite quick start for uv and non-Windows shells

The quick start was PowerShell-only and used python -m venv plus pip, so it
could not be followed on macOS, where python is not on PATH and only a 3.9
python3 exists - too old for the X | None syntax in rag/rules.py.

- prerequisites now list uv, which installs and pins Python 3.11 itself
- backend, Streamlit and frontend setup use uv run and cross-platform env var
  syntax, with the PowerShell variants kept and labelled for Windows
- development section lists the exact gates CI enforces and documents that
  pyproject.toml is the only hand-edited dependency file, with the uv export
  command for regenerating what Render installs
- project structure adds AGENTS.md, CLAUDE.md and uv.lock

Verified by executing every documented command from a fresh clone in a
temporary directory with no preinstalled Python: uv sync succeeded, 19 tests
passed, ruff was clean, and the documented start command served /health with
status ok.
MSG
```

---

## Phase 0 Exit Gate

Per spec §5, Phase 0 is done when a clean clone runs `uv sync && uv run pytest`
successfully on macOS, and CI fails on a deliberately introduced lint error, a
frontend build error, and a stale requirements export.

- [ ] `uv sync --all-groups && uv run pytest` → `19 passed`, from a fresh clone
- [ ] `uv run ruff check .` and `uv run ruff format --check .` → both clean
- [ ] `(cd frontend && npm ci && npm run lint && npm run build)` → succeeds
- [ ] Lint gate verified to fail on a deliberate unused import, then reverted (Task 3 Steps 4–5)
- [ ] Drift gate verified to fail on a hand-edited export, then reverted (Task 3 Steps 6–7)
- [ ] Frontend build gate: confirm CI fails on a deliberate syntax error in `frontend/src/App.jsx`, then revert — the one gate Task 3 does not itself prove
- [ ] `AGENTS.md`, `CLAUDE.md` and `docs/0_coding_standards.md` through `docs/5_agent_log.md` all exist
- [ ] No dangling doc links outside `docs/superpowers/` (Task 4 Step 9)
- [ ] Repo agrees on port 8000 (Task 6 Step 3)
- [ ] All seven commits follow §9, one coherent change each
- [ ] `git status --short` is clean; no `.env`, `.venv`, `node_modules` or `dist` staged
- [ ] Append the Phase 0 completion entry to `docs/5_agent_log.md`

Then write the Phase 1 plan from spec §6.
