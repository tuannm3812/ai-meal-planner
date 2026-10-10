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
  passed `main`'s older single-job workflow. `uv run pytest` runs 486 tests (402
  backend, 84 Streamlit) with the Gemini warning fix, coverage 94.20% against the 89% CI floor;
  the frontend has 39 tests.
- 2026-10-10: G3 (#11/#12), G4 (#13), G5b (#14), G6's code half (#15), the
  README screenshots and decision-log index (#16) and G6's deployment half
  (#17) are merged. #17 is `.github/workflows/deploy.yml` (Cloud Run, Workload
  Identity Federation, inert until configured), `docs/6_deployment.md`,
  `scripts/live_check.sh` and `X-Instance-Id`. CI rehearses a two-instance
  deploy and a key revocation. The real deploy needs the owner's GCP project
  (`docs/6_deployment.md` §1).
- 2026-10-10: G10b tracing is on `feat/g10b-tracing`, in review. It has
  OpenTelemetry stage spans exported to Cloud Trace over OTLP, and holds
  traces and logs to one allowlist (DEC-17 to DEC-19). The proof is
  `test_telemetry_redaction.py`.

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
- `ProfileNotFound` in `core/exceptions.py` is wired to a handler but never
  raised. The other three are raised:
  - `NutritionProviderError` (502, code `unverified_required`) only when
    `REQUIRE_VERIFIED_NUTRITION` is on and an ingredient is estimated. It is off
    by default;
  - `RetrievalUnavailable` (503) when no fallback template is safe and the
    retriever never loaded;
  - `NoFeasibleMeal`, only when the corpus and the fallback templates are both
    exhausted. It is an internal signal: `MealPlanningService` turns it into a
    successful response with `plan_status: "infeasible"`, so it never reaches
    HTTP as a 422.
- **`render.yaml` will not start since G4.** It sets `APP_ENV=production` with no
  `API_KEYS`, and production refuses that by design. Cloud Run is now the target
  (DEC-16), so retire Render or fix it as a documented fallback.
- **In hosted mode the React History tab button stays visible.** Its contents
  are replaced with a notice. Hiding the button would need a `/health` call on
  first render, which the frozen `App.test.jsx` forbids. React cannot call a keyed
  production API in v1 anyway (DEC-8).
- **G4 limits, by design.**
  - The rate limit is per instance, so N instances allow N times the limit.
  - Open local mode (no `API_KEYS`) is unauthenticated, though production
    refuses to start in it.
  - The React dashboard cannot call a keyed API in v1.
  - A pre-G4 `database/ai_meal_planner.db` is refused at startup. Delete it
    (stateless v1).
- **Telemetry limits (DEC-17, DEC-18).** Three things the allowlist does not
  cover:
  - unexpected 500s log a traceback, including that exception's message;
  - Cloud Run's request log and the server's access log record full URLs, so
    `user_id` must be opaque;
  - Cloud Run limits CPU between requests, so batched spans can be sent late.
- `agents/meal_recommendation_agent.py` sits at 93% coverage. What remains
  uncovered: the retriever's startup failure, the Gemini client setup (it runs
  only with a key), one warning branch and one defensive return.
- `backend/requirements.txt` is **generated** by `uv export`; edit
  `pyproject.toml` and re-export instead. CI fails on drift.
