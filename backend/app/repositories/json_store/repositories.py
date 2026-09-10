"""JSON file-backed implementations of the storage protocols."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from typing import Any

from ..base import owner_of_meal_plan


def _write_json_atomically(path: Path, records: list[dict[str, Any]]) -> None:
    """Write records to path so a crash cannot leave a truncated file.

    Writes to a temporary file in the same directory, then renames it over the
    target. ``os.replace`` is atomic on POSIX and Windows, so a reader either
    sees the old file or the new one, never a partial write.

    Args:
        path: Destination file.
        records: Records to serialise.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        json.dump(records, handle, indent=2)
        temp_name = handle.name
    try:
        os.replace(temp_name, path)
    except OSError:
        Path(temp_name).unlink(missing_ok=True)
        raise


class UserProfileRepository:
    def __init__(self, data_dir: Path):
        self.profile_path = data_dir / "user_profiles.json"

    def fetch_user_profile(self, user_id: str) -> dict[str, Any]:
        profiles = self._load_profiles()
        return profiles.get(user_id, profiles["default"])

    def _load_profiles(self) -> dict[str, dict[str, Any]]:
        if not self.profile_path.exists():
            return self._default_profiles()

        with self.profile_path.open("r", encoding="utf-8") as profile_file:
            profiles = json.load(profile_file)

        profiles.setdefault("default", self._default_profiles()["default"])
        return profiles

    @staticmethod
    def _default_profiles() -> dict[str, dict[str, Any]]:
        return {
            "default": {
                "age": 28,
                "gender": "m",
                "weight": 80.0,
                "height": 180.0,
                "workout_level": 1.55,
                "dietary_restrictions": ["dairy-free", "high-protein"],
            }
        }


class MealPlanRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.history_path = data_dir / "meal_history.json"
        self._lock = Lock()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict[str, Any]) -> None:
        record = {
            "saved_at": datetime.now(UTC).isoformat(),
            **payload,
        }

        with self._lock:
            records = self._load_records()
            records.append(record)
            _write_json_atomically(self.history_path, records)

    def list_for_user(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        records = self._load_records()
        user_records = [record for record in records if owner_of_meal_plan(record) == user_id]
        return list(reversed(user_records[-limit:]))

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []

        with self.history_path.open("r", encoding="utf-8") as history_file:
            return json.load(history_file)


class MealFeedbackRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.feedback_path = data_dir / "meal_feedback.json"
        self._lock = Lock()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "saved_at": datetime.now(UTC).isoformat(),
            **payload,
        }

        with self._lock:
            records = self._load_records()
            records.append(record)
            _write_json_atomically(self.feedback_path, records)
        return record

    def list_for_user(
        self,
        user_id: str,
        limit: int = 20,
        saved_only: bool = False,
    ) -> list[dict[str, Any]]:
        records = self._load_records()
        user_records = [record for record in records if record.get("user_id") == user_id]
        if saved_only:
            user_records = [record for record in user_records if record.get("saved")]
        return list(reversed(user_records[-limit:]))

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.feedback_path.exists():
            return []

        with self.feedback_path.open("r", encoding="utf-8") as feedback_file:
            return json.load(feedback_file)
