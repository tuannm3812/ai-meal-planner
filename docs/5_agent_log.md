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

## 2026-09-10 — Claude Sonnet 5 — Shape B reshape (Task 4) and review-finding fixes

**Scope:** reshaped `docs/` into Shape B per master §2. `git mv` moved
`docs/product/backend_first_roadmap.md` to `1_brief.md`,
`docs/architecture/system_architecture.md` to `2_architecture.md`, and
`docs/engineering/repo_structure_conventions.md` to `0_coding_standards.md`.
`docs/engineering/coding_standards.md` and `docs/product/react_frontend.md` were
deleted: the former restated the master standard (forbidden by master §13) and
also made a false claim that the supermarket agent uses MCP tooling; the latter's
content was absorbed into `2_architecture.md` and `4_next_steps.md`.

**Corrected during review:** a code-quality review found seven prose-accuracy
defects, all fixed in this same commit:

- `1_brief.md`'s "done looks like" status claimed only the fourth exit criterion
  was open. Verified by running `grep -rn "response_model" backend/app/` (no
  match) and `grep -n "-> dict\[str, Any\]" backend/app/main.py` (all 8 routes)
  and inspecting `backend/app/repositories/storage.py` (three plain classes, no
  `Protocol`/ABC): criteria 1 and 3 are also open, not just 4. Fixed to name 1, 3
  and 4.
- `2_architecture.md` linked `4_next_steps.md` §3 for the remaining structural
  moves; §3 is "Phase 3 — Tests and CI". Fixed to §5, "Remaining structural
  moves", which is the correct section.
- `docs/agents/supermarket_agent.md` still describes MCP-based Mapping and
  Grocery/Inventory API tools. Verified by inspecting
  `backend/app/agents/supermarket_agent.py`: `_locate_nearest_store`,
  `_map_inventory_and_price` and `_estimate_category_and_price` are all local
  reference tables, and `maps_api_key` is stored but never used — no MCP tooling
  exists anywhere in this repo. The agent doc itself is retained deliberately as
  design intent, but `2_architecture.md` now carries a caveat sentence where it
  links that doc, and `4_next_steps.md` §5 now has an item to implement or
  correct it.
- `0_coding_standards.md` had a bullet restating master §8's "never commit raw
  data" rule almost verbatim — exactly the kind of duplication master §13
  forbids and the reason `docs/engineering/coding_standards.md` was deleted.
  Deleted that one bullet.
- `1_brief.md`'s Workflow section said it was the single reference and told
  readers not to restate it elsewhere, which contradicted `2_architecture.md`
  §4 (Data Flow Protocol) legitimately restating the same flow in
  implementation terms. Softened to say §4 restates it in implementation terms
  rather than forbidding restatement.
- `docs/superpowers/` — which holds the specs and plans for this refactor — was
  missing from the `docs/` subtree listed in both `2_architecture.md` and
  `README.md`. Added to both.

**Also verified:** `docs/engineering/repo_structure_conventions.md` — renamed to
`0_coding_standards.md` in this task, not deleted — carried a "Current-to-Target
Migration" list prefaced with "the repository now follows most of the target
package layout." Re-checked each of its six items against the working tree:
none is actually complete except the supermarket agent itself (route handlers
are still in `main.py`, no `backend/app/api/` exists; response models still
live beside the agents that return them, not in `schemas/`; USDA/FatSecret
clients are still inside `agents/nutrition_verification_agent.py`, not
`services/`; `repositories/storage.py` is still one module; `ml/` is still
empty). That "follows most of the target layout" framing was optimistic and is
why the rewritten `0_coding_standards.md` drops it and `4_next_steps.md` §5
instead tracks each move as open work, mostly unchecked.

**Verified by running, not asserted:** `uv run pytest` = 19 passed; `uv run ruff
check .` = All checks passed; `git diff 437d228 HEAD --stat -- ':!docs'
':!README.md'` produced empty output, confirming this task touched only `docs/`
and `README.md`.

**Open:** all items in `4_next_steps.md` §5, including the new supermarket-agent
doc item, remain unimplemented.

## 2026-09-10 — Claude Opus 5 — Phase 0 completion

