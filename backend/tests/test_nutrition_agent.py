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


# --- FatSecret provider path -------------------------------------------------
#
# FatSecret needs two round trips per cold lookup: an OAuth token fetch
# (``https://oauth.fatsecret.com/connect/token``) followed by the food search
# itself (``https://platform.fatsecret.com/rest/server.api``). Both go through
# the same patched ``urlopen``, so the fakes below dispatch by request URL
# instead of returning one fixed payload like the USDA fakes above.
#
# The realistic ``food_description`` format used below was derived directly
# from ``_parse_fatsecret_description``: it requires the literal substring
# "per 100g" (case-insensitive) somewhere in the description, then four
# independent regexes - ``Calories:\s*([0-9.]+)\s*kcal``, ``Fat:\s*([0-9.]+)\s*g``,
# ``Carbs:\s*([0-9.]+)\s*g``, ``Protein:\s*([0-9.]+)\s*g`` - each of which must
# match or the whole description is rejected. That matches FatSecret's real
# ``foods.search`` response shape, e.g. "Per 100g - Calories: 165kcal | Fat:
# 3.60g | Carbs: 0.00g | Protein: 31.00g".

FATSECRET_TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
FATSECRET_SEARCH_URL = "https://platform.fatsecret.com/rest/server.api"

FATSECRET_TOKEN_PAYLOAD = {"access_token": "test-access-token", "expires_in": 3600}

FATSECRET_DESCRIPTION = "Per 100g - Calories: 165kcal | Fat: 3.60g | Carbs: 0.00g | Protein: 31.00g"

FATSECRET_SEARCH_PAYLOAD = {"foods": {"food": {"food_description": FATSECRET_DESCRIPTION}}}


class _BytesResponse:
    """A urlopen response stand-in that replays fixed bytes from ``.read()``."""

    def __init__(self, payload_bytes: bytes) -> None:
        self._payload_bytes = payload_bytes

    def read(self) -> bytes:
        return self._payload_bytes


def _multi_urlopen(
    responses: dict[str, Any],
) -> tuple[Any, dict[str, int]]:
    """Build a urlopen replacement that dispatches by request URL.

    Needed because a single FatSecret lookup makes two calls through the same
    patched ``urlopen`` - one to the OAuth token endpoint, one to the food
    search endpoint - and some tests also mix in the USDA endpoint. The plain
    single-payload ``_fake_urlopen`` above cannot tell those apart.

    Args:
        responses: Maps a URL to either a JSON-serializable payload or an
            ``Exception`` instance to raise when that URL is requested.

    Returns:
        A tuple of (opener, calls) where ``opener`` is usable as a context
        manager like the real ``urlopen``, and ``calls`` counts requests per
        URL so tests can assert on call counts (e.g. token reuse, cooldown).
    """
    calls: dict[str, int] = {}

    @contextmanager
    def _opener(request: object, *args: object, **kwargs: object):
        url = getattr(request, "full_url", request)
        for target_url, handler in responses.items():
            if url == target_url or (isinstance(url, str) and url.startswith(target_url)):
                calls[target_url] = calls.get(target_url, 0) + 1
                if isinstance(handler, Exception):
                    raise handler
                yield _BytesResponse(json.dumps(handler).encode("utf-8"))
                return
        raise AssertionError(f"unexpected urlopen call: {url}")

    return _opener, calls


