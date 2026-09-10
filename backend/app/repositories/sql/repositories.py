"""SQLite-backed repository implementations."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, col, create_engine, desc, select

from .models import MealFeedbackRow, MealPlanRow

DEFAULT_PROFILE: dict[str, Any] = {
    "age": 28,
    "gender": "m",
    "weight": 80.0,
    "height": 180.0,
    "workout_level": 1.55,
    "dietary_restrictions": ["dairy-free", "high-protein"],
}


def build_engine(path: Path) -> Engine:
    """Create the SQLite engine and ensure the schema exists.

    Args:
        path: Filesystem location of the database file.

    Returns:
        A ready-to-use SQLAlchemy engine.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _now() -> str:
    """Return the current UTC time in ISO-8601 form.

    Returns:
        The current UTC timestamp, ISO-8601 formatted.
    """
    return datetime.now(UTC).isoformat()


class SqlUserProfileRepository:
    """Reads user profiles, falling back to the built-in default."""

    def __init__(self, engine: Engine) -> None:
        """Store the engine.

        Args:
            engine: The SQLite engine.
        """
        self.engine = engine

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        """Return the default profile.

        Profiles are not yet stored in SQL - the JSON backend reads a
        hand-maintained file, and nothing writes profiles at runtime. This
        returns the same default the JSON store falls back to, so the two
        backends behave identically. See docs/4_next_steps.md.

        Args:
            user_id: Accepted for protocol compatibility; unused.

        Returns:
            A copy of the default profile.
        """
        return dict(DEFAULT_PROFILE)


class SqlMealPlanRepository:
    """Stores meal plans in SQLite."""

    def __init__(self, engine: Engine) -> None:
        """Store the engine.

        Args:
            engine: The SQLite engine.
        """
        self.engine = engine

    def save(self, payload: dict[str, Any]) -> None:
        """Append one meal-plan response.

        Args:
            payload: The full API response to store.
        """
        record = {"saved_at": _now(), **payload}
        with Session(self.engine) as session:
            session.add(
                MealPlanRow(
                    user_id=str(payload.get("request", {}).get("user_id", "")),
                    saved_at=record["saved_at"],
                    payload=record,
                )
            )
            session.commit()

    def list_for_user(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return a user's most recent meal plans, newest first.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.

        Returns:
            Up to ``limit`` records, newest first.
        """
        with Session(self.engine) as session:
            rows = session.exec(
                select(MealPlanRow)
                .where(MealPlanRow.user_id == user_id)
                .order_by(desc(MealPlanRow.id))
                .limit(limit)
            ).all()
        return [row.payload for row in rows]


class SqlMealFeedbackRepository:
    """Stores meal feedback in SQLite."""

    def __init__(self, engine: Engine) -> None:
        """Store the engine.

        Args:
            engine: The SQLite engine.
        """
        self.engine = engine

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Append one feedback record.

        Args:
            payload: The feedback to store.

        Returns:
            The stored record, including its ``saved_at`` timestamp.
        """
        record = {"saved_at": _now(), **payload}
        with Session(self.engine) as session:
            session.add(
                MealFeedbackRow(
                    user_id=str(payload.get("user_id", "")),
                    saved=bool(payload.get("saved", False)),
                    saved_at=record["saved_at"],
                    payload=record,
                )
            )
            session.commit()
        return record

    def list_for_user(
        self, user_id: str, limit: int = 20, saved_only: bool = False
    ) -> list[dict[str, Any]]:
        """Return a user's most recent feedback, newest first.

        The ``saved_only`` filter is applied in the SQL ``WHERE`` clause
        before ``LIMIT`` is applied, so the database filters first and then
        limits - never the other way round. Filtering in Python after an
        unconditional ``LIMIT`` would silently drop matching rows that fall
        outside the unfiltered page.

        Args:
            user_id: Owner of the records.
            limit: Maximum records to return.
            saved_only: Restrict to records flagged as saved.

        Returns:
            Up to ``limit`` records, newest first.
        """
        with Session(self.engine) as session:
            statement = select(MealFeedbackRow).where(MealFeedbackRow.user_id == user_id)
            if saved_only:
                statement = statement.where(col(MealFeedbackRow.saved).is_(True))
            rows = session.exec(statement.order_by(desc(MealFeedbackRow.id)).limit(limit)).all()
        return [row.payload for row in rows]
