"""Import existing JSON store records into the SQLite database.

Run once after switching STORAGE_BACKEND to sqlite:

    uv run python scripts/migrate_json_to_sqlite.py

Idempotency is NOT provided: running it twice imports the records twice. Check
the reported counts before re-running.
"""

import json
import sys
from pathlib import Path

from backend.app.core.config import AppSettings
from backend.app.repositories.sql import (
    SqlMealFeedbackRepository,
    SqlMealPlanRepository,
    build_engine,
)


def _load(path: Path) -> list[dict]:
    """Read a JSON store, returning an empty list when it does not exist.

    Args:
        path: Location of the JSON store file.

    Returns:
        The parsed list of records, or an empty list when the file is absent.
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    """Copy JSON records into SQLite and report the counts.

    Returns:
        Process exit code, always ``0``.
    """
    settings = AppSettings.from_env()
    engine = build_engine(settings.sqlite_path)

    plans = _load(settings.data_dir / "meal_history.json")
    feedback = _load(settings.data_dir / "meal_feedback.json")

    plan_repo = SqlMealPlanRepository(engine)
    feedback_repo = SqlMealFeedbackRepository(engine)
    for record in plans:
        plan_repo.save(record)
    for record in feedback:
        feedback_repo.save(record)

    print(f"imported {len(plans)} meal plans and {len(feedback)} feedback records")
    print(f"into {settings.sqlite_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
