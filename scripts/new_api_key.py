"""Generate an API key and the API_KEYS record that authorises it (G4).

    python scripts/new_api_key.py <client_id> [scope ...]

Prints JSON with the raw `key`, which is shown once: give it to the client and
do not store it. It also prints the `record`, which goes into the API_KEYS
list, holding only the key's SHA-256 hash. Scopes default to all three.
Reusing a client_id when rotating keeps that client's history namespace.
Standard library only, so it runs anywhere Python does.
"""

import hashlib
import json
import secrets
import sys

SCOPES = ("plans:write", "feedback:write", "history:read")


def main(argv: list[str]) -> int:
    """Print a new key and its record.

    Args:
        argv: The client id, then optional scopes.

    Returns:
        Process exit code.
    """
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    client_id, *scopes = argv
    scopes = scopes or list(SCOPES)
    unknown = sorted(set(scopes) - set(SCOPES))
    if unknown:
        print(f"unknown scope(s) {unknown}; choose from {list(SCOPES)}", file=sys.stderr)
        return 2
    key = secrets.token_urlsafe(32)
    record = {
        "client_id": client_id,
        "key_sha256": hashlib.sha256(key.encode("utf-8")).hexdigest(),
        "scopes": scopes,
    }
    print(json.dumps({"key": key, "record": record}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
