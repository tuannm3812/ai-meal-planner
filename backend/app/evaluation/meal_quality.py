"""Measure how well generated plans hit their calorie target and a balanced macro split.

The meal-quality milestone (owner decision, 2026-10-14) needs a baseline that
every later change is judged against. This module runs a fixed scenario set
through the real ``MealPlanningService`` and reports, per plan and in
aggregate:

- whether a corpus meal, a fallback template or nothing was served;
- the shipped calorie total against the meal's calorie target;
- the macro split, as each macro's share of the meal's calories, against a
  reference range.

The service has no macro targets of its own, so the split is checked against
the Acceptable Macronutrient Distribution Ranges (AMDR) for adults: protein
10-35%, carbohydrate 45-65% and fat 20-35% of energy. They are a daily
reference applied to one meal, so they read as "is this meal balanced", not
as a hard rule.

Every run is offline and deterministic: no Gemini key, no USDA or FatSecret
credentials, and an empty profile store, so a request's stored profile is the
built-in default. Run it with ``scripts/meal_quality_baseline.py``.
"""

import statistics
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from backend.app.agents.calorie_expenditure_agent import CalorieExpenditureAgent
from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.agents.supermarket_agent import SupermarketAgent
from backend.app.core.config import AppSettings
from backend.app.core.portions import MAX_SCALE, MIN_SCALE
from backend.app.repositories.json_store import UserProfileRepository
from backend.app.schemas.requests import MealRequest
from backend.app.services.meal_planning_service import (
    DEFAULT_TOLERANCE,
    MealPlanningService,
    MealPlanResult,
)

AMDR_PERCENT = {"protein": (10.0, 35.0), "carbs": (45.0, 65.0), "fat": (20.0, 35.0)}
"""Adult AMDR, as a percentage of energy: macro -> (low, high)."""

KCAL_PER_GRAM = {"protein": 4.0, "carbs": 4.0, "fat": 9.0}

WEAK_MATCH_SCORE = 0.25
"""A corpus match scoring below this is reported as weak. The retriever's own
threshold (0.16) decides corpus versus fallback; this one only flags matches
worth a look, and is a reporting choice, not a rule the service applies."""


@dataclass(frozen=True)
class Profile:
    """Biometrics sent with a request, so the calorie budget does not hang on a stored profile."""

    name: str
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    activity_multiplier: float
    goal: str


@dataclass(frozen=True)
class Scenario:
    """One request in the fixed set."""

    craving: str
    profile: Profile
    health_conditions: tuple[str, ...] = ()
    dietary_preferences: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        """A stable, human-readable id for the scenario."""
        constraints = [*self.dietary_preferences, *self.health_conditions]
        suffix = f" [{', '.join(constraints)}]" if constraints else ""
        return f"{self.craving} / {self.profile.name}{suffix}"

    def to_request(self) -> MealRequest:
        """Build the API request this scenario stands for."""
        return MealRequest(
            craving=self.craving,
            health_conditions=list(self.health_conditions),
            dietary_preferences=list(self.dietary_preferences),
            age=self.profile.age,
            sex=self.profile.sex,
            height_cm=self.profile.height_cm,
            weight_kg=self.profile.weight_kg,
            activity_multiplier=self.profile.activity_multiplier,
            goal=self.profile.goal,
        )


PROFILES = (
    Profile("older sedentary woman, losing", 62, "female", 158, 52, 1.2, "lose"),
    Profile("average man, maintaining", 28, "male", 180, 80, 1.55, "maintain"),
    Profile("active woman, maintaining", 34, "female", 168, 64, 1.725, "maintain"),
    Profile("large athlete, gaining", 24, "male", 193, 110, 1.9, "gain"),
)

CRAVINGS = (
    "chicken fried rice",
    "high-protein burger",
    "creamy pasta",
    "salmon dinner",
    "steak and rice",
    "spicy curry",
    "breakfast oats",
    "taco bowl",
    "light soup",
    "sushi",
    "pizza",
    "chocolate dessert",
)
"""A spread of cravings: most have a close corpus meal, and the last three do not."""