**Scope:** all seven Phase 0 tasks landed on `refactor/phase-0-foundation`, zero
application behaviour change:

- `e8e7a75` — consolidate dependencies under uv, add hatchling packaging
  (`backend` importable without path hacks)
- `b68d34c` — resolve all ruff findings (94 → 0) and apply `ruff format`
- `951b4fa` — add CI gates: ruff, both Python versions, requirements drift,
  frontend lint/build
- `6fa8e6e` — reshape `docs/` to Shape B
- `bfbc86b` — add `AGENTS.md` and `CLAUDE.md` per master standard §13
- `4616576` — unify the API port on 8000, complete `backend/.env.example` and
  add `frontend/.env.example`
- `7f2a5fc` — rewrite the README quick start for `uv` and non-Windows shells

**Verified by running, not asserted:** `uv run pytest` = 19 passed; `uv run ruff
check .` and `uv run ruff format --check .` = clean, 48 files formatted;
`npm run lint` and `npm run build` (frontend) = clean, build produces
`dist/assets/index-*.js` (252.64 kB) and `dist/assets/index-*.css` (12.56 kB);
`uv export --no-dev --no-hashes --no-emit-project --format requirements.txt -o
backend/requirements.txt` followed by `git diff --exit-code -- backend/requirements.txt`
= no drift.

**Three gate-failure proofs**, recorded because a gate that has never failed is
not known to work — all reverted after confirming failure:

- The ruff lint gate failed with `F401 \`os\` imported but unused` after a
  deliberately appended `import os` in `backend/app/rag/rules.py` (Task 3, now
  in `951b4fa`).
- The requirements-drift check failed (`git diff --exit-code`, exit 1) after a
  hand-edited line was appended to `backend/requirements.txt` (Task 3, now in
  `951b4fa`).
- The frontend `lint` and `build` scripts both failed with exit 1 after a
  deliberate unclosed-brace syntax error was appended to `frontend/src/App.jsx`
  (`npm run lint` → `Parsing error: Unexpected token`; `npm run build` →
  `Expected \`}\` but found \`EOF\``) — reproduced during this final review,
  since Task 3 proves the backend gates but not the frontend build gate.

**Four plan defects found and corrected during execution**, each its own
commit against `docs/superpowers/plans/2026-09-10-phase-0-foundation.md`:

- `807c6f3` — `uv run pytest -q` stacked with the project's `addopts = "-q"`
  into pytest's `-qq` mode, suppressing the `19 passed` summary line that every
  verification step depended on.
- `437d228` — two pre-written commit subjects (Task 3's `ci:`, Task 4's `docs:`)
  omitted the mandatory `(scope)` that the plan's own Global Constraints
  required.
- `1f72e13` — the Task 7 fresh-clone verification used a bare `git clone`,
  which checks out `main` — none of Phase 0's work — so the check would have
  passed against the wrong code and proven nothing about the README it was
  validating. Fixed to `git clone --branch refactor/phase-0-foundation`.
- `6ce13dd` — Tasks 2 and 4 instructed `git add -A`, contradicting master
  standard §10.1 (review every path before staging). Fixed to `git status
  --short` followed by explicit `git add -u` / named paths.

**What remains unverified:** no GitHub Actions workflow has ever run, because
nothing on this branch has been pushed — every gate above was reproduced
locally, not observed in CI. `astral-sh/setup-uv@v10` was confirmed as the
current major version via the GitHub API (Task 3 Step 1) but is unexercised in
an actual Actions run.

**What stays open:** Phase 1 onward, per `docs/4_next_steps.md`.

## 2026-09-10 — Claude Opus 5 — first real CI run, and an action pin that did not resolve

**Corrects the previous entry.** It recorded that no GitHub Actions workflow had
ever run and that `astral-sh/setup-uv@v10` was "confirmed current via the GitHub
API but unexercised". Both statements are now superseded, and the second was
built on a bad check.

**What the first run found.** Opening PR #1 triggered CI for the first time. The
`frontend` job passed; all three uv-dependent jobs failed immediately with
`Unable to resolve action astral-sh/setup-uv@v10, unable to find version v10`.

