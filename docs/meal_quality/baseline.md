## Measured

- calorie_model_version: `hist_gradient_boosting_deep_v0.1.0`
- calorie_model_sha256: `33a154b3d5807af1e2dd53ee69dc250e3f9a4429bfed90260e27671eac168c95`
- meal_corpus_sha256: `5243924a0a8aab3557d68bff805f00d786dbe8ee30359b84d7e14b873c0c1ac2`
- meal_count: `34`
- retriever: `tfidf_vector_retriever_v0.1`

## Summary

- Plans: 72 (fallback 11, matched 61).
- **Meeting the targets** (calories within 10%, all macros in AMDR): 72 of 72.
- Within the 10% calorie target: 72 of 72 scaled plans.
- Within the service's 15% retry tolerance: 72 of 72 scaled plans.
- Calorie deviation: median 0.3%, 90th percentile 3.4%, max 9.9%.
- Rescaled by reconciliation: 0. First-pass scaling clamped: 27.
- Meal target as a share of the daily budget: 18.8% to 29.2%.
- Daily budget across profiles: 1200.0 to 4521.1 kcal.
- Macro share inside AMDR: protein 72, carbs 72, fat 72; all three 72 of 72.
- Plans with at least one estimated ingredient: 68 of 72.
- Corpus matches scoring below 0.25: 0.

## Plans

