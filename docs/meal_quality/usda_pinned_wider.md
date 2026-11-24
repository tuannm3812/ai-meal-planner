## Measured

- calorie_model_version: `hist_gradient_boosting_deep_v0.1.0`
- calorie_model_sha256: `33a154b3d5807af1e2dd53ee69dc250e3f9a4429bfed90260e27671eac168c95`
- meal_corpus_sha256: `cebde36f88214e2bb08e21243f64c99046e13c131ea038931209dc2d4423b33c`
- meal_count: `76`
- retriever: `tfidf_vector_retriever_v0.1`
- nutrition_source: `usda_fooddata_central`
- usda_lookups: `39`
- usda_lookup_failures: `0`
- usda_no_usable_match: `0`
- usda_ingredients_cached: `39`

## Summary

- Plans: 152 (matched 152).
- **Meeting the targets** (calories within 10%, all macros in AMDR): 144 of 152.
- Within the 10% calorie target: 151 of 152 scaled plans.
- Within the service's 15% retry tolerance: 152 of 152 scaled plans.
- Calorie deviation: median 0.7%, 90th percentile 5.6%, max 10.3%.
- Rescaled by reconciliation: 4. First-pass scaling clamped: 67.
- Meal target as a share of the daily budget: 28.0% to 29.2%.
- Daily budget across profiles: 1200.0 to 2889.4 kcal.
- Macro share inside AMDR: protein 151, carbs 146, fat 147; all three 145 of 152.
- Plans with at least one estimated ingredient: 0 of 152.
- Plans with at least one USDA-verified ingredient: 148 of 152.
- Corpus matches scoring below 0.25: 0.

## Plans

