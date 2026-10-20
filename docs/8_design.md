# Product Design — React showcase

**Status: proposal for discussion (2026-10-21).** Nothing here is built.
The owner and Codex review it in `docs/5_agent_log.md` first. Once it is
agreed, the decisions it settles go to `docs/3_decisions.md` and the work
moves into `docs/4_next_steps.md`.

The owner wants the React dashboard to become a proper web app, in the
spirit of the FarmLens showcase. The first target is a **polished local
showcase** (owner's choice, 2026-10-20), not a public app.

## 1. Goal and scope

Someone opens the app, says who they are and what they feel like eating,
and gets one meal they can trust plus a shopping list. Every number on
screen comes from the service and says how it was produced.

In scope:

- one guided flow in the React client: profile and goal, then craving,
  then the plan;
- a visual identity: name treatment, mark, colour, type and components;
- every state the API can return: matched, fallback, infeasible,
  rebalanced or outside the ranges, estimated nutrition, errors;
- desktop and phone layouts, keyboard use and screen readers.

Out of scope until decided separately:

- public hosting and browser access to a keyed API (DEC-7, DEC-8);
- accounts, saved plans and durable history (hosted history is off by
  design);
- live store prices or stock, cooking steps, meal photos (the API has
  none of these);
- a Streamlit redesign. Streamlit stays the working demo and reference
  client.

## 2. Prototype

Three linked screens, built from a real service response (Chicken Fried
Rice for a 34-year-old woman maintaining her weight: 629 kcal against a
625 kcal target, 27/46/27 split).

| Screen | Desktop | Phone |
| --- | --- | --- |
| 1 · Profile and goal | ![](assets/design/1-profile-desktop.png) | ![](assets/design/1-profile-mobile.png) |
| 2 · Craving | ![](assets/design/2-craving-desktop.png) | ![](assets/design/2-craving-mobile.png) |
| 3 · Your plan | ![](assets/design/3-plan-desktop.png) | ![](assets/design/3-plan-mobile.png) |

The static HTML is in `docs/design/prototype/`; open
`1-profile.html` in a browser and click through. It is a mockup only:
inputs do nothing and it calls no API. Screenshots were taken with
Chromium at 1280 px and 390 px wide.

## 3. The flow

### 3.1 You (profile and goal)

Collects what `MealRequest` already accepts: `goal` (lose, maintain,
gain), `age`, `sex`, `height_cm`, `weight_kg`, `activity_multiplier`,
`dietary_preferences` and `health_conditions`. Today the meal tab sends
only `user_id`, `craving` and `location`, and the calories tab keeps its
own biometric state, so the meal is never sized to the person in the
browser. This screen fixes that gap; it is functional, not cosmetic.

- Activity is a plain-language select mapped to the multiplier.
- Avoid-chips map to the restriction and condition values the service
  already understands; only offer values it handles.
- Kept in memory for the session only; nothing is saved ("Nothing here is
  saved"). `user_id` stays a generated opaque value, out of sight.
- A side panel explains how the meal is sized (model, goal and floor,
  balancing, verification) and says it is not medical advice.

### 3.2 Craving

One large input, suggestion chips drawn from real corpus meals, and the
shopping location. Three short promises underneath, each true today:
matched to a tested menu, honest when nothing is close, shopping list
included.

### 3.3 Your plan

One response, top to bottom:

- **Header:** "For your craving …" (the submitted craving, never the live
  input), meal name, description, badges: match quality, target result,
  dietary flags.
- **Calories:** this meal against its target; protein, carbs and fat in
  grams.
- **Balance:** each macro's share of the served calories (computed from
  `nutrition`, as #32 does) on a bar with the recommended range shaded.
- **Ingredients:** served portions in grams.
- **How this plan was made:** collapsed; the service's warnings in plain
  words (match terms, daily estimate, scaling, rebalancing, estimated
  nutrition).
- **Shopping list:** store, items by aisle with estimated prices and a
  checkbox each, total, and the note that prices are estimates from a
  local reference list.

States the screen must cover, each with its own copy:

| State | What the person sees |
| --- | --- |
| Matched, on target or rebalanced | As in the prototype |
| Fallback (`plan_status: fallback`) | A notice that nothing on the menu is a close match for the craving, then the standard meal |
| Outside the ranges (`no_feasible_balance`, `reverted`) | Amber badge; the bars show where the served split falls outside the band |
| Estimated nutrition | Each estimated ingredient marked; a line saying so |
| Infeasible (`plan_status: infeasible`) | No meal; the service's reason and a way back to change the profile or craving |
| Loading | The three steps the service runs, without fake progress |
| API unreachable or error | The existing error copy, with a retry |

## 4. Visual identity

One look, named "Kitchen green": calm, food-adjacent, confident.

- **Mark:** a ring and dot (a plate seen from above), in tomato.
  `frontend/src/assets/brand/logo-mark.svg`, `logo-wordmark.svg`; the
  favicon is the same mark.
- **Name:** "AI Meal Planner" for now. A product name is the owner's call.
- **Colour** (`docs/assets/design/palette.svg`):

  | Token | Hex | Use |
  | --- | --- | --- |
  | ink | `#15291F` | Text, dark panels, active step |
  | muted | `#4B5B52` | Secondary text (7.2:1 on white) |
  | ground | `#F6F7F2` | Page background |
  | surface | `#FFFFFF` | Cards |
  | line | `#DDE3DA` | Borders |
  | accent | `#C8431F` | Primary buttons, mark (white text 4.9:1) |
  | accent-text | `#B23A17` | Accent used as text |
  | success-bg / fg | `#E3EFE6` / `#1B5E3F` | Positive badges |
  | protein | `#2F6FAB` | Macro bar |
  | carbs | `#9A6A12` | Macro bar |
  | fat | `#7A4E9C` | Macro bar |

  The three macro colours differ in lightness as well as hue.
- **Type:** Bricolage Grotesque (700) for headings and big numbers, Inter
  (400–600) for everything else, from Google Fonts. Self-hosting them is
  an open question (§7).
- **Shape:** 10–14 px radius on inputs, 16–20 px on cards, pill chips and
  badges; borders over shadows.
- **Touch targets** at least 44 px; text contrast at least 4.5:1.

These become Tailwind theme tokens (`tailwind.config.js` `extend`), so
components use `bg-ink`, `text-muted` and so on, not raw hex.

## 5. Build plan

Small PRs, each green in CI and checked in a browser at 1280 and 390 px
with the keyboard before review:

1. **Tokens and shell.** Tailwind tokens, fonts, mark and favicon, page
   title, header with the step indicator. No behaviour change.
2. **Profile step.** A form for the `MealRequest` profile fields and
   held state; the request carries them. The calories tab's model call
   folds in here.
3. **Craving step.** Input, suggestions, location.
4. **Plan screen.** Header, calories, balance, ingredients, "how it was
   made", using today's response fields only.
5. **Shopping list** by aisle with estimates.
6. **States.** Fallback, outside the ranges, estimated, infeasible,
   loading, errors, each with a test.
7. **Retire the tabs.** History is off in hosted mode and has no place
   in the flow; it moves behind a small link or goes, per §7.

Tests: `App.test.jsx` is frozen and pins the three-tab layout and its
headings. The redesign replaces that layout, so the frozen file has to
change. This needs the owner's explicit OK; the replacement must keep
its guarantees (no network on first render, the meal request's payload,
the error banner) rather than weaken them.

## 6. What not to do

- Do not imply features the API does not have (photos, recipes,
  live prices, accounts).
- Do not hide quality warnings, the fallback notice or estimated
  nutrition to make the page look cleaner.
- Do not put an API key in the Vite bundle.
- Do not re-derive targets in the client; the service owns them.

## 7. Open questions

For the owner:

1. Approve the flow and the "Kitchen green" look, or say what to change.
2. Keep "AI Meal Planner" as the name, or pick another?
3. OK to replace the frozen `App.test.jsx` with flow tests that keep its
   guarantees?
4. History: drop it from the showcase, or keep a small "past plans" link
   for local mode?

For Codex:

5. Is anything in §3's state table missing or wrong against the API?
6. Should the profile live in the URL, memory only, or `sessionStorage`?
7. Self-host the two fonts, or keep Google Fonts for a local showcase?
