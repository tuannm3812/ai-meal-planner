# Meal Quality

The owner chose meal quality as the next product milestone on 2026-10-14:
the stateless demo stays, and the plans themselves get better. This file says
how quality is measured and what the first measurement found. Each change in
this milestone reruns the measurement and is judged against the baseline.

## 1. How it is measured

`scripts/meal_quality_baseline.py` runs a fixed set of 72 requests through the
real `MealPlanningService` (`backend/app/evaluation/meal_quality.py`):

- 12 cravings × 4 biometric profiles, with no extra constraints;
- 6 cravings × 4 constraint sets (vegan, hypertension, kidney disease,
  celiac) on the average profile.

The profiles span an older sedentary woman losing weight to a large athlete
gaining. Three cravings (`pizza`, `chocolate dessert`, `light soup`) were
chosen to test what happens with no close corpus meal; `light soup` turned
out to have one.

The run is offline and deterministic: no Gemini, USDA or FatSecret keys, and
an empty profile store, so every request also carries the built-in default
profile's restrictions (`dairy-free`, `high-protein`). Two runs produce
byte-identical output.

Per plan it records the plan status, the meal, the calorie target, the
verified calories that ship, their deviation from the target, the scale
factor, and the macro split as each macro's share of the meal's energy.

**The service has no macro targets**, so the split is checked against the
adult AMDR (protein 10–35%, carbohydrate 45–65%, fat 20–35% of energy). They
are a daily reference applied to one meal, so they answer "is this meal
balanced", not "is this meal wrong".

```bash
uv run python scripts/meal_quality_baseline.py                      # Markdown report
uv run python scripts/meal_quality_baseline.py --json out.json      # plus rows as JSON
```

## 2. Baseline, 2026-10-15

Full report: [`meal_quality/baseline.md`](meal_quality/baseline.md); rows:
[`meal_quality/baseline.json`](meal_quality/baseline.json).

| Measure | Baseline |
|---|---|
| Plans served | 72 of 72, all `matched` (no fallback, none infeasible) |
| Within the 15% calorie tolerance | 72 of 72 |
| Calorie deviation | median 1.6%, p90 8.5%, max 14.3% |
| Rescaled by reconciliation | 12 |
| First-pass scaling clamped (0.65–1.6) | 33 |
| All three macros inside AMDR | **11 of 72** |
| Protein / carbs / fat inside AMDR | 32 / 18 / 31 |
| Plans with an estimated ingredient | 68 of 72 |
| Corpus matches scoring below 0.25 | 11 |

## 3. What the baseline shows

1. **Calories are on target; macros are not balanced.** Every plan lands
   within tolerance, but only 11 of 72 have all three macros inside AMDR.
   Carbohydrate is low in 46 plans (under 45%), protein high in 40 (over
   35%), fat low in 34 (under 20%). Some meals are skewed the other way:
   Salmon Quinoa Plate is 46% fat and Chickpea Curry Bowl 70% carbohydrate.
   Part of the protein skew comes from the default profile's `high-protein`
   restriction, which favours high-protein meals in ranking (inferred from
   the retriever's preference bonus, `rag/retriever.py`).
2. **Off-menu cravings get an unrelated meal instead of the fallback.**
   `pizza` and `chocolate dessert` are served Chicken Fried Rice for every
   profile, with no matched terms, at a score of 0.198. That clears the
   retriever's 0.16 threshold only because of the preference bonus from the
   default profile's restrictions, so the deterministic fallback is never
   reached. Three constrained requests are similar: vegan `salmon dinner` and
   `high-protein burger` get a tofu noodle bowl, and kidney-disease
   `spicy curry` gets a turkey burger bowl (scores 0.18–0.19).
3. **The meal target ignores the extremes.** The target is 28% of the daily
   budget, clamped to 350–850 kcal. The large athlete's budget is 4,521 kcal,
   so its meal is capped at 850 (19% of the day). The older woman's is 986
   kcal, so her floor of 350 is 36% of the day.
4. **The smallest daily budget looks too low.** 986 kcal for a 62-year-old,
   52 kg woman losing weight is expenditure minus a fixed 400 kcal, with no
   floor (`CalorieExpenditureAgent._meal_budget`). Common guidance puts a
   floor near 1,200 kcal for women. This is a calorie-model question rather
   than a meal-quality one, so it is recorded here and not changed.
5. **Calorie accuracy is measured against local tables.** Offline, 68 of 72
   plans have at least one ingredient whose macros are estimated. So the
   tolerance result says the planner is consistent with its own tables, not
   that the meals truly have those calories. A run with a USDA key would
   test that, but it would no longer be deterministic.

## 4. Suggested order of work

Each item is a separate PR that reruns the baseline and reports the change.

1. **Macro-aware selection and scaling** (finding 1). Add macro targets for a
   meal, use them when ranking candidates, and scale the components (protein,
   carbohydrate, fat sources) separately instead of by one factor.
2. **Relevance gate on craving terms** (finding 2). Stop the preference bonus
   alone from carrying a meal over the threshold, so an off-menu craving
   reaches the fallback or an honest "no close match".
3. **Corpus growth** (`4_next_steps.md` §7.9), aimed at the gaps the baseline
   shows: balanced vegan mains, kidney-safe options, and the cravings with no
   match today.
4. **Meal target at the extremes** (finding 3), once the owner decides how
   many meals a day the target assumes.

Finding 4 needs an owner decision before any change, since it alters the
calorie budget every client shows.