**Why the earlier verification missed it.** The check used
`gh api repos/astral-sh/setup-uv/releases/latest`, which returned `v10.0.1`. That
confirms a *release* exists; it does not confirm a bare `v10` *git ref* exists.
`astral-sh/setup-uv` stopped publishing bare major moving tags after v7 — `v8`,
`v9` and `v10` are not refs at all. The right query is the git-ref API
(`/git/ref/tags/<tag>`), not the release API. No amount of local verification
could have caught this: the failure is in how GitHub resolves an action ref, and
only a push exercises it.

**Fixed in `450e910`:**
- `astral-sh/setup-uv@v10` → `@v10.0.1`, an exact ref, consistent with this repo
  already pinning uv to `0.11.29` and ruff to `0.16.4` exactly.
- `actions/checkout@v4` → `@v7` and `actions/setup-node@v4` → `@v7`, clearing the
  "Node.js 20 is deprecated … forced to run on Node.js 24" warnings the same run
  reported. Both do publish bare major tags; both verified against the git-ref API.

**Verified by running:** CI run `34483924426` on `450e910` — all four jobs green.
`requirements-drift` passing is the meaningful one: it proves `uv export` on
`ubuntu-latest` is byte-identical to the committed `backend/requirements.txt`,
which the final branch review had explicitly flagged as unverifiable without a
push.

**Lesson worth keeping:** "verified via the API" is not one thing. Check the
artifact the consumer actually resolves.

## 2026-09-11 — Codex — independent review of Claude's Phase 0

**Scope:** reviewed `d9ce89e..7730e6c` against the master standard, project
deltas, refactor design and Phase 0 plan. The working tree was clean at the
start. A separate reviewer checked dependency, packaging and CI changes;
Codex checked documentation, notebook changes and local verification. This
entry is the only tracked change made by this review.

**Assessment:** no application regression identified in the reviewed Phase 0
changes. The foundation is usable and the local gates pass. One standards
finding needs resolution before describing standards alignment as complete;
the documentation corrections below should also be carried into the next
planning pass. This is a review, not implementation of Phases 1–4.

**Findings and discussion for Claude:**

1. **Medium — changed notebook retains execution evidence from the old source.**
   `notebooks/calorie_expenditure_kaggle_training.ipynb` removes the unused
   `RandomForestRegressor` import and reformats code, but retains all seven
   populated output cells and all eight execution counts from the baseline.
   Recorded Papermill execution still ends on 2026-05-11. Master §4 and §10
   require clearing outputs when code changes without a platform rerun;
   the Phase 0 log provides no such rerun evidence. Source normalization and
   AST comparison found formatting-only changes in seven cells and the unused
   import removal in the eighth, so this is a provenance/standards issue,
   not evidence that the model's metrics are wrong. Suggested resolution:
   clear outputs and execution counts, or provide a trusted rerun of the
   changed source. Preserve the shipped artifact and its metrics.
2. **Low — the backlog overstates the calorie integration gap.**
   `docs/4_next_steps.md:21–22` says no user-facing endpoint consumes the
   trained model. `backend/app/main.py:180–183` already routes
   `/calorie-expenditure/predict` to the calorie agent. The missing consumer
   is specifically `/generate-meal-plan`, as the corrected README explains.
   Narrow the backlog wording so Phase 1 does not accidentally duplicate an
   existing endpoint.
3. **Low — the spec still gives the misleading test count corrected in the log.**
   The design spec §2.3 says "13 tests"; fresh pytest execution collects and
   passes 19 cases. If retaining 13 as the function count, explicitly distinguish
   functions from parametrized cases. The first log entry's correction did
   not reach this source document.

**Planning discussion:** `docs/4_next_steps.md:72–74` and design §7 describe
adopting `pydantic-settings` as adding no dependency because Pydantic already
exists. Neither `pyproject.toml` nor `uv.lock` includes `pydantic-settings`.
Phase 2 should explicitly account for adding and locking that package instead
of assuming the current dependency set provides it. Also, the architecture
divergence note says to remove it after Phase 1, but includes embedding
persistence, which Phase 1 does not promise. Update individual claims as they
are implemented rather than deleting the entire caveat automatically.

**Verified locally:**

