# Decision Log

Dated, append-only. Each entry records what was chosen and what it ruled out.
Correct an entry by adding a new one, never by rewriting it. The index below is
navigation only: add a row for each new entry. The agent log
(`docs/5_agent_log.md`) records *how* work was done and verified; this file
records *what was decided and why*, briefly enough to read in one sitting.

| DEC | Decision | Date |
| --- | --- | --- |
| 1 | Portfolio-first, built for a later transition to real users | 2026-09-10 |
| 2 | Streamlit demo imports the real backend in-process | 2026-09-10 |
| 3 | Foundation-first sequencing, calorie wiring pulled forward | 2026-09-10 |
| 4 | Repository Protocol plus a SQLite implementation | 2026-09-10 |
| 5 | Docs reshaped to Shape B in one atomic commit | 2026-09-10 |
| 6 | Both requirements files are generated from `uv.lock` | 2026-09-10 |
| 7 | Trusted-client API keys before OIDC | 2026-10-11 |
| 8 | Open local mode without keys; production refuses it | 2026-10-11 |
| 9 | A real `client_id` column; old SQLite schemas refused | 2026-10-11 |
| 10 | Hosted mode refuses history instead of instance-local reads | 2026-10-11 |
| 11 | No safe meal is a typed 200 (`plan_status: infeasible`), not an error | 2026-10-10 |
| 12 | Hard constraints on every return path, through one shared rule | 2026-10-08 |
| 13 | Nutrition provenance is separate from verification status | 2026-10-10 |
| 14 | Strict nutrition verification is opt-in | 2026-10-10 |
| 15 | One image from `uv.lock`; smoke tests isolated from the operator | 2026-10-11 |
| 16 | Cloud Run is the hosted target | 2026-10-11 |
| 17 | Traces go to Cloud Trace over OTLP; traces and logs export allowlisted metadata only | 2026-10-10 |
| 18 | `user_id` stays in history paths and must be opaque | 2026-10-10 |
| 19 | Keep the 30-day trace and log retention defaults | 2026-10-10 |
| 20 | Incoming trace context: `traceparent` only | 2026-10-10 |
| 21 | The OpenAPI document is a committed, CI-checked contract | 2026-10-11 |
| 22 | Render is retired; Cloud Run is the only hosted API target | 2026-10-12 |
| 23 | Every error response uses `ErrorResponse` | 2026-10-12 |
| 24 | A weight-loss budget has a floor of 1,200 kcal (women) or 1,500 (men) | 2026-10-17 |
| 25 | Meal-quality targets: calories within 10%, macros inside AMDR | 2026-10-17 |
| 26 | Portions are rebalanced per ingredient toward AMDR, never the meal itself | 2026-10-18 |
| 27 | Only the craving decides whether the corpus has a match; the profile only ranks | 2026-10-18 |
| 28 | Recipes with no fat source get a cooking oil; a rounding miss is retried 2 points inside AMDR | 2026-10-18 |
| 29 | The React app becomes one guided showcase flow, per `docs/8_design.md` | 2026-10-21 |
| 30 | Eleven recipes get a carb or fat they plausibly hold; plant milks and nut butters are not dairy | 2026-11-04 |
| 31 | Soy sauce and oats count as gluten; soy sauce is swapped for coconut aminos | 2026-11-07 |
| 32 | Alembic owns the schema and upgrades at startup; supersedes DEC-9's refusal | 2026-11-07 |
| 33 | The meal request takes today's workout; a rest day adds no exercise | 2026-11-22 |
| 34 | Diet rules read a tag table of ingredients; an untagged ingredient is refused | 2026-11-22 |
| 35 | The corpus grows to 76 recipes; new ingredients are estimates until USDA checks them | 2026-11-22 |
| 39 | A workout past the model's 30-minute range is counted per minute; past 128 bpm it is flagged | 2026-11-22 |
| 40 | A stated workout replaces the activity level's exercise | 2026-11-22 |
| 43 | User accounts: Firebase Auth, Firestore and Firebase Hosting on free tiers | 2026-11-23 |
| 44 | Market Receipt brand and a desktop side rail replace Kitchen green | 2026-11-23 |

## 2026-09-10 — Refactor and standards alignment

Source: `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md`

### DEC-1 — Portfolio-first, built for a later transition to real users

Chosen so no work is thrown away when the project takes real users. Ruled out
both shortcuts that assume it stays a demo, and full production hardening
(auth, managed Postgres) that no current user justifies.

### DEC-2 — Streamlit demo mode imports the real backend in-process

`streamlit_app/app.py` reimplemented meal selection, macros and pricing in
`local_demo_request` — a second source of truth. Demo mode will instead build the
real agents through the shared factory the DI container uses. Ruled out deleting
demo mode (the deployed demo would need a live backend, and Render's free tier
cold-starts) and dropping Streamlit entirely (loses the zero-setup demo link).

### DEC-3 — Foundation-first sequencing, with the calorie wiring pulled forward

Phase 0 lands tooling, CI and standards before any refactor, so later phases are
gated and verifiable. The one exception: wiring `CalorieExpenditureAgent` into
meal planning is the first task of Phase 1 rather than buried mid-phase, because
a trained model that is never used is a story-level flaw, not a style one. Ruled
out correctness-first (refactors would land before CI gates existed) and
vertical slices (fragments the cross-cutting dependency and CI work).

### DEC-4 — Repository Protocol plus a SQLite implementation

Gives real SQL and indexed queries with zero infra to run, and makes Postgres
later a config change plus one class. JSON implementations are retained for demo
mode. Ruled out staying on JSON (leaves the portfolio story at "file-backed
prototype") and going straight to Postgres (adds infra to every dev setup and to
CI for a project with no users).

### DEC-5 — Docs reshaped to Shape B in one atomic commit

