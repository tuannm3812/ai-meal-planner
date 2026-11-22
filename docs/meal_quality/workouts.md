## Measured

- calorie_model_version: `hist_gradient_boosting_deep_v0.1.0`
- calorie_model_sha256: `33a154b3d5807af1e2dd53ee69dc250e3f9a4429bfed90260e27671eac168c95`
- meal_corpus_sha256: `cebde36f88214e2bb08e21243f64c99046e13c131ea038931209dc2d4423b33c`
- meal_count: `76`
- retriever: `tfidf_vector_retriever_v0.1`

## Summary

- Plans: 144 (matched 144).
- **Meeting the targets** (calories within 10%, all macros in AMDR): 143 of 144.
- Within the 10% calorie target: 144 of 144 scaled plans.
- Within the service's 15% retry tolerance: 144 of 144 scaled plans.
- Calorie deviation: median 0.5%, 90th percentile 3.7%, max 5.2%.
- Rescaled by reconciliation: 0. First-pass scaling clamped: 40.
- Meal target as a share of the daily budget: 16.7% to 29.2%.
- Daily budget across profiles: 1200.0 to 5094.1 kcal.
- Macro share inside AMDR: protein 144, carbs 143, fat 144; all three 143 of 144.
- Plans with at least one estimated ingredient: 144 of 144.
- Corpus matches scoring below 0.25: 0.

## Plans

