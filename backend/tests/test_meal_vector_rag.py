from pathlib import Path

from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.rag.retriever import MealVectorRetriever


CORPUS_PATH = Path("data/meal_corpus/meals.json")


class FakeUserProfileRepository:
    def fetch_user_profile(self, user_id: str) -> dict:
        return {
            "age": 28,
            "gender": "m",
            "weight": 80.0,
            "height": 180.0,
            "workout_level": 1.55,
            "dietary_restrictions": ["dairy-free", "high-protein"],
        }


def test_vector_retriever_matches_fried_rice() -> None:
    retriever = MealVectorRetriever(CORPUS_PATH)

    result = retriever.best_match(
        query="fried rice",
        dietary_restrictions=["dairy-free"],
        dietary_preferences=["high protein"],
    )

    assert result is not None
    assert "fried_rice" in result.meal.meal_id
    assert result.score >= retriever.min_score


def test_meal_agent_uses_vector_rag_before_gemini() -> None:
    agent = MealRecommendationAgent(
        db_connection=FakeUserProfileRepository(),
        gemini_api_key=None,
        meal_corpus_path=CORPUS_PATH,
    )

    payload = agent.generate_meal_payload(
        craving="fried rice",
        user_id="user_123",
        dietary_preferences=["high protein"],
    )

    assert payload.metadata.source == "local_vector_rag_meal_corpus"
    assert "Fried Rice" in payload.meal_definition.structured_meal_name
    assert any(
        ingredient.item_name in {"chicken breast", "firm tofu"}
        for ingredient in payload.meal_definition.ingredients
    )


def test_vector_retriever_respects_primary_craving() -> None:
    retriever = MealVectorRetriever(CORPUS_PATH)

    result = retriever.best_match(
        query="steak",
        dietary_restrictions=["dairy-free"],
        dietary_preferences=["high protein"],
    )

    assert result is not None
    assert "steak" in result.meal.meal_id
    assert "Steak" in result.meal.name
