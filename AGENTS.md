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

- 2026-10-08: the refactor (`docs/superpowers/specs/2026-09-10-refactor-and-
  standards-alignment-design.md`, Phases 0–3, 4a and 4b) is **on `main`**.
  PRs #1–#6 and the `.gitignore` fix #7 were merged with merge commits.
  `main` CI passed all four jobs after each of #1–#6; #7 merged first and
  passed `main`'s older single-job workflow. `uv run pytest` runs 255 tests (222
  backend, 33 Streamlit), coverage 91% against the 89% CI floor; the frontend
  has 36 tests.
- Next work follows the production-readiness direction in
  `docs/5_agent_log.md` (2026-10-07 and 2026-10-08 entries): G3 typed
  failure semantics, then G4 API-key auth, G5 containers, G6 hosted mode
  with history disabled, and tracing after G5.

## Open risks

- `.streamlit/secrets.toml` is now gitignored (PR #7). Local
  `database/meal_history.json` still holds 75 records, most of them likely
  synthetic (see the agent log); cleanup is an owner decision and must happen
  before `scripts/migrate_json_to_sqlite.py` is ever run.
- Storage defaults to `STORAGE_BACKEND=sqlite` and starts empty; JSON history
  is invisible until `scripts/migrate_json_to_sqlite.py` runs once, and that
  script is **not idempotent** (a second run duplicates rows). Schema creation
  is `create_all`, which cannot alter an existing table, so there is no
  migration path once a deployment holds real data.
- Three of the typed exceptions in `core/exceptions.py` (`ProfileNotFound`,
  `RetrievalUnavailable`, `NutritionProviderError`) are wired to handlers but
  never raised. Only `NoFeasibleMeal` (422) is raised, when no meal can satisfy
  the request's hard constraints.
- `agents/meal_recommendation_agent.py` sits at ~85% coverage, the largest
  remaining gap in core business logic.
- `backend/requirements.txt` is **generated** by `uv export`; edit
  `pyproject.toml` and re-export instead. CI fails on drift.