Master §2 forbids renumbering existing repos except those "being substantially
reworked anyway", which this refactor is. Done in a single commit because every
doc path changes at once and a split would leave the README pointing at moved
files.

### DEC-6 — Both requirements files become generated artifacts

`pyproject.toml` plus `uv.lock` is the single source. Neither requirements file
can be deleted: Streamlit Cloud reads the root one and Render's `buildCommand`
reads `backend/requirements.txt`. The root file stays a one-line `-r` include;
only the backend file is exported, and CI fails on drift.

## 2026-10-11 — G4 authentication and ownership

Source: the production-readiness direction and owner decisions in
`docs/5_agent_log.md` (2026-10-07, 2026-10-08 and 2026-10-11 entries) and the
portfolio collaboration log.

### DEC-7 — Trusted-client API keys before OIDC

Keys identify client applications, each with a stable `client_id` that owns a
storage namespace. Chosen over OAuth/OIDC user tokens because v1 has no end
users calling the API directly: the public demo runs in-process, and the API's
callers are applications. Keys need no identity provider, no token
validation, no account store, and fit stateless v1. It rules out per-user
authorisation inside a client: a client is trusted to keep its own users'
`user_id`s apart. Per-user tokens are the upgrade path if end users ever call
the API directly.

### DEC-8 — Open local mode without keys; production refuses it

With `API_KEYS` empty the API runs unauthenticated in one `local` namespace, so
the React dashboard works in development without a key baked into its public
bundle. `APP_ENV=production` with no keys refuses to start. Rules out an
always-on dev key in the React bundle (owner decision A1, 2026-10-11).

### DEC-9 — A real `client_id` column, old SQLite schemas refused at startup

Every stored record carries an indexed `client_id`. `create_all` cannot add a
column and there are no migrations, so a pre-G4 database is refused at startup
with a message naming the file, rather than failing on its first query. Rules
out encoding the namespace into `user_id` (owner decision B1, 2026-10-11).

## 2026-10-11 — G6 hosted stateless mode

### DEC-10 — Hosted mode refuses history rather than serving instance-local reads

On a hosted deployment with several instances, each instance's SQLite file
holds only the requests it served. `HOSTED_MODE=true` therefore refuses history
and feedback with `501 history_disabled_stateless`, and stores no generated
plans, rather than offering reads that would differ from one instance to the
next. Rules out best-effort cross-instance reads, which cannot be described
honestly (portfolio log, 2026-10-08, point 2). Durable shared storage is the
later phase that would lift this.

## 2026-10-08 to 2026-10-10 — G3 failure semantics (recorded 2026-10-11)

Recorded retroactively: these were agreed in the portfolio log and implemented
in PRs #9, #11 and #12, but lived only in the agent log until now. Sources: the
agent-log entries of those dates.

### DEC-11 — No safe meal is a typed 200 (`plan_status: infeasible`), not an error

Every meal response carries `plan_status` (`matched`, `fallback` or
`infeasible`). "No meal satisfies these constraints" is an answer: HTTP 200,
the calorie budget kept, the meal sections null, and a client-safe
`infeasible_reason`. It is reported only once the corpus *and* the fallback
templates are exhausted; a safe low-relevance corpus meal is served first.
Unavailable retrieval stays an error (503), because infeasibility is unproven.
Rules out the interim 422, and any status that conflates "no safe meal" with
"could not look".

### DEC-12 — Hard constraints on every return path, through one shared rule

Retrieval selection, retrieval substitution and the deterministic fallback all
use `rules.safe_substitution`. A substitution rule is trusted only for the
groups it is written for; its replacement must be safe under every other
constraint (tofu to chickpeas fixes a soy allergy, not kidney disease). Rules
out per-path constraint logic, which is how the fallback once ignored health
conditions entirely.

### DEC-13 — Nutrition provenance is separate from verification status

Each ingredient keeps its `data_source` and gains a derived `verification`
(`verified_external`, `trusted_local`, `estimated`); each meal reports
`nutrition_status` (`verified` or `mixed`) and the `sources` used. An
all-estimated meal reports `mixed`, per the agreed rule; an `estimated`
aggregate would be a later, explicit amendment. Rules out the vague aggregate
string `usda_fatsecret_or_estimated`.

### DEC-14 — Strict nutrition verification is opt-in

`REQUIRE_VERIFIED_NUTRITION` (default off) makes any estimated ingredient fail
the request: `502`, code `unverified_required`. Off by default so the keyless
demo always produces plans. Both the API and the Streamlit demo parse it with
the same pydantic boolean rules. Rules out silently serving estimates where an
operator demanded verified data, and failing the keyless demo by default.

## 2026-10-11 — G5b containers

### DEC-15 — One image from `uv.lock`; smoke tests isolated from the operator

A single multi-stage image, built from `uv.lock` (so DEC-6 holds), runs the
API and, through compose, the Streamlit client. `.dockerignore` is an
allowlist, so local history and secrets cannot enter an image. History lives
inside the container and is lost on redeploy (stateless v1). The smoke tests
run as their own compose project with pinned, keyless, offline settings, and
are verified in CI from a clean checkout. Rules out a second dependency source
for the image, and smoke tests that could reuse or delete a developer's stack.

## 2026-10-11 — G6 deployment target

### DEC-16 — Cloud Run is the hosted target

Owner's choice, 2026-10-11. Chosen because the G5b image deploys unchanged; it
is the target `docs/2_architecture.md` already names; it scales to zero and runs
several instances, which is the shape hosted mode (DEC-10) was designed for;
`API_KEYS` can come from Secret Manager; and deploys can run from GitHub Actions
through Workload Identity Federation with no long-lived credentials.
Consequences: the service must set its container port to 8000 (the image
listens there, while Cloud Run defaults to 8080), and set `HOSTED_MODE=true`,
`APP_ENV=production` and `API_KEYS`. Render (`render.yaml`) is superseded; it
cannot start since G4 without `API_KEYS`, so it is to be retired or fixed as a
documented fallback. Rules out deploying without the container, and a
single-instance host on which hosted mode would be untested.

