# Refactor and Standards Alignment — Design

**Date:** 2026-09-10
**Status:** Approved, ready for implementation planning
**Scope:** Whole repository — backend architecture, storage, tests/CI, frontend, Streamlit, docs

## 1. Purpose

`ai-meal-planner` works and is better engineered than a typical study project, but
it carries four distinct problem clusters: architecture gaps that undercut its own
stated design, substantial duplication, thin test coverage, and drift from the
master coding standard. This document specifies a five-phase refactor that closes
all four without changing what the product does for a user.

**Positioning decision:** the project is a self-directed portfolio piece first,
with an intended path to real users later. Every choice here is made so that
nothing has to be thrown away when that transition happens. No rubric or external
marking criteria apply.

**Planning granularity:** this document is the spec for the whole refactor, but it
is deliberately too large for one implementation plan. Each phase in §5–§9 gets its
own plan, written and executed in order, with the phase's "Done when" clause as its
exit gate. Later phases assume the earlier ones have landed — in particular, Phase 1
depends on Phase 0's CI gates, Phase 2 on Phase 1's DI container, and Phase 4's
Streamlit change on Phase 1's importable package.

## 2. Findings

Line references are to the pre-refactor `main` at commit `d9ce89e`.

### 2.1 Architecture and correctness

| # | Finding | Location |
| --- | --- | --- |
| A1 | **The trained calorie model is not used for meal planning.** `MealRecommendationAgent` recomputes a daily target with its own Mifflin-St Jeor implementation instead of consuming `CalorieExpenditureAgent`. The agent already returns exactly the value needed, `meal_calorie_budget_kcal`, and it is ignored. This contradicts step 2 of the documented workflow. | `backend/app/agents/meal_recommendation_agent.py:120`, `backend/app/agents/calorie_expenditure_agent.py:27` |
| A2 | **No orchestrator.** `services/` is an empty package; `main.py` performs the orchestration inline. Workflow steps 5–6 of the roadmap — compare the generated estimate against the verified total, revise portions when out of tolerance — are not implemented at all. | `backend/app/main.py:127-178`, `backend/app/services/__init__.py` |
| A3 | **Agents are module-level singletons built at import time**, so no endpoint can be tested without constructing the real agents, loading the model artifact, and building the retrieval index. | `backend/app/main.py:58-82` |
| A4 | **Dual `try/except ImportError` import block** duplicating every import to work around package-path ambiguity. | `backend/app/main.py:12-40` |
| A5 | **No `response_model` on any of the 8 endpoints**; all return `Dict[str, Any]`. `/docs` therefore documents no response schemas and nothing enforces the response contract. | all routes in `backend/app/main.py` |
| A6 | **Bare `except Exception` returns the raw exception string in the HTTP body**, leaking internals and mapping every failure — provider outage, missing profile, retrieval failure — to a single 500. | `backend/app/main.py:175-177` |
| A7 | **Dead code that raises `NotImplementedError`**: `predict_user_preferences` and `_initialize_preference_classifier`. The empty `ml/` package is unused scaffolding. | `backend/app/agents/meal_recommendation_agent.py:179`, `:513` |

### 2.2 Duplication

| # | Finding | Location |
| --- | --- | --- |
| D1 | `AgentMetadata` is defined three times, once per agent. | `meal_recommendation_agent.py:25`, `nutrition_verification_agent.py:28`, `supermarket_agent.py:27` |
| D2 | `_average_confidence` is defined twice. | `nutrition_verification_agent.py:448`, `supermarket_agent.py:216` |
| D3 | **Large reference tables hardcoded inside methods**: a 45-entry calorie lookup, ~100 lines of price/category mapping, macro fallbacks, trusted local overrides, and a craving `if/elif` chain of fallback meal templates. This is data living in code. | `meal_recommendation_agent.py:_estimate_ingredient_calories`, `:_fallback_payload`, `nutrition_verification_agent.py:_estimate_macros_per_100g`, `:_trusted_local_override`, `supermarket_agent.py:_map_inventory_and_price` |
| D4 | **Streamlit demo mode reimplements the backend.** `local_demo_request` and `is_meal_like_input` are a parallel implementation of meal selection, macros and pricing — a second source of truth guaranteed to drift. | `streamlit_app/app.py:115`, `:155` |
| D5 | **`App.jsx` is 811 lines**: three tab components, eight shared UI primitives, formatters, an inline SVG icon, and raw `axios` calls. Each tab duplicates its own `isLoading`/`error`/`data` state triple. No `components/`, `api/`, or `hooks/` directories exist. | `frontend/src/App.jsx` |

