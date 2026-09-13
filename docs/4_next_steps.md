# Next Steps

Everything not yet built, in priority order, consolidated from one place so there is
no second backlog to keep in sync. Sources: the design spec §6–§9 (phases), the
Later Scope list formerly in [`1_brief.md`](1_brief.md), the Current-to-Target
Migration list formerly in [`0_coding_standards.md`](0_coding_standards.md), the
README roadmap, and the spec's §12 out-of-scope list. Overlapping entries have been
merged; each item appears exactly once, in the highest-priority section that claims
it.

Status as of 2026-09-14: Phases 0–3 (tooling, CI, standards, backend architecture,
storage, tests and CI) are done. Phase 4 is split into 4a and 4b: **Phase 4a
(the React decomposition) is done**; **Phase 4b (the matching Streamlit split)
is planned but unstarted**. 222 backend tests and 35 frontend tests pass;
backend coverage is 91%, floor 89%; the meal corpus holds 34 templates.

Sections §1–§4 are committed work with a written design. §5 tracks structural moves
those phases do not cover. §6 is product backlog with no phase yet. §7 is the
deliberate gaps — known and accepted, not overlooked.

## 1. Phase 1 — Backend architecture — **DONE 2026-09-11**

Delivered on `refactor/phase-1-backend-architecture`: the orchestrator and calorie
wiring, the reconciliation loop, the dual-import and dead-code removal, the shared
schema module, reference-data extraction, typed exceptions, the DI container, the
router split, and response models on all eight endpoints. 19 tests at the start of
Phase 0, 57 now. The items below are kept for traceability.


