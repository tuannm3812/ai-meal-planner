"""G3 nutrition contract: per-ingredient verification and per-meal status.

The agreed contract (portfolio log, 2026-10-08) keeps each ingredient's
``data_source`` and adds:

- ``verification``: ``verified_external`` (USDA, FatSecret), ``trusted_local``
  (the curated override table) or ``estimated`` (the fallback table and
  category estimates);
- ``nutrition_status`` on the meal: ``verified`` when no ingredient is
  estimated, ``mixed`` when at least one is, and ``unverified_required`` - the
  only failing case - when verification is required and cannot be met;
- ``sources``: the sorted, de-duplicated data sources actually used, replacing
  the old aggregate string ``usda_fatsecret_or_estimated``.

Every case is checked on serialised output, not on warning text. Also covered:
timeout and URLError at each of the three ``urlopen`` calls, and recovery once
a cooldown expires.
"""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from urllib.error import URLError

import pytest

from backend.app.agents import nutrition_verification_agent as module
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
from backend.app.core.config import AppSettings
from backend.app.core.exceptions import NutritionProviderError
from backend.app.schemas.requests import Ingredient

USDA_PAYLOAD = {
    "foods": [
        {
            "foodNutrients": [
                {"nutrientName": "Energy", "value": 165.0},
                {"nutrientName": "Protein", "value": 31.0},
                {"nutrientName": "Carbohydrate, by difference", "value": 0.0},
                {"nutrientName": "Total lipid (fat)", "value": 3.6},
            ]
        }
    ]
}
FATSECRET_TOKEN = {"access_token": "token", "expires_in": 3600}
FATSECRET_FOODS = {
    "foods": {
        "food": {
            "food_description": (
                "Per 100g - Calories: 120kcal | Fat: 2.00g | Carbs: 3.00g | Protein: 20.00g"
            )
        }
    }
}

TRUSTED = "whole egg"  # in trusted_overrides.json
FALLBACK_TABLE = "lean turkey mince"  # in macro_fallbacks.json only
UNKNOWN = "zzz mystery ingredient"  # in neither table


class _Opener:
    """A urlopen stand-in: canned JSON per URL, or a raised error, and a call log."""

    def __init__(self, routes: dict[str, Any]) -> None:
        self.routes = routes
        self.calls: list[tuple[str, float | None]] = []

    @contextmanager
    def __call__(self, target: Any, timeout: float | None = None) -> Iterator[Any]:
        url = target if isinstance(target, str) else target.full_url
        self.calls.append((url, timeout))
        for fragment, outcome in self.routes.items():
            if fragment in url:
                if isinstance(outcome, BaseException):
                    raise outcome

                class _Response:
                    def read(self, payload: Any = outcome) -> bytes:
                        return json.dumps(payload).encode("utf-8")

                yield _Response()
                return
        raise AssertionError(f"unexpected URL {url}")


def _meal(*names: str) -> list[Ingredient]:
    return [Ingredient(item_name=name, base_quantity_grams=100) for name in names]


@pytest.mark.parametrize(
    ("agent_kwargs", "routes", "name", "source", "verification", "status"),
    [
        (
            {"usda_api_key": "k"},
            {"api.nal.usda.gov": USDA_PAYLOAD},
            UNKNOWN,
            "usda_fooddata_central",
            "verified_external",
            "verified",
        ),
        (
            {"fatsecret_client_id": "id", "fatsecret_client_secret": "secret"},
            {"oauth.fatsecret.com": FATSECRET_TOKEN, "rest/server.api": FATSECRET_FOODS},
            UNKNOWN,
            "fatsecret_platform",
            "verified_external",
            "verified",
        ),
        ({}, {}, TRUSTED, "trusted_local_reference", "trusted_local", "verified"),
        ({}, {}, FALLBACK_TABLE, "local_reference_table", "estimated", "mixed"),
        ({}, {}, UNKNOWN, "category_estimate", "estimated", "mixed"),
    ],
    ids=["usda", "fatsecret", "trusted-local", "fallback-table", "category-estimate"],
)
def test_each_single_source_meal_serialises_truthfully(
    monkeypatch: pytest.MonkeyPatch,
    agent_kwargs: dict[str, str],
    routes: dict[str, Any],
    name: str,
    source: str,
    verification: str,
    status: str,
) -> None:
    monkeypatch.setattr(module, "urlopen", _Opener(routes))
    nutrition = NutritionVerificationAgent(**agent_kwargs).calculate_meal_macros(_meal(name))
    body = nutrition.model_dump()

    assert body["ingredients_macros"][0]["data_source"] == source
    assert body["ingredients_macros"][0]["verification"] == verification
    assert body["nutrition_status"] == status
    assert body["sources"] == [source]
    assert body["metadata"]["source"] != "usda_fatsecret_or_estimated"