| Scenario | Status | Meal | Target | Verified | Dev. | Scale | P/C/F % | Score |
|---|---|---|---:|---:|---:|---:|---|---:|
| Chicken Fried Rice / older sedentary woman, losing | matched | Chicken Fried Rice | 350 | 349.8 | 0.1% | 0.65 | 28/47/25 | 0.999 |
| Tofu Fried Rice / older sedentary woman, losing | matched | Tofu Fried Rice | 350 | 352.2 | 0.6% | 0.65 | 21/50/29 | 0.842 |
| High-Protein Turkey Burger Bowl / older sedentary woman, losing | matched | High-Protein Turkey Burger Bowl | 350 | 350.5 | 0.1% | 0.82 | 27/47/27 | 0.988 |
| High-Protein Tomato Turkey Pasta / older sedentary woman, losing | matched | High-Protein Tomato Turkey Pasta | 350 | 358.6 | 2.5% | 0.65 | 22/47/31 | 0.94 |
| Chicken Avocado Power Salad / older sedentary woman, losing | matched | Chicken Avocado Power Salad | 350 | 346.1 | 1.1% | 0.65 | 23/46/31 | 0.971 |
| High-Protein Asian Tofu Noodle Bowl / older sedentary woman, losing | matched | High-Protein Asian Tofu Noodle Bowl | 350 | 343.9 | 1.7% | 0.65 | 28/45/26 | 0.971 |
| Chicken Vegetable Stir Fry / older sedentary woman, losing | matched | Chicken Vegetable Stir Fry | 350 | 346.4 | 1.0% | 0.65 | 33/46/21 | 1.125 |
| Vegetarian Spinach Omelette / older sedentary woman, losing | matched | Vegetarian Spinach Omelette | 350 | 346.8 | 0.9% | 0.75 | 20/46/34 | 0.84 |
| Tuna Brown Rice Bowl / older sedentary woman, losing | matched | Tuna Brown Rice Bowl | 350 | 350.8 | 0.2% | 0.8 | 22/46/32 | 0.984 |
| Chicken Salad Wrap / older sedentary woman, losing | matched | Chicken Salad Wrap | 350 | 354.0 | 1.1% | 0.65 | 23/47/30 | 0.875 |
| Low-Sodium Chicken Rice Bowl / older sedentary woman, losing | matched | Low-Sodium Chicken Rice Bowl | 350 | 351.5 | 0.4% | 0.65 | 30/46/24 | 1.056 |
| Vegan Burrito Bowl / older sedentary woman, losing | matched | Vegan Burrito Bowl | 350 | 353.3 | 0.9% | 0.65 | 20/45/35 | 0.813 |
| Lean Steak Rice Plate / older sedentary woman, losing | matched | Lean Steak Rice Plate | 350 | 346.1 | 1.1% | 0.65 | 26/46/28 | 0.996 |
| Steak Salad Bowl / older sedentary woman, losing | matched | Steak Salad Bowl | 350 | 348.8 | 0.3% | 0.65 | 20/47/33 | 0.824 |
| Salmon Quinoa Plate / older sedentary woman, losing | matched | Salmon Quinoa Plate | 350 | 348.2 | 0.5% | 0.56 | 27/26/47 | 0.997 |
| Shrimp Taco Bowl / older sedentary woman, losing | matched | Shrimp Taco Bowl | 350 | 352.9 | 0.8% | 0.86 | 22/46/32 | 1.013 |
| Chickpea Curry Bowl / older sedentary woman, losing | matched | Chickpea Curry Bowl | 350 | 350.7 | 0.2% | 0.65 | 16/61/23 | 0.823 |
| Lentil Bolognese Pasta / older sedentary woman, losing | matched | Lentil Bolognese Pasta | 350 | 349.6 | 0.1% | 0.65 | 17/54/30 | 0.842 |
| Greek Chicken Bowl / older sedentary woman, losing | matched | Greek Chicken Bowl | 350 | 347.7 | 0.7% | 0.65 | 29/46/25 | 0.772 |
| Turkey Chili Bowl / older sedentary woman, losing | matched | Turkey Chili Bowl | 350 | 346.6 | 1.0% | 0.65 | 28/49/23 | 0.955 |
| Beef Taco Salad / older sedentary woman, losing | matched | Beef Taco Salad | 350 | 350.3 | 0.1% | 0.5 | 22/28/50 | 1.025 |
| Banana Oat Protein Bowl / older sedentary woman, losing | matched | Banana Oat Protein Bowl | 350 | 384.5 | 9.9% | 0.82 | 16/64/21 | 0.732 |
| Vegan Oat Bowl / older sedentary woman, losing | matched | Vegan Oat Bowl | 350 | 340.7 | 2.7% | 0.86 | 16/58/26 | 0.817 |
| Egg Breakfast Wrap / older sedentary woman, losing | matched | Egg Breakfast Wrap | 350 | 356.6 | 1.9% | 0.9 | 19/47/34 | 0.94 |
| Turkey Meatball Rice Bowl / older sedentary woman, losing | matched | Turkey Meatball Rice Bowl | 350 | 353.6 | 1.0% | 0.75 | 26/46/28 | 1.002 |
| Falafel Salad Bowl / older sedentary woman, losing | matched | Falafel Salad Bowl | 350 | 374.4 | 7.0% | 0.65 | 15/51/34 | 0.792 |
| Tuna Sushi Bowl / older sedentary woman, losing | matched | Tuna Sushi Bowl | 350 | 367.3 | 4.9% | 0.73 | 27/46/27 | 0.912 |
| Peanut Tofu Bowl / older sedentary woman, losing | matched | Peanut Tofu Bowl | 350 | 360.8 | 3.1% | 0.65 | 21/45/34 | 0.869 |
| Chicken Vegetable Soup Bowl / older sedentary woman, losing | matched | Chicken Vegetable Soup Bowl | 350 | 349.3 | 0.2% | 0.65 | 33/46/21 | 0.99 |
| Sweet Potato Chicken Plate / older sedentary woman, losing | matched | Sweet Potato Chicken Plate | 350 | 340.1 | 2.8% | 0.77 | 39/40/20 | 1.042 |
| Black Bean Burrito Bowl / older sedentary woman, losing | matched | Black Bean Burrito Bowl | 350 | 383.1 | 9.5% | 0.72 | 15/60/25 | 0.951 |
| Turkey Sweet Potato Hash / older sedentary woman, losing | matched | Turkey Sweet Potato Hash | 350 | 350.5 | 0.1% | 0.85 | 27/46/27 | 1.142 |
| Cottage Cheese Toast Plate / older sedentary woman, losing | matched | Cottage Cheese Toast Plate | 350 | 352.7 | 0.8% | 0.94 | 17/50/33 | 1.08 |
| Low-Sodium Salmon Salad / older sedentary woman, losing | matched | Low-Sodium Salmon Salad | 350 | 350.8 | 0.2% | 0.48 | 24/30/46 | 1.03 |
| Lemon Cod Potato Traybake / older sedentary woman, losing | matched | Lemon Cod Potato Traybake | 350 | 352.6 | 0.7% | 0.72 | 26/46/28 | 1.01 |
| Pork Stir Fry Noodles / older sedentary woman, losing | matched | Pork Stir Fry Noodles | 350 | 354.9 | 1.4% | 0.65 | 30/47/23 | 1.013 |
| Tempeh Quinoa Power Bowl / older sedentary woman, losing | matched | Tempeh Quinoa Power Bowl | 350 | 353.4 | 1.0% | 0.65 | 20/46/34 | 1.004 |
| Edamame Brown Rice Bowl / older sedentary woman, losing | matched | Edamame Brown Rice Bowl | 350 | 340.7 | 2.7% | 0.72 | 19/52/30 | 0.859 |
| Moroccan Chicken Couscous / older sedentary woman, losing | matched | Moroccan Chicken Couscous | 350 | 347.4 | 0.7% | 0.65 | 24/47/29 | 1.004 |
| Almond Crusted Chicken Plate / older sedentary woman, losing | matched | Almond Crusted Chicken Plate | 350 | 330.5 | 5.6% | 0.65 | 21/49/30 | 1.064 |
| Cashew Chicken Stir Fry / older sedentary woman, losing | matched | Cashew Chicken Stir Fry | 350 | 344.7 | 1.5% | 0.65 | 22/46/32 | 0.983 |
| Beef Mushroom Rice Bowl / older sedentary woman, losing | matched | Beef Mushroom Rice Bowl | 350 | 354.3 | 1.2% | 0.65 | 18/48/34 | 1.022 |
| Pumpkin Lentil Soup / older sedentary woman, losing | matched | Pumpkin Lentil Soup | 350 | 347.7 | 0.7% | 0.65 | 15/54/30 | 0.989 |
| Salmon Potato Salad / older sedentary woman, losing | matched | Salmon Potato Salad | 350 | 346.4 | 1.0% | 0.66 | 20/47/34 | 1.04 |
| Turkey Zucchini Pasta / older sedentary woman, losing | matched | Turkey Zucchini Pasta | 350 | 353.0 | 0.9% | 0.65 | 22/47/31 | 1.085 |
| Chickpea Hummus Wrap / older sedentary woman, losing | matched | Chickpea Hummus Wrap | 350 | 380.8 | 8.8% | 0.65 | 14/49/38 | 0.859 |
| Tofu Mushroom Noodle Soup / older sedentary woman, losing | matched | Tofu Mushroom Noodle Soup | 350 | 353.1 | 0.9% | 0.65 | 22/47/32 | 0.965 |
| Chicken Pumpkin Soup / older sedentary woman, losing | matched | Chicken Pumpkin Soup | 350 | 345.8 | 1.2% | 0.68 | 33/47/20 | 0.943 |
| Pork Sweet Potato Plate / older sedentary woman, losing | matched | Pork Sweet Potato Plate | 350 | 350.0 | 0.0% | 0.69 | 30/46/24 | 1.101 |
| Cod Fish Tacos / older sedentary woman, losing | matched | Cod Fish Tacos | 350 | 352.6 | 0.7% | 0.83 | 26/46/28 | 0.975 |
| Shrimp Couscous Bowl / older sedentary woman, losing | matched | Shrimp Couscous Bowl | 350 | 356.2 | 1.8% | 0.79 | 28/43/29 | 0.986 |
| Beef Potato Hash / older sedentary woman, losing | matched | Beef Potato Hash | 350 | 352.7 | 0.8% | 0.66 | 20/46/34 | 1.071 |
| Mushroom Egg Toast / older sedentary woman, losing | matched | Mushroom Egg Toast | 350 | 353.9 | 1.1% | 0.74 | 21/47/32 | 0.937 |
| Almond Banana Overnight Oats / older sedentary woman, losing | matched | Almond Banana Overnight Oats | 350 | 375.8 | 7.4% | 0.65 | 13/60/28 | 0.917 |
| Tempeh Taco Bowl / older sedentary woman, losing | matched | Tempeh Taco Bowl | 350 | 348.0 | 0.6% | 0.65 | 20/50/30 | 0.75 |
| Chicken Quinoa Salad / older sedentary woman, losing | matched | Chicken Quinoa Salad | 350 | 349.3 | 0.2% | 0.65 | 29/45/25 | 1.055 |
| Tuna Pasta Salad / older sedentary woman, losing | matched | Tuna Pasta Salad | 350 | 380.5 | 8.7% | 0.65 | 26/45/29 | 1.088 |
| Pork Fried Rice / older sedentary woman, losing | matched | Pork Fried Rice | 350 | 349.0 | 0.3% | 0.65 | 26/46/28 | 1.027 |
| Ginger Cod Rice Bowl / older sedentary woman, losing | matched | Ginger Cod Rice Bowl | 350 | 314.0 | 10.3% | 0.7 | 31/49/20 | 0.872 |
| Edamame Noodle Salad / older sedentary woman, losing | matched | Edamame Noodle Salad | 350 | 348.5 | 0.4% | 0.65 | 14/63/23 | 0.845 |
| Glazed Chicken Thigh Rice Bowl / older sedentary woman, losing | matched | Glazed Chicken Thigh Rice Bowl | 350 | 347.9 | 0.6% | 0.71 | 24/46/31 | 1.133 |
| Lentil Potato Curry / older sedentary woman, losing | matched | Lentil Potato Curry | 350 | 373.4 | 6.7% | 0.65 | 14/60/26 | 0.964 |
| Black Bean Quinoa Salad / older sedentary woman, losing | matched | Black Bean Quinoa Salad | 350 | 351.1 | 0.3% | 0.69 | 14/52/34 | 0.89 |
| Turkey Couscous Meatballs / older sedentary woman, losing | matched | Turkey Couscous Meatballs | 350 | 351.0 | 0.3% | 0.68 | 22/47/31 | 1.071 |
| Steak and Potato Wedges / older sedentary woman, losing | matched | Steak and Potato Wedges | 350 | 349.8 | 0.1% | 0.65 | 28/46/26 | 1.157 |
| Salmon Noodle Bowl / older sedentary woman, losing | matched | Salmon Noodle Bowl | 350 | 347.9 | 0.6% | 0.65 | 19/47/35 | 0.86 |
| Chicken Sweet Potato Tacos / older sedentary woman, losing | matched | Chicken Sweet Potato Tacos | 350 | 355.0 | 1.4% | 0.65 | 28/50/21 | 1.072 |
| Tofu Scramble Toast / older sedentary woman, losing | matched | Tofu Scramble Toast | 350 | 352.7 | 0.8% | 0.66 | 23/46/31 | 1.004 |
| Peanut Butter Banana Toast / older sedentary woman, losing | matched | Peanut Butter Banana Toast | 350 | 369.7 | 5.6% | 0.7 | 18/48/34 | 1.069 |
| Cashew Tofu Curry / older sedentary woman, losing | matched | Cashew Tofu Curry | 350 | 350.4 | 0.1% | 0.65 | 16/49/35 | 0.84 |
| Mediterranean Couscous Salad / older sedentary woman, losing | matched | Mediterranean Couscous Salad | 350 | 327.1 | 6.5% | 0.72 | 15/64/20 | 0.865 |
| Pork Burrito Bowl / older sedentary woman, losing | matched | Pork Burrito Bowl | 350 | 352.8 | 0.8% | 0.67 | 29/46/24 | 0.91 |
| Chicken Hummus Plate / older sedentary woman, losing | matched | Chicken Hummus Plate | 350 | 348.2 | 0.5% | 0.66 | 28/46/26 | 1.036 |
| Shrimp Noodle Stir Fry / older sedentary woman, losing | matched | Shrimp Noodle Stir Fry | 350 | 356.4 | 1.8% | 0.65 | 23/49/29 | 1.007 |
| Potato Zucchini Frittata / older sedentary woman, losing | matched | Potato Zucchini Frittata | 350 | 347.5 | 0.7% | 0.83 | 18/48/34 | 1.044 |
| Mushroom Tempeh Noodles / older sedentary woman, losing | matched | Mushroom Tempeh Noodles | 350 | 357.2 | 2.1% | 0.65 | 21/46/33 | 0.859 |
| Chicken Fried Rice / average man, maintaining | matched | Chicken Fried Rice | 809 | 811.2 | 0.3% | 1.11 | 30/48/22 | 0.999 |
| Tofu Fried Rice / average man, maintaining | matched | Tofu Fried Rice | 809 | 810.3 | 0.2% | 1.28 | 23/46/31 | 0.842 |
| High-Protein Turkey Burger Bowl / average man, maintaining | matched | High-Protein Turkey Burger Bowl | 809 | 806.5 | 0.3% | 1.6 | 27/46/27 | 0.988 |
| High-Protein Tomato Turkey Pasta / average man, maintaining | matched | High-Protein Tomato Turkey Pasta | 809 | 806.6 | 0.3% | 1.14 | 23/46/31 | 0.94 |
| Chicken Avocado Power Salad / average man, maintaining | matched | Chicken Avocado Power Salad | 809 | 811.9 | 0.4% | 1.28 | 26/46/28 | 0.971 |
| High-Protein Asian Tofu Noodle Bowl / average man, maintaining | matched | High-Protein Asian Tofu Noodle Bowl | 809 | 809.5 | 0.1% | 1.27 | 25/52/23 | 0.971 |
| Chicken Vegetable Stir Fry / average man, maintaining | matched | Chicken Vegetable Stir Fry | 809 | 808.5 | 0.1% | 1.28 | 30/46/24 | 1.125 |
| Vegetarian Spinach Omelette / average man, maintaining | matched | Vegetarian Spinach Omelette | 809 | 799.9 | 1.1% | 1.6 | 20/46/34 | 0.84 |
| Tuna Brown Rice Bowl / average man, maintaining | matched | Tuna Brown Rice Bowl | 809 | 808.8 | 0.0% | 1.6 | 26/46/28 | 0.984 |
| Chicken Salad Wrap / average man, maintaining | matched | Chicken Salad Wrap | 809 | 806.8 | 0.3% | 1.38 | 22/46/31 | 0.875 |
| Low-Sodium Chicken Rice Bowl / average man, maintaining | matched | Low-Sodium Chicken Rice Bowl | 809 | 808.7 | 0.0% | 1.44 | 30/46/24 | 1.056 |
| Vegan Burrito Bowl / average man, maintaining | matched | Vegan Burrito Bowl | 809 | 808.7 | 0.0% | 1.51 | 20/46/34 | 0.813 |
| Lean Steak Rice Plate / average man, maintaining | matched | Lean Steak Rice Plate | 809 | 810.6 | 0.2% | 1.37 | 24/46/30 | 0.996 |
| Steak Salad Bowl / average man, maintaining | matched | Steak Salad Bowl | 809 | 810.2 | 0.1% | 1.47 | 21/46/33 | 0.824 |
| Salmon Quinoa Plate / average man, maintaining | matched | Salmon Quinoa Plate | 809 | 814.9 | 0.7% | 1.31 | 22/46/33 | 0.997 |
| Shrimp Taco Bowl / average man, maintaining | matched | Shrimp Taco Bowl | 809 | 807.5 | 0.2% | 1.6 | 26/46/28 | 1.013 |
| Chickpea Curry Bowl / average man, maintaining | matched | Chickpea Curry Bowl | 809 | 819.9 | 1.3% | 1.46 | 15/59/26 | 0.823 |
| Lentil Bolognese Pasta / average man, maintaining | matched | Lentil Bolognese Pasta | 809 | 840.5 | 3.9% | 1.14 | 18/62/21 | 0.842 |
| Greek Chicken Bowl / average man, maintaining | matched | Greek Chicken Bowl | 809 | 766.7 | 5.2% | 1.45 | 25/46/29 | 0.772 |
| Turkey Chili Bowl / average man, maintaining | matched | Turkey Chili Bowl | 809 | 807.3 | 0.2% | 1.45 | 29/47/25 | 0.955 |
| Beef Taco Salad / average man, maintaining | matched | Beef Taco Salad | 809 | 880.9 | 8.9% | 1.26 | 22/28/50 | 1.025 |
| Banana Oat Protein Bowl / average man, maintaining | matched | Banana Oat Protein Bowl | 809 | 771.1 | 4.7% | 1.6 | 16/63/22 | 0.732 |
| Vegan Oat Bowl / average man, maintaining | matched | Vegan Oat Bowl | 809 | 739.0 | 8.7% | 1.6 | 16/60/24 | 0.817 |
| Egg Breakfast Wrap / average man, maintaining | matched | Egg Breakfast Wrap | 809 | 806.1 | 0.4% | 1.6 | 18/48/34 | 0.94 |
| Turkey Meatball Rice Bowl / average man, maintaining | matched | Turkey Meatball Rice Bowl | 809 | 808.4 | 0.1% | 1.6 | 26/46/28 | 1.002 |
| Falafel Salad Bowl / average man, maintaining | matched | Falafel Salad Bowl | 809 | 811.7 | 0.3% | 1.43 | 15/52/32 | 0.792 |
| Tuna Sushi Bowl / average man, maintaining | matched | Tuna Sushi Bowl | 809 | 798.4 | 1.3% | 1.6 | 28/46/26 | 0.912 |
| Peanut Tofu Bowl / average man, maintaining | matched | Peanut Tofu Bowl | 809 | 811.6 | 0.3% | 1.42 | 21/46/33 | 0.869 |
| Chicken Vegetable Soup Bowl / average man, maintaining | matched | Chicken Vegetable Soup Bowl | 809 | 808.1 | 0.1% | 1.46 | 29/46/25 | 0.99 |
| Sweet Potato Chicken Plate / average man, maintaining | matched | Sweet Potato Chicken Plate | 809 | 811.2 | 0.3% | 1.4 | 32/46/22 | 1.042 |
| Black Bean Burrito Bowl / average man, maintaining | matched | Black Bean Burrito Bowl | 809 | 841.7 | 4.0% | 1.6 | 15/60/24 | 0.951 |
| Turkey Sweet Potato Hash / average man, maintaining | matched | Turkey Sweet Potato Hash | 809 | 813.6 | 0.6% | 1.6 | 27/46/28 | 1.142 |
| Cottage Cheese Toast Plate / average man, maintaining | matched | Cottage Cheese Toast Plate | 809 | 811.2 | 0.3% | 1.6 | 18/55/27 | 1.08 |
| Low-Sodium Salmon Salad / average man, maintaining | matched | Low-Sodium Salmon Salad | 809 | 807.9 | 0.1% | 1.18 | 19/47/34 | 1.03 |
| Lemon Cod Potato Traybake / average man, maintaining | matched | Lemon Cod Potato Traybake | 809 | 808.9 | 0.0% | 1.6 | 28/47/25 | 1.01 |
| Pork Stir Fry Noodles / average man, maintaining | matched | Pork Stir Fry Noodles | 809 | 803.2 | 0.7% | 1.18 | 26/54/20 | 1.013 |
| Tempeh Quinoa Power Bowl / average man, maintaining | matched | Tempeh Quinoa Power Bowl | 809 | 804.2 | 0.6% | 1.41 | 21/46/33 | 1.004 |
| Edamame Brown Rice Bowl / average man, maintaining | matched | Edamame Brown Rice Bowl | 809 | 803.3 | 0.7% | 1.6 | 18/50/32 | 0.859 |
| Moroccan Chicken Couscous / average man, maintaining | matched | Moroccan Chicken Couscous | 809 | 803.9 | 0.6% | 1.34 | 22/46/32 | 1.004 |
| Almond Crusted Chicken Plate / average man, maintaining | matched | Almond Crusted Chicken Plate | 809 | 805.9 | 0.4% | 1.26 | 25/46/29 | 1.064 |
| Cashew Chicken Stir Fry / average man, maintaining | matched | Cashew Chicken Stir Fry | 809 | 810.9 | 0.2% | 1.16 | 28/51/21 | 0.983 |
| Beef Mushroom Rice Bowl / average man, maintaining | matched | Beef Mushroom Rice Bowl | 809 | 814.4 | 0.7% | 1.45 | 19/47/34 | 1.022 |
| Pumpkin Lentil Soup / average man, maintaining | matched | Pumpkin Lentil Soup | 809 | 823.5 | 1.8% | 1.44 | 17/57/26 | 0.989 |
| Salmon Potato Salad / average man, maintaining | matched | Salmon Potato Salad | 809 | 805.5 | 0.4% | 1.52 | 21/46/33 | 1.04 |
| Turkey Zucchini Pasta / average man, maintaining | matched | Turkey Zucchini Pasta | 809 | 812.8 | 0.5% | 1.27 | 23/46/31 | 1.085 |
| Chickpea Hummus Wrap / average man, maintaining | matched | Chickpea Hummus Wrap | 809 | 839.8 | 3.8% | 1.5 | 15/52/34 | 0.859 |
| Tofu Mushroom Noodle Soup / average man, maintaining | matched | Tofu Mushroom Noodle Soup | 809 | 849.2 | 5.0% | 1.36 | 23/47/30 | 0.965 |
| Chicken Pumpkin Soup / average man, maintaining | matched | Chicken Pumpkin Soup | 809 | 808.7 | 0.0% | 1.58 | 30/46/24 | 0.943 |
| Pork Sweet Potato Plate / average man, maintaining | matched | Pork Sweet Potato Plate | 809 | 807.9 | 0.1% | 1.6 | 28/46/26 | 1.101 |
| Cod Fish Tacos / average man, maintaining | matched | Cod Fish Tacos | 809 | 813.8 | 0.6% | 1.6 | 26/48/26 | 0.975 |
| Shrimp Couscous Bowl / average man, maintaining | matched | Shrimp Couscous Bowl | 809 | 801.0 | 1.0% | 1.6 | 28/52/20 | 0.986 |
| Beef Potato Hash / average man, maintaining | matched | Beef Potato Hash | 809 | 805.5 | 0.4% | 1.53 | 20/46/34 | 1.071 |
| Mushroom Egg Toast / average man, maintaining | matched | Mushroom Egg Toast | 809 | 804.7 | 0.5% | 1.6 | 24/46/30 | 0.937 |
| Almond Banana Overnight Oats / average man, maintaining | matched | Almond Banana Overnight Oats | 809 | 867.0 | 7.2% | 1.48 | 13/60/27 | 0.917 |
| Tempeh Taco Bowl / average man, maintaining | matched | Tempeh Taco Bowl | 809 | 812.9 | 0.5% | 1.36 | 22/46/32 | 0.75 |
| Chicken Quinoa Salad / average man, maintaining | matched | Chicken Quinoa Salad | 809 | 810.0 | 0.1% | 1.44 | 26/46/29 | 1.055 |
| Tuna Pasta Salad / average man, maintaining | matched | Tuna Pasta Salad | 809 | 809.4 | 0.0% | 1.4 | 26/46/28 | 1.088 |
| Pork Fried Rice / average man, maintaining | matched | Pork Fried Rice | 809 | 806.7 | 0.3% | 1.35 | 27/46/27 | 1.027 |
| Ginger Cod Rice Bowl / average man, maintaining | matched | Ginger Cod Rice Bowl | 809 | 741.2 | 8.4% | 1.6 | 29/47/24 | 0.872 |
| Edamame Noodle Salad / average man, maintaining | matched | Edamame Noodle Salad | 809 | 808.0 | 0.1% | 1.47 | 14/64/22 | 0.845 |
| Glazed Chicken Thigh Rice Bowl / average man, maintaining | matched | Glazed Chicken Thigh Rice Bowl | 809 | 809.1 | 0.0% | 1.6 | 24/46/30 | 1.133 |
| Lentil Potato Curry / average man, maintaining | matched | Lentil Potato Curry | 809 | 825.3 | 2.0% | 1.45 | 14/62/24 | 0.964 |
| Black Bean Quinoa Salad / average man, maintaining | matched | Black Bean Quinoa Salad | 809 | 870.8 | 7.6% | 1.6 | 14/53/33 | 0.89 |
| Turkey Couscous Meatballs / average man, maintaining | matched | Turkey Couscous Meatballs | 809 | 808.1 | 0.1% | 1.58 | 20/46/34 | 1.071 |
| Steak and Potato Wedges / average man, maintaining | matched | Steak and Potato Wedges | 809 | 810.8 | 0.2% | 1.44 | 25/46/29 | 1.157 |
| Salmon Noodle Bowl / average man, maintaining | matched | Salmon Noodle Bowl | 809 | 776.7 | 4.0% | 1.26 | 22/46/32 | 0.86 |
| Chicken Sweet Potato Tacos / average man, maintaining | matched | Chicken Sweet Potato Tacos | 809 | 731.9 | 9.5% | 1.35 | 29/49/22 | 1.072 |
| Tofu Scramble Toast / average man, maintaining | matched | Tofu Scramble Toast | 809 | 810.2 | 0.1% | 1.52 | 26/46/27 | 1.004 |
| Peanut Butter Banana Toast / average man, maintaining | matched | Peanut Butter Banana Toast | 809 | 822.6 | 1.7% | 1.6 | 18/50/32 | 1.069 |
| Cashew Tofu Curry / average man, maintaining | matched | Cashew Tofu Curry | 809 | 819.5 | 1.3% | 1.4 | 22/45/33 | 0.84 |
| Mediterranean Couscous Salad / average man, maintaining | matched | Mediterranean Couscous Salad | 809 | 769.4 | 4.9% | 1.6 | 14/62/24 | 0.865 |
| Pork Burrito Bowl / average man, maintaining | matched | Pork Burrito Bowl | 809 | 805.4 | 0.4% | 1.55 | 29/46/25 | 0.91 |
| Chicken Hummus Plate / average man, maintaining | matched | Chicken Hummus Plate | 809 | 808.5 | 0.1% | 1.53 | 29/46/25 | 1.036 |
| Shrimp Noodle Stir Fry / average man, maintaining | matched | Shrimp Noodle Stir Fry | 809 | 799.0 | 1.2% | 1.29 | 21/54/26 | 1.007 |
| Potato Zucchini Frittata / average man, maintaining | matched | Potato Zucchini Frittata | 809 | 809.5 | 0.1% | 1.6 | 19/46/35 | 1.044 |
| Mushroom Tempeh Noodles / average man, maintaining | matched | Mushroom Tempeh Noodles | 809 | 842.5 | 4.1% | 1.36 | 20/51/29 | 0.859 |