### 2.3 Tests and CI

- 13 test functions — **19 cases once parametrization expands them** — all
  unit-level against the retriever and two agents.
- **Zero endpoint tests** — `TestClient` appears nowhere in the repository.
- No coverage at all for the nutrition agent, supermarket agent, or `rag/rules.py`;
  storage has one test covering one method.
- No frontend tests; `vitest` is not installed.
- CI runs `compileall` plus `pytest` only. Ruff is configured in `pyproject.toml`
  and never runs. The frontend lint and build scripts exist and never run.

### 2.4 Developer experience

- **Dependencies declared three times**: root `requirements.txt` (which just
  includes the backend one), `backend/requirements.txt`, `[project].dependencies`,
  and a `[tool.poetry.dependencies]` block. No lockfile. Mostly unpinned.
  `pytest` ships in the runtime install.
- **Port mismatch**: the frontend and Streamlit both default to `:8000`; the README
  instructs running uvicorn on `:8010`. The React app cannot reach the API with the
  documented setup.
- The README Quick Start is PowerShell-only. There is no `frontend/.env.example`
  documenting `VITE_API_URL`.
- **Storage rewrites the entire JSON file per request, non-atomically** — a crash
  mid-write corrupts the store. History is capped at 200 records and feedback at
  500. `list_for_user` loads every record and filters in Python.

### 2.5 Drift from the master coding standard

Audited against `~/Documents/GitHub/coding-standards/coding_standards.md`.

**Already compliant, and deliberately left alone:** the `.gitignore` uses the §8
"blanket rule plus explicit negation" pattern for the shipped model artifact. The
master standard names this repository as one of two doing it correctly. Phase work
must not disturb it.

| § | Violation |
| --- | --- |
| 13 | **No `AGENTS.md` and no `CLAUDE.md`.** Layers 2 and 3 of the three-layer setup are entirely absent, so every session in this repo starts with no knowledge of the standard. |
| 13 | `docs/engineering/coding_standards.md` is a local copy of master content (PEP 8, typing) — precisely the drift §13 forbids. It is also stale: it claims the architecture integrates "Model Context Protocol (MCP) tools", which nothing in the repo does, and prescribes `train_df`/`log_reg_clf` notebook naming, irrelevant to a FastAPI service. `log_reg_clf` occurs only inside the dead code at A7. |
| 13 | No agent collaboration log. |
| 2 | Docs are not in **Shape B**. This is an app/product repo. §2 permits reshaping for "repos being substantially reworked anyway", which this refactor is. |
| 3 | **Zero Google-style docstrings across all 20 backend `.py` files.** |
| 3 | `line-length = 100` versus the master's "79 where practical" — defensible for FastAPI signatures, but undeclared. §13 requires deltas be stated explicitly. |
| 9 | Commit messages carry **no scopes** and several carry no type at all (`polish streamlit demo controls`, `add local vector rag meal retrieval`). |

## 3. Decisions taken

| ID | Decision | Rationale |
| --- | --- | --- |
| DEC-1 | Portfolio-first, built for a later transition to real users | No throwaway work; boundaries chosen so production swaps are config changes |
| DEC-2 | Streamlit demo mode **imports the real backend in-process** | Removes D4 entirely and makes drift structurally impossible. Requires `backend` to be an importable package, which Phase 1 needs anyway |
| DEC-3 | Sequencing: **foundation first** (Approach A), with the calorie wiring pulled to the front of Phase 1 | Foundation is cheap and makes later phases self-enforcing and verifiable; A1 is the one gap with story-level consequences, so it must not sit behind plumbing |
| DEC-4 | Storage: **repository `Protocol` plus a SQLite implementation**, JSON retained for demo mode | Real SQL for the portfolio story, zero infra to run, and Postgres later becomes a config change plus one class |
| DEC-5 | Docs reshaped to **Shape B**, in one atomic commit | Every doc path changes at once; spreading it across commits leaves the README linking to moved files |
| DEC-6 | `requirements.txt` and `backend/requirements.txt` become **generated artifacts** | Streamlit Cloud reads the root file and Render's `buildCommand` reads the backend one, so neither can be deleted; generating both from `uv.lock` restores a single source of truth |

