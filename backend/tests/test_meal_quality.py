"""The meal-quality baseline measures what the real service ships.

These pin the measurement, not the planner's current numbers: a meal-quality
change is meant to move the baseline, so no test fails because it did.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureResponse
from backend.app.evaluation.meal_quality import (
    PROFILES,
    PlanQuality,
    Scenario,
    default_scenarios,
    in_amdr,
    macro_percentages,
    measure,
    render_markdown,
    run,
    summarise,
)
from backend.app.services.meal_planning_service import MealPlanResult

REPO = Path(__file__).resolve().parents[2]


def test_macro_percentages_weight_fat_at_nine_kcal_per_gram() -> None:
    # 25 g protein = 100 kcal, 25 g carbs = 100 kcal, 22.2 g fat = 200 kcal.
    assert macro_percentages(25, 25, 200 / 9) == {"protein": 25.0, "carbs": 25.0, "fat": 50.0}


def test_macro_percentages_of_nothing_are_zero() -> None:
    assert macro_percentages(0, 0, 0) == {"protein": 0.0, "carbs": 0.0, "fat": 0.0}


def test_amdr_bounds_are_inclusive() -> None:
    assert in_amdr({"protein": 35.0, "carbs": 45.0, "fat": 20.0}) == {
        "protein": True,
        "carbs": True,
        "fat": True,
    }
    assert in_amdr({"protein": 35.1, "carbs": 44.9, "fat": 35.1}) == {
        "protein": False,
        "carbs": False,
        "fat": False,
    }


def test_default_scenarios_are_fixed_and_distinct() -> None:
    scenarios = default_scenarios()

    assert len(scenarios) == 72
    assert len({scenario.label for scenario in scenarios}) == 72
    assert scenarios == default_scenarios()


def test_an_infeasible_result_keeps_only_its_status_and_budget() -> None:
    result = MealPlanResult(
        plan_status="infeasible",
        calorie_budget=CalorieExpenditureResponse(
            estimated_daily_expenditure_kcal=2400,
            meal_calorie_budget_kcal=2000,
            model_version="test",
            confidence=0.9,
        ),
        infeasible_reason="nothing safe",
    )

    quality = measure(Scenario("anything", PROFILES[0]), result)

    assert quality.plan_status == "infeasible"
    assert quality.daily_budget_kcal == 2000
    assert quality.verified_kcal is None
    assert quality.macro_percent is None


def test_measure_reads_the_shipped_plan() -> None:
    """Deviation is measured on the verified total that ships, against the meal target."""
    (quality,) = run([Scenario("chicken fried rice", PROFILES[1])])

    assert quality.plan_status == "matched"
    assert quality.meal_name == "Chicken Fried Rice"
    assert quality.target_meal_kcal is not None
    assert quality.calorie_deviation == pytest.approx(
        abs(quality.verified_kcal - quality.target_meal_kcal) / quality.target_meal_kcal,
        abs=1e-3,
    )
    assert sum(quality.macro_percent.values()) == pytest.approx(100, abs=0.2)
    assert set(quality.macros_in_range) == {"protein", "carbs", "fat"}


def test_summary_counts_and_report() -> None:
    rows = [
        PlanQuality(
            scenario="a",
            plan_status="matched",
            meal_name="A",
            daily_budget_kcal=2000,
            target_meal_kcal=560,
            verified_kcal=560,
            calorie_deviation=0.0,
            within_tolerance=True,
            rescaled=False,
            scale_factor=1.0,
            scale_clamped=False,
            protein_g=30,
            macro_percent={"protein": 20.0, "carbs": 50.0, "fat": 30.0},
            macros_in_range={"protein": True, "carbs": True, "fat": True},
            estimated_ingredients=0,
            retrieval_score=0.2,
        ),
        PlanQuality(
            scenario="b",
            plan_status="matched",
            meal_name="B",
            daily_budget_kcal=3000,
            target_meal_kcal=840,
            verified_kcal=1008,
            calorie_deviation=0.2,
            within_tolerance=False,
            rescaled=True,
            scale_factor=1.6,
            scale_clamped=True,
            protein_g=80,
            macro_percent={"protein": 40.0, "carbs": 40.0, "fat": 20.0},
            macros_in_range={"protein": False, "carbs": False, "fat": True},
            estimated_ingredients=2,
            retrieval_score=0.9,
        ),
        PlanQuality(scenario="c", plan_status="infeasible", daily_budget_kcal=1500),
    ]

    summary = summarise(rows)

    assert summary.plans == 3
    assert summary.status_counts == {"matched": 2, "infeasible": 1}
    assert (summary.scaled_plans, summary.within_tolerance) == (2, 1)
    assert summary.median_deviation == pytest.approx(0.1)
    assert summary.max_deviation == 0.2
    assert (summary.rescaled, summary.scale_clamped) == (1, 1)
    assert summary.macros_in_range == {"protein": 1, "carbs": 1, "fat": 2}
    assert summary.all_macros_in_range == 1
    assert summary.with_estimated_ingredients == 1
    assert summary.weak_matches == 1
    assert summary.daily_budget_kcal == {"min": 1500, "max": 3000}

    report = render_markdown(rows, summary)
    assert "- Plans: 3 (infeasible 1, matched 2)." in report
    assert "all three 1 of 2." in report
    assert "| b | matched | B | 840 | 1008.0 | 20.0% | 1.6 | 40/40/20 | 0.9 |" in report


def test_script_prints_the_report_and_writes_json(tmp_path: Path) -> None:
    output = tmp_path / "baseline.json"
    completed = subprocess.run(
        [sys.executable, "scripts/meal_quality_baseline.py", "--json", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )

    assert completed.stdout.startswith("## Summary\n")
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["plans"] == 72
    assert len(payload["plans"]) == 72
