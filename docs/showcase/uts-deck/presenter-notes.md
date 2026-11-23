# Presenter notes

## 1. What should I eat tonight?

Introduce the app through the question everyone asks.

Everyone asks this question, so that's where this project starts. You type a craving, and you get one meal sized to you, with each ingredient's source shown and the shopping list already written.
The rest of this deck shows how it works and how I measured it.

References:
- sources.md

## 2. Agenda

Locate each section by its page number.

The deck runs from the problem, through how the planner works, to what was measured and what is still open.

References:

## 3. One craving, sized to four different people

If you read one slide, read this one.

This is the same craving for four people, so the meal fits the person.
That quality is measured: all 72 plans in the project's own benchmark meet the targets, up from 10.
It stays honest: estimates are labelled, and it says so when nothing matches.

References:
- sources.md
- claims-register.md

## 4. Picking a meal is easy; sizing it to you is not

Show the work that sits between a craving and a meal.

Most of us know what we feel like eating. The hard part comes after that.
The right amount depends on the person. Diets and conditions change the meal. And even one meal means several ingredients to find and price.
The next section shows how one request answers all three.
Sources: Benchmark budgets: docs/meal_quality/baseline.json; pasta examples: local run, 7 November 2026, no provider keys.

References:
- sources.md
- claims-register.md

## 5. One craving in, one meal and a shopping list out

Walk through the real app: details once, then search, then the plan page.

The first visit asks for your details once and keeps them on this device, including today's workout.
After that the home page is one search box: say what you feel like eating, or pick a suggestion.
The plan page shows the meal against its target, a macro donut, where the calories come from and a shopping list. You can save the meal and rate it.
Sources: Captures: docs/showcase/slides/captures/2026-11-22-plan.json; React app on main (ac4d44d), local run, 22 November 2026.

References:
- sources.md
- claims-register.md

## 6. Four agents work like one kitchen

Show the four agents and their real outputs.

The calorie agent sets a daily budget, the recommendation agent picks and sizes the meal, the nutrition agent labels estimates, and the supermarket agent prices the list.
The service balances portions after verification.
Sources: backend/app/services/meal_planning_service.py; local run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 7. From your body to a meal target

Follow one person from body to meal target.

Body size and activity give about 2,344 kcal a day. The trained model adds 125. Her goal is to maintain, so her budget is 2,469, and one meal gets 28%: 691 kcal.
Exercise adds only 5% here because the run uses default exercise inputs: 30 minutes at 100 bpm.
A weight-loss floor of 1,200 kcal for women and 1,500 for men protects low budgets.
Sources: calorie_expenditure_agent.py; models/calorie_expenditure/metrics.json; local run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 8. Hard limits come first, then a relevant recipe

Show the funnel from one real request.

Of 76 recipes, 30 are safe for a vegan, 6 are relevant to the craving, and one is served.
If nothing is close, you get a standard meal and a note. If nothing is safe, it refuses.
Sources: backend/app/rag/retriever.py; local run, 7 November 2026; docs/meal_quality/baseline.json.

References:
- sources.md
- claims-register.md

## 9. Each ingredient is looked up, and estimates are labelled

Show where each number came from.

Three of the six ingredients are estimates, but they include chicken and rice, the biggest items, so they carry 459 of the 694 kcal.
Sources: nutrition_verification_agent.py; local run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 10. We defined a good meal before improving one

Fix what good means before changing anything.

Dots: chicken fried rice for the active woman. AMDR is a daily reference, applied here to one meal.
Calories had to land within 10% of the target, and each macro inside the adult AMDR range. The same 72 requests run every time.
Sources: docs/7_meal_quality.md §1; DEC-25.

References:
- sources.md
- claims-register.md

## 11. Three fixes took the planner from 10 to 72 of 72

Show what each fix changed.

Resizing each ingredient took it to 41. The relevance gate moved 11 off-menu requests to fallback meals, giving 47. Adding a fat to six recipes and a rounding retry took it to 72.
The fixes were tuned on these 72, so I also asked for every recipe by name: 49 of 68 passed before a further fix, 68 of 68 after; with 76 recipes it is 152 of 152.
Sources: docs/7_meal_quality.md §2; docs/meal_quality/baseline.md; DEC-26 to DEC-30.

References:
- sources.md
- claims-register.md

## 12. One service, two clients, four agents

Show the whole system on one page.

Read left to right by stage, top to bottom inside a stage. Step 4 is the only exit: no close match falls back to a standard meal; nothing safe is refused.
Docker, GitHub Actions and the Cloud Run workflow are on the engineering slide. Gemini only writes an optional note, and only with a key.
Both clients use the same planning service, so the logic lives in one place.
The hosted demo runs the same service inside Streamlit.
Sources: docs/2_architecture.md; pyproject.toml; frontend/package.json.

References:
- sources.md
- claims-register.md

## 13. Built like a product, not a notebook

Show the production habits.