CONSTRAINED = (
    ((), ("vegan",)),
    (("hypertension",), ()),
    (("kidney disease",), ()),
    (("celiac",), ()),
)
"""(health_conditions, dietary_preferences) pairs, each run on six cravings."""


def default_scenarios() -> list[Scenario]:
    """Return the fixed scenario set: every craving for every profile, plus constraints.

    Returns:
        48 unconstrained scenarios (12 cravings x 4 profiles) followed by 24
        constrained ones (6 cravings x 4 constraint sets, average profile).
    """
    scenarios = [Scenario(craving, profile) for profile in PROFILES for craving in CRAVINGS]
    average = PROFILES[1]
    for conditions, preferences in CONSTRAINED:
        scenarios.extend(
            Scenario(craving, average, conditions, preferences) for craving in CRAVINGS[:6]
        )
    return scenarios


class PlanQuality(BaseModel):
    """What one scenario produced, reduced to the numbers the baseline tracks."""

    scenario: str
    plan_status: str
    meal_name: str | None = None
    daily_budget_kcal: float
    target_meal_kcal: int | None = None
    verified_kcal: float | None = None
    calorie_deviation: float | None = None
    within_tolerance: bool | None = None
    rescaled: bool | None = None
    scale_factor: float | None = None
    scale_clamped: bool | None = None
    protein_g: float | None = None
    macro_percent: dict[str, float] | None = None
    macros_in_range: dict[str, bool] | None = None
    estimated_ingredients: int | None = None
    retrieval_score: float | None = None


def macro_percentages(protein_g: float, carbs_g: float, fat_g: float) -> dict[str, float]:
    """Each macro's share of the calories the three macros supply.

    Args:
        protein_g: Grams of protein.
        carbs_g: Grams of carbohydrate.
        fat_g: Grams of fat.

    Returns:
        Percentages keyed by macro, rounded to one place; all zero when the
        macros supply no energy.
    """
    energy = {
        "protein": protein_g * KCAL_PER_GRAM["protein"],
        "carbs": carbs_g * KCAL_PER_GRAM["carbs"],
        "fat": fat_g * KCAL_PER_GRAM["fat"],
    }
    total = sum(energy.values())
    if total <= 0:
        return {macro: 0.0 for macro in energy}
    return {macro: round(100 * kcal / total, 1) for macro, kcal in energy.items()}


def in_amdr(percentages: dict[str, float]) -> dict[str, bool]:
    """Whether each macro's share falls inside its AMDR range, inclusive."""
    return {
        macro: AMDR_PERCENT[macro][0] <= percentages[macro] <= AMDR_PERCENT[macro][1]
        for macro in AMDR_PERCENT
    }


def measure(scenario: Scenario, result: MealPlanResult) -> PlanQuality:
    """Reduce one service result to its quality numbers.

    The calorie deviation is measured on what ships: after reconciliation when
    it ran, otherwise the first verified total.

    Args:
        scenario: The scenario that produced the result.
        result: The service's answer.

    Returns:
        The scenario's PlanQuality.
    """
    quality = PlanQuality(
        scenario=scenario.label,
        plan_status=result.plan_status,
        daily_budget_kcal=round(result.calorie_budget.meal_calorie_budget_kcal, 1),
    )
    if result.meal_plan is None or result.nutrition is None:
        return quality

    nutrition = result.nutrition
    percentages = macro_percentages(
        nutrition.total_protein, nutrition.total_carbs, nutrition.total_fat
    )
    quality.meal_name = result.meal_plan.meal_definition.structured_meal_name
    quality.verified_kcal = round(nutrition.total_calories, 1)
    quality.protein_g = round(nutrition.total_protein, 1)
    quality.macro_percent = percentages
    quality.macros_in_range = in_amdr(percentages)
    quality.estimated_ingredients = sum(
        1 for ingredient in nutrition.ingredients_macros if ingredient.verification == "estimated"
    )
    if result.meal_plan.retrieval is not None:
        quality.retrieval_score = round(result.meal_plan.retrieval.selected_score, 3)

    scaling = result.meal_plan.portion_scaling
    if scaling is not None:
        target = scaling.target_meal_calories
        quality.target_meal_kcal = target
        quality.scale_factor = scaling.scale_factor
        quality.scale_clamped = _first_pass_clamped(target, scaling.estimated_template_calories)
        deviation = abs(nutrition.total_calories - target) / target
        quality.calorie_deviation = round(deviation, 4)
        quality.within_tolerance = deviation <= DEFAULT_TOLERANCE
    if result.reconciliation is not None:
        quality.rescaled = result.reconciliation.rescaled
    return quality