## 2026-10-10 — Correction: dates of DEC-7 to DEC-16

The headings above for G4 (DEC-7 to DEC-9), G6 hosted mode (DEC-10), G5b
(DEC-15) and the G6 deployment target (DEC-16), the "recorded" date on the G3
group, and the index rows for DEC-7 to DEC-10, DEC-15 and DEC-16 say
2026-10-11. All of those decisions were made, and recorded, on **2026-10-10**
(AEDT), as the commits that added them show (`git log docs/3_decisions.md`).
The owner's G4 choices (A1, B1) and the choice of Cloud Run were made that day
too. The decisions themselves are unchanged.

## 2026-10-10 — G10b tracing and telemetry redaction

Source: the 2026-10-07 production-readiness direction (item F and its
amendment) and the G10b proposal in `docs/5_agent_log.md` (2026-10-10). The
owner chose the recommended option on each fork the same day.

### DEC-17 — Traces go to Cloud Trace over OTLP; traces and logs export allowlisted metadata only

OpenTelemetry spans wrap each request and each `MealPlanningService` stage.
They are exported, when `TRACING_EXPORTER=cloud_trace`, over OTLP/HTTP to
Google's Telemetry API (`telemetry.googleapis.com`), authenticated with
Application Default Credentials. Google documents this as the recommended
ingestion path. Spans carry only attributes on a typed allowlist
(`core/telemetry.py`), and a failing span records the exception type and never
its message. Logs follow the same rule, because on Cloud Run they are retained
telemetry too. Request log lines use route templates, error types and codes,
and provider failures log their type and HTTP status only.

Only `opentelemetry-api` is a core dependency. It is a no-op without an SDK,
so with tracing off nothing is recorded and the SDK is never imported. The SDK
and the exporter are the `tracing` extra, which the image installs.

The secret-marker test is the evidence (`test_telemetry_redaction.py`).
Before the change it found five leaks:
- the location;
- the constraint groups, `kidney_disease` included, and the craving;
- the USDA key in a logged URL;
- `user_id` in logged paths.

Rules out: Langfuse (a third-party processor for health-adjacent data);
FastAPI auto-instrumentation (it records the raw path, which carries
`user_id`); exception events on spans; and Google's older Cloud Trace
exporter.

### DEC-18 — `user_id` stays in history paths and must be opaque

The history routes keep `/{user_id}` in the path. Cloud Run's platform request
log, and the server's access log, record full URLs, which the app cannot
redact. So `user_id` is documented as an opaque identifier, never an email
address or a name (README §8.1). Rules out moving it out of the path, a
breaking change for both clients.

### DEC-19 — Keep the 30-day trace and log retention defaults

Cloud Trace keeps spans for 30 days. Cloud Logging's `_Default` bucket keeps
logs for 30 days by default, configurable from 1 to 3,650 days. Both were
checked against Google's documentation on 2026-10-10. Hosted mode stores no
meal plans or feedback (DEC-10), so telemetry is the only retained request
record, and it holds allowlisted metadata only. Rules out a custom retention
period for v1. The command to shorten it is in `docs/6_deployment.md` §4.

### DEC-20 — Incoming trace context: `traceparent` only

This extends DEC-17, after Codex's review of PR #18. The server span continues
a caller's trace from its `traceparent` header only. That header holds a
fixed-format trace id, parent span id and flags, which are enough to join
Cloud Run's request trace.

`tracestate` and `baggage` are free text that the caller chooses. Before the
fix, `tracestate` was inherited by every span's context and exported in the
OTLP payload, outside the attribute allowlist, even on the public `/health`
route. So neither is read. Rules out the global propagator's default
`tracecontext,baggage` extraction, and any allowlist for vendor `tracestate`
entries, which nothing here needs.

## 2026-10-11 — API contract artefact

### DEC-21 — The OpenAPI document is a committed, CI-checked contract

Direction item G (2026-10-07). `docs/openapi.json` is FastAPI's generated
document, committed beside the brief and the architecture.
`test_openapi_contract.py` fails when the code's document differs from it, so
an API change, whether deliberate or not, appears in review as a diff to a
readable file. `scripts/export_openapi.py` regenerates it, ignoring
`backend/.env` so the output depends on the code alone.

The check runs inside the existing pytest job, so no new CI job is needed. It
fails on a deliberate schema change and passes once that change is reverted.

Rules out generating the document only at release time, and a separate
hand-written API description that could disagree with the code.

## 2026-10-11 — Correction: DEC-21's isolation claim