def test_fatsecret_is_reached_when_usda_is_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no USDA key, FatSecret must be tried and its macros returned as-is.

    Would catch a regression where the provider chain skips FatSecret
    entirely (falling straight to the local estimate) or mislabels its
    results under the wrong ``source``.
    """
    opener, calls = _multi_urlopen(
        {
            FATSECRET_TOKEN_URL: FATSECRET_TOKEN_PAYLOAD,
            FATSECRET_SEARCH_URL: FATSECRET_SEARCH_PAYLOAD,
        }
    )
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    macros = agent._query_macros_per_100g("kale")
    assert macros["source"] == "fatsecret_platform"
    assert macros["calories"] == 165.0
    assert macros["protein"] == 31.0
    assert macros["fat"] == 3.6
    assert macros["carbs"] == 0.0
    assert calls[FATSECRET_TOKEN_URL] == 1
    assert calls[FATSECRET_SEARCH_URL] == 1


def test_fatsecret_token_is_reused_while_unexpired(monkeypatch: pytest.MonkeyPatch) -> None:
    """A second, distinct lookup must reuse the cached OAuth token.

    Would catch a bug that re-fetches the token on every FatSecret call
    instead of caching it for its lifetime, which would waste a request and
    risk hitting FatSecret's rate limits.
    """
    opener, calls = _multi_urlopen(
        {
            FATSECRET_TOKEN_URL: FATSECRET_TOKEN_PAYLOAD,
            FATSECRET_SEARCH_URL: FATSECRET_SEARCH_PAYLOAD,
        }
    )
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    agent._query_macros_per_100g("kale")
    agent._query_macros_per_100g("spinach")  # different search name: bypasses the macro cache
    assert calls[FATSECRET_TOKEN_URL] == 1
    assert calls[FATSECRET_SEARCH_URL] == 2


def test_expired_fatsecret_token_triggers_a_refetch(monkeypatch: pytest.MonkeyPatch) -> None:
    """An expired token must be refetched, not reused blindly.

    Would catch a bug that checks token presence but not expiry, which would
    keep using a token FatSecret has already rejected.
    """
    opener, calls = _multi_urlopen({FATSECRET_TOKEN_URL: FATSECRET_TOKEN_PAYLOAD})
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    token = agent._get_fatsecret_token()
    assert token == "test-access-token"
    assert calls[FATSECRET_TOKEN_URL] == 1

    agent.fatsecret_token_expires_at = module.time.time() - 1
    token_again = agent._get_fatsecret_token()
    assert token_again == "test-access-token"
    assert calls[FATSECRET_TOKEN_URL] == 2


def test_parse_fatsecret_description_extracts_macros() -> None:
    """A realistic FatSecret description must parse into the four macro keys.

    Would catch a regex/format mismatch that silently stops every FatSecret
    result from ever parsing, forcing a permanent fallback to estimates.
    """
    agent = NutritionVerificationAgent()
    macros = agent._parse_fatsecret_description(FATSECRET_DESCRIPTION)
    assert macros == {"calories": 165.0, "fat": 3.6, "carbs": 0.0, "protein": 31.0}


def test_malformed_fatsecret_description_falls_back_to_a_local_estimate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A description that doesn't match the expected shape must degrade, not raise.

    Would catch a bug where an unparseable description (e.g. missing the "per
    100g" marker, or missing one of the four macro fields) raises instead of
    letting the caller fall through to the local estimate.
    """
    opener, calls = _multi_urlopen(
        {
            FATSECRET_TOKEN_URL: FATSECRET_TOKEN_PAYLOAD,
            FATSECRET_SEARCH_URL: {
                "foods": {"food": {"food_description": "Serving size 1 cup (240g)"}}
            },
        }
    )
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    macros = agent._query_macros_per_100g("some unusual ingredient")
    assert macros["calories"] > 0
    assert macros["source"] not in {"usda_fooddata_central", "fatsecret_platform"}


def test_three_fatsecret_failures_open_its_cooldown(monkeypatch: pytest.MonkeyPatch) -> None:
    """After _FAILURE_THRESHOLD consecutive failures, FatSecret must be paused.

    Would catch a bug where only the USDA failure counter is wired up and
    FatSecret failures are silently ignored, hammering a dead provider forever.
    """

    def _boom(*args: object, **kwargs: object) -> None:
        raise OSError("fatsecret unavailable")

    monkeypatch.setattr(module, "urlopen", _boom)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    assert agent._fatsecret_cooldown_until == 0.0
    for index in range(NutritionVerificationAgent._FAILURE_THRESHOLD):
        agent._query_macros_per_100g(f"ingredient {index}")
    assert agent._fatsecret_consecutive_failures >= NutritionVerificationAgent._FAILURE_THRESHOLD
    assert agent._fatsecret_cooldown_until > 0.0