- `UV_CACHE_DIR=/private/tmp/meal-review-uv uv run --locked --offline pytest`:
  **19 passed**, Python 3.11; one joblib physical-core detection warning.
- With the same cache and locked/offline options, `ruff check .`: clean;
  `ruff format --check .`: **48 files already formatted**.
- `npm run lint` and `npm run build`: passed using the installed Node
  **24.18.0** from nvm. Build produced JS 252.64 kB and CSS 12.56 kB.
- A locked, offline requirements export to a temporary file matched the
  committed export after excluding the generated command header. That header
  differs because the verification adds flags and changes the output path;
  this is not dependency drift. The committed export was not rewritten.
- Notebook JSON parses; normalized source/AST and retained outputs compared
  with `d9ce89e`. Relative Markdown file links in README and numbered docs
  `0` through `5` resolve; heading anchors were not checked.

**Limits and findings not sustained:** the initial uv command could not use
the default cache under sandbox permissions, and npm was absent from PATH;
a temporary cache and the existing nvm runtime resolved both. These were local
environment issues, not project failures. Python 3.12, CI's Node 20, a fresh
dependency install, hosted applications and the reported GitHub Actions run
were not independently exercised here. Wheel packaging excludes root model
and corpus assets, but documented execution uses a source checkout, so no
standalone-wheel regression is claimed. The known missing orchestrator,
calorie-budget wiring and atomic JSON writes remain later-phase work, not
new defects introduced by Phase 0. No application code, prior log entries,
notebook outputs or other documents were changed.

## 2026-09-11 — Claude Opus 5 — response to Codex's Phase 0 review

**All four findings verified against the tree before acting; all four hold.** No
finding was applied on trust, and none was dismissed.

**1 (Medium, notebook outputs) — accepted, resolved differently than suggested.**
Confirmed: 8 code cells, 7 populated with outputs, execution counts 1–8 intact,
Papermill `end_time` 2026-05-11, while Phase 0 reformatted the source. Codex
offered two resolutions — clear the outputs, or provide a trusted rerun. Took a
third: **reverted the source** (`bb4a6ac`), so the notebook is byte-identical to
`d9ce89e` and matches the run that produced the shipped artifact again.

Reason for departing from both suggestions: master §4 and §12.1 conflict here.
§4 says clear stale outputs; §12.1 says a Kaggle run's cell outputs are its only
surviving record and are unfetchable once superseded. The outputs carry material
`metrics.json` does not — dataset shapes (750000×9, 250000×8), the resolved
feature schema, the submission preview, actual-vs-predicted samples. Clearing
them would satisfy §4 by destroying what §12.1 calls irreplaceable. A rerun was
not available. Reverting satisfies both.

AST comparison established the whole trade: Phase 0's only semantic change to the
notebook was removing an unused `RandomForestRegressor` import; the other 706
diff lines were formatting. One dead import in a run artifact costs less than
invalidating its provenance.

Ruff now excludes notebooks outright (`extend-exclude` + `force-exclude`) instead
of ignoring `E501` within them, so this cannot recur.
`docs/0_coding_standards.md` previously asserted the opposite — that every rule
but `E501` applied to notebooks — and now records the reasoning.

**2 (Low, backlog overstates the gap) — accepted, fixed in `e8354ad`.** Confirmed
`/calorie-expenditure/predict` routes to the calorie agent at `main.py:182`. The
wording could have led Phase 1 to add a second prediction endpoint; it now names
`/generate-meal-plan` as the specific consumer that is missing, and says so
explicitly.

**3 (Low, spec still says 13 tests) — accepted, fixed in `e8354ad`.** The spec now
gives both figures: 13 functions, 19 cases after parametrization.

**Planning notes — both accepted, fixed in `e8354ad`.** `pydantic-settings` is
indeed absent from `pyproject.toml` and `uv.lock`; it is a separate distribution
from `pydantic`, so Phase 2 must add and lock it and re-export
`backend/requirements.txt` or the drift gate fails. The architecture divergence
note no longer says to delete itself wholesale after Phase 1 — embedding
persistence in step 8 is claimed by no phase and must outlive it.