DEC-21 says the exporter ignores `backend/.env`, "so the output depends on the
code alone". That was not true. Settings read from the shell, such as
`APP_NAME`, still changed the document's title. So the exporter wrote a
different contract, and the drift test failed with no code change (Codex, P2
on PR #20).

The contract is now generated in a fresh process whose environment holds no
settings and skips the dotenv file. The exporter and the drift test both use
that one path, so every setting takes its default from the code. A running
deployment's own `/openapi.json` still reflects its configuration. The
decision itself is unchanged.

## 2026-10-12 — Owner decisions after the production-readiness gates

The owner took the recommended option on each of four open questions. Two are
architectural and recorded here. The other two, replacing the hotlinked README
hero and removing the empty `backend/app/ml/` package, are recorded in
`docs/4_next_steps.md` and the agent log.

### DEC-22 — Render is retired; Cloud Run is the only hosted API target

DEC-16 left `render.yaml` "to be retired or fixed as a documented fallback".
It could not start since G4: it set `APP_ENV=production` with no `API_KEYS`. It
is now deleted. Cloud Run, with the deploy workflow, the live check and the
runbook, is the one hosted API path. The Streamlit Community Cloud demo is
unaffected (DEC-2). `backend/requirements.txt` stays generated (DEC-6),
because the demo installs it through the root `requirements.txt`. Rules out a
second, unexercised hosting path, which would drift from the tested one.

### DEC-23 — Every error response uses `ErrorResponse`

The feedback route's 400 ("no feedback signal") was a plain `HTTPException`,
with only `{"detail": ...}`. It is now the domain error
`FeedbackSignalRequired`, with code `feedback_signal_required`. Every
documented error therefore has one body: `status`, `error`, an optional
`code`, and `detail`. `detail` and the 400 status are unchanged, so both
clients, which read `detail`, keep working. Rules out a second error shape that
clients would have to special-case.

## 2026-10-17 — Meal quality

Source: `docs/7_meal_quality.md`. Both are owner decisions.

### DEC-24 — A weight-loss budget has a floor of 1,200 kcal (women) or 1,500 (men)

The weight-loss budget was expenditure minus 400 kcal with no lower limit, so
the baseline's 62-year-old, 52 kg woman got 986 kcal a day. The deficit now
stops at 1,200 kcal for women and 1,500 for men; a sex outside the trained
categories gets the higher floor. The floor never lifts the budget above
estimated expenditure, which would turn a deficit into a surplus. A warning in
the response says when it applied. Rules out a demo recommending a daily total
below common guidance.

### DEC-25 — Meal-quality targets: calories within 10%, macros inside AMDR

A plan meets the targets when its shipped calories are within 10% of the meal
target and protein, carbohydrate and fat each sit inside the adult AMDR (10-35%,
45-65% and 20-35% of energy). Every meal-quality change is judged by how many of
the baseline's 72 plans meet them. The service's 15% reconciliation tolerance is
unchanged: it is when the service retries, not the product's target. Rules out
judging changes on calories alone, and a looser high-protein range.

### DEC-26 — Portions are rebalanced per ingredient toward AMDR, never the meal itself

Uniform portion scaling hits a calorie target but keeps a template's macro
split, so 61 of the baseline's 72 plans missed AMDR (62 missed the combined
calorie and macro targets). After the first
verification, a plan that misses the 10% calorie target or any AMDR range now
gets one factor per ingredient from a small linear programme
(`core/macro_balance.py`, solved with `scipy.optimize.linprog`):

- each factor stays within 0.5–2.0 of the scaled portion;
- calories land within 5% of the meal target;
- each macro sits 1 point inside its AMDR bound, so rounding to 5 g holds
  (since DEC-28, a miss after rounding is solved once more at 2 points);
- the sum of `|factor - 1|`, plus ten times the calorie deviation, is minimised.

