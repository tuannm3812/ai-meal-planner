# Next Steps

Everything not yet built, in priority order, consolidated from one place so there is
no second backlog to keep in sync. Sources: the design spec §6–§9 (phases), the
Later Scope list formerly in [`1_brief.md`](1_brief.md), the Current-to-Target
Migration list formerly in [`0_coding_standards.md`](0_coding_standards.md), the
README roadmap, and the spec's §12 out-of-scope list. Overlapping entries have been
merged; each item appears exactly once, in the highest-priority section that claims
it.

Status as of 2026-09-10: Phase 0 (tooling, CI, standards) is landing now. Phases
1–4 are specified but unplanned. 19 tests pass; the meal corpus holds 34 templates.

Sections §1–§4 are committed work with a written design. §5 tracks structural moves
those phases do not cover. §6 is product backlog with no phase yet. §7 is the
deliberate gaps — known and accepted, not overlooked.

## 1. Phase 1 — Backend architecture

[Spec §6](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
Highest priority: the repository ships a trained calorie model that no user-facing
endpoint consumes, which is a story-level flaw rather than a style one (DEC-3).

1. **Wire the calorie model into meal planning.** `/generate-meal-plan` calls
   `CalorieExpenditureAgent` through a new `services/meal_planning_service.py` and
   passes `meal_calorie_budget_kcal` to the recommendation agent.
   `MealRecommendationAgent.calculate_bmr` is deleted and its Mifflin-St Jeor logic
   moves into the calorie agent as the no-model fallback, where estimating
   expenditure belongs. *Supersedes the README roadmap item "connect
   `/generate-meal-plan` more tightly with `/calorie-expenditure/predict`".*
2. **Reconciliation loop.** The orchestrator compares the portion-scaled estimate
   against the verified total and rescales portions once if the deviation exceeds a
   configurable tolerance (default 15%), reporting `reconciliation` metadata.
   Exactly one retry. This is Workflow steps 5–6 of [`1_brief.md`](1_brief.md),
   currently unimplemented.
3. **Package the backend properly** so `from backend.app...` always resolves, then
   delete the dual-import block in `main.py` — it exists only because it does not.
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

## 2. Phase 2 — Storage

[Spec §7](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
Second because the current single-file JSON store loads everything and filters in
Python, and because the Protocol boundary is what makes Postgres a later config
change rather than a rewrite (DEC-4).

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
4. **`core/config.py` migrated to `pydantic-settings`**, replacing the hand-rolled
   `from_env` dataclass. Pydantic is already a dependency, so this removes code
   rather than adding a dependency.
5. Schema creation via `create_all`. **Alembic is out of scope** — see §7.1.

## 3. Phase 3 — Tests and CI

[Spec §8](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
Third because it depends on Phase 1's DI container and Phase 2's Protocol boundary;
running it earlier would test code about to be replaced.

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

## 4. Phase 4 — Frontend and Streamlit

[Spec §9](superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md).
Last because both clients consume backend contracts that Phases 1–2 change; doing it
first would mean doing it twice.

- **React** — decompose `App.jsx` into `api/client.js`, `api/mealPlanner.js`,
  `hooks/useAsyncRequest.js`, `components/ui/` (eight primitives), three
  `features/{mealPlan,calories,history}/` tabs and `lib/format.js`, leaving `App.jsx`
  with shell, tab state and routing only. *This is the Later Scope entry "React
  frontend refinement".*
- **Streamlit** — delete `local_demo_request` and `is_meal_like_input`; demo mode
  calls the same shared agent factory the DI container uses, so the demo cannot
  diverge from the backend (DEC-2). `app.py` splits into `app.py`, `api.py`,
  `demo.py` and `views/`.
- **Done when** no file in `frontend/src` or `streamlit_app` exceeds ~200 lines, the
  deployed Streamlit demo still works with no API server running, and both clients
  still cover meal plan, calorie prediction and history.

## 5. Remaining structural moves

From the Current-to-Target Migration list, checked against the working tree on
2026-09-10. The target layout is in [`2_architecture.md`](2_architecture.md) §5.

- [ ] **Route handlers out of `main.py`** into `backend/app/api/routes/` — covered by
      §1.5; `backend/app/api/` does not exist yet.
- [ ] **Agent response models into `backend/app/schemas/`** — covered by §1.6–1.7.
      `schemas/` currently holds `requests.py` only; response models still live
      beside the agents that return them.
- [ ] **Extract the USDA and FatSecret clients into `backend/app/services/`** — not
      claimed by any phase, so it is tracked here. Both providers are called from
      inside `agents/nutrition_verification_agent.py`; `services/` exists but holds
      only `__init__.py`. Do this alongside §1 while that agent is already open.
- [ ] **Split storage repositories by domain** — covered by §2.1–2.3.
      `repositories/storage.py` is a single module today.
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
2. **Authentication and user accounts.** The endpoints that take a `user_id` take it on trust.
   Also a README roadmap item; it blocks real multi-user use, which DEC-1 places
   after the portfolio milestone.
3. **Postgres.** Phase 2's Protocol boundary reduces this to a config change plus one
   class, which is exactly why it need not be done now — no current user justifies
   adding managed infrastructure to every dev setup and to CI (DEC-4).
4. **Expanding the meal corpus** beyond its current 34 templates. The README roadmap
   targets 75–100 curated templates. It is content work, not engineering, and it
   gates the vector-database item in §6.
5. **Using feedback signals as retrieval ranking features.** README roadmap item:
   saved meals, likes, dislikes and ratings are collected but do not influence
   retrieval order.
6. **Migrating `requests` to async `httpx`.** The current `run_in_threadpool`
   wrapping is correct, just not idiomatic — so this is a tidiness change with no
   behavioural payoff.
7. **Retraining or improving the calorie model.** The shipped artifact and its
   `scikit-learn==1.6.1` pin stay as they are; §1.1 is about *using* the model, not
   improving it.
