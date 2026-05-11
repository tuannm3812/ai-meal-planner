from pydantic import BaseModel, Field


class MealRequest(BaseModel):
    user_id: str = Field(default="user_123", min_length=3, max_length=80)
    craving: str = Field(min_length=2, max_length=180)
    location: str = Field(default="Earlwood, NSW", min_length=2, max_length=160)
    health_conditions: list[str] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)


class MealFeedbackRequest(BaseModel):
    user_id: str = Field(default="user_123", min_length=3, max_length=80)
    request_id: str = Field(min_length=8, max_length=120)
    meal_id: str | None = Field(default=None, max_length=120)
    meal_name: str = Field(min_length=2, max_length=180)
    liked: bool | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    saved: bool = False
    notes: str | None = Field(default=None, max_length=500)