The plan is verified once more, and uniform reconciliation still runs after it.
When no factors fit, or the re-verified portions miss either target (rounding
to 5 g, or a live provider's numbers), the plan ships unchanged and says so. Every response
carries a `macro_balance` record: the outcome and the split before and after.
The meal, its ingredients and their order never change, so retrieval, craving
relevance and hard-constraint substitutions are untouched.

Effect on the baseline: 41 of 72 plans meet the targets, up from 10. The other
31 cannot reach the fat range by resizing what they hold. Wider bounds
(0.25–3.0) reach 50 of 72 but triple some portions; that trade-off is the
owner's to make. Rules out changing ingredients or meals to fix the split,
which is corpus and selection work, and unbounded portion changes.

### DEC-27 — Only the craving decides whether the corpus has a match; the profile only ranks

A retrieval score adds a bonus of up to 0.24 each for meals that match the
user's restrictions and preferences. The default profile's `dairy-free` and
`high-protein` carried meals that share no term with the craving over the 0.16
threshold, so `pizza` and `chocolate dessert` were served Chicken Fried Rice,
and three constrained requests got a meal unrelated to what was asked
(`docs/7_meal_quality.md`, finding 2). Each result now also carries a
`relevance`: its score without those bonuses (the condition penalty still
applies). The corpus is used only when the top result's relevance clears the
threshold; otherwise the request takes the fallback path, whose warning says no
close match was found. A craving with no content terms, such as "high protein
meal", says nothing the profile does not, so for it relevance is the score.
Meals that clear the threshold on relevance rank ahead of those that do
not, before the top-3 cut, and the score, bonuses included, orders each group.
So a profile-boosted unrelated meal cannot hide a match ranked below it or
outside the top three (Codex, 2026-10-18: `curry` and `oats` under extra
preferences fell back while Chickpea Curry Bowl and Banana Oat Protein Bowl
qualified).

Effect on the baseline: the 11 requests above now fall back (8 off-menu, 3
constrained), and no other plan changes. 47 of 72 meet the targets, up from 41,
but all 6 gained plans are off-menu ones that now get the fallback template
instead of an equally unrelated corpus meal, so the count says nothing new
about matched meals: 36 of the 61 matched plans meet the targets, as before.

Macro-aware selection was measured and left out. For every one of the 25
plans still missing the targets, the meals that would meet them are less
relevant to the craving: Tofu Fried Rice for `chicken fried rice`, Tuna Brown
Rice Bowl for `steak and rice`, unrelated meals for `spicy curry` and `light
soup`. The one near-tie is `chicken fried rice` under kidney disease (0.38 for
the served soup bowl against 0.37 for Low-Sodium Chicken Rice Bowl). Rules out
trading relevance for the macro targets; the remaining gap is recipe and
corpus work.

### DEC-28 — Recipes with no fat source get a cooking oil; a rounding miss is retried 2 points inside AMDR

After DEC-26 and DEC-27, the 25 matched plans still missing the targets were
all six recipes with no fat source at all: Chicken Fried Rice, Lean Steak Rice
Plate, Chicken Vegetable Soup Bowl, Chickpea Curry Bowl, High-Protein Tomato
Turkey Pasta and Lentil Bolognese Pasta. Resizing their ingredients could not
lift fat to 20% of energy. Each now lists 10 g of the oil it would be cooked
in: sesame oil for the fried rice, as Tofu Fried Rice already has, and olive
oil for the rest. Both oils are in the local nutrition tables, no constraint
blocks olive oil, and a sesame allergy swaps sesame oil for olive oil through
the existing substitution. After balancing, the oil ships at 5 to 15 g.

With the oil, one plan was solved and then lost to rounding: Chicken Fried Rice
at 350 kcal re-verified at 44.7% carbohydrate after 5 g rounding, so DEC-26's
guard served the original portions. When portions solved 1 point inside each
AMDR bound miss the targets once rounded and re-verified, the solver now runs
once more at 2 points, and the result is verified again. No plan in the 72 or
in the 350–850 kcal rounding sweep is lost to rounding.

Requiring 2 points of every meal instead was tried first and ruled out (Codex,
2026-10-19): it shrinks every meal's feasible region, so Turkey Chili Bowl,
Beef Taco Salad and Turkey Sweet Potato Hash, which balance at 1 point, found
no solution. On Codex's wider check, every recipe name as a craving for the
first two profiles (68 requests), 40 met the targets before this change, 44
with the 2-point requirement (five regressions) and 49 with the retry, with no
regressions and no meal changed.

Effect on the baseline: 72 of 72 meet the targets, and all 61 matched plans,
up from 36. No scenario's meal or plan status changes. The 11 fallback plans
already met them. Rules out adding ingredients a recipe would not plausibly
contain, and changing meals to reach the targets. The guardrail corpus keeps
its pre-DEC-28 copies, so the guardrails stay comparable.

## 2026-10-21 — React showcase

Source: `docs/8_design.md`, reviewed by Codex (agent log, 2026-10-22 entry)
and approved by the owner.

### DEC-29 — The React app becomes one guided showcase flow, per `docs/8_design.md`

The three-tab dashboard becomes one flow: profile and goal, then craving, then
the plan with its shopping list, in the "Kitchen green" look. The first target
is a local showcase, not a public app. The profile is held in React state only,
never in a URL or browser storage, and goes with the meal request, so the meal
is sized to the person on screen. The screen says that a local server keeps
plan history with those details; retention is unchanged. Estimated nutrition
is disclosed per ingredient and at meal level, and "on target" is described as
measured against the same local tables. No avoid-option is offered that the
rules do not enforce, so diabetes is not offered. The frozen `App.test.jsx`
may be replaced by flow tests that keep every guarantee it has today (no
network on first render, the request payload, error and retry, the
stale-result guard, #32's meal-quality regressions). Defaults taken with the
approval, changeable by the owner: the name stays "AI Meal Planner", the meal
request keeps the service's default workout, and History stays as a small
link in local mode. Rules out photos, recipes, live prices and accounts in
this milestone, and an API key in the browser bundle.

## 2026-11-04 — Meal quality: the wider recipe check

Source: the wider recipe check (`scripts/meal_quality_baseline.py --wider`),
approved as the next milestone by the owner.

### DEC-30 — Eleven recipes get a carb or fat they plausibly hold; plant milks and nut butters are not dairy

Asking for every recipe by name, for the first two profiles, 49 of 68 plans
met the targets. All 19 misses were eleven recipes whose ingredients cannot
reach AMDR at any portions inside 0.5x to 2x: too much protein and too little
carbohydrate (the chicken plates), or too much fat (the omelette and the
avocado salads). Each now holds more of a carbohydrate or a fat it would
plausibly contain, almost always one it already listed or one a sibling recipe
uses:

- more brown rice (80 to 180 g) in Chicken Avocado Power Salad, more quinoa
  (100 to 200 g) in Low-Sodium Salmon Salad, a larger tortilla (50 to 80 g)
  in Beef Taco Salad;
- 120 g brown rice in Steak Salad Bowl and 80 g wholegrain toast with
  Vegetarian Spinach Omelette;
- a cooking oil in Chicken Vegetable Stir Fry (10 g sesame), Greek Chicken
  Bowl (10 g olive), Sweet Potato Chicken Plate (10 g olive) and Falafel Salad
  Bowl (15 g olive), and 15 g olive oil instead of 10 in Lentil Bolognese
  Pasta;
- 40 g avocado in Cottage Cheese Toast Plate.

The omelette and the steak bowl were the corpus's only low-carb meals. A
low-carb meal cannot reach AMDR's 45% carbohydrate, so both lose the
`low-carb` flag, and the omelette its `gluten-free` flag (a celiac request
still gets it, with gluten-free bread). The "Low carb" preference now favours
no meal.

Separately, a dairy keyword inside a plant food's name blocked it as dairy:
"milk" in soy milk, "butter" in peanut butter and sunflower seed butter,
"yogurt" in soy yogurt. The default profile is dairy-free, so Vegan Oat Bowl
and Peanut Tofu Bowl were never served, and asking for either by name gave
High-Protein Asian Tofu Noodle Bowl. A vegan request could not get Vegan Oat
Bowl either. Named plant foods (`PLANT_BASED_DAIRY_NAMES` in `rag/rules.py`)
are no longer dairy; real dairy and their soy or peanut groups still block.

Effect: the wider check meets the targets in 68 of 68, every recipe served as
itself. The baseline stays 72 of 72 with no meal or plan status changed; only
the vegan `creamy pasta` plan (Lentil Bolognese Pasta) moves, to 2.0% from its
target. Guardrails 5 of 5. Rules out adding ingredients a recipe would not
plausibly contain, widening the portion bounds, and exempting low-carb meals
from the targets.

### DEC-31 — Soy sauce and oats count as gluten; soy sauce is swapped for coconut aminos

Dated 2026-11-07. A check of the showcase deck found that a celiac request for
chicken fried rice kept ordinary soy sauce, which is normally brewed with wheat.
The gluten keywords named only wheat, bread, buns, pasta and tortillas. Soy sauce
and low-sodium soy sauce now count as gluten, and the swap to coconut aminos that
soy and sodium limits already use covers gluten too. Five recipes are affected.
The benchmark still has 72 of 72 plans on target. One plan changed, and the median
calorie deviation moves from 0.36% to 0.37%, which rounds to 0.4%.

Oats now count as gluten too, on the owner's choice: they contain no wheat but are
often cross-contaminated, and Australian labelling does not treat them as
gluten-free. Two oat recipes have no swap, so a gluten limit excludes them. The
benchmark's constrained cravings do not include oats, so its numbers do not move.

Rules out a gluten-free soy sauce as the replacement, because the keyword rules
would flag it and it would need a new nutrition entry.

## 2026-11-07 — Storage: database migrations

### DEC-32 — Alembic owns the schema and upgrades at startup; supersedes DEC-9's refusal

`create_all` could not change an existing table, so a schema change after data
existed had no route forward. Alembic now owns the schema. Revision `0001` is the
original table layout and `0002` adds the G4 columns, so an old file is upgraded
with its records kept instead of being refused, which replaces that part of DEC-9.
The `client_id` column itself stands.

The app applies revisions when it opens the database, as `create_all` did, so the
API, scripts and tests need no extra step. The upgrade is one transaction holding
SQLite's write lock: a failed revision leaves the file as it was, and a second
process waits rather than racing. A file with no version table is matched to the
revision that describes it. A shape no revision describes, or a revision newer
than the code, stops startup and leaves the file alone. A test fails when the
models and revisions disagree.

`scripts/migrate_json_to_sqlite.py` now skips records already stored, so running
it twice is safe.

Rules out a separate migration step before each deploy for now: with one SQLite
file per instance there is nothing shared to run it against. Postgres (§7.3 of the
next steps) should revisit this, because many instances would share one schema.

## 2026-11-22 — Calorie model: real exercise details

### DEC-33 — The meal request takes today's workout; a rest day adds no exercise

The trained model predicts the calories of one workout, and the service adds
them to BMR times the activity multiplier. The meal request had no workout
fields, so every plan assumed 30 minutes at 100 bpm, even on a rest day.

`MealRequest` now takes optional `duration_minutes`, `heart_rate_bpm` and
`body_temp_c`, passed to the calorie model. `duration_minutes: 0` is a rest day:
no exercise is added and the model is not called, because its training data has
no zero-minute rows. A detail left out keeps the old default, so plans without
workout details, including the meal-quality baseline, do not change.
`calorie_budget.exercise` reports the workout used, its calories and which
details were defaulted, so the clients describe it from the response.

The React step 1 asks for today's workout (not sure, rest day, or minutes with
an optional heart rate). Body temperature is not asked.

Still open: the activity levels count exercise days in a usual week, so a
workout day can still count some exercise twice. Ruled out for now: retiring the
model's exercise estimate, which would remove the trained model from the meal
flow.

## 2026-11-22 — Diet rules: tagged allergens

### DEC-34 — Diet rules read a tag table of ingredients; an untagged ingredient is refused

The diet rules looked for keywords in ingredient names. That missed soy sauce as
gluten until DEC-31, read "gluten-free bun" as gluten, and needed a list of plant
foods so "peanut butter" was not dairy. A tree-nut allergy refused nothing, because
it had no keywords.

`data/reference/ingredient_allergens.json` now lists all 50 ingredients a meal can
hold, with what each contains: the nine allergens, `meat`, and `high_sodium` and
`kidney_caution`. Each constraint group refuses a set of tags (vegan refuses meat,
fish, shellfish, dairy and egg). A swap must leave the ingredient safe under every
group in force. An ingredient missing from the table is refused under any diet rule,
and a test fails until every recipe, fallback and swap ingredient is listed. New
recipes (P7) have to be tagged.

The meal-quality baseline is unchanged, line for line. The sodium and kidney tags
copy what the name rules did, so black beans stay allowed for kidney disease while
kidney beans do not. A dietitian should review those two (P9).

Rules out tags on each recipe instead of each ingredient. Swaps change a meal's
ingredients, so a recipe-level tag would go stale.

## 2026-11-22 — Recipes: a larger corpus

### DEC-35 — The corpus grows to 76 recipes; new ingredients are estimates until USDA checks them

The corpus grows from 34 recipes to 76, inside the README's target of 75 to 100.
The 42 new recipes add cuisines and proteins the corpus lacked: white fish, pork,
chicken thigh, tempeh and edamame. They also add potato, couscous and nut dishes,
so a tree-nut allergy has something to refuse. Each recipe has a protein, a
carbohydrate and a cooking fat, so portion balancing (DEC-26, DEC-28) can bring it
inside AMDR.

Fifteen ingredients are new. Each is tagged (DEC-34) and has typical per-100 g
values from USDA FoodData Central in `macro_fallbacks` and `ingredient_calories`.
They go there rather than `trusted_overrides` because they were not checked against
a live lookup, so plans label them estimated until P4's USDA run confirms them. None
has a store price, so the shopping list uses category prices for them (P8).

Measured: the wider check asks for every recipe by name for two profiles, and 152 of
152 plans meet the targets, each served the recipe it named. Six recipes needed more
oil or carbohydrate before they did. The fixed baseline stays at 72 of 72, but
retrieval picks some new recipes over old ones. "Creamy pasta" now gets Tuna Pasta
Salad, "salmon dinner" Salmon Noodle Bowl, and the kidney-disease "chicken fried rice"
Low-Sodium Chicken Rice Bowl. The median calorie deviation moves from 0.4% to 0.5%.

Rules out generating recipes with Gemini. Each recipe here was written and checked
by hand against the targets, and the corpus stays a curated, reviewable file.

## 2026-11-22 — React becomes the main app

### DEC-36 — The React app remembers the person on this device

Mike chose a personal kitchen app: you come back to your saved meals and past plans,
which only works if the app knows you. There are no accounts. The browser now keeps
one `localStorage` key, `aimp.v1`, holding the opaque user ID, the profile and where
the person shops. Nothing else is stored: no plans, no ratings, no shopping ticks.

The Profile page says so, and "Forget me on this device" clears the key after a
confirmation. Server history is not touched, and the confirmation says that too.
Storage that is blocked or full is caught, and the app works for the visit and says it
can't remember. Health fields still never go in a URL.

Supersedes the "never in `localStorage`" line of DEC-29 (docs/8_design.md §3.1). Rules
out accounts for now: they need backend work (docs/4_next_steps.md §7.7).

### DEC-37 — React is the main app, rebuilt as a kitchen app in "Flat kitchen"

Mike judged the React plan screen to look like the Streamlit app. React becomes the main
app, and Streamlit stays as the simple backup demo, unchanged. Over six questions he
chose:

- a kitchen app (home, plan page, My meals, Past plans, Profile) over a wizard;
- save, rate, a shopping checklist and the retrieval's runners-up on every plan;
- a home page led by one big craving search;
- the "Flat kitchen" look: Bricolage Grotesque 800 and Inter, flat dish illustrations,
  a light green ground, and white cards with no border.

He asked for Viridis in charts, less grey, and bigger icons with no tiles. The macro
colours became Viridis stops #440154, #2A788E and #22A884 (each at least 3:1 on white),
and the plan page draws a calorie ring, a macro donut, range bars and a stacked bar of
where the calories come from, all in plain SVG with no chart library. Icons come from
`lucide-react` (ISC), and routing from `react-router-dom` (MIT).

Constraints kept: feedback is append-only, so a save can't be undone (an unsave is a
backend change). A stored plan reopens from history as it was, never re-planned. A
hosted server's 501 hides saving and rating, but planning still works. A first visit
still makes no network call before the person plans. A returning visit reads its own
saved meals and history on Home.

