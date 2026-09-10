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
