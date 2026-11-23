# USDA ingredient match diagnosis (P4)

Run on 2026-11-23 against USDA FoodData Central `foods/search`. The script sent the same request as
`NutritionVerificationAgent._query_usda_database` (`query`, `pageSize=1`, no `dataType`
filter) for every distinct ingredient in `data/meal_corpus/meals.json`. It used the agent's own
`_normalize_search_name`, `_nutrient_value` and `_has_usable_macros`. USDA is live data, so a
later run can return different top hits.

60 distinct ingredients. 19 hit the trusted local override and are never looked up, so they are
skipped: banana, black beans, chia seeds, chickpeas, coconut aminos, cooked quinoa, corn tortilla, cucumber, kidney beans, lentils, mixed vegetables, oat milk, olive oil, peanut butter, rolled oats, sesame oil, soy milk, sweet potato, whole egg. The other 41 were looked up.

The kJ bug (finding 1) was fixed in 3185f99. The tables below show what the agent read before
that fix. The runs after the fix are `usda_baseline.md` and `usda_wider.md`; the
`*_before_kcal_fix` files are the earlier runs.

## Findings

1. **kJ is read as kcal (a parser bug).** `_query_usda_database` keys nutrients by
   `nutrientName`. SR Legacy and some Foundation foods list two entries both named `Energy`, one
   in kJ and one in KCAL. The second entry overwrites the first in the dict, so when the kJ entry
   comes last the agent takes kJ as kcal (×4.18). The search hit this for shrimp
   (356 for 85 kcal), tuna (376 for 90) and low-sodium chicken broth (67 for 16). The unit is
   never checked.
2. **The top hit is often the wrong food.** With `pageSize=1` and no filter, the top hit can be a
   different food: avocado → *Avocado dressing* (427 kcal, 43 g fat); lean turkey mince →
   *Ham, minced* (21 g fat); potato → *Potato patty*; red capsicum → *Sangria, red*; cod fillet
   → a branded, apparently breaded cod (153 kcal, 12 g carbs); chicken thigh → a skin-on branded
   thigh. Others return the wrong state of the food: brown rice → dry branded rice
   (349 kcal, where the recipe means cooked, 123 kcal); wholemeal pasta → cooked pasta
   (157 kcal, where the local table holds dry, 348 kcal).
3. **"No usable match" is almost all tomato.** Only one of the 41 names is unusable: `tomato`
   returns a branded *TOMATO* item with no nutrients. Unusable results are not cached, so the
   benchmark looks tomato up again each time a plan needs it. That accounts for the reported 84
   (baseline) and 102 (wider) counts, at about two lookups per plan. The plans reported with an
   estimated ingredient, 41 of 72 and 52 of 152, are exactly the plans whose meal contains tomato. Every other name is
   accepted, including the wrong foods above, because `_has_usable_macros` only asks that one
   value be above 0.
4. **A `dataType=Foundation,SR Legacy` filter is worse.** For the problem ingredients the filtered
   top hit is usually further off: avocado → *Oil, avocado* (884 kcal); cod fillet →
   *Fish oil, cod liver*; tomato → *Tomato powder*; potato → *Bread, potato*;
   red capsicum → *cayenne pepper*; brown rice → *puffed*. SR Legacy also has the duplicate
   `Energy` entries, so the kJ bug fires more often (cooked white rice and chicken thigh too).
   A filter alone does not fix matching.

## The four meals that miss worst

| Meal | Ingredients (g) | What drives the miss |
|---|---|---|
| Shrimp Taco Bowl (+55–104% kcal) | shrimp 160, brown rice 120, salad greens 90, tomato 90, avocado 60 | Shrimp read in kJ (356 for 85 kcal per 100 g): about +430 kcal. Brown rice matched dry (349 for 123): about +270. Avocado matched dressing (427 for 160): about +160. |
| Tuna Brown Rice Bowl (+58–82% kcal) | tuna 140, brown rice 120, salad greens 100, avocado 60, tomato 80 | Tuna read in kJ (376 for 90 actual, 116 local): about +365 kcal. Brown rice matched dry, plus avocado dressing. |
| Tuna Sushi Bowl (+16–31% kcal; carbs low, fat high) | tuna 140, cooked white rice 170, cucumber 80, avocado 60, soy sauce 15 | Tuna kJ bug. Avocado dressing adds about 26 g fat. White rice matched glutinous (96 for 130). |
| High-Protein Turkey Burger Bowl (fat 53%, carbs 24%) | lean turkey mince 160, wholemeal bun 60, salad greens 100, tomato 80 | Lean turkey mince matched *Ham, minced* (20.7 g fat for 7 g per 100 g): about +22 g fat. Calories still land on target, but fat pushes carbs out of range. |

