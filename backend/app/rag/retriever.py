from dataclasses import dataclass
from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .meal_corpus import MealCorpusItem, load_meal_corpus


@dataclass(frozen=True)
class MealRetrievalResult:
    meal: MealCorpusItem
    score: float
    matched_terms: list[str]
    warnings: list[str]
    rank: int = 0


class MealVectorRetriever:
    def __init__(self, corpus_path: Path, min_score: float = 0.16):
        self.corpus_path = corpus_path
        self.min_score = min_score
        self.meals = load_meal_corpus(corpus_path)
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
        )
        self.document_matrix = self.vectorizer.fit_transform(
            [meal.retrieval_text() for meal in self.meals]
        )

    def retrieve(
        self,
        query: str,
        dietary_restrictions: list[str] | None = None,
        health_conditions: list[str] | None = None,
        dietary_preferences: list[str] | None = None,
        top_k: int = 3,
    ) -> list[MealRetrievalResult]:
        dietary_restrictions = self._normalize_items(dietary_restrictions or [])
        dietary_preferences = self._normalize_items(dietary_preferences or [])
        health_conditions = self._normalize_items(health_conditions or [])

        query_terms = self._content_terms(query)
        expanded_query = " ".join(
            [
                query,
                " ".join(dietary_restrictions),
                " ".join(dietary_preferences),
                " ".join(health_conditions),
            ]
        )
        query_vector = self.vectorizer.transform([expanded_query.lower()])
        similarities = cosine_similarity(query_vector, self.document_matrix).ravel()

        scored_results = []
        for index, meal in enumerate(self.meals):
            craving_overlap = self._craving_overlap(meal, query_terms)
            score = float(similarities[index])
            if query_terms and craving_overlap == 0:
                score *= 0.15
            score += self._preference_bonus(meal, dietary_preferences)
            score += self._preference_bonus(meal, dietary_restrictions)
            score += min(craving_overlap * 0.1, 0.3)
            score -= self._condition_penalty(meal, health_conditions)
            warnings = self._warnings_for(meal, health_conditions)
            scored_results.append(
                MealRetrievalResult(
                    meal=meal,
                    score=round(max(score, 0.0), 4),
                    matched_terms=self._matched_terms(meal, expanded_query),
                    warnings=warnings,
                )
            )

        ranked_results = []
        for rank, result in enumerate(
            sorted(scored_results, key=lambda result: result.score, reverse=True),
            start=1,
        ):
            ranked_results.append(
                MealRetrievalResult(
                    meal=result.meal,
                    score=result.score,
                    matched_terms=result.matched_terms,
                    warnings=result.warnings,
                    rank=rank,
                )
            )
        return ranked_results[:top_k]

    def best_match(
        self,
        query: str,
        dietary_restrictions: list[str] | None = None,
        health_conditions: list[str] | None = None,
        dietary_preferences: list[str] | None = None,
    ) -> MealRetrievalResult | None:
        results = self.retrieve(
            query=query,
            dietary_restrictions=dietary_restrictions,
            health_conditions=health_conditions,
            dietary_preferences=dietary_preferences,
            top_k=1,
        )
        if not results:
            return None
        if results[0].score < self.min_score:
            return None
        return results[0]

    @staticmethod
    def _normalize_items(items: list[str]) -> list[str]:
        return [item.strip().lower().replace("_", " ").replace("-", " ") for item in items if item.strip()]

    @staticmethod
    def _preference_bonus(meal: MealCorpusItem, preferences: list[str]) -> float:
        if not preferences:
            return 0.0
        meal_flags = {flag.lower().replace("-", " ") for flag in meal.dietary_flags}
        meal_tags = {tag.lower().replace("-", " ") for tag in meal.tags}
        matches = sum(1 for preference in preferences if preference in meal_flags or preference in meal_tags)
        return min(matches * 0.08, 0.24)

    @staticmethod
    def _condition_penalty(meal: MealCorpusItem, health_conditions: list[str]) -> float:
        avoid_conditions = {
            condition.lower().replace("-", " ") for condition in meal.avoid_conditions
        }
        matches = sum(1 for condition in health_conditions if condition in avoid_conditions)
        return min(matches * 0.2, 0.5)

    @staticmethod
    def _warnings_for(meal: MealCorpusItem, health_conditions: list[str]) -> list[str]:
        avoid_conditions = {
            condition.lower().replace("-", " ") for condition in meal.avoid_conditions
        }
        return [
            f"{meal.name} may need review for {condition}."
            for condition in health_conditions
            if condition in avoid_conditions
        ]

    @staticmethod
    def _matched_terms(meal: MealCorpusItem, query: str) -> list[str]:
        query_terms = MealVectorRetriever._content_terms(query)
        meal_terms = set(meal.retrieval_text().split())
        return sorted(query_terms & meal_terms)[:12]

    @staticmethod
    def _content_terms(text: str) -> set[str]:
        stop_terms = {
            "high",
            "low",
            "free",
            "protein",
            "dairy",
            "gluten",
            "meal",
            "food",
            "healthy",
            "quick",
        }
        terms = {
            term
            for term in re.findall(r"[a-zA-Z]+", text.lower())
            if len(term) > 2 and term not in stop_terms
        }
        return terms

    @staticmethod
    def _craving_overlap(meal: MealCorpusItem, query_terms: set[str]) -> int:
        if not query_terms:
            return 0
        meal_terms = MealVectorRetriever._content_terms(meal.retrieval_text())
        return len(query_terms & meal_terms)