| Scenario | Status | Meal | Target | Verified | Dev. | Scale | P/C/F % | Score |
|---|---|---|---:|---:|---:|---:|---|---:|
| chicken fried rice / older sedentary woman, losing / workout not given | matched | Chicken Fried Rice | 350 | 363.4 | 3.8% | 0.65 | 29/46/26 | 0.999 |
| high-protein burger / older sedentary woman, losing / workout not given | matched | High-Protein Turkey Burger Bowl | 350 | 351.7 | 0.5% | 0.82 | 31/46/23 | 0.656 |
| creamy pasta / older sedentary woman, losing / workout not given | matched | Tuna Pasta Salad | 350 | 351.0 | 0.3% | 0.65 | 24/46/30 | 0.612 |
| salmon dinner / older sedentary woman, losing / workout not given | matched | Salmon Noodle Bowl | 350 | 345.9 | 1.2% | 0.65 | 18/48/34 | 0.566 |
| steak and rice / older sedentary woman, losing / workout not given | matched | Lean Steak Rice Plate | 350 | 349.0 | 0.3% | 0.65 | 26/46/28 | 0.864 |
| spicy curry / older sedentary woman, losing / workout not given | matched | Chickpea Curry Bowl | 350 | 348.9 | 0.3% | 0.65 | 16/62/23 | 0.435 |
| chicken fried rice / older sedentary woman, losing / rest day | matched | Chicken Fried Rice | 350 | 363.4 | 3.8% | 0.65 | 29/46/26 | 0.999 |
| high-protein burger / older sedentary woman, losing / rest day | matched | High-Protein Turkey Burger Bowl | 350 | 351.7 | 0.5% | 0.82 | 31/46/23 | 0.656 |
| creamy pasta / older sedentary woman, losing / rest day | matched | Tuna Pasta Salad | 350 | 351.0 | 0.3% | 0.65 | 24/46/30 | 0.612 |
| salmon dinner / older sedentary woman, losing / rest day | matched | Salmon Noodle Bowl | 350 | 345.9 | 1.2% | 0.65 | 18/48/34 | 0.566 |
| steak and rice / older sedentary woman, losing / rest day | matched | Lean Steak Rice Plate | 350 | 349.0 | 0.3% | 0.65 | 26/46/28 | 0.864 |
| spicy curry / older sedentary woman, losing / rest day | matched | Chickpea Curry Bowl | 350 | 348.9 | 0.3% | 0.65 | 16/62/23 | 0.435 |
| chicken fried rice / older sedentary woman, losing / 20 min walk at 95 bpm | matched | Chicken Fried Rice | 350 | 363.4 | 3.8% | 0.65 | 29/46/26 | 0.999 |
| high-protein burger / older sedentary woman, losing / 20 min walk at 95 bpm | matched | High-Protein Turkey Burger Bowl | 350 | 351.7 | 0.5% | 0.82 | 31/46/23 | 0.656 |
| creamy pasta / older sedentary woman, losing / 20 min walk at 95 bpm | matched | Tuna Pasta Salad | 350 | 351.0 | 0.3% | 0.65 | 24/46/30 | 0.612 |
| salmon dinner / older sedentary woman, losing / 20 min walk at 95 bpm | matched | Salmon Noodle Bowl | 350 | 345.9 | 1.2% | 0.65 | 18/48/34 | 0.566 |
| steak and rice / older sedentary woman, losing / 20 min walk at 95 bpm | matched | Lean Steak Rice Plate | 350 | 349.0 | 0.3% | 0.65 | 26/46/28 | 0.864 |
| spicy curry / older sedentary woman, losing / 20 min walk at 95 bpm | matched | Chickpea Curry Bowl | 350 | 348.9 | 0.3% | 0.65 | 16/62/23 | 0.435 |
| chicken fried rice / older sedentary woman, losing / 30 min jog at 120 bpm | matched | Chicken Fried Rice | 350 | 363.4 | 3.8% | 0.65 | 29/46/26 | 0.999 |
| high-protein burger / older sedentary woman, losing / 30 min jog at 120 bpm | matched | High-Protein Turkey Burger Bowl | 350 | 351.7 | 0.5% | 0.82 | 31/46/23 | 0.656 |
| creamy pasta / older sedentary woman, losing / 30 min jog at 120 bpm | matched | Tuna Pasta Salad | 350 | 351.0 | 0.3% | 0.65 | 24/46/30 | 0.612 |
| salmon dinner / older sedentary woman, losing / 30 min jog at 120 bpm | matched | Salmon Noodle Bowl | 350 | 345.9 | 1.2% | 0.65 | 18/48/34 | 0.566 |
| steak and rice / older sedentary woman, losing / 30 min jog at 120 bpm | matched | Lean Steak Rice Plate | 350 | 349.0 | 0.3% | 0.65 | 26/46/28 | 0.864 |
| spicy curry / older sedentary woman, losing / 30 min jog at 120 bpm | matched | Chickpea Curry Bowl | 350 | 348.9 | 0.3% | 0.65 | 16/62/23 | 0.435 |
| chicken fried rice / older sedentary woman, losing / 60 min run at 140 bpm | matched | Chicken Fried Rice | 378 | 376.4 | 0.4% | 0.65 | 28/47/25 | 0.999 |
| high-protein burger / older sedentary woman, losing / 60 min run at 140 bpm | matched | High-Protein Turkey Burger Bowl | 378 | 374.6 | 0.9% | 0.89 | 31/46/23 | 0.656 |
| creamy pasta / older sedentary woman, losing / 60 min run at 140 bpm | matched | Tuna Pasta Salad | 378 | 385.8 | 2.1% | 0.65 | 30/43/28 | 0.612 |
| salmon dinner / older sedentary woman, losing / 60 min run at 140 bpm | matched | Salmon Noodle Bowl | 378 | 384.9 | 1.8% | 0.65 | 19/48/34 | 0.566 |
| steak and rice / older sedentary woman, losing / 60 min run at 140 bpm | matched | Lean Steak Rice Plate | 378 | 375.9 | 0.6% | 0.65 | 26/46/28 | 0.864 |
| spicy curry / older sedentary woman, losing / 60 min run at 140 bpm | matched | Chickpea Curry Bowl | 378 | 358.3 | 5.2% | 0.68 | 16/62/22 | 0.435 |
| chicken fried rice / older sedentary woman, losing / 90 min ride at 135 bpm | matched | Chicken Fried Rice | 448 | 450.2 | 0.5% | 0.65 | 31/46/23 | 0.999 |
| high-protein burger / older sedentary woman, losing / 90 min ride at 135 bpm | matched | High-Protein Turkey Burger Bowl | 448 | 454.1 | 1.4% | 1.05 | 31/46/23 | 0.656 |
| creamy pasta / older sedentary woman, losing / 90 min ride at 135 bpm | matched | Tuna Pasta Salad | 448 | 451.3 | 0.7% | 0.77 | 29/46/25 | 0.612 |
| salmon dinner / older sedentary woman, losing / 90 min ride at 135 bpm | matched | Salmon Noodle Bowl | 448 | 436.0 | 2.7% | 0.7 | 20/46/34 | 0.566 |
| steak and rice / older sedentary woman, losing / 90 min ride at 135 bpm | matched | Lean Steak Rice Plate | 448 | 449.4 | 0.3% | 0.76 | 21/46/33 | 0.864 |
| spicy curry / older sedentary woman, losing / 90 min ride at 135 bpm | matched | Chickpea Curry Bowl | 448 | 458.7 | 2.4% | 0.81 | 15/57/28 | 0.435 |
| chicken fried rice / average man, maintaining / workout not given | matched | Chicken Fried Rice | 809 | 808.8 | 0.0% | 1.11 | 30/46/24 | 0.999 |
| high-protein burger / average man, maintaining / workout not given | matched | High-Protein Turkey Burger Bowl | 809 | 811.4 | 0.3% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / workout not given | matched | Tuna Pasta Salad | 809 | 808.1 | 0.1% | 1.4 | 27/46/27 | 0.612 |
| salmon dinner / average man, maintaining / workout not given | matched | Salmon Noodle Bowl | 809 | 798.4 | 1.3% | 1.26 | 22/46/32 | 0.566 |
| steak and rice / average man, maintaining / workout not given | matched | Lean Steak Rice Plate | 809 | 808.9 | 0.0% | 1.37 | 23/46/31 | 0.864 |
| spicy curry / average man, maintaining / workout not given | matched | Chickpea Curry Bowl | 809 | 815.7 | 0.8% | 1.46 | 15/59/26 | 0.435 |
| chicken fried rice / average man, maintaining / rest day | matched | Chicken Fried Rice | 777 | 776.0 | 0.1% | 1.07 | 30/46/24 | 0.999 |
| high-protein burger / average man, maintaining / rest day | matched | High-Protein Turkey Burger Bowl | 777 | 777.9 | 0.1% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / rest day | matched | Tuna Pasta Salad | 777 | 762.2 | 1.9% | 1.34 | 31/47/23 | 0.612 |
| salmon dinner / average man, maintaining / rest day | matched | Salmon Noodle Bowl | 777 | 757.6 | 2.5% | 1.21 | 21/46/33 | 0.566 |
| steak and rice / average man, maintaining / rest day | matched | Lean Steak Rice Plate | 777 | 779.4 | 0.3% | 1.32 | 23/46/31 | 0.864 |
| spicy curry / average man, maintaining / rest day | matched | Chickpea Curry Bowl | 777 | 791.2 | 1.8% | 1.4 | 15/59/26 | 0.435 |
| chicken fried rice / average man, maintaining / 20 min walk at 95 bpm | matched | Chicken Fried Rice | 795 | 797.2 | 0.3% | 1.1 | 30/46/24 | 0.999 |
| high-protein burger / average man, maintaining / 20 min walk at 95 bpm | matched | High-Protein Turkey Burger Bowl | 795 | 798.4 | 0.4% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 20 min walk at 95 bpm | matched | Tuna Pasta Salad | 795 | 800.6 | 0.7% | 1.37 | 27/46/27 | 0.612 |
| salmon dinner / average man, maintaining / 20 min walk at 95 bpm | matched | Salmon Noodle Bowl | 795 | 788.0 | 0.9% | 1.24 | 21/47/32 | 0.566 |
| steak and rice / average man, maintaining / 20 min walk at 95 bpm | matched | Lean Steak Rice Plate | 795 | 794.3 | 0.1% | 1.35 | 23/46/31 | 0.864 |
| spicy curry / average man, maintaining / 20 min walk at 95 bpm | matched | Chickpea Curry Bowl | 795 | 800.5 | 0.7% | 1.43 | 15/59/26 | 0.435 |
| chicken fried rice / average man, maintaining / 30 min jog at 120 bpm | matched | Chicken Fried Rice | 841 | 840.4 | 0.1% | 1.16 | 30/46/24 | 0.999 |
| high-protein burger / average man, maintaining / 30 min jog at 120 bpm | matched | High-Protein Turkey Burger Bowl | 841 | 811.4 | 3.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 30 min jog at 120 bpm | matched | Tuna Pasta Salad | 841 | 837.1 | 0.5% | 1.45 | 28/46/26 | 0.612 |
| salmon dinner / average man, maintaining / 30 min jog at 120 bpm | matched | Salmon Noodle Bowl | 841 | 828.8 | 1.5% | 1.31 | 22/46/32 | 0.566 |
| steak and rice / average man, maintaining / 30 min jog at 120 bpm | matched | Lean Steak Rice Plate | 841 | 842.6 | 0.2% | 1.43 | 24/46/30 | 0.864 |
| spicy curry / average man, maintaining / 30 min jog at 120 bpm | matched | Chickpea Curry Bowl | 841 | 840.4 | 0.1% | 1.52 | 15/59/25 | 0.435 |
| chicken fried rice / average man, maintaining / 60 min run at 140 bpm | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / average man, maintaining / 60 min run at 140 bpm | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 60 min run at 140 bpm | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / average man, maintaining / 60 min run at 140 bpm | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / average man, maintaining / 60 min run at 140 bpm | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / average man, maintaining / 60 min run at 140 bpm | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / average man, maintaining / 90 min ride at 135 bpm | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / average man, maintaining / 90 min ride at 135 bpm | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 90 min ride at 135 bpm | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / average man, maintaining / 90 min ride at 135 bpm | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / average man, maintaining / 90 min ride at 135 bpm | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / average man, maintaining / 90 min ride at 135 bpm | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / active woman, maintaining / workout not given | matched | Chicken Fried Rice | 691 | 693.6 | 0.4% | 0.95 | 28/46/26 | 0.999 |
| high-protein burger / active woman, maintaining / workout not given | matched | High-Protein Turkey Burger Bowl | 691 | 695.9 | 0.7% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / workout not given | matched | Tuna Pasta Salad | 691 | 700.9 | 1.4% | 1.19 | 29/46/24 | 0.612 |
| salmon dinner / active woman, maintaining / workout not given | matched | Salmon Noodle Bowl | 691 | 683.6 | 1.1% | 1.07 | 21/45/33 | 0.566 |
| steak and rice / active woman, maintaining / workout not given | matched | Lean Steak Rice Plate | 691 | 689.4 | 0.2% | 1.17 | 25/46/29 | 0.864 |
| spicy curry / active woman, maintaining / workout not given | matched | Chickpea Curry Bowl | 691 | 667.3 | 3.4% | 1.25 | 16/61/23 | 0.435 |
| chicken fried rice / active woman, maintaining / rest day | matched | Chicken Fried Rice | 656 | 662.0 | 0.9% | 0.9 | 28/46/26 | 0.999 |
| high-protein burger / active woman, maintaining / rest day | matched | High-Protein Turkey Burger Bowl | 656 | 653.2 | 0.4% | 1.54 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / rest day | matched | Tuna Pasta Salad | 656 | 648.7 | 1.1% | 1.13 | 29/46/26 | 0.612 |
| salmon dinner / active woman, maintaining / rest day | matched | Salmon Noodle Bowl | 656 | 661.0 | 0.8% | 1.02 | 21/47/32 | 0.566 |
| steak and rice / active woman, maintaining / rest day | matched | Lean Steak Rice Plate | 656 | 658.0 | 0.3% | 1.11 | 25/46/29 | 0.864 |
| spicy curry / active woman, maintaining / rest day | matched | Chickpea Curry Bowl | 656 | 635.6 | 3.1% | 1.18 | 16/61/24 | 0.435 |
| chicken fried rice / active woman, maintaining / 20 min walk at 95 bpm | matched | Chicken Fried Rice | 676 | 676.7 | 0.1% | 0.93 | 29/46/26 | 0.999 |
| high-protein burger / active woman, maintaining / 20 min walk at 95 bpm | matched | High-Protein Turkey Burger Bowl | 676 | 674.5 | 0.2% | 1.59 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 20 min walk at 95 bpm | matched | Tuna Pasta Salad | 676 | 677.7 | 0.3% | 1.17 | 29/46/25 | 0.612 |
| salmon dinner / active woman, maintaining / 20 min walk at 95 bpm | matched | Salmon Noodle Bowl | 676 | 673.2 | 0.4% | 1.05 | 21/46/33 | 0.566 |
| steak and rice / active woman, maintaining / 20 min walk at 95 bpm | matched | Lean Steak Rice Plate | 676 | 680.6 | 0.7% | 1.15 | 25/46/29 | 0.864 |
| spicy curry / active woman, maintaining / 20 min walk at 95 bpm | matched | Chickpea Curry Bowl | 676 | 650.8 | 3.7% | 1.22 | 16/61/23 | 0.435 |
| chicken fried rice / active woman, maintaining / 30 min jog at 120 bpm | matched | Chicken Fried Rice | 722 | 726.3 | 0.6% | 0.99 | 29/46/25 | 0.999 |
| high-protein burger / active woman, maintaining / 30 min jog at 120 bpm | matched | High-Protein Turkey Burger Bowl | 722 | 716.4 | 0.8% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 30 min jog at 120 bpm | matched | Tuna Pasta Salad | 722 | 714.1 | 1.1% | 1.25 | 30/46/24 | 0.612 |
| salmon dinner / active woman, maintaining / 30 min jog at 120 bpm | matched | Salmon Noodle Bowl | 722 | 713.9 | 1.1% | 1.12 | 21/46/33 | 0.566 |
| steak and rice / active woman, maintaining / 30 min jog at 120 bpm | matched | Lean Steak Rice Plate | 722 | 721.3 | 0.1% | 1.23 | 26/46/28 | 0.864 |
| spicy curry / active woman, maintaining / 30 min jog at 120 bpm | matched | Chickpea Curry Bowl | 722 | 736.2 | 2.0% | 1.3 | 15/58/27 | 0.435 |
| chicken fried rice / active woman, maintaining / 60 min run at 140 bpm | matched | Chicken Fried Rice | 793 | 790.7 | 0.3% | 1.09 | 30/46/24 | 0.999 |
| high-protein burger / active woman, maintaining / 60 min run at 140 bpm | matched | High-Protein Turkey Burger Bowl | 793 | 790.9 | 0.3% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 60 min run at 140 bpm | matched | Tuna Pasta Salad | 793 | 794.8 | 0.2% | 1.37 | 26/46/27 | 0.612 |
| salmon dinner / active woman, maintaining / 60 min run at 140 bpm | matched | Salmon Noodle Bowl | 793 | 788.0 | 0.6% | 1.23 | 21/47/32 | 0.566 |
| steak and rice / active woman, maintaining / 60 min run at 140 bpm | matched | Lean Steak Rice Plate | 793 | 788.1 | 0.6% | 1.35 | 23/46/31 | 0.864 |
| spicy curry / active woman, maintaining / 60 min run at 140 bpm | matched | Chickpea Curry Bowl | 793 | 800.5 | 0.9% | 1.43 | 15/59/26 | 0.435 |
| chicken fried rice / active woman, maintaining / 90 min ride at 135 bpm | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / active woman, maintaining / 90 min ride at 135 bpm | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 90 min ride at 135 bpm | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / active woman, maintaining / 90 min ride at 135 bpm | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / active woman, maintaining / 90 min ride at 135 bpm | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / active woman, maintaining / 90 min ride at 135 bpm | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / large athlete, gaining / workout not given | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / workout not given | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / workout not given | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / workout not given | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / workout not given | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / large athlete, gaining / workout not given | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / large athlete, gaining / rest day | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / rest day | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / rest day | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / rest day | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / rest day | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / large athlete, gaining / rest day | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / large athlete, gaining / 20 min walk at 95 bpm | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / 20 min walk at 95 bpm | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / 20 min walk at 95 bpm | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / 20 min walk at 95 bpm | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / 20 min walk at 95 bpm | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / large athlete, gaining / 20 min walk at 95 bpm | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / large athlete, gaining / 30 min jog at 120 bpm | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / 30 min jog at 120 bpm | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / 30 min jog at 120 bpm | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / 30 min jog at 120 bpm | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / 30 min jog at 120 bpm | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / large athlete, gaining / 30 min jog at 120 bpm | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / large athlete, gaining / 60 min run at 140 bpm | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / 60 min run at 140 bpm | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / 60 min run at 140 bpm | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / 60 min run at 140 bpm | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / 60 min run at 140 bpm | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / large athlete, gaining / 60 min run at 140 bpm | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / large athlete, gaining / 90 min ride at 135 bpm | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / 90 min ride at 135 bpm | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / 90 min ride at 135 bpm | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / 90 min ride at 135 bpm | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / 90 min ride at 135 bpm | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / large athlete, gaining / 90 min ride at 135 bpm | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |

