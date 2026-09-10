"""Loads the JSON reference tables the agents use for local estimates."""

import json
from functools import cache
from pathlib import Path
from typing import Any

REFERENCE_DIR = Path(__file__).resolve().parents[3] / "data" / "reference"


@cache
def load_reference(name: str) -> dict[str, Any]:
    """Load and cache one reference table.

    Args:
        name: File stem under ``data/reference``, e.g. ``ingredient_calories``.

    Returns:
        The parsed JSON object.

    Raises:
        FileNotFoundError: If the table is missing, which is a packaging error
            rather than a runtime condition worth degrading over.
    """
    path = REFERENCE_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
