from pathlib import Path

import pytest

from backend.app.rag.retriever import MealVectorRetriever

CORPUS_PATH = Path("data/meal_corpus/meals.json")


@pytest.mark.parametrize(
    ("query", "expected_meal_id"),
    [
        ("fried rice", "chicken_fried_rice"),
        ("steak", "lean_steak_rice_plate"),
        ("salmon", "salmon_quinoa_plate"),
        ("breakfast oats", "banana_oat_protein_bowl"),
        ("curry", "chickpea_curry_bowl"),
        ("burrito bowl", "vegan_burrito_bowl"),
        ("soup", "chicken_soup_bowl"),
    ],
)
def test_retrieval_quality_common_cravings(query: str, expected_meal_id: str) -> None:
    retriever = MealVectorRetriever(CORPUS_PATH)

    result = retriever.best_match(
        query=query,
        dietary_preferences=["high protein"],
    )

    assert result is not None
    assert result.meal.meal_id == expected_meal_id
    assert result.score >= retriever.min_score


def test_retrieval_regression_shellfish_allergy_excludes_shrimp() -> None:
    retriever = MealVectorRetriever(CORPUS_PATH)

    result = retriever.best_match(
        query="shrimp taco bowl",
        health_conditions=["shellfish allergy"],
    )

    assert result is not None
    assert "shrimp" not in {ingredient.item_name.lower() for ingredient in result.meal.ingredients}


def test_retrieval_regression_gluten_free_keeps_substitutable_burger() -> None:
    retriever = MealVectorRetriever(CORPUS_PATH)

    result = retriever.best_match(
        query="burger",
        dietary_preferences=["gluten free", "high protein"],
    )

    assert result is not None
    assert result.meal.meal_id == "turkey_burger_bowl"
    assert result.substitutions


def test_every_recipe_asked_for_by_name_is_served_under_the_default_profile() -> None:
    """The default profile is dairy-free. "milk" in soy milk and "butter" in peanut
    butter once blocked Vegan Oat Bowl and Peanut Tofu Bowl as dairy, so asking for
    either by name served High-Protein Asian Tofu Noodle Bowl (2026-11-04)."""
    retriever = MealVectorRetriever(CORPUS_PATH)

    for meal in retriever.meals:
        result = retriever.best_match(
            query=meal.name,
            dietary_restrictions=["dairy-free", "high-protein"],
        )
        assert result is not None and result.meal.meal_id == meal.meal_id, meal.name
