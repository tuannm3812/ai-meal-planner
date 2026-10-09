"""SQLModel table definitions for the SQLite backend."""

from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# Both tables order by descending id rather than saved_at: two records written in the
# same ISO-8601 microsecond would otherwise order arbitrarily, and neither table ever
# deletes rows, so SQLite's rowid is monotonic.
class MealPlanRow(SQLModel, table=True):
    """One stored meal-plan response.

    Attributes:
        id: Auto-incrementing primary key, used for newest-first ordering.
        client_id: The client application that owns the record (G4); indexed
            because every query filters on it first.
        user_id: Owner within the client's namespace; indexed because queries
            filter on it.
        request_id: The generation request id, indexed so feedback can check
            that a referenced plan belongs to the caller.
        saved_at: ISO-8601 UTC timestamp of when the record was written.
        payload: The full API response, stored verbatim as JSON.
    """

    __tablename__ = "meal_plans"

    id: int | None = Field(default=None, primary_key=True)
    client_id: str = Field(index=True)
    user_id: str = Field(index=True)
    request_id: str | None = Field(default=None, index=True)
    saved_at: str
    payload: dict[str, Any] = Field(sa_column=Column(JSON))


class MealFeedbackRow(SQLModel, table=True):
    """One stored feedback record.

    Attributes:
        id: Auto-incrementing primary key, used for newest-first ordering.
        client_id: The client application that owns the record (G4); indexed
            because every query filters on it first.
        user_id: Owner within the client's namespace; indexed because queries
            filter on it.
        saved: Whether the feedback was flagged as saved; indexed because
            queries filter on it.
        saved_at: ISO-8601 UTC timestamp of when the record was written.
        payload: The full feedback payload, stored verbatim as JSON.
    """

    __tablename__ = "meal_feedback"

    id: int | None = Field(default=None, primary_key=True)
    client_id: str = Field(index=True)
    user_id: str = Field(index=True)
    saved: bool = Field(default=False, index=True)
    saved_at: str
    payload: dict[str, Any] = Field(sa_column=Column(JSON))
