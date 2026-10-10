#!/usr/bin/env bash
# G6 rehearsal: two hosted-mode instances behind one URL, checked with the same
# scripts/live_check.sh used against a real deployment. Then the key is rotated
# and the deployment rolled, to prove the old key is refused by every instance
# (G4's revocation acceptance).
#
#   scripts/hosted_smoke.sh
#
# Isolated like container_smoke.sh: its own compose project, free port and image
# tag, and the operator's .env bypassed. Throwaway keys are generated per run and
# never leave it.
set -euo pipefail
cd "$(dirname "$0")/.."

free_port() { python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'; }
new_key() { python3 -c 'import secrets; print(secrets.token_urlsafe(24))'; }
# One key record for client "smoke": rotation keeps the client_id, so the namespace.
key_list() { KEY="$1" python3 -c '
import hashlib, json, os
digest = hashlib.sha256(os.environ["KEY"].encode()).hexdigest()
print(json.dumps([{"client_id": "smoke", "key_sha256": digest,
                   "scopes": ["plans:write", "feedback:write", "history:read"]}]))'; }

RUN_ID="hosted-$$-${RANDOM}"
PROJECT="ai-meal-planner-smoke-${RUN_ID}"
export MEAL_PLANNER_IMAGE="ai-meal-planner:smoke-${RUN_ID}"
export HOSTED_PORT
HOSTED_PORT="$(free_port)"

# Defence in depth: compose.hosted.yaml passes no provider keys, but never let an
# operator's real keys or strictness sit in the environment compose reads.
export GEMINI_API_KEY= USDA_API_KEY= FATSECRET_CLIENT_ID= FATSECRET_CLIENT_SECRET= \
  MEAL_PLANNER_API_KEY= REQUIRE_VERIFIED_NUTRITION=0
EMPTY_ENV="$(mktemp)"

compose() {
  docker compose --project-name "$PROJECT" --env-file "$EMPTY_ENV" -f compose.hosted.yaml "$@"
}

cleanup() {
  compose down --volumes --remove-orphans >/dev/null 2>&1 || true
  docker image rm "$MEAL_PLANNER_IMAGE" >/dev/null 2>&1 || true
  rm -f "$EMPTY_ENV"
}
trap cleanup EXIT

URL="http://127.0.0.1:${HOSTED_PORT}"
OLD_KEY="$(new_key)"
NEW_KEY="$(new_key)"

echo "== deployment 1: key A =="
export API_KEYS
API_KEYS="$(key_list "$OLD_KEY")"
compose up --build --detach --wait --wait-timeout 240
MEAL_PLANNER_KEY="$OLD_KEY" scripts/live_check.sh "$URL"

echo "== deployment 2: key A revoked, key B issued, every instance replaced =="
API_KEYS="$(key_list "$NEW_KEY")"
# Recreate the balancer too: nginx resolves upstream names only at start, and the
# replaced API containers may come back on new addresses.
compose up --detach --force-recreate --wait --wait-timeout 240
MEAL_PLANNER_KEY="$NEW_KEY" OLD_KEY="$OLD_KEY" scripts/live_check.sh "$URL"

echo "hosted smoke test passed"
