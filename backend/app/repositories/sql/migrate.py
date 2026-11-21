"""Brings a SQLite database to the current schema with Alembic (DEC-32)."""

from pathlib import Path
from typing import Any

from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError
from sqlalchemy import Connection, Engine, create_engine, event, inspect

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

# Seconds a process waits for another process's migration to finish.
_LOCK_TIMEOUT_SECONDS = 30

# Databases made by create_all, before migrations existed, have no version
# table. Each known shape maps to the revision that describes it.
_BASELINE_COLUMNS = {
    "meal_plans": {"id", "user_id", "saved_at", "payload"},
    "meal_feedback": {"id", "user_id", "saved", "saved_at", "payload"},
}
_G4_COLUMNS = {
    "meal_plans": _BASELINE_COLUMNS["meal_plans"] | {"client_id", "request_id"},
    "meal_feedback": _BASELINE_COLUMNS["meal_feedback"] | {"client_id"},
}
_REVISION_OF_SHAPE = (("0001", _BASELINE_COLUMNS), ("0002", _G4_COLUMNS))


def migrate_to_head(path: Path) -> None:
    """Upgrade the database file to the latest revision, creating it if needed.

    The whole upgrade is one transaction that holds SQLite's write lock. A
    failed migration leaves the file as it was, and a second process starting
    at the same moment waits, then finds nothing left to do.

    Args:
        path: Filesystem location of the database file.

    Raises:
        RuntimeError: If the file's schema is not one this code can upgrade,
            or it was written by a newer revision than this code knows.
    """
    engine = _single_writer_engine(path)
    config = Config()
    # Config values are %-interpolated, so a literal % in the path is doubled.
    config.set_main_option("script_location", str(MIGRATIONS_DIR).replace("%", "%%"))
    try:
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            revision = _revision_of_unversioned_schema(connection, path)
            if revision is not None:
                command.stamp(config, revision)
            command.upgrade(config, "head")
    except CommandError as exc:
        raise RuntimeError(
            f"{path} could not be migrated: {exc}. Its schema may be newer than this "
            "code; deploy the matching version or restore a backup."
        ) from exc
    finally:
        engine.dispose()


def _single_writer_engine(path: Path) -> Engine:
    """Build an engine whose transactions take the write lock and cover DDL.

    By default the sqlite3 driver commits around DDL and starts transactions
    late, which would break both promises of ``migrate_to_head``. This is the
    recipe from SQLAlchemy's SQLite documentation, with ``BEGIN IMMEDIATE`` so
    the lock is held before the schema is inspected.

    Args:
        path: Filesystem location of the database file.

    Returns:
        An engine to use for migration only.
    """
    engine = create_engine(f"sqlite:///{path}", connect_args={"timeout": _LOCK_TIMEOUT_SECONDS})

    @event.listens_for(engine, "connect")
    def _leave_transactions_to_sqlalchemy(dbapi_connection: Any, _record: Any) -> None:
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _take_the_write_lock(connection: Connection) -> None:
        connection.exec_driver_sql("BEGIN IMMEDIATE")

    return engine


def _revision_of_unversioned_schema(connection: Connection, path: Path) -> str | None:
    """Name the revision an existing, unversioned database already matches.

    Args:
        connection: A connection to the database.
        path: The database file, named in the error.

    Returns:
        The matching revision, or None when there is nothing to stamp: the
        database already has a version, or it holds none of our tables.

    Raises:
        RuntimeError: If our tables exist in a shape no revision describes.
    """
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if "alembic_version" in tables or not tables & set(_BASELINE_COLUMNS):
        return None
    shape = {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in tables & set(_BASELINE_COLUMNS)
    }
    for revision, known_shape in _REVISION_OF_SHAPE:
        if shape == known_shape:
            return revision
    raise RuntimeError(
        f"{path} has no migration history and an unrecognised schema, so it was left "
        "untouched. Move this file aside and restart to begin with an empty database."
    )