def test_a_mixed_source_meal_reports_mixed_and_every_source() -> None:
    nutrition = NutritionVerificationAgent().calculate_meal_macros(_meal(TRUSTED, UNKNOWN))
    body = nutrition.model_dump()

    assert [i["verification"] for i in body["ingredients_macros"]] == [
        "trusted_local",
        "estimated",
    ]
    assert body["nutrition_status"] == "mixed"
    assert body["sources"] == ["category_estimate", "trusted_local_reference"]


def test_trusted_local_is_not_warned_about_as_an_estimate() -> None:
    """The old warning fired for every non-provider source, trusted ones included."""
    nutrition = NutritionVerificationAgent().calculate_meal_macros(_meal(TRUSTED))

    assert not any("Estimated" in warning for warning in nutrition.metadata.warnings)


def test_required_verification_that_cannot_be_met_fails() -> None:
    """The only failing status: verification is required and an ingredient is estimated."""
    agent = NutritionVerificationAgent(require_verified=True)

    with pytest.raises(NutritionProviderError) as raised:
        agent.calculate_meal_macros(_meal(TRUSTED, UNKNOWN))

    assert raised.value.error_code == "unverified_required"


def test_required_verification_passes_when_nothing_is_estimated() -> None:
    nutrition = NutritionVerificationAgent(require_verified=True).calculate_meal_macros(
        _meal(TRUSTED)
    )

    assert nutrition.nutrition_status == "verified"


def test_require_verified_nutrition_defaults_off_and_reads_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Off by default, so the offline demo keeps producing plans."""
    monkeypatch.delenv("REQUIRE_VERIFIED_NUTRITION", raising=False)
    assert AppSettings.from_env().require_verified_nutrition is False

    monkeypatch.setenv("REQUIRE_VERIFIED_NUTRITION", "1")
    assert AppSettings.from_env().require_verified_nutrition is True


_TIMEOUT = TimeoutError("timed out")
_URL_ERROR = URLError("connection refused")


@pytest.mark.parametrize("error", [_TIMEOUT, _URL_ERROR], ids=["timeout", "urlerror"])
@pytest.mark.parametrize(
    ("agent_kwargs", "routes_for", "failed_counter", "expected_timeout"),
    [
        (
            {"usda_api_key": "k"},
            lambda error: {"api.nal.usda.gov": error},
            "_usda_consecutive_failures",
            6,
        ),
        (
            {"fatsecret_client_id": "id", "fatsecret_client_secret": "secret"},
            lambda error: {"oauth.fatsecret.com": FATSECRET_TOKEN, "rest/server.api": error},
            "_fatsecret_consecutive_failures",
            8,
        ),
        (
            {"fatsecret_client_id": "id", "fatsecret_client_secret": "secret"},
            lambda error: {"oauth.fatsecret.com": error},
            "_fatsecret_consecutive_failures",
            8,
        ),
    ],
    ids=["usda-search", "fatsecret-search", "fatsecret-token"],
)
def test_each_upstream_call_degrades_on_timeout_and_url_error(
    monkeypatch: pytest.MonkeyPatch,
    error: BaseException,
    agent_kwargs: dict[str, str],
    routes_for: Any,
    failed_counter: str,
    expected_timeout: int,
) -> None:
    """A dead provider yields an estimate and a counted failure, never an exception."""
    opener = _Opener(routes_for(error))
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(**agent_kwargs)

    nutrition = agent.calculate_meal_macros(_meal(UNKNOWN))

    assert nutrition.ingredients_macros[0].verification == "estimated"
    assert getattr(agent, failed_counter) == 1
    # The failing call was made with its bounded timeout.
    assert opener.calls[-1][1] == expected_timeout


def test_a_provider_is_retried_and_recovers_once_its_cooldown_expires(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [1_000.0]
    monkeypatch.setattr(module.time, "time", lambda: clock[0])
    monkeypatch.setattr(module, "urlopen", _Opener({"api.nal.usda.gov": _TIMEOUT}))
    agent = NutritionVerificationAgent(usda_api_key="k")
    for index in range(3):
        agent.calculate_meal_macros(_meal(f"{UNKNOWN} {index}"))
    assert agent._usda_cooldown_until > clock[0], "precondition: cooldown is open"

    healthy = _Opener({"api.nal.usda.gov": USDA_PAYLOAD})
    monkeypatch.setattr(module, "urlopen", healthy)
    during = agent.calculate_meal_macros(_meal(f"{UNKNOWN} during"))
    assert healthy.calls == [], "the provider must not be called during cooldown"
    assert during.ingredients_macros[0].verification == "estimated"

    clock[0] = agent._usda_cooldown_until + 1
    after = agent.calculate_meal_macros(_meal(f"{UNKNOWN} after"))

    assert after.ingredients_macros[0].verification == "verified_external"
    assert after.nutrition_status == "verified"
    assert agent._usda_consecutive_failures == 0
