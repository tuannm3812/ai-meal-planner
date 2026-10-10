#!/usr/bin/env bash
# G5b smoke test: build and start the compose stack from this checkout, then
# check what the gate asks for. Used by CI; runnable locally with Docker:
#
#   scripts/container_smoke.sh
#
# Isolation (Codex P2s, 2026-10-10):
# - It runs as its own compose project, with its own free ports and its own image
#   tag, so it never reuses, recreates or removes a developer's running stack.
#   Cleanup removes only this run's containers, volumes and image.
# - It pins its own configuration and bypasses the operator's .env, so the API is
#   open, keyless and offline whatever the shell or .env says. The resolved
#   values are checked inside the container.
#
# Exits non-zero on the first failed check, and always cleans up its own run.
set -euo pipefail
cd "$(dirname "$0")/.."

free_port() { python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'; }

RUN_ID="smoke-$$-${RANDOM}"
PROJECT="ai-meal-planner-${RUN_ID}"
export MEAL_PLANNER_IMAGE="ai-meal-planner:${RUN_ID}"
export API_PORT UI_PORT
API_PORT="$(free_port)"
UI_PORT="$(free_port)"

# Smoke-only configuration. Exported values win over the shell's, and the empty
# --env-file below replaces the root .env compose would otherwise read.
export APP_ENV=development STORAGE_BACKEND=sqlite API_KEYS= RATE_LIMIT_PER_MINUTE=60 \
  REQUIRE_VERIFIED_NUTRITION=0 GEMINI_API_KEY= USDA_API_KEY= FATSECRET_CLIENT_ID= \
  FATSECRET_CLIENT_SECRET= MEAL_PLANNER_API_KEY= \
  ALLOWED_ORIGINS="http://localhost:${UI_PORT}"
EMPTY_ENV="$(mktemp)"

compose() {
  docker compose --project-name "$PROJECT" --env-file "$EMPTY_ENV" -f compose.yaml "$@"
}

cleanup() {
  compose down --volumes --remove-orphans >/dev/null 2>&1 || true
  docker image rm "$MEAL_PLANNER_IMAGE" >/dev/null 2>&1 || true
  rm -f "$EMPTY_ENV"
}
trap cleanup EXIT

API="http://127.0.0.1:${API_PORT}"
UI="http://127.0.0.1:${UI_PORT}"

compose up --build --detach --wait --wait-timeout 180

check() { python3 -c "import json,sys; d=json.load(sys.stdin); $1" ; }

echo "0. the smoke configuration is what actually runs (project ${PROJECT})"
compose exec -T api sh -c 'test -z "$API_KEYS" && test -z "$GEMINI_API_KEY" && test -z "$USDA_API_KEY" && test "$REQUIRE_VERIFIED_NUTRITION" = 0'

echo "1. /health answers 200 and reports the deployment facts"
curl -fsS "$API/health" | check '
s = d["services"]
assert d["status"] == "ok", d
for key in ("storage_backend", "hosted_mode", "gemini_configured", "usda_configured"):
    assert key in s, f"missing {key}"
assert s["hosted_mode"] is False, s["hosted_mode"]
assert s["gemini_configured"] is False and s["usda_configured"] is False, s
print("   storage_backend=%s hosted_mode=%s" % (s["storage_backend"], s["hosted_mode"]))'

echo "2. history starts empty: no data was imported at build or start"
curl -fsS "$API/meal-plans/user_123" | check 'assert d["items"] == [], d["items"]'
compose exec -T api sh -c 'ls -A database' | python3 -c '
import sys
files = sys.stdin.read().split()
assert not any(f.endswith(".json") for f in files), f"JSON history in image: {files}"
print("   database/:", files)'

echo "3. the image carries no local secrets"
compose exec -T api sh -c 'test ! -e .env && test ! -e backend/.env && test ! -e .streamlit/secrets.toml'

echo "4. a meal plan is generated offline"
curl -fsS -X POST "$API/generate-meal-plan" -H 'Content-Type: application/json' \
  -d '{"craving": "pasta"}' | check '
assert d["plan_status"] in {"matched", "fallback"}, d["plan_status"]
print("   plan_status=%s" % d["plan_status"])'

echo "5. the Streamlit client is up, and reaches the API at its configured URL"
curl -fsS "$UI/_stcore/health" >/dev/null
compose exec -T streamlit python -c '
import json, os, urllib.request
url = os.environ["API_BASE_URL"] + "/health"
body = json.load(urllib.request.urlopen(url, timeout=5))
assert body["status"] == "ok", body
print("   streamlit -> %s: ok" % url)'

echo "6. a restart keeps history; a redeploy (new container) starts empty"
# Check 4 saved one plan. Stateless v1 means a *new* container starts empty; a
# restart of the same container keeps its writable layer (Codex, 2026-10-10).
count() { curl -fsS "$API/meal-plans/user_123" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["items"]))'; }
[ "$(count)" = 1 ] || { echo "   expected the plan from check 4 to be stored"; exit 1; }
compose restart api >/dev/null
compose up --detach --wait --wait-timeout 120 api >/dev/null
[ "$(count)" = 1 ] || { echo "   a restart lost history; expected it to be kept"; exit 1; }
compose up --detach --force-recreate --no-deps --wait --wait-timeout 120 api >/dev/null
[ "$(count)" = 0 ] || { echo "   a recreated container kept history; expected it empty"; exit 1; }
echo "   after restart: 1 plan; after recreate: 0 plans"

echo "container smoke test passed"
