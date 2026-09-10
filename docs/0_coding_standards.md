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
  using the slack that master §3 already grants to notebook display and print
  calls. Every other rule still applies to notebooks.
- **`scikit-learn` is pinned exactly to `1.6.1`.** The shipped model artifact was
  trained under it; unpinning silently risks load-time incompatibility warnings and
  changed predictions.

## 3. Naming

- Agent classes end with `Agent`, for example `CalorieExpenditureAgent`.
- Service classes end with `Service` or `Client`, for example `UsdaFoodDataClient`.
- Pydantic request models end with `Request`.
- Pydantic response models end with `Response`.
- Database abstractions end with `Repository`.
- Model artifacts include semantic versions, for example `calorie_expenditure_v0.1.0.joblib`.

## 4. API Conventions

- Prefer nouns in route paths: `/meal-plans`, `/nutrition/verify`, `/calorie-expenditure/predict`.
- Include `request_id`, `model_version`, and `metadata` in AI or ML responses.
- Never return raw LLM text as the primary contract. Return typed JSON.
- Include confidence and warnings for generated, predicted, or externally matched values.
- Keep health-sensitive fields explicit and auditable.

## 5. Data & Model Conventions

- Put raw local datasets under `data/raw/`.
- Put cleaned feature tables under `data/processed/`.
- Put third-party reference files under `data/external/`.
- Save trained models under `models/`.
- Track model metrics in a small JSON file next to the artifact.

## 6. Testing Conventions

- Unit test schemas, feature transforms, calorie prediction inference, and nutrition scaling.
- Mock external APIs by default.
- Add one integration test for the full meal-planning orchestration.
- Keep deterministic fallback tests so demos work without paid API keys.

## 7. Streamlit Convention

Use Streamlit as the first live interface. It should call the same backend service layer as FastAPI, not duplicate agent logic. Treat it as an operator/demo UI until the React frontend is ready.
