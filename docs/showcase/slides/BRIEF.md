# Showcase deck brief

**Status: deck approved by Mike on 7 November 2026: 16 slides, in the live Google Slides deck.**

This file decides what the deck says. [DESIGN.md](DESIGN.md) decides how it looks. The
[live Google Slides deck](https://docs.google.com/presentation/d/1KGb2_smqGofSohDuDjxM5hCyvOZyz5uDUbWdUn2US_4/edit)
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
| 04 Build and limits | How is it built, what is unproven, and what is pending? | 12–15 |
| Close | Where do I try it? | 16 |

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
- **Content:** "What should I eat tonight?" A search bar reading "chicken fried rice". "One meal sized to you, each ingredient's source shown, the shopping list ready." Three plate labels: Chicken breast, 100 g, Estimated; Cooked rice, 220 g, Estimated; Vegetables, 115 g, Reference. A tag: 694 kcal, target 691. A receipt: the six items and Estimated $24.50.
- **Visual:** `ink` background, calendar plate logo with the name top left, our own plate illustration cropped at the bottom (`assets/cover-art.png`), a tilted receipt in Google Sans Code, a small QR code at bottom left with "Try the live demo".
- **Elsewhere:** Mike's name goes on slide 14.

**Slide 2. Executive summary: "One craving, sized to four different people"** (new)
- **Question:** if I read one slide, what should I know?
- **Message:** what it does, the features behind it, and the numbers that prove it.
- **Content:** chicken fried rice at 363, 694, 809 and 850 kcal (26, 48, 60, 63 g protein) for four benchmark profiles. Four features, each with key terms highlighted and the number that proves it: sized to you (0.4% median gap to the meal target, worst 9.9%); fits your limits (5 of 5 guardrail cases, on a controlled recipe set); balanced and checked (72 of 72, up from 10, 11 of them fallback meals); ready to shop ($24.50 estimated basket for the 694 kcal plan, not a cost per meal). A note states that meal targets stay within 350–850 kcal. Subtitle: four agents, 34 curated recipes, no LLM key.
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
- **Content:** a speech bubble, "I feel like pasta tonight.", then three questions with facts: budgets from 1,200 to 4,521 kcal; asked for pasta, a vegan gets lentil bolognese and a coeliac gets gluten-free pasta; this pasta means five ingredients to find and price.
- **Visual:** an ink panel with a pasta plate, beside three tinted question cards, each with a small Today to With the app flow.
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
- **Visual:** an order ticket feeding four kitchen stations, each with a flat illustration and aligned text: portion planner, chef, taster, shopper. The roles are a metaphor.
- **Question:** what happens behind the screen?
- **Message:** the four steps, and the core path works with no LLM key.
- **Content:** Calorie expenditure: estimates daily expenditure and sets the daily budget. Meal recommendation: sets the meal target, excludes conflicting meals, picks a relevant recipe and sizes its portions. Nutrition verification: looks up each ingredient and labels estimates. Supermarket: matches ingredients to store items or category prices. White labels follow the active woman's real plan: 2,469 kcal budget, 691 kcal target, 694 kcal with 3 of 6 estimated, $24.50 estimated. The service balances portions after verification. Output: one typed JSON response with meal, nutrition, shopping list and warnings.
- **Source:** `docs/2_architecture.md`, `docs/agents/`.
- **Elsewhere:** how each agent works (slides 7–9).

**Slide 7. "From your body to a meal target"** (`p5`)
- **Subtitle:** Worked example: an active woman who is keeping her weight gets a 691 kcal target for this meal.
- **Question:** how does it decide how much?
- **Message:** a four-step calculation with a safety floor.
- **Content, as a flow:** body and activity (2,344 kcal) → trained model adds exercise (+125 kcal) → goal (+250 to gain, −400 to lose, with a floor; here a 2,469 kcal budget) → this meal, 28% of the budget, kept to 350–850 kcal (691 kcal). A to-scale bar chart shows the day and the meal.
- **Evidence:** exercise-calorie model, validation R² 0.996 and MAE 2.2 kcal; Kaggle Playground dataset of 750,000 rows.
- **Takeaways:** 1. The score is for exercise calories, not daily needs; with default inputs the model adds about 110–140 kcal, 3–10% of the day. 2. Weight-loss budgets apply a floor of 1,200 kcal for women or 1,500 for men, capped at estimated expenditure. Without it, one test profile would get 986 kcal.
- **Note:** in the meal flow, exercise inputs use defaults (30 minutes, 100 bpm), and the activity multiplier may already count that exercise. The 28% share is a design choice.
- **Source:** `docs/agents/calorie_expenditure_agent.md`, `metrics.json`, `calorie_expenditure_agent.py`, `meal_recommendation_agent.py`, DEC-24, `docs/8_design.md` §3.1.

**Slide 8. "Hard limits first, then a relevant recipe"** (`p6`)
- **Subtitle:** A vegan asks for chicken fried rice: the recipes narrow down to one, and the app ends in one of three ways.
- **Question:** how does it choose the meal?
- **Message:** three honest outcomes: close match, standard meal with a note, or refusal.
- **Content:** a funnel from one real request: 34 recipes, 13 safe, 5 relevant, 1 served (Tofu Fried Rice). Three outcomes with examples and counts: close match, 61 of 72; no close match, 11 of 72; nothing safe, 2 of 5 guardrail cases on a controlled recipe set. A fourth card shows a safe swap: gluten-free pasta for a coeliac.
- **Takeaways:** 1. Safety comes before taste: a recipe that breaks a limit is out, or adapted, before relevance counts. 2. Relevance decides what qualifies; an off-menu craving falls back with a warning, and the profile only changes the order.
- **Source:** `docs/agents/meal_recommendation_agent.md`, `backend/app/rag/retriever.py`, DEC-27, `docs/7_meal_quality.md`.
- **Elsewhere:** results (slide 11).

**Slide 9. "Each ingredient is looked up, and estimates are labelled"** (`p7`)
- **Subtitle:** Example: Chicken Fried Rice from a real local run with no provider keys.
- **Question:** can I trust the numbers?
- **Message:** every value shows its source, and estimates are visible.
- **Content:** ingredient table with kcal and badges; a stacked bar of the 694 kcal (459 estimated, 235 reference); lookup order: trusted local reference first; otherwise cached or provider lookup (USDA, then FatSecret if configured); then local or category estimates.
- **Takeaways:** 1. 3 of 6 ingredients are estimates, and they carry 66% of the calories. 2. With no provider keys, values come from local tables, so "Reference" is local too and nothing here is externally verified.
- **Source:** run of 6 November 2026 (34, male, 165 cm, 65 kg, moderately active, maintain): 694 kcal against 691, 48/78/19 g, 28/46/26%; `backend/app/agents/nutrition_verification_agent.py`.

**Takeaway columns, 7 November 2026.** Only slides 7 to 14 have takeaways, three each with supporting points and key terms; the exact text is in `build_deck.js`. Slides 2 to 6 and 15 are full width. Earlier wording, kept for reference: Slide 4: fourfold range, limits change the meal, framing. Slide 5: two screens, the plan shows its working. Slide 6: one job per station, retrieval not generation. Slide 7 adds that 28% is a design choice. Slide 10: only 10 of 72 first cleared both tests though 68 hit calories; fixed requests make runs fair.

### 03 Evidence

**Slide 10. "We defined a good meal before improving one"** (`p8`)
- **Subtitle:** A plan passes only if it clears both tests, on a fixed set of 72 requests run offline.
- **Question:** what counts as good?
- **Message:** a plan passes only if calories and all three macros are in range.
- **Content:** two tests, with one real plan (28/46/26%) marked on the bands, and 72 dots for the requests. Calories within 10% of target; protein 10–35%, carbs 45–65%, fat 20–35% of energy. 72 requests: 12 cravings × 4 body profiles, plus 6 cravings × 4 diet or health limits.
- **Limit:** AMDR is a daily reference, applied here to one meal.
- **Source:** `docs/7_meal_quality.md` §1, DEC-25.

**Slide 11. "Three fixes took the planner from 10 to 72 of 72"** (`p9`)
- **Subtitle:** Plans meeting both targets on the project's own benchmark, and what each fix changed.
- **Question:** did it get better, and why?
- **Message:** each change is measured. Balancing and the final step kept the served meals; the relevance gate moved 11 off-menu scenarios to fallback meals, which accounts for the rise to 47.
- **Figure values:** First run 10. Portion balancing 41. Honest fallback 47. Cooking fat and rounding retry 72.
- **Content:** median calorie deviation 0.4%, worst 9.9%. 5 of 5 guardrail cases hold. Wider check, 68 of 68.
- **Takeaways:** 1. 61 plans match the craving; 11 are fallbacks, and both pass. The 41 to 47 step came from those 11 moving to fallback meals, not from better meals; 8 of them are pizza and dessert. 2. 68 of 72 plans include an estimated ingredient, because the benchmark runs without provider keys. 3. The fixes were tuned on these 72. Asked for by name, recipes passed only 49 of 68 until a further fix made it 68 of 68, and neither shows that users prefer the plans.
- **Source:** `docs/7_meal_quality.md` §2, `docs/meal_quality/baseline.md`, DEC-26 to DEC-28.

### 04 Build and limits

**Slide 12. "One service, two clients, four agents"** (new)
- **Subtitle:** A request flows left to right. Each box names the model, data or tool behind it.
- **Question:** what is it made of?
- **Message:** one typed service serves two clients, and each agent has its own model or data source.
- **Content:** a diagram: clients (Streamlit; React, Vite, Tailwind) → FastAPI and Pydantic, with SQLite history → MealPlanningService: calorie expenditure (HistGradientBoosting), meal recommendation (TF-IDF, diet rules), nutrition verification (local tables, USDA, FatSecret), a balance and reconcile step (SciPy), supermarket. A "Built with" row: Python, Docker, GitHub Actions, Cloud Run, OpenTelemetry, Gemini. Logos are used only here.
- **Takeaways:** 1. Both clients use the same planning service. 2. The trained model is 0.64 MB, and TF-IDF is enough for 34 recipes. 3. Balancing runs after lookup, before the shopping list.
- **Note:** the hosted demo runs the agents inside Streamlit. Cloud Run is ready but not deployed.
- **Source:** `docs/2_architecture.md`, `pyproject.toml`, `frontend/package.json`, DEC-2.

**Slide 13. "Built like a product, not a notebook"** (`p10`)
- **Subtitle:** Six production habits, in the order a change travels through them, each with a file behind it.
- **Question:** is the engineering real?
- **Message:** a change passes six habits on its way to production; four run today and two wait for a GCP project.
- **Content:** a delivery line: contract, tests, security, container (green); Cloud Run, tracing (amber), each with its file. Three panels: 630 Python tests (538 backend, 92 Streamlit); 95% coverage against an 89% floor; the 5 CI checks by name.
- **Takeaways:** 1. CI stops drift. 2. Built isn't live: no GCP project exists yet. 3. Privacy is tested, but a real trace still has to arrive in Cloud Trace.
- **Limit:** the Cloud Run workflow is ready but not yet deployed to a GCP project.
- **Source:** `docs/openapi.json`, `.github/workflows/`, `docs/6_deployment.md`, `docs/5_agent_log.md`.

**Slide 14. "What this project does not prove yet"** (new)
- **Subtitle:** The further right, the less has been shown.
- **Question:** what is unproven?
- **Message:** the results are real, and their limits are stated in one place.
- **Content:** an evidence staircase. Measured: 72 of 72 and 68 of 68 offline; the checks guided the fixes; 11 of 72 fall back. Estimated: 68 of 72 include an estimate; AMDR on one meal; default exercise inputs; name-matched diet rules. Not tested: no users, no clinical review, not deployed, no migrations, taste and health unknown. Not medical advice.
- **Takeaways:** what is solid, what is soft, what is unknown.
- **Source:** `docs/4_next_steps.md` §7, `docs/7_meal_quality.md`, DEC-31, AGENTS.md.

**Slide 15. "What comes next, in priority order"** (`p11`)
- **Subtitle:** How the project got here, and the work still ahead.
- **Question:** what comes next?
- **Message:** nine open tasks, in the order they should be done.
- **Content:** a milestone line (8 Oct refactor, 11 Oct keys, deploy workflow and tracing, 18 Oct 72 of 72, 21 Oct React design, 7 Nov 68 of 68 and the gluten fix), above a Now, Next, Later board of nine notes: migrations, Cloud Run, accounts; USDA benchmark, exercise details, allergen tags; recipes, live prices, feedback and user testing.
- **Takeaways:** fix what visitors see first; accuracy before scale; people matter most.
- **Source:** [../pending-tasks.md](../pending-tasks.md), `docs/4_next_steps.md` §6, §7.

### Close

**Slide 16. "Try it and read the code"** (`p12`)
- **Content:** live demo link, GitHub link, QR code, "A multi-agent meal planner, a portfolio project by Mike", "A study project. Not medical advice." "The demo is the Streamlit client and may take a minute to wake."
- **Visual:** matches the cover.

## 5. Open items

- Confirm speaker notes came through conversion, then apply the note typography in DESIGN.md.
- Slide 3's lower half is empty; consider a taller layout.
- The app's own step 1 panel says a trained model "estimates the energy you burn in a day". That is loose against the exercise-calorie claim rule, and is an app copy decision, not a deck one.
- Slide 7 pass: without a duration, the model is fed a default 30-minute session at 100 bpm, so check how the deck describes its role.
- Rebuild the poster and LinkedIn image to the new standards once the deck's content is approved.

## 5a. Record check, slides 7 to 14

Checked 7 November 2026 against the code, `baseline.json` and fresh runs with no provider
keys. Mike approved these on 7 November 2026: section 4 changed first, then the slides. PRs #43
and #45 have since merged, so 49 of 68, 0.3% and 601 tests became 68 of 68, 0.4% and 630, and the
slide numbers below 12 are unchanged but 12 to 14 moved to 13 to 16. See [../pending-tasks.md](../pending-tasks.md).

| Slide | Record | Result | Proposed change |
| --- | --- | --- | --- |
| 7 | Four-step flow, +250/−400, 28%, 350–850 | Correct | None |
| 7 | R² 0.996, MAE 2.2 kcal, 750,000 rows | Correct, on Kaggle data | Add why it matters less: with default inputs the model adds about 110–140 kcal, 3–10% of expenditure |
| 7 | Exercise inputs use defaults | Correct | Add as a limit: the activity multiplier may already count that exercise, so the model's calories can double count it |
| 7 | Floor of 1,200 or 1,500 kcal | Correct | Add the example: the older woman's budget would be 986 kcal without it |
| 7 | 350–850 kcal | Correct, but the 28% has no recorded reason | State it as a design choice. The athlete's meal is capped at 19% of the day |
| 8 | Limits checked before scoring | Correct (`retriever.py`) | Add that limits can swap an ingredient as well as exclude a recipe |
| 8 | Three outcomes | Correct | Add counts: 61 matched and 11 fallback of 72; refusal appears only in 2 guardrail cases |
| 8 | "Vector similarity" | Correct but vague | Say TF-IDF, which is what runs at 34 recipes |
| 9 | Table and 3 of 6 estimated | Correct | None |
| 9 | Lookup order | Correct | Add that "Reference" still means local, and no benchmark value is externally verified |
| 10 | Targets and 72 requests | Correct; targets were set on 17 October, before the first fix | None |
| 11 | 10, 41, 47, 72 | Correct | Say the 41 to 47 step comes from 11 requests moving to fallback meals, not better meals. 8 of the 11 are pizza and dessert |
| 11 | 72 of 72 as the headline | Correct but incomplete | **Add the wider check:** the fixes were tuned on these 72. Asking for every recipe by name gives 49 of 68 on `main`, and PR #43 would make it 68 of 68 |
| 11 | Median 0.3% | Changes after PR #45 | Becomes 0.4% |
| 12 | 598 tests | Out of date | 601 collected on this branch; use a fresh full run after PRs #43 and #45 |
| 12 | Other five habits | Correct | None |
| 13 | Next and Not yet | Correct | Add the wider check and the oats question if still open |
| 14 | Notes: "every number showing how it was produced" | Overclaims | Match the cover: "each ingredient's source shown" |
| 14 | Live demo link | **Fails on first use.** It sleeps when idle and took about a minute to wake. It then opens with demo mode off, and Generate shows "Could not connect to the API". With the toggle on, a plan generates | Turn demo mode on by default in the Streamlit Cloud settings, then retest from a phone. Same fix covers the cover's QR code |
| 5, 14 | Demo versus deck | The QR opens the Streamlit demo, not the React app slide 5 shows | Say so on slide 14, or host the React app |

## 6. Decisions

Decided by Mike, 6 November 2026:

1. **Type:** Google Sans for the showcase (changed from Bricolage and Inter, 6 November). The app keeps its own fonts.
   **Colour:** Garden green on a white canvas.
   **Logo:** plate on a calendar.
   **App:** keeps its own UI fonts and, for now, its logo.
2. **Audience:** portfolio viewers, reading with no presenter. The deck can also be presented.
3. **Length:** 14 slides, adding an executive summary and agenda. Now 16, with architecture and limits slides.
4. **Slide 5:** capture the real React app.
5. **Poster order:** rebuild the poster after the deck's content is approved.
