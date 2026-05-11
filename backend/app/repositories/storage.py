import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List


class UserProfileRepository:
    def __init__(self, data_dir: Path):
        self.profile_path = data_dir / "user_profiles.json"

    def fetch_user_profile(self, user_id: str) -> Dict[str, Any]:
        profiles = self._load_profiles()
        return profiles.get(user_id, profiles["default"])

    def _load_profiles(self) -> Dict[str, Dict[str, Any]]:
        if not self.profile_path.exists():
            return self._default_profiles()

        with self.profile_path.open("r", encoding="utf-8") as profile_file:
            profiles = json.load(profile_file)

        profiles.setdefault("default", self._default_profiles()["default"])
        return profiles

    @staticmethod
    def _default_profiles() -> Dict[str, Dict[str, Any]]:
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

    def save(self, payload: Dict[str, Any]) -> None:
        record = {
            "saved_at": datetime.now(UTC).isoformat(),
            **payload,
        }

        with self._lock:
            records = self._load_records()
            records.append(record)
            with self.history_path.open("w", encoding="utf-8") as history_file:
                json.dump(records[-200:], history_file, indent=2)

    def list_for_user(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        records = self._load_records()
        user_records = [
            record for record in records if record.get("request", {}).get("user_id") == user_id
        ]
        return list(reversed(user_records[-limit:]))

    def _load_records(self) -> List[Dict[str, Any]]:
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

    def save(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "saved_at": datetime.now(UTC).isoformat(),
            **payload,
        }

        with self._lock:
            records = self._load_records()
            records.append(record)
            with self.feedback_path.open("w", encoding="utf-8") as feedback_file:
                json.dump(records[-500:], feedback_file, indent=2)
        return record

    def list_for_user(
        self,
        user_id: str,
        limit: int = 20,
        saved_only: bool = False,
    ) -> List[Dict[str, Any]]:
        records = self._load_records()
        user_records = [
            record for record in records if record.get("user_id") == user_id
        ]
        if saved_only:
            user_records = [record for record in user_records if record.get("saved")]
        return list(reversed(user_records[-limit:]))

    def _load_records(self) -> List[Dict[str, Any]]:
        if not self.feedback_path.exists():
            return []

        with self.feedback_path.open("r", encoding="utf-8") as feedback_file:
            return json.load(feedback_file)
