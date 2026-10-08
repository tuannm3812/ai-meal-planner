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

- 2026-09-14: refactor Phases 0–3 (`docs/superpowers/specs/2026-09-10-refactor-
  and-standards-alignment-design.md`) are done, open as PRs #1–#4 stacked on
  each other. Phase 4 split into 4a and 4b: **Phase 4a (React decomposition
  of `frontend/src/App.jsx`) is done**; **Phase 4b (the matching Streamlit
  split) is planned but unstarted**. 222 backend tests, 35 frontend tests,
  all green; backend coverage 91%, floor 89% enforced in CI.

## Open risks

- Storage defaults to `STORAGE_BACKEND=sqlite` and starts empty; JSON history
  is invisible until `scripts/migrate_json_to_sqlite.py` runs once, and that
  script is **not idempotent** (a second run duplicates rows). Schema creation
  is `create_all`, which cannot alter an existing table, so there is no
  migration path once a deployment holds real data.
- The typed exceptions in `core/exceptions.py` (`ProfileNotFound`,
  `RetrievalUnavailable`, `NutritionProviderError`) are wired to handlers but
  never raised; every failure still lands on the catch-all 500.
- `agents/meal_recommendation_agent.py` sits at ~81% coverage, the largest
  remaining gap in core business logic.
- `backend/requirements.txt` is **generated** by `uv export`; edit
  `pyproject.toml` and re-export instead. CI fails on drift.
