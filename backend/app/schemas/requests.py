from pydantic import BaseModel, Field


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
