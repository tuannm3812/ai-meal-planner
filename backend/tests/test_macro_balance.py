"""Per-ingredient macro balancing (DEC-26).

The solver is checked on hand-built meals; the service is checked offline on
the meal-quality scenarios, against the same service with balancing switched
off, so the only thing that may differ is portion sizes.
"""

import dataclasses
import tempfile
from pathlib import Path

import pytest

from backend.app.core import macro_balance
from backend.app.core.macro_balance import (
    AMDR_PERCENT,
    CALORIE_BAND,
    MAX_FACTOR,
    MIN_FACTOR,
    SHARE_MARGIN,
    IngredientEnergy,
    balance_factors,
    in_amdr,
    macro_percentages,
)
from backend.app.evaluation.meal_quality import (
    CRAVINGS,
    GUARDRAIL_CORPUS,
    PROFILES,
    BenchmarkConfig,
    Scenario,
    build_service,
    default_scenarios,
    guardrail_scenarios,
)
from backend.app.services import meal_planning_service

# Per current portion: kcal, protein g, carbs g, fat g.
CHICKEN = IngredientEnergy(330, 62, 0, 7)
RICE = IngredientEnergy(260, 5, 56, 2)
AVOCADO = IngredientEnergy(110, 1.4, 6, 10)


def _shares(ingredients: list[IngredientEnergy], factors: list[float]) -> dict[str, float]:
    return macro_percentages(
        sum(item.protein_g * f for item, f in zip(ingredients, factors, strict=True)),
        sum(item.carbs_g * f for item, f in zip(ingredients, factors, strict=True)),
        sum(item.fat_g * f for item, f in zip(ingredients, factors, strict=True)),
    )


def test_a_meal_already_in_range_keeps_its_portions() -> None:
    meal = [IngredientEnergy(100, 5, 14, 3.5), IngredientEnergy(100, 5, 14, 3.5)]
    assert all(in_amdr(_shares(meal, [1, 1])).values())

    factors = balance_factors(meal, 200)

    assert factors == pytest.approx([1.0, 1.0])


def test_a_skewed_meal_is_brought_inside_every_range_and_the_calorie_band() -> None:
    meal = [CHICKEN, RICE, AVOCADO]
    assert not all(in_amdr(_shares(meal, [1, 1, 1])).values())  # protein-heavy

    factors = balance_factors(meal, 700)

    assert factors is not None
    assert all(MIN_FACTOR - 1e-9 <= f <= MAX_FACTOR + 1e-9 for f in factors)
    calories = sum(item.calories * f for item, f in zip(meal, factors, strict=True))
    assert abs(calories - 700) / 700 <= CALORIE_BAND + 1e-9
    shares = _shares(meal, factors)
    for macro, (low, high) in AMDR_PERCENT.items():
        assert low + SHARE_MARGIN - 1e-6 <= shares[macro] <= high - SHARE_MARGIN + 1e-6


def test_no_factors_when_the_ingredients_cannot_reach_the_ranges() -> None:
    """Chicken alone has no carbohydrate, so no portion of it reaches 45%."""
    assert balance_factors([CHICKEN], 330) is None


@pytest.mark.parametrize(("meal", "target"), [([], 500), ([RICE], 0)])
def test_no_factors_without_ingredients_or_a_target(
    meal: list[IngredientEnergy], target: float
) -> None:
    assert balance_factors(meal, target) is None


def _plans(scenarios: list[Scenario], config: BenchmarkConfig | None = None) -> list:
    with tempfile.TemporaryDirectory() as data_dir:
        service, _ = build_service(Path(data_dir), config)
        return [service.generate(scenario.to_request()) for scenario in scenarios]


@pytest.fixture(scope="module")
def balanced_and_unbalanced() -> tuple[list, list]:
    """Every default scenario, with balancing on and with it off."""
    scenarios = default_scenarios()
    balanced = _plans(scenarios)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(meal_planning_service, "balance_factors", lambda *_args: None)
        unbalanced = _plans(scenarios)
    return balanced, unbalanced


def _names(result) -> tuple[str, list[str]]:
    plan = result.meal_plan
    return plan.meal_definition.structured_meal_name, [
        ingredient.item_name for ingredient in plan.meal_definition.ingredients
    ]


def test_balancing_changes_portions_only(balanced_and_unbalanced: tuple[list, list]) -> None:
    """Same meal, same ingredients in the same order: selection, craving relevance and
    every hard-constraint substitution are untouched, because balancing can only
    resize what retrieval already chose."""
    balanced, unbalanced = balanced_and_unbalanced

    assert [_names(result) for result in balanced] == [_names(result) for result in unbalanced]
    assert [r.plan_status for r in balanced] == [r.plan_status for r in unbalanced]


