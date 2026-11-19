# AI Meal Planner claims register

Every substantive number on the slides, with its source. Benchmark figures come from the project's own
offline benchmark (no USDA or FatSecret keys), rerun on `main` after PRs #43 and #45, 7 November 2026.
They measure plans against fixed targets, not users. AMDR is a daily reference applied to one meal.

| Claim | Value | Source | Limits |
| --- | --- | --- | --- |
| Curated recipes | 34 | data/meal_corpus/meals.json | |
| Agents | 4 (four) | backend/app/agents/ | |
| Chicken fried rice by profile | 363, 694, 809, 850 kcal | docs/meal_quality/baseline.json | Older woman losing; active woman, average man maintaining; large athlete gaining |
| Plans meeting targets | 72 of 72, up from 10 | docs/meal_quality/baseline.md; docs/7_meal_quality.md §2 | Offline benchmark; 11 of 72 are fallback meals |
| Median calorie gap | 0.4% (worst 9.9%) | docs/meal_quality/baseline.md | |
| Guardrail cases | 5 of 5 | docs/meal_quality/baseline.json | Controlled recipe set |
| Plans with an estimated ingredient | 68 of 72 | docs/meal_quality/baseline.json | No provider keys |
| Fallback meals | 11 of 72 | docs/meal_quality/baseline.json | |
| Daily budgets | 1,200 to 4,521 kcal | docs/meal_quality/baseline.json | 1,200 is the weight-loss floor |
| Pasta ingredients | five (5) | Local run of "pasta", average man, 7 November 2026 | High-Protein Tomato Turkey Pasta |
| Example meal | chicken fried rice, 694 kcal against a 691 kcal target | docs/showcase/slides/captures/2026-11-06-plan.json | Local run, no provider keys |
| Daily budget example | 2,469 kcal: 2,344 body and activity + 125 exercise; meal 691 kcal (28%); rest of the day 1,778 kcal; exercise is 5% of the budget (125 of 2,469) | Local run, 7 November 2026 | Active woman maintaining |
| Exercise share | 3–10% of the day | Local run, 7 November 2026 | Default exercise inputs: 30 minutes, 100 bpm |
| Model score | R² 0.996 | models/calorie_expenditure/metrics.json | Exercise calories only |
| Recipe funnel | 34, 13, 5, 1 | Local run, 7 November 2026 | Vegan asks for chicken fried rice |
| Matched and fallback | 61 of 72, 11 of 72 | docs/meal_quality/baseline.json | |
| Ingredients | 3 of 6 estimated; 165, 286, 72, 75, 8, 88 kcal; 100, 220, 50, 115, 15, 10 g; 66% | Local run, 7 November 2026 | 459 kcal estimated |
| Targets | 10%; protein 10–35%, carbs 45–65%, fat 20–35% | docs/7_meal_quality.md §1, DEC-25 | AMDR daily reference |
| Benchmark design | 12 × 4 profiles, 6 × 4 limits, 72 requests | docs/7_meal_quality.md §1 | |
| Results | 10, 41, 47, 72; 49 of 68 then 68 of 68 | docs/7_meal_quality.md §2 | Fixes tuned on the same set |
| Model size | 0.64 MB | models/calorie_expenditure/metrics.json | |
| Tests | 630, 95%, 89% floor, 5 CI checks | Local full run, 7 November 2026; ci.yml | |
| Plan cost | $24.50 | Local run, 7 November 2026 | Category prices for 4 of 6 items |
| Next steps | 75–100 recipes | docs/4_next_steps.md §7.9 | |
| Weight-loss floor | 1,200 and 1,500 kcal | DEC-24 | |
| Exercise defaults | 30 minutes, 100 bpm | calorie_expenditure_agent.py | |
| Calorie split | 459 and 235 kcal; 66% and 34% | Local run, 7 November 2026 | |
| Chart axis | 2,500 kcal maximum on the calorie chart | Layout scale | Not a claim |
| Plate proteins | 26, 48, 60, 63 g | docs/meal_quality/baseline.json | |
| Capture profile | 34, male, 165 cm, 65 kg | slides/captures/2026-11-06-plan.json | |
| Goal adjustments | +250, −400 kcal; meal 350–850 kcal | calorie_expenditure_agent.py; meal_recommendation_agent.py | |
| Benchmark counts | 2 of 5 guardrail refusals; 6 recipes given oil | baseline.json; DEC-28 | |
| Test split | 538 backend, 92 Streamlit | Local full run, 7 November 2026 | |
| Milestones | 8 Oct, 11 Oct, 18 Oct, 21 Oct, 7 Nov 2026 | AGENTS.md, Current state | |
| Recipe example | Tofu Fried Rice from 34 → 13 → 5 → 1 | Local run | |
| Cover receipt | $7.80, $3.20, $3.50, $3.50, $3.50, $3.00; total $24.50 | slides/captures/2026-11-06-plan.json | Category prices for 4 of 6 |
| Cover tags | Chicken breast 100 g, cooked rice 220 g, vegetables 115 g | Local run, 6 November 2026 | |
| Pasta for the average man | 2,889 kcal a day; 809 kcal meal target | Local offline run of "pasta", average man, 19 November 2026 (scripts/meal_quality_baseline.py service) | Same as docs/meal_quality/baseline.json "creamy pasta / average man" |
| Pasta swaps | Vegan: Lentil Bolognese Pasta; coeliac: gluten-free pasta | Same run | Coeliac swap is DEC-31 |
| Pasta shopping list | $6.50, $2.80, $2.30, $3.50, $3.50; $18.60 estimated | Same run, Coles Earlwood local reference | Olive oil is a category price estimate |
