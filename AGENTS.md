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
- `DESIGN.md` — the design standard for the app, poster, LinkedIn image and deck
- `docs/openapi.json` — the API contract; CI fails on drift, regenerate with
  `scripts/export_openapi.py`

## Agent review loop

Changes are reviewed in a loop between Claude Code and Codex, through
`docs/5_agent_log.md`. Each agent appends one dated entry per turn, headed
`## YYYY-MM-DD — Claude — <title>` or `— Codex —`: Claude records what it
changed and verified, Codex reviews that and records findings (P1–P3) or a
clean verdict, and Claude answers each finding in its next entry. A branch is
pushed only after a clean Codex review; nothing is merged without the owner.
An entry that needs the owner says "Needs Mike", which ends the loop.

Run a Codex review by hand with
`codex exec --sandbox workspace-write "<prompt>" < /dev/null` (without the
redirect it waits on stdin and never starts). `scripts/agent_relay.sh` automates
the hand-offs by watching the log; its header says how to run it.

## Current state

- 2026-10-08: the refactor (`docs/superpowers/specs/2026-09-10-refactor-and-
  standards-alignment-design.md`, Phases 0–3, 4a and 4b) is **on `main`**.
  PRs #1–#6 and the `.gitignore` fix #7 were merged with merge commits.
  `main` CI passed all four jobs after each of #1–#6; #7 merged first and
  passed `main`'s older single-job workflow. `uv run pytest` runs 596 tests (504
  backend, 92 Streamlit), coverage 95.06% against the 89% CI floor;
  the frontend has 44 tests.
