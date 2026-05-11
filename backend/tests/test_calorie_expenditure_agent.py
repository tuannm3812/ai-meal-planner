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
