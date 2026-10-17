## Measured

- calorie_model_version: `hist_gradient_boosting_deep_v0.1.0`
- calorie_model_sha256: `33a154b3d5807af1e2dd53ee69dc250e3f9a4429bfed90260e27671eac168c95`
- meal_corpus_sha256: `685ae059a59cd5149f9d87dc9bab4ac9464c58ef51b371bbeefe41c4801e002f`
- meal_count: `34`
- retriever: `tfidf_vector_retriever_v0.1`

## Summary

- Plans: 72 (matched 72).
- **Meeting the targets** (calories within 10%, all macros in AMDR): 10 of 72.
- Within the 10% calorie target: 68 of 72 scaled plans.
- Within the service's 15% retry tolerance: 72 of 72 scaled plans.
- Calorie deviation: median 1.6%, 90th percentile 8.5%, max 14.3%.
- Rescaled by reconciliation: 12. First-pass scaling clamped: 33.
- Meal target as a share of the daily budget: 18.8% to 29.2%.
- Daily budget across profiles: 1200.0 to 4521.1 kcal.
- Macro share inside AMDR: protein 32, carbs 18, fat 31; all three 11 of 72.
- Plans with at least one estimated ingredient: 68 of 72.
- Corpus matches scoring below 0.25: 11.

## Plans