Rules out meal photos (the service has none, and a stock photo would show a different
dish) and a chart library (four small charts don't need one).

### DEC-38 — One tokens file holds every app colour; icons go through one component

After the kitchen app merged, Mike asked for a better design setup: a consistent colour
palette, with the icons refined to follow it. An audit of the React code found 36 raw
hex values, Tailwind's stock reds, ambers, greys, sky, violet and rose, and icons in nine
sizes, three strokes and five colours, including macro colours and tomato used on
icons. He approved the palette and icon sheet on the design canvas.

`frontend/src/theme/tokens.js` now holds every colour in five groups (neutrals, brand,
status, data, food). `tailwind.config.js` maps its class names from that file, and the
charts and dish drawings import it. Icons render through `Icon`: one 1.75 stroke, sizes
20, 24 and 32, and a colour taken from the surface (leaf on light, lime on ink, the text
colour in a button). New tokens: `leaf`, `lime`, `ink-raised`, `on-ink-muted`, the
`danger` pair and `danger-on-ink`, and `band`. Errors move from stock red to `danger`,
and the calorie ring moves off the fat colour to `viridis-2`, so a macro colour means
only its macro. A guard test enforces all of it.

Rules out CSS variables for theming (there is one theme, and Tailwind classes plus a JS
module cover both HTML and SVG) and a second icon set.

## 2026-11-22 — Calorie model: workouts past its training range

### DEC-39 — A workout past the model's 30-minute range is counted per minute; past 128 bpm it is flagged

The workout check (`scripts/meal_quality_baseline.py --workouts`) found that the
model scored a 45, 60 and 90-minute workout the same: 238 kcal for the average
man. Its training data (Kaggle S5E5) holds workouts of 1 to 30 minutes and heart
rates of 67 to 128 bpm, read from the trees' bin edges, and boosted trees are flat
past the last edge.

A workout longer than 30 minutes is now predicted at 30 minutes and scaled by its
length, so the 30-minute rate per minute holds: a 60-minute run at 140 bpm adds
477 kcal for the average man, not 238. A heart rate above 128 bpm is still
predicted as 128, and the response warns that a harder workout may be
undercounted. Each case adds a warning to `calorie_budget.warnings`. Workouts of
30 minutes or less, and the 72-plan baseline, do not change.

Still open: the body-temperature default of 37 °C is below the training range
(37.1 to 41.5 °C, mean 40.0), and the model is not monotonic in it, so a short
workout at the default scores high (10 minutes at 110 bpm: 173 kcal at 37 °C, 67
at 40.5 °C). The overlap between the activity level and today's workout is
measured by the same check and fixed by DEC-40.
Ruled out: a linear model past 30 minutes fitted to the trees, which would add a
second model to explain for one edge.

### DEC-40 — A stated workout replaces the activity level's exercise

The clients describe the activity levels as exercise days in a usual week, so BMR
times the multiplier already holds an average day's exercise (626 kcal for the
average man at x1.55). DEC-33 then added today's workout on top, so a workout day
counted exercise twice, and a rest day still counted the week's average. The workout
check found this on 15 of 24 profile-days. Mike chose this fix on 2026-11-22.