def test_a_cooled_down_fatsecret_is_not_called(monkeypatch: pytest.MonkeyPatch) -> None:
    """While FatSecret is in cooldown, the agent must skip it entirely.

    Would catch a bug where the cooldown check reads the wrong attribute
    (e.g. the USDA cooldown) and keeps calling a paused FatSecret provider.
    """
    calls: list[str] = []

    def _counting(*args: object, **kwargs: object) -> None:
        calls.append("hit")
        raise OSError("fatsecret unavailable")

    monkeypatch.setattr(module, "urlopen", _counting)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    agent._fatsecret_cooldown_until = module.time.time() + 120
    agent._query_macros_per_100g("anything at all")
    assert calls == []


def test_usda_failure_falls_through_to_a_working_fatsecret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When USDA fails, FatSecret must still be tried and its result used.

    This is the cross-provider fallback that is the whole point of
    configuring two providers. Would catch a bug where a USDA exception
    aborts the entire lookup instead of falling through to the next provider.
    """
    usda_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    opener, calls = _multi_urlopen(
        {
            usda_url: OSError("usda unavailable"),
            FATSECRET_TOKEN_URL: FATSECRET_TOKEN_PAYLOAD,
            FATSECRET_SEARCH_URL: FATSECRET_SEARCH_PAYLOAD,
        }
    )
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(
        usda_api_key="test-key",
        fatsecret_client_id="id",
        fatsecret_client_secret="secret",
    )
    macros = agent._query_macros_per_100g("kale")
    assert macros["source"] == "fatsecret_platform"
    assert calls[usda_url] == 1
    assert calls[FATSECRET_TOKEN_URL] == 1
    assert calls[FATSECRET_SEARCH_URL] == 1


def test_fatsecret_error_payload_is_treated_as_a_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A FatSecret response carrying an ``error`` object must raise, not be
    silently returned as if it were valid macro data.

    Would catch a bug where FatSecret's documented error-payload shape (HTTP
    200 with an ``{"error": {...}}`` body) is treated as a successful lookup.
    """
    opener, calls = _multi_urlopen(
        {
            FATSECRET_TOKEN_URL: FATSECRET_TOKEN_PAYLOAD,
            FATSECRET_SEARCH_URL: {"error": {"code": 5, "message": "Invalid search_expression"}},
        }
    )
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    macros = agent._query_macros_per_100g("kale")
    assert macros["source"] not in {"usda_fooddata_central", "fatsecret_platform"}
    assert agent._fatsecret_consecutive_failures == 1
    assert calls[FATSECRET_SEARCH_URL] == 1


def test_fatsecret_empty_results_fall_back_to_a_local_estimate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty FatSecret food list must degrade to the local estimate.

    Would catch an ``IndexError`` if ``foods[0]`` is accessed without first
    checking that FatSecret actually returned a match.
    """
    opener, calls = _multi_urlopen(
        {
            FATSECRET_TOKEN_URL: FATSECRET_TOKEN_PAYLOAD,
            FATSECRET_SEARCH_URL: {"foods": {}},
        }
    )
    monkeypatch.setattr(module, "urlopen", opener)
    agent = NutritionVerificationAgent(fatsecret_client_id="id", fatsecret_client_secret="secret")
    macros = agent._query_macros_per_100g("a very obscure ingredient")
    assert macros["calories"] > 0
    assert macros["source"] not in {"usda_fooddata_central", "fatsecret_platform"}
    assert calls[FATSECRET_SEARCH_URL] == 1


def test_parse_fatsecret_description_rejects_a_partial_match() -> None:
    """A description with the "per 100g" marker but a missing macro field
    must return ``None`` rather than a partially-filled dict.

    Would catch a bug where one missing regex match (e.g. FatSecret omitting
    "Carbs" for a zero-carb item written differently) still returns whatever
    fields did match, silently corrupting downstream totals with missing keys.
    """
    agent = NutritionVerificationAgent()
    macros = agent._parse_fatsecret_description(
        "Per 100g - Calories: 165kcal | Fat: 3.60g | Protein: 31.00g"
    )
    assert macros is None
