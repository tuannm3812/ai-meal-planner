"""Measure how well generated meal plans hit their calorie target and a balanced macro split.

Runs the fixed scenario set in ``backend/app/evaluation/meal_quality.py``
through the real planning service, offline, and prints a Markdown report:

    uv run python scripts/meal_quality_baseline.py
    uv run python scripts/meal_quality_baseline.py --json docs/meal_quality/baseline.json

Run it before and after a meal-quality change and compare the two reports.
"""

import argparse
import dataclasses
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.app.evaluation.meal_quality import render_markdown, run, summarise  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run the scenarios, print the report and optionally write the rows as JSON."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", type=Path, help="Also write the summary and rows here.")
    args = parser.parse_args(argv)

    rows, provenance = run()
    summary = summarise(rows)
    print(render_markdown(rows, summary, provenance), end="")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "provenance": provenance,
            "summary": dataclasses.asdict(summary),
            "plans": [row.model_dump() for row in rows],
        }
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
