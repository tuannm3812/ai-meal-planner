# AI Meal Planner claims register

Every substantive number on the slides, with its source. Benchmark figures come from the project's own
offline benchmark (no USDA or FatSecret keys), rerun on `main` after PRs #43 and #45, 7 November 2026.
They measure plans against fixed targets, not users. AMDR is a daily reference applied to one meal.

| Claim | Value | Source | Limits |
| --- | --- | --- | --- |
| Curated recipes | 76 | data/meal_corpus/meals.json on main after PR #49, 22 November 2026 | Was 34 before PR #49 |
| Agents | 4 (four) | backend/app/agents/ | |
| Chicken fried rice by profile | 363, 694, 809, 850 kcal | docs/meal_quality/baseline.json | Older woman losing; active woman, average man maintaining; large athlete gaining |
| Plans meeting targets | 72 of 72, up from 10 | docs/meal_quality/baseline.md; docs/7_meal_quality.md §2 | Offline benchmark; 11 of 72 are fallback meals |
| Median calorie gap | 0.5% (worst 9.9%) | scripts/meal_quality_baseline.py on main, 22 November 2026 | 72 of 72 still meet targets; 61 matched, 11 fallback |
| Guardrail cases | 5 of 5 | docs/meal_quality/baseline.json | Controlled recipe set |
| Plans with an estimated ingredient | 68 of 72 | docs/meal_quality/baseline.json | No provider keys |
| Fallback meals | 11 of 72 | docs/meal_quality/baseline.json | |
| Daily budgets | 1,200 to 4,521 kcal | docs/meal_quality/baseline.json | 1,200 is the weight-loss floor |
| Pasta ingredients | five (5) | Offline run of "pasta", average man, on main, 22 November 2026 | Tuna Pasta Salad |
| Example meal | chicken fried rice, 694 kcal against a 691 kcal target | docs/showcase/slides/captures/2026-11-06-plan.json | Local run, no provider keys |
| Daily budget example | 2,469 kcal: 2,344 body and activity + 125 exercise; meal 691 kcal (28%); rest of the day 1,778 kcal; exercise is 5% of the budget (125 of 2,469) | Local run, 7 November 2026 | Active woman maintaining |
| Exercise share | 3–10% of the day | Local run, 7 November 2026 | Default exercise inputs: 30 minutes, 100 bpm |
| Model score | R² 0.996 | models/calorie_expenditure/metrics.json | Exercise calories only |
| Recipe funnel | 76, 30, 6, 1 | Retriever on main, 22 November 2026 | Vegan asks for chicken fried rice; Tofu Fried Rice served |
| Matched and fallback | 61 of 72, 11 of 72 | docs/meal_quality/baseline.json | |
| Ingredients | 3 of 6 estimated; 165, 286, 72, 75, 8, 88 kcal; 100, 220, 50, 115, 15, 10 g; 66% | Local run, 7 November 2026 | 459 kcal estimated |
| Targets | 10%; protein 10–35%, carbs 45–65%, fat 20–35% | docs/7_meal_quality.md §1, DEC-25 | AMDR daily reference |
| Benchmark design | 12 × 4 profiles, 6 × 4 limits, 72 requests | docs/7_meal_quality.md §1 | |
| Results | 10, 41, 47, 72 (gains +31, +6, +25); 49 of 68 then 68 of 68; with 76 recipes, 152 of 152 | docs/7_meal_quality.md §2 | Fixes tuned on the same set |
| Model size | 0.64 MB | models/calorie_expenditure/metrics.json | |
| Tests | 662 (570 backend, 92 Streamlit), 97%, 89% floor, 5 CI checks | CI's pytest command on main, 22 November 2026; ci.yml | |
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
| Test split | 570 backend, 92 Streamlit | CI pytest command on main, 22 November 2026 | |
| Milestones | 8 Oct, 11 Oct, 18 Oct, 21 Oct, 7 Nov 2026 | AGENTS.md, Current state | |
| Recipe example | Tofu Fried Rice from 76 → 30 → 6 → 1 | Retriever on main, 22 November 2026 | |
| Cover receipt | $7.80, $3.20, $3.50, $3.50, $3.50, $3.00; total $24.50 | slides/captures/2026-11-06-plan.json | Category prices for 4 of 6 |
| Cover tags | Chicken breast 100 g, cooked rice 220 g, vegetables 115 g | Local run, 6 November 2026 | |
| Pasta for the average man | 2,889 kcal a day; 809 kcal meal target | Offline run of "pasta", average man, on main, 22 November 2026 (scripts/meal_quality_baseline.py service) | Same as docs/meal_quality/baseline.json "creamy pasta / average man" |
| Pasta swaps | Vegan: Lentil Bolognese Pasta instead of Tuna Pasta Salad; coeliac: gluten-free pasta | Same run | Coeliac swap is DEC-31 |
| Pasta shopping list | $3.50, $2.80, $3.50, $1.40, $3.50; $14.70 estimated | Same run, Coles Earlwood local reference | Tuna, cucumber and olive oil are category price estimates |
| Latest milestone | 22 Nov: 76 recipes, kitchen app, Cloud Run | PRs #47 to #52 merged 22 November 2026; deploy run 45010039893 | |
| Wider check | 152 of 152 | scripts/meal_quality_baseline.py --wider on main, 22 November 2026 | Every recipe by name, two profiles |
| Cloud Run live | API live in australia-southeast1, max 1 instance, live check passed | deploy.yml run 45010039893 on main (e6ef769), 22 November 2026 | Free tier, scales to zero; hosted mode stores nothing |
| First real trace | One POST /generate-meal-plan with five stage spans in Cloud Trace | Cloud Trace API read, project ai-meal-planner-515508, 22 November 2026 | Only sampled requests are traced; batches can be lost when Cloud Run throttles CPU |
| Workout check | 143 of 144 plans; 4 profiles × 6 workouts × 6 cravings; 1 miss: Tuna Pasta Salad at a 378 kcal target, carbs 43% | docs/meal_quality/workouts.md; docs/7_meal_quality.md §5 (Workout days), PR #57 | Modelled workouts, not measured ones; 37 °C default |
| Average man's budget by workout (BMR × 1.2 = 2,148; activity exercise 626) | rest 2,148 (was 2,774); 20 min walk at 95 bpm 2,211 (was 2,838, +63); 30 min jog at 120 bpm 2,378 (was 3,005, +230); 60 min run at 140 bpm 2,625 (was 3,251, +477); 90 min ride at 135 bpm 2,863 (was 3,490, +715) | docs/meal_quality/workouts.md, Workout days table | "Was" is the budget before DEC-40 |
| Long workouts | 60 minutes adds 477 kcal, was 238 (capped at 30 minutes) | docs/7_meal_quality.md §5 finding 2, DEC-39 | Average man; model trained on 1–30 minutes |
| USDA benchmark | 72, 64, 72 within 10% of calories; 72, 47, 50 meeting both targets (offline, first run, kJ fixed); wider check 152, 108, 113 of 152; guardrails 5 of 5 | docs/7_meal_quality.md §5 (With USDA data), PR #59; docs/meal_quality/usda_baseline.md, usda_wider.md | Live USDA search, not repeatable; run on the owner's Mac, 23 November 2026 |
| USDA lookup findings | shrimp read 356 kcal per 100 g, really 85; turkey-as-ham match causes 16 of 22 misses | docs/meal_quality/usda_lookup_diagnosis.md; docs/7_meal_quality.md §5 | 19 ingredients with trusted local values never sent |
