"""JSON repositories must write atomically and keep every record."""

import json
from pathlib import Path

from backend.app.repositories.base import MealFeedbackStore, MealPlanStore, UserProfileStore
from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)


def test_implementations_satisfy_the_protocols(tmp_path: Path) -> None:
    """Runtime-checkable protocols make the seam real, not decorative."""
    assert isinstance(UserProfileRepository(tmp_path), UserProfileStore)
    assert isinstance(MealPlanRepository(tmp_path), MealPlanStore)
    assert isinstance(MealFeedbackRepository(tmp_path), MealFeedbackStore)


def test_meal_plans_are_not_capped_at_200(tmp_path: Path) -> None:
    """The old implementation silently discarded everything past 200."""
    repo = MealPlanRepository(tmp_path)
    for i in range(205):
        repo.save({"request": {"user_id": "u1"}, "n": i})
    stored = json.loads((tmp_path / "meal_history.json").read_text(encoding="utf-8"))
    assert len(stored) == 205


def test_feedback_is_not_capped_at_500(tmp_path: Path) -> None:
    repo = MealFeedbackRepository(tmp_path)
    for i in range(505):
        repo.save({"user_id": "u1", "n": i})
    stored = json.loads((tmp_path / "meal_feedback.json").read_text(encoding="utf-8"))
    assert len(stored) == 505


def test_writes_leave_no_temp_file_behind(tmp_path: Path) -> None:
    repo = MealPlanRepository(tmp_path)
    repo.save({"request": {"user_id": "u1"}})
    assert sorted(p.name for p in tmp_path.iterdir()) == ["meal_history.json"]


def test_a_crash_mid_write_cannot_corrupt_the_store(tmp_path: Path, monkeypatch) -> None:
    """The original wrote in place, so a crash truncated the file."""
    repo = MealPlanRepository(tmp_path)
    repo.save({"request": {"user_id": "u1"}, "n": 0})
    good = (tmp_path / "meal_history.json").read_text(encoding="utf-8")

    def _boom(*args: object, **kwargs: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("os.replace", _boom)
    try:
        repo.save({"request": {"user_id": "u1"}, "n": 1})
    except OSError:
        pass
    # The original file must be intact and still valid JSON.
    assert (tmp_path / "meal_history.json").read_text(encoding="utf-8") == good
    assert len(json.loads(good)) == 1
