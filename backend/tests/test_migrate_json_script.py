"""scripts/migrate_json_to_sqlite.py must be safe to run more than once."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest
from sqlalchemy import Engine

from backend.app.repositories.sql import (
    SqlMealFeedbackRepository,
    SqlMealPlanRepository,
    build_engine,
)

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "migrate_json_to_sqlite.py"
PLAN = {"saved_at": "t1", "request": {"user_id": "u1"}, "request_id": "r1"}
FEEDBACK = {"saved_at": "t1", "user_id": "u1", "saved": True}


@pytest.fixture
def script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("migrate_json_to_sqlite", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    return build_engine(tmp_path / "t.db")


def _write(data_dir: Path, plans: list[dict], feedback: list[dict]) -> None:
    (data_dir / "meal_history.json").write_text(json.dumps(plans), encoding="utf-8")
    (data_dir / "meal_feedback.json").write_text(json.dumps(feedback), encoding="utf-8")


def test_a_second_run_imports_nothing(script: ModuleType, engine: Engine, tmp_path: Path) -> None:
    _write(tmp_path, [PLAN, {**PLAN, "request_id": "r2", "saved_at": "t2"}], [FEEDBACK])

    first = script.import_records(engine, tmp_path)
    second = script.import_records(engine, tmp_path)

    assert first == {"meal plans": (2, 0), "feedback records": (1, 0)}
    assert second == {"meal plans": (0, 2), "feedback records": (0, 1)}
    stored = SqlMealPlanRepository(engine).list_for_user("u1", client_id="local")
    assert [p["request_id"] for p in stored] == ["r2", "r1"]
    assert stored[1]["saved_at"] == "t1"
    feedback = SqlMealFeedbackRepository(engine).list_for_user("u1", client_id="local")
    assert len(feedback) == 1


def test_only_records_added_since_are_imported(
    script: ModuleType, engine: Engine, tmp_path: Path
) -> None:
    _write(tmp_path, [PLAN], [])
    script.import_records(engine, tmp_path)
    _write(tmp_path, [PLAN, {**PLAN, "request_id": "r2", "saved_at": "t2"}], [])

    assert script.import_records(engine, tmp_path)["meal plans"] == (1, 1)


def test_the_same_record_in_another_namespace_is_kept(
    script: ModuleType, engine: Engine, tmp_path: Path
) -> None:
    _write(tmp_path, [PLAN, {**PLAN, "client_id": "app-a"}], [])

    assert script.import_records(engine, tmp_path)["meal plans"] == (2, 0)


def test_a_record_without_a_date_stops_the_import(
    script: ModuleType, engine: Engine, tmp_path: Path
) -> None:
    undated = {key: value for key, value in PLAN.items() if key != "saved_at"}
    _write(tmp_path, [PLAN, undated], [])

    with pytest.raises(ValueError, match="saved_at"):
        script.import_records(engine, tmp_path)

    assert SqlMealPlanRepository(engine).list_for_user("u1", client_id="local") == []


def test_missing_stores_import_nothing(script: ModuleType, engine: Engine, tmp_path: Path) -> None:
    assert script.import_records(engine, tmp_path) == {
        "meal plans": (0, 0),
        "feedback records": (0, 0),
    }
