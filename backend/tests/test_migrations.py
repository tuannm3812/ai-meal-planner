"""Alembic must carry existing data forward, and match the models exactly (DEC-32)."""

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from backend.app.repositories.sql import (
    SqlMealFeedbackRepository,
    SqlMealPlanRepository,
    build_engine,
)
from backend.app.repositories.sql.migrate import MIGRATIONS_DIR, migrate_to_head

HEAD = "0002"
PRE_G4_SCHEMA = """
CREATE TABLE meal_plans (
    id INTEGER NOT NULL, user_id VARCHAR NOT NULL, saved_at VARCHAR NOT NULL,
    payload JSON, PRIMARY KEY (id));
CREATE INDEX ix_meal_plans_user_id ON meal_plans (user_id);
CREATE TABLE meal_feedback (
    id INTEGER NOT NULL, user_id VARCHAR NOT NULL, saved BOOLEAN NOT NULL,
    saved_at VARCHAR NOT NULL, payload JSON, PRIMARY KEY (id));
CREATE INDEX ix_meal_feedback_saved ON meal_feedback (saved);
CREATE INDEX ix_meal_feedback_user_id ON meal_feedback (user_id);
"""


def _config(connection: object) -> Config:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    config.attributes["connection"] = connection
    return config


def _version(path: Path) -> str:
    with sqlite3.connect(path) as connection:
        return connection.execute("SELECT version_num FROM alembic_version").fetchone()[0]


def _tables(path: Path) -> set[str]:
    with sqlite3.connect(path) as connection:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        return {name for (name,) in rows}


def _pre_g4_database(path: Path, plan: str | None = None) -> None:
    """Write the schema Mike's local file really has, holding one plan and one rating."""
    if plan is None:
        plan = json.dumps({"request": {"user_id": "u1"}, "request_id": "old-plan"})
    with sqlite3.connect(path) as connection:
        connection.executescript(PRE_G4_SCHEMA)
        connection.execute(
            "INSERT INTO meal_plans (user_id, saved_at, payload) VALUES ('u1', 't1', ?)", (plan,)
        )
        connection.execute(
            "INSERT INTO meal_feedback (user_id, saved, saved_at, payload) "
            "VALUES ('u1', 1, 't1', ?)",
            (json.dumps({"user_id": "u1", "saved": True, "meal_name": "Old meal"}),),
        )


def test_the_revisions_form_one_line_ending_at_head() -> None:
    script = ScriptDirectory(str(MIGRATIONS_DIR))
    assert script.get_heads() == [HEAD]


def test_a_new_file_reaches_head_and_matches_the_models(tmp_path: Path) -> None:
    """Fails when a model changes without a revision, as the OpenAPI check does for routes."""
    path = tmp_path / "new.db"
    build_engine(path)

    assert _version(path) == HEAD
    engine = create_engine(f"sqlite:///{path}")
    with engine.begin() as connection:
        command.check(_config(connection))


def test_a_pre_g4_database_keeps_its_records(tmp_path: Path) -> None:
    path = tmp_path / "old.db"
    _pre_g4_database(path)

    engine = build_engine(path)

    plans = SqlMealPlanRepository(engine)
    assert [p["request_id"] for p in plans.list_for_user("u1", client_id="local")] == ["old-plan"]
    assert plans.find_by_request_id("old-plan", client_id="local") is not None
    assert plans.list_for_user("u1", client_id="app-a") == []
    feedback = SqlMealFeedbackRepository(engine).list_for_user(
        "u1", saved_only=True, client_id="local"
    )
    assert [f["meal_name"] for f in feedback] == ["Old meal"]
    assert _version(path) == HEAD


def test_a_database_from_create_all_is_stamped_without_change(tmp_path: Path) -> None:
    """The current schema, made before migrations existed, must not be rebuilt."""
    path = tmp_path / "g4.db"
    engine = create_engine(f"sqlite:///{path}")
    SQLModel.metadata.create_all(engine)
    SqlMealPlanRepository(engine).save(
        {"request": {"user_id": "u1"}, "request_id": "r1"}, client_id="app-a"
    )

    migrated = build_engine(path)

    assert _version(path) == HEAD
    stored = SqlMealPlanRepository(migrated).list_for_user("u1", client_id="app-a")
    assert [p["request_id"] for p in stored] == ["r1"]


def test_starting_again_changes_nothing(tmp_path: Path) -> None:
    path = tmp_path / "t.db"
    plans = SqlMealPlanRepository(build_engine(path))
    plans.save({"request": {"user_id": "u1"}, "request_id": "r1"}, client_id="local")

    again = SqlMealPlanRepository(build_engine(path))

    assert len(again.list_for_user("u1", client_id="local")) == 1


def test_a_failed_migration_leaves_the_file_as_it_was(tmp_path: Path) -> None:
    """The stored JSON is unreadable, so 0002 fails after it has already added columns."""
    path = tmp_path / "bad.db"
    _pre_g4_database(path, plan="{not json")

    with pytest.raises(json.JSONDecodeError):
        migrate_to_head(path)

    assert "alembic_version" not in _tables(path)
    with sqlite3.connect(path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(meal_plans)")}
        assert columns == {"id", "user_id", "saved_at", "payload"}
        assert connection.execute("SELECT count(*) FROM meal_plans").fetchone() == (1,)


def test_an_unrecognised_schema_is_refused_untouched(tmp_path: Path) -> None:
    path = tmp_path / "other.db"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE meal_plans (id INTEGER PRIMARY KEY, name TEXT)")

    with pytest.raises(RuntimeError, match=r"other\.db"):
        build_engine(path)

    assert _tables(path) == {"meal_plans"}


def test_a_file_from_a_newer_version_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "newer.db"
    build_engine(path)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE alembic_version SET version_num = '9999'")

    with pytest.raises(RuntimeError, match=r"newer\.db"):
        build_engine(path)


def test_downgrade_and_upgrade_round_trip_keeps_records(tmp_path: Path) -> None:
    path = tmp_path / "t.db"
    _pre_g4_database(path)
    build_engine(path)
    engine = create_engine(f"sqlite:///{path}")

    with engine.begin() as connection:
        command.downgrade(_config(connection), "0001")
    assert _version(path) == "0001"

    plans = SqlMealPlanRepository(build_engine(path))
    assert plans.find_by_request_id("old-plan", client_id="local") is not None


def test_processes_starting_together_migrate_once(tmp_path: Path) -> None:
    """The API and a second instance can open one new file at the same moment."""
    path = tmp_path / "shared.db"
    code = (
        "import sys; from pathlib import Path\n"
        "from backend.app.repositories.sql.migrate import migrate_to_head\n"
        "migrate_to_head(Path(sys.argv[1]))\n"
    )
    processes = [
        subprocess.Popen([sys.executable, "-c", code, str(path)], stderr=subprocess.PIPE)
        for _ in range(4)
    ]

    errors = [process.communicate()[1].decode() for process in processes]

    assert [process.returncode for process in processes] == [0, 0, 0, 0], errors
    assert _version(path) == HEAD