## 4. Target structure

```text
ai-meal-planner/
├── AGENTS.md                       # NEW  §13 layer 2
├── CLAUDE.md                       # NEW  contains only: @AGENTS.md
├── pyproject.toml                  # single dependency source of truth
├── uv.lock                         # NEW
├── requirements.txt                # GENERATED (uv export) — Streamlit Cloud
├── backend/requirements.txt        # GENERATED (uv export) — Render buildCommand
├── docs/
│   ├── 0_coding_standards.md       # deltas ONLY
│   ├── 1_brief.md
│   ├── 2_architecture.md
│   ├── 3_decisions.md              # NEW  dated decision log
│   ├── 4_next_steps.md
│   ├── 5_agent_log.md              # NEW  append-only
│   ├── agents/                     # kept — 4 files justify a subfolder per §2
│   └── superpowers/specs/          # this document
├── data/reference/                 # NEW  extracted from D3
│   ├── ingredient_calories.json
│   ├── macro_fallbacks.json
│   ├── trusted_overrides.json
│   ├── supermarket_prices.json
│   └── fallback_meals.json
├── backend/app/
│   ├── api/routes/{health,meal_plans,calories,feedback}.py
│   ├── core/{config,container,exceptions}.py
│   ├── services/meal_planning_service.py
│   ├── repositories/{base.py,json_store/,sql/}
│   ├── schemas/{requests,responses,common}.py
│   ├── agents/
│   └── rag/
├── frontend/src/{api,components/ui,features,hooks,lib}/
└── streamlit_app/{app.py,api.py,demo.py,views/}
```

## 5. Phase 0 — Foundation

**Goal:** make the repo runnable in one command, self-enforcing of the standard,
and gated by CI, before any refactor lands.

1. **`AGENTS.md`** from `coding-standards/templates/AGENTS.md.template`, 20–40 lines:
   repo identity, reference to the master standard, `@docs/0_coding_standards.md`
   import, deltas, evidence locations, current state, open risks. Plus `CLAUDE.md`
   containing only `@AGENTS.md`.
2. **`docs/0_coding_standards.md`** replacing `docs/engineering/coding_standards.md`.
   Contains only genuine deltas. Removes the copied PEP 8/typing text, the false MCP
   claim, and the notebook naming rules. Declares: Shape B, `line-length = 100` and
   why, service-app rather than notebook-first, and the §8-justified reason `data/`
   and `models/` exist here.
3. **Docs reshaped to Shape B** in one commit (DEC-5). `1_brief.md` derives from
   `product/backend_first_roadmap.md`; `2_architecture.md` consolidates
   `architecture/system_architecture.md` and `architecture/vector_rag.md` and links
   `docs/agents/`; `4_next_steps.md` absorbs the README roadmap. `3_decisions.md` is
   seeded with DEC-1 through DEC-6. All README and cross-doc links updated in the
   same commit.
4. **Dependency consolidation.** `pyproject.toml` becomes the only hand-edited
   source; the dead `[tool.poetry]` block is removed; `pytest` and `ruff` move to a
   dev dependency group; `uv.lock` is committed. Both `requirements.txt` files are
   regenerated with `uv export`.
5. **CI gates added** to `.github/workflows/ci.yml`: `uv sync`, `ruff check`,
   `ruff format --check`, `pytest` on a 3.11 + 3.12 matrix, `npm run lint`,
   `npm run build`, and a check that the exported requirements files match `uv.lock`.
6. **Port unified to 8000** across README, `frontend/src/App.jsx` default,
   Streamlit default and `render.yaml`. Add `frontend/.env.example` documenting
   `VITE_API_URL`.
7. **README Quick Start** gains bash/zsh instructions using `uv` alongside the
   existing PowerShell block.

**Done when:** a clean clone runs `uv sync && uv run pytest` successfully on macOS,
and CI fails on a deliberately introduced lint error, a frontend build error, and a
stale requirements export.

