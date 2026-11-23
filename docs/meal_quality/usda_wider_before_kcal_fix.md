## Measured

- calorie_model_version: `hist_gradient_boosting_deep_v0.1.0`
- calorie_model_sha256: `33a154b3d5807af1e2dd53ee69dc250e3f9a4429bfed90260e27671eac168c95`
- meal_corpus_sha256: `cebde36f88214e2bb08e21243f64c99046e13c131ea038931209dc2d4423b33c`
- meal_count: `76`
- retriever: `tfidf_vector_retriever_v0.1`
- nutrition_source: `usda_fooddata_central`
- usda_lookups: `140`
- usda_lookup_failures: `0`
- usda_no_usable_match: `102`
- usda_ingredients_cached: `38`

## Summary

- Plans: 152 (matched 152).
- **Meeting the targets** (calories within 10%, all macros in AMDR): 108 of 152.
- Within the 10% calorie target: 140 of 152 scaled plans.
- Within the service's 15% retry tolerance: 142 of 152 scaled plans.
- Calorie deviation: median 1.2%, 90th percentile 8.6%, max 103.5%.
- Rescaled by reconciliation: 42. First-pass scaling clamped: 67.
- Meal target as a share of the daily budget: 28.0% to 29.2%.
- Daily budget across profiles: 1200.0 to 2889.4 kcal.
- Macro share inside AMDR: protein 151, carbs 115, fat 113; all three 112 of 152.
- Plans with at least one estimated ingredient: 52 of 152.
- Plans with at least one USDA-verified ingredient: 148 of 152.
- Corpus matches scoring below 0.25: 0.

## Plans

