## Measured

- calorie_model_version: `hist_gradient_boosting_deep_v0.1.0`
- calorie_model_sha256: `33a154b3d5807af1e2dd53ee69dc250e3f9a4429bfed90260e27671eac168c95`
- meal_corpus_sha256: `cebde36f88214e2bb08e21243f64c99046e13c131ea038931209dc2d4423b33c`
- meal_count: `76`
- retriever: `tfidf_vector_retriever_v0.1`
- nutrition_source: `usda_fooddata_central`
- usda_lookups: `106`
- usda_lookup_failures: `0`
- usda_no_usable_match: `84`
- usda_ingredients_cached: `22`

## Summary

- Plans: 72 (fallback 11, matched 61).
- **Meeting the targets** (calories within 10%, all macros in AMDR): 47 of 72.
- Within the 10% calorie target: 64 of 72 scaled plans.
- Within the service's 15% retry tolerance: 64 of 72 scaled plans.
- Calorie deviation: median 0.8%, 90th percentile 16.5%, max 103.5%.
- Rescaled by reconciliation: 26. First-pass scaling clamped: 27.
- Meal target as a share of the daily budget: 18.8% to 29.2%.
- Daily budget across profiles: 1200.0 to 4521.1 kcal.
- Macro share inside AMDR: protein 72, carbs 51, fat 52; all three 51 of 72.
- Plans with at least one estimated ingredient: 41 of 72.
- Plans with at least one USDA-verified ingredient: 68 of 72.
- Corpus matches scoring below 0.25: 0.

## Plans

