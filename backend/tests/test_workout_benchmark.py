"""The workout check runs stated workouts through the real service and measures the overlap."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from backend.app.evaluation.meal_quality import PROFILES, default_scenarios
from backend.app.evaluation.workouts import (
    WORKOUT_CRAVINGS,
    WORKOUTS,
    render_workouts,
    run_workouts,
    workout_scenarios,
)

REPO = Path(__file__).resolve().parents[2]


def test_workout_scenarios_cover_every_profile_and_workout() -> None:
    scenarios = workout_scenarios()

    assert len(scenarios) == len(PROFILES) * len(WORKOUTS) * len(WORKOUT_CRAVINGS) == 144
    assert len({scenario.label for scenario in scenarios}) == 144
    rest = next(scenario for scenario in scenarios if scenario.workout.name == "rest day")
    assert rest.to_request().duration_minutes == 0


def test_the_fixed_set_still_sends_no_workout() -> None:
    """The 72 stay comparable: no workout fields, and labels without one."""
    for scenario in default_scenarios():
        request = scenario.to_request()
        assert request.duration_minutes is None
        assert request.heart_rate_bpm is None
        assert scenario.label.count(" / ") == 1


def test_the_report_puts_each_workout_next_to_the_activity_overlap() -> None:
    rows, days, _ = run_workouts()

    assert len(rows) == 144
    assert len(days) == len(PROFILES) * len(WORKOUTS)
    by_key = {(day.profile, day.workout): day for day in days}
    sedentary_rest = by_key[(PROFILES[0].name, "rest day")]
    assert sedentary_rest.workout_kcal == 0
    assert sedentary_rest.activity_exercise_kcal == 0
    average_rest = by_key[(PROFILES[1].name, "rest day")]
    # BMR 1,790 x (1.55 - 1.2): the exercise a moderate activity level already counts.
    assert average_rest.activity_exercise_kcal == 626.5
    assert average_rest.replaced_budget_kcal == round(1790 * 1.2, 1)
    run_day = by_key[(PROFILES[1].name, "60 min run at 140 bpm")]
    assert run_day.budget_kcal - average_rest.budget_kcal == pytest.approx(
        run_day.workout_kcal, abs=0.1
    )
    assert run_day.warnings
    report = render_workouts(days)
    assert report.startswith("\n## Workout days\n")
    assert "| average man, maintaining (x1.55) | rest day | 0 | 626 | 2774 | 2148 |" in report


def test_script_runs_the_workout_check(tmp_path: Path) -> None:
    output = tmp_path / "workouts.json"
    completed = subprocess.run(
        [sys.executable, "scripts/meal_quality_baseline.py", "--workouts", "--json", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["plans"] == 144
    assert len(payload["workout_days"]) == 24
    assert "guardrails" not in payload
    assert "\n## Workout days\n" in completed.stdout


def test_script_refuses_two_checks_at_once() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/meal_quality_baseline.py", "--wider", "--workouts"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "choose one" in completed.stderr