Macro shares stay plausible in the bowls with the kJ bug because only the energy value is
wrong; the protein, carbs and fat grams are right.

## Every looked-up ingredient

Values are kcal / protein / carbs / fat per 100 g. *Picked* is the energy unit the agent's parser
used. *Local* is what the offline run uses (`_estimate_macros_per_100g`).

| Ingredient | Search name | USDA top hit | Type | Agent reads | Picked | KCAL entry | Usable | Local |
|---|---|---|---|---|---|---:|---|---|
| almonds | almonds | ALMONDS | Branded | 633 / 23.3 / 13.3 / 56.7 | KCAL | 633 | yes | 579 / 21.2 / 21.6 / 49.9 |
| avocado | avocado | Avocado dressing | Survey (FNDDS) | 427 / 1.9 / 7.4 / 43.3 | KCAL | 427 | yes | 160 / 2 / 8.5 / 14.7 |
| baby spinach | baby spinach | BABY SPINACH | Branded | 25 / 2.8 / 3.5 / 0.3 | KCAL | 25.0 | yes | 23 / 2.9 / 3.6 / 0.4 |
| broccoli | broccoli | BROCCOLI | Branded | 24 / 2.4 / 4.7 / 0.0 | KCAL | 24.0 | yes | 35 / 2.4 / 7.2 / 0.4 |
| brown rice | brown rice | BROWN RICE | Branded | 349 / 9.3 / 76.7 / 2.3 | KCAL | 349 | yes | 123 / 2.7 / 25.6 / 1 |
| carrot | carrot | Carrots, raw | Survey (FNDDS) | 44 / 0.9 / 9.7 / 0.2 | KCAL | 44 | yes | 41 / 0.9 / 9.6 / 0.2 |
| cashews | cashews | CASHEWS | Branded | 571 / 17.9 / 28.6 / 46.4 | KCAL | 571 | yes | 553 / 18.2 / 30.2 / 43.9 |
| chicken breast | chicken breast raw skinless boneless | Chicken, breast, boneless, skinless, raw | Foundation | 106 / 22.5 / 0.0 / 1.9 | KCAL | 106 | yes | 165 / 31 / 0 / 3.6 |
| chicken thigh | chicken thigh | CHICKEN THIGH | Branded | 193 / 14.0 / 0.9 / 16.7 | KCAL | 193 | yes | 121 / 19.9 / 0.0 / 4.1 |
| cod fillet | cod fillet | COD FILLET | Branded | 153 / 8.2 / 12.2 / 7.1 | KCAL | 153 | yes | 82 / 17.8 / 0.0 / 0.7 |
| cooked couscous | cooked couscous | Couscous, cooked | SR Legacy | 112 / 3.8 / 23.2 / 0.2 | KCAL | 112 | yes | 112 / 3.8 / 23.2 / 0.2 |
| cooked white rice | white rice cooked | Rice, white, cooked, glutinous | Survey (FNDDS) | 96 / 2.0 / 21.0 / 0.2 | KCAL | 96 | yes | 130 / 2.7 / 28.2 / 0.3 |
| cottage cheese | cottage cheese | COTTAGE CHEESE | Branded | 62 / 10.6 / 3.5 / 0.0 | KCAL | 62.0 | yes | 98 / 11.1 / 3.4 / 4.3 |
| edamame | edamame | EDAMAME | Branded | 106 / 11.8 / 7.1 / 4.7 | KCAL | 106 | yes | 121 / 11.9 / 8.9 / 5.2 |
| firm tofu | firm tofu | FIRM TOFU | Branded | 89 / 8.9 / 2.5 / 3.8 | KCAL | 89.0 | yes | 144 / 17 / 3 / 9 |
| greek yogurt | greek yogurt plain nonfat | Yogurt, Greek, plain, nonfat | Foundation | 61 / 10.3 / 3.6 / 0.4 | KCAL | 61.0 | yes | 59 / 10.3 / 3.6 / 0.4 |
| hummus | hummus | HUMMUS | Branded | 321 / 7.1 / 21.4 / 28.6 | KCAL | 321 | yes | 166 / 7.9 / 14.3 / 9.6 |
| lean beef mince | ground beef lean raw | Beef, ground, raw | Survey (FNDDS) | 213 / 18.4 / 0.0 / 14.9 | KCAL | 213 | yes | 176 / 20 / 0 / 10 |
| lean beef steak | beef steak lean raw | Beef, grass-fed, strip steaks, lean only, raw | SR Legacy | 117 / 23.1 / 0.0 / 2.7 | KCAL | 117 | yes | 170 / 26 / 0 / 7 |
| lean turkey mince | lean turkey mince | Ham, minced | SR Legacy | 263 / 16.3 / 1.8 / 20.7 | KCAL | 263 | yes | 150 / 22 / 0 / 7 |
| low sodium chicken broth | low sodium chicken broth | Soup, chicken broth, low sodium, canned | SR Legacy | 67 / 2.0 / 1.2 / 0.6 | kJ ⚠ kJ | 16.0 | yes | 7 / 1 / 0.4 / 0.2 |
| low sodium soy sauce | soy sauce low sodium | Soy sauce made from soy and wheat (shoyu), low sodium | SR Legacy | 57 / 9.1 / 5.6 / 0.3 | KCAL | 57.0 | yes | 53 / 8 / 4.9 / 0.6 |
| mixed salad greens | mixed salad greens | Mixed salad greens, raw | Survey (FNDDS) | 21 / 1.3 / 3.4 / 0.2 | KCAL | 21 | yes | 15 / 1.5 / 3 / 0.2 |
| mushrooms | mushrooms | MUSHROOMS | Branded | 23 / 2.3 / 3.1 / 0.8 | KCAL | 23.0 | yes | 22 / 3.1 / 3.3 / 0.3 |
| pork tenderloin | pork tenderloin | PORK TENDERLOIN | Branded | 98 / 17.9 / 2.7 / 2.2 | KCAL | 98.0 | yes | 121 / 21.0 / 0.0 / 3.5 |
| potato | potato | Potato patty | Survey (FNDDS) | 171 / 3.9 / 13.5 / 11.3 | KCAL | 171 | yes | 77 / 2.0 / 17.5 / 0.1 |
| pumpkin | pumpkin | PUMPKIN | Branded | 33 / 0.8 / 8.3 / 0.0 | KCAL | 33.0 | yes | 26 / 1.0 / 6.5 / 0.1 |
| red capsicum | red capsicum | Sangria, red | Survey (FNDDS) | 85 / 0.0 / 7.2 / 0.0 | KCAL | 85 | yes | 31 / 1.0 / 6.0 / 0.3 |
| rice noodles | rice noodles | RICE NOODLES | Branded | 357 / 7.1 / 80.4 / 0.9 | KCAL | 357 | yes | 364 / 6 / 80 / 0.6 |
| salmon fillet | salmon raw | Fish, salmon, raw | Survey (FNDDS) | 188 / 20.4 / 0.0 / 11.2 | KCAL | 188 | yes | 208 / 20.4 / 0 / 13.4 |
| shrimp | shrimp raw | Crustaceans, shrimp, raw | SR Legacy | 356 / 20.1 / 0.0 / 0.5 | kJ ⚠ kJ | 85.0 | yes | 85 / 20.1 / 0.2 / 0.5 |
| soy sauce | soy sauce | Soy sauce | Survey (FNDDS) | 53 / 8.1 / 4.9 / 0.6 | KCAL | 53 | yes | 53 / 8 / 4.9 / 0.6 |
| tempeh | tempeh | Tempeh | SR Legacy | 192 / 20.3 / 7.6 / 10.8 | KCAL | 192 | yes | 192 / 20.3 / 7.6 / 10.8 |
| tomato | tomato | TOMATO | Branded | 0 / 0.0 / 0.0 / 0.0 | none | none | no (no calories, protein, carbs, fat) | 18 / 0.9 / 3.9 / 0.2 |
| tomato passata | tomato passata | TOMATO PASSATA, TOMATO | Branded | 32 / 1.6 / 4.8 / 0.0 | KCAL | 32.0 | yes | 33 / 1.6 / 5.5 / 0.2 |
| tuna | tuna canned in water | Fish, tuna, light, canned in water, drained solids | Foundation | 376 / 19.0 / 0.1 / 0.9 | kJ ⚠ kJ | 90.0 | yes | 116 / 25.5 / 0 / 0.8 |
| whole wheat bread | whole wheat bread | WHOLE WHEAT BREAD | Branded | 233 / 11.6 / 44.2 / 3.5 | KCAL | 233 | yes | 247 / 13 / 41 / 4.2 |
| whole wheat hamburger bun | whole wheat hamburger bun | Roll, whole wheat, hamburger bun | Survey (FNDDS) | 269 / 12.4 / 44.9 / 4.4 | KCAL | 269 | yes | 260 / 10 / 44 / 4 |
| whole wheat tortilla | whole wheat tortilla | Tortilla, whole wheat | Survey (FNDDS) | 310 / 9.8 / 45.9 / 9.8 | KCAL | 310 | yes | 310 / 9 / 50 / 8 |
| wholemeal pasta | wholemeal pasta | Pasta, cooked | Survey (FNDDS) | 157 / 5.8 / 30.7 / 0.9 | KCAL | 157 | yes | 348 / 14 / 70 / 2.5 |
| zucchini | zucchini | ZUCCHINI | Branded | 21 / 1.1 / 4.2 / 0.0 | KCAL | 21.0 | yes | 17 / 1.2 / 3.1 / 0.3 |

