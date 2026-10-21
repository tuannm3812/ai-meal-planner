#!/usr/bin/env bash
# G6 acceptance against a running hosted deployment:
#
#   MEAL_PLANNER_KEY=<raw key> scripts/live_check.sh https://<service-url>
#
# Optional:
#   OLD_KEY=<revoked raw key>   also prove a revoked key is refused (G4)
#   EXPECT_INSTANCES=2          distinct X-Instance-Id values each check needs (default 2)
#   REQUESTS=12                 requests per check, sent in parallel
#   REQUEST_TIMEOUT=60          seconds a request may take in total (default 60)
#   CONNECT_TIMEOUT=10          seconds to connect (default 10)
#
# On Cloud Run, raise --min-instances to at least EXPECT_INSTANCES while this
# runs, so the parallel requests land on more than one instance.
#
# It checks that:
# - /health is public, reports production, and reports hosted mode;
# - each history and feedback route returns 501 history_disabled_stateless;
# - an anonymous request gets 401, and a keyed meal plan gets 200;
# - with OLD_KEY, the revoked key gets 401.
# Every fanned-out check must, on its own, be answered by at least
# EXPECT_INSTANCES distinct instances; a response without an instance id counts
# for none. Every request must be answered in full within REQUEST_TIMEOUT: a
# stalled, refused, dropped or cut-short transfer fails the check, even if its
# status and body looked right so far. This is a sample, so it proves the instances
# that answered, not that no other instance or revision exists.
set -euo pipefail

URL="${1:?usage: MEAL_PLANNER_KEY=... scripts/live_check.sh <url>}"
URL="${URL%/}"
KEY="${MEAL_PLANNER_KEY:?set MEAL_PLANNER_KEY to a raw API key}"
EXPECT_INSTANCES="${EXPECT_INSTANCES:-2}"
REQUESTS="${REQUESTS:-12}"
CURL_LIMITS=(--connect-timeout "${CONNECT_TIMEOUT:-10}" --max-time "${REQUEST_TIMEOUT:-60}")
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# One request; records "<status> <code> <instance>" on one line in $WORK/$label.
probe() {
  local label="$1" method="$2" path="$3" key="$4" body="${5:-}"
  # mktemp, not $RANDOM: parallel subshells can share a RANDOM sequence, and two
  # probes writing the same file corrupt each other's status lines (seen in CI).
  local out headers=(-H 'Content-Type: application/json')
  out="$(mktemp "$WORK/$label.XXXXXX")"
  [ -n "$key" ] && headers+=(-H "X-API-Key: $key")
  local data=()
  [ -n "$body" ] && data=(-d "$body")
  local rc=0
  curl -sS "${CURL_LIMITS[@]}" -o "$out.body" -D "$out.head" -X "$method" "$URL$path" \
    "${headers[@]}" ${data[@]+"${data[@]}"} || rc=$?
  local status code instance
  status="$(head -1 "$out.head" | awk '{print $2}')"
  code="$(python3 -c 'import json,sys
try: print(json.load(open(sys.argv[1])).get("code") or "-")
except Exception: print("-")' "$out.body")"
  instance="$(tr -d '\r' < "$out.head" | awk -F': ' 'tolower($1)=="x-instance-id"{print $2}')"
  # A failed transfer is a failed answer, however right its first bytes look:
  # curl exits non-zero when it times out (28) or the body is cut short (18).
  [ "$rc" -eq 0 ] || status="curl-exit-$rc"
  echo "${status:-no-response} $code ${instance:--}" >> "$WORK/$label"
}

# Send REQUESTS copies in parallel. Every probe must finish, every transfer must
# complete and match, and this check alone must reach EXPECT_INSTANCES ids.
fan_out() {
  local label="$1" want_status="$2" want_code="$3"; shift 3
  local pids=() pid died=0
  for _ in $(seq 1 "$REQUESTS"); do probe "$label" "$@" & pids+=("$!"); done
  # Each probe's own exit status: a bare `wait` ignores it, and a probe that died
  # before recording its answer would silently shrink the sample.
  for pid in "${pids[@]}"; do wait "$pid" || died=$((died + 1)); done
  [ "$died" -eq 0 ] || { echo "   $label: $died probe(s) did not finish"; exit 1; }
  local bad distinct
  bad="$(awk -v s="$want_status" -v c="$want_code" '$1!=s || (c!="*" && $2!=c)' "$WORK/$label")"
  [ -z "$bad" ] || { echo "   $label: unexpected responses:"; echo "$bad" | sort | uniq -c; exit 1; }
  distinct="$(awk '$3!="-"{print $3}' "$WORK/$label" | sort -u | wc -l | tr -d ' ')"
  echo "   $label -> $want_status ${want_code/\*/} x$REQUESTS from $distinct instance(s)"
  [ "$distinct" -ge "$EXPECT_INSTANCES" ] || {
    echo "   $label: only $distinct instance(s) answered; expected at least $EXPECT_INSTANCES"
    exit 1; }
}

echo "1. /health is public, production, hosted"
curl -fsS "${CURL_LIMITS[@]}" "$URL/health" | python3 -c '
import json, sys
d = json.load(sys.stdin)
assert d["environment"] == "production", d["environment"]
assert d["services"]["hosted_mode"] is True, d["services"]
print("   environment=production hosted_mode=True")'

echo "2. each history and feedback route is refused, by at least $EXPECT_INSTANCES instance(s)"
FEEDBACK='{"user_id":"user_123","request_id":"abcdefgh","meal_name":"Meal","liked":true}'
fan_out meal-plans 501 history_disabled_stateless GET /meal-plans/user_123 "$KEY"
fan_out meal-feedback 501 history_disabled_stateless GET /meal-feedback/user_123 "$KEY"
fan_out saved-meals 501 history_disabled_stateless GET /saved-meals/user_123 "$KEY"
fan_out post-feedback 501 history_disabled_stateless POST /meal-feedback "$KEY" "$FEEDBACK"

echo "3. authentication first; meal planning works"
fan_out anonymous 401 missing_or_invalid_api_key GET /meal-plans/user_123 ""
probe generate POST /generate-meal-plan "$KEY" '{"craving": "pasta"}'
read -r status _ _ < "$WORK/generate"
[ "$status" = 200 ] || { echo "   generate -> $status"; exit 1; }
echo "   generate -> 200"

if [ -n "${OLD_KEY:-}" ]; then
  echo "4. the revoked key is refused, by at least $EXPECT_INSTANCES instance(s)"
  fan_out revoked 401 missing_or_invalid_api_key GET /meal-plans/user_123 "$OLD_KEY"
fi

echo "live check passed"
