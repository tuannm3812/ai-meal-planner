"""Tests for the shared schema helpers."""

import pytest
from pydantic import BaseModel, Field

from backend.app.schemas.common import AgentMetadata, MealAgentMetadata, average_confidence


class _Scored(BaseModel):
    confidence: float = Field(ge=0, le=1)


def test_agent_metadata_has_no_explanation_field() -> None:
    """The base metadata must not add an explanation key to agent responses."""
    assert "explanation" not in AgentMetadata.model_fields


def test_meal_agent_metadata_adds_explanation() -> None:
    """Only the meal agent carries an explanation."""
    assert "explanation" in MealAgentMetadata.model_fields
    assert MealAgentMetadata(agent_name="a", source="s", confidence=0.5).explanation is None


def test_average_confidence_rounds_to_two_places() -> None:
    """Matches Python's built-in round() (banker's rounding), like the code it replaces.

    (0.5 + 0.75) / 2 == 0.625, which round(x, 2) rounds to 0.62, not 0.63 -- both
    pre-existing _average_confidence implementations used the same round() call and
    would produce the identical result, so this is not a behaviour change.
    """
    assert average_confidence([_Scored(confidence=0.5), _Scored(confidence=0.75)]) == 0.62


def test_average_confidence_of_nothing_is_zero() -> None:
    """An empty list must not raise ZeroDivisionError."""
    assert average_confidence([]) == 0.0


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_agent_metadata_rejects_out_of_range_confidence(bad: float) -> None:
    with pytest.raises(ValueError):
        AgentMetadata(agent_name="a", source="s", confidence=bad)
