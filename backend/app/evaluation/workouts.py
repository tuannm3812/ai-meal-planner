"""Run the meal-quality benchmark across realistic workouts, and measure the activity overlap.

Since DEC-33 a meal request can state today's workout, but the fixed 72 plans
send none, so every one assumes the model's default (30 minutes at 100 bpm).
This check sends six workouts, from a rest day to a 90-minute ride, for each
baseline profile on six matched cravings: 144 plans, reported apart from the 72
so the baseline stays comparable.

It also measures a known gap. The activity levels are described as exercise
days in a usual week ("moderately active: exercise 3-5 days a week"), so
BMR times the multiplier already holds an average day's exercise, and the
service then adds today's workout on top. The report shows both numbers side
by side, and the budget the day would get if today's workout replaced the
activity level's exercise (BMR times the sedentary 1.2, plus the workout).

Run it with ``scripts/meal_quality_baseline.py --workouts``.
"""

import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.agents.calorie_expenditure_agent import (
    CalorieExpenditureAgent,
    CalorieExpenditureRequest,
)
from backend.app.evaluation.meal_quality import (
    CRAVINGS,
    PROFILES,
    BenchmarkConfig,
    PlanQuality,
    Profile,
    Scenario,
    Workout,
    build_service,
    measure,
)

SEDENTARY_MULTIPLIER = 1.2
"""The activity level that counts no exercise; the clients' lowest option."""

WORKOUTS = (
    Workout("workout not given"),
    Workout("rest day", 0),
    Workout("20 min walk at 95 bpm", 20, 95),
    Workout("30 min jog at 120 bpm", 30, 120),
    Workout("60 min run at 140 bpm", 60, 140),
    Workout("90 min ride at 135 bpm", 90, 135),
)
"""From no exercise to a long session. The first sends nothing, like the fixed 72."""

WORKOUT_CRAVINGS = CRAVINGS[:6]
"""Six cravings the corpus matches, so the plans measure budgets, not fallbacks."""


def workout_scenarios() -> list[Scenario]:
    """Return every workout for every baseline profile on six matched cravings.

    Returns:
        144 scenarios, grouped by profile, then workout, then craving.
    """
    return [
        Scenario(craving, profile, workout=workout)
        for profile in PROFILES
        for workout in WORKOUTS
        for craving in WORKOUT_CRAVINGS
    ]


@dataclass(frozen=True)
class DayBudget:
    """One profile on one workout day: what the service budgeted, and the overlap."""

    profile: str
    workout: str
    activity_multiplier: float
    expenditure_kcal: float
    budget_kcal: float
    workout_kcal: float
    activity_exercise_kcal: float
    """BMR times (multiplier - 1.2): the exercise the activity level already counts."""
    replaced_budget_kcal: float
    """The budget if today's workout replaced the activity level's exercise."""
    warnings: tuple[str, ...]
    plans: int
    meets_targets: int


def _day_budget(
    profile: Profile, workout: Workout, result: Any, rows: Sequence[PlanQuality]
) -> DayBudget:
    """Summarise one profile-workout group from its first result and all its rows."""
    budget = result.calorie_budget
    workout_kcal = budget.exercise.kcal if budget.exercise else 0.0
    sedentary = CalorieExpenditureRequest(
        age=profile.age,
        sex=profile.sex,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_multiplier=SEDENTARY_MULTIPLIER,
    )
    bmr = CalorieExpenditureAgent._estimate_with_bmr(sedentary) / SEDENTARY_MULTIPLIER
    replaced, _ = CalorieExpenditureAgent._meal_budget(
        bmr * SEDENTARY_MULTIPLIER + workout_kcal, profile.goal, profile.sex
    )
    return DayBudget(
        profile=profile.name,
        workout=workout.name,
        activity_multiplier=profile.activity_multiplier,
        expenditure_kcal=budget.estimated_daily_expenditure_kcal,
        budget_kcal=budget.meal_calorie_budget_kcal,
        workout_kcal=workout_kcal,
        activity_exercise_kcal=round(bmr * (profile.activity_multiplier - SEDENTARY_MULTIPLIER), 1),
        replaced_budget_kcal=round(replaced, 1),
        warnings=tuple(
            warning
            for warning in budget.warnings
            if "training range" in warning or "bpm" in warning
        ),
        plans=len(rows),
        meets_targets=sum(1 for row in rows if row.meets_targets),
    )


def run_workouts(
    config: BenchmarkConfig | None = None,
) -> tuple[list[PlanQuality], list[DayBudget], dict[str, Any]]:
    """Run the workout check through a freshly built offline service.

    Args:
        config: The artifacts to measure; the canonical baseline when omitted.

    Returns:
        One PlanQuality per scenario, one DayBudget per profile and workout,
        and the run's provenance.
    """
    rows: list[PlanQuality] = []
    days: list[DayBudget] = []
    with tempfile.TemporaryDirectory() as data_dir:
        service, provenance = build_service(Path(data_dir), config)
        for profile in PROFILES:
            for workout in WORKOUTS:
                scenarios = [
                    Scenario(craving, profile, workout=workout) for craving in WORKOUT_CRAVINGS
                ]
                results = [service.generate(scenario.to_request()) for scenario in scenarios]
                group = [
                    measure(scenario, result)
                    for scenario, result in zip(scenarios, results, strict=True)
                ]
                rows.extend(group)
                days.append(_day_budget(profile, workout, results[0], group))
    return rows, days, provenance


def render_workouts(days: Sequence[DayBudget]) -> str:
    """Render the per-day budgets and the activity overlap as a Markdown section.

    Args:
        days: What ``run_workouts`` returned, one per profile and workout.

    Returns:
        The section, ending in a newline.
    """
    plans = sum(day.plans for day in days)
    met = sum(day.meets_targets for day in days)
    stated = [day for day in days if day.workout_kcal > 0 and day.activity_exercise_kcal > 0]
    lines = [
        "",
        "## Workout days",
        "",
        f"{len(WORKOUTS)} workouts for each of the {len(PROFILES)} profiles, on "
        f"{len(WORKOUT_CRAVINGS)} matched cravings each. **Meeting the targets: {met} of "
        f"{plans}.**",
        "",
        '"Activity level counts" is BMR times (multiplier - 1.2): the exercise the '
        "activity level already holds for an average day. The service adds today's "
        'workout on top of it. "If replaced" is the budget when today\'s workout '
        "replaces that exercise instead.",
        "",
        f"On {len(stated)} of the {len(days)} days, both a workout and an activity level "
        "above sedentary count exercise.",
        "",
        "| Profile | Workout | Workout kcal | Activity level counts | Budget | If replaced "
        "| Meets targets |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for day in days:
        lines.append(
            f"| {day.profile} (x{day.activity_multiplier}) | {day.workout} "
            f"| {day.workout_kcal:.0f} | {day.activity_exercise_kcal:.0f} "
            f"| {day.budget_kcal:.0f} | {day.replaced_budget_kcal:.0f} "
            f"| {day.meets_targets} of {day.plans} |"
        )
    flagged = sorted({warning for day in days for warning in day.warnings})
    if flagged:
        lines += ["", "Model-range warnings these days raised:", ""]
        lines += [f"- {warning}" for warning in flagged]
    return "\n".join(lines) + "\n"
