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