## 6. Phase 1 — Backend architecture

Ordered so A1 lands first (DEC-3).

1. **Wire the calorie model in.** Create `services/meal_planning_service.py`.
   `/generate-meal-plan` accepts optional biometrics; the orchestrator calls
   `CalorieExpenditureAgent`, reads `meal_calorie_budget_kcal`, and passes it to
   `MealRecommendationAgent`. Delete `MealRecommendationAgent.calculate_bmr`; its
   Mifflin-St Jeor logic moves into `CalorieExpenditureAgent` as the
   no-model-available fallback, which is where estimating expenditure belongs.
   When biometrics are absent, the profile repository supplies them as it does today.
2. **Reconciliation loop** (A2). The orchestrator compares the portion-scaled
   estimate against the verified nutrition total. If the deviation exceeds a
   configurable tolerance (default 15%), portions are rescaled once and re-verified.
   The response carries `reconciliation` metadata recording the attempt, the before
   and after deviation, and whether tolerance was met. Exactly one retry — no loop.
3. **Package the backend properly** so `from backend.app...` always resolves, then
   delete the dual-import block (A4).
4. **DI container** (`core/container.py`). Agents and repositories are constructed in
   a FastAPI `lifespan` handler and injected via `Depends()`. This is the change that
   makes endpoint testing possible.
5. **Split `main.py`** into `api/routes/{health,meal_plans,calories,feedback}.py`
   using `APIRouter`. `main.py` retains only app construction, middleware, lifespan
   and router registration.
6. **`schemas/responses.py`** with a response model per endpoint, and
   `response_model=` on all 8 routes (A5).
7. **Deduplicate shared models** into `schemas/common.py`: one `AgentMetadata` (D1)
   and one confidence-averaging helper (D2).
8. **Typed exceptions** in `core/exceptions.py` — `ProfileNotFound`,
   `RetrievalUnavailable`, `NutritionProviderError`, `MealPlanningError` — with a
   FastAPI exception handler mapping each to an appropriate status code and a safe
   client-facing message. Internal detail goes to logs only (A6).
9. **Extract reference data** to `data/reference/*.json`, loaded once at startup
   (D3). Agents keep the logic and lose the tables.
10. **Delete dead code** (A7) and either use or remove the empty `ml/` package.
11. **Google-style docstrings** on every public class and function in each module
    touched by this phase.

**Done when:** `/generate-meal-plan` demonstrably uses the model's calorie budget,
the response includes `reconciliation` metadata, `/docs` shows full response
schemas, and a provider failure returns a non-500 status with no internal detail
in the body.

## 7. Phase 2 — Storage

1. **`repositories/base.py`** — a `Protocol` per repository: `UserProfileRepository`,
   `MealPlanRepository`, `MealFeedbackRepository`.
2. **JSON implementations retained** for demo mode, moved to
   `repositories/json_store/`, with two fixes: writes become atomic via temp file
   plus `os.replace`, and the 200/500 record caps are removed.
3. **`repositories/sql/`** — SQLModel table definitions and a SQLite implementation
   with indexed `user_id` lookups, replacing load-everything-then-filter-in-Python.
   Selected by a `STORAGE_BACKEND=json|sqlite` setting, defaulting to `sqlite`.
4. **`core/config.py` migrated to `pydantic-settings`**, replacing the hand-rolled
   `from_env` dataclass. Pydantic is already a dependency.
   **`pydantic-settings` is a new dependency** — it is a separate
   distribution from `pydantic` and is in neither `pyproject.toml` nor
   `uv.lock` today. Phase 2 must add and lock it, then re-export
   `backend/requirements.txt`, or the drift gate fails.
5. Schema creation via `create_all`. **Alembic is explicitly out of scope** and is
   recorded in `4_next_steps.md` — migrations are a real gap and will be stated as
   one rather than implied to be handled.

**Done when:** both backends pass the same contract test suite (§8), and switching
`STORAGE_BACKEND` changes no API behaviour.

## 8. Phase 3 — Tests and CI

**Endpoint tests.** All 8 routes, happy path and error path, via `TestClient` with
DI overrides supplying fake agents. No network access in CI.

