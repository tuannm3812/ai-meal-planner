"""SQLModel table definitions for the SQLite backend."""

from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class MealPlanRow(SQLModel, table=True):
    """One stored meal-plan response.

    Attributes:
        id: Auto-incrementing primary key, used for newest-first ordering.
        user_id: Owner of the record; indexed because queries filter on it.
        saved_at: ISO-8601 UTC timestamp of when the record was written.
        payload: The full API response, stored verbatim as JSON.
    """

    __tablename__ = "meal_plans"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    saved_at: str
    payload: dict[str, Any] = Field(sa_column=Column(JSON))


class MealFeedbackRow(SQLModel, table=True):
    """One stored feedback record.

    Attributes:
        id: Auto-incrementing primary key, used for newest-first ordering.
        user_id: Owner of the record; indexed because queries filter on it.
        saved: Whether the feedback was flagged as saved; indexed because
            queries filter on it.
        saved_at: ISO-8601 UTC timestamp of when the record was written.
        payload: The full feedback payload, stored verbatim as JSON.
    """

    __tablename__ = "meal_feedback"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    saved: bool = Field(default=False, index=True)
    saved_at: str
    payload: dict[str, Any] = Field(sa_column=Column(JSON))
