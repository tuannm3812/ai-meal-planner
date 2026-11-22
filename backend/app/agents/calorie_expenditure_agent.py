import logging
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

WEIGHT_LOSS_FLOOR_KCAL = {"female": 1200.0, "male": 1500.0}
"""The lowest daily budget a weight-loss goal produces (owner decision, 2026-10-17).
A sex outside the trained categories gets the higher floor."""


class CalorieExpenditureRequest(BaseModel):
    age: int = Field(gt=0, le=120)
    sex: str = Field(min_length=1, max_length=16)
    height_cm: float = Field(gt=80, le=260)
    weight_kg: float = Field(gt=20, le=350)
    activity_multiplier: float = Field(default=1.35, gt=1.0, le=2.5)
    # 0 is a rest day: no exercise is added. None means not known, so the
    # model's defaults stand in (EXERCISE_DEFAULTS).
    duration_minutes: float | None = Field(default=None, ge=0, le=600)
    heart_rate_bpm: float | None = Field(default=None, gt=20, le=240)
    body_temp_c: float | None = Field(default=None, gt=30, le=45)
    goal: str = Field(default="maintain", min_length=3, max_length=40)
    health_conditions: list[str] = Field(default_factory=list)


EXERCISE_DEFAULTS = {"duration_minutes": 30.0, "heart_rate_bpm": 100.0, "body_temp_c": 37.0}
"""What the model assumes for a workout detail the request leaves out."""

MODEL_MAX_DURATION_MINUTES = 30.0
"""The longest workout in the model's training data (Kaggle S5E5, 1-30 minutes).

Its boosted trees are flat past this point, so a 90-minute workout predicted
directly scores the same as a 30-minute one. A longer workout is predicted at
30 minutes and scaled by its length, holding the 30-minute rate per minute."""

MODEL_MAX_HEART_RATE_BPM = 128.0
"""The highest average heart rate in the training data. The model predicts the
same calories for any rate above it, so a harder workout is undercounted."""

SEDENTARY_MULTIPLIER = 1.2
"""The activity multiplier that holds no exercise. The other activity levels are
exercise days in a usual week, so a stated workout replaces them (DEC-40)."""


class ExerciseEstimate(BaseModel):
    """The workout the trained model added to the daily estimate (DEC-33).

    Attributes:
        duration_minutes: Minutes of exercise; 0 is a rest day.
        heart_rate_bpm: Average heart rate during the workout.
        body_temp_c: Body temperature during the workout.
        kcal: Calories the workout added to the daily estimate.
        defaulted: The details the request left out, filled from EXERCISE_DEFAULTS.
        replaces_activity_exercise: True when the request stated today's workout,
            so the day counts it in place of the activity level's usual exercise
            (DEC-40). False when the workout was not given, and the default is
            added to the activity level as before.
    """

    duration_minutes: float
    heart_rate_bpm: float
    body_temp_c: float
    kcal: float
    defaulted: list[str] = Field(default_factory=list)
    replaces_activity_exercise: bool = False


class CalorieExpenditureResponse(BaseModel):
    estimated_daily_expenditure_kcal: float
    meal_calorie_budget_kcal: float
    model_version: str
    confidence: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)
    # None when the rule-based fallback ran, which adds no exercise.
    exercise: ExerciseEstimate | None = None