[Spec §6](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
~~Highest priority: `/generate-meal-plan` does not consume the trained calorie model.~~
**Resolved 2026-09-11.** `/generate-meal-plan` now routes through
`MealPlanningService`, which calls `CalorieExpenditureAgent` and passes
`meal_calorie_budget_kcal` to the recommendation agent; the meal agent's own
`calculate_bmr` is deleted. Verified live: the response reports
`model_version: hist_gradient_boosting_deep_v0.1.0` and the meal plan's
`caloric_target` equals the agent's budget.

1. **Wire the calorie model into meal planning.** `/generate-meal-plan` calls
   `CalorieExpenditureAgent` through a new `services/meal_planning_service.py` and
   passes `meal_calorie_budget_kcal` to the recommendation agent.
   `MealRecommendationAgent.calculate_bmr` is deleted and its Mifflin-St Jeor logic
   moves into the calorie agent as the no-model fallback, where estimating
   expenditure belongs. *Supersedes the README roadmap item "connect
   `/generate-meal-plan` more tightly with `/calorie-expenditure/predict`".*
2. **Done (Phase 1).** **Reconciliation loop.** The orchestrator compares the
   portion-scaled estimate against the verified total and rescales portions once
   if the deviation exceeds a configurable tolerance (default 15%), reporting
   `reconciliation` metadata. Exactly one retry. This was Workflow steps 5–6 of
   [`1_brief.md`](1_brief.md); delivered as `_reconcile` in
   `services/meal_planning_service.py`.
3. **Delete the dual-import block** in `main.py:11-40` — Phase 0 packaged
   `backend` with hatchling, so `from backend.app...` now always resolves and the
   fallback is dead weight.
4. **DI container** (`core/container.py`), built in a FastAPI `lifespan` handler and
   injected via `Depends()`. This is the change that makes endpoint testing possible
   at all, so it gates Phase 3.
5. **Split `main.py`** into `api/routes/{health,meal_plans,calories,feedback}.py`.
6. **`schemas/responses.py`** with `response_model=` on all 8 routes, so `/docs`
   shows real contracts instead of `dict[str, Any]`.
7. **Deduplicate shared models** into `schemas/common.py`: one `AgentMetadata`, one
   confidence-averaging helper.
8. **Typed exceptions** in `core/exceptions.py` with a FastAPI handler, so a provider
   failure returns an appropriate status and no internal detail in the body.
9. **Extract reference data** to `data/reference/*.json`, loaded once at startup.
   Agents keep the logic and lose the hard-coded tables.
10. **Delete dead code**, and either use or remove the empty `ml/` package.
11. **Google-style docstrings** on every public class and function in each module
    this phase touches.

## 2. Phase 2 — Storage — **DONE 2026-09-11**

[Spec §7](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
Second because the current single-file JSON store loads everything and filters in
Python, and because the Protocol boundary is what makes Postgres a later config
change rather than a rewrite (DEC-4). The items below are kept for traceability.

1. **`repositories/base.py`** — a `Protocol` per repository: `UserProfileRepository`,
   `MealPlanRepository`, `MealFeedbackRepository`.
2. **JSON implementations retained** for demo mode under `repositories/json_store/`,
   with atomic writes (temp file plus `os.replace`) and the 200/500 record caps
   removed. *Absorbs the migration item "split JSON storage repositories by domain".*
3. **`repositories/sql/`** — SQLModel tables and a SQLite implementation with indexed
   `user_id` lookups, selected by `STORAGE_BACKEND=json|sqlite`, defaulting to
   `sqlite`. *Supersedes the README roadmap item and Later Scope entry "move local
   JSON stores for history, feedback and profiles to a managed database", to the
   extent SQLite satisfies them; Postgres itself stays in §7.*
4. **Done (Phase 2).** `core/config.py` migrated to `pydantic-settings`, replacing
   the hand-rolled `from_env` dataclass. `pydantic-settings` is a separate
   distribution from `pydantic`; Phase 2 added it to `pyproject.toml` and
   `uv.lock` and re-exported `backend/requirements.txt` to match.
5. Schema creation via `create_all`. **Alembic is out of scope** — see §7.1.

## 3. Phase 3 — Tests and CI — **DONE 2026-09-11**

[Spec §8](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
Third because it depends on Phase 1's DI container and Phase 2's Protocol boundary;
running it earlier would test code about to be replaced. Raised backend coverage
82% → 89.98% (214 tests) at Phase 3 completion; a later Codex-review pass added
four more endpoint error-path tests and three more frontend tests, bringing the
current totals to 222 backend tests, 8 frontend tests, and 91% coverage. Also
added the network guard. The items below are kept for traceability.

- **Endpoint tests** for all 8 routes, happy and error path, via `TestClient` with DI
  overrides supplying fake agents. No network access in CI.
- **Repository contract tests** — one suite parameterised over both implementations,
  which is what makes the Phase 2 Protocol boundary load-bearing rather than
  decorative.
- **New unit coverage** for the currently untested: the nutrition agent with mocked
  USDA and FatSecret responses including the per-provider cooldown path, the
  supermarket agent, and `rag/rules.py`.
- **Retained unchanged:** the existing retrieval quality regression tests are the
  guard against RAG changes and must keep passing through every phase. *This is the
  standing migration rule "keep retrieval quality tests updated whenever the meal
  corpus changes", now enforced by CI rather than by memory.*
- **Frontend tests** — `vitest` plus React Testing Library on the API client and one
  test per tab component.
- **Coverage floor** reported in CI, set from the actual post-phase number so the
  floor is honest rather than aspirational.

## 4. Phase 4 — Frontend and Streamlit — **4a DONE 2026-09-14 / 4b open**

[Spec §9](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
Last because both clients consume backend contracts that Phases 1–2 change; doing it
first would mean doing it twice. Split into two sub-phases on `refactor/phase-4a-react`
so the React half (which has no dependency on the Streamlit half) could land first.

- **4a — React, DONE 2026-09-14.** `App.jsx` decomposed 811 → 43 lines into
  `api/client.js`, `api/mealPlanner.js`, `hooks/useAsyncRequest.js`,
  `components/ui/` (ten primitives), three `features/{mealPlan,calories,history}/`
  tabs (with `MealPlanResult.jsx` and `CalorieResult.jsx` split out of the two tabs
  that were still over ~200 lines), and `lib/format.js`, leaving `App.jsx` with
  shell, tab state and routing only. *This is the Later Scope entry "React frontend
  refinement".* Frontend tests 8 → 35; `App.test.jsx`, the phase's regression
  harness, is byte-identical to the phase start. See
  `docs/superpowers/plans/2026-09-14-phase-4a-react-decomposition.md` and the
  2026-09-14 entries in `docs/5_agent_log.md`.
- **4a deferral — no `axios.create()` instance or error interceptor yet.** Spec
  §9 asks `api/client.js` to provide "a single axios instance, `baseURL` from
  env, error interceptor." Only the `baseURL`-from-env half was delivered;
  `api/client.js` exports `API_BASE_URL` and a comment, not an instance. This is
  deliberate, not an oversight: `App.test.jsx` mocks the `axios` module as a bare
  `{ default: { get, post } }` with no `create`, so an `axios.create()` instance
  would bypass that mock and break the byte-identical regression harness that is
  Phase 4a's entire warrant. The consequence is that the `response?.data?.detail`
  extraction an interceptor would centralise is still duplicated once in
  `hooks/useAsyncRequest.js` (serving `MealPlanTab` and `CaloriesTab`) and twice
  inline in `features/history/HistoryTab.jsx`. **Revisit when** the harness's
  axios mock is replaced with something that survives a real instance (for
  example MSW) — at that point add the instance and interceptor, and collapse
  `HistoryTab`'s two inline `detail` extractions into it too.
- **4b — Streamlit, unstarted.** Delete `local_demo_request` and
  `is_meal_like_input`; demo mode calls the same shared agent factory the DI
  container uses, so the demo cannot diverge from the backend (DEC-2). `app.py`
  splits into `app.py`, `api.py`, `demo.py` and `views/`.
- **Done when** no file in `frontend/src` or `streamlit_app` exceeds ~200 lines, the
  deployed Streamlit demo still works with no API server running, and both clients
  still cover meal plan, calorie prediction and history. (React side: met — the
  largest JS/JSX file is `CaloriesTab.jsx` at 174 lines; the largest file of any
  kind is `App.css` at 184 lines. Streamlit side: not yet attempted.)

## 5. Remaining structural moves

From the Current-to-Target Migration list, checked against the working tree on
2026-09-10. The target layout is in [`2_architecture.md`](2_architecture.md) §5.

- [x] **Done (Phase 1).** **Route handlers out of `main.py`** into
      `backend/app/api/routes/` — covered by §1.5; delivered as
      `api/routes/{health,meal_plans,calories,feedback}.py`.
- [x] **Done (Phase 1).** **Agent response models into `backend/app/schemas/`** —
      covered by §1.6–1.7. `schemas/responses.py` now sets `response_model=` on
      all 8 routes. Per-agent payload types (`CalorieExpenditureResponse`,
      `MealPlanPayload`, `MealNutrition`, `SupermarketPayload`) still live beside
      the agents that return them and are composed into `schemas/responses.py`;
      that split is intentional, not a leftover gap.
- [ ] **Extract the USDA and FatSecret clients into `backend/app/services/`** — not
      claimed by any phase, so it is tracked here. Both providers are still called
      from inside `agents/nutrition_verification_agent.py`. `services/` now also
      holds `meal_planning_service.py` (added in Phase 1 for the calorie-model
      wiring), but that is unrelated to this item — no USDA/FatSecret extraction
      has happened. Do this alongside §1 while that agent is already open.
- [x] **Done (Phase 2).** **Split storage repositories by domain** — covered by
      §2.1–2.3. `repositories/storage.py` no longer exists; it is
      `repositories/json_store/repositories.py` (`UserProfileRepository`,
      `MealPlanRepository`, `MealFeedbackRepository`) and `repositories/sql/`.
- [ ] **Reusable calorie-model feature transforms under `backend/app/ml/`** — the
      package is empty. §1.10 decides its fate: populate it or delete it, not leave
      it as an empty promise.
- [x] **Supermarket agent** — the one Later Scope item already delivered;
      `agents/supermarket_agent.py` ships and `/generate-meal-plan` returns a
      shopping list.
- [ ] **Reconcile `docs/agents/supermarket_agent.md` with the implementation.**
      The doc's "MCP Tool Integration" section describes a Mapping API and
      Grocery/Inventory APIs that do not exist in this repo; `_locate_nearest_store`,
      `_map_inventory_and_price` and `_estimate_category_and_price` in
      `backend/app/agents/supermarket_agent.py` are all local reference tables, and
      `maps_api_key` is stored but never used. Either build the MCP-based tooling
      the doc describes, or rewrite the doc to describe the local-reference-table
      implementation.

## 6. Product backlog

Wanted, with no phase assigned. Ordered by how much each improves the product per
unit of work.

- **Improve macro-target balancing, serving-size normalisation and ingredient
  matching.** The highest-value quality work: it makes the plans themselves better,
  independently of any refactor. README roadmap item.
- **Vector database for meal retrieval.** `RAG_BACKEND=auto` already keeps TF-IDF for
  small corpora and switches to sentence embeddings plus FAISS at a configured size,
  so this is only worth doing once the corpus is large enough to trigger it — which
  ties it to the corpus expansion in §7.4. See
  [`architecture/vector_rag.md`](architecture/vector_rag.md).
- **Model registry for calorie expenditure models.** Deferred until there is more
  than one model version to track; today one artifact plus `metrics.json` beside it
  is the honest scale.
- **Audit logging** for profile and plan changes. Named in Later Scope alongside the
  managed database; health-adjacent recommendations are the case for it.
- **User feedback loop for preference learning.** The consuming half — feedback as a
  retrieval ranking feature — is a §7.5 gap; the collection half already works, so
  this is about what the stored signal is used for.

## 7. Acknowledged gaps

Deliberately out of scope, recorded so they are known gaps rather than oversights.
From spec §12.

1. **Alembic migrations — first, and the most consequential.** Phase 2 creates its
   schema with `create_all` and ships no migration path, so the first schema change
   after data exists has no supported route forward. Acceptable only while the data
   is disposable local development state. This must be closed before any deployment
   holds data worth keeping, and before Postgres (§7.3).
2. **Profiles are not stored in SQL.** Both backends return the same built-in
   default; nothing writes profiles at runtime. Real profile storage needs a write
   path and an endpoint, neither of which exists.
3. **The typed domain exceptions are still never raised.** `ProfileNotFound`,
   `RetrievalUnavailable` and `NutritionProviderError` are defined and wired to
   handlers but no production code raises them, so every failure still lands on the
   catch-all 500. Carried from Phase 1's final review.
4. **`deviation_after` falls back to `deviation_before`** when a reconciliation
   retry verifies to 0 kcal, understating the miss. `within_tolerance` stays
   correct.
5. **The 0.65/1.6 clamp and 5 g rounding are duplicated** between `_reconcile` and
   `MealRecommendationAgent._scale_ingredients_to_meal_target`.
6. **`backend/app/ml/` is an empty package.** Spec §6 item 10 said to use or remove
   it; neither happened.
7. **Authentication and user accounts.** The endpoints that take a `user_id` take it on trust.
   Also a README roadmap item; it blocks real multi-user use, which DEC-1 places
   after the portfolio milestone.
8. **Postgres.** Phase 2's Protocol boundary reduces this to a config change plus one
   class, which is exactly why it need not be done now — no current user justifies
   adding managed infrastructure to every dev setup and to CI (DEC-4).
9. **Expanding the meal corpus** beyond its current 34 templates. The README roadmap
   targets 75–100 curated templates. It is content work, not engineering, and it
   gates the vector-database item in §6.
10. **Using feedback signals as retrieval ranking features.** README roadmap item:
    saved meals, likes, dislikes and ratings are collected but do not influence
    retrieval order.
11. **Migrating `requests` to async `httpx`.** The current `run_in_threadpool`
    wrapping is correct, just not idiomatic — so this is a tidiness change with no
    behavioural payoff.
12. **Retraining or improving the calorie model.** The shipped artifact and its
    `scikit-learn==1.6.1` pin stay as they are; §1.1 is about *using* the model, not
    improving it.
13. **`kidney_disease` has no substitution path.** It is the only constraint group
    with block-list entries but no `SUBSTITUTION_RULES` match, so a meal containing
    kidney beans, lentils, chickpeas, tofu or soy sauce is rejected outright for
    those users rather than adapted. This may well be the right conservative
    default — the vegan pattern would swap egg for tofu, and tofu is itself
    kidney-blocked — but it was never written down as intentional. The current
    behaviour is pinned by
    `backend/tests/test_rag_rules.py::test_meal_is_allowed_false_when_kidney_disease_blocked_ingredient_has_no_substitution`,
    so changing it will break a test and force a deliberate decision.
14. **`meal_recommendation_agent.py` is at 72% coverage.** Unlike
    `rag/embedding_index.py` (32%, excused because its sentence-transformers/FAISS
    path sits behind the uninstalled `semantic-rag` optional dependency group), this
    is core business logic with no optional-dependency excuse: 42 statements go
    untested, the largest remaining gap in the backend —
    `agents/meal_recommendation_agent.py:96-97, 100-111, 166-169, 177-183, 204, 213,
    302-322, 355, 392-403`. This is a real remaining gap, not an intentional
    exclusion, and is unassigned to any phase.
15. **Three deliberate deviations from spec §8, found by a Codex review of
    Phases 1–3 and recorded here rather than silently left as gaps:**
    - §8 asks for happy- and error-path tests on all eight endpoints. `GET /`
      and `GET /health` take no input at all, so there is no
      input-validation error path to test for them; "all eight, happy and
      error path" is satisfied for the six endpoints that take input
      (`/generate-meal-plan`, `/calorie-expenditure/predict`,
      `/meal-feedback`, `/meal-plans/{user_id}`, `/meal-feedback/{user_id}`,
      `/saved-meals/{user_id}`).
    - §8 asks for endpoint tests via "DI overrides supplying fake agents."
      `backend/tests/test_api_endpoints.py` instead injects real agents
      backed by temporary repositories (see its `client` fixture). This is a
      deliberate choice, not an oversight: it exercises the real pipeline
      end-to-end, and network isolation is guaranteed by the conftest
      network guard rather than by faking, so it is stronger coverage than
      the spec's letter asks for.
    - §8 asks for frontend tests on "the API client and one test per tab
      component." That ask is now satisfied by Phase 4a (§4): the API layer
      lives in `frontend/src/api/` (`client.js`, `mealPlanner.js`) and is
      covered by `api/mealPlanner.test.js`, and each tab has its own test
      file — `features/mealPlan/MealPlanTab.test.jsx`,
      `features/calories/CaloriesTab.test.jsx`, and
      `features/history/HistoryTab.test.jsx`. `App.test.jsx` still covers the
      end-to-end request/response/error contract at the `App` level (a fired
      `axios.post`, a rendered error banner on rejection, and a rendered plan
      on success); it was the only such coverage before Phase 4a and remains
      unedited as the regression harness now that the per-module tests exist
      alongside it.
