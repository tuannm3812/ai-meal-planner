# Decision Log

Dated, append-only. Each entry records what was chosen and what it ruled out.
Correct an entry by adding a new one, never by rewriting it.

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

