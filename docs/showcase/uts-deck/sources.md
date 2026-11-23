# Sources

- Source ID: baseline
- Author or organisation: this project
- Title and date: Meal-quality benchmark report, rerun 7 November 2026 on `main`
- Path: docs/meal_quality/baseline.json and baseline.md
- Locator: summary block and chicken fried rice rows
- Supports: plan counts, calorie gaps, guardrails, budgets, the four plates
- Limits: offline, no provider keys; plans measured against fixed targets, not users
- Slides: summary, problem

- Source ID: corpus
- Path: data/meal_corpus/meals.json (34 recipes)
- Slides: summary

- Source ID: local-runs
- Title: local runs of the planning service with no provider keys, 6 and 7 November 2026
- Path: docs/showcase/slides/captures/2026-11-06-plan.json; pasta runs recorded in docs/showcase/README.md fact sheet
- Slides: problem, cover

- Source ID: illustrations
- Title: project-drawn flat plate illustrations, docs/showcase/slides/build_cover_art.py
- Licence: project's own artwork
- Slides: cover

- Source ID: workouts
- Author or organisation: this project
- Title and date: Workout check, 144 plans, 22 November 2026 on `main` after PR #57
- Path: docs/meal_quality/workouts.md and workouts.json; docs/7_meal_quality.md §5 (Workout days)
- Locator: Summary block and Workout days table
- Supports: 143 of 144, the average man's budgets, the long-workout fix, the one miss
- Limits: modelled workouts on fixed profiles; every request uses the 37 °C body-temperature default
- Slides: workouts, limits, next

- Source ID: usda-run
- Author or organisation: this project
- Title and date: Meal-quality benchmark with USDA FoodData Central, 23 November 2026, PR #59
- Path: docs/7_meal_quality.md §6 (With USDA data), DEC-41; docs/meal_quality/usda_baseline.md, usda_wider.md, usda_lookup_diagnosis.md
- Locator: results table and "What it found"
- Supports: 47 then 50 of 72, 64 then 72 within 10%, 108 then 113 of 152, shrimp 356 vs 85 kcal, 16 of 22 misses from the turkey match
- Limits: live search results, not repeatable; run on the owner's Mac because the cloud sandbox cannot reach the USDA API
- Slides: usda, limits, next

- Source ID: usda-pinned
- Author or organisation: this project
- Title and date: Meal-quality benchmark with pinned USDA FoodData Central IDs, 23 November 2026, PR #61
- Path: docs/7_meal_quality.md §7; data/reference/usda_fdc_ids.json; docs/meal_quality/usda_pinned_baseline.md, usda_pinned_wider.md
- Locator: results table and the eight wider misses
- Supports: 72 of 72, 144 of 152, 0 of 72 with an estimate
- Limits: live USDA by ID; run on the owner's Mac; Hass avocado and store-bought hummus kept on purpose
- Slides: usda, limits, next
