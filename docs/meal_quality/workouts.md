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
- Calorie deviation: median 0.6%, 90th percentile 2.5%, max 5.2%.
- Rescaled by reconciliation: 0. First-pass scaling clamped: 35.
- Meal target as a share of the daily budget: 18.8% to 29.2%.
- Daily budget across profiles: 1200.0 to 4521.1 kcal.
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
| chicken fried rice / average man, maintaining / rest day | matched | Chicken Fried Rice | 601 | 603.1 | 0.3% | 0.83 | 27/46/27 | 0.999 |
| high-protein burger / average man, maintaining / rest day | matched | High-Protein Turkey Burger Bowl | 601 | 595.2 | 1.0% | 1.41 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / rest day | matched | Tuna Pasta Salad | 601 | 604.8 | 0.6% | 1.04 | 27/46/27 | 0.612 |
| salmon dinner / average man, maintaining / rest day | matched | Salmon Noodle Bowl | 601 | 602.0 | 0.2% | 0.93 | 21/46/33 | 0.566 |
| steak and rice / average man, maintaining / rest day | matched | Lean Steak Rice Plate | 601 | 602.7 | 0.3% | 1.02 | 24/46/30 | 0.864 |
| spicy curry / average man, maintaining / rest day | matched | Chickpea Curry Bowl | 601 | 594.7 | 1.0% | 1.08 | 15/60/24 | 0.435 |
| chicken fried rice / average man, maintaining / 20 min walk at 95 bpm | matched | Chicken Fried Rice | 619 | 617.7 | 0.2% | 0.85 | 27/46/27 | 0.999 |
| high-protein burger / average man, maintaining / 20 min walk at 95 bpm | matched | High-Protein Turkey Burger Bowl | 619 | 616.5 | 0.4% | 1.46 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 20 min walk at 95 bpm | matched | Tuna Pasta Salad | 619 | 612.3 | 1.1% | 1.07 | 27/46/27 | 0.612 |
| salmon dinner / average man, maintaining / 20 min walk at 95 bpm | matched | Salmon Noodle Bowl | 619 | 630.6 | 1.9% | 0.96 | 21/46/33 | 0.566 |
| steak and rice / average man, maintaining / 20 min walk at 95 bpm | matched | Lean Steak Rice Plate | 619 | 624.4 | 0.9% | 1.05 | 25/46/30 | 0.864 |
| spicy curry / average man, maintaining / 20 min walk at 95 bpm | matched | Chickpea Curry Bowl | 619 | 611.1 | 1.3% | 1.12 | 15/60/24 | 0.435 |
| chicken fried rice / average man, maintaining / 30 min jog at 120 bpm | matched | Chicken Fried Rice | 666 | 662.0 | 0.6% | 0.92 | 28/46/26 | 0.999 |
| high-protein burger / average man, maintaining / 30 min jog at 120 bpm | matched | High-Protein Turkey Burger Bowl | 666 | 660.7 | 0.8% | 1.57 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 30 min jog at 120 bpm | matched | Tuna Pasta Salad | 666 | 671.9 | 0.9% | 1.15 | 29/46/25 | 0.612 |
| salmon dinner / average man, maintaining / 30 min jog at 120 bpm | matched | Salmon Noodle Bowl | 666 | 673.2 | 1.1% | 1.04 | 21/46/33 | 0.566 |
| steak and rice / average man, maintaining / 30 min jog at 120 bpm | matched | Lean Steak Rice Plate | 666 | 666.0 | 0.0% | 1.13 | 25/46/29 | 0.864 |
| spicy curry / average man, maintaining / 30 min jog at 120 bpm | matched | Chickpea Curry Bowl | 666 | 650.8 | 2.3% | 1.2 | 16/61/23 | 0.435 |
| chicken fried rice / average man, maintaining / 60 min run at 140 bpm | matched | Chicken Fried Rice | 735 | 732.8 | 0.3% | 1.01 | 29/46/25 | 0.999 |
| high-protein burger / average man, maintaining / 60 min run at 140 bpm | matched | High-Protein Turkey Burger Bowl | 735 | 736.9 | 0.3% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 60 min run at 140 bpm | matched | Tuna Pasta Salad | 735 | 731.5 | 0.5% | 1.27 | 30/46/24 | 0.612 |
| salmon dinner / average man, maintaining / 60 min run at 140 bpm | matched | Salmon Noodle Bowl | 735 | 724.3 | 1.5% | 1.14 | 22/45/33 | 0.566 |
| steak and rice / average man, maintaining / 60 min run at 140 bpm | matched | Lean Steak Rice Plate | 735 | 737.7 | 0.4% | 1.25 | 26/46/28 | 0.864 |
| spicy curry / average man, maintaining / 60 min run at 140 bpm | matched | Chickpea Curry Bowl | 735 | 751.4 | 2.2% | 1.32 | 15/58/27 | 0.435 |
| chicken fried rice / average man, maintaining / 90 min ride at 135 bpm | matched | Chicken Fried Rice | 802 | 800.5 | 0.2% | 1.1 | 30/46/24 | 0.999 |
| high-protein burger / average man, maintaining / 90 min ride at 135 bpm | matched | High-Protein Turkey Burger Bowl | 802 | 798.4 | 0.4% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / average man, maintaining / 90 min ride at 135 bpm | matched | Tuna Pasta Salad | 802 | 802.3 | 0.0% | 1.39 | 27/46/27 | 0.612 |
| salmon dinner / average man, maintaining / 90 min ride at 135 bpm | matched | Salmon Noodle Bowl | 802 | 788.0 | 1.7% | 1.25 | 21/47/32 | 0.566 |
| steak and rice / average man, maintaining / 90 min ride at 135 bpm | matched | Lean Steak Rice Plate | 802 | 802.8 | 0.1% | 1.36 | 23/46/31 | 0.864 |
| spicy curry / average man, maintaining / 90 min ride at 135 bpm | matched | Chickpea Curry Bowl | 802 | 807.5 | 0.7% | 1.45 | 15/59/26 | 0.435 |
| chicken fried rice / active woman, maintaining / workout not given | matched | Chicken Fried Rice | 691 | 693.6 | 0.4% | 0.95 | 28/46/26 | 0.999 |
| high-protein burger / active woman, maintaining / workout not given | matched | High-Protein Turkey Burger Bowl | 691 | 695.9 | 0.7% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / workout not given | matched | Tuna Pasta Salad | 691 | 700.9 | 1.4% | 1.19 | 29/46/24 | 0.612 |
| salmon dinner / active woman, maintaining / workout not given | matched | Salmon Noodle Bowl | 691 | 683.6 | 1.1% | 1.07 | 21/45/33 | 0.566 |
| steak and rice / active woman, maintaining / workout not given | matched | Lean Steak Rice Plate | 691 | 689.4 | 0.2% | 1.17 | 25/46/29 | 0.864 |
| spicy curry / active woman, maintaining / workout not given | matched | Chickpea Curry Bowl | 691 | 667.3 | 3.4% | 1.25 | 16/61/23 | 0.435 |
| chicken fried rice / active woman, maintaining / rest day | matched | Chicken Fried Rice | 457 | 456.7 | 0.1% | 0.65 | 31/47/23 | 0.999 |
| high-protein burger / active woman, maintaining / rest day | matched | High-Protein Turkey Burger Bowl | 457 | 454.1 | 0.6% | 1.07 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / rest day | matched | Tuna Pasta Salad | 457 | 451.3 | 1.2% | 0.79 | 29/46/25 | 0.612 |
| salmon dinner / active woman, maintaining / rest day | matched | Salmon Noodle Bowl | 457 | 464.6 | 1.7% | 0.71 | 20/47/34 | 0.566 |
| steak and rice / active woman, maintaining / rest day | matched | Lean Steak Rice Plate | 457 | 457.3 | 0.1% | 0.78 | 21/46/32 | 0.864 |
| spicy curry / active woman, maintaining / rest day | matched | Chickpea Curry Bowl | 457 | 474.0 | 3.7% | 0.82 | 15/57/28 | 0.435 |
| chicken fried rice / active woman, maintaining / 20 min walk at 95 bpm | matched | Chicken Fried Rice | 477 | 478.5 | 0.3% | 0.66 | 31/46/23 | 0.999 |
| high-protein burger / active woman, maintaining / 20 min walk at 95 bpm | matched | High-Protein Turkey Burger Bowl | 477 | 476.2 | 0.2% | 1.12 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 20 min walk at 95 bpm | matched | Tuna Pasta Salad | 477 | 481.9 | 1.0% | 0.82 | 30/46/24 | 0.612 |
| salmon dinner / active woman, maintaining / 20 min walk at 95 bpm | matched | Salmon Noodle Bowl | 477 | 476.8 | 0.0% | 0.74 | 20/46/34 | 0.566 |
| steak and rice / active woman, maintaining / 20 min walk at 95 bpm | matched | Lean Steak Rice Plate | 477 | 474.5 | 0.5% | 0.81 | 22/46/32 | 0.864 |
| spicy curry / active woman, maintaining / 20 min walk at 95 bpm | matched | Chickpea Curry Bowl | 477 | 490.4 | 2.8% | 0.86 | 15/58/27 | 0.435 |
| chicken fried rice / active woman, maintaining / 30 min jog at 120 bpm | matched | Chicken Fried Rice | 523 | 517.7 | 1.0% | 0.72 | 32/46/22 | 0.999 |
| high-protein burger / active woman, maintaining / 30 min jog at 120 bpm | matched | High-Protein Turkey Burger Bowl | 523 | 521.3 | 0.3% | 1.23 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 30 min jog at 120 bpm | matched | Tuna Pasta Salad | 523 | 512.5 | 2.0% | 0.9 | 31/46/23 | 0.612 |
| salmon dinner / active woman, maintaining / 30 min jog at 120 bpm | matched | Salmon Noodle Bowl | 523 | 517.6 | 1.0% | 0.81 | 20/46/34 | 0.566 |
| steak and rice / active woman, maintaining / 30 min jog at 120 bpm | matched | Lean Steak Rice Plate | 523 | 529.1 | 1.2% | 0.89 | 23/46/31 | 0.864 |
| spicy curry / active woman, maintaining / 30 min jog at 120 bpm | matched | Chickpea Curry Bowl | 523 | 530.1 | 1.4% | 0.94 | 15/59/26 | 0.435 |
| chicken fried rice / active woman, maintaining / 60 min run at 140 bpm | matched | Chicken Fried Rice | 593 | 594.9 | 0.3% | 0.82 | 27/46/27 | 0.999 |
| high-protein burger / active woman, maintaining / 60 min run at 140 bpm | matched | High-Protein Turkey Burger Bowl | 593 | 594.3 | 0.2% | 1.39 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 60 min run at 140 bpm | matched | Tuna Pasta Salad | 593 | 587.4 | 0.9% | 1.02 | 27/45/28 | 0.612 |
| salmon dinner / active woman, maintaining / 60 min run at 140 bpm | matched | Salmon Noodle Bowl | 593 | 602.0 | 1.5% | 0.92 | 21/46/33 | 0.566 |
| steak and rice / active woman, maintaining / 60 min run at 140 bpm | matched | Lean Steak Rice Plate | 593 | 592.4 | 0.1% | 1.01 | 24/46/30 | 0.864 |
| spicy curry / active woman, maintaining / 60 min run at 140 bpm | matched | Chickpea Curry Bowl | 593 | 586.5 | 1.1% | 1.07 | 15/60/25 | 0.435 |
| chicken fried rice / active woman, maintaining / 90 min ride at 135 bpm | matched | Chicken Fried Rice | 661 | 662.0 | 0.2% | 0.91 | 28/46/26 | 0.999 |
| high-protein burger / active woman, maintaining / 90 min ride at 135 bpm | matched | High-Protein Turkey Burger Bowl | 661 | 660.7 | 0.0% | 1.55 | 31/46/23 | 0.656 |
| creamy pasta / active woman, maintaining / 90 min ride at 135 bpm | matched | Tuna Pasta Salad | 661 | 671.9 | 1.6% | 1.14 | 29/46/25 | 0.612 |
| salmon dinner / active woman, maintaining / 90 min ride at 135 bpm | matched | Salmon Noodle Bowl | 661 | 671.4 | 1.6% | 1.03 | 21/46/33 | 0.566 |
| steak and rice / active woman, maintaining / 90 min ride at 135 bpm | matched | Lean Steak Rice Plate | 661 | 664.2 | 0.5% | 1.12 | 25/46/29 | 0.864 |
| spicy curry / active woman, maintaining / 90 min ride at 135 bpm | matched | Chickpea Curry Bowl | 661 | 650.8 | 1.5% | 1.19 | 16/61/23 | 0.435 |
| chicken fried rice / large athlete, gaining / workout not given | matched | Chicken Fried Rice | 850 | 849.6 | 0.0% | 1.17 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / workout not given | matched | High-Protein Turkey Burger Bowl | 850 | 811.4 | 4.5% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / workout not given | matched | Tuna Pasta Salad | 850 | 844.5 | 0.6% | 1.47 | 28/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / workout not given | matched | Salmon Noodle Bowl | 850 | 828.8 | 2.5% | 1.32 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / workout not given | matched | Lean Steak Rice Plate | 850 | 848.7 | 0.2% | 1.44 | 24/46/30 | 0.864 |
| spicy curry / large athlete, gaining / workout not given | matched | Chickpea Curry Bowl | 850 | 848.7 | 0.2% | 1.53 | 15/59/25 | 0.435 |
| chicken fried rice / large athlete, gaining / rest day | matched | Chicken Fried Rice | 806 | 808.8 | 0.3% | 1.11 | 30/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / rest day | matched | High-Protein Turkey Burger Bowl | 806 | 811.4 | 0.7% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / rest day | matched | Tuna Pasta Salad | 806 | 802.3 | 0.5% | 1.39 | 27/46/27 | 0.612 |
| salmon dinner / large athlete, gaining / rest day | matched | Salmon Noodle Bowl | 806 | 798.4 | 0.9% | 1.25 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / rest day | matched | Lean Steak Rice Plate | 806 | 808.9 | 0.4% | 1.37 | 23/46/31 | 0.864 |
| spicy curry / large athlete, gaining / rest day | matched | Chickpea Curry Bowl | 806 | 807.5 | 0.2% | 1.45 | 15/59/26 | 0.435 |
| chicken fried rice / large athlete, gaining / 20 min walk at 95 bpm | matched | Chicken Fried Rice | 823 | 823.6 | 0.1% | 1.13 | 31/46/24 | 0.999 |
| high-protein burger / large athlete, gaining / 20 min walk at 95 bpm | matched | High-Protein Turkey Burger Bowl | 823 | 811.4 | 1.4% | 1.6 | 31/46/23 | 0.656 |
| creamy pasta / large athlete, gaining / 20 min walk at 95 bpm | matched | Tuna Pasta Salad | 823 | 831.3 | 1.0% | 1.42 | 27/46/26 | 0.612 |
| salmon dinner / large athlete, gaining / 20 min walk at 95 bpm | matched | Salmon Noodle Bowl | 823 | 798.4 | 3.0% | 1.28 | 22/46/32 | 0.566 |
| steak and rice / large athlete, gaining / 20 min walk at 95 bpm | matched | Lean Steak Rice Plate | 823 | 825.2 | 0.3% | 1.4 | 23/46/31 | 0.864 |
| spicy curry / large athlete, gaining / 20 min walk at 95 bpm | matched | Chickpea Curry Bowl | 823 | 824.0 | 0.1% | 1.48 | 15/59/26 | 0.435 |
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

