"""The optional Gemini explanation step: client-safe when it fails.

Agent log, 2026-10-10 (raised in G10b, kept separate by Codex): when Gemini
failed, the exception's text was appended to the response's
``metadata.warnings``. A provider error can quote request details, quota or
key status, so the client gets a fixed warning and the log gets the exception
type only, as G3 does for every other error.
"""

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.app.agents.meal_recommendation_agent import MealRecommendationAgent
from backend.app.repositories.json_store import UserProfileRepository

CORPUS_PATH = Path(__file__).resolve().parents[2] / "data" / "meal_corpus" / "meals.json"
MARK = "zq7marker-provider-detail"


class _Models:
    def __init__(self, outcome: object) -> None:
        self.outcome = outcome

    def generate_content(self, **_: object) -> object:
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return SimpleNamespace(text=self.outcome)


def _agent(tmp_path: Path, outcome: object) -> MealRecommendationAgent:
    agent = MealRecommendationAgent(
        db_connection=UserProfileRepository(tmp_path),
        meal_corpus_path=CORPUS_PATH,
        enable_llm_adaptation=True,
    )
    # Stand in for a configured google-genai client; no network is used.
    agent.model = SimpleNamespace(models=_Models(outcome))
    agent.types = SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs)
    return agent


def _payload(agent: MealRecommendationAgent):  # noqa: ANN202 - MealPlanPayload
    return agent.generate_meal_payload(
        craving="fried rice", user_id="user_123", daily_calorie_target=2200
    )


def test_a_gemini_failure_gives_the_client_a_fixed_warning(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    agent = _agent(tmp_path, RuntimeError(f"400 INVALID_ARGUMENT {MARK}"))

    with caplog.at_level(logging.WARNING):
        payload = _payload(agent)

    assert "Gemini final explanation unavailable." in payload.metadata.warnings
    assert MARK not in payload.model_dump_json()
    assert "Gemini final explanation failed: RuntimeError" in caplog.text
    assert MARK not in caplog.text
    assert "gemini" not in payload.metadata.source


def test_a_gemini_explanation_is_used_when_it_succeeds(tmp_path: Path) -> None:
    agent = _agent(tmp_path, '{"explanation": "Balanced and quick."}')

    payload = _payload(agent)

    assert payload.metadata.explanation == "Balanced and quick."
    assert payload.metadata.source.endswith("+gemini_final_explanation")
    assert "Gemini used only for final explanation." in payload.metadata.warnings
