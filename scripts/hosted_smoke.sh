#!/usr/bin/env bash
# G6 smoke test: two hosted-mode API instances behind one URL must both refuse
# history and feedback, while /health stays public and meal planning works.
#
#   scripts/hosted_smoke.sh
#
# Isolated like container_smoke.sh: its own compose project, free port and image
# tag, and the operator's .env is bypassed. A throwaway API key is generated per
# run and never leaves the run.
set -euo pipefail
cd "$(dirname "$0")/.."

free_port() { python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'; }

RUN_ID="hosted-$$-${RANDOM}"
PROJECT="ai-meal-planner-smoke-${RUN_ID}"
export MEAL_PLANNER_IMAGE="ai-meal-planner:smoke-${RUN_ID}"
export HOSTED_PORT
HOSTED_PORT="$(free_port)"

KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
export API_KEYS
API_KEYS="$(KEY="$KEY" python3 -c '
import hashlib, json, os
digest = hashlib.sha256(os.environ["KEY"].encode()).hexdigest()
print(json.dumps([{"client_id": "smoke", "key_sha256": digest,
                   "scopes": ["plans:write", "feedback:write", "history:read"]}]))')"
# Defence in depth: compose.hosted.yaml passes no provider keys, but never let an
# operator's real keys or strictness sit in the environment compose reads.
export GEMINI_API_KEY= USDA_API_KEY= FATSECRET_CLIENT_ID= FATSECRET_CLIENT_SECRET= \
  MEAL_PLANNER_API_KEY= REQUIRE_VERIFIED_NUTRITION=0
EMPTY_ENV="$(mktemp)"
BODY="$(mktemp)"

compose() {
  docker compose --project-name "$PROJECT" --env-file "$EMPTY_ENV" -f compose.hosted.yaml "$@"
}

cleanup() {
  compose down --volumes --remove-orphans >/dev/null 2>&1 || true
  docker image rm "$MEAL_PLANNER_IMAGE" >/dev/null 2>&1 || true
  rm -f "$EMPTY_ENV" "$BODY"
}
trap cleanup EXIT

URL="http://127.0.0.1:${HOSTED_PORT}"
compose up --build --detach --wait --wait-timeout 240

echo "1. /health is public through the shared URL, and reports hosted mode"
curl -fsS "$URL/health" | python3 -c '
import json, sys
d = json.load(sys.stdin)
assert d["environment"] == "production", d["environment"]
assert d["services"]["hosted_mode"] is True, d["services"]
print("   environment=production hosted_mode=True")'

echo "2. every history and feedback route is refused, by both instances"
served=()
for route in "GET /meal-plans/user_123" "GET /meal-feedback/user_123" "GET /saved-meals/user_123" "POST /meal-feedback"; do
  method="${route%% *}"; path="${route#* }"
  for _ in 1 2 3 4; do
    body=()
    if [ "$method" = POST ]; then
      body=(-H 'Content-Type: application/json' \
        -d '{"user_id":"user_123","request_id":"abcdefgh","meal_name":"Meal","liked":true}')
    fi
    # ${body[@]+...}: an empty array is "unbound" under set -u in bash 3.2 (macOS).
    response="$(curl -sS -D - -o "$BODY" -X "$method" "$URL$path" \
      -H "X-API-Key: $KEY" ${body[@]+"${body[@]}"})"
    status="$(printf '%s' "$response" | head -1 | awk '{print $2}')"
    code="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("code"))' "$BODY")"
    instance="$(printf '%s' "$response" | tr -d '\r' | awk -F': ' 'tolower($1)=="x-served-by"{print $2}')"
    [ "$status" = 501 ] && [ "$code" = history_disabled_stateless ] || {
      echo "   $method $path -> $status $code (expected 501 history_disabled_stateless)"; exit 1; }
    served+=("$instance")
  done
  echo "   $method $path -> 501 history_disabled_stateless"
done
distinct="$(printf '%s\n' "${served[@]}" | sort -u | wc -l | tr -d ' ')"
echo "   refusals came from ${distinct} distinct instances: $(printf '%s\n' "${served[@]}" | sort -u | tr '\n' ' ')"
[ "$distinct" -ge 2 ] || { echo "   expected both instances to answer"; exit 1; }

echo "3. authentication still comes first, and meal planning still works"
anonymous="$(curl -s -o /dev/null -w '%{http_code}' "$URL/meal-plans/user_123")"
[ "$anonymous" = 401 ] || { echo "   anonymous -> $anonymous, expected 401"; exit 1; }
curl -fsS -X POST "$URL/generate-meal-plan" -H 'Content-Type: application/json' \
  -H "X-API-Key: $KEY" -d '{"craving": "pasta"}' | python3 -c '
import json, sys
d = json.load(sys.stdin)
assert d["plan_status"] in {"matched", "fallback"}, d
print("   anonymous -> 401; generate -> 200 plan_status=%s" % d["plan_status"])'

echo "hosted smoke test passed"