| Scenario | Status | Meal | Target | Verified | Dev. | Scale | P/C/F % | Score |
|---|---|---|---:|---:|---:|---:|---|---:|
| Chicken Fried Rice / older sedentary woman, losing | matched | Chicken Fried Rice | 350 | 353.0 | 0.9% | 0.65 | 29/46/25 | 0.999 |
| Tofu Fried Rice / older sedentary woman, losing | matched | Tofu Fried Rice | 350 | 316.3 | 9.6% | 0.65 | 21/50/29 | 0.842 |
| High-Protein Turkey Burger Bowl / older sedentary woman, losing | matched | High-Protein Turkey Burger Bowl | 350 | 350.5 | 0.1% | 0.57 | 23/24/53 | 0.988 |
| High-Protein Tomato Turkey Pasta / older sedentary woman, losing | matched | High-Protein Tomato Turkey Pasta | 350 | 358.4 | 2.4% | 0.5 | 20/23/57 | 0.94 |
| Chicken Avocado Power Salad / older sedentary woman, losing | matched | Chicken Avocado Power Salad | 350 | 365.7 | 4.5% | 0.65 | 20/53/27 | 0.971 |
| High-Protein Asian Tofu Noodle Bowl / older sedentary woman, losing | matched | High-Protein Asian Tofu Noodle Bowl | 350 | 343.4 | 1.9% | 0.65 | 28/50/21 | 0.971 |
| Chicken Vegetable Stir Fry / older sedentary woman, losing | matched | Chicken Vegetable Stir Fry | 350 | 360.8 | 3.1% | 0.45 | 27/54/19 | 1.125 |
| Vegetarian Spinach Omelette / older sedentary woman, losing | matched | Vegetarian Spinach Omelette | 350 | 352.3 | 0.7% | 0.56 | 16/29/55 | 0.84 |
| Tuna Brown Rice Bowl / older sedentary woman, losing | matched | Tuna Brown Rice Bowl | 350 | 637.2 | 82.1% | 0.52 | 20/48/32 | 0.984 |
| Chicken Salad Wrap / older sedentary woman, losing | matched | Chicken Salad Wrap | 350 | 398.4 | 13.8% | 0.65 | 30/26/44 | 0.875 |
| Low-Sodium Chicken Rice Bowl / older sedentary woman, losing | matched | Low-Sodium Chicken Rice Bowl | 350 | 346.2 | 1.1% | 0.65 | 31/46/23 | 1.056 |
| Vegan Burrito Bowl / older sedentary woman, losing | matched | Vegan Burrito Bowl | 350 | 337.8 | 3.5% | 0.65 | 14/54/33 | 0.813 |
| Lean Steak Rice Plate / older sedentary woman, losing | matched | Lean Steak Rice Plate | 350 | 343.0 | 2.0% | 0.65 | 32/46/22 | 0.996 |
| Steak Salad Bowl / older sedentary woman, losing | matched | Steak Salad Bowl | 350 | 347.1 | 0.8% | 0.65 | 24/46/30 | 0.824 |
| Salmon Quinoa Plate / older sedentary woman, losing | matched | Salmon Quinoa Plate | 350 | 352.0 | 0.6% | 0.51 | 25/22/54 | 0.997 |
| Shrimp Taco Bowl / older sedentary woman, losing | matched | Shrimp Taco Bowl | 350 | 712.3 | 103.5% | 0.56 | 22/49/29 | 1.013 |
| Chickpea Curry Bowl / older sedentary woman, losing | matched | Chickpea Curry Bowl | 350 | 350.1 | 0.0% | 0.65 | 15/64/21 | 0.823 |
| Lentil Bolognese Pasta / older sedentary woman, losing | matched | Lentil Bolognese Pasta | 350 | 349.6 | 0.1% | 0.65 | 18/53/29 | 0.842 |
| Greek Chicken Bowl / older sedentary woman, losing | matched | Greek Chicken Bowl | 350 | 347.7 | 0.7% | 0.65 | 29/46/25 | 0.772 |
| Turkey Chili Bowl / older sedentary woman, losing | matched | Turkey Chili Bowl | 350 | 333.3 | 4.8% | 0.65 | 21/49/31 | 0.955 |
| Beef Taco Salad / older sedentary woman, losing | matched | Beef Taco Salad | 350 | 356.0 | 1.7% | 0.42 | 19/21/60 | 1.025 |
| Banana Oat Protein Bowl / older sedentary woman, losing | matched | Banana Oat Protein Bowl | 350 | 384.5 | 9.9% | 0.82 | 16/64/21 | 0.732 |
| Vegan Oat Bowl / older sedentary woman, losing | matched | Vegan Oat Bowl | 350 | 340.7 | 2.7% | 0.86 | 16/58/26 | 0.817 |
| Egg Breakfast Wrap / older sedentary woman, losing | matched | Egg Breakfast Wrap | 350 | 340.0 | 2.9% | 0.9 | 19/47/34 | 0.94 |
| Turkey Meatball Rice Bowl / older sedentary woman, losing | matched | Turkey Meatball Rice Bowl | 350 | 465.3 | 32.9% | 0.49 | 18/45/37 | 1.002 |
| Falafel Salad Bowl / older sedentary woman, losing | matched | Falafel Salad Bowl | 350 | 374.4 | 7.0% | 0.65 | 15/51/34 | 0.792 |
| Tuna Sushi Bowl / older sedentary woman, losing | matched | Tuna Sushi Bowl | 350 | 458.0 | 30.9% | 0.47 | 23/31/46 | 0.912 |
| Peanut Tofu Bowl / older sedentary woman, losing | matched | Peanut Tofu Bowl | 350 | 346.1 | 1.1% | 0.65 | 22/46/32 | 0.869 |
| Chicken Vegetable Soup Bowl / older sedentary woman, losing | matched | Chicken Vegetable Soup Bowl | 350 | 348.9 | 0.3% | 0.65 | 31/46/24 | 0.99 |
| Sweet Potato Chicken Plate / older sedentary woman, losing | matched | Sweet Potato Chicken Plate | 350 | 343.1 | 2.0% | 0.79 | 41/39/20 | 1.042 |
| Black Bean Burrito Bowl / older sedentary woman, losing | matched | Black Bean Burrito Bowl | 350 | 330.5 | 5.6% | 0.72 | 13/60/27 | 0.951 |
| Turkey Sweet Potato Hash / older sedentary woman, losing | matched | Turkey Sweet Potato Hash | 350 | 353.0 | 0.9% | 0.59 | 21/28/51 | 1.142 |
| Cottage Cheese Toast Plate / older sedentary woman, losing | matched | Cottage Cheese Toast Plate | 350 | 352.5 | 0.7% | 0.94 | 16/50/34 | 1.08 |
| Low-Sodium Salmon Salad / older sedentary woman, losing | matched | Low-Sodium Salmon Salad | 350 | 349.8 | 0.1% | 0.42 | 21/27/52 | 1.03 |
| Lemon Cod Potato Traybake / older sedentary woman, losing | matched | Lemon Cod Potato Traybake | 350 | 410.0 | 17.1% | 0.47 | 12/31/56 | 1.01 |
| Pork Stir Fry Noodles / older sedentary woman, losing | matched | Pork Stir Fry Noodles | 350 | 341.0 | 2.6% | 0.65 | 29/50/21 | 1.013 |
| Tempeh Quinoa Power Bowl / older sedentary woman, losing | matched | Tempeh Quinoa Power Bowl | 350 | 351.3 | 0.4% | 0.65 | 20/46/34 | 1.004 |
| Edamame Brown Rice Bowl / older sedentary woman, losing | matched | Edamame Brown Rice Bowl | 350 | 349.0 | 0.3% | 0.72 | 16/61/24 | 0.859 |
| Moroccan Chicken Couscous / older sedentary woman, losing | matched | Moroccan Chicken Couscous | 350 | 362.8 | 3.7% | 0.49 | 19/36/46 | 1.004 |
| Almond Crusted Chicken Plate / older sedentary woman, losing | matched | Almond Crusted Chicken Plate | 350 | 330.9 | 5.5% | 0.65 | 21/48/31 | 1.064 |
| Cashew Chicken Stir Fry / older sedentary woman, losing | matched | Cashew Chicken Stir Fry | 350 | 341.1 | 2.5% | 0.65 | 22/47/31 | 0.983 |
| Beef Mushroom Rice Bowl / older sedentary woman, losing | matched | Beef Mushroom Rice Bowl | 350 | 353.3 | 0.9% | 0.65 | 17/49/34 | 1.022 |
| Pumpkin Lentil Soup / older sedentary woman, losing | matched | Pumpkin Lentil Soup | 350 | 378.9 | 8.3% | 0.65 | 16/57/27 | 0.989 |
| Salmon Potato Salad / older sedentary woman, losing | matched | Salmon Potato Salad | 350 | 356.8 | 1.9% | 0.49 | 20/18/61 | 1.04 |
| Turkey Zucchini Pasta / older sedentary woman, losing | matched | Turkey Zucchini Pasta | 350 | 349.2 | 0.2% | 0.56 | 20/25/55 | 1.085 |
| Chickpea Hummus Wrap / older sedentary woman, losing | matched | Chickpea Hummus Wrap | 350 | 354.8 | 1.4% | 0.54 | 12/45/43 | 0.859 |
| Tofu Mushroom Noodle Soup / older sedentary woman, losing | matched | Tofu Mushroom Noodle Soup | 350 | 335.8 | 4.1% | 0.65 | 18/55/27 | 0.965 |
| Chicken Pumpkin Soup / older sedentary woman, losing | matched | Chicken Pumpkin Soup | 350 | 366.2 | 4.6% | 0.48 | 27/28/45 | 0.943 |
| Pork Sweet Potato Plate / older sedentary woman, losing | matched | Pork Sweet Potato Plate | 350 | 353.6 | 1.0% | 0.69 | 33/46/21 | 1.101 |
| Cod Fish Tacos / older sedentary woman, losing | matched | Cod Fish Tacos | 350 | 356.4 | 1.8% | 0.54 | 12/41/47 | 0.975 |
| Shrimp Couscous Bowl / older sedentary woman, losing | matched | Shrimp Couscous Bowl | 350 | 465.8 | 33.1% | 0.51 | 35/44/21 | 0.986 |
| Beef Potato Hash / older sedentary woman, losing | matched | Beef Potato Hash | 350 | 374.3 | 6.9% | 0.43 | 17/18/64 | 1.071 |
| Mushroom Egg Toast / older sedentary woman, losing | matched | Mushroom Egg Toast | 350 | 349.8 | 0.1% | 0.74 | 20/46/34 | 0.937 |
| Almond Banana Overnight Oats / older sedentary woman, losing | matched | Almond Banana Overnight Oats | 350 | 376.5 | 7.6% | 0.65 | 13/58/29 | 0.917 |
| Tempeh Taco Bowl / older sedentary woman, losing | matched | Tempeh Taco Bowl | 350 | 340.8 | 2.6% | 0.65 | 18/57/25 | 0.75 |
| Chicken Quinoa Salad / older sedentary woman, losing | matched | Chicken Quinoa Salad | 350 | 348.8 | 0.3% | 0.65 | 29/46/25 | 1.055 |
| Tuna Pasta Salad / older sedentary woman, losing | matched | Tuna Pasta Salad | 350 | 355.3 | 1.5% | 0.65 | 27/47/26 | 1.088 |
| Pork Fried Rice / older sedentary woman, losing | matched | Pork Fried Rice | 350 | 352.3 | 0.7% | 0.65 | 28/46/26 | 1.027 |
| Ginger Cod Rice Bowl / older sedentary woman, losing | matched | Ginger Cod Rice Bowl | 350 | 378.0 | 8.0% | 0.7 | 13/62/25 | 0.872 |
| Edamame Noodle Salad / older sedentary woman, losing | matched | Edamame Noodle Salad | 350 | 349.0 | 0.3% | 0.65 | 15/62/23 | 0.845 |
| Glazed Chicken Thigh Rice Bowl / older sedentary woman, losing | matched | Glazed Chicken Thigh Rice Bowl | 350 | 361.7 | 3.3% | 0.6 | 19/29/52 | 1.133 |
| Lentil Potato Curry / older sedentary woman, losing | matched | Lentil Potato Curry | 350 | 350.5 | 0.1% | 0.65 | 16/51/33 | 0.964 |
| Black Bean Quinoa Salad / older sedentary woman, losing | matched | Black Bean Quinoa Salad | 350 | 357.1 | 2.0% | 0.5 | 11/42/46 | 0.89 |
| Turkey Couscous Meatballs / older sedentary woman, losing | matched | Turkey Couscous Meatballs | 350 | 364.2 | 4.1% | 0.52 | 19/29/52 | 1.071 |
| Steak and Potato Wedges / older sedentary woman, losing | matched | Steak and Potato Wedges | 350 | 356.8 | 1.9% | 0.51 | 26/20/54 | 1.157 |
| Salmon Noodle Bowl / older sedentary woman, losing | matched | Salmon Noodle Bowl | 350 | 345.1 | 1.4% | 0.65 | 21/46/33 | 0.86 |
| Chicken Sweet Potato Tacos / older sedentary woman, losing | matched | Chicken Sweet Potato Tacos | 350 | 341.4 | 2.5% | 0.65 | 29/46/25 | 1.072 |
| Tofu Scramble Toast / older sedentary woman, losing | matched | Tofu Scramble Toast | 350 | 352.0 | 0.6% | 0.66 | 22/49/29 | 1.004 |
| Peanut Butter Banana Toast / older sedentary woman, losing | matched | Peanut Butter Banana Toast | 350 | 354.3 | 1.2% | 0.7 | 17/49/34 | 1.069 |
| Cashew Tofu Curry / older sedentary woman, losing | matched | Cashew Tofu Curry | 350 | 353.4 | 1.0% | 0.65 | 16/49/35 | 0.84 |
| Mediterranean Couscous Salad / older sedentary woman, losing | matched | Mediterranean Couscous Salad | 350 | 345.8 | 1.2% | 0.72 | 15/65/20 | 0.865 |
| Pork Burrito Bowl / older sedentary woman, losing | matched | Pork Burrito Bowl | 350 | 354.1 | 1.2% | 0.67 | 20/58/22 | 0.91 |
| Chicken Hummus Plate / older sedentary woman, losing | matched | Chicken Hummus Plate | 350 | 348.5 | 0.4% | 0.66 | 23/46/31 | 1.036 |
| Shrimp Noodle Stir Fry / older sedentary woman, losing | matched | Shrimp Noodle Stir Fry | 350 | 366.9 | 4.8% | 0.65 | 24/53/23 | 1.007 |
| Potato Zucchini Frittata / older sedentary woman, losing | matched | Potato Zucchini Frittata | 350 | 361.3 | 3.2% | 0.63 | 19/19/62 | 1.044 |
| Mushroom Tempeh Noodles / older sedentary woman, losing | matched | Mushroom Tempeh Noodles | 350 | 384.3 | 9.8% | 0.65 | 20/50/31 | 0.859 |
| Chicken Fried Rice / average man, maintaining | matched | Chicken Fried Rice | 809 | 808.8 | 0.0% | 1.11 | 30/48/22 | 0.999 |
| Tofu Fried Rice / average man, maintaining | matched | Tofu Fried Rice | 809 | 810.3 | 0.2% | 1.28 | 18/59/23 | 0.842 |
| High-Protein Turkey Burger Bowl / average man, maintaining | matched | High-Protein Turkey Burger Bowl | 809 | 813.7 | 0.6% | 1.32 | 23/24/53 | 0.988 |
| High-Protein Tomato Turkey Pasta / average man, maintaining | matched | High-Protein Tomato Turkey Pasta | 809 | 772.8 | 4.5% | 1.14 | 20/47/34 | 0.94 |
| Chicken Avocado Power Salad / average man, maintaining | matched | Chicken Avocado Power Salad | 809 | 811.6 | 0.3% | 1.28 | 25/47/28 | 0.971 |
| High-Protein Asian Tofu Noodle Bowl / average man, maintaining | matched | High-Protein Asian Tofu Noodle Bowl | 809 | 806.7 | 0.3% | 1.27 | 27/52/21 | 0.971 |
| Chicken Vegetable Stir Fry / average man, maintaining | matched | Chicken Vegetable Stir Fry | 809 | 813.8 | 0.6% | 1.28 | 31/46/23 | 1.125 |
| Vegetarian Spinach Omelette / average man, maintaining | matched | Vegetarian Spinach Omelette | 809 | 795.9 | 1.6% | 1.3 | 17/30/54 | 0.84 |
| Tuna Brown Rice Bowl / average man, maintaining | matched | Tuna Brown Rice Bowl | 809 | 1275.0 | 57.6% | 1.04 | 19/49/32 | 0.984 |
| Chicken Salad Wrap / average man, maintaining | matched | Chicken Salad Wrap | 809 | 869.5 | 7.5% | 1.38 | 29/26/45 | 0.875 |
| Low-Sodium Chicken Rice Bowl / average man, maintaining | matched | Low-Sodium Chicken Rice Bowl | 809 | 804.5 | 0.6% | 1.44 | 30/46/24 | 1.056 |
| Vegan Burrito Bowl / average man, maintaining | matched | Vegan Burrito Bowl | 809 | 803.8 | 0.6% | 1.51 | 13/54/33 | 0.813 |
| Lean Steak Rice Plate / average man, maintaining | matched | Lean Steak Rice Plate | 809 | 815.9 | 0.9% | 1.37 | 29/46/25 | 0.996 |
| Steak Salad Bowl / average man, maintaining | matched | Steak Salad Bowl | 809 | 809.1 | 0.0% | 1.47 | 25/46/29 | 0.824 |
| Salmon Quinoa Plate / average man, maintaining | matched | Salmon Quinoa Plate | 809 | 920.8 | 13.8% | 1.31 | 24/22/54 | 0.997 |
| Shrimp Taco Bowl / average man, maintaining | matched | Shrimp Taco Bowl | 809 | 1316.8 | 62.8% | 1.04 | 22/48/30 | 1.013 |
| Chickpea Curry Bowl / average man, maintaining | matched | Chickpea Curry Bowl | 809 | 818.5 | 1.2% | 1.46 | 14/62/24 | 0.823 |
| Lentil Bolognese Pasta / average man, maintaining | matched | Lentil Bolognese Pasta | 809 | 808.9 | 0.0% | 1.56 | 19/56/25 | 0.842 |
| Greek Chicken Bowl / average man, maintaining | matched | Greek Chicken Bowl | 809 | 766.7 | 5.2% | 1.45 | 25/46/29 | 0.772 |
| Turkey Chili Bowl / average man, maintaining | matched | Turkey Chili Bowl | 809 | 798.1 | 1.3% | 1.45 | 21/50/30 | 0.955 |
| Beef Taco Salad / average man, maintaining | matched | Beef Taco Salad | 809 | 804.0 | 0.6% | 0.94 | 18/23/59 | 1.025 |
| Banana Oat Protein Bowl / average man, maintaining | matched | Banana Oat Protein Bowl | 809 | 771.1 | 4.7% | 1.6 | 16/63/22 | 0.732 |
| Vegan Oat Bowl / average man, maintaining | matched | Vegan Oat Bowl | 809 | 739.0 | 8.7% | 1.6 | 16/60/24 | 0.817 |
| Egg Breakfast Wrap / average man, maintaining | matched | Egg Breakfast Wrap | 809 | 803.2 | 0.7% | 1.6 | 19/47/34 | 0.94 |
| Turkey Meatball Rice Bowl / average man, maintaining | matched | Turkey Meatball Rice Bowl | 809 | 808.2 | 0.1% | 1.6 | 18/47/34 | 1.002 |
| Falafel Salad Bowl / average man, maintaining | matched | Falafel Salad Bowl | 809 | 811.7 | 0.3% | 1.43 | 15/52/32 | 0.792 |
| Tuna Sushi Bowl / average man, maintaining | matched | Tuna Sushi Bowl | 809 | 990.1 | 22.4% | 1.04 | 24/32/44 | 0.912 |
| Peanut Tofu Bowl / average man, maintaining | matched | Peanut Tofu Bowl | 809 | 814.1 | 0.6% | 1.42 | 21/49/29 | 0.869 |
| Chicken Vegetable Soup Bowl / average man, maintaining | matched | Chicken Vegetable Soup Bowl | 809 | 817.7 | 1.1% | 1.46 | 26/46/27 | 0.99 |
| Sweet Potato Chicken Plate / average man, maintaining | matched | Sweet Potato Chicken Plate | 809 | 807.8 | 0.1% | 1.4 | 32/46/22 | 1.042 |
| Black Bean Burrito Bowl / average man, maintaining | matched | Black Bean Burrito Bowl | 809 | 822.1 | 1.6% | 1.6 | 13/60/27 | 0.951 |
| Turkey Sweet Potato Hash / average man, maintaining | matched | Turkey Sweet Potato Hash | 809 | 811.3 | 0.3% | 1.6 | 17/49/34 | 1.142 |
| Cottage Cheese Toast Plate / average man, maintaining | matched | Cottage Cheese Toast Plate | 809 | 815.9 | 0.9% | 1.6 | 15/50/35 | 1.08 |
| Low-Sodium Salmon Salad / average man, maintaining | matched | Low-Sodium Salmon Salad | 809 | 812.3 | 0.4% | 0.99 | 21/27/52 | 1.03 |
| Lemon Cod Potato Traybake / average man, maintaining | matched | Lemon Cod Potato Traybake | 809 | 962.2 | 18.9% | 1.04 | 12/30/58 | 1.01 |
| Pork Stir Fry Noodles / average man, maintaining | matched | Pork Stir Fry Noodles | 809 | 823.0 | 1.7% | 1.18 | 22/55/23 | 1.013 |
| Tempeh Quinoa Power Bowl / average man, maintaining | matched | Tempeh Quinoa Power Bowl | 809 | 809.3 | 0.0% | 1.41 | 21/46/33 | 1.004 |
| Edamame Brown Rice Bowl / average man, maintaining | matched | Edamame Brown Rice Bowl | 809 | 810.1 | 0.1% | 1.6 | 15/59/26 | 0.859 |
| Moroccan Chicken Couscous / average man, maintaining | matched | Moroccan Chicken Couscous | 809 | 803.9 | 0.6% | 1.34 | 17/50/34 | 1.004 |
| Almond Crusted Chicken Plate / average man, maintaining | matched | Almond Crusted Chicken Plate | 809 | 810.7 | 0.2% | 1.26 | 24/46/30 | 1.064 |
| Cashew Chicken Stir Fry / average man, maintaining | matched | Cashew Chicken Stir Fry | 809 | 808.4 | 0.1% | 1.16 | 28/47/24 | 0.983 |
| Beef Mushroom Rice Bowl / average man, maintaining | matched | Beef Mushroom Rice Bowl | 809 | 800.5 | 1.1% | 1.45 | 18/48/34 | 1.022 |
| Pumpkin Lentil Soup / average man, maintaining | matched | Pumpkin Lentil Soup | 809 | 803.7 | 0.7% | 1.44 | 17/58/26 | 0.989 |
| Salmon Potato Salad / average man, maintaining | matched | Salmon Potato Salad | 809 | 787.5 | 2.7% | 1.12 | 22/19/58 | 1.04 |
| Turkey Zucchini Pasta / average man, maintaining | matched | Turkey Zucchini Pasta | 809 | 797.6 | 1.4% | 1.27 | 19/47/34 | 1.085 |
| Chickpea Hummus Wrap / average man, maintaining | matched | Chickpea Hummus Wrap | 809 | 805.7 | 0.4% | 1.5 | 14/52/34 | 0.859 |
| Tofu Mushroom Noodle Soup / average man, maintaining | matched | Tofu Mushroom Noodle Soup | 809 | 806.2 | 0.3% | 1.36 | 17/60/23 | 0.965 |
| Chicken Pumpkin Soup / average man, maintaining | matched | Chicken Pumpkin Soup | 809 | 836.0 | 3.3% | 1.58 | 22/46/33 | 0.943 |
| Pork Sweet Potato Plate / average man, maintaining | matched | Pork Sweet Potato Plate | 809 | 807.9 | 0.1% | 1.6 | 27/50/23 | 1.101 |
| Cod Fish Tacos / average man, maintaining | matched | Cod Fish Tacos | 809 | 809.8 | 0.1% | 1.2 | 12/40/48 | 0.975 |
| Shrimp Couscous Bowl / average man, maintaining | matched | Shrimp Couscous Bowl | 809 | 803.6 | 0.7% | 1.6 | 30/47/23 | 0.986 |
| Beef Potato Hash / average man, maintaining | matched | Beef Potato Hash | 809 | 809.0 | 0.0% | 0.99 | 19/20/61 | 1.071 |
| Mushroom Egg Toast / average man, maintaining | matched | Mushroom Egg Toast | 809 | 813.4 | 0.5% | 1.6 | 23/46/31 | 0.937 |
| Almond Banana Overnight Oats / average man, maintaining | matched | Almond Banana Overnight Oats | 809 | 868.4 | 7.3% | 1.48 | 13/59/28 | 0.917 |
| Tempeh Taco Bowl / average man, maintaining | matched | Tempeh Taco Bowl | 809 | 790.3 | 2.3% | 1.36 | 18/55/27 | 0.75 |
| Chicken Quinoa Salad / average man, maintaining | matched | Chicken Quinoa Salad | 809 | 809.0 | 0.0% | 1.44 | 26/46/28 | 1.055 |
| Tuna Pasta Salad / average man, maintaining | matched | Tuna Pasta Salad | 809 | 803.2 | 0.7% | 1.4 | 29/46/25 | 1.088 |
| Pork Fried Rice / average man, maintaining | matched | Pork Fried Rice | 809 | 811.2 | 0.3% | 1.35 | 27/48/24 | 1.027 |
| Ginger Cod Rice Bowl / average man, maintaining | matched | Ginger Cod Rice Bowl | 809 | 851.2 | 5.2% | 1.6 | 13/63/24 | 0.872 |
| Edamame Noodle Salad / average man, maintaining | matched | Edamame Noodle Salad | 809 | 812.3 | 0.4% | 1.47 | 15/64/21 | 0.845 |
| Glazed Chicken Thigh Rice Bowl / average man, maintaining | matched | Glazed Chicken Thigh Rice Bowl | 809 | 822.3 | 1.6% | 1.6 | 15/50/35 | 1.133 |
| Lentil Potato Curry / average man, maintaining | matched | Lentil Potato Curry | 809 | 813.2 | 0.5% | 1.45 | 16/50/34 | 0.964 |
| Black Bean Quinoa Salad / average man, maintaining | matched | Black Bean Quinoa Salad | 809 | 791.7 | 2.1% | 1.6 | 14/53/33 | 0.89 |
| Turkey Couscous Meatballs / average man, maintaining | matched | Turkey Couscous Meatballs | 809 | 801.4 | 0.9% | 1.19 | 19/30/51 | 1.071 |
| Steak and Potato Wedges / average man, maintaining | matched | Steak and Potato Wedges | 809 | 789.4 | 2.4% | 1.13 | 27/20/53 | 1.157 |
| Salmon Noodle Bowl / average man, maintaining | matched | Salmon Noodle Bowl | 809 | 747.4 | 7.6% | 1.26 | 23/47/29 | 0.86 |
| Chicken Sweet Potato Tacos / average man, maintaining | matched | Chicken Sweet Potato Tacos | 809 | 812.7 | 0.5% | 1.35 | 21/46/33 | 1.072 |
| Tofu Scramble Toast / average man, maintaining | matched | Tofu Scramble Toast | 809 | 806.5 | 0.3% | 1.52 | 23/53/23 | 1.004 |
| Peanut Butter Banana Toast / average man, maintaining | matched | Peanut Butter Banana Toast | 809 | 786.1 | 2.8% | 1.6 | 17/50/33 | 1.069 |
| Cashew Tofu Curry / average man, maintaining | matched | Cashew Tofu Curry | 809 | 807.2 | 0.2% | 1.4 | 16/58/26 | 0.84 |
| Mediterranean Couscous Salad / average man, maintaining | matched | Mediterranean Couscous Salad | 809 | 812.3 | 0.4% | 1.6 | 14/62/24 | 0.865 |
| Pork Burrito Bowl / average man, maintaining | matched | Pork Burrito Bowl | 809 | 817.0 | 1.0% | 1.55 | 20/60/20 | 0.91 |
| Chicken Hummus Plate / average man, maintaining | matched | Chicken Hummus Plate | 809 | 802.3 | 0.8% | 1.53 | 23/46/31 | 1.036 |
| Shrimp Noodle Stir Fry / average man, maintaining | matched | Shrimp Noodle Stir Fry | 809 | 808.1 | 0.1% | 1.29 | 22/49/29 | 1.007 |
| Potato Zucchini Frittata / average man, maintaining | matched | Potato Zucchini Frittata | 809 | 833.0 | 3.0% | 1.39 | 18/18/64 | 1.044 |
| Mushroom Tempeh Noodles / average man, maintaining | matched | Mushroom Tempeh Noodles | 809 | 823.0 | 1.7% | 1.36 | 20/50/30 | 0.859 |
