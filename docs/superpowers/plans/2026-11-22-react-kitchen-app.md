# React Kitchen App Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the React client from a three-step wizard into the personal kitchen app designed in
`docs/superpowers/specs/2026-11-22-react-kitchen-app-design.md`.

**Architecture:** `MealFlow`'s request logic moves, unchanged, into a `usePlanner` hook. A
`PlannerProvider` context exposes it to routed pages (`react-router-dom`). The profile and location
persist in `localStorage` through `useStoredProfile`. The plan page is rebuilt from small SVG chart
components and flat illustration components. The pure helpers in `plan.js`, `shopping.js`,
`profile.js` and `craving.js` stay, and new helpers sit beside them with unit tests.

**Tech stack:** React 19, Vite 8, Tailwind 3, Vitest 4 with Testing Library, `react-router-dom` 7,
`lucide-react`.

## Global constraints

- Frontend and docs only. No change under `backend/`, `data/` or `streamlit_app/`.
- No network on first render. The meal request payload stays exactly as today.
- A URL never carries a health field. `localStorage` holds only `aimp.v1` = `{ userId, profile, location }`.
- Macro colours: protein `#440154`, carbs `#2A788E`, fat `#22A884`. The chart ramp is
  `#440154 #414487 #2A788E #22A884 #7AD151 #FDE725`.
- Ground `#EEF4EF`, tint `#DCEEE1`. Bricolage Grotesque 800 for display, Inter for body.
- Icons come from `lucide-react` at 24–32 px with no tile. Touch targets are at least 44 px.
- Every spec state in `docs/8_design.md` §3.3 keeps its copy.
- `npm test`, `npm run lint` and `npm run build` pass after every task. `uv run pytest` passes at the
  end, and `docs/openapi.json` is untouched.

## File map

| File | Role |
| --- | --- |
| `src/app/storage.js` | `loadStored()`, `saveStored(value)`, `clearStored()`; try/catch; key `aimp.v1` |
| `src/app/usePlanner.js` | MealFlow's state machine: profile, craving, location, submit, stale, 422 mapping, retry pause, ticks |
| `src/app/PlannerContext.jsx` | `PlannerProvider`, `usePlannerContext()` |
| `src/app/AppShell.jsx` | Top bar (logo, My meals, Past plans, Profile) and `<Outlet/>` |
| `src/App.jsx` | Routes, wrapped in the provider |
| `src/main.jsx` | `BrowserRouter` |
| `src/pages/HomePage.jsx` | First visit (welcome and profile form) or the craving banner, My meals and Past plans |
| `src/pages/PlanPage.jsx` | The current plan: loading, failure, stale and dropped states, then `PlanDetail` |
| `src/pages/StoredPlanPage.jsx` | `/plans/:requestId` from history |
| `src/pages/SavedMealsPage.jsx`, `HistoryPage.jsx`, `ProfilePage.jsx` | Lists and the profile, with Forget me and the calorie estimate |
| `src/features/plan/PlanDetail.jsx` | Banner, notice, nutrition, sources, runners-up, how made, shopping, rating |
| `src/features/plan/charts/CalorieRing.jsx`, `MacroDonut.jsx`, `RangeBars.jsx`, `CalorieSources.jsx` | SVG charts |
| `src/features/plan/charts/geometry.js` | `ringFraction`, `donutSegments`, `sourceSegments` |
| `src/features/plan/runnersUp.js` | `runnersUp(plan, max = 3)` |
| `src/features/plan/RatingCard.jsx`, `SaveButton.jsx`, `shoppingText.js` | Feedback, and list-to-text |
| `src/features/meals/meals.js` | `dedupeSaved(items)`, `findPlan(items, requestId)`, `planSummary(plan)` |
| `src/features/meals/MealCard.jsx`, `useMealLists.js` | Cards and the hooks for saved meals and history |
| `src/components/illustrations/dishType.js`, `DishIllustration.jsx`, `BlobShape.jsx` | Dish art |
| `src/api/mealPlanner.js` | Adds `sendFeedback(payload)` |