When the request states today's workout (`duration_minutes` given, 0 for a rest day),
the day's expenditure is BMR times 1.2, the sedentary multiplier, plus the workout. A
multiplier below 1.2 is kept. When the workout is not given, nothing changes: the
activity level stands and the model's 30-minute default is added, so the 72-plan
baseline does not move. `calorie_budget.exercise.replaces_activity_exercise` says
which applied, and the React plan page says so.

Budgets on stated days fall: the average man's rest day goes from 2,774 to 2,148 kcal
and his 60-minute run day from 3,251 to 2,625. Consequence to watch: a person on a
high activity level who states a modest workout gets far less than one who answers
"not sure" (the athlete: 3,333 kcal for a 60-minute run, 4,521 for not sure), so a
physical job, which the activity level also covers, is no longer counted on stated
days. Ruled out: keeping the weekly average and adding only a workout's excess over
it, which would make a rest day count the average again.
### DEC-41 — The benchmark can run on USDA data; USDA energy is read by unit

2026-11-23, P4. Mike asked for the meal-quality benchmark to run with real USDA data.
`scripts/meal_quality_baseline.py --usda` passes `USDA_API_KEY` (shell or `backend/.env`,
never an argument) to the production nutrition agent. The run's provenance records
`nutrition_source` and counts USDA lookups, failures and unusable answers, and the script
exits 2 when no key is set or no lookup succeeded, so a run that quietly fell back to the
local tables cannot pass as a USDA run. USDA search is live, so these runs are recorded
apart from the deterministic offline baseline, which stays the reference for every change.

