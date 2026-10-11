"""Write the API's OpenAPI document to docs/openapi.json (direction item G).

The committed file is the reviewable API contract.
``backend/tests/test_openapi_contract.py`` fails whenever the code drifts from
it, so after a deliberate contract change, run this and commit the diff:

    uv run python scripts/export_openapi.py
"""

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "docs" / "openapi.json"


def main() -> None:
    """Generate the OpenAPI document and write it, formatted, to docs/openapi.json."""
    # The contract depends on the code only, not on a developer's backend/.env.
    os.environ["SKIP_DOTENV"] = "1"
    sys.path.insert(0, str(REPO))
    from backend.app.main import app

    OUTPUT.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(app.openapi()['paths'])} paths to {OUTPUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