Removed: `features/flow/MealFlow.jsx`, `features/flow/StepIndicator.jsx`, `features/plan/PlanView.jsx`,
`features/history/HistoryTab.jsx`, `components/brand/BrandBar.jsx`. Their tests move to the pages.

## Tasks

### Task 1: Tokens, dependencies, illustrations

- [ ] Add `react-router-dom` and `lucide-react` with `npm install --save-exact`.
- [ ] `tailwind.config.js`: set `ground` to `#EEF4EF`, add `tint: '#DCEEE1'`, set `protein`, `carbs` and
  `fat` to the Viridis values, and add `viridis: { 1..6 }` and `estimate: { bg: '#FBEBD6', fg: '#7A4A0C' }`.
  Import the `@fontsource/bricolage-grotesque` 800 weight in `main.jsx`.
- [ ] Write `dishType.test.js` first. Cases: "Chicken Fried Rice" → `rice`, "Cashew Chicken Stir Fry" → `stirfry`,
  "Pork Stir Fry Noodles" → `noodles` (noodles wins over stir fry), "Lentil Bolognese Pasta" → `pasta`,
  "Turkey Chili Bowl" → `curry`, "Chicken Pumpkin Soup" → `soup`, "Tofu Mushroom Noodle Soup" → `soup`,
  "Beef Taco Salad" → `taco`, "Steak Salad Bowl" → `salad`, "Mushroom Egg Toast" → `eggs`,
  "Vegan Oat Bowl" → `oats`, "Lemon Cod Potato Traybake" → `plate`, "Greek Chicken Bowl" → `bowl`,
  `''` → `bowl`. Keyword order: soup, curry|chili, noodle, pasta, taco|burrito|wrap, salad,
  toast|omelette|frittata|scramble, oat, stir fry, rice, plate|hash|traybake|wedges|meatball, else bowl.
- [ ] Implement `dishType` and `DishIllustration({ type, className })`, which returns an
  `aria-hidden` SVG for each of the 12 types, plus `BlobShape`.
- [ ] Run, lint, commit `feat(frontend): Flat kitchen tokens, icons and dish illustrations`.

### Task 2: Storage, the planner hook, the shell and routes

- [ ] `storage.test.js`: round trip; `loadStored()` returns `null` on bad JSON or when `getItem`
  throws; `saveStored` swallows a throwing `setItem` and returns `false`; `clearStored` removes the key.
- [ ] Implement `storage.js`.
- [ ] Move MealFlow's logic into `usePlanner({ initial })` without changing it. It returns
  `{ profile, setProfile, craving, setCraving, location, setLocation, userId, plan, isLoading, error,
  failure, errorMessage, profileErrors, fieldErrors, requestFieldErrors, profileIsValid, canSubmit,
  isStale, droppedInFlight, submitted, submitPlan, planFor(craving), ticked, toggleTick, retryPause,
  remembered, forget }`. Stored values seed it, and every profile or location change is saved.
- [ ] `AppShell`, `App` routes and `main.jsx` `BrowserRouter`. Add a test helper
  `renderApp({ route, stored })` in `src/test/renderApp.jsx`, using `MemoryRouter`.
- [ ] Port `App.test.jsx`: first render (brand, no network), the payload, the error and retry, stale
  after editing the craving, and the calorie estimate opened from Profile. Replace "keeps the profile
  out of browser storage" with: storage holds only `aimp.v1`, its keys are exactly `userId`, `profile`
  and `location`, and no URL holds a health field.
- [ ] Commit `feat(frontend): app shell, routes and remembered profile`.

### Task 3: Home and Profile pages