The first run showed `_query_usda_database` keyed nutrients by name, so when a food listed
`Energy` in both kcal and kJ the kJ value could win (shrimp 356 "kcal" instead of 85).
`_energy_kcal` now prefers a kcal entry, then converts kJ at 4.184, and reads an entry
with no unit as kcal as before. Results and the per-ingredient diagnosis:
`docs/7_meal_quality.md` §6.

Rules out a dataType filter (Foundation, SR Legacy) as the fix for wrong matches: it was
measured and matched worse foods. Pinned FoodData Central IDs per ingredient are the
proposed next step, not done here.

### DEC-42 — Corpus ingredients are looked up in USDA by a reviewed FDC ID

2026-11-23, Mike's choice after DEC-41's run. Name search took USDA's top hit, which was
the wrong food for many ingredients (lean turkey mince as minced ham, avocado as avocado
dressing, cod as breaded cod), and a dataType filter matched worse. Each of the 41 corpus
ingredients without a trusted local value is now pinned in
`data/reference/usda_fdc_ids.json` to one Foundation, SR Legacy or Survey food, chosen for
the state the recipe's weight implies, and fetched from `/fdc/v1/food/{fdcId}`. A test
fails when a corpus ingredient is neither trusted nor pinned. An unpinned name still falls
back to search, which no corpus ingredient reaches.

Energy is read as plain Energy (208) in kcal, then "Energy (Atwater General Factors)"
(957), which is what Foundation foods carry; entries with no amount are skipped. With the
pins, 72 of 72 benchmark plans and 144 of 152 wider plans meet the targets on USDA data
(`docs/7_meal_quality.md` §7).

Rules out tuning pins to the score: Hass avocado and store-bought hummus stay although
USDA averages would clear about five misses.

## 2026-11-23 — User accounts

Source: `docs/superpowers/specs/2026-11-22-user-accounts-design.md`.

### DEC-43 — User accounts: Firebase Auth, Firestore and Firebase Hosting on free tiers

Mike chose Google sign-in through Firebase Auth, Firestore for profiles, plans and
feedback, and Firebase Hosting for the React app, all on free tiers in the existing GCP
project and its A$1 budget alert. A signed-out visitor to the hosted app is signed in
anonymously, so planning and history work without a Google account; Google is the only
named sign-in for now.

The API verifies Firebase ID tokens with `google-auth`, stores only the uid, and for an
account caller ignores any body `user_id` and refuses a path `user_id` that is not the
caller's. API keys keep working for Streamlit and scripts. Hosted mode serves history
when storage is Firestore; DEC-10's refusal stays for hosted SQLite.

Rules out Supabase (a second vendor whose free project sleeps after a week idle), Cloud
SQL (about A$15 or more a month) and staying device-only. Supersedes DEC-36's "no
accounts" and lifts DEC-8's limit that React cannot call the hosted API.

### DEC-44 — Market Receipt brand and a desktop side rail replace Kitchen green

2026-11-23, Mike's choice. He found the dark green unattractive and the desktop app too
narrow (one 1,152 px column, about 384 px empty each side on a 1,920 px screen). From a
proposal with three layouts he chose a side rail; from three brand directions he chose
**Market Receipt**: cobalt (#2448C9) and coral (#FF5A36) on white and paper, navy ink
(#14213D), Unbounded for display type and Inter for reading.

- Coral marks the one main action and carries ink text, not white (5.2:1; white is 3.1:1).
  Primary buttons get a hard navy "sticker" shadow.
- Banners are cobalt; ink stays for dark panels and the footer. Peach (#FFD3C7) colours
  icons, focus rings and highlights on cobalt and ink.
- Viridis stays for data (DEC-37), and the macro colours keep their meaning.
- From 1,280 px the top bar becomes a white rail on the left with five tabs (Plan a meal,
  My meals, Past plans, Calories, Profile) and a "Sized for you" card; pages widen to
  1,440 px. Phones and tablets keep the top bar.
- The calorie estimate moves from a button inside Profile to its own Calories tab.

Later slices bring the receipt-style shopping list, price-tag badges, a Home workspace
and a tabbed plan page. Rules out widening only (sides still empty on big screens) and a
FarmLens split screen (no map to fill the fixed half). Supersedes DEC-37's "Flat kitchen"
look; DEC-38's single tokens file and Icon component stay.