class CalorieExpenditureAgent:
    _TRAINED_SEX_CATEGORIES = {"male", "female"}
    _SEX_ALIASES = {"m": "male", "male": "male", "f": "female", "female": "female"}

    def __init__(self, model_path: Path | None = None, model_version: str = "rule_based_v0.1.0"):
        self.model_path = model_path
        self.model_version = model_version
        self.model: Any | None = None
        self.model_warning: str | None = None

        if model_path and model_path.exists():
            try:
                import warnings

                import joblib

                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")
                    self.model = joblib.load(model_path)
                if caught_warnings:
                    warning_count = len(caught_warnings)
                    self.model_warning = (
                        f"Loaded calorie model with {warning_count} compatibility warning(s). "
                        "Install pinned backend requirements before production use."
                    )
            except Exception as exc:
                self.model_warning = f"Unable to load calorie model: {exc}"
        elif model_path:
            self.model_warning = f"Calorie model artifact not found: {model_path}"

        if self.model is not None:
            self._warm_up_model()

    def _warm_up_model(self) -> None:
        # Absorbs first-call JIT/bin-cache costs at startup instead of on the first user request.
        try:
            self.model.predict(
                pd.DataFrame(
                    [
                        {
                            "Sex": "male",
                            "Age": 30,
                            "Height": 175.0,
                            "Weight": 75.0,
                            "Duration": 30.0,
                            "Heart_Rate": 100.0,
                            "Body_Temp": 37.0,
                        }
                    ]
                )
            )
        except Exception as exc:
            logger.warning("Calorie model warm-up prediction failed: %s", exc)

    def predict(self, request: CalorieExpenditureRequest) -> CalorieExpenditureResponse:
        warnings = self._health_warnings(request.health_conditions)
        if self.model_warning:
            warnings.append(self.model_warning)

        if self.model:
            normalized_sex, sex_warning = self._normalize_sex_category(request.sex)
            if sex_warning:
                warnings.append(sex_warning)
            exercise, exercise_kcal = self._estimate_exercise(request, normalized_sex)
            warnings.extend(self._workout_range_warnings(exercise))
            multiplier = request.activity_multiplier
            if exercise.replaces_activity_exercise:
                multiplier = min(multiplier, SEDENTARY_MULTIPLIER)
            expenditure = self._estimate_with_bmr(request, multiplier) + exercise_kcal
            confidence = 0.82
            model_version = self.model_version
        else:
            expenditure = self._estimate_with_bmr(request)
            confidence = 0.55
            model_version = "mifflin_st_jeor_fallback_v0.1.0"
            exercise = None
            warnings.append("Using rule-based fallback until trained model artifact is available.")

        meal_budget, floor_warning = self._meal_budget(expenditure, request.goal, request.sex)
        if floor_warning:
            warnings.append(floor_warning)
        return CalorieExpenditureResponse(
            estimated_daily_expenditure_kcal=round(expenditure, 1),
            meal_calorie_budget_kcal=round(meal_budget, 1),
            model_version=model_version,
            confidence=confidence,
            warnings=warnings,
            exercise=exercise,
        )

    @classmethod
    def _normalize_sex_category(cls, sex: str) -> tuple[str, str | None]:
        normalized = sex.strip().lower()
        mapped = cls._SEX_ALIASES.get(normalized)
        if mapped:
            return mapped, None
        return normalized, (
            f"Unrecognized sex value '{sex}'; the calorie model was trained on "
            f"{sorted(cls._TRAINED_SEX_CATEGORIES)} and may return a degraded prediction."
        )

    def _estimate_exercise(
        self, request: CalorieExpenditureRequest, normalized_sex: str
    ) -> tuple[ExerciseEstimate, float]:
        """Predict the calories one workout adds, filling unknown details.

        Args:
            request: The calorie request; any workout detail may be missing.
            normalized_sex: The sex category the model was trained on.

        Returns:
            The workout used, and its unrounded calories for the daily sum
            (the estimate reports them rounded). A rest day adds none and does
            not call the model, whose training data has no zero-minute rows.
        """
        given = {field: getattr(request, field) for field in EXERCISE_DEFAULTS}
        defaulted = [field for field, value in given.items() if value is None]
        used = {
            field: EXERCISE_DEFAULTS[field] if given[field] is None else given[field]
            for field in EXERCISE_DEFAULTS
        }
        duration = used["duration_minutes"]
        if duration == 0:
            kcal = 0.0
        else:
            modelled = min(duration, MODEL_MAX_DURATION_MINUTES)
            row = {
                "Sex": normalized_sex,
                "Age": request.age,
                "Height": request.height_cm,
                "Weight": request.weight_kg,
                "Duration": modelled,
                "Heart_Rate": used["heart_rate_bpm"],
                "Body_Temp": used["body_temp_c"],
            }
            kcal = max(float(self.model.predict(pd.DataFrame([row]))[0]), 0.0)
            kcal *= duration / modelled
        estimate = ExerciseEstimate(
            **used,
            kcal=round(kcal, 1),
            defaulted=defaulted,
            replaces_activity_exercise=given["duration_minutes"] is not None,
        )
        return estimate, kcal

    @staticmethod
    def _workout_range_warnings(exercise: ExerciseEstimate) -> list[str]:
        """Say when a stated workout lies outside what the model was trained on."""
        warnings = []
        if exercise.duration_minutes > MODEL_MAX_DURATION_MINUTES:
            warnings.append(
                f"Workouts over {MODEL_MAX_DURATION_MINUTES:.0f} minutes are estimated at the "
                f"{MODEL_MAX_DURATION_MINUTES:.0f}-minute rate per minute, beyond the model's "
                "training range."
            )
        if exercise.duration_minutes and exercise.heart_rate_bpm > MODEL_MAX_HEART_RATE_BPM:
            warnings.append(
                f"Heart rates above {MODEL_MAX_HEART_RATE_BPM:.0f} bpm are estimated as "
                f"{MODEL_MAX_HEART_RATE_BPM:.0f} bpm, so a harder workout may be undercounted."
            )
        return warnings

    @staticmethod
    def _estimate_with_bmr(
        request: CalorieExpenditureRequest, multiplier: float | None = None
    ) -> float:
        """BMR (Mifflin-St Jeor) times a multiplier, the request's activity level by default."""
        sex = request.sex.strip().lower()
        if sex in {"m", "male"}:
            bmr = (10 * request.weight_kg) + (6.25 * request.height_cm) - (5 * request.age) + 5
        else:
            bmr = (10 * request.weight_kg) + (6.25 * request.height_cm) - (5 * request.age) - 161
        return bmr * (request.activity_multiplier if multiplier is None else multiplier)

    @classmethod
    def _meal_budget(cls, expenditure: float, goal: str, sex: str) -> tuple[float, str | None]:
        """Turn expenditure into the daily budget for a goal.

        A weight-loss deficit of 400 kcal stops at a floor of 1,200 kcal for
        women and 1,500 for men, and the floor never lifts the budget above
        expenditure, which would turn the deficit into a surplus.

        Returns:
            The budget and, when the floor applied, a warning saying so.
        """
        normalized_goal = goal.strip().lower()
        if normalized_goal in {"cut", "lose", "fat_loss", "weight_loss"}:
            deficit_budget = expenditure - 400
            floor = WEIGHT_LOSS_FLOOR_KCAL.get(
                cls._SEX_ALIASES.get(sex.strip().lower(), ""),
                max(WEIGHT_LOSS_FLOOR_KCAL.values()),
            )
            if deficit_budget >= floor:
                return deficit_budget, None
            return min(floor, expenditure), (
                f"The weight-loss budget was raised to the {floor:.0f} kcal minimum "
                "(or to estimated expenditure, if lower)."
            )
        if normalized_goal in {"bulk", "gain", "muscle_gain", "weight_gain"}:
            return expenditure + 250, None
        return expenditure, None

    @staticmethod
    def _health_warnings(health_conditions: list[str]) -> list[str]:
        if not health_conditions:
            return []
        return [
            "Health conditions are used as recommendation constraints only; "
            "this is not medical advice."
        ]
