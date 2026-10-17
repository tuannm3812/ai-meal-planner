from pathlib import Path

from backend.app.agents.calorie_expenditure_agent import (
    CalorieExpenditureAgent,
    CalorieExpenditureRequest,
)

MODEL_PATH = Path("models/calorie_expenditure/calorie_expenditure_model.joblib")


def test_calorie_model_artifact_loads_and_predicts() -> None:
    agent = CalorieExpenditureAgent(
        model_path=MODEL_PATH,
        model_version="test_model",
    )
    request = CalorieExpenditureRequest(
        age=28,
        sex="male",
        height_cm=180,
        weight_kg=80,
        activity_multiplier=1.55,
        duration_minutes=30,
        heart_rate_bpm=100,
        body_temp_c=40,
        goal="maintain",
    )

    response = agent.predict(request)

    assert agent.model is not None
    assert response.model_version == "test_model"
    assert response.confidence == 0.82
    assert response.estimated_daily_expenditure_kcal > 2000
    assert response.meal_calorie_budget_kcal == response.estimated_daily_expenditure_kcal
    assert all("Unable to load calorie model" not in warning for warning in response.warnings)
    assert all("Using rule-based fallback" not in warning for warning in response.warnings)


def test_calorie_agent_falls_back_when_model_missing() -> None:
    agent = CalorieExpenditureAgent(model_path=Path("missing-model.joblib"))
    request = CalorieExpenditureRequest(
        age=28,
        sex="male",
        height_cm=180,
        weight_kg=80,
        activity_multiplier=1.55,
        goal="weight_loss",
    )

    response = agent.predict(request)

    assert response.model_version == "mifflin_st_jeor_fallback_v0.1.0"
    assert response.confidence == 0.55
    assert response.meal_calorie_budget_kcal < response.estimated_daily_expenditure_kcal
    assert response.warnings


def _rule_based_budget(sex: str, weight_kg: float, goal: str = "lose") -> tuple[float, list]:
    """Predict with the rule-based fallback, so the expenditure is plain Mifflin-St Jeor."""
    response = CalorieExpenditureAgent().predict(
        CalorieExpenditureRequest(
            age=62, sex=sex, height_cm=158, weight_kg=weight_kg, activity_multiplier=1.2, goal=goal
        )
    )
    return response.meal_calorie_budget_kcal, response.warnings


def test_weight_loss_budget_never_drops_below_the_floor_for_women() -> None:
    """Owner decision 2026-10-17: expenditure minus 400 stops at 1,200 kcal for women."""
    # Mifflin-St Jeor: (520 + 987.5 - 310 - 161) * 1.2 = 1243.8 kcal; minus 400 is 843.8.
    budget, warnings = _rule_based_budget("female", 52)

    assert budget == 1200
    assert any("1200 kcal minimum" in warning for warning in warnings)


def test_the_floor_never_raises_a_weight_loss_budget_above_expenditure() -> None:
    """Men's floor is 1,500 kcal, but a floor above expenditure would turn the deficit
    into a surplus, so the budget stops at expenditure."""
    # (520 + 987.5 - 310 + 5) * 1.2 = 1443.0 kcal: below the 1,500 floor itself.
    budget, warnings = _rule_based_budget("male", 52)

    assert budget == 1443.0
    assert any("1500 kcal minimum" in warning for warning in warnings)


def test_a_weight_loss_budget_above_the_floor_is_unchanged() -> None:
    # (900 + 987.5 - 310 - 161) * 1.2 = 1699.8 kcal; minus 400 is 1299.8, above 1,200.
    budget, warnings = _rule_based_budget("female", 90)

    assert budget == 1299.8
    assert not any("minimum" in warning for warning in warnings)


def test_an_unrecognised_sex_gets_the_higher_floor() -> None:
    budget, _ = _rule_based_budget("x", 90)

    assert budget == 1500


def test_the_floor_applies_only_to_weight_loss() -> None:
    budget, warnings = _rule_based_budget("female", 52, goal="maintain")

    assert budget == 1243.8
    assert not any("minimum" in warning for warning in warnings)
