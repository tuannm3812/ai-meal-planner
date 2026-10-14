"""Unit tests for the Streamlit app's self-contained demo-mode request router.

`/generate-meal-plan` runs the real MealPlanningService in-process (the same
orchestrator FastAPI uses). conftest.py's autouse `_isolate_secrets` fixture
forces the env to the offline path before calling it: no Gemini key is
passed, and USDA/FatSecret keys are unset, so NutritionVerificationAgent and
MealRecommendationAgent never reach for the network (both are gated by
`if self.api_key:` / `if gemini_api_key:` in backend/app/agents/*). No
`allow_network` marker is needed.
"""

from typing import Any

from demo import StreamlitUserProfileRepository, local_demo_request

PROFILE = {
    "age": 28,
    "sex": "male",
    "height_cm": 180.0,
    "weight_kg": 80.0,
    "activity_multiplier": 1.55,
    "dietary_restrictions": ["dairy-free"],
}


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


# --- Codex, 2026-10-12: the demo saved feedback without the API's rules ---------
# The API refuses feedback with no signal (400) and feedback for a plan the
# client never generated (404), and validates the body (422). The demo saved any
# payload straight to the repository. It now goes through the same shared
# service, so the two cannot drift apart.


def _feedback(request_id: str, **signal: Any) -> dict[str, Any]:
    return {"user_id": "user_123", "request_id": request_id, "meal_name": "Pasta Bowl", **signal}


def _saved_meals() -> list[dict[str, Any]]:
    return local_demo_request("/saved-meals/user_123", None, PROFILE)["items"]


def test_demo_feedback_without_a_signal_is_refused() -> None:
    import pytest

    from backend.app.core.exceptions import FeedbackSignalRequired

    plan = local_demo_request("/generate-meal-plan", {"craving": "pasta"}, PROFILE)

    with pytest.raises(FeedbackSignalRequired):
        local_demo_request("/meal-feedback", _feedback(plan["request_id"]), PROFILE)


def test_demo_feedback_for_a_plan_it_never_made_is_refused_and_not_stored() -> None:
    import pytest

    from backend.app.core.exceptions import MealPlanNotFound

    with pytest.raises(MealPlanNotFound):
        local_demo_request("/meal-feedback", _feedback("no-such-plan-id", saved=True), PROFILE)
    assert _saved_meals() == []


def test_demo_feedback_body_is_validated_like_the_api() -> None:
    import pytest
    from pydantic import ValidationError

    plan = local_demo_request("/generate-meal-plan", {"craving": "pasta"}, PROFILE)

    with pytest.raises(ValidationError):
        local_demo_request("/meal-feedback", _feedback(plan["request_id"], rating=9), PROFILE)


def test_valid_demo_feedback_is_saved_in_the_api_record_shape() -> None:
    from backend.app.schemas.requests import MealFeedbackRequest

    plan = local_demo_request("/generate-meal-plan", {"craving": "pasta"}, PROFILE)

    result = local_demo_request(
        "/meal-feedback", _feedback(plan["request_id"], saved=True, rating=4), PROFILE
    )

    item = result["item"]
    assert result["status"] == "success"
    assert (item["request_id"], item["rating"], item["saved"]) == (plan["request_id"], 4, True)
    assert set(MealFeedbackRequest.model_fields) <= set(item), "every API field, defaults included"
    assert [meal["request_id"] for meal in _saved_meals()] == [plan["request_id"]]
