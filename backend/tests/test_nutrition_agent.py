"""Nutrition agent: provider chain, cooldown, caching and fallbacks.

Every test patches ``backend.app.agents.nutrition_verification_agent.urlopen``.
Patching ``urllib.request.urlopen`` would not work - the module binds the name at
import time.
"""

import json
from contextlib import contextmanager
from typing import Any

import pytest

from backend.app.agents import nutrition_verification_agent as module
from backend.app.agents.nutrition_verification_agent import NutritionVerificationAgent
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


def _fake_urlopen(payload: dict[str, Any]):
    """Build a urlopen replacement returning one JSON payload.

    Args:
        payload: The object the fake endpoint should return.

    Returns:
        A callable usable as a context manager, like the real urlopen.
    """

    @contextmanager
    def _opener(*args: object, **kwargs: object):
        class _Response:
            def read(self) -> bytes:
                return json.dumps(payload).encode("utf-8")

        yield _Response()

    return _opener


def _boom(*args: object, **kwargs: object):
    """A urlopen replacement that always fails."""
    raise OSError("provider unavailable")


def test_no_keys_means_no_network_and_a_local_estimate() -> None:
    """With no credentials the agent must not attempt any provider."""
    agent = NutritionVerificationAgent()
    result = agent.calculate_meal_macros(
        [Ingredient(item_name="chicken breast", base_quantity_grams=100)]
    )
    assert result.total_calories > 0
    assert result.ingredients_macros[0].data_source != "usda_fooddata_central"


def test_usda_is_used_when_a_key_is_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """A configured key must actually route through USDA."""
    monkeypatch.setattr(module, "urlopen", _fake_urlopen(USDA_PAYLOAD))
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    macros = agent._query_macros_per_100g("kale")
    assert macros["source"] == "usda_fooddata_central"
    assert macros["calories"] == 165.0
    assert macros["protein"] == 31.0


def test_a_successful_lookup_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    """The second lookup of the same ingredient must not call the provider again."""
    calls: list[str] = []

    def _counting(*args: object, **kwargs: object):
        calls.append("hit")
        return _fake_urlopen(USDA_PAYLOAD)(*args, **kwargs)

    monkeypatch.setattr(module, "urlopen", _counting)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    agent._query_macros_per_100g("kale")
    agent._query_macros_per_100g("kale")
    assert len(calls) == 1


def test_a_trusted_override_short_circuits_the_providers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Local overrides must win before any network call is considered.

    ``olive oil`` is confirmed present in the ``trusted_overrides`` reference
    table (see task-2-report.md), so this test always exercises the real
    assertion rather than skipping.
    """
    monkeypatch.setattr(module, "urlopen", _boom)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    override = agent._trusted_local_override("olive oil")
    assert override is not None
    assert agent._query_macros_per_100g("olive oil") == override


def test_provider_failure_falls_back_to_a_local_estimate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing provider must degrade, not raise."""
    monkeypatch.setattr(module, "urlopen", _boom)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    macros = agent._query_macros_per_100g("some unusual ingredient")
    assert macros["calories"] > 0
    assert macros["source"] != "usda_fooddata_central"


def test_three_failures_open_the_cooldown(monkeypatch: pytest.MonkeyPatch) -> None:
    """After _FAILURE_THRESHOLD failures the provider is paused."""
    monkeypatch.setattr(module, "urlopen", _boom)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    assert agent._usda_cooldown_until == 0.0
    for index in range(NutritionVerificationAgent._FAILURE_THRESHOLD):
        agent._query_macros_per_100g(f"ingredient {index}")
    assert agent._usda_consecutive_failures >= NutritionVerificationAgent._FAILURE_THRESHOLD
    assert agent._usda_cooldown_until > 0.0


def test_a_cooled_down_provider_is_not_called(monkeypatch: pytest.MonkeyPatch) -> None:
    """While in cooldown the agent must skip the provider entirely."""
    calls: list[str] = []

    def _counting(*args: object, **kwargs: object):
        calls.append("hit")
        raise OSError("provider unavailable")

    monkeypatch.setattr(module, "urlopen", _counting)
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    agent._usda_cooldown_until = module.time.time() + 120
    agent._query_macros_per_100g("anything at all")
    assert calls == []


def test_success_resets_the_failure_counter(monkeypatch: pytest.MonkeyPatch) -> None:
    """A working call must clear the path back to cooldown."""
    agent = NutritionVerificationAgent(usda_api_key="test-key")
    monkeypatch.setattr(module, "urlopen", _boom)
    agent._query_macros_per_100g("first")
    assert agent._usda_consecutive_failures == 1
    monkeypatch.setattr(module, "urlopen", _fake_urlopen(USDA_PAYLOAD))
    agent._query_macros_per_100g("second")
    assert agent._usda_consecutive_failures == 0


def test_macros_scale_with_portion_size() -> None:
    """200 g must yield roughly twice the macros of 100 g."""
    agent = NutritionVerificationAgent()
    small = agent.calculate_meal_macros(
        [Ingredient(item_name="brown rice", base_quantity_grams=100)]
    )
    large = agent.calculate_meal_macros(
        [Ingredient(item_name="brown rice", base_quantity_grams=200)]
    )
    assert large.total_calories == pytest.approx(small.total_calories * 2, rel=0.01)


def test_metadata_reports_a_confidence_and_agent_name() -> None:
    agent = NutritionVerificationAgent()
    result = agent.calculate_meal_macros(
        [Ingredient(item_name="chicken breast", base_quantity_grams=150)]
    )
    assert 0 <= result.metadata.confidence <= 1
    assert result.metadata.agent_name
