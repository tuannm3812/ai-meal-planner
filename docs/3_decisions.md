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
