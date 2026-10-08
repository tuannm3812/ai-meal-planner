"""The deterministic fallback must honour the same hard constraints as retrieval.

Found by Codex on 2026-10-08: with retrieval unavailable, a user with
kidney_disease asking for "tofu" was served firm tofu and soy sauce, because
`generate_meal_payload` called `_fallback_payload` without the user's health
conditions or dietary preferences, and the fallback ran no constraint rules.
"""

from typing import Any

import pytest

from backend.app.agents.meal_recommendation_agent import (
    MealPlanPayload,
    MealRecommendationAgent,
)
from backend.app.core.config import AppSettings
from backend.app.core.exceptions import NoFeasibleMeal, RetrievalUnavailable
from backend.app.rag.rules import blocked_groups_for_ingredient, constraint_groups
from backend.app.repositories.json_store import UserProfileRepository


class _EmptyRetriever:
    """A working retriever whose corpus admits no meal for the request."""

    min_score = 0.16
    active_backend = "stub"

    def retrieve(self, **_: Any) -> list[Any]:
        return []


_REAL = object()


def _agent(retriever: Any = None) -> MealRecommendationAgent:
    """Build an agent; ``retriever=None`` forces the deterministic fallback path."""
    settings = AppSettings.from_env()
    agent = MealRecommendationAgent(
        db_connection=UserProfileRepository(settings.data_dir),
        meal_corpus_path=settings.meal_corpus_path,
    )
    if retriever is not _REAL:
        agent.meal_retriever = retriever
    return agent


def _profile(dietary_restrictions: list[str] | None = None) -> dict[str, Any]:
    return {
        "age": 30,
        "gender": "f",
        "height": 165,
        "weight": 62,
        "workout_level": 1.4,
        "dietary_restrictions": dietary_restrictions or [],
    }


def _generate(
    craving: str,
    *,
    health_conditions: list[str] | None = None,
    dietary_preferences: list[str] | None = None,
    dietary_restrictions: list[str] | None = None,
    retriever: Any = None,
) -> MealPlanPayload:
    return _agent(retriever).generate_meal_payload(
        craving=craving,
        user_id="user_123",
        daily_calorie_target=2200,
        health_conditions=health_conditions,
        dietary_preferences=dietary_preferences,
        profile=_profile(dietary_restrictions),
    )


def _violations(payload: MealPlanPayload, labels: list[str]) -> list[str]:
    groups = constraint_groups(labels)
    return [
        ingredient.item_name
        for ingredient in payload.meal_definition.ingredients
        if blocked_groups_for_ingredient(ingredient.item_name, groups)
    ]


def _names(payload: MealPlanPayload) -> list[str]:
    return [ingredient.item_name for ingredient in payload.meal_definition.ingredients]


def test_kidney_disease_tofu_craving_gets_no_blocked_ingredient() -> None:
    """Codex's probe: retrieval unavailable, kidney_disease, craving "tofu"."""
    payload = _generate("tofu", health_conditions=["kidney_disease"])

    assert payload.metadata.source == "deterministic_fallback"
    assert _violations(payload, ["kidney_disease"]) == [], _names(payload)


def test_unconstrained_fallback_keeps_its_keyword_choice() -> None:
    """Regression guard: with no constraints the keyword match still wins."""
    payload = _generate("tofu")

    assert payload.meal_definition.structured_meal_name == "Tofu Rice Bowl"


def test_fallback_applies_a_substitution_when_one_exists() -> None:
    """A gluten constraint swaps the wheat pasta instead of abandoning the template."""
    payload = _generate("pasta", dietary_preferences=["gluten-free"])

    assert payload.meal_definition.structured_meal_name == "High-Protein Tomato Turkey Pasta"
    assert "wholemeal pasta" not in _names(payload)
    assert "gluten-free pasta" in _names(payload)
    # Not asserted via _violations: the keyword rules match "pasta" inside
    # "gluten-free pasta", so they cannot judge a replacement's own name.
    assert any("substitution" in warning for warning in payload.metadata.warnings)


def test_fallback_honours_profile_dietary_restrictions() -> None:
    """Restrictions stored on the profile bind the fallback too, as in retrieval."""
    payload = _generate("noodle", dietary_restrictions=["soy allergy"])

    assert _violations(payload, ["soy allergy"]) == [], _names(payload)


_VEGAN_KIDNEY = {"health_conditions": ["kidney_disease"], "dietary_preferences": ["vegan"]}


def test_no_safe_template_without_a_retriever_reports_retrieval_unavailable() -> None:
    """Vegan plus kidney disease rules out every fallback template.

    With no retriever, the corpus was never consulted, so the agent cannot claim
    that no meal is feasible - only that retrieval is unavailable (Codex,
    2026-10-08: a 422 here would mask the outage).
    """
    with pytest.raises(RetrievalUnavailable):
        _generate("tofu", **_VEGAN_KIDNEY)


def test_no_safe_template_and_no_safe_corpus_meal_raises_no_feasible_meal() -> None:
    """Only a consulted, exhausted corpus plus exhausted templates is infeasible."""
    with pytest.raises(NoFeasibleMeal):
        _generate("tofu", retriever=_EmptyRetriever(), **_VEGAN_KIDNEY)


def test_a_safe_low_relevance_corpus_meal_beats_giving_up() -> None:
    """Codex's probe: "zzzz", vegan plus kidney disease.

    The corpus holds a safe meal scoring below min_score. The threshold decides
    whether the corpus beats a fallback template; it must not turn "a safe meal
    exists" into "no meal is feasible" when no template is safe.
    """
    payload = _generate("zzzz", retriever=_REAL, **_VEGAN_KIDNEY)

    assert payload.metadata.source == "local_vector_rag_meal_corpus"
    assert _violations(payload, ["kidney_disease", "vegan"]) == [], _names(payload)
    assert any("below the relevance threshold" in w for w in payload.metadata.warnings)


def test_soy_allergy_and_kidney_disease_reject_the_tofu_swap() -> None:
    """Tofu under soy allergy plus kidney disease has no valid substitute.

    The soy rule swaps firm tofu for chickpeas, which fixes the allergy but is
    itself blocked for kidney disease, so the noodle template must be rejected,
    not "fixed".
    """
    payload = _generate(
        "noodle",
        health_conditions=["kidney_disease"],
        dietary_restrictions=["soy allergy"],
    )

    assert _violations(payload, ["kidney_disease", "soy allergy"]) == [], _names(payload)
    assert "chickpeas" not in _names(payload)


def test_a_replacement_is_rechecked_against_the_other_constraints() -> None:
    """Egg allergy swaps whole egg for firm tofu; kidney disease forbids tofu.

    No fallback template contains egg, so this exercises the template check
    directly with a synthetic template.
    """
    template = [{"item_name": "whole egg", "base_quantity_grams": 100}]

    assert (
        MealRecommendationAgent._constrained_ingredients(
            template, constraint_groups(["egg allergy", "kidney_disease"])
        )
        is None
    )
    # Control: with the egg allergy alone the swap to tofu is valid.
    safe = MealRecommendationAgent._constrained_ingredients(
        template, constraint_groups(["egg allergy"])
    )
    assert safe is not None
    assert [ingredient.item_name for ingredient in safe[0]] == ["firm tofu"]