## Problem ingredients searched with `dataType=Foundation,SR Legacy`

| Ingredient | Filtered top hit | Type | Agent reads | Picked | KCAL entry | Better? |
|---|---|---|---|---|---:|---|
| shrimp | Crustaceans, shrimp, raw | SR Legacy | 356 / 20.1 / 0.0 / 0.5 | kJ | 85.0 | same food, kJ bug |
| tuna | Fish, tuna, light, canned in water, drained solids | Foundation | 376 / 19.0 / 0.1 / 0.9 | kJ | 90.0 | same food, kJ bug |
| low sodium chicken broth | Soup, chicken broth, low sodium, canned | SR Legacy | 67 / 2.0 / 1.2 / 0.6 | kJ | 16.0 | same food, kJ bug |
| avocado | Oil, avocado | SR Legacy | 884 / 0.0 / 0.0 / 100.0 | KCAL | 884 | no (oil) |
| lean turkey mince | Ham, minced | SR Legacy | 263 / 16.3 / 1.8 / 20.7 | KCAL | 263 | no (same ham) |
| potato | Bread, potato | SR Legacy | 266 / 12.5 / 47.1 / 3.1 | KCAL | 266 | no (bread) |
| red capsicum | Spices, pepper, red or cayenne | SR Legacy | 1330 / 12.0 / 56.6 / 17.3 | kJ | 318 | no (cayenne, kJ bug) |
| brown rice | Brown rice, puffed | Foundation | 377 / 7.8 / 80.3 / 2.8 | KCAL | 377 | no (puffed) |
| hummus | Hummus, commercial | SR Legacy | 237 / 7.8 / 15.0 / 17.8 | KCAL | 237 | closer (237 vs 321) |
| cod fillet | Fish oil, cod liver | SR Legacy | 902 / 0.0 / 0.0 / 100.0 | KCAL | 902 | no (cod liver oil) |
| chicken thigh | Chicken, skin (drumsticks and thighs), raw | SR Legacy | 1840 / 9.6 / 0.8 / 44.2 | kJ | 440 | no (skin, kJ bug) |
| wholemeal pasta | Pasta, dry, enriched | SR Legacy | 371 / 13.0 / 74.7 / 1.5 | KCAL | 371 | no (dry pasta) |
| tomato | Tomato powder | SR Legacy | 302 / 12.9 / 74.7 / 0.4 | KCAL | 302 | no (powder) |
| cooked white rice | Rice, white, glutinous, unenriched, cooked | SR Legacy | 406 / 2.0 / 21.1 / 0.2 | kJ | 97.0 | no (glutinous, kJ bug) |
