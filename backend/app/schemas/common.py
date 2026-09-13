"""Schema fragments shared by more than one agent."""

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    """Provenance and confidence reported by every agent."""

    agent_name: str
    source: str
    confidence: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)


class MealAgentMetadata(AgentMetadata):
    """Meal-agent metadata, which may carry an LLM-generated explanation."""

    explanation: str | None = None


def average_confidence(items: Sequence[Any]) -> float:
    """Average the confidence of scored items.

    Args:
        items: Objects exposing a numeric ``confidence`` attribute.

    Returns:
        The mean confidence rounded to two places, or 0.0 when there is nothing
        to average.
    """
    if not items:
        return 0.0
    return round(sum(item.confidence for item in items) / len(items), 2)
