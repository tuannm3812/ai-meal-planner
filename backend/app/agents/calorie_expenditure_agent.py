from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class CalorieExpenditureRequest(BaseModel):
    age: int = Field(gt=0, le=120)
    sex: str = Field(min_length=1, max_length=16)
    height_cm: float = Field(gt=80, le=260)
    weight_kg: float = Field(gt=20, le=350)
    activity_multiplier: float = Field(default=1.35, gt=1.0, le=2.5)
    duration_minutes: float | None = Field(default=None, gt=0, le=600)
    heart_rate_bpm: float | None = Field(default=None, gt=20, le=240)
    body_temp_c: float | None = Field(default=None, gt=30, le=45)
    goal: str = Field(default="maintain", min_length=3, max_length=40)
    health_conditions: list[str] = Field(default_factory=list)


class CalorieExpenditureResponse(BaseModel):
    estimated_daily_expenditure_kcal: float
    meal_calorie_budget_kcal: float
    model_version: str
    confidence: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)


class CalorieExpenditureAgent:
    def __init__(self, model_path: Path | None = None, model_version: str = "rule_based_v0.1.0"):
        self.model_path = model_path
        self.model_version = model_version
        self.model: Any | None = None
        self.model_warning: str | None = None

        if model_path and model_path.exists():
            try:
                import joblib

                self.model = joblib.load(model_path)
            except Exception as exc:
                self.model_warning = f"Unable to load calorie model: {exc}"

    def predict(self, request: CalorieExpenditureRequest) -> CalorieExpenditureResponse:
        warnings = self._health_warnings(request.health_conditions)
        if self.model_warning:
            warnings.append(self.model_warning)

        if self.model:
            expenditure = self._predict_with_model(request)
            confidence = 0.82
            model_version = self.model_version
        else:
            expenditure = self._estimate_with_bmr(request)
            confidence = 0.55
            model_version = "mifflin_st_jeor_fallback_v0.1.0"
            warnings.append("Using rule-based fallback until trained model artifact is available.")

        meal_budget = self._meal_budget(expenditure, request.goal)
        return CalorieExpenditureResponse(
            estimated_daily_expenditure_kcal=round(expenditure, 1),
            meal_calorie_budget_kcal=round(meal_budget, 1),
            model_version=model_version,
            confidence=confidence,
            warnings=warnings,
        )

    def _predict_with_model(self, request: CalorieExpenditureRequest) -> float:
        import pandas as pd

        row = {
            "Sex": request.sex,
            "Age": request.age,
            "Height": request.height_cm,
            "Weight": request.weight_kg,
            "Duration": request.duration_minutes or 30,
            "Heart_Rate": request.heart_rate_bpm or 100,
            "Body_Temp": request.body_temp_c or 37,
        }
        prediction = self.model.predict(pd.DataFrame([row]))[0]
        exercise_calories = max(float(prediction), 0.0)
        return self._estimate_with_bmr(request) + exercise_calories

    @staticmethod
    def _estimate_with_bmr(request: CalorieExpenditureRequest) -> float:
        sex = request.sex.strip().lower()
        if sex in {"m", "male"}:
            bmr = (10 * request.weight_kg) + (6.25 * request.height_cm) - (5 * request.age) + 5
        else:
            bmr = (10 * request.weight_kg) + (6.25 * request.height_cm) - (5 * request.age) - 161
        return bmr * request.activity_multiplier

    @staticmethod
    def _meal_budget(expenditure: float, goal: str) -> float:
        normalized_goal = goal.strip().lower()
        if normalized_goal in {"cut", "lose", "fat_loss", "weight_loss"}:
            return expenditure - 400
        if normalized_goal in {"bulk", "gain", "muscle_gain", "weight_gain"}:
            return expenditure + 250
        return expenditure

    @staticmethod
    def _health_warnings(health_conditions: list[str]) -> list[str]:
        if not health_conditions:
            return []
        return [
            "Health conditions are used as recommendation constraints only; this is not medical advice."
        ]
