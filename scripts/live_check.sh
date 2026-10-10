#!/usr/bin/env bash
# G6 acceptance against a running hosted deployment:
#
#   MEAL_PLANNER_KEY=<raw key> scripts/live_check.sh https://<service-url>
#
# Optional:
#   OLD_KEY=<revoked raw key>   also prove a revoked key is refused (G4)
#   EXPECT_INSTANCES=2          distinct X-Instance-Id values required (default 2)
#   REQUESTS=12                 requests per check, sent in parallel
#
# On Cloud Run, raise --min-instances to at least EXPECT_INSTANCES while this
# runs, so the parallel requests land on more than one instance.
#
# It checks that:
# - /health is public, reports production, and reports hosted mode;
# - every history and feedback route returns 501 history_disabled_stateless,
#   and the refusals come from at least EXPECT_INSTANCES instances;
# - an anonymous request gets 401, and a keyed meal plan gets 200;
# - with OLD_KEY, the revoked key gets 401 from at least EXPECT_INSTANCES
#   instances.
set -euo pipefail

URL="${1:?usage: MEAL_PLANNER_KEY=... scripts/live_check.sh <url>}"
URL="${URL%/}"
KEY="${MEAL_PLANNER_KEY:?set MEAL_PLANNER_KEY to a raw API key}"
EXPECT_INSTANCES="${EXPECT_INSTANCES:-2}"
REQUESTS="${REQUESTS:-12}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# One request; records "<status> <code> <instance>" on one line in $WORK/$label.
probe() {
  local label="$1" method="$2" path="$3" key="$4" body="${5:-}"
  local out="$WORK/$label.$RANDOM$RANDOM" headers=(-H 'Content-Type: application/json')
  [ -n "$key" ] && headers+=(-H "X-API-Key: $key")
  local data=()
  [ -n "$body" ] && data=(-d "$body")
  curl -sS -o "$out.body" -D "$out.head" -X "$method" "$URL$path" \
    "${headers[@]}" ${data[@]+"${data[@]}"} || true
  local status code instance
  status="$(head -1 "$out.head" | awk '{print $2}')"
  code="$(python3 -c 'import json,sys
try: print(json.load(open(sys.argv[1])).get("code") or "-")
except Exception: print("-")' "$out.body")"
  instance="$(tr -d '\r' < "$out.head" | awk -F': ' 'tolower($1)=="x-instance-id"{print $2}')"
  echo "$status $code ${instance:--}" >> "$WORK/$label"
}

# Send REQUESTS copies in parallel, then require every line to match and count instances.
fan_out() {
  local label="$1" want_status="$2" want_code="$3"; shift 3
  for _ in $(seq 1 "$REQUESTS"); do probe "$label" "$@" & done
  wait
  local bad distinct
  bad="$(awk -v s="$want_status" -v c="$want_code" '$1!=s || (c!="*" && $2!=c)' "$WORK/$label")"
  [ -z "$bad" ] || { echo "   $label: unexpected responses:"; echo "$bad" | sort | uniq -c; exit 1; }
  distinct="$(awk '$3!="-"{print $3}' "$WORK/$label" | sort -u | wc -l | tr -d ' ')"
  echo "   $label -> $want_status ${want_code/\*/} x$REQUESTS from $distinct instance(s)"
  echo "$distinct" > "$WORK/$label.instances"
}

require_instances() {
  local n
  n="$(cat "$WORK/$1.instances")"
  [ "$n" -ge "$EXPECT_INSTANCES" ] || {
    echo "   $1: only $n instance(s) answered; expected at least $EXPECT_INSTANCES"; exit 1; }
}

echo "1. /health is public, production, hosted"
curl -fsS "$URL/health" | python3 -c '
import json, sys
d = json.load(sys.stdin)
assert d["environment"] == "production", d["environment"]
assert d["services"]["hosted_mode"] is True, d["services"]
print("   environment=production hosted_mode=True")'

echo "2. history and feedback are refused by every instance"
FEEDBACK='{"user_id":"user_123","request_id":"abcdefgh","meal_name":"Meal","liked":true}'
fan_out meal-plans 501 history_disabled_stateless GET /meal-plans/user_123 "$KEY"
fan_out meal-feedback 501 history_disabled_stateless GET /meal-feedback/user_123 "$KEY"
fan_out saved-meals 501 history_disabled_stateless GET /saved-meals/user_123 "$KEY"
fan_out post-feedback 501 history_disabled_stateless POST /meal-feedback "$KEY" "$FEEDBACK"
cat "$WORK"/meal-plans "$WORK"/meal-feedback "$WORK"/saved-meals "$WORK"/post-feedback \
  | awk '{print $3}' | sort -u | wc -l | tr -d ' ' > "$WORK/refusals.instances"
require_instances refusals

echo "3. authentication first; meal planning works"
fan_out anonymous 401 missing_or_invalid_api_key GET /meal-plans/user_123 ""
probe generate POST /generate-meal-plan "$KEY" '{"craving": "pasta"}'
read -r status _ _ < "$WORK/generate"
[ "$status" = 200 ] || { echo "   generate -> $status"; exit 1; }
echo "   generate -> 200"

if [ -n "${OLD_KEY:-}" ]; then
  echo "4. the revoked key is refused by every instance"
  fan_out revoked 401 missing_or_invalid_api_key GET /meal-plans/user_123 "$OLD_KEY"
  require_instances revoked
fi

echo "live check passed"