- 2026-10-10: G3 (#11/#12), G4 (#13), G5b (#14), G6's code half (#15), the
  README screenshots and decision-log index (#16) and G6's deployment half
  (#17) are merged. #17 is `.github/workflows/deploy.yml` (Cloud Run, Workload
  Identity Federation, inert until configured), `docs/6_deployment.md`,
  `scripts/live_check.sh` and `X-Instance-Id`. CI rehearses a two-instance
  deploy and a key revocation. The real deploy went live on 2026-11-22 (see
  below).
- 2026-10-11: G10b tracing (#18) is merged. It has OpenTelemetry stage spans
  exported to Cloud Trace over OTLP, holds traces and logs to one allowlist,
  and continues only an incoming `traceparent` (DEC-17 to DEC-20). The proof
  is `test_telemetry_redaction.py`. The client-safe Gemini warning (#19) is
  merged too. A real trace reached Cloud Trace on 2026-11-22.
  Direction item G, the committed and CI-checked OpenAPI contract
  (`docs/openapi.json`, DEC-21), is merged (#20), and so is its follow-up
  (#21), which declares the `X-API-Key` scheme and each route's domain errors.
- 2026-10-15: demo feedback parity (#25) and the supermarket agent doc (#26)
  are merged. The owner chose **meal quality** as the next milestone; its
  baseline and order of work are in `docs/7_meal_quality.md`, measured by
  `scripts/meal_quality_baseline.py`.
- 2026-10-17: the owner set the meal-quality targets (calories within 10%,
  macros inside AMDR; DEC-25) and a weight-loss calorie floor of 1,200 kcal
  for women and 1,500 for men (DEC-24). 10 of the baseline's 72 plans meet the
  targets. That work (#27) is merged. The baseline also runs five guardrail
  cases (fallback and refusal) on a controlled corpus, reported apart from the
  72 plans (#28, merged).
- 2026-10-18: per-ingredient portion balancing toward AMDR (DEC-26) lifts the
  baseline to 41 of 72 plans meeting the targets. It never changes the meal or
  its ingredients. `scipy` is now a direct dependency (#29, merged).
- 2026-10-18: only relevance to the craving, without the profile's bonus,
  decides whether the corpus has a match (DEC-27). Off-menu cravings now fall
  back with a warning; 47 of 72 meet the targets, 36 of the 61 matched as
  before. Macro-aware selection was measured and ruled out: it only helps by
  serving a less relevant meal (#30, merged).
- 2026-10-18: the six recipes with no fat source get 10 g of cooking oil, and
  a balance that misses after rounding is retried 2 points inside AMDR (DEC-28). 72 of 72 meet the targets,
  all 61 matched plans included, with no meal or plan status changed (#31, merged).
- 2026-10-19: the Streamlit demo and the React dashboard show each plan's
  macro split, whether it met the targets or was rebalanced, its calorie
  target, and a notice when an off-menu craving fell back to a standard meal.
- 2026-10-21: the owner approved the React showcase design (`docs/8_design.md`,
  DEC-29; #33 merged). It is built in six slices; the first adds the "Kitchen
  green" Tailwind tokens, self-hosted fonts and the brand bar.
- 2026-11-04: eleven recipes get a carb or fat they plausibly hold, and plant
  milks and nut butters no longer read as dairy (DEC-30). The wider recipe
  check (`--wider`) meets the targets in 68 of 68, up from 49; the baseline
  stays 72 of 72. The corpus has no low-carb meal now.
- 2026-11-07: gluten limits now swap soy sauce for coconut aminos (DEC-31). 72 of 72
  still meet the targets; the median calorie deviation rounds to 0.4%.
- 2026-11-07: Alembic migrations replace `create_all` (P2, DEC-32). A pre-G4
  database is now upgraded with its records instead of being refused.
- 2026-11-22: the meal request takes today's workout (P5, DEC-33). A rest day
  adds no exercise; leaving it out keeps the 30-minute default.
- 2026-11-22: diet rules read `data/reference/ingredient_allergens.json`, not
  ingredient names (P6, DEC-34). A new ingredient must be tagged there; an
  untagged one is refused under any diet rule.
- 2026-11-22: the corpus holds 76 recipes (P7, DEC-35); the wider check meets
  the targets for 152 of 152. New ingredients use estimated nutrition until a
  USDA run (P4).
- 2026-11-22: the workout check (`meal_quality_baseline.py --workouts`, 144 plans,
  six stated workouts per profile) meets the targets for 143 of 144. Workouts past
  the model's 30-minute training range now count per minute (DEC-39), and a stated
  workout or rest day replaces the activity level's exercise (DEC-40, Mike's choice).
  A workout left out keeps the activity level plus the 30-minute default.

- 2026-11-22: React is the main app and Streamlit the backup demo (DEC-37). React is
  now a kitchen app: home, plan page with Viridis charts and runners-up, save and
  rate, My meals, Past plans, and a profile remembered on the device (DEC-36). Spec
  and plan are in `docs/superpowers/`.
- 2026-11-22: every React colour lives in `frontend/src/theme/tokens.js`, and icons
  render through one `Icon` component (DEC-38). A guard test fails on raw hex, stock
  Tailwind colours or a stray Lucide import. The frontend has 233 tests.
- 2026-11-22: the API is live on Cloud Run (GCP free tier, project
  `ai-meal-planner-515508`, australia-southeast1), deployed by `deploy.yml` with
  its live check passing. `GCP_MAX_INSTANCES=1` caps it at one instance (#52), and
  a billing budget of about A$1 alerts the owner. A full `POST /generate-meal-plan`
  trace with all five stage spans reached Cloud Trace. G6's two-instance and
  revocation runs (`docs/6_deployment.md` §3) have not been run on the real service.
- 2026-11-22: `docs/9_dietitian_review_and_user_tests.md` plans P9's people work: a
  dietitian checklist of every diet rule, then a five-to-eight-person usability test.
  Neither has run; ethics approval is to be checked with the supervisor first.
- 2026-11-23: the benchmark runs on USDA data with `--usda` (P4, DEC-41), apart from the
  deterministic offline baseline. USDA energy is now read in kcal, not kJ. With USDA, 50 of 72
  meet the targets and all 72 are within 10% of calories; the misses come from USDA's top
  search hit being the wrong food (`docs/7_meal_quality.md` §6).
- 2026-11-23: corpus ingredients are looked up in USDA by a reviewed FDC ID
  (`data/reference/usda_fdc_ids.json`, DEC-42); a new ingredient must be pinned there
  unless it is a trusted local value. On USDA data 72 of 72 meet the targets and 144 of
  152 in the wider check (`docs/7_meal_quality.md` §7).

- 2026-11-23: user accounts (DEC-43, Mike's choice): Firebase Auth with Google and
  anonymous sign-in, Firestore and Firebase Hosting, on free tiers. Spec
  `docs/superpowers/specs/2026-11-22-user-accounts-design.md`, built in five slices. Slice 1:
  the API accepts a Firebase ID token as `Authorization: Bearer` (`FIREBASE_PROJECT_ID`) and
  acts only for the token's uid, in the `accounts` namespace. Slice 2: `STORAGE_BACKEND=firestore`,
  whose contract tests run on the Firestore emulator in CI. Slice 3: `GET`/`PUT /me/profile` and
  `DELETE /me`, and a hosted deployment on Firestore keeps history (`history_enabled`).

## Open risks

- `.streamlit/secrets.toml` is now gitignored (PR #7). Local
  `database/meal_history.json` still holds 75 records, most of them likely
  synthetic. On 2026-11-21 the owner chose not to import them; they are not in
  any database.
- Storage defaults to `STORAGE_BACKEND=sqlite` and starts empty; JSON history
  is invisible until `scripts/migrate_json_to_sqlite.py` runs, which skips
  records already stored. Alembic owns the schema and upgrades at startup
  (DEC-32). That suits one SQLite file per instance; Postgres should revisit it.
- `ProfileNotFound` (404, `profile_not_found`) is raised by `GET /me/profile` for an account
  with no saved profile (DEC-43). The others:
  - `NutritionProviderError` (502, code `unverified_required`) only when
    `REQUIRE_VERIFIED_NUTRITION` is on and an ingredient is estimated. It is off
    by default;
  - `RetrievalUnavailable` (503) when no fallback template is safe and the
    retriever never loaded;
  - `NoFeasibleMeal`, only when the corpus and the fallback templates are both
    exhausted. It is an internal signal: `MealPlanningService` turns it into a
    successful response with `plan_status: "infeasible"`, so it never reaches
    HTTP as a 422.
- **In hosted mode the React "My meals" and "Past plans" links stay visible.**
  Opening them shows a notice instead of history, and a 501 on save or rate hides
  those controls. React cannot call a keyed production API in v1 anyway (DEC-8).
- **G4 limits, by design.**
  - The rate limit is per instance, so N instances allow N times the limit.
  - Open local mode (no `API_KEYS`) is unauthenticated, though production
    refuses to start in it.
  - The React dashboard cannot call a keyed API in v1.
- **Only sampled requests are traced.** The app continues Cloud Run's `traceparent`,
  so a request is traced only when Cloud Run samples it or the caller sends a sampled
  one. One span batch was lost to an export timeout on 2026-11-22, likely while CPU
  was throttled between requests.
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
