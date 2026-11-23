from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class Ingredient(BaseModel):
    item_name: str = Field(min_length=2)
    base_quantity_grams: int = Field(gt=0, le=2000)


class MealRequest(BaseModel):
    user_id: str = Field(default="user_123", min_length=3, max_length=80)
    craving: str = Field(min_length=2, max_length=180)
    location: str = Field(default="Earlwood, NSW", min_length=2, max_length=160)
    health_conditions: list[str] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    age: int | None = Field(default=None, gt=0, le=120)
    sex: str | None = Field(default=None, min_length=1, max_length=16)
    height_cm: float | None = Field(default=None, gt=80, le=260)
    weight_kg: float | None = Field(default=None, gt=20, le=350)
    activity_multiplier: float | None = Field(default=None, gt=1.0, le=2.5)
    # Today's workout (DEC-33). 0 minutes is a rest day; an omitted detail
    # falls back to the calorie model's default.
    duration_minutes: float | None = Field(default=None, ge=0, le=600)
    heart_rate_bpm: float | None = Field(default=None, gt=20, le=240)
    body_temp_c: float | None = Field(default=None, gt=30, le=45)
    goal: str = Field(default="maintain", min_length=3, max_length=40)


class MealFeedbackRequest(BaseModel):
    user_id: str = Field(default="user_123", min_length=3, max_length=80)
    request_id: str = Field(min_length=8, max_length=120)
    meal_id: str | None = Field(default=None, max_length=120)
    meal_name: str = Field(min_length=2, max_length=180)
    liked: bool | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    saved: bool = False
    notes: str | None = Field(default=None, max_length=500)


class AccountProfile(BaseModel):
    """The React app's profile fields, as it holds them (DEC-36, DEC-43).

    Number inputs are kept as the strings the person typed; the app converts
    them only when it plans. Every field is bounded and no other field is
    accepted, so an account stores exactly what the Profile page shows.
    """

    model_config = ConfigDict(extra="forbid")

    goal: str | None = Field(default=None, max_length=40)
    age: str | None = Field(default=None, max_length=8)
    sex: str | None = Field(default=None, max_length=16)
    heightCm: str | None = Field(default=None, max_length=8)  # noqa: N815 - the app's key
    weightKg: str | None = Field(default=None, max_length=8)  # noqa: N815
    activity: str | None = Field(default=None, max_length=8)
    workout: str | None = Field(default=None, max_length=16)
    workoutMinutes: str | None = Field(default=None, max_length=8)  # noqa: N815
    heartRate: str | None = Field(default=None, max_length=8)  # noqa: N815
    avoid: list[Annotated[str, Field(max_length=40)]] = Field(default_factory=list, max_length=16)


class AccountProfileRequest(BaseModel):
    """A signed-in user's profile and shopping location, to save to their account."""

    model_config = ConfigDict(extra="forbid")

    profile: AccountProfile
    location: str | None = Field(default=None, max_length=160)
