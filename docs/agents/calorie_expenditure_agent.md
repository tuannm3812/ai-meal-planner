# Calorie Expenditure Agent

## Role

Predict calorie expenditure and produce a meal calorie budget for downstream meal recommendation.

## Inputs

- Age, sex, height, and weight.
- Activity multiplier.
- Optional exercise session features: duration, heart rate, and body temperature.
- Goal such as maintain, weight loss, or muscle gain.
- Health conditions used as recommendation constraints.

## Promoted Model

The current promoted artifact lives at `models/calorie_expenditure/calorie_expenditure_model.joblib`.

Training source: Kaggle Playground Series S5E5 calorie expenditure dataset.

Current model: `hist_gradient_boosting_deep_v0.1.0`.

The model predicts exercise calories from:

- `Sex`
- `Age`
- `Height`
- `Weight`
- `Duration`
- `Heart_Rate`
- `Body_Temp`

The backend agent adds predicted exercise calories to a BMR-based daily estimate, then adjusts the meal calorie budget by goal: minus 400 kcal to lose weight, plus 250 to gain. A weight-loss budget never drops below 1,200 kcal for women or 1,500 for men (or an unrecognised sex), and never rises above estimated expenditure; when the floor applies, a warning says so (DEC-24).

## Outputs

- `estimated_daily_expenditure_kcal`
- `meal_calorie_budget_kcal`
- `model_version`
- `confidence`
- `warnings`