## Workout days

6 workouts for each of the 4 profiles, on 6 matched cravings each. **Meeting the targets: 143 of 144.**

"Activity level counts" is BMR times (multiplier - 1.2): the exercise the activity level already holds for an average day. The service adds today's workout on top of it. "If replaced" is the budget when today's workout replaces that exercise instead.

On 15 of the 24 days, both a workout and an activity level above sedentary count exercise.

| Profile | Workout | Workout kcal | Activity level counts | Budget | If replaced | Meets targets |
|---|---|---:|---:|---:|---:|---:|
| older sedentary woman, losing (x1.2) | workout not given | 142 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | rest day | 0 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | 20 min walk at 95 bpm | 82 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | 30 min jog at 120 bpm | 246 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | 60 min run at 140 bpm | 505 | 0 | 1349 | 1349 | 5 of 6 |
| older sedentary woman, losing (x1.2) | 90 min ride at 135 bpm | 757 | 0 | 1601 | 1601 | 6 of 6 |
| average man, maintaining (x1.55) | workout not given | 115 | 626 | 2889 | 2263 | 6 of 6 |
| average man, maintaining (x1.55) | rest day | 0 | 626 | 2774 | 2148 | 6 of 6 |
| average man, maintaining (x1.55) | 20 min walk at 95 bpm | 63 | 626 | 2838 | 2211 | 6 of 6 |
| average man, maintaining (x1.55) | 30 min jog at 120 bpm | 230 | 626 | 3005 | 2378 | 6 of 6 |
| average man, maintaining (x1.55) | 60 min run at 140 bpm | 477 | 626 | 3251 | 2625 | 6 of 6 |
| average man, maintaining (x1.55) | 90 min ride at 135 bpm | 715 | 626 | 3490 | 2863 | 6 of 6 |
| active woman, maintaining (x1.725) | workout not given | 125 | 714 | 2469 | 1756 | 6 of 6 |
| active woman, maintaining (x1.725) | rest day | 0 | 714 | 2344 | 1631 | 6 of 6 |
| active woman, maintaining (x1.725) | 20 min walk at 95 bpm | 72 | 714 | 2416 | 1703 | 6 of 6 |
| active woman, maintaining (x1.725) | 30 min jog at 120 bpm | 236 | 714 | 2580 | 1867 | 6 of 6 |
| active woman, maintaining (x1.725) | 60 min run at 140 bpm | 487 | 714 | 2832 | 2118 | 6 of 6 |
| active woman, maintaining (x1.725) | 90 min ride at 135 bpm | 731 | 714 | 3075 | 2362 | 6 of 6 |
| large athlete, gaining (x1.9) | workout not given | 108 | 1534 | 4521 | 2987 | 6 of 6 |
| large athlete, gaining (x1.9) | rest day | 0 | 1534 | 4413 | 2880 | 6 of 6 |
| large athlete, gaining (x1.9) | 20 min walk at 95 bpm | 60 | 1534 | 4474 | 2940 | 6 of 6 |
| large athlete, gaining (x1.9) | 30 min jog at 120 bpm | 223 | 1534 | 4636 | 3103 | 6 of 6 |
| large athlete, gaining (x1.9) | 60 min run at 140 bpm | 454 | 1534 | 4867 | 3333 | 6 of 6 |
| large athlete, gaining (x1.9) | 90 min ride at 135 bpm | 681 | 1534 | 5094 | 3560 | 6 of 6 |

Model-range warnings these days raised:

- Heart rates above 128 bpm are estimated as 128 bpm, so a harder workout may be undercounted.
- Workouts over 30 minutes are estimated at the 30-minute rate per minute, beyond the model's training range.
