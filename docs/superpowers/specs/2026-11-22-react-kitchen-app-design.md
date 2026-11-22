# React kitchen app — design

**Status:** brainstormed with the owner on 22 November 2026, waiting on his review of this file.
Mockups: the "Meal planner layouts" design canvas (owner's private artifact). Its three rows are
the home layouts, the visual directions and the plan page.

## 1. Why

The owner judged the React app's plan screen to look "like the Streamlit app". It is a three-step
form ending in a column of grey cards. The service can do more than the app shows. It can save a
meal, rate it and list past plans, and the retrieval step ranks runners-up. React uses none of
these. Streamlit still does save and rate.

Two decisions follow:

- **React becomes the main app.** Streamlit stays as the simple backup demo, and it is not
  redesigned.
- **React becomes a personal kitchen app,** not a wizard. You open it to a home screen, say what
  you crave, get a plan page, and come back later to your saved meals and past plans.

## 2. What the owner chose

| # | Question | Answer |
| --- | --- | --- |
| 1 | What the app feels like | A personal kitchen app: home, plan page, My meals, Past plans |
| 2 | Remembering the person | On this device: the browser keeps the opaque ID and the profile, says so, and has "Forget me on this device" |
| 3 | Actions on a plan | All four: save, rate with a note, shop from a checklist, open a runner-up |
| 4 | Home layout | B, "Big craving search", with C's calorie ring and macro donut on the plan page |
| 5 | Visual direction | 1, "Flat kitchen": Bricolage Grotesque ExtraBold and Inter, flat food illustrations, blob shapes |
| 6 | Plan page | As mocked up |

Standing preferences: Viridis for charts, less grey, bigger icons with no tiles behind them.

## 3. Scope

**In scope:** everything under `frontend/`, plus `DESIGN.md`, `docs/8_design.md`,
`docs/3_decisions.md`, `docs/4_next_steps.md`, `README.md` and `docs/5_agent_log.md`.

**Out of scope:** any backend, schema or corpus change; accounts; live prices; meal photos; a
Streamlit redesign; hosted React against a keyed API (DEC-8 stands).

## 4. Screens and routes

Routing uses `react-router-dom` (MIT). A URL carries a `request_id` at most, never a health field.

| Route | Screen |
| --- | --- |
| `/` | Home |
| `/plan` | The plan just made, held in memory |
| `/plans/:requestId` | A past or saved plan, read back from local history |
| `/meals` | My meals |
| `/history` | Past plans |
| `/profile` | Profile, plus the separate calorie estimate as a section |

A shared top bar holds the logo (it links to Home) and three links with 26 px icons and text:
My meals, Past plans and Profile. On a phone the links wrap below the logo.

### 4.1 First visit

With no stored profile, Home opens with a welcome banner and the existing profile form, using the
same fields, chips, workout input and validation as today's step 1. Saving it stores the profile
and shows the normal Home. "Forget me on this device" on the Profile page clears the storage and
returns to this state.

### 4.2 Home (layout B)

- A dark `ink` banner with the headline "Say what you crave. Get a meal that fits you.", a large
  craving input with a search icon, the tomato "Plan my meal" button, and the suggestion chips.
  The suggestions are real corpus meals, as today.
- A line under the input: "Sized for you: about N kcal a meal. Shopping near <location>." with a
  link to Profile. The location input moves to Profile, and it is stored with the profile.
- The flat illustration and the blob shape behind it sit on the banner's right and are hidden
  below 768 px.
- **My meals:** up to four cards, each with its dish illustration, name, kcal, a Viridis macro bar
  and the split as text. "See all" goes to `/meals`.
- **Past plans:** the latest five, with the meal name, the craving and kcal.
- Loading uses the existing indeterminate "Planning your meal…" state. Submitting navigates to
  `/plan` when the response arrives. The stale-result guard stays.

### 4.3 Plan page

From top to bottom (left column on desktop):

1. **Banner** (`ink`): "← Home", "For your craving …", the meal name at 56 px, badges for the match,
   the balance outcome and "Some nutrition estimated", **Save meal** (tomato, then "Saved to My
   meals" in green) and **Try another craving**, plus the dish illustration on the right.
2. **Estimate notice** (amber), whenever any ingredient is estimated. The copy is today's.
3. **Nutrition:** the kcal ring (served kcal against the meal target; the arc fills to
   min(served / target, 1), and the text gives both numbers), the macro donut with grams and
   percentages beside it, then the range bars: each macro's bar in its Viridis colour over a green
   band for its range, with an "(outside)" label when it is out of range. The verdict stays the
   service's.
4. **Where the calories come from:** one stacked bar, a segment per ingredient sized by its
   `calories_kcal` and coloured from the six-step Viridis ramp, largest first. Below it is the
   ingredient list: a colour key, the name, an Estimated or Reference tag, grams and kcal.
5. **Also close to your craving:** up to three runners-up from `meal_plan.retrieval.candidates`,
   leaving out the served meal. A button sends a new plan request with that meal's name as the
   craving and the same profile.
6. **How this plan was made:** a folded `<details>` with today's notes.

The right column (it stacks below on a phone):

7. **Shopping list:** today's aisle grouping, ticks, notes and total, plus **Copy list** (plain
   text to the clipboard) and **Print** (a print stylesheet that prints only the list).
8. **How was it?** (`ink` card): a five-star radio group and an optional note, sent together with
   **Save rating**. One rating per plan can be sent. After sending, the card shows the stars it
   sent.

Every state in `docs/8_design.md` §3.3 keeps its copy. An infeasible plan has no meal, so it
shows no charts, Save, rating or shopping list. A fallback plan keeps its notice under the banner.
A missing field still leaves its section out.

### 4.4 My meals and Past plans

- **My meals** (`/meals`): a grid of the same cards as Home. The data is `GET /saved-meals/{id}`,
  de-duplicated by `request_id`, newest first.
- **Past plans** (`/history`): today's history list, restyled as cards with the craving and kcal.
- Both open `/plans/:requestId`, which finds the response in `GET /meal-plans/{id}` and renders the
  plan page from it. Shopping ticks are never stored, so they start empty. A record that can't be found shows
  "This plan is no longer in your history" with a link back.
- Feedback is append-only on the server, so there is no "unsave". A saved meal's button reads
  "Saved to My meals" and is disabled. Adding unsave would be a backend change, listed in
  `docs/4_next_steps.md`.

### 4.5 Hosted mode

`/health` reports `hosted_mode`. Today's rule stays: no `/health` call before the first plan
request. When a call to history, saved meals or feedback returns 501, the screen says "Saving,
ratings and history are off on this hosted server" instead of failing. After a 501, the Save and
rating controls are hidden. Planning a meal still works.

## 5. Remembering the person (supersedes the browser-storage rule in docs/8_design.md §3.1)

- `localStorage` key `aimp.v1` holds `{ userId, profile, location }`. Nothing else is stored:
  no plans, no ratings and no ticks.
- Every read and write is wrapped in try/catch. With storage blocked, the app works for the visit
  and says it can't remember you on this device.
- Profile page copy: "Your details are kept in this browser so you don't retype them. They go with
  each plan request, and when the app runs locally the server keeps a history of plans, including
  these details." The **Forget me on this device** button asks to confirm, then clears the key and
  returns to the first visit. It does not delete server history, and the confirm text says so.
- This becomes **DEC-36**, which supersedes the "never in localStorage" line of DEC-29.

## 6. Visual system ("Flat kitchen")

These changes go into `DESIGN.md` and `tailwind.config.js` in the same PR. That makes **DEC-37**.

- **Ground:** `#EEF4EF` (light green) replaces `#F6F7F2`. Cards are white with no border. Section
  tints are `#DCEEE1`. Banners use `ink`.
- **Macro colours (Viridis):** protein `#440154`, carbs `#2A788E`, fat `#22A884`. Each has at
  least 3:1 contrast on white. On `ink`, protein uses `#B9A3C8`.
- **Chart ramp:** `#440154 #414487 #2A788E #22A884 #7AD151 #FDE725`, used for categorical series
  in order and always with a text label. `#7AD151` and `#FDE725` are for fills on `ink` or beside
  a label, never for text on white.
- **Type:** Bricolage Grotesque 800 for headlines and big numbers (the self-hosted variable font
  gains the 800 weight), Inter for reading.
- **Icons:** `lucide-react` (ISC), a single outline set at 1.8 px stroke, 24–32 px, with no tile
  or background. It replaces DESIGN.md §5's "There is no icon set".
- **Illustrations:** flat SVG React components with no outlines or gradients, drawn from the
  palette plus food colours (rice `#FFF6E0`, chicken `#D9A066`, egg `#F2C14E`, salmon `#F08A5D`,
  curry `#D98E2B`). There are 12 dish types: rice bowl, stir fry, noodles, pasta, curry or chili,
  soup, salad, taco or wrap, eggs and toast, oats, plate, and a generic bowl. A pure function
  `dishType(mealName)` picks one by keyword, in that order, and falls back to the generic bowl.
  Each illustration is `aria-hidden` and shown as a kind of dish, never as a photo of the meal.
- **Shapes:** one soft blob behind each banner illustration, 24 px card corners, pill badges.
- **Tomato** stays the one loud thing: the primary button.

## 7. Code structure

```
src/
  app/        AppShell (top bar, routes), useStoredProfile (localStorage), routes.jsx
  pages/      HomePage, PlanPage, SavedMealsPage, HistoryPage, ProfilePage
  features/
    plan/     existing plan.js and shopping.js (kept), plus PlanBanner, NutritionCard,
              CalorieRing, MacroDonut, RangeBars, CalorieSources, RunnersUp,
              ShoppingList (restyled), RatingCard
    meals/    MealCard, useSavedMeals, useHistory
    profile/  existing ProfileForm and profile.js (kept)
    craving/  existing craving.js and CravingSuggestions (kept)
  components/illustrations/  DishIllustration, dishType.js, one file per dish
```

`features/flow/MealFlow.jsx` and `StepIndicator.jsx` go away. Their request building, validation
and stale-result guard move into a `usePlanRequest` hook shared by Home, the runners-up and Profile.
Charts are plain SVG components, with no chart library.

## 8. Testing

- Every guarantee in `docs/8_design.md` §5 stays: no network on first render, the exact meal
  request payload, the error banner and retry, the stale-result guard, and the meal-quality
  regressions. Tests that pinned the three-step flow are rewritten against the routes.
- New unit tests cover `dishType`, the ring's and donut's arithmetic, the calorie-sources ordering,
  storage (including blocked storage and Forget me), runners-up filtering, saved-meal
  de-duplication, and the 501 hosted messages.
- New component tests cover Save, the rating payload sent to `POST /meal-feedback`, Copy list, and
  keyboard use of stars and ticks.
- Browser check at 1280 and 390 px with the keyboard, and screenshots go to the owner before the PR
  merges.

## 9. Build order

Each slice is a commit on one branch. The owner asked for a single PR, merged when tests pass.

1. Tokens, fonts, `lucide-react`, illustrations and `dishType`.
2. App shell, router, stored profile, first visit and the Profile page.
3. Home.
4. Plan page: banner, nutrition charts, calorie sources and runners-up.
5. Shopping list actions, and Save and rating.
6. My meals, Past plans and `/plans/:requestId`.
7. Docs: DESIGN.md, docs/8_design.md, DEC-36, DEC-37, README (React main, Streamlit backup),
   next steps and the agent log.