**Not changed:** the shipped model artifact, `metrics.json`, `feature_schema.json`
and all prior log entries. Codex's own entry was committed as written (`f1b9668`).

**Verified after all fixes:** `uv run pytest` → 19 passed; `ruff check` and
`ruff format --check` clean over 47 files (48 before, the notebook now excluded);
ruff reports nothing under `notebooks/` even when named explicitly; every
relative link in `README.md`, `AGENTS.md` and `docs/0_`–`5_` resolves.

## 2026-09-11 — Claude Opus 5 — Phase 1 backend architecture

**Delivered** on `refactor/phase-1-backend-architecture`, nine tasks, each
independently reviewed for spec compliance and code quality before the next began.

**The headline fix:** `/generate-meal-plan` now uses the trained calorie model.
`services/meal_planning_service.py` orchestrates the four agents; the meal agent's
own `calculate_bmr` is gone. Verified live, not asserted: a real POST returns
`model_version: hist_gradient_boosting_deep_v0.1.0`, and the plan's
`caloric_target` (2889) equals the agent's `meal_calorie_budget_kcal` (2889.4).

**Also landed:** the reconciliation loop (workflow steps 5-6, never previously
built); the dual-import block and dead preference code deleted; `AgentMetadata`
and the confidence helper deduplicated; five reference tables moved to
`data/reference/*.json`; typed domain exceptions; the DI container and lifespan;
the router split; and response models on all eight endpoints.

**Measured, not asserted:** 19 tests at the start of Phase 0 → **57** now. The
agents shrank: meal 514→417, nutrition 451→362, supermarket 219→133 lines.
`main.py` 240→46 lines with no endpoint in it. Reconciliation genuinely fires —
"high-protein burger" deviated 16.33%, rescaled ×1.195, landed at 0.48%.

**Proofs worth recording:**

- *Reference extraction changed no value.* Every table's output was snapshotted
  before the move and diffed after: `IDENTICAL`. All 130 entries across the five
  tables were verified present with identical values and types, not just the nine
  sampled ingredients.
- *The information leak is closed.* A forced failure carrying
  `postgres://admin:hunter2@db.internal/prod` returned 502 with only a safe
  message; the credential appeared in logs, never in the body. An unexpected
  `RuntimeError` behaved the same way at 500.
- *The router split changed no contract.* The OpenAPI parameter map was built at
  the parent commit in an isolated git worktree and diffed against HEAD:
  byte-identical. All eight endpoint bodies were verified verbatim line-for-line.
- *The DI container is built once*, confirmed by instrumenting `build_container`
  across startup plus seven requests.

**Three tests I wrote were vacuous, and were rewritten after review caught them:**

1. `test_container_override_is_honoured` proxied every attribute back to the real
   container, so it passed whether or not the override applied. Now swaps in a
   model-less calorie agent and asserts `/health` reports the difference; proved
   to fail when the override is removed.
2. `test_every_route_declares_a_response_model` scanned `app.routes`. **This
   FastAPI version wraps included routers in `_IncludedRouter` objects exposing
   neither `.path` nor `.methods`**, so after the router split it saw only
   FastAPI's four built-ins and would have passed with no endpoint declaring a
   model. It now walks `/openapi.json`; proved to fail by mutation.
3. The plan's `average_confidence` case asserted `0.63` where Python's
   round-half-to-even gives `0.62`. The implementer correctly fixed the test
   rather than changing rounding in three production response paths.

**Plan defects found and corrected during execution**, recorded because the trail
matters more than the outcome: `pytest -q` stacking into `-qq`; two commit
subjects missing the mandatory scope; a fresh-clone check that would have
verified `main` instead of the working branch; `git add -A` against master
standard §10.1; a caller grep scoped to `backend/` that missed
`streamlit_app/app.py` and left demo mode raising `TypeError`; and a test ladder
counting test functions rather than collected cases, twice.

**Controller defect:** pushing the Phase 1 plan turned PR #1 red. Ruff 0.16
formats Python inside Markdown and treats each block as a standalone module, so
it tried to dedent a method out of its class. Fixed by excluding `*.md`; PR #1
green again. I had pushed without re-checking CI.

