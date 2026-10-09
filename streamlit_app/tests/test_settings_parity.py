"""Demo mode must read boolean settings exactly as the API does.

Codex, 2026-10-10 (P2): demo.py compared REQUIRE_VERIFIED_NUTRITION to "1",
while the API parses a pydantic boolean. "true", "yes", "on", and a native
TOML `true` (which get_secret stringifies to "True") enabled strict
verification in the API but silently left it off in the demo, so an estimated
meal was returned and saved anyway. ENABLE_GEMINI_ADAPTATION had the same
mismatch.
"""

from typing import Any

import pytest
from config import get_bool_secret
from demo import local_demo_request
from pydantic import ValidationError
from streamlit.runtime.secrets import Secrets

from backend.app.core.config import AppSettings
from backend.app.core.exceptions import NutritionProviderError

PROFILE = {
    "age": 30,
    "sex": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "activity_multiplier": 1.4,
    "dietary_restrictions": [],
}
VALUES = ["1", "true", "True", "TRUE", "yes", "on", "0", "false", "False", "off", "no"]


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize(
    ("env_name", "field"),
    [
        ("REQUIRE_VERIFIED_NUTRITION", "require_verified_nutrition"),
        ("ENABLE_GEMINI_ADAPTATION", "enable_gemini_adaptation"),
    ],
)
def test_demo_and_api_parse_the_same_value_the_same_way(
    monkeypatch: pytest.MonkeyPatch, env_name: str, field: str, value: str
) -> None:
    monkeypatch.setenv(env_name, value)

    assert get_bool_secret(env_name) is getattr(AppSettings(_env_file=None), field)


def test_an_unset_flag_is_off() -> None:
    assert get_bool_secret("REQUIRE_VERIFIED_NUTRITION") is False


def test_a_native_secrets_boolean_is_honoured(monkeypatch: pytest.MonkeyPatch) -> None:
    """`REQUIRE_VERIFIED_NUTRITION = true` in secrets.toml arrives as the bool True."""
    real_get = Secrets.get

    def _get(self: Secrets, key: str, default: Any = None) -> Any:
        if key == "REQUIRE_VERIFIED_NUTRITION":
            return True
        return real_get(self, key, default)

    monkeypatch.setattr(Secrets, "get", _get)

    assert get_bool_secret("REQUIRE_VERIFIED_NUTRITION") is True


def test_an_invalid_value_is_refused_as_the_api_refuses_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The API will not start with an unparseable flag; the demo must not guess."""
    monkeypatch.setenv("REQUIRE_VERIFIED_NUTRITION", "maybe")

    with pytest.raises(ValidationError):
        get_bool_secret("REQUIRE_VERIFIED_NUTRITION")


@pytest.mark.parametrize("value", ["1", "true"])
def test_demo_strict_mode_fails_an_estimated_meal(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    """Keyless, so some ingredient is estimated: strict mode must refuse it."""
    monkeypatch.setenv("REQUIRE_VERIFIED_NUTRITION", value)

    with pytest.raises(NutritionProviderError):
        local_demo_request("/generate-meal-plan", {"craving": "pasta"}, PROFILE)


def test_demo_strict_mode_via_native_secrets_boolean(monkeypatch: pytest.MonkeyPatch) -> None:
    real_get = Secrets.get

    def _get(self: Secrets, key: str, default: Any = None) -> Any:
        if key == "REQUIRE_VERIFIED_NUTRITION":
            return True
        return real_get(self, key, default)

    monkeypatch.setattr(Secrets, "get", _get)

    with pytest.raises(NutritionProviderError):
        local_demo_request("/generate-meal-plan", {"craving": "pasta"}, PROFILE)


def test_demo_default_still_returns_a_plan() -> None:
    response = local_demo_request("/generate-meal-plan", {"craving": "pasta"}, PROFILE)

    assert response["plan_status"] in {"matched", "fallback"}
    assert response["nutrition"]["nutrition_status"] in {"verified", "mixed"}