| Scenario | Status | Meal | Target | Verified | Dev. | Scale | P/C/F % | Score |
|---|---|---|---:|---:|---:|---:|---|---:|
| chicken fried rice / older sedentary woman, losing | matched | Chicken Fried Rice | 350 | 353.0 | 0.9% | 0.65 | 29/46/25 | 0.999 |
| high-protein burger / older sedentary woman, losing | matched | High-Protein Turkey Burger Bowl | 350 | 350.5 | 0.1% | 0.57 | 23/24/53 | 0.656 |
| creamy pasta / older sedentary woman, losing | matched | Tuna Pasta Salad | 350 | 355.3 | 1.5% | 0.65 | 27/47/26 | 0.612 |
| salmon dinner / older sedentary woman, losing | matched | Salmon Noodle Bowl | 350 | 345.1 | 1.4% | 0.65 | 21/46/33 | 0.566 |
| steak and rice / older sedentary woman, losing | matched | Lean Steak Rice Plate | 350 | 343.0 | 2.0% | 0.65 | 32/46/22 | 0.864 |
| spicy curry / older sedentary woman, losing | matched | Chickpea Curry Bowl | 350 | 350.1 | 0.0% | 0.65 | 15/64/21 | 0.435 |
| breakfast oats / older sedentary woman, losing | matched | Banana Oat Protein Bowl | 350 | 384.5 | 9.9% | 0.82 | 16/64/21 | 0.594 |
| taco bowl / older sedentary woman, losing | matched | Shrimp Taco Bowl | 350 | 712.3 | 103.5% | 0.56 | 22/49/29 | 0.664 |
| light soup / older sedentary woman, losing | matched | Chicken Vegetable Soup Bowl | 350 | 348.9 | 0.3% | 0.65 | 31/46/24 | 0.742 |
| sushi / older sedentary woman, losing | matched | Tuna Sushi Bowl | 350 | 458.0 | 30.9% | 0.47 | 23/31/46 | 0.594 |
| pizza / older sedentary woman, losing | fallback | High-Protein Turkey Burger Bowl | 350 | 350.5 | 0.1% | 0.57 | 23/24/53 |  |
| chocolate dessert / older sedentary woman, losing | fallback | High-Protein Turkey Burger Bowl | 350 | 350.5 | 0.1% | 0.57 | 23/24/53 |  |
| chicken fried rice / average man, maintaining | matched | Chicken Fried Rice | 809 | 808.8 | 0.0% | 1.11 | 30/48/22 | 0.999 |
| high-protein burger / average man, maintaining | matched | High-Protein Turkey Burger Bowl | 809 | 813.7 | 0.6% | 1.32 | 23/24/53 | 0.656 |
| creamy pasta / average man, maintaining | matched | Tuna Pasta Salad | 809 | 803.2 | 0.7% | 1.4 | 29/46/25 | 0.612 |
| salmon dinner / average man, maintaining | matched | Salmon Noodle Bowl | 809 | 747.4 | 7.6% | 1.26 | 23/47/29 | 0.566 |
| steak and rice / average man, maintaining | matched | Lean Steak Rice Plate | 809 | 815.9 | 0.9% | 1.37 | 29/46/25 | 0.864 |
| spicy curry / average man, maintaining | matched | Chickpea Curry Bowl | 809 | 818.5 | 1.2% | 1.46 | 14/62/24 | 0.435 |
| breakfast oats / average man, maintaining | matched | Banana Oat Protein Bowl | 809 | 771.1 | 4.7% | 1.6 | 16/63/22 | 0.594 |
| taco bowl / average man, maintaining | matched | Shrimp Taco Bowl | 809 | 1316.8 | 62.8% | 1.04 | 22/48/30 | 0.664 |
| light soup / average man, maintaining | matched | Chicken Vegetable Soup Bowl | 809 | 817.7 | 1.1% | 1.46 | 26/46/27 | 0.742 |
| sushi / average man, maintaining | matched | Tuna Sushi Bowl | 809 | 990.1 | 22.4% | 1.04 | 24/32/44 | 0.594 |
| pizza / average man, maintaining | fallback | High-Protein Turkey Burger Bowl | 809 | 813.7 | 0.6% | 1.32 | 23/24/53 |  |
| chocolate dessert / average man, maintaining | fallback | High-Protein Turkey Burger Bowl | 809 | 813.7 | 0.6% | 1.32 | 23/24/53 |  |
| chicken fried rice / active woman, maintaining | matched | Chicken Fried Rice | 691 | 689.6 | 0.2% | 0.95 | 30/46/24 | 0.999 |
| high-protein burger / active woman, maintaining | matched | High-Protein Turkey Burger Bowl | 691 | 687.5 | 0.5% | 1.12 | 23/23/53 | 0.656 |
| creamy pasta / active woman, maintaining | matched | Tuna Pasta Salad | 691 | 664.5 | 3.8% | 0.96 | 33/35/33 | 0.612 |
| salmon dinner / active woman, maintaining | matched | Salmon Noodle Bowl | 691 | 640.2 | 7.4% | 1.07 | 23/47/30 | 0.566 |
| steak and rice / active woman, maintaining | matched | Lean Steak Rice Plate | 691 | 699.0 | 1.2% | 1.17 | 32/47/22 | 0.864 |
| spicy curry / active woman, maintaining | matched | Chickpea Curry Bowl | 691 | 689.2 | 0.3% | 1.25 | 15/64/21 | 0.435 |
| breakfast oats / active woman, maintaining | matched | Banana Oat Protein Bowl | 691 | 693.4 | 0.3% | 1.6 | 15/62/23 | 0.594 |
| taco bowl / active woman, maintaining | matched | Shrimp Taco Bowl | 691 | 1316.8 | 90.6% | 1.04 | 22/48/30 | 0.664 |
| light soup / active woman, maintaining | matched | Chicken Vegetable Soup Bowl | 691 | 692.9 | 0.3% | 1.24 | 30/46/24 | 0.742 |
| sushi / active woman, maintaining | matched | Tuna Sushi Bowl | 691 | 896.4 | 29.7% | 0.93 | 24/32/44 | 0.594 |
| pizza / active woman, maintaining | fallback | High-Protein Turkey Burger Bowl | 691 | 687.5 | 0.5% | 1.12 | 23/23/53 |  |
| chocolate dessert / active woman, maintaining | fallback | High-Protein Turkey Burger Bowl | 691 | 687.5 | 0.5% | 1.12 | 23/23/53 |  |
| chicken fried rice / large athlete, gaining | matched | Chicken Fried Rice | 850 | 851.1 | 0.1% | 1.17 | 30/48/22 | 0.999 |
| high-protein burger / large athlete, gaining | matched | High-Protein Turkey Burger Bowl | 850 | 843.0 | 0.8% | 1.38 | 23/23/53 | 0.656 |
| creamy pasta / large athlete, gaining | matched | Tuna Pasta Salad | 850 | 850.2 | 0.0% | 1.47 | 30/46/25 | 0.612 |
| salmon dinner / large athlete, gaining | matched | Salmon Noodle Bowl | 850 | 775.9 | 8.7% | 1.32 | 23/48/29 | 0.566 |
| steak and rice / large athlete, gaining | matched | Lean Steak Rice Plate | 850 | 854.1 | 0.5% | 1.44 | 30/46/24 | 0.864 |
| spicy curry / large athlete, gaining | matched | Chickpea Curry Bowl | 850 | 839.2 | 1.3% | 1.53 | 14/62/24 | 0.435 |
| breakfast oats / large athlete, gaining | matched | Banana Oat Protein Bowl | 850 | 771.1 | 9.3% | 1.6 | 16/63/22 | 0.594 |
| taco bowl / large athlete, gaining | matched | Shrimp Taco Bowl | 850 | 1316.8 | 54.9% | 1.04 | 22/48/30 | 0.664 |
| light soup / large athlete, gaining | matched | Chicken Vegetable Soup Bowl | 850 | 851.5 | 0.2% | 1.53 | 27/46/27 | 0.742 |
| sushi / large athlete, gaining | matched | Tuna Sushi Bowl | 850 | 990.1 | 16.5% | 1.04 | 24/32/44 | 0.594 |
| pizza / large athlete, gaining | fallback | High-Protein Turkey Burger Bowl | 850 | 843.0 | 0.8% | 1.38 | 23/23/53 |  |
| chocolate dessert / large athlete, gaining | fallback | High-Protein Turkey Burger Bowl | 850 | 843.0 | 0.8% | 1.38 | 23/23/53 |  |
| chicken fried rice / average man, maintaining [vegan] | matched | Tofu Fried Rice | 809 | 810.3 | 0.2% | 1.28 | 18/59/23 | 0.637 |
| high-protein burger / average man, maintaining [vegan] | fallback | High-Protein Asian Tofu Noodle Bowl | 809 | 806.7 | 0.3% | 1.27 | 27/52/21 |  |
| creamy pasta / average man, maintaining [vegan] | matched | Lentil Bolognese Pasta | 809 | 808.9 | 0.0% | 1.56 | 19/56/25 | 0.37 |
| salmon dinner / average man, maintaining [vegan] | fallback | High-Protein Asian Tofu Noodle Bowl | 809 | 806.7 | 0.3% | 1.27 | 27/52/21 |  |
| steak and rice / average man, maintaining [vegan] | matched | Tempeh Quinoa Power Bowl | 809 | 809.3 | 0.0% | 1.41 | 21/46/33 | 0.52 |
| spicy curry / average man, maintaining [vegan] | matched | Chickpea Curry Bowl | 809 | 818.5 | 1.2% | 1.46 | 14/62/24 | 0.484 |
| chicken fried rice / average man, maintaining [hypertension] | matched | Chicken Fried Rice | 809 | 809.9 | 0.1% | 1.11 | 29/48/22 | 0.999 |
| high-protein burger / average man, maintaining [hypertension] | matched | High-Protein Turkey Burger Bowl | 809 | 813.7 | 0.6% | 1.32 | 23/24/53 | 0.656 |
| creamy pasta / average man, maintaining [hypertension] | matched | Tuna Pasta Salad | 809 | 803.2 | 0.7% | 1.4 | 29/46/25 | 0.612 |
| salmon dinner / average man, maintaining [hypertension] | matched | Salmon Noodle Bowl | 809 | 747.4 | 7.6% | 1.26 | 23/47/29 | 0.566 |
| steak and rice / average man, maintaining [hypertension] | matched | Lean Steak Rice Plate | 809 | 815.9 | 0.9% | 1.37 | 29/46/25 | 0.864 |
| spicy curry / average man, maintaining [hypertension] | matched | Chickpea Curry Bowl | 809 | 818.5 | 1.2% | 1.46 | 14/62/24 | 0.435 |
| chicken fried rice / average man, maintaining [kidney disease] | matched | Low-Sodium Chicken Rice Bowl | 809 | 804.5 | 0.6% | 1.44 | 30/46/24 | 0.511 |
| high-protein burger / average man, maintaining [kidney disease] | matched | High-Protein Turkey Burger Bowl | 809 | 813.7 | 0.6% | 1.32 | 23/24/53 | 0.656 |
| creamy pasta / average man, maintaining [kidney disease] | matched | Tuna Pasta Salad | 809 | 803.2 | 0.7% | 1.4 | 29/46/25 | 0.612 |
| salmon dinner / average man, maintaining [kidney disease] | matched | Salmon Noodle Bowl | 809 | 747.4 | 7.6% | 1.26 | 23/47/29 | 0.566 |
| steak and rice / average man, maintaining [kidney disease] | matched | Lean Steak Rice Plate | 809 | 815.9 | 0.9% | 1.37 | 29/46/25 | 0.864 |
| spicy curry / average man, maintaining [kidney disease] | fallback | High-Protein Turkey Burger Bowl | 809 | 813.7 | 0.6% | 1.32 | 23/24/53 |  |
| chicken fried rice / average man, maintaining [celiac] | matched | Chicken Fried Rice | 809 | 809.9 | 0.1% | 1.11 | 29/48/22 | 0.999 |
| high-protein burger / average man, maintaining [celiac] | matched | High-Protein Turkey Burger Bowl | 809 | 808.5 | 0.1% | 1.33 | 20/26/54 | 0.656 |
| creamy pasta / average man, maintaining [celiac] | matched | Tuna Pasta Salad | 809 | 803.2 | 0.7% | 1.39 | 15/50/35 | 0.612 |
| salmon dinner / average man, maintaining [celiac] | matched | Salmon Noodle Bowl | 809 | 747.4 | 7.6% | 1.26 | 23/47/29 | 0.566 |
| steak and rice / average man, maintaining [celiac] | matched | Lean Steak Rice Plate | 809 | 815.9 | 0.9% | 1.37 | 29/46/25 | 0.864 |
| spicy curry / average man, maintaining [celiac] | matched | Chickpea Curry Bowl | 809 | 818.5 | 1.2% | 1.46 | 14/62/24 | 0.435 |

## Guardrails

Run against a controlled corpus with no plant-based meal (`guardrail_meals.json`, sha256 `9e4f5300321f`). As expected: 5 of 5.

| Scenario | Expected | Got | Meal | As expected |
|---|---|---|---|---|
| steak and rice / average man, maintaining | matched | matched | Lean Steak Rice Plate | yes |
| tofu bowl / average man, maintaining [vegan] | fallback | fallback | Tofu Rice Bowl | yes |
| pasta / average man, maintaining [vegan] | fallback | fallback | High-Protein Asian Tofu Noodle Bowl | yes |
| tofu bowl / average man, maintaining [vegan, soy allergy, kidney disease] | infeasible | infeasible |  | yes |
| pasta / average man, maintaining [vegan, soy allergy, kidney disease] | infeasible | infeasible |  | yes |
