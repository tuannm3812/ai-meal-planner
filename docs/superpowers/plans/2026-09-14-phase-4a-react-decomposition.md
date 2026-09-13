# Phase 4a — React Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the 811-line `frontend/src/App.jsx` into focused modules, changing no behaviour.

**Architecture:** A pure refactor, extracted bottom-up so each step is independently verifiable: formatters first (pure functions), then the UI primitives, then the API layer, then a hook that removes the duplicated loading/error/data triple, then the three tab features, and finally `App.jsx` reduced to a shell. **The eight existing tests in `App.test.jsx` query by role and accessible name through `render(<App />)`, never by file or component identity — so they must pass unchanged after every single task. They are the regression harness for the whole phase.**

**Tech Stack:** React 19, Vite 8, axios, vitest 4, React Testing Library.

**Spec:** `docs/superpowers/specs/2026-09-10-refactor-and-standards-alignment-design.md` §9 (React half)
**Branches from:** `refactor/phase-3-tests-and-ci` (PR #4, not yet merged). Its PR targets that branch.

## Scope note: Phase 4 is split in two

Spec §9 covers two independent subsystems. This plan is **4a, the React half only**.
The Streamlit half is 4b and gets its own plan. Each produces working software on its own.

**One spec correction, established before planning:** §9 says to delete
`is_meal_like_input` from `streamlit_app/app.py` as part of the duplication cleanup.
It is **not** duplicated backend logic — it is a client-side guard at `app.py:480`
that stops polite-only inputs ("thanks", "hello", "ok") reaching the API. Deleting it
would remove a real check. That belongs to 4b anyway; recorded here so the decision
is not lost.

## Verified Starting State

Measured on 2026-09-14 at the tip of `refactor/phase-3-tests-and-ci`:

| Check | Result |
| --- | --- |
| `frontend/src/App.jsx` | **811 lines** — the whole dashboard |
| `frontend/src/App.test.jsx` | 99 lines, **8 tests**, all querying through `render(<App />)` |
| `npm test` / `npm run lint` / `npm run build` | all pass |
| Backend | 222 tests, unaffected by this phase |
| Components in `App.jsx` | 10 primitives, 3 tab features, 1 shell |
| Formatters | `formatCurrency`, `formatMacro`, `formatDateTime`, `parseCommaList`, plus the `macroCards` table |
| axios call sites | 4 — `App.jsx:225`, `:445`, `:628`, `:646` |
| Duplicated state triple | `isLoading`/`error`/data in all three tabs; `HistoryTab` has **two** loading flags |

### The component inventory, with line ranges

| Symbol | Lines | Destination |
| --- | --- | --- |
| `formatCurrency`, `formatMacro`, `formatDateTime`, `parseCommaList`, `macroCards` | 6-33 | `lib/format.js` |
| `TABS` | 34-39 | stays in `App.jsx` |
| `SparkleIcon` | 40-66 | `components/ui/SparkleIcon.jsx` |
| `InputField` | 67-79 | `components/ui/InputField.jsx` |
| `SelectField` | 80-98 | `components/ui/SelectField.jsx` |
| `StatCard` | 99-110 | `components/ui/StatCard.jsx` |
| `SectionCard` | 111-126 | `components/ui/SectionCard.jsx` |
| `EmptyState` | 127-146 | `components/ui/EmptyState.jsx` |
| `SuccessBanner` | 147-154 | `components/ui/SuccessBanner.jsx` |
| `ErrorBanner` | 155-162 | `components/ui/ErrorBanner.jsx` |
| `SubmitButton` | 163-177 | `components/ui/SubmitButton.jsx` |
| `TabBar` | 178-198 | `components/ui/TabBar.jsx` |
| `MealPlanTab` | 199-411 | `features/mealPlan/MealPlanTab.jsx` |
| `GOAL_OPTIONS`, `SEX_OPTIONS` | 412-422 | `features/calories/CaloriesTab.jsx` |
| `CaloriesTab` | 423-614 | `features/calories/CaloriesTab.jsx` |
| `HistoryTab` | 615-776 | `features/history/HistoryTab.jsx` |
| `App` | 777-811 | stays in `App.jsx` |

## Global Constraints

- **No behaviour may change.** This is a move-and-rewire refactor. The eight existing
  tests in `frontend/src/App.test.jsx` must pass **unchanged** after every task —
  do not edit that file except where a task explicitly says to.
- **`npm test`, `npm run lint` and `npm run build` must all pass after every task.**
  Run all three; a passing test suite with a broken build is not done.
- **No file in `frontend/src` may exceed 200 lines** when the phase completes (spec §9's
  "done when"). Check with `wc -l` and report.
- **No new runtime dependencies.** React, axios and the existing dev tooling are all
  that is needed. If you think you need a package, stop and report.
- **Backend is untouched.** `git diff --stat -- backend streamlit_app pyproject.toml uv.lock`
  must be empty. Do not run the backend suite as a gate; it cannot be affected.
- **Never `git add -A`.** `git status --short`, review every path, stage explicitly.
  Master standard §10.1. Note `.coverage` and `database/ai_meal_planner.db` are
  gitignored local artifacts — leave them.
- Commit format `<type>(<scope>): <imperative summary>`; the `(scope)` is mandatory.
  Every body ends with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- Use the project's existing style: functional components, named `function` declarations,
  Tailwind class strings copied verbatim, single quotes, no semicolons. **Match what is
  there** — do not reformat or "improve" markup while moving it.
- Work on branch `refactor/phase-4a-react`. Do not push or open PRs.

## Critical Facts

### The tests are the harness, and they are behaviour-level

`App.test.jsx` renders `<App />` and queries `getByRole('button', { name: 'Meal Plan' })`,
`getByRole('heading', { name: 'Plan Request' })` and similar. It never imports a
sub-component. That is what makes a bottom-up extraction safe: if a heading's text or a
button's accessible name changes, or a tab stops rendering, the suite fails immediately.
**Run it after every extraction, not just at the end.**

### `axios` is mocked at module level in the test file

`App.test.jsx` does `vi.mock('axios', ...)`. Once the API layer moves to
`api/client.js`, that mock still works **only if** `client.js` imports the default
`axios` export and the mock keeps providing `default.get`/`default.post`. If you switch
to `axios.create()`, the existing mock will not intercept it — the module mock returns a
plain object with no `create`. **Task 3 addresses this explicitly; read it before
touching the API layer.**

### `HistoryTab` has two independent loading flags

`isLoadingHistory` and `isLoadingSaved`, driving two separate fetches
(`/meal-plans/{id}` and `/saved-meals/{id}`) that share one `error`. A single
`useAsyncRequest` instance cannot model that. Use **two** instances and keep the shared
error semantics, or leave `HistoryTab` on its existing local state and say so. Do not
collapse the two flags into one — that would change what the UI shows.

---

## File Structure

**Created:**

| File | Responsibility |
| --- | --- |
| `frontend/src/lib/format.js` | The four formatters and the `macroCards` table |
| `frontend/src/lib/format.test.js` | Unit tests for the formatters |
| `frontend/src/api/client.js` | Base URL resolution and the shared request helper |
| `frontend/src/api/mealPlanner.js` | One function per endpoint |
| `frontend/src/api/mealPlanner.test.js` | Tests that each function calls the right URL |
| `frontend/src/hooks/useAsyncRequest.js` | The loading/error/data triple, once |
| `frontend/src/hooks/useAsyncRequest.test.jsx` | Hook tests |
| `frontend/src/components/ui/*.jsx` | Ten primitives, one file each |
| `frontend/src/features/mealPlan/MealPlanTab.jsx` | The meal-plan tab |
| `frontend/src/features/calories/CaloriesTab.jsx` | The calorie tab |
| `frontend/src/features/history/HistoryTab.jsx` | The history tab |

**Modified:** `frontend/src/App.jsx` — shrinks to shell, `TABS` and tab state.

---

## Task 1: Extract the formatters

Pure functions with no React involvement — the safest possible starting point, and it
proves the import wiring works before anything harder moves.

**Files:**
- Create: `frontend/src/lib/format.js`, `frontend/src/lib/format.test.js`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Produces: named exports `formatCurrency(value)`, `formatMacro(value, unit)`,
  `formatDateTime(value)`, `parseCommaList(value)` and the array `macroCards`.
  Tasks 5-7 import these.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/lib/format.test.js`:

```javascript
import { describe, expect, it } from 'vitest'

import { formatCurrency, formatDateTime, formatMacro, macroCards, parseCommaList } from './format'

describe('formatCurrency', () => {
  it('formats a number as AUD', () => {
    expect(formatCurrency(12.5)).toContain('12.50')
  })

  it('treats null and undefined as zero rather than NaN', () => {
    expect(formatCurrency(null)).toContain('0.00')
    expect(formatCurrency(undefined)).toContain('0.00')
  })
})

describe('formatMacro', () => {
  it('fixes to one decimal and appends the unit', () => {
    expect(formatMacro(31.456, 'g')).toBe('31.5g')
  })

  it('treats a missing value as zero', () => {
    expect(formatMacro(null, ' kcal')).toBe('0.0 kcal')
  })
})

describe('formatDateTime', () => {
  it('returns a placeholder for an empty value', () => {
    expect(formatDateTime('')).toBe('Unknown time')
  })

  it('returns the input unchanged when it is not a date', () => {
    expect(formatDateTime('not-a-date')).toBe('not-a-date')
  })

  it('formats a real ISO timestamp', () => {
    expect(formatDateTime('2026-09-14T10:30:00Z')).not.toBe('Unknown time')
  })
})

describe('parseCommaList', () => {
  it('splits, trims and drops blanks', () => {
    expect(parseCommaList(' a , , b ')).toEqual(['a', 'b'])
  })

  it('returns an empty array for an empty string', () => {
    expect(parseCommaList('')).toEqual([])
  })
})

describe('macroCards', () => {
  it('describes the four macros the nutrition panel renders', () => {
    expect(macroCards.map((card) => card.key)).toEqual([
      'total_calories',
      'total_protein',
      'total_carbs',
      'total_fat',
    ])
  })
})
```

- [ ] **Step 2: Run it to verify it fails**

```bash
cd frontend && npx vitest run src/lib/format.test.js
```
Expected: FAIL — cannot resolve `./format`.

- [ ] **Step 3: Create the module**

Create `frontend/src/lib/format.js` by **moving lines 6-33 of `App.jsx` verbatim** and
adding `export` to each binding. Do not change any formatting logic — the locale
`'en-AU'`, the currency `'AUD'`, the `toFixed(1)`, the `dateStyle`/`timeStyle` options
and the Tailwind `dot` classes in `macroCards` must all be byte-identical.

- [ ] **Step 4: Rewire `App.jsx`**

Delete lines 6-33 from `App.jsx` and add, after the existing React import:

```javascript
import { formatCurrency, formatDateTime, formatMacro, macroCards, parseCommaList } from './lib/format'
```

- [ ] **Step 5: Verify — the harness must still pass unchanged**

```bash
cd frontend && npm test && npm run lint && npm run build
```
Expected: **13 tests pass** (8 existing + 5 new describe blocks' cases — report the real
number), lint clean, build succeeds. **If any of the 8 original tests fails, a formatter
changed behaviour** — revert and find the difference rather than editing the test.

- [ ] **Step 6: Commit**

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
git status --short
git add frontend/src/lib frontend/src/App.jsx
git commit -F - <<'MSG'
refactor(frontend): extract the formatters into lib/format.js

First step of splitting the 811-line App.jsx. The four formatters and the
macroCards table are pure functions with no React involvement, so they move with
the least risk and prove the import wiring before anything harder follows.

Moved verbatim - the en-AU locale, the AUD currency, toFixed(1), the date style
options and the Tailwind dot classes are byte-identical, and now have unit tests
including the null-to-zero behaviour that was previously untested.

The eight existing App tests pass unchanged; they query by role and accessible
name through render(<App />), so they are the regression harness for this phase.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 2: Extract the ten UI primitives

**Files:**
- Create: `frontend/src/components/ui/{SparkleIcon,InputField,SelectField,StatCard,SectionCard,EmptyState,SuccessBanner,ErrorBanner,SubmitButton,TabBar}.jsx`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Produces: ten default-exported components, each keeping its current props exactly:
  `SparkleIcon({ className })`, `InputField({ helperText, label, ...inputProps })`,
  `SelectField({ helperText, label, options, ...selectProps })`,
  `StatCard({ dot, label, value })`, `SectionCard({ eyebrow, title, children, className })`,
  `EmptyState({ isLoading, loadingTitle, loadingBody, idleTitle, idleBody })`,
  `SuccessBanner({ children })`, `ErrorBanner({ children })`,
  `SubmitButton({ isLoading, idleLabel, loadingLabel, disabled })`,
  `TabBar({ activeTab, onChange })`.
  Tasks 5-7 import these.

- [ ] **Step 1: Move each component to its own file**

For each row in the inventory table above, create the file and move the function
**verbatim** — same props, same Tailwind class strings, same markup. Add
`export default <Name>` at the end of each. `TabBar` needs the `TABS` array; **import it
from `../../App`** would be circular, so **move `TABS` into `components/ui/TabBar.jsx`**
and export it as a named export, then have `App.jsx` import it back:

```javascript
export const TABS = [
  // ... the existing three entries, verbatim
]
```

- [ ] **Step 2: Rewire `App.jsx`**

Delete lines 40-198 and add the ten imports plus the `TABS` re-import:

```javascript
import EmptyState from './components/ui/EmptyState'
import ErrorBanner from './components/ui/ErrorBanner'
import InputField from './components/ui/InputField'
import SectionCard from './components/ui/SectionCard'
import SelectField from './components/ui/SelectField'
import SparkleIcon from './components/ui/SparkleIcon'
import StatCard from './components/ui/StatCard'
import SubmitButton from './components/ui/SubmitButton'
import SuccessBanner from './components/ui/SuccessBanner'
import TabBar, { TABS } from './components/ui/TabBar'
```

Ruff does not apply here, but **ESLint will flag any import that is now unused** — if a
primitive is only used by a tab and not by `App` itself, the import belongs in the tab's
file, not in `App.jsx`. Let `npm run lint` tell you; do not guess.

- [ ] **Step 3: Verify**

```bash
cd frontend && npm test && npm run lint && npm run build
wc -l src/App.jsx src/components/ui/*.jsx
```
Expected: all tests pass (report the count), lint clean, build succeeds. Every file in
`components/ui/` should be well under 100 lines. **If lint reports unused imports in
`App.jsx`, move them to whichever file actually uses them** — that is the signal telling
you where each primitive belongs.

- [ ] **Step 4: Commit**

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
git status --short
git add frontend/src/components frontend/src/App.jsx
git commit -F - <<'MSG'
refactor(frontend): move the ten UI primitives into components/ui

One file per primitive - SparkleIcon, InputField, SelectField, StatCard,
SectionCard, EmptyState, SuccessBanner, ErrorBanner, SubmitButton and TabBar -
each moved verbatim with its props and Tailwind class strings unchanged.

TABS moved into TabBar.jsx as a named export rather than staying in App.jsx,
which would have made the import circular; App.jsx imports it back.

The eight existing App tests pass unchanged, which is what makes this
verifiable as a pure move.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 3: Extract the API layer

**Read the Critical Facts note about the axios mock before starting.**

**Files:**
- Create: `frontend/src/api/client.js`, `frontend/src/api/mealPlanner.js`, `frontend/src/api/mealPlanner.test.js`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Produces: from `api/client.js`, the named export `API_BASE_URL`. From
  `api/mealPlanner.js`, four async functions:
  `generateMealPlan(payload) -> Promise<object>`,
  `predictCalorieExpenditure(payload) -> Promise<object>`,
  `fetchMealPlans(userId, limit) -> Promise<object>`,
  `fetchSavedMeals(userId, limit) -> Promise<object>`.
  Each resolves to the response **body** (`data`), not the axios response. Tasks 5-7
  import these.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/api/mealPlanner.test.js`:

```javascript
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { ok: 'get' } })),
    post: vi.fn(() => Promise.resolve({ data: { ok: 'post' } })),
  },
}))

import axios from 'axios'

import { API_BASE_URL } from './client'
import {
  fetchMealPlans,
  fetchSavedMeals,
  generateMealPlan,
  predictCalorieExpenditure,
} from './mealPlanner'

describe('mealPlanner', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('posts a meal plan request to the right URL and returns the body', async () => {
    const body = await generateMealPlan({ craving: 'pasta' })
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/generate-meal-plan`,
      { craving: 'pasta' },
      expect.anything(),
    )
    expect(body).toEqual({ ok: 'post' })
  })

  it('posts a calorie prediction to the right URL', async () => {
    await predictCalorieExpenditure({ age: 28 })
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/calorie-expenditure/predict`,
      { age: 28 },
      expect.anything(),
    )
  })

  it('gets meal plans for a user with the limit as a query param', async () => {
    await fetchMealPlans('user_123', 10)
    expect(axios.get).toHaveBeenCalledWith(
      `${API_BASE_URL}/meal-plans/user_123`,
      { params: { limit: 10 } },
    )
  })

  it('gets saved meals for a user with the limit as a query param', async () => {
    await fetchSavedMeals('user_123', 5)
    expect(axios.get).toHaveBeenCalledWith(
      `${API_BASE_URL}/saved-meals/user_123`,
      { params: { limit: 5 } },
    )
  })
})
```

- [ ] **Step 2: Run it to verify it fails**

```bash
cd frontend && npx vitest run src/api/mealPlanner.test.js
```
Expected: FAIL — cannot resolve `./client`.

- [ ] **Step 3: Read the current call sites before writing anything**

```bash
sed -n '218,240p;438,460p;624,655p' src/App.jsx
```
Note the **exact** third argument each `axios` call passes. **Correction, verified
2026-09-14:** the POSTs pass only **two** arguments — there is no Gemini-key header in
the React client at all; that header belongs to the backend's `/generate-meal-plan`
route, not this caller. The GETs pass `{ params: { limit } }`. Trust the code over this
plan if they ever disagree.
Your functions must reproduce those exactly. If a call site passes something this plan's
signatures cannot express, **widen the signature and say so in your report** rather than
dropping the argument.

- [ ] **Step 4: Write the modules**

Create `frontend/src/api/client.js`:

```javascript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

Keep it to that. A `axios.create()` instance would be tidier but **breaks the existing
module-level `vi.mock('axios')` in `App.test.jsx`**, which provides only `default.get`
and `default.post` and no `create` — the eight-test harness would fail. Note that
trade-off in a comment so the next reader knows it was deliberate.

Create `frontend/src/api/mealPlanner.js` with one function per endpoint, each calling
`axios` and returning `data`. Reproduce the third arguments exactly as found in Step 3.

- [ ] **Step 5: Rewire `App.jsx`**

Replace the four inline `axios` calls with calls to these functions, and remove the now
unused `axios` and `API_BASE_URL` from `App.jsx`. **`App.jsx` line 4's `API_BASE_URL`
is also displayed in the footer** (`API target ...`) — import it from `./api/client` so
that display keeps working.

- [ ] **Step 6: Verify**

```bash
cd frontend && npm test && npm run lint && npm run build
```
Expected: all pass. **The eight original tests include one asserting `axios.get` and
`axios.post` are not called on first render** — it must still pass, which it will only
if the API layer is imported but not invoked at module scope.

- [ ] **Step 7: Commit**

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
git status --short
git add frontend/src/api frontend/src/App.jsx
git commit -F - <<'MSG'
refactor(frontend): extract the API layer into api/

Four inline axios calls scattered through App.jsx become one function per
endpoint in api/mealPlanner.js, each returning the response body rather than the
axios response. api/client.js owns base-URL resolution.

client.js deliberately does not use axios.create(): the existing test harness
mocks the axios module with only default.get and default.post, so an instance
would not be intercepted and the eight-test suite would break. The trade-off is
noted in the file.

New tests assert each function calls the right URL with the right params. The
eight existing App tests pass unchanged, including the one asserting no request
fires on first render.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 4: The `useAsyncRequest` hook

**Read the Critical Facts note about `HistoryTab`'s two loading flags before starting.**

**Files:**
- Create: `frontend/src/hooks/useAsyncRequest.js`, `frontend/src/hooks/useAsyncRequest.test.jsx`

**Interfaces:**
- Produces: `useAsyncRequest(requestFn)` returning
  `{ data, error, isLoading, run, reset }` where `run(...args)` calls
  `requestFn(...args)`, sets `isLoading` while it is in flight, stores the resolved value
  in `data`, and on rejection stores a string in `error` and leaves `data` untouched.
  `reset()` clears `data` and `error`. Tasks 5-6 use it.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/hooks/useAsyncRequest.test.jsx`:

```javascript
import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { useAsyncRequest } from './useAsyncRequest'

describe('useAsyncRequest', () => {
  it('starts idle', () => {
    const { result } = renderHook(() => useAsyncRequest(vi.fn()))
    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBe('')
  })

  it('stores the resolved value', async () => {
    const request = vi.fn(() => Promise.resolve({ ok: true }))
    const { result } = renderHook(() => useAsyncRequest(request))
    await act(async () => {
      await result.current.run('arg')
    })
    expect(request).toHaveBeenCalledWith('arg')
    expect(result.current.data).toEqual({ ok: true })
    expect(result.current.error).toBe('')
    expect(result.current.isLoading).toBe(false)
  })

  it('stores a string error on rejection and does not throw', async () => {
    const request = vi.fn(() => Promise.reject(new Error('boom')))
    const { result } = renderHook(() => useAsyncRequest(request))
    await act(async () => {
      await result.current.run()
    })
    await waitFor(() => expect(result.current.error).not.toBe(''))
    expect(typeof result.current.error).toBe('string')
    expect(result.current.isLoading).toBe(false)
  })

  it('clears state on reset', async () => {
    const request = vi.fn(() => Promise.resolve({ ok: true }))
    const { result } = renderHook(() => useAsyncRequest(request))
    await act(async () => {
      await result.current.run()
    })
    act(() => {
      result.current.reset()
    })
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBe('')
  })
})
```

- [ ] **Step 2: Run it to verify it fails**

```bash
cd frontend && npx vitest run src/hooks/useAsyncRequest.test.jsx
```
Expected: FAIL — cannot resolve `./useAsyncRequest`.

- [ ] **Step 3: Write the hook**

Create `frontend/src/hooks/useAsyncRequest.js` exporting a named `useAsyncRequest`. Use
`useState` for the three values and `useCallback` for `run` and `reset`. `run` must
`await` the request inside `try/finally` so `isLoading` is cleared on both paths, and
must not re-throw.

- [ ] **Step 4: Verify**

```bash
cd frontend && npm test && npm run lint && npm run build
```
Expected: all pass. This task adds the hook and its tests but **wires nothing up yet** —
that happens in Tasks 5 and 6, so the eight App tests are unaffected.

- [ ] **Step 5: Commit**

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
git status --short
git add frontend/src/hooks
git commit -F - <<'MSG'
feat(frontend): add a useAsyncRequest hook

All three tabs repeat the same isLoading/error/data triple with the same
try/catch/finally around a request. This hook holds it once. It is added with
tests here and wired into the tabs in the following commits, so this change is
purely additive.

run() never re-throws and clears isLoading in a finally block, so a rejected
request leaves the UI in a usable state rather than an unhandled rejection.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 5: Extract `MealPlanTab`

The largest single component at 213 lines, so it gets its own task.

**Files:**
- Create: `frontend/src/features/mealPlan/MealPlanTab.jsx`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Consumes: `lib/format`, `components/ui/*`, `api/mealPlanner.generateMealPlan`,
  `hooks/useAsyncRequest`.
- Produces: a default-exported `MealPlanTab` taking **no props** — it owns its own form
  state, exactly as it does today.

- [ ] **Step 1: Move the component**

Move lines 199-411 of `App.jsx` verbatim into `frontend/src/features/mealPlan/MealPlanTab.jsx`,
add the imports it needs, and `export default MealPlanTab`. Keep every heading string,
every Tailwind class and every `helperText` exactly as it is — the harness asserts
`getByRole('heading', { name: 'Plan Request' })`, so a changed heading breaks it.

- [ ] **Step 2: Wire it to the hook and the API layer**

Replace this component's local `isLoading`/`error`/`mealPlan` triple and its inline
`axios.post` with `useAsyncRequest(generateMealPlan)`. **Keep the user-facing error text
identical** — the current `catch` produces a specific message mentioning port 8000; if
the hook's generic message differs, pass a formatter or keep the component's own
mapping so the rendered text does not change.

**If wiring the hook would change any rendered string, keep the local state instead and
report why.** A smaller diff that preserves behaviour beats a tidier one that does not.

- [ ] **Step 3: Rewire `App.jsx`**

Delete lines 199-411 and add `import MealPlanTab from './features/mealPlan/MealPlanTab'`.

- [ ] **Step 4: Verify**

```bash
cd frontend && npm test && npm run lint && npm run build
wc -l src/App.jsx src/features/mealPlan/MealPlanTab.jsx
```
Expected: all tests pass. Three of the eight target this tab directly — the default-tab
render, the form submission firing `axios.post`, and the rejected-request error banner.
**All three must pass without editing them.**

- [ ] **Step 5: Commit**

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
git status --short
git add frontend/src/features/mealPlan frontend/src/App.jsx
git commit -F - <<'MSG'
refactor(frontend): move MealPlanTab into features/mealPlan

The largest component in App.jsx at 213 lines. Moved verbatim, then wired to
useAsyncRequest and api/mealPlanner.generateMealPlan in place of its local
loading/error/data triple and inline axios call.

Every heading, helper text and Tailwind class is unchanged, and the user-facing
error message is preserved rather than replaced by the hook's generic one - three
of the eight harness tests assert against this tab's rendered text, including the
submit-fires-a-request and rejected-request-shows-the-banner cases, and all three
pass unedited.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 6: Extract `CaloriesTab` and `HistoryTab`

**Read the Critical Facts note about `HistoryTab`'s two loading flags.**

**Files:**
- Create: `frontend/src/features/calories/CaloriesTab.jsx`, `frontend/src/features/history/HistoryTab.jsx`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Consumes: the same modules as Task 5, plus
  `api/mealPlanner.predictCalorieExpenditure`, `fetchMealPlans` and `fetchSavedMeals`.
- Produces: default-exported `CaloriesTab` and `HistoryTab`, both taking no props.

- [ ] **Step 1: Move `CaloriesTab`**

Move lines 412-614 (including `GOAL_OPTIONS` and `SEX_OPTIONS`, which only this tab uses)
into `frontend/src/features/calories/CaloriesTab.jsx`. Wire it to
`useAsyncRequest(predictCalorieExpenditure)` under the same behaviour-preserving rule as
Task 5: if the hook would change a rendered string, keep the local state and say so.

- [ ] **Step 2: Move `HistoryTab`**

Move lines 615-776 into `frontend/src/features/history/HistoryTab.jsx`. This tab has
**two** loading flags and **two** fetches sharing one error. Use **two**
`useAsyncRequest` instances — one per fetch — or leave its local state alone. **Do not
merge the two flags**; the UI shows them independently and merging would change what a
user sees.

- [ ] **Step 3: Rewire `App.jsx`**

Delete lines 412-776 and add both imports.

- [ ] **Step 4: Verify**

```bash
cd frontend && npm test && npm run lint && npm run build
wc -l src/App.jsx src/features/*/*.jsx
```
Expected: all tests pass. Two of the eight assert
`getByRole('heading', { name: 'Calorie Expenditure' })` and the three History headings
(`History`, `Meal History`, `Saved Meals`) — all must pass unedited.

- [ ] **Step 5: Commit**

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
git status --short
git add frontend/src/features frontend/src/App.jsx
git commit -F - <<'MSG'
refactor(frontend): move CaloriesTab and HistoryTab into features/

CaloriesTab takes GOAL_OPTIONS and SEX_OPTIONS with it, since nothing else uses
them.

HistoryTab keeps two independent loading flags driving two fetches that share one
error. They are modelled as two useAsyncRequest instances rather than collapsed
into one - the UI shows them separately, so merging them would change what a user
sees while looking like a simplification.

The harness tests asserting the Calorie Expenditure heading and the three History
headings pass unedited.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Task 7: Reduce `App.jsx` to a shell and check the size target

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Trim what is left**

`App.jsx` should now contain only: the imports, the `App` function (shell, tab state,
header, footer, and the `activeTab` switch), and `export default App`. Remove any import
ESLint reports as unused. It should be well under 100 lines.

- [ ] **Step 2: Check the spec's size target**

```bash
cd frontend
wc -l src/App.jsx src/App.test.jsx src/main.jsx src/lib/*.js src/api/*.js src/hooks/*.js src/components/ui/*.jsx src/features/*/*.jsx | sort -rn | head -20
```
Spec §9's "done when" is **no file in `frontend/src` over ~200 lines**. Report the largest
file. If one still exceeds 200, say which and by how much — do **not** split it further
just to hit the number without saying so.

- [ ] **Step 3: Confirm nothing behavioural moved**

```bash
npm test && npm run lint && npm run build
```
Expected: all pass, with the eight original tests **never having been edited**. Prove it:

```bash
cd "/Users/tuannm3812/Documents/GitHub/1. Study/ai-meal-planner"
git diff refactor/phase-3-tests-and-ci HEAD -- frontend/src/App.test.jsx
```
Expected: **empty**. If that file changed, the refactor altered behaviour and the change
was absorbed into the test instead of being fixed — report exactly what and why.

- [ ] **Step 4: Confirm the backend is untouched**

```bash
git diff refactor/phase-3-tests-and-ci HEAD --stat -- backend streamlit_app pyproject.toml uv.lock docs
```
Expected: empty except the plan document.

- [ ] **Step 5: Commit**

```bash
git status --short
git add frontend/src/App.jsx
git commit -F - <<'MSG'
refactor(frontend): reduce App.jsx to a shell

App.jsx now holds only the shell - imports, tab state, header, footer and the
active-tab switch. It was 811 lines.

Spec section 9's target is no file in frontend/src over roughly 200 lines; the
largest is now reported in the phase log.

The eight behaviour tests in App.test.jsx are byte-identical to before the phase
started, which is the evidence that this decomposition changed nothing a user can
observe.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
MSG
```

---

## Phase 4a Exit Gate

Spec §9's React half is done when `App.jsx` is a shell, no file in `frontend/src` exceeds
~200 lines, and the dashboard still covers meal plan, calorie prediction and history.

- [ ] `npm test` passes; report the real count (8 harness tests plus the new unit tests)
- [ ] **`frontend/src/App.test.jsx` is byte-identical to the phase start** —
      `git diff refactor/phase-3-tests-and-ci HEAD -- frontend/src/App.test.jsx` is empty
- [ ] `npm run lint` and `npm run build` both pass
- [ ] No file in `frontend/src` exceeds ~200 lines — report the largest
- [ ] `App.jsx` contains no component other than `App`
- [ ] No new runtime dependency: `git diff ... -- frontend/package.json` adds nothing to `dependencies`
- [ ] Backend untouched: `git diff ... --stat -- backend streamlit_app pyproject.toml uv.lock` empty
- [ ] All three tabs still render and switch — covered by the harness
- [ ] `git status --short` clean
- [ ] Append a Phase 4a entry to `docs/5_agent_log.md`; tick this checklist

Then write the Phase 4b plan for the Streamlit half of spec §9.
