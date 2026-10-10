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