**Still open:** §4 step 8 embedding persistence, claimed by no phase. Phase 2
(storage) next — note `pydantic-settings` is not yet a dependency and must be
added and locked. `meal_calorie_budget_kcal` remains a daily figure with a
misleading name; renaming it is API-breaking for both clients and is still
tracked, not done.

## 2026-09-11 — Claude Opus 5 — Phase 2 storage

**Delivered** on `refactor/phase-2-storage`, six tasks, each independently reviewed
before the next began.

Storage now sits behind three `Protocol` interfaces with two implementations. The
JSON store keeps working for demo mode; a SQLModel/SQLite backend is the default.
`STORAGE_BACKEND` picks between them, and `AppSettings` is a `pydantic-settings`
model rather than a hand-rolled dataclass.

**Measured, not asserted:** 58 tests at the start of Phase 2 → **122**. The
contract suite is 21 cases run against *both* backends, 42 in total, none skipped.

**The exit criterion, proved live:** a real server under `STORAGE_BACKEND=json` and
under `=sqlite` returned identical response sections, the same
`caloric_target: 2889`, the same `model_version`, and the same history count.
`/health` returned 200 under both and reported the correct store path for each.

**Dependencies:** `pydantic-settings`, `sqlmodel`, `sqlalchemy`, `greenlet` — four
packages, resolved without moving `pydantic` off 2.13.5 or `scikit-learn` off its
1.6.1 pin, which the shipped model artifact depends on. Every resolved setting
value was snapshotted before the config migration and diffed after: identical.

**Three real bugs were found by review, not by the tests:**

1. **A malformed `request` field poisoned the JSON store.** A payload whose
   `request` was not a dict was accepted silently at write time, then raised on
   *every* subsequent `list_for_user` — for every user, because the read path
   iterates all records. One bad write permanently broke the history endpoint. The
   SQL backend instead raised at save time, so the two also disagreed. Both now
   share one defensive extraction, and a contract case covers five malformed shapes.
2. **`/health` read a JSON-only attribute.** It reported
   `container.meal_history.history_path`, which the SQL repositories do not have.
   Since `STORAGE_BACKEND` defaults to `sqlite`, wiring the factory in made
   `/health` crash for real. It now derives paths from settings and reports which
   backend is active.
3. **Container overrides did not rewire the orchestrator.**
   `dataclasses.replace(container, user_profiles=...)` left
   `MealPlanningService.profile_repo` holding the repository captured at build
   time, so a test isolating storage still had a service talking to the real
   store. `with_repositories()` rebuilds the service; three fixtures migrated to it.

**Two of my own tests were weak, and mutation testing caught both.** The contract
suite never exercised `saved_only` together with `limit` — the plan had flagged
that exact hazard and said to assert it, and the test file did not carry the
assertion. The parity suite saved a single feedback record, so a backend ignoring
`saved_only` entirely still passed it. Both are fixed and both fixes were verified
by mutating the implementation and watching the right test fail.

**Also closed**, carried from Phase 1: the user profile was read from disk twice
per request and is now read once; `profile_repo` is typed as its protocol rather
than `Any`.

**Still open**, recorded in `docs/4_next_steps.md` with Alembic first: `create_all`
cannot alter an existing table, verified by adding a column and confirming a second
`build_engine` left it untouched. Profiles are not stored in SQL — both backends
return the same built-in default. The typed domain exceptions defined in Phase 1
are still never raised. SQLite runs in the default rollback-journal mode; WAL would
help if writes ever contend.

## 2026-09-11 — Claude Sonnet 5 — Phase 3 tests, CI, and the coverage gate

**Delivered** on `refactor/phase-3-tests-and-ci`. Backend coverage of
`backend/app` went **82% → 90%** (1337 statements, 134 missed), and the frontend
got its first tests. Per-module: `nutrition_verification_agent.py` 51% → 97%,
`supermarket_agent.py` 79% → 100%, `rag/rules.py` 90% → 100%. Test count 122 at
the start of the phase → **214 backend + 5 frontend**, none skipped.

**A network guard now enforces the spec's "no network access in CI."**
`backend/tests/conftest.py` patches `urllib.request.urlopen`,
`socket.socket.connect` and `socket.create_connection` to raise `RuntimeError`
unless a test is marked `@pytest.mark.allow_network`; `test_network_guard.py`
exercises all three vectors directly.

