# Showcase deck brief

**Status: evidence lock clean; stages 3 and 4 applied in a 14-slide live deck, 6 November 2026. Standards revised: all choices made and applied in the restyled live deck; awaiting Mike's flip-through, then the deck is restyled.** Stage 5 items are in §5.

This file decides what the deck says. [DESIGN.md](DESIGN.md) decides how it looks. The
[live Google Slides deck](https://docs.google.com/presentation/d/1KpI1000mDr8I143nNIUvZvncuwm51mZvPYzZvAm7hGM/edit)
follows both. A design agent can work from this file alone: find the slide, read its fields,
then edit the live slide. When the story changes, change this file first, then the slide.
Numbers and sources are in the [fact sheet](../README.md#fact-sheet).

## 1. The story

**One sentence:** say what you crave and get one meal sized to your body and goal, with every
number showing how it was produced, and a measured check of whether the meals are any good.

**The thread:**

1. Choosing a meal is easy; sizing it to your body, diet and shopping is the work.
2. One request runs through four agents and returns one typed answer.
3. It is honest by design: estimates are labelled, and it says when nothing matches.
4. Quality was defined first, then measured: 10 of 72 plans became 72 of 72.
5. The limits are stated, and the next steps follow from them.

**Audience:** a portfolio reader, such as a hiring manager or lecturer, who may read it with no
presenter. Each slide has to make sense alone. It also works for a 10-minute talk.

**Tone:** plain and exact. Say what was measured, on what. Don't claim clinical value, user
outcomes or a better product than anyone else's. This is a self-directed portfolio project.

## 2. Workflow

Each stage ends at a gate. The next stage starts only after the gate passes.

| Stage | What happens | Who | Gate |
| --- | --- | --- | --- |
| 1. Brief | Agree story, slide list and content below | Claude drafts, Mike edits | Mike approves this file |
| 2. Evidence lock | Check every claim against its source | Codex | No open findings |
| 3. Structure pass | Reorder, add slides, set labels and agenda; no restyling | One editor | Mike flips through |
| 4. Content pass | Titles, subtitles, evidence, takeaways, notes, one section at a time | One editor per section | Mike approves each section |
| 5. Design pass | Apply DESIGN.md: grid, type, markers, spacing, figures | One editor | Rendered check of every slide |
| 6. Release | Codex review, export PDF, commit | Codex and Claude | Mike says push |

Only one agent edits the live deck at a time; say which before starting. A new number goes
into the fact sheet first. Each pass adds a short entry to `docs/5_agent_log.md`. Design waits
for stage 5, so nothing gets polished and then cut.

## 3. Section map

These names appear in the agenda and slide labels, so the two always match.

| Section | Reader question | Slides |
| --- | --- | --- |
| Opening | What is this, and what did it find? | 1–3 |
| 01 Problem | Why is this worth solving? | 4 |
| 02 Solution | What does it do, and how? | 5–9 |
| 03 Evidence | What is a good meal, and did we get there? | 10–11 |
| 04 Build and limits | How is it built, and what is still unproven? | 12–13 |
| Close | Where do I try it? | 14 |

| New | First deck | Label | Change |
| --- | --- | --- | --- |
| 1 | `p1` | none | Keep; light wording |
| 2 | new | EXECUTIVE SUMMARY | New slide |
| 3 | new | AGENDA | New slide |
| 4 | `p2` | PROBLEM > WHY IT MATTERS | Add label, subtitle |
| 5 | `p3` | SOLUTION > THE FLOW | Real captures if available |
| 6 | `p4` | SOLUTION > FOUR AGENTS | **Fix agent 1 wording** |
| 7 | `p5` | SOLUTION > CALORIE TARGET | **Rewrite: claim is wrong today** |
| 8 | `p6` | SOLUTION > CHOOSING THE MEAL | **Reword title**, add takeaways |
| 9 | `p7` | SOLUTION > NUTRITION | **Soften title, fix lookup order** |
| 10 | `p8` | EVIDENCE > WHAT GOOD MEANS | Add limits |
| 11 | `p9` | EVIDENCE > RESULTS | Add fallback split, guardrails |
| 12 | `p10` | BUILD AND LIMITS > ENGINEERING | **Update test count** |
| 13 | `p11` | BUILD AND LIMITS > NEXT STEPS | Light edits |
| 14 | `p12` | none | Keep |

## 4. Slide briefs

Titles are working titles.

### Opening

**Slide 1. Cover** (`p1`)
- **Message:** the question, the app's answer, and proof that it works. The app leads, not the author.
- **Content:** "What should I eat tonight?" A search bar reading "chicken fried rice". "One meal sized to you, every number explained, the shopping list ready." Three plate labels: Chicken breast, 100 g, Estimated; Cooked rice, 220 g, Estimated; Vegetables, 115 g, Reference. A tag: 694 kcal, target 691. A receipt: the six items and Estimated $24.50.
- **Visual:** `ink` background, calendar plate logo with the name top left, our own plate illustration cropped at the bottom (`assets/cover-art.png`), a tilted receipt in Google Sans Code, a small QR code at bottom left with "Try the live demo".
- **Elsewhere:** Mike's name goes on slide 14.

**Slide 2. Executive summary: "One craving, sized to four different people"** (new)
- **Question:** if I read one slide, what should I know?
- **Message:** what it does, the features behind it, and the numbers that prove it.
- **Content:** chicken fried rice at 363, 694, 809 and 850 kcal (26, 48, 60, 63 g protein) for four benchmark profiles. Four features, each with key terms highlighted and the number that proves it: sized to you (0.3% median calorie deviation); safe for your diet (5 of 5 guardrail cases); balanced and checked (72 of 72, up from 10); ready to shop ($24.50 estimated list for the 694 kcal plan). Subtitle: four agents, 34 curated recipes, no LLM key.
- **Visual:** three rows: four plates on an ink band, area to scale with calories; four feature cards; four key numbers. No takeaway column or markers.
- **Source:** fact sheet; `docs/meal_quality/baseline.json`.

**Slide 3. Agenda: "Today's menu"** (new)
- **Message:** four courses with page ranges.
- **Content:** Starter: Problem. Main: Solution. Taste test: Evidence. The bill: Build and limits. Each course lists its pages by slide label with the page number, like dishes and prices, and each is clickable.
- **Visual:** four tinted menu rows with icons and dotted leaders to the page, and a different dish on the right: the Salmon Quinoa Plate from the recipe library. Section names stay the same as the slide labels.

### 01 Problem

**Slide 4. "Picking a meal is easy; sizing it to you is not"** (`p2`)
- **Subtitle:** Three questions sit between a craving and a meal you can trust.
- **Question:** why build this?
- **Message:** the work is how much, whether it suits you, and what to buy.
- **Content:** a speech bubble, "I feel like pasta tonight.", then three questions with facts: budgets from 1,200 to 4,521 kcal; four diet and health limits; several ingredients to find and price.
- **Visual:** an ink panel with a pasta plate, beside three tinted question cards with icons.
- **Source:** `docs/1_brief.md`, `docs/meal_quality/baseline.json`, `docs/7_meal_quality.md` §1. The questions are framing in Mike's voice, not research findings.
- **Elsewhere:** how the app answers each one.

### 02 Solution

**Slide 5. "One craving in, one meal and a shopping list out"** (`p3`)
- **Subtitle:** Three steps in the React app.
- **Question:** what does using it look like?
- **Message:** you, craving, your plan.
- **Content:** three screens with short captions.
- **Visual:** real captures of the current React app, in `captures/`.
- **Source:** `docs/8_design.md`; capture target `frontend/src/features/flow/MealFlow.jsx`. `scripts/capture_screenshots.py` drives the old dashboard and is legacy, so `capture_app.py` here captured them.

**Slide 6. "Four agents work like one kitchen"** (`p4`)
- **Subtitle:** An order comes in, each station does one job, and a planning service runs them in order.
- **Visual:** an order ticket feeding four kitchen stations: portion planner, chef, taster, shopper. The roles are a metaphor.
- **Question:** what happens behind the screen?
- **Message:** the four steps, and the core path works with no LLM key.
- **Content:** Calorie expenditure: estimates daily expenditure and sets the daily budget. Meal recommendation: sets the meal target, excludes conflicting meals, picks a relevant recipe and sizes its portions. Nutrition verification: looks up each ingredient and labels estimates. Supermarket: maps ingredients to products with an estimated cost. The service balances portions after verification. Output: one typed JSON response with meal, nutrition, shopping list and warnings.
- **Source:** `docs/2_architecture.md`, `docs/agents/`.
- **Elsewhere:** how each agent works (slides 7–9).

**Slide 7. "From your body to a meal target"** (`p5`)
- **Subtitle:** A trained exercise-calorie model feeds a daily budget, then one meal's target.
- **Question:** how does it decide how much?
- **Message:** a four-step calculation with a safety floor.
- **Content, as a flow:** model predicts exercise calories → added to a BMR-based daily estimate → goal adjusts it (+250 kcal to gain, −400 to lose, subject to the floor) → meal target is 28% of the daily budget, kept between 350 and 850 kcal.
- **Evidence:** exercise-calorie model, validation R² 0.996 and MAE 2.2 kcal; Kaggle Playground dataset of 750,000 rows.
- **Takeaways:** 1. The score is for exercise calories, not daily needs. 2. Weight-loss budgets apply a floor of 1,200 kcal for women or 1,500 for men, capped at estimated expenditure, and a warning explains when it applies.
- **Note:** in the meal flow, exercise inputs use defaults (30 minutes, 100 bpm).
- **Source:** `docs/agents/calorie_expenditure_agent.md`, `metrics.json`, `calorie_expenditure_agent.py`, `meal_recommendation_agent.py`, DEC-24, `docs/8_design.md` §3.1.

**Slide 8. "Hard limits first, then a relevant recipe"** (`p6`)
- **Subtitle:** Incompatible recipes are excluded before selection, across 34 curated recipes.
- **Question:** how does it choose the meal?
- **Message:** three honest outcomes: close match, standard meal with a note, or refusal.
- **Content:** craving and profile → vector relevance and hard constraints → ranking → three outcomes.
- **Takeaways:** 1. Relevance alone decides whether a recipe qualifies, so an off-menu craving falls back with a warning; the profile only influences ranking. 2. If nothing is safe, it refuses.
- **Source:** `docs/agents/meal_recommendation_agent.md`, `backend/app/rag/retriever.py`, DEC-27, `docs/7_meal_quality.md`.
- **Elsewhere:** results (slide 11).

**Slide 9. "Each ingredient is looked up, and estimates are labelled"** (`p7`)
- **Subtitle:** Example: Chicken Fried Rice from a real local run with no provider keys.
- **Question:** can I trust the numbers?
- **Message:** every value shows its source, and estimates are visible.
- **Content:** ingredient table with badges; lookup order: trusted local reference first; otherwise cached or provider lookup (USDA, then FatSecret if configured); then local or category estimates.
- **Takeaways:** 1. 3 of 6 ingredients here are estimates, and the app says so. 2. With no provider keys, values come from local tables.
- **Source:** run of 6 November 2026 (34, male, 165 cm, 65 kg, moderately active, maintain): 694 kcal against 691, 48/78/19 g, 28/46/26%; `backend/app/agents/nutrition_verification_agent.py`.

### 03 Evidence

**Slide 10. "We defined a good meal before improving one"** (`p8`)
- **Subtitle:** Fixed targets on 72 requests, run offline and repeatably.
- **Question:** what counts as good?
- **Message:** a plan passes only if calories and all three macros are in range.
- **Content:** calories within 10% of target; protein 10–35%, carbs 45–65%, fat 20–35% of energy. 72 requests: 12 cravings × 4 body profiles, plus 6 cravings × 4 diet or health limits.
- **Limit:** AMDR is a daily reference, applied here to one meal.
- **Source:** `docs/7_meal_quality.md` §1, DEC-25.

**Slide 11. "Three fixes took the planner from 10 to 72 of 72"** (`p9`)
- **Subtitle:** Plans meeting the targets on the project's own benchmark.
- **Question:** did it get better, and why?
- **Message:** each change is measured. Balancing and the final step kept the served meals; the relevance gate moved 11 off-menu scenarios to fallback meals, which accounts for the rise to 47.
- **Figure values:** First run 10. Portion balancing 41. Honest fallback 47. Cooking fat and rounding retry 72.
- **Content:** median calorie deviation 0.3%, worst 9.9%. 5 of 5 guardrail cases hold.
- **Takeaways:** 1. 61 plans match the craving; 11 are honest fallbacks, and both pass. 2. 68 of 72 plans include an estimated ingredient, because the benchmark runs without provider keys. 3. This shows plans meet targets, not that users prefer them.
- **Source:** `docs/7_meal_quality.md` §2, `docs/meal_quality/baseline.md`, DEC-26 to DEC-28.

### 04 Build and limits

**Slide 12. "Built like a product, not a notebook"** (`p10`)
- **Subtitle:** Production habits on a portfolio project.
- **Question:** is the engineering real?
- **Message:** six habits, each with a file behind it.
- **Content:** typed API contract checked in CI; 598 Python tests at 95% coverage; API keys and rate limits; containers and a Cloud Run workflow; tracing that keeps health data out; two clients.
- **Limit:** the Cloud Run workflow is ready but not yet deployed to a GCP project.
- **Source:** `docs/openapi.json`, `.github/workflows/`, `docs/6_deployment.md`, `docs/5_agent_log.md`.

**Slide 13. "What comes next, and what it is not yet"** (`p11`)
- **Subtitle:** The next steps follow from the limits.
- **Question:** what is unproven?
- **Message:** next steps and limits, side by side.
- **Content:** Next: a larger recipe library; learning from user feedback; a live Cloud Run deployment. Not yet: live store prices; full verified nutrition; any user or clinical testing. Not medical advice.
- **Source:** `docs/4_next_steps.md` §6, §7.

### Close

**Slide 14. "Try it and read the code"** (`p12`)
- **Content:** live demo link, GitHub link, QR code, "A multi-agent meal planner, a portfolio project by Mike", "A study project. Not medical advice."
- **Visual:** matches the cover.

## 5. Open items

- Confirm speaker notes came through conversion, then apply the note typography in DESIGN.md.
- Slide 3's lower half is empty; consider a taller layout.
- The app's own step 1 panel says a trained model "estimates the energy you burn in a day". That is loose against the exercise-calorie claim rule, and is an app copy decision, not a deck one.
- Rebuild the poster and LinkedIn image to the new standards once the deck's content is approved.

## 6. Decisions

Decided by Mike, 6 November 2026:

1. **Type:** Google Sans for the showcase (changed from Bricolage and Inter, 6 November). The app keeps its own fonts.
   **Colour:** Garden green on a white canvas.
   **Logo:** plate on a calendar.
   **App:** keeps its own UI fonts and, for now, its logo.
2. **Audience:** portfolio viewers, reading with no presenter. The deck can also be presented.
3. **Length:** 14 slides, adding an executive summary and agenda.
4. **Slide 5:** capture the real React app.
5. **Poster order:** rebuild the poster after the deck's content is approved.
