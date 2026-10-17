"""The meal-quality baseline measures what the real service ships.

These pin the measurement, not the planner's current numbers: a meal-quality
change is meant to move the baseline, so no test fails because it did.
"""

import dataclasses
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureResponse
from backend.app.evaluation import meal_quality
from backend.app.evaluation.meal_quality import (
    GUARDRAIL_CORPUS,
    PROFILES,
    BenchmarkConfig,
    BenchmarkConfigurationError,
    Guardrail,
    GuardrailResult,
    PlanQuality,
    Scenario,
    build_service,
    calorie_deviation,
    default_scenarios,
    guardrail_scenarios,
    in_amdr,
    macro_percentages,
    measure,
    render_guardrails,
    render_markdown,
    run,
    run_guardrails,
    summarise,
)
from backend.app.rag.meal_corpus import load_meal_corpus
from backend.app.rag.rules import constraint_groups, meal_is_allowed
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
    (quality,), provenance = run([Scenario("chicken fried rice", PROFILES[1])])

    assert provenance["retriever"] == "tfidf_vector_retriever_v0.1"
    assert provenance["meal_count"] == 34

    assert quality.plan_status == "matched"
    assert quality.meal_name == "Chicken Fried Rice"
    assert quality.target_meal_kcal is not None
    assert quality.calorie_deviation == pytest.approx(
        abs(quality.verified_kcal - quality.target_meal_kcal) / quality.target_meal_kcal,
        abs=1e-3,
    )
    assert sum(quality.macro_percent.values()) == pytest.approx(100, abs=0.2)
    assert set(quality.macros_in_range) == {"protein", "carbs", "fat"}
    assert quality.meets_targets == (
        quality.calorie_deviation <= 0.10 and all(quality.macros_in_range.values())
    )


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
            within_calorie_target=True,
            meets_targets=True,
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
            within_calorie_target=False,
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
    assert (summary.within_calorie_target, summary.meets_targets) == (1, 1)
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
    assert "**Meeting the targets** (calories within 10%, all macros in AMDR): 1 of 3." in report
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

    assert completed.stdout.startswith("## Measured\n")
    assert "\n## Summary\n" in completed.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["summary"]["plans"] == 72
    assert payload["provenance"]["calorie_model_version"] == "hist_gradient_boosting_deep_v0.1.0"
    assert len(payload["plans"]) == 72
    assert [result["as_expected"] for result in payload["guardrails"]] == [True] * 5
    assert "\n## Guardrails\n" in completed.stdout


# Codex, 2026-10-18: rounding must not decide pass or fail at a boundary.


def test_macro_shares_just_outside_every_range_are_not_rounded_into_it() -> None:
    # Energy 35.04 / 44.98 / 19.98 kcal: protein just over 35%, carbs and fat just under.
    shares = macro_percentages(35.04 / 4, 44.98 / 4, 19.98 / 9)

    assert shares["protein"] == pytest.approx(35.04)
    assert in_amdr(shares) == {"protein": False, "carbs": False, "fat": False}


def test_calorie_target_is_inclusive_and_unrounded() -> None:
    assert calorie_deviation(549.9, 500) <= 0.10  # just inside
    assert calorie_deviation(550, 500) <= 0.10  # exactly on the bound
    assert calorie_deviation(500 * 1.10004, 500) > 0.10  # just outside, 0.1000 when rounded


def test_summary_counts_the_per_plan_calorie_verdict() -> None:
    """A plan just outside the calorie target counts as outside in the aggregate too."""
    row = PlanQuality(
        scenario="edge",
        plan_status="matched",
        daily_budget_kcal=2000,
        target_meal_kcal=500,
        calorie_deviation=calorie_deviation(500 * 1.10004, 500),
        within_tolerance=True,
        within_calorie_target=False,
        meets_targets=False,
        macro_percent={"protein": 20.0, "carbs": 50.0, "fat": 30.0},
        macros_in_range={"protein": True, "carbs": True, "fat": True},
    )

    summary = summarise([row])

    assert (summary.within_calorie_target, summary.meets_targets) == (0, 0)


# Codex, 2026-10-18: the caller's shell must not change what the baseline measures.

