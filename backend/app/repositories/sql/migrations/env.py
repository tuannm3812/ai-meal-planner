"""Alembic environment for the SQLite store.

The app passes its own connection (``migrate.py``). The ``alembic`` command line
has none, so it uses the configured database file; that is for writing new
revisions. Logging is left alone: ``fileConfig`` would disable the app's loggers.
"""

from alembic import context
from sqlalchemy import Connection, create_engine
from sqlmodel import SQLModel

from backend.app.core.config import AppSettings
from backend.app.repositories.sql import models  # noqa: F401 - registers the tables


def _run_migrations(connection: Connection) -> None:
    """Run the requested Alembic command on one connection.

    Args:
        connection: The connection to migrate.
    """
    context.configure(
        connection=connection,
        target_metadata=SQLModel.metadata,
        render_as_batch=True,
        transactional_ddl=True,
    )
    with context.begin_transaction():
        context.run_migrations()


app_connection = context.config.attributes.get("connection")
if app_connection is not None:
    _run_migrations(app_connection)
else:
    engine = create_engine(f"sqlite:///{AppSettings.from_env().sqlite_path}")
    with engine.begin() as cli_connection:
        _run_migrations(cli_connection)