def _first_pass_clamped(target: int, estimated_template_calories: float) -> bool:
    """Whether first-pass scaling wanted more than one pass may give, so portions stopped short.

    The reported factor cannot show this after a reconciliation retry, which
    multiplies it, so the wanted ratio is recomputed from the scaling metadata.
    """
    if estimated_template_calories <= 0:
        return False
    return not MIN_SCALE <= target / estimated_template_calories <= MAX_SCALE


def build_service(data_dir: Path) -> MealPlanningService:
    """Build the real service with every external provider switched off.

    Args:
        data_dir: An empty directory for the profile store, so every request
            reads the built-in default profile.

    Returns:
        A MealPlanningService wired like production, minus API keys.
    """
    settings = AppSettings(_env_file=None)
    profile_repo = UserProfileRepository(data_dir)
    return MealPlanningService(
        meal_agent=MealRecommendationAgent(
            db_connection=profile_repo,
            meal_corpus_path=settings.meal_corpus_path,
            rag_backend=settings.rag_backend,
        ),
        nutrition_agent=NutritionVerificationAgent(),
        supermarket_agent=SupermarketAgent(),
        calorie_agent=CalorieExpenditureAgent(
            model_path=settings.calorie_model_path,
            model_version=settings.calorie_model_version,
        ),
        profile_repo=profile_repo,
    )


def run(scenarios: Iterable[Scenario] | None = None) -> list[PlanQuality]:
    """Run scenarios through a freshly built offline service.

    Args:
        scenarios: The scenarios to run; the fixed default set when omitted.

    Returns:
        One PlanQuality per scenario, in order.
    """
    scenarios = list(scenarios) if scenarios is not None else default_scenarios()
    with tempfile.TemporaryDirectory() as data_dir:
        service = build_service(Path(data_dir))
        return [
            measure(scenario, service.generate(scenario.to_request())) for scenario in scenarios
        ]


@dataclass
class Summary:
    """Aggregate numbers for a set of PlanQuality rows."""

    plans: int
    status_counts: dict[str, int]
    scaled_plans: int
    within_tolerance: int
    median_deviation: float | None
    p90_deviation: float | None
    max_deviation: float | None
    rescaled: int
    scale_clamped: int
    target_share_of_budget: dict[str, float | None]
    macros_in_range: dict[str, int]
    all_macros_in_range: int
    with_estimated_ingredients: int
    weak_matches: int
    daily_budget_kcal: dict[str, float | None]


def summarise(rows: Sequence[PlanQuality]) -> Summary:
    """Aggregate per-plan numbers into the baseline's headline figures.

    Args:
        rows: Per-scenario results.

    Returns:
        The Summary.
    """
    served = [row for row in rows if row.macro_percent is not None]
    scaled = [row for row in served if row.calorie_deviation is not None]
    deviations = sorted(row.calorie_deviation for row in scaled)
    shares = [
        row.target_meal_kcal / row.daily_budget_kcal
        for row in scaled
        if row.target_meal_kcal and row.daily_budget_kcal > 0
    ]
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row.plan_status] = status_counts.get(row.plan_status, 0) + 1

    return Summary(
        plans=len(rows),
        status_counts=status_counts,
        scaled_plans=len(scaled),
        within_tolerance=sum(1 for row in scaled if row.within_tolerance),
        median_deviation=round(statistics.median(deviations), 4) if deviations else None,
        p90_deviation=_percentile(deviations, 0.9),
        max_deviation=deviations[-1] if deviations else None,
        rescaled=sum(1 for row in scaled if row.rescaled),
        scale_clamped=sum(1 for row in scaled if row.scale_clamped),
        target_share_of_budget={
            "min": round(min(shares), 3) if shares else None,
            "max": round(max(shares), 3) if shares else None,
        },
        macros_in_range={
            macro: sum(1 for row in served if row.macros_in_range[macro]) for macro in AMDR_PERCENT
        },
        all_macros_in_range=sum(1 for row in served if all(row.macros_in_range.values())),
        with_estimated_ingredients=sum(1 for row in served if row.estimated_ingredients),
        weak_matches=sum(
            1
            for row in served
            if row.plan_status == "matched"
            and row.retrieval_score is not None
            and row.retrieval_score < WEAK_MATCH_SCORE
        ),
        daily_budget_kcal={
            "min": min((row.daily_budget_kcal for row in rows), default=None),
            "max": max((row.daily_budget_kcal for row in rows), default=None),
        },
    )