def test_every_rebalanced_plan_ships_inside_amdr(
    balanced_and_unbalanced: tuple[list, list],
) -> None:
    balanced, unbalanced = balanced_and_unbalanced
    outcomes = {result.macro_balance.outcome for result in balanced}
    assert "rebalanced" in outcomes
    assert outcomes <= {"in_range", "rebalanced", "no_feasible_balance"}

    for after, before in zip(balanced, unbalanced, strict=True):
        record = after.macro_balance
        portions = [i.base_quantity_grams for i in after.meal_plan.meal_definition.ingredients]
        original = [i.base_quantity_grams for i in before.meal_plan.meal_definition.ingredients]
        if record.outcome == "rebalanced":
            assert record.macros_in_range_after is True
            shares = macro_percentages(
                after.nutrition.total_protein,
                after.nutrition.total_carbs,
                after.nutrition.total_fat,
            )
            assert all(in_amdr(shares).values())
            assert any(
                "Rebalanced ingredient portions" in w for w in after.meal_plan.metadata.warnings
            )
        else:
            if record.outcome != "reverted":
                assert record.macro_percent_after is None
            assert portions == original


def test_guardrail_outcomes_survive_balancing() -> None:
    config = dataclasses.replace(BenchmarkConfig.canonical(), meal_corpus_path=GUARDRAIL_CORPUS)
    guardrails = guardrail_scenarios()

    results = _plans([guardrail.scenario for guardrail in guardrails], config)

    for guardrail, result in zip(guardrails, results, strict=True):
        assert result.plan_status == guardrail.expected_status
        if result.meal_plan is None:
            assert result.macro_balance is None
        else:
            assert result.meal_plan.meal_definition.structured_meal_name == guardrail.expected_meal


def test_a_rebalanced_plan_reports_its_split_before_and_after() -> None:
    (result,) = _plans([Scenario("chicken fried rice", PROFILES[1])])
    record = result.macro_balance

    assert record.outcome == "rebalanced"
    assert not all(in_amdr(record.macro_percent_before).values())
    assert all(in_amdr(record.macro_percent_after).values())
    assert record.target_meal_calories == result.meal_plan.portion_scaling.target_meal_calories


def test_the_bounds_are_read_when_solving(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no room to move, a skewed meal cannot be balanced."""
    monkeypatch.setattr(macro_balance, "MIN_FACTOR", 1.0)
    monkeypatch.setattr(macro_balance, "MAX_FACTOR", 1.0)

    assert balance_factors([CHICKEN, RICE, AVOCADO], 700) is None


# Codex, 2026-10-18: the solver's answer is unrounded and unverified, so test what
# ships after rounding to 5 g and re-verification, including when it goes wrong.


def test_portions_that_miss_on_re_verification_are_reverted() -> None:
    """A provider that disagrees with the first verification must not ship a worse split."""
    with tempfile.TemporaryDirectory() as data_dir:
        service, _ = build_service(Path(data_dir))
        real = service.nutrition_agent.calculate_meal_macros
        calls = []

        def adverse(ingredients):
            nutrition = real(ingredients)
            calls.append(nutrition)
            if len(calls) == 2:  # the re-verification of balanced portions
                return nutrition.model_copy(update={"total_fat": nutrition.total_fat * 3})
            return nutrition

        service.nutrition_agent.calculate_meal_macros = adverse
        result = service.generate(Scenario("chicken fried rice", PROFILES[1]).to_request())

    record = result.macro_balance
    assert record.outcome == "reverted"
    assert record.macros_in_range_after is False
    assert record.macro_percent_after is not None
    first = calls[0]
    assert [i.base_quantity_grams for i in result.meal_plan.meal_definition.ingredients] == [
        i.base_quantity_grams for i in first.ingredients_macros
    ]
    assert not any("Rebalanced" in w for w in result.meal_plan.metadata.warnings)


@pytest.mark.parametrize("craving", CRAVINGS)
def test_rounded_portions_hold_across_meal_targets(craving: str) -> None:
    """From 350 to 850 kcal in 50 kcal steps, no solved plan is lost to 5 g rounding."""
    with tempfile.TemporaryDirectory() as data_dir:
        service, _ = build_service(Path(data_dir))
        profile = service.profile_repo.fetch_user_profile("user_123")
        solved = 0
        for target in range(350, 851, 50):
            plan = service.meal_agent.generate_meal_payload(
                craving=craving,
                user_id="user_123",
                daily_calorie_target=round(target / 0.28),
                profile=profile,
            )
            nutrition = service.nutrition_agent.calculate_meal_macros(
                plan.meal_definition.ingredients
            )
            _, shipped, record = service._balance(plan, nutrition)
            assert record.outcome != "reverted", (craving, target)
            if record.outcome == "rebalanced":
                solved += 1
                shares = macro_percentages(
                    shipped.total_protein, shipped.total_carbs, shipped.total_fat
                )
                assert all(in_amdr(shares).values())
                meal_target = record.target_meal_calories
                assert abs(shipped.total_calories - meal_target) / meal_target <= 0.10


def test_every_matched_default_plan_meets_the_targets(
    balanced_and_unbalanced: tuple[list, list],
) -> None:
    """DEC-28: with a cooking fat in each recipe that had none, every corpus match
    can be balanced, so none ships outside the targets."""
    balanced, _ = balanced_and_unbalanced

    for result in balanced:
        if result.plan_status != "matched":
            continue
        nutrition = result.nutrition
        shares = macro_percentages(
            nutrition.total_protein, nutrition.total_carbs, nutrition.total_fat
        )
        target = result.macro_balance.target_meal_calories
        name = result.meal_plan.meal_definition.structured_meal_name
        assert all(in_amdr(shares).values()), name
        assert abs(nutrition.total_calories - target) / target <= 0.10, name
