"""Import existing JSON store records into the SQLite database.

Run after switching STORAGE_BACKEND to sqlite:

    uv run python scripts/migrate_json_to_sqlite.py

Safe to run again: a record the database already holds is skipped, so an
interrupted import can simply be restarted.
"""

import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlmodel import Session, select

from backend.app.core.config import AppSettings
from backend.app.repositories.base import client_of
from backend.app.repositories.sql import (
    SqlMealFeedbackRepository,
    SqlMealPlanRepository,
    build_engine,
)
from backend.app.repositories.sql.models import MealFeedbackRow, MealPlanRow


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


def _fingerprint(client_id: str, record: dict[str, Any]) -> str:
    """Identify a record's content within its client namespace.

    ``client_id`` is set aside because rows stored before G4 lack it in the payload.

    Args:
        client_id: The namespace the record belongs to.
        record: A stored or about-to-be-imported record.

    Returns:
        A string equal for the same record, wherever it was read from.
    """
    content = {key: value for key, value in record.items() if key != "client_id"}
    return json.dumps([client_id, content], sort_keys=True)


def _stored_fingerprints(engine: Engine, row_type: type[MealPlanRow | MealFeedbackRow]) -> set[str]:
    """Fingerprint every record of one kind already in the database.

    Args:
        engine: The SQLite engine.
        row_type: The table to read.

    Returns:
        The fingerprints of the stored records.
    """
    with Session(engine) as session:
        rows = session.exec(select(row_type)).all()
    return {_fingerprint(row.client_id, row.payload) for row in rows}


def _import(records: list[dict], repository: Any, stored: set[str]) -> int:
    """Save the records the database does not hold yet, in file order.

    Args:
        records: Records read from a JSON store.
        repository: The SQL repository to save into.
        stored: Fingerprints already present; extended as records are saved.

    Returns:
        How many records were saved.

    Raises:
        ValueError: If a record has no ``saved_at``, before anything is saved.
            The timestamp would be invented on import, so the record could
            never be recognised again.
    """
    undated = sum("saved_at" not in record for record in records)
    if undated:
        raise ValueError(f"{undated} records have no saved_at; the JSON store always writes one")
    imported = 0
    # Records written before G4 carry no client_id and keep the "local" namespace.
    for record in records:
        client_id = client_of(record)
        fingerprint = _fingerprint(client_id, record)
        if fingerprint not in stored:
            repository.save(record, client_id=client_id)
            stored.add(fingerprint)
            imported += 1
    return imported


def import_records(engine: Engine, data_dir: Path) -> dict[str, tuple[int, int]]:
    """Copy JSON records that are not yet in the database.

    Args:
        engine: The SQLite engine.
        data_dir: Directory holding the JSON stores.

    Returns:
        For each store, how many records were imported and how many were skipped.
    """
    stores = {
        "meal plans": ("meal_history.json", SqlMealPlanRepository, MealPlanRow),
        "feedback records": ("meal_feedback.json", SqlMealFeedbackRepository, MealFeedbackRow),
    }
    counts = {}
    for label, (filename, repository_type, row_type) in stores.items():
        records = _load(data_dir / filename)
        stored = _stored_fingerprints(engine, row_type)
        imported = _import(records, repository_type(engine), stored)
        counts[label] = (imported, len(records) - imported)
    return counts


def main() -> int:
    """Copy JSON records into SQLite and report the counts.

    Returns:
        Process exit code, always ``0``.
    """
    settings = AppSettings.from_env()
    engine = build_engine(settings.sqlite_path)
    for label, (imported, skipped) in import_records(engine, settings.data_dir).items():
        print(f"{label}: imported {imported}, already present {skipped}")
    print(f"into {settings.sqlite_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