"Activity level counts" is BMR times (multiplier - 1.2): the exercise the activity level holds for an average day. A stated workout replaces it (DEC-40). "Added on top" is the budget the day had before DEC-40, when the workout was always added to the activity level.

Days that still count exercise twice: 3 of 24, all with the workout not given, where the model's default is added to the activity level.

| Profile | Workout | Workout kcal | Activity level counts | Budget | Added on top | Meets targets |
|---|---|---:|---:|---:|---:|---:|
| older sedentary woman, losing (x1.2) | workout not given | 142 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | rest day | 0 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | 20 min walk at 95 bpm | 82 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | 30 min jog at 120 bpm | 246 | 0 | 1200 | 1200 | 6 of 6 |
| older sedentary woman, losing (x1.2) | 60 min run at 140 bpm | 505 | 0 | 1349 | 1349 | 5 of 6 |
| older sedentary woman, losing (x1.2) | 90 min ride at 135 bpm | 757 | 0 | 1601 | 1601 | 6 of 6 |
| average man, maintaining (x1.55) | workout not given | 115 | 626 | 2889 | 2889 | 6 of 6 |
| average man, maintaining (x1.55) | rest day | 0 | 626 | 2148 | 2774 | 6 of 6 |
| average man, maintaining (x1.55) | 20 min walk at 95 bpm | 63 | 626 | 2211 | 2838 | 6 of 6 |
| average man, maintaining (x1.55) | 30 min jog at 120 bpm | 230 | 626 | 2378 | 3005 | 6 of 6 |
| average man, maintaining (x1.55) | 60 min run at 140 bpm | 477 | 626 | 2625 | 3251 | 6 of 6 |
| average man, maintaining (x1.55) | 90 min ride at 135 bpm | 715 | 626 | 2863 | 3490 | 6 of 6 |
| active woman, maintaining (x1.725) | workout not given | 125 | 714 | 2469 | 2469 | 6 of 6 |
| active woman, maintaining (x1.725) | rest day | 0 | 714 | 1631 | 2344 | 6 of 6 |
| active woman, maintaining (x1.725) | 20 min walk at 95 bpm | 72 | 714 | 1703 | 2416 | 6 of 6 |
| active woman, maintaining (x1.725) | 30 min jog at 120 bpm | 236 | 714 | 1867 | 2580 | 6 of 6 |
| active woman, maintaining (x1.725) | 60 min run at 140 bpm | 487 | 714 | 2118 | 2832 | 6 of 6 |
| active woman, maintaining (x1.725) | 90 min ride at 135 bpm | 731 | 714 | 2362 | 3075 | 6 of 6 |
| large athlete, gaining (x1.9) | workout not given | 108 | 1534 | 4521 | 4521 | 6 of 6 |
| large athlete, gaining (x1.9) | rest day | 0 | 1534 | 2880 | 4413 | 6 of 6 |
| large athlete, gaining (x1.9) | 20 min walk at 95 bpm | 60 | 1534 | 2940 | 4474 | 6 of 6 |
| large athlete, gaining (x1.9) | 30 min jog at 120 bpm | 223 | 1534 | 3103 | 4637 | 6 of 6 |
| large athlete, gaining (x1.9) | 60 min run at 140 bpm | 454 | 1534 | 3333 | 4867 | 6 of 6 |
| large athlete, gaining (x1.9) | 90 min ride at 135 bpm | 681 | 1534 | 3560 | 5094 | 6 of 6 |

Model-range warnings these days raised:

- Heart rates above 128 bpm are estimated as 128 bpm, so a harder workout may be undercounted.
- Workouts over 30 minutes are estimated at the 30-minute rate per minute, beyond the model's training range.