**Repository contract tests.** One suite parameterised over both implementations,
proving JSON and SQLite behave identically. This is what makes the `Protocol`
boundary from Phase 2 worth having rather than decorative.

**New unit coverage** for the currently untested: the nutrition agent with mocked
USDA and FatSecret responses including the per-provider cooldown path, the
supermarket agent, and `rag/rules.py`.

**Retained.** The existing retrieval quality regression tests remain the guard
against RAG changes and must keep passing unchanged through every phase.

**Frontend.** Add `vitest` and React Testing Library. Cover the API client and one
test per tab component.

**Coverage.** Reported in CI with a floor set from the actual post-phase number, so
the floor is honest rather than aspirational.

**Done when:** every endpoint has a test, the contract suite runs green against both
storage backends, and CI enforces the coverage floor.

## 9. Phase 4 — Frontend and Streamlit

**React** — decompose `App.jsx` (D5):

- `api/client.js` — a single axios instance, `baseURL` from env, error interceptor
- `api/mealPlanner.js` — one function per endpoint
- `hooks/useAsyncRequest.js` — removes the duplicated loading/error/data triple
- `components/ui/` — the eight primitives, one file each
- `features/{mealPlan,calories,history}/` — the three tabs
- `lib/format.js` — the formatters
- `App.jsx` retains only shell, tab state and routing

**Streamlit** — delete `local_demo_request` and `is_meal_like_input` (D4, DEC-2).
Demo mode calls a shared agent factory, the same one the DI container uses, so the
demo cannot diverge from the backend. `app.py` splits into `app.py`, `api.py`,
`demo.py` and `views/`.

**Done when:** no file in `frontend/src` or `streamlit_app` exceeds ~200 lines, the
deployed Streamlit demo still works with no API server running, and both clients
still cover meal plan, calorie prediction and history.

## 10. Testing strategy

| Layer | Approach |
| --- | --- |
| Endpoints | `TestClient` with DI overrides; fake agents; no network |
| Repositories | One contract suite parameterised across JSON and SQLite |
| Agents | Unit tests with mocked HTTP providers, including failure and cooldown paths |
| RAG | Existing quality regression tests, unchanged, as the guard |
| Orchestrator | Reconciliation tolerance covered both in and out of tolerance |
| Frontend | vitest + React Testing Library on the API client and each tab |
| Streamlit | Smoke test that the shared agent factory builds |

External providers are never called in tests. Ruff, both test suites, the frontend
build and the requirements-drift check all gate CI from Phase 0 onward.

## 11. Conventions applied throughout

- Every commit follows §9: `<type>(<scope>): <imperative summary>`, one coherent
  change per commit, material detail in the body. No phase-sized commits.
- `docs/3_decisions.md` gains a dated entry for each architectural decision.
- `docs/5_agent_log.md` is appended after each phase — what changed, what was
  verified, what remains open. Append-only; corrections are new entries.
- Google-style docstrings on every reusable function in modules that are touched.
- Claims of completion require the verification command and its output, never
  assertion alone.

## 12. Out of scope

Stated explicitly so these are known gaps rather than oversights:

- **Alembic migrations** — deferred to `4_next_steps.md` (§7.5)
- **Authentication and user accounts** — already on the README roadmap
- **Postgres** — the Phase 2 boundary makes it a config change plus one class
- **Expanding the meal corpus** beyond its current 34 templates
- **Using feedback signals as retrieval ranking features** — roadmap item
- **Migrating `requests` to async `httpx`** — the current `run_in_threadpool`
  wrapping is correct, just not idiomatic
- **Retraining or improving the calorie model**

## 13. Risks

| Risk | Mitigation |
| --- | --- |
| The docs reshape breaks every doc link at once | Single atomic commit, with a link check before committing |
| The DI refactor is broad and touches every endpoint | Phase 0's CI gates land first; endpoint tests are written against the new container as it is built |
| Streamlit in-process import could break the deployed demo | Verify the demo runs with no API server before the Streamlit commit; the shared factory is smoke-tested |
| Extracting reference data could silently change outputs | The retrieval regression tests plus a before/after comparison on a fixed set of cravings |
| SQLite offers little visible payoff for a portfolio reader | Accepted knowingly under DEC-4; it is the phase to cut first if scope must shrink |