| Scenario | Status | Meal | Target | Verified | Dev. | Scale | P/C/F % | Score |
|---|---|---|---:|---:|---:|---:|---|---:|
| chicken fried rice / older sedentary woman, losing | matched | Chicken Fried Rice | 350 | 347.0 | 0.9% | 0.54 | 41/43/16 | 1.019 |
| high-protein burger / older sedentary woman, losing | matched | High-Protein Turkey Burger Bowl | 350 | 348.7 | 0.4% | 0.82 | 40/31/29 | 0.672 |
| creamy pasta / older sedentary woman, losing | matched | High-Protein Tomato Turkey Pasta | 350 | 346.7 | 0.9% | 0.55 | 33/47/20 | 0.489 |
| salmon dinner / older sedentary woman, losing | matched | Salmon Quinoa Plate | 350 | 399.9 | 14.3% | 0.65 | 28/27/46 | 0.569 |
| steak and rice / older sedentary woman, losing | matched | Lean Steak Rice Plate | 350 | 353.4 | 1.0% | 0.7 | 41/35/24 | 0.866 |
| spicy curry / older sedentary woman, losing | matched | Chickpea Curry Bowl | 350 | 353.9 | 1.1% | 0.75 | 18/70/12 | 0.452 |
| breakfast oats / older sedentary woman, losing | matched | Banana Oat Protein Bowl | 350 | 384.5 | 9.9% | 0.82 | 16/64/21 | 0.583 |
| taco bowl / older sedentary woman, losing | matched | Shrimp Taco Bowl | 350 | 348.7 | 0.4% | 0.86 | 36/40/24 | 0.689 |
| light soup / older sedentary woman, losing | matched | Chicken Vegetable Soup Bowl | 350 | 346.3 | 1.1% | 0.75 | 49/37/14 | 0.78 |
| sushi / older sedentary woman, losing | matched | Tuna Sushi Bowl | 350 | 364.8 | 4.2% | 0.73 | 34/46/20 | 0.568 |
| pizza / older sedentary woman, losing | matched | Chicken Fried Rice | 350 | 347.0 | 0.9% | 0.54 | 41/43/16 | 0.198 |
| chocolate dessert / older sedentary woman, losing | matched | Chicken Fried Rice | 350 | 347.0 | 0.9% | 0.54 | 41/43/16 | 0.198 |
| chicken fried rice / average man, maintaining | matched | Chicken Fried Rice | 809 | 838.3 | 3.6% | 1.27 | 41/42/16 | 1.019 |
| high-protein burger / average man, maintaining | matched | High-Protein Turkey Burger Bowl | 809 | 812.9 | 0.5% | 1.91 | 40/30/29 | 0.672 |
| creamy pasta / average man, maintaining | matched | High-Protein Tomato Turkey Pasta | 809 | 802.9 | 0.8% | 1.31 | 33/47/20 | 0.489 |
| salmon dinner / average man, maintaining | matched | Salmon Quinoa Plate | 809 | 809.6 | 0.1% | 1.31 | 27/27/46 | 0.569 |
| steak and rice / average man, maintaining | matched | Lean Steak Rice Plate | 809 | 794.9 | 1.7% | 1.6 | 41/35/25 | 0.866 |
| spicy curry / average man, maintaining | matched | Chickpea Curry Bowl | 809 | 740.6 | 8.5% | 1.6 | 18/70/12 | 0.452 |
| breakfast oats / average man, maintaining | matched | Banana Oat Protein Bowl | 809 | 771.1 | 4.7% | 1.6 | 16/63/22 | 0.583 |
| taco bowl / average man, maintaining | matched | Shrimp Taco Bowl | 809 | 808.3 | 0.1% | 1.99 | 36/40/24 | 0.689 |
| light soup / average man, maintaining | matched | Chicken Vegetable Soup Bowl | 809 | 749.7 | 7.3% | 1.6 | 49/37/14 | 0.78 |
| sushi / average man, maintaining | matched | Tuna Sushi Bowl | 809 | 796.7 | 1.5% | 1.6 | 35/46/19 | 0.568 |
| pizza / average man, maintaining | matched | Chicken Fried Rice | 809 | 838.3 | 3.6% | 1.27 | 41/42/16 | 0.198 |
| chocolate dessert / average man, maintaining | matched | Chicken Fried Rice | 809 | 838.3 | 3.6% | 1.27 | 41/42/16 | 0.198 |
| chicken fried rice / active woman, maintaining | matched | Chicken Fried Rice | 691 | 713.4 | 3.2% | 1.08 | 42/42/16 | 1.019 |
| high-protein burger / active woman, maintaining | matched | High-Protein Turkey Burger Bowl | 691 | 676.9 | 2.0% | 1.6 | 41/30/29 | 0.672 |
| creamy pasta / active woman, maintaining | matched | High-Protein Tomato Turkey Pasta | 691 | 692.4 | 0.2% | 1.11 | 33/47/20 | 0.489 |
| salmon dinner / active woman, maintaining | matched | Salmon Quinoa Plate | 691 | 690.6 | 0.1% | 1.12 | 27/27/46 | 0.569 |
| steak and rice / active woman, maintaining | matched | Lean Steak Rice Plate | 691 | 690.4 | 0.1% | 1.38 | 41/35/24 | 0.866 |
| spicy curry / active woman, maintaining | matched | Chickpea Curry Bowl | 691 | 691.4 | 0.1% | 1.48 | 18/70/12 | 0.452 |
| breakfast oats / active woman, maintaining | matched | Banana Oat Protein Bowl | 691 | 771.1 | 11.6% | 1.6 | 16/63/22 | 0.583 |
| taco bowl / active woman, maintaining | matched | Shrimp Taco Bowl | 691 | 650.3 | 5.9% | 1.6 | 37/40/24 | 0.689 |
| light soup / active woman, maintaining | matched | Chicken Vegetable Soup Bowl | 691 | 689.3 | 0.2% | 1.48 | 49/37/14 | 0.78 |
| sushi / active woman, maintaining | matched | Tuna Sushi Bowl | 691 | 714.3 | 3.4% | 1.43 | 35/46/19 | 0.568 |
| pizza / active woman, maintaining | matched | Chicken Fried Rice | 691 | 713.4 | 3.2% | 1.08 | 42/42/16 | 0.198 |
| chocolate dessert / active woman, maintaining | matched | Chicken Fried Rice | 691 | 713.4 | 3.2% | 1.08 | 42/42/16 | 0.198 |
| chicken fried rice / large athlete, gaining | matched | Chicken Fried Rice | 850 | 874.4 | 2.9% | 1.33 | 42/42/16 | 1.019 |
| high-protein burger / large athlete, gaining | matched | High-Protein Turkey Burger Bowl | 850 | 851.7 | 0.2% | 2.01 | 40/30/29 | 0.672 |
| creamy pasta / large athlete, gaining | matched | High-Protein Tomato Turkey Pasta | 850 | 856.0 | 0.7% | 1.37 | 33/47/20 | 0.489 |
| salmon dinner / large athlete, gaining | matched | Salmon Quinoa Plate | 850 | 853.8 | 0.4% | 1.38 | 27/27/46 | 0.569 |
| steak and rice / large athlete, gaining | matched | Lean Steak Rice Plate | 850 | 794.9 | 6.5% | 1.6 | 41/35/25 | 0.866 |
| spicy curry / large athlete, gaining | matched | Chickpea Curry Bowl | 850 | 740.6 | 12.9% | 1.6 | 18/70/12 | 0.452 |
| breakfast oats / large athlete, gaining | matched | Banana Oat Protein Bowl | 850 | 771.1 | 9.3% | 1.6 | 16/63/22 | 0.583 |
| taco bowl / large athlete, gaining | matched | Shrimp Taco Bowl | 850 | 855.0 | 0.6% | 2.09 | 37/40/24 | 0.689 |
| light soup / large athlete, gaining | matched | Chicken Vegetable Soup Bowl | 850 | 749.7 | 11.8% | 1.6 | 49/37/14 | 0.78 |
| sushi / large athlete, gaining | matched | Tuna Sushi Bowl | 850 | 796.7 | 6.3% | 1.6 | 35/46/19 | 0.568 |
| pizza / large athlete, gaining | matched | Chicken Fried Rice | 850 | 874.4 | 2.9% | 1.33 | 42/42/16 | 0.198 |
| chocolate dessert / large athlete, gaining | matched | Chicken Fried Rice | 850 | 874.4 | 2.9% | 1.33 | 42/42/16 | 0.198 |
| chicken fried rice / average man, maintaining [vegan] | matched | Tofu Fried Rice | 809 | 826.7 | 2.2% | 1.28 | 24/43/33 | 0.679 |
| high-protein burger / average man, maintaining [vegan] | matched | High-Protein Asian Tofu Noodle Bowl | 809 | 815.5 | 0.8% | 1.27 | 24/52/23 | 0.184 |
| creamy pasta / average man, maintaining [vegan] | matched | Lentil Bolognese Pasta | 809 | 794.8 | 1.8% | 1.41 | 22/73/5 | 0.423 |
| salmon dinner / average man, maintaining [vegan] | matched | High-Protein Asian Tofu Noodle Bowl | 809 | 815.5 | 0.8% | 1.27 | 24/52/23 | 0.181 |
| steak and rice / average man, maintaining [vegan] | matched | High-Protein Asian Tofu Noodle Bowl | 809 | 815.5 | 0.8% | 1.27 | 24/52/23 | 0.506 |
| spicy curry / average man, maintaining [vegan] | matched | Chickpea Curry Bowl | 809 | 740.6 | 8.5% | 1.6 | 18/70/12 | 0.579 |
| chicken fried rice / average man, maintaining [hypertension] | matched | Chicken Fried Rice | 809 | 839.7 | 3.8% | 1.27 | 41/43/16 | 1.019 |
| high-protein burger / average man, maintaining [hypertension] | matched | High-Protein Turkey Burger Bowl | 809 | 812.9 | 0.5% | 1.91 | 40/30/29 | 0.672 |
| creamy pasta / average man, maintaining [hypertension] | matched | High-Protein Tomato Turkey Pasta | 809 | 802.9 | 0.8% | 1.31 | 33/47/20 | 0.489 |
| salmon dinner / average man, maintaining [hypertension] | matched | Salmon Quinoa Plate | 809 | 809.6 | 0.1% | 1.31 | 27/27/46 | 0.569 |
| steak and rice / average man, maintaining [hypertension] | matched | Lean Steak Rice Plate | 809 | 794.9 | 1.7% | 1.6 | 41/35/25 | 0.866 |
| spicy curry / average man, maintaining [hypertension] | matched | Chickpea Curry Bowl | 809 | 740.6 | 8.5% | 1.6 | 18/70/12 | 0.452 |
| chicken fried rice / average man, maintaining [kidney disease] | matched | Chicken Vegetable Soup Bowl | 809 | 749.7 | 7.3% | 1.6 | 49/37/14 | 0.54 |
| high-protein burger / average man, maintaining [kidney disease] | matched | High-Protein Turkey Burger Bowl | 809 | 812.9 | 0.5% | 1.91 | 40/30/29 | 0.672 |
| creamy pasta / average man, maintaining [kidney disease] | matched | High-Protein Tomato Turkey Pasta | 809 | 802.9 | 0.8% | 1.31 | 33/47/20 | 0.489 |
| salmon dinner / average man, maintaining [kidney disease] | matched | Salmon Quinoa Plate | 809 | 809.6 | 0.1% | 1.31 | 27/27/46 | 0.569 |
| steak and rice / average man, maintaining [kidney disease] | matched | Lean Steak Rice Plate | 809 | 794.9 | 1.7% | 1.6 | 41/35/25 | 0.866 |
| spicy curry / average man, maintaining [kidney disease] | matched | High-Protein Turkey Burger Bowl | 809 | 812.9 | 0.5% | 1.91 | 40/30/29 | 0.186 |
| chicken fried rice / average man, maintaining [celiac] | matched | Chicken Fried Rice | 809 | 838.3 | 3.6% | 1.27 | 41/42/16 | 1.019 |
| high-protein burger / average man, maintaining [celiac] | matched | High-Protein Turkey Burger Bowl | 809 | 812.9 | 0.5% | 1.91 | 37/33/30 | 0.672 |
| creamy pasta / average man, maintaining [celiac] | matched | High-Protein Tomato Turkey Pasta | 809 | 805.2 | 0.5% | 1.3 | 29/51/19 | 0.489 |
| salmon dinner / average man, maintaining [celiac] | matched | Salmon Quinoa Plate | 809 | 809.6 | 0.1% | 1.31 | 27/27/46 | 0.569 |
| steak and rice / average man, maintaining [celiac] | matched | Lean Steak Rice Plate | 809 | 794.9 | 1.7% | 1.6 | 41/35/25 | 0.866 |
| spicy curry / average man, maintaining [celiac] | matched | Chickpea Curry Bowl | 809 | 740.6 | 8.5% | 1.6 | 18/70/12 | 0.452 |
