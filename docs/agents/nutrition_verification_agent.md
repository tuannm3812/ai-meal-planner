# Nutrition Verification Agent

## Role

Verify ingredient-level nutrition using USDA FoodData Central and deterministic scaling by portion.

## Inputs

- Structured ingredients from `MealRecommendationAgent`.
- Ingredient names.
- Quantity in grams.

## Process

1. Normalize each ingredient name.
2. Query USDA FoodData Central.
3. Extract calories, protein, carbohydrates, and fat per 100 grams.
4. Scale nutrients by requested grams.
5. Return confidence and warnings for unmatched or estimated items.

## Outputs

- `ingredients_macros`
- `total_calories`
- `total_protein`
- `total_carbs`
- `total_fat`
- `metadata`
