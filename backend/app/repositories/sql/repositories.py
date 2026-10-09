"""SQLite-backed repository implementations."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, inspect
from sqlmodel import Session, SQLModel, col, create_engine, desc, select

from ..base import owner_of_feedback, owner_of_meal_plan
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
    _refuse_a_pre_g4_schema(engine, path)
    SQLModel.metadata.create_all(engine)
    return engine


_REQUIRED_COLUMNS = {
    "meal_plans": {"client_id", "request_id"},
    "meal_feedback": {"client_id"},
}


def _refuse_a_pre_g4_schema(engine: Engine, path: Path) -> None:
    """Stop at startup if an existing table predates G4's client_id column.

    ``create_all`` creates missing tables but cannot add columns to existing
    ones, and there are no migrations (next steps §7.1). Without this check an
    old database would fail on its first query instead of at startup.

    Args:
        engine: The engine for the database file.
        path: The database file, named in the error.

    Raises:
        RuntimeError: If an existing table lacks a required column.
    """
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    for table, required in _REQUIRED_COLUMNS.items():
        if table not in existing:
            continue
        missing = required - {column["name"] for column in inspector.get_columns(table)}
        if missing:
            raise RuntimeError(
                f"{path} has a pre-G4 schema: table {table!r} lacks {sorted(missing)}. "
                "There are no migrations, so delete this file (or migrate it by "
                "hand) and restart. Stateless v1 does not keep history across restarts."
            )


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

    def save(self, payload: dict[str, Any], *, client_id: str) -> None:
        """Append one meal-plan response.

        Args:
            payload: The full API response to store.
            client_id: The client application that owns the record.
        """
        record = {"saved_at": _now(), **payload, "client_id": client_id}
        request_id = payload.get("request_id")
        with Session(self.engine) as session:
            session.add(
                MealPlanRow(
                    client_id=client_id,
                    request_id=request_id if isinstance(request_id, str) else None,
                    user_id=owner_of_meal_plan(payload),
                    saved_at=record["saved_at"],
                    payload=record,
                )
            )
            session.commit()

    def list_for_user(
        self, user_id: str, limit: int = 20, *, client_id: str
    ) -> list[dict[str, Any]]:
        """Return a user's most recent meal plans within one client, newest first.

        Args:
            user_id: Owner of the records within the client's namespace.
            limit: Maximum records to return.
            client_id: The client application whose namespace to read.

        Returns:
            Up to ``limit`` records, newest first.
        """
        with Session(self.engine) as session:
            rows = session.exec(
                select(MealPlanRow)
                .where(MealPlanRow.client_id == client_id)
                .where(MealPlanRow.user_id == user_id)
                .order_by(desc(MealPlanRow.id))
                .limit(limit)
            ).all()
        return [row.payload for row in rows]

    def find_by_request_id(self, request_id: str, *, client_id: str) -> dict[str, Any] | None:
        """Return the client's meal plan with this request id, if any.

        Args:
            request_id: The id returned when the plan was generated.
            client_id: The client application whose namespace to search.

        Returns:
            The stored record, or None if this client has no such plan.
        """
        with Session(self.engine) as session:
            row = session.exec(
                select(MealPlanRow)
                .where(MealPlanRow.client_id == client_id)
                .where(MealPlanRow.request_id == request_id)
                .order_by(desc(MealPlanRow.id))
                .limit(1)
            ).first()
        return row.payload if row else None


class SqlMealFeedbackRepository:
    """Stores meal feedback in SQLite."""

    def __init__(self, engine: Engine) -> None:
        """Store the engine.

        Args:
            engine: The SQLite engine.
        """
        self.engine = engine

    def save(self, payload: dict[str, Any], *, client_id: str) -> dict[str, Any]:
        """Append one feedback record.

        Args:
            payload: The feedback to store.
            client_id: The client application that owns the record.

        Returns:
            The stored record, including its ``saved_at`` timestamp.
        """
        record = {"saved_at": _now(), **payload, "client_id": client_id}
        with Session(self.engine) as session:
            session.add(
                MealFeedbackRow(
                    client_id=client_id,
                    user_id=owner_of_feedback(payload),
                    saved=bool(payload.get("saved", False)),
                    saved_at=record["saved_at"],
                    payload=record,
                )
            )
            session.commit()
        return record

    def list_for_user(
        self, user_id: str, limit: int = 20, saved_only: bool = False, *, client_id: str
    ) -> list[dict[str, Any]]:
        """Return a user's most recent feedback within one client, newest first.

        The ``saved_only`` filter is applied in the SQL ``WHERE`` clause
        before ``LIMIT`` is applied, so the database filters first and then
        limits - never the other way round. Filtering in Python after an
        unconditional ``LIMIT`` would silently drop matching rows that fall
        outside the unfiltered page.

        Args:
            user_id: Owner of the records within the client's namespace.
            limit: Maximum records to return.
            saved_only: Restrict to records flagged as saved.
            client_id: The client application whose namespace to read.

        Returns:
            Up to ``limit`` records, newest first.
        """
        with Session(self.engine) as session:
            statement = (
                select(MealFeedbackRow)
                .where(MealFeedbackRow.client_id == client_id)
                .where(MealFeedbackRow.user_id == user_id)
            )
            if saved_only:
                statement = statement.where(col(MealFeedbackRow.saved).is_(True))
            rows = session.exec(statement.order_by(desc(MealFeedbackRow.id)).limit(limit)).all()
        return [row.payload for row in rows]