All six steps on the line run today: the API is live on Cloud Run in Sydney, capped at one instance.
The last full run, on main on 22 November 2026, passed 662 Python tests at 97% coverage. Five checks run on every pull request.
The first real trace reached Cloud Trace on 22 November 2026: one plan request, five stage spans, allowlisted fields only.
Sources: deploy.yml run 45010039893; ci.yml; docs/openapi.json; test_telemetry_redaction.py; local full run, 7 November 2026.

References:
- sources.md
- claims-register.md

## 14. What this project does not prove yet

Put the limits in one place.

Plans hit their targets on fixed requests, offline and on USDA data, but those requests guided the fixes. Calorie inputs are modelled. Nobody has used it yet.
Sources: docs/4_next_steps.md §7; docs/7_meal_quality.md §5 to §7; DEC-31, DEC-42.

References:
- sources.md
- claims-register.md

## 15. What comes next, in priority order

Pair the limits with the work that answers them.

Foundations first: migrations are done and accounts are next; the API went live on Cloud Run on 22 November, and the workout and USDA runs are in the appendix. Then better inputs. Then testing with people.
Sources: docs/4_next_steps.md §6 and §7.

References:
- sources.md
- claims-register.md

## 16. Thank you

Thank the audience and point to the demo and code.

Thank you. That's AI Meal Planner: one craving in, one meal sized to you, with each ingredient's source shown.
The demo and the code are linked here.

References:
- sources.md

## 17. A1. First visit: your details, asked once

Appendix: a closer look at one screen of the React app.

The first visit asks for these details once. Each field maps to one step of the calorie target or the safety rules.
Sources: docs/showcase/slides/captures/2026-11-22-plan.json and capture_walk_2026-11-22.py; React app on main (ac4d44d), local run with no provider keys, 22 November 2026.

References:
- sources.md

## 18. A2. Home: one search box

Appendix: a closer look at one screen of the React app.

Three meals were planned and saved before this capture, so the cards are filled.
Sources: docs/showcase/slides/captures/2026-11-22-plan.json and capture_walk_2026-11-22.py; React app on main (ac4d44d), local run with no provider keys, 22 November 2026.

References:
- sources.md

## 19. A3. The plan page: what it is and how it fits

Appendix: a closer look at one screen of the React app.

Ring, donut and bars use the app's Viridis macro colours: protein, carbs, fat.
Sources: docs/showcase/slides/captures/2026-11-22-plan.json and capture_walk_2026-11-22.py; React app on main (ac4d44d), local run with no provider keys, 22 November 2026.

References:
- sources.md

## 20. A4. Below the plan: sources, feedback and other options

Appendix: a closer look at one screen of the React app.

The rating here was 4 of 5 stars, given during the capture.
Sources: docs/showcase/slides/captures/2026-11-22-plan.json and capture_walk_2026-11-22.py; React app on main (ac4d44d), local run with no provider keys, 22 November 2026.

References:
- sources.md

## 21. A5. Workout days: today's workout replaces the usual week

Appendix: what the workout check measured and the two fixes it led to.

The fixed 72 requests send no workout. This check sends six: not given, rest day, a walk, a jog, a run and a ride, for each of the four profiles on six cravings.
The activity level already holds an average day's exercise: 626 kcal for this man. Before the fix, today's workout was added on top on 15 of 24 profile-days. Now a stated workout replaces it, so his run day falls from 3,251 to 2,625 kcal. A workout left out still adds the 30-minute default to the activity level.
The model was trained on 1 to 30 minutes, so 60 and 90 minutes used to count as 30. They now count per minute. Heart rates above 128 bpm are still read as 128, and every request uses the 37 °C body-temperature default, which is just below the training range.
The one miss: targets between about 360 and 390 kcal push Tuna Pasta Salad's carbs to 43%, because the pasta cannot shrink below half a portion.
Sources: docs/7_meal_quality.md §5 (Workout days); docs/meal_quality/workouts.md; DEC-39, DEC-40; PR #57.

References:
- sources.md
- claims-register.md

## 22. A6. With pinned USDA foods, 72 of 72 plans meet both targets

Appendix: the first benchmark run with independent nutrition data, and what it found.

The same 72 requests, with each ingredient's nutrition from USDA FoodData Central instead of the local tables. Nineteen ingredients with a trusted local value are never sent.
Searching USDA by name first read energy in kilojoules for foods that list both units, so shrimp came out at 356 kcal per 100 g instead of 85. With that fixed, 50 of 72 met both targets. Almost every miss had fat too high because the first search hit was the wrong food: avocado found avocado dressing, and lean turkey mince found minced ham, which alone caused 16 of the 22 misses.
Each of the 41 ingredients now has one reviewed USDA food, fetched by its ID. All 72 plans meet both targets, the median gap is 0.4%, and no plan uses an estimated ingredient. The wider check is 144 of 152: the misses are mostly Hass avocado and store-bought hummus, which Mike kept because they are what people buy.
Sources: docs/7_meal_quality.md §6 and §7; DEC-41, DEC-42; docs/meal_quality/usda_pinned_baseline.md, usda_pinned_wider.md, usda_lookup_diagnosis.md; PRs #59 and #61.

References:
- sources.md
- claims-register.md
