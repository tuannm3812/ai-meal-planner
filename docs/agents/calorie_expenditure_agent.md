# Calorie Expenditure Agent

## Role

Predict calorie expenditure and produce a meal calorie budget for downstream meal recommendation.

## Inputs

- Age, sex, height, and weight.
- Activity multiplier.
- Optional exercise session features: duration, heart rate, and body temperature.
- Goal such as maintain, weight loss, or muscle gain.
- Health conditions used as recommendation constraints.

## Model Plan

Train a regression model with the Kaggle Playground Series S5E5 calorie expenditure dataset. Start with the notebook in `notebooks/calorie_expenditure_kaggle_training.ipynb`, then promote the exported `joblib` artifact into `models/calorie_expenditure/`.

## Outputs

- `estimated_daily_expenditure_kcal`
- `meal_calorie_budget_kcal`
- `model_version`
- `confidence`
- `warnings`
