# Calorie Expenditure Model

## Artifact

```text
calorie_expenditure_model.joblib
```

Current promoted version:

```text
hist_gradient_boosting_deep_v0.1.0
```

Training source:

```text
Kaggle Playground Series S5E5 - Predict Calorie Expenditure
```

## Validation Metrics

```text
MAE:   2.2364
RMSE:  3.7203
RMSLE: 0.0605
R2:    0.9964
```

## Feature Schema

Inputs expected by the trained model:

```text
Sex
Age
Height
Weight
Duration
Heart_Rate
Body_Temp
```

The model predicts exercise calories. The backend `CalorieExpenditureAgent` adds that prediction to a BMR-based daily expenditure estimate and then adjusts the meal calorie budget by goal.

## Runtime Notes

The artifact was trained with `scikit-learn==1.6.1`. Keep the backend dependency pinned to avoid estimator version warnings or incompatible model loading.

Do not commit Kaggle `submission.csv` files or large model variants here.