_HOSTILE_ENV = {
    "CALORIE_MODEL_PATH": "/nonexistent/model.joblib",
    "CALORIE_MODEL_VERSION": "not_the_shipped_model",
    "MEAL_CORPUS_PATH": "/nonexistent/meals.json",
    "RAG_BACKEND": "sentence-transformers",
    "RAG_EMBEDDING_ACTIVATION_SIZE": "1",
}


def test_canonical_config_ignores_the_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    clean = BenchmarkConfig.canonical()
    for name, value in _HOSTILE_ENV.items():
        monkeypatch.setenv(name, value)

    assert BenchmarkConfig.canonical() == clean
    assert clean.calorie_model_path.exists() and clean.meal_corpus_path.exists()


def test_script_output_is_unchanged_by_shell_settings(tmp_path: Path) -> None:
    def run_script(env: dict[str, str]) -> str:
        return subprocess.run(
            [sys.executable, "scripts/meal_quality_baseline.py"],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    base_env = {key: value for key, value in os.environ.items() if key not in _HOSTILE_ENV}

    assert run_script({**base_env, **_HOSTILE_ENV}) == run_script(base_env)


@pytest.mark.parametrize(
    ("field", "message"),
    [("calorie_model_path", "Calorie model"), ("meal_corpus_path", "Meal corpus")],
)
def test_a_missing_artifact_stops_the_run(tmp_path: Path, field: str, message: str) -> None:
    """A missing artifact must not quietly become a rule-based budget or template meals."""
    config = dataclasses.replace(BenchmarkConfig.canonical(), **{field: tmp_path / "missing"})

    with pytest.raises(BenchmarkConfigurationError, match=message):
        build_service(tmp_path, config)


# Codex, 2026-10-18: exercise the fallback and refusal paths, reported apart
# from the default set so its denominator stays comparable.


def test_the_guardrail_corpus_has_no_meal_a_vegan_can_eat() -> None:
    """The fallback and refusal guardrails rest on this, so it is pinned."""
    groups = constraint_groups(["vegan"])

    assert not [
        meal for meal in load_meal_corpus(GUARDRAIL_CORPUS) if meal_is_allowed(meal, groups, [])
    ]


def test_guardrails_cover_every_plan_status() -> None:
    guardrails = guardrail_scenarios()

    assert {guardrail.expected_status for guardrail in guardrails} == {
        "matched",
        "fallback",
        "infeasible",
    }
    assert len({guardrail.scenario.label for guardrail in guardrails}) == len(guardrails)


def test_every_guardrail_holds() -> None:
    results = run_guardrails()

    assert [(r.plan_status, r.meal_name) for r in results] == [
        (g.expected_status, g.expected_meal) for g in guardrail_scenarios()
    ]
    assert all(result.as_expected for result in results)


def test_guardrails_ignore_the_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    """The controlled corpus replaces whatever MEAL_CORPUS_PATH says."""
    for name, value in _HOSTILE_ENV.items():
        monkeypatch.setenv(name, value)

    assert all(result.as_expected for result in run_guardrails())


def test_a_broken_guardrail_is_reported_and_fails_the_script(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    wrong = Guardrail(Scenario("steak and rice", PROFILES[1]), "infeasible", None)
    monkeypatch.setattr(meal_quality, "guardrail_scenarios", lambda: [wrong])
    spec = importlib.util.spec_from_file_location(
        "meal_quality_baseline", REPO / "scripts" / "meal_quality_baseline.py"
    )
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    assert script.main([]) == 1
    captured = capsys.readouterr()
    assert "| steak and rice / average man, maintaining | infeasible | matched " in captured.out
    assert "| **no** |" in captured.out
    assert "Guardrails not as expected: steak and rice" in captured.err


def test_render_guardrails_counts_the_outcomes() -> None:
    results = [
        GuardrailResult(
            scenario="a",
            expected_status="fallback",
            expected_meal="A",
            plan_status="fallback",
            meal_name="A",
            as_expected=True,
        ),
        GuardrailResult(
            scenario="b",
            expected_status="infeasible",
            expected_meal=None,
            plan_status="matched",
            meal_name="B",
            as_expected=False,
        ),
    ]

    assert "As expected: 1 of 2." in render_guardrails(results)