- [ ] Tests: the first visit shows "Tell us about you" and the profile form, and saving shows the
  craving banner; a stored profile opens straight on the banner; a suggestion chip fills the
  craving; "Plan my meal" posts and navigates to `/plan`; the Profile page edits stick after a
  reload; Forget me confirms, clears storage and returns to the first visit.
- [ ] Port `ProfileStep.test.jsx` and `CravingStep.test.jsx` onto these pages (Profile edits on
  `/profile`, the craving on `/`), keeping every assertion.
- [ ] Implement `HomePage` and `ProfilePage`.
- [ ] Commit `feat(frontend): home and profile pages`.

### Task 4: Plan page

- [ ] `geometry.test.js`: `ringFraction(629, 625) === 1`, `ringFraction(300, 600) === 0.5`,
  `ringFraction(x, null) === null`; `donutSegments({protein:27,carbs:46,fat:27}, 48)` lengths sum to
  the circumference with offsets increasing; `sourceSegments(ingredients)` sorts by kcal descending,
  assigns ramp colours in order and drops items without kcal.
- [ ] `runnersUp.test.js`: leaves out the selected `meal_id`, keeps rank order, caps at 3, and
  returns `[]` for a missing retrieval.
- [ ] Port `PlanScreen.test.jsx` and `MealFlow.test.jsx` onto `/plan`, keeping every assertion, and
  add: the ring's and donut's accessible names, the sources list, and a runner-up click posting a new
  request with that meal's name as the craving.
- [ ] Implement the charts, `PlanDetail` and `PlanPage`.
- [ ] Commit `feat(frontend): plan page with Viridis charts and runners-up`.

### Task 5: Shopping actions, saving and rating

- [ ] `shoppingText.test.js`: a store line, one line per item with its price, and the total.
- [ ] Tests: Copy list writes that text to `navigator.clipboard`; Print calls `window.print`;
  Save posts `{ user_id, request_id, meal_id, meal_name, saved: true }` and then reads "Saved to My
  meals" (disabled); rating posts `{ …, rating, notes }` and shows the stars sent; a 501 hides both and
  shows the hosted sentence.
- [ ] Port `ShoppingList.test.jsx`.
- [ ] Implement `sendFeedback`, `SaveButton`, `RatingCard` and the list actions, plus print CSS
  (`@media print` shows only `[data-print]`).
- [ ] Commit `feat(frontend): save, rate and take the shopping list`.

### Task 6: My meals, Past plans, stored plans

- [ ] `meals.test.js`: `dedupeSaved` keeps the newest record per `request_id`; `findPlan` matches
  `request_id` and returns `null` otherwise; `planSummary` gives name, kcal, split and dish type.
- [ ] Tests: Home lists saved meals and past plans; `/meals` and `/history` show cards; a card opens
  `/plans/req-1` and renders the stored plan without posting; a missing id shows "This plan is no
  longer in your history"; a 501 shows the hosted sentence. Port `HistoryTab.test.jsx`.
- [ ] Implement the pages and `useMealLists`.
- [ ] Commit `feat(frontend): my meals, past plans and stored plans`.

### Task 7: Docs, checks, screenshots

- [ ] `DESIGN.md` §3–§6: the new tokens, Viridis, icons, illustrations and shapes.
  `docs/8_design.md`: a status line pointing to the spec, and §3.1's storage rule replaced.
  `docs/3_decisions.md`: DEC-36 (remembered on this device) and DEC-37 (React main app, Flat kitchen).
  `README.md`: React is the main app and Streamlit is the backup demo. `docs/4_next_steps.md`:
  unsave and meal photos as follow-ups. `docs/5_agent_log.md`: a Claude entry. `AGENTS.md`
  current state: one line.
- [ ] Run `npm test`, `npm run lint`, `npm run build` and `uv run pytest`, plus the OpenAPI export
  check.
- [ ] Take screenshots at 1280 and 390 px of Home, the plan, My meals and Profile, and send them to
  the owner.
- [ ] Commit, push, open the PR, merge after the owner's OK on the screenshots and green CI.
