"""Unit tests for the Streamlit app's self-contained demo-mode request router.

`/generate-meal-plan` runs the real MealPlanningService in-process (the same
orchestrator FastAPI uses), so these tests force the env to the offline path
before calling it: no Gemini key is passed, and USDA/FatSecret keys are
unset, so NutritionVerificationAgent and MealRecommendationAgent never reach
for the network (both are gated by `if self.api_key:` / `if gemini_api_key:`
in backend/app/agents/*). No `allow_network` marker is needed.
"""

from typing import Any

import pytest
from demo import StreamlitUserProfileRepository, local_demo_request

PROFILE = {
    "age": 28,
    "sex": "male",
    "height_cm": 180.0,
    "weight_kg": 80.0,
    "activity_multiplier": 1.55,
    "dietary_restrictions": ["dairy-free"],
}


@pytest.fixture(autouse=True)
def _offline_demo_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force local_demo_request onto its deterministic, no-network path."""
    for name in (
        "USDA_API_KEY",
        "FATSECRET_CLIENT_ID",
        "FATSECRET_CLIENT_SECRET",
        "ENABLE_GEMINI_ADAPTATION",
        "GEMINI_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_health_reports_ok_status_and_services() -> None:
    result = local_demo_request("/health", None, PROFILE)

    assert result["status"] == "ok"
    assert "services" in result


def test_generate_meal_plan_returns_the_expected_sections() -> None:
    result = local_demo_request(
        "/generate-meal-plan",
        {"craving": "high-protein burger"},
        PROFILE,
        api_key="",
    )

    expected_keys = {
        "status",
        "request_id",
        "meal_plan",
        "nutrition",
        "shopping_list",
        "calorie_budget",
        "reconciliation",
    }
    assert expected_keys.issubset(result.keys()), result.keys()
    assert result["status"] == "success"


def test_fetch_user_profile_maps_sex_to_the_backend_shape() -> None:
    repository = StreamlitUserProfileRepository(
        age=28,
        sex="male",
        height_cm=180.0,
        weight_kg=80.0,
        activity_multiplier=1.55,
        dietary_restrictions=["dairy-free"],
    )

    profile: dict[str, Any] = repository.fetch_user_profile("user_123")

    assert profile == {
        "age": 28,
        "gender": "m",
        "height": 180.0,
        "weight": 80.0,
        "workout_level": 1.55,
        "dietary_restrictions": ["dairy-free"],
    }


def test_fetch_user_profile_maps_non_male_sex_to_f() -> None:
    repository = StreamlitUserProfileRepository(
        age=30,
        sex="female",
        height_cm=165.0,
        weight_kg=60.0,
        activity_multiplier=1.2,
        dietary_restrictions=[],
    )

    assert repository.fetch_user_profile("user_456")["gender"] == "f"
