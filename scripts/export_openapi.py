"""Write the API's OpenAPI document to docs/openapi.json (direction item G).

The committed file is the reviewable API contract.
``backend/tests/test_openapi_contract.py`` fails whenever the code drifts from
it, so after a deliberate contract change, run this and commit the diff:

    uv run python scripts/export_openapi.py

The document is generated in a fresh process with no settings in its
environment and the dotenv file skipped. Every setting, the title from
APP_NAME included, therefore takes its default from the code, and neither a
developer's shell nor backend/.env can change the contract. A running
deployment's own /openapi.json still reflects its configuration.
"""

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "docs" / "openapi.json"
_GENERATE = "import json; from backend.app.main import app; print(json.dumps(app.openapi()))"
# What the interpreter itself needs; anything else could be a setting.
_INTERPRETER_VARIABLES = ("PATH", "SYSTEMROOT")


def contract_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """The environment the contract is generated in: no settings, no dotenv.

    Args:
        environ: The caller's environment.

    Returns:
        Only the interpreter's own variables, plus PYTHONPATH and a forced
        SKIP_DOTENV=1.
    """
    kept = {name: environ[name] for name in _INTERPRETER_VARIABLES if name in environ}
    return {**kept, "PYTHONPATH": str(REPO), "SKIP_DOTENV": "1"}


def canonical_document() -> dict[str, Any]:
    """Generate the OpenAPI document with every setting at its code default.

    Returns:
        The document, as FastAPI produces it.
    """
    result = subprocess.run(
        [sys.executable, "-c", _GENERATE],
        env=contract_environment(os.environ),
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
        timeout=180,
    )
    return json.loads(result.stdout)


def main() -> None:
    """Write the canonical document, formatted, to docs/openapi.json."""
    document = canonical_document()
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(document['paths'])} paths to {OUTPUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