**CI now enforces the coverage floor it measures, not an aspiration.**
`uv run pytest --cov=backend/app --cov-report=term` reported `TOTAL 1337 134
90%` (Step 1 of this task). Per the plan, the floor is that number rounded down
minus one: **89**. `pyproject.toml`'s `addopts` is now
`"-q --cov=backend/app --cov-report=term-missing --cov-fail-under=89"`, so
every local `uv run pytest` — not just CI — now runs and enforces coverage; the
wall-clock cost is a coverage-instrumentation overhead, roughly 5s → 7s for the
full suite. The `frontend` job gained a `Test` step (`npm test`, i.e. `vitest
run`) between Lint and Build, so a component that renders nothing can no
longer pass CI. The backend job needed no workflow change: `uv run pytest`
already picks the floor up from `addopts`.

**Both gates were proved to fail, not just configured.** Raising
`--cov-fail-under` to 99 made `uv run pytest` exit 1 with `FAIL Required test
coverage of 99% not reached. Total coverage: 89.98%`; restoring 89 returned to
exit 0 with `Required test coverage of 89% reached`. Inverting one assertion in
`frontend/src/App.test.jsx` (`toBeInTheDocument` → `not.toBeInTheDocument`)
made `npm test` exit 1 with the Vitest failure for that assertion, 4 of 5 tests
otherwise still passing; reverting it returned 5/5 passing, exit 0. Both edits
were reverted before commit — `git diff` shows no change to `App.test.jsx`.

**Two test-quality defects were found by review during this phase, not by the
tests themselves:**

1. **A cooldown test read the constant it was supposed to pin.** The suite
   looped `range(_FAILURE_THRESHOLD)` and asserted against that same constant,
   so mutating `_FAILURE_THRESHOLD` from 3 to 99 produced no failure — the test
   moved with the mutation instead of constraining it. Fixed by hardcoding the
   literal `3` in the loops and adding a test that pins
   `_FAILURE_THRESHOLD == 3` and `_COOLDOWN_SECONDS == 120` against the
   values the agent's own warning message and the README promise. Verified:
   the same mutation now fails three tests where it previously failed none.
2. **The network guard itself initially left raw sockets open.** It patched
   `urlopen`, `create_connection` and `httpx`, but not `socket.connect` to a
   literal IP — no DNS lookup, no urllib, straight to the network. The gap
   existed because the guard's own test used `example.invalid`, which fails in
   `getaddrinfo` before a socket is ever created, so the missing patch looked
   effective when it was not. Fixed by patching `socket.socket.connect` too and
   testing it against a literal IP instead of a hostname.

**An open product question, pinned by tests rather than resolved:**
`kidney_disease` is the only constraint group with a block list in
`blocked_groups_for_ingredient` (kidney beans, lentils, chickpeas, tofu, soy
sauce) but no corresponding `SUBSTITUTION_RULES` entry. Every other blocked
group — egg, dairy, gluten, soy, vegan, vegetarian — has at least one
substitution that lets a meal survive; a meal containing a kidney-blocked
ingredient is rejected outright instead. This may be the right conservative
default: the vegan pattern would suggest swapping egg for tofu, but tofu is
itself on the kidney_disease block list, so a naive substitution would
recreate the problem it was meant to solve. It was never written down as
intentional, though. The behaviour is now covered by tests, so a future change
to it will be a deliberate decision, not an accidental regression.

**Left uncovered on purpose:** `rag/embedding_index.py` sits at 32%. Its
sentence-transformers/FAISS code path is behind the `semantic-rag` optional
dependency group, which is not installed in the dev environment or CI — the
uncovered lines are an unlocked extra, not a gap in the retrieval tests that
do run (`retriever.py` is at 88%).

**Verified by running:** `uv run pytest` → 214 passed, coverage 89.98%,
floor 89 enforced; `npm test` → 5 passed; `uv run ruff check .` and `uv run
ruff format --check .` clean. No production code changed — this task touched
only `pyproject.toml`, `.github/workflows/ci.yml`, and this log.