| Scenario | Status | Meal | Target | Verified | Dev. | Scale | P/C/F % | Score |
|---|---|---|---:|---:|---:|---:|---|---:|
| chicken fried rice / older sedentary woman, losing | matched | Chicken Fried Rice | 350 | 363.4 | 3.8% | 0.65 | 29/46/26 | 1.001 |
| high-protein burger / older sedentary woman, losing | matched | High-Protein Turkey Burger Bowl | 350 | 351.7 | 0.5% | 0.82 | 31/46/23 | 0.672 |
| creamy pasta / older sedentary woman, losing | matched | High-Protein Tomato Turkey Pasta | 350 | 352.0 | 0.6% | 0.65 | 26/47/27 | 0.48 |
| salmon dinner / older sedentary woman, losing | matched | Salmon Quinoa Plate | 350 | 345.5 | 1.3% | 0.65 | 22/46/31 | 0.569 |
| steak and rice / older sedentary woman, losing | matched | Lean Steak Rice Plate | 350 | 349.0 | 0.3% | 0.65 | 26/46/28 | 0.853 |
| spicy curry / older sedentary woman, losing | matched | Chickpea Curry Bowl | 350 | 348.9 | 0.3% | 0.65 | 16/62/23 | 0.445 |
| breakfast oats / older sedentary woman, losing | matched | Banana Oat Protein Bowl | 350 | 384.5 | 9.9% | 0.82 | 16/64/21 | 0.583 |
| taco bowl / older sedentary woman, losing | matched | Shrimp Taco Bowl | 350 | 347.7 | 0.7% | 0.86 | 30/46/24 | 0.689 |
| light soup / older sedentary woman, losing | matched | Chicken Vegetable Soup Bowl | 350 | 349.1 | 0.3% | 0.65 | 33/46/22 | 0.769 |
| sushi / older sedentary woman, losing | matched | Tuna Sushi Bowl | 350 | 346.7 | 0.9% | 0.73 | 33/47/21 | 0.568 |
| pizza / older sedentary woman, losing | fallback | High-Protein Turkey Burger Bowl | 350 | 351.7 | 0.5% | 0.82 | 31/46/23 |  |
| chocolate dessert / older sedentary woman, losing | fallback | High-Protein Turkey Burger Bowl | 350 | 351.7 | 0.5% | 0.82 | 31/46/23 |  |
| chicken fried rice / average man, maintaining | matched | Chicken Fried Rice | 809 | 808.8 | 0.0% | 1.11 | 30/46/24 | 1.001 |
| high-protein burger / average man, maintaining | matched | High-Protein Turkey Burger Bowl | 809 | 811.4 | 0.3% | 1.6 | 31/46/23 | 0.672 |
| creamy pasta / average man, maintaining | matched | High-Protein Tomato Turkey Pasta | 809 | 798.3 | 1.3% | 1.14 | 27/46/27 | 0.48 |
| salmon dinner / average man, maintaining | matched | Salmon Quinoa Plate | 809 | 808.2 | 0.1% | 1.31 | 21/46/33 | 0.569 |
| steak and rice / average man, maintaining | matched | Lean Steak Rice Plate | 809 | 808.9 | 0.0% | 1.37 | 23/46/31 | 0.853 |
| spicy curry / average man, maintaining | matched | Chickpea Curry Bowl | 809 | 815.7 | 0.8% | 1.46 | 15/59/26 | 0.445 |
| breakfast oats / average man, maintaining | matched | Banana Oat Protein Bowl | 809 | 771.1 | 4.7% | 1.6 | 16/63/22 | 0.583 |
| taco bowl / average man, maintaining | matched | Shrimp Taco Bowl | 809 | 812.0 | 0.4% | 1.6 | 31/48/21 | 0.689 |
| light soup / average man, maintaining | matched | Chicken Vegetable Soup Bowl | 809 | 806.5 | 0.3% | 1.46 | 28/46/26 | 0.769 |
| sushi / average man, maintaining | matched | Tuna Sushi Bowl | 809 | 809.8 | 0.1% | 1.6 | 33/46/21 | 0.568 |
| pizza / average man, maintaining | fallback | High-Protein Turkey Burger Bowl | 809 | 811.4 | 0.3% | 1.6 | 31/46/23 |  |
| chocolate dessert / average man, maintaining | fallback | High-Protein Turkey Burger Bowl | 809 | 811.4 | 0.3% | 1.6 | 31/46/23 |  |
| chicken fried rice / active woman, maintaining | matched | Chicken Fried Rice | 691 | 693.6 | 0.4% | 0.95 | 28/46/26 | 1.001 |
| high-protein burger / active woman, maintaining | matched | High-Protein Turkey Burger Bowl | 691 | 695.9 | 0.7% | 1.6 | 31/46/23 | 0.672 |
| creamy pasta / active woman, maintaining | matched | High-Protein Tomato Turkey Pasta | 691 | 688.8 | 0.3% | 0.98 | 26/46/28 | 0.48 |
| salmon dinner / active woman, maintaining | matched | Salmon Quinoa Plate | 691 | 688.7 | 0.3% | 1.12 | 21/46/33 | 0.569 |
| steak and rice / active woman, maintaining | matched | Lean Steak Rice Plate | 691 | 689.4 | 0.2% | 1.17 | 25/46/29 | 0.853 |
| spicy curry / active woman, maintaining | matched | Chickpea Curry Bowl | 691 | 667.3 | 3.4% | 1.25 | 16/61/23 | 0.445 |
| breakfast oats / active woman, maintaining | matched | Banana Oat Protein Bowl | 691 | 693.4 | 0.3% | 1.6 | 15/62/23 | 0.583 |
| taco bowl / active woman, maintaining | matched | Shrimp Taco Bowl | 691 | 690.2 | 0.1% | 1.6 | 31/46/23 | 0.689 |
| light soup / active woman, maintaining | matched | Chicken Vegetable Soup Bowl | 691 | 695.5 | 0.7% | 1.24 | 31/46/23 | 0.769 |
| sushi / active woman, maintaining | matched | Tuna Sushi Bowl | 691 | 694.1 | 0.4% | 1.43 | 33/46/21 | 0.568 |
| pizza / active woman, maintaining | fallback | High-Protein Turkey Burger Bowl | 691 | 695.9 | 0.7% | 1.6 | 31/46/23 |  |
| chocolate dessert / active woman, maintaining | fallback | High-Protein Turkey Burger Bowl | 691 | 695.9 | 0.7% | 1.6 | 31/46/23 |  |
| chicken fried rice / large athlete, gaining | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 1.001 |
| high-protein burger / large athlete, gaining | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.672 |
| creamy pasta / large athlete, gaining | matched | High-Protein Tomato Turkey Pasta | 850 | 857.2 | 0.8% | 1.2 | 27/46/27 | 0.48 |
| salmon dinner / large athlete, gaining | matched | Salmon Quinoa Plate | 850 | 852.3 | 0.3% | 1.38 | 21/46/33 | 0.569 |
| steak and rice / large athlete, gaining | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.853 |
| spicy curry / large athlete, gaining | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.445 |
| breakfast oats / large athlete, gaining | matched | Banana Oat Protein Bowl | 850 | 771.1 | 9.3% | 1.6 | 16/63/22 | 0.583 |
| taco bowl / large athlete, gaining | matched | Shrimp Taco Bowl | 850 | 849.0 | 0.1% | 1.6 | 30/49/21 | 0.689 |
| light soup / large athlete, gaining | matched | Chicken Vegetable Soup Bowl | 850 | 849.4 | 0.1% | 1.53 | 29/46/25 | 0.769 |
| sushi / large athlete, gaining | matched | Tuna Sushi Bowl | 850 | 848.9 | 0.1% | 1.6 | 33/46/21 | 0.568 |
| pizza / large athlete, gaining | fallback | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 |  |
| chocolate dessert / large athlete, gaining | fallback | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 |  |
| chicken fried rice / average man, maintaining [vegan] | matched | Tofu Fried Rice | 809 | 809.5 | 0.1% | 1.28 | 23/46/31 | 0.683 |
| high-protein burger / average man, maintaining [vegan] | fallback | High-Protein Asian Tofu Noodle Bowl | 809 | 815.5 | 0.8% | 1.27 | 24/52/23 |  |
| creamy pasta / average man, maintaining [vegan] | matched | Lentil Bolognese Pasta | 809 | 809.0 | 0.0% | 1.22 | 18/61/21 | 0.416 |
| salmon dinner / average man, maintaining [vegan] | fallback | High-Protein Asian Tofu Noodle Bowl | 809 | 815.5 | 0.8% | 1.27 | 24/52/23 |  |
| steak and rice / average man, maintaining [vegan] | matched | High-Protein Asian Tofu Noodle Bowl | 809 | 815.5 | 0.8% | 1.27 | 24/52/23 | 0.506 |
| spicy curry / average man, maintaining [vegan] | matched | Chickpea Curry Bowl | 809 | 815.7 | 0.8% | 1.46 | 15/59/26 | 0.571 |
| chicken fried rice / average man, maintaining [hypertension] | matched | Chicken Fried Rice | 809 | 803.4 | 0.7% | 1.11 | 30/46/24 | 1.001 |
| high-protein burger / average man, maintaining [hypertension] | matched | High-Protein Turkey Burger Bowl | 809 | 811.4 | 0.3% | 1.6 | 31/46/23 | 0.672 |
| creamy pasta / average man, maintaining [hypertension] | matched | High-Protein Tomato Turkey Pasta | 809 | 798.3 | 1.3% | 1.14 | 27/46/27 | 0.48 |
| salmon dinner / average man, maintaining [hypertension] | matched | Salmon Quinoa Plate | 809 | 808.2 | 0.1% | 1.31 | 21/46/33 | 0.569 |
| steak and rice / average man, maintaining [hypertension] | matched | Lean Steak Rice Plate | 809 | 808.9 | 0.0% | 1.37 | 23/46/31 | 0.853 |
| spicy curry / average man, maintaining [hypertension] | matched | Chickpea Curry Bowl | 809 | 815.7 | 0.8% | 1.46 | 15/59/26 | 0.445 |
| chicken fried rice / average man, maintaining [kidney disease] | matched | Chicken Vegetable Soup Bowl | 809 | 806.5 | 0.3% | 1.46 | 28/46/26 | 0.535 |
| high-protein burger / average man, maintaining [kidney disease] | matched | High-Protein Turkey Burger Bowl | 809 | 811.4 | 0.3% | 1.6 | 31/46/23 | 0.672 |
| creamy pasta / average man, maintaining [kidney disease] | matched | High-Protein Tomato Turkey Pasta | 809 | 798.3 | 1.3% | 1.14 | 27/46/27 | 0.48 |
| salmon dinner / average man, maintaining [kidney disease] | matched | Salmon Quinoa Plate | 809 | 808.2 | 0.1% | 1.31 | 21/46/33 | 0.569 |
| steak and rice / average man, maintaining [kidney disease] | matched | Lean Steak Rice Plate | 809 | 808.9 | 0.0% | 1.37 | 23/46/31 | 0.853 |
| spicy curry / average man, maintaining [kidney disease] | fallback | High-Protein Turkey Burger Bowl | 809 | 811.4 | 0.3% | 1.6 | 31/46/23 |  |
| chicken fried rice / average man, maintaining [celiac] | matched | Chicken Fried Rice | 809 | 808.8 | 0.0% | 1.11 | 30/46/24 | 1.001 |
| high-protein burger / average man, maintaining [celiac] | matched | High-Protein Turkey Burger Bowl | 809 | 809.9 | 0.1% | 1.6 | 28/46/26 | 0.672 |
| creamy pasta / average man, maintaining [celiac] | matched | High-Protein Tomato Turkey Pasta | 809 | 801.4 | 0.9% | 1.14 | 25/47/28 | 0.48 |
| salmon dinner / average man, maintaining [celiac] | matched | Salmon Quinoa Plate | 809 | 808.2 | 0.1% | 1.31 | 21/46/33 | 0.569 |
| steak and rice / average man, maintaining [celiac] | matched | Lean Steak Rice Plate | 809 | 808.9 | 0.0% | 1.37 | 23/46/31 | 0.853 |
| spicy curry / average man, maintaining [celiac] | matched | Chickpea Curry Bowl | 809 | 815.7 | 0.8% | 1.46 | 15/59/26 | 0.445 |

## Guardrails

Run against a controlled corpus with no plant-based meal (`guardrail_meals.json`, sha256 `9e4f5300321f`). As expected: 5 of 5.

| Scenario | Expected | Got | Meal | As expected |
|---|---|---|---|---|
| steak and rice / average man, maintaining | matched | matched | Lean Steak Rice Plate | yes |
| tofu bowl / average man, maintaining [vegan] | fallback | fallback | Tofu Rice Bowl | yes |
| pasta / average man, maintaining [vegan] | fallback | fallback | High-Protein Asian Tofu Noodle Bowl | yes |
| tofu bowl / average man, maintaining [vegan, soy allergy, kidney disease] | infeasible | infeasible |  | yes |
| pasta / average man, maintaining [vegan, soy allergy, kidney disease] | infeasible | infeasible |  | yes |