def _percentile(sorted_values: Sequence[float], fraction: float) -> float | None:
    """Nearest-rank percentile of already sorted values."""
    if not sorted_values:
        return None
    rank = max(1, round(fraction * len(sorted_values)))
    return sorted_values[min(rank, len(sorted_values)) - 1]


def render_markdown(rows: Sequence[PlanQuality], summary: Summary) -> str:
    """Render the summary and the per-plan table as Markdown.

    Args:
        rows: Per-scenario results.
        summary: Their aggregate.

    Returns:
        The report, ending in a newline.
    """
    served = summary.plans - summary.status_counts.get("infeasible", 0)
    statuses = ", ".join(
        f"{status} {count}" for status, count in sorted(summary.status_counts.items())
    )
    lines = [
        "## Summary",
        "",
        f"- Plans: {summary.plans} ({statuses}).",
        f"- Within the {DEFAULT_TOLERANCE:.0%} calorie tolerance: "
        f"{summary.within_tolerance} of {summary.scaled_plans} scaled plans.",
        f"- Calorie deviation: median {_pct(summary.median_deviation)}, "
        f"90th percentile {_pct(summary.p90_deviation)}, max {_pct(summary.max_deviation)}.",
        f"- Rescaled by reconciliation: {summary.rescaled}. "
        f"First-pass scaling clamped: {summary.scale_clamped}.",
        f"- Meal target as a share of the daily budget: "
        f"{_pct(summary.target_share_of_budget['min'])} to "
        f"{_pct(summary.target_share_of_budget['max'])}.",
        f"- Daily budget across profiles: {summary.daily_budget_kcal['min']} to "
        f"{summary.daily_budget_kcal['max']} kcal.",
        f"- Macro share inside AMDR: protein {summary.macros_in_range['protein']}, "
        f"carbs {summary.macros_in_range['carbs']}, fat {summary.macros_in_range['fat']}; "
        f"all three {summary.all_macros_in_range} of {served}.",
        f"- Plans with at least one estimated ingredient: "
        f"{summary.with_estimated_ingredients} of {served}.",
        f"- Corpus matches scoring below {WEAK_MATCH_SCORE}: {summary.weak_matches}.",
        "",
        "## Plans",
        "",
        "| Scenario | Status | Meal | Target | Verified | Dev. | Scale | P/C/F % | Score |",
        "|---|---|---|---:|---:|---:|---:|---|---:|",
    ]
    for row in rows:
        split = (
            "/".join(f"{row.macro_percent[macro]:.0f}" for macro in AMDR_PERCENT)
            if row.macro_percent
            else ""
        )
        lines.append(
            f"| {row.scenario} | {row.plan_status} | {row.meal_name or ''} "
            f"| {row.target_meal_kcal or ''} | {row.verified_kcal or ''} "
            f"| {_pct(row.calorie_deviation)} | {row.scale_factor or ''} | {split} "
            f"| {row.retrieval_score if row.retrieval_score is not None else ''} |"
        )
    return "\n".join(lines) + "\n"


def _pct(value: float | None) -> str:
    """Format a fraction as a percentage, or a dash when absent."""
    return "-" if value is None else f"{value:.1%}"
