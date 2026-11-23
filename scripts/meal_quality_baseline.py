"""Measure how well generated meal plans hit their calorie target and a balanced macro split.

Runs the fixed scenario set in ``backend/app/evaluation/meal_quality.py``
through the real planning service, offline, and prints a Markdown report:

    uv run python scripts/meal_quality_baseline.py
    uv run python scripts/meal_quality_baseline.py --json docs/meal_quality/baseline.json
    uv run python scripts/meal_quality_baseline.py --wider
    uv run python scripts/meal_quality_baseline.py --workouts
    uv run python scripts/meal_quality_baseline.py --usda

Run it before and after a meal-quality change and compare the two reports. It
exits 1 when a guardrail (a fixed fallback or refusal case) does not hold.

``--wider`` runs the wider recipe check instead: every corpus recipe's name as
a craving for the first two profiles (152 requests), reported on its own and
without the guardrails. ``--workouts`` runs six stated workouts, from a rest day
to 90 minutes, for every profile (144 requests), and reports each day's budget
next to the exercise its activity level already counts.

``--usda`` looks ingredients up in USDA FoodData Central (P4). The key comes
from ``USDA_API_KEY`` in the shell or ``backend/.env``, never the command line,
so it stays out of shell history. A USDA run is live data, not deterministic;
it exits 2 when no key is set or no lookup succeeded, rather than report the
local tables as USDA numbers. It combines with the fixed set or ``--wider``.
"""

import argparse
import dataclasses
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.app.core.config import AppSettings  # noqa: E402
from backend.app.evaluation.meal_quality import (  # noqa: E402
    render_guardrails,
    render_markdown,
    run,
    run_guardrails,
    summarise,
    wider_scenarios,
)
from backend.app.evaluation.workouts import render_workouts, run_workouts  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run the scenarios and guardrails, print the report and optionally write JSON.

    Returns:
        0, or 1 when a guardrail did not produce its expected outcome.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", type=Path, help="Also write the summary and rows here.")
    parser.add_argument(
        "--wider",
        action="store_true",
        help="Run every corpus recipe as a craving (152 requests) instead of the fixed set.",
    )
    parser.add_argument(
        "--workouts",
        action="store_true",
        help="Run six stated workouts for every profile (144 requests) instead of the fixed set.",
    )
    parser.add_argument(
        "--usda",
        action="store_true",
        help="Verify nutrition against USDA FoodData Central (needs USDA_API_KEY).",
    )
    args = parser.parse_args(argv)
    if args.wider and args.workouts:
        parser.error("choose one of --wider and --workouts")
    if args.usda and args.workouts:
        parser.error("--usda runs with the fixed set or --wider, not --workouts")

    usda_api_key = None
    if args.usda:
        usda_api_key = AppSettings().usda_api_key
        if not usda_api_key:
            print("--usda needs USDA_API_KEY in the shell or backend/.env.", file=sys.stderr)
            return 2

    days = []
    if args.workouts:
        rows, days, provenance = run_workouts()
    else:
        rows, provenance = run(wider_scenarios() if args.wider else None, usda_api_key=usda_api_key)
    if args.usda and not provenance.get("usda_ingredients_cached"):
        print(
            f"No USDA lookup succeeded ({provenance.get('usda_lookup_failures', 0)} failed); "
            "check the key and the network.",
            file=sys.stderr,
        )
        return 2
    summary = summarise(rows)
    fixed_set = not (args.wider or args.workouts)
    guardrails = run_guardrails() if fixed_set else []
    print(render_markdown(rows, summary, provenance), end="")
    if fixed_set:
        print(render_guardrails(guardrails), end="")
    if args.workouts:
        print(render_workouts(days), end="")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "provenance": provenance,
            "summary": dataclasses.asdict(summary),
            "plans": [row.model_dump() for row in rows],
        }
        if args.workouts:
            payload["workout_days"] = [dataclasses.asdict(day) for day in days]
        if fixed_set:
            payload["guardrails"] = [result.model_dump() for result in guardrails]
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    failed = [result.scenario for result in guardrails if not result.as_expected]
    if failed:
        print(f"Guardrails not as expected: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
