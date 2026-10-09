#!/usr/bin/env bash
# G5b smoke test: build and start the compose stack from this checkout, then
# check what the gate asks for. Used by CI; runnable locally with Docker:
#
#   scripts/container_smoke.sh
#
# Exits non-zero on the first failed check, and always tears the stack down.
set -euo pipefail

API=http://127.0.0.1:8000
UI=http://127.0.0.1:8501

cleanup() { docker compose down --volumes --remove-orphans >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker compose up --build --detach --wait --wait-timeout 180

check() { python3 -c "import json,sys; d=json.load(sys.stdin); $1" ; }

echo "1. /health answers 200 and reports the deployment facts"
curl -fsS "$API/health" | check '
s = d["services"]
assert d["status"] == "ok", d
for key in ("storage_backend", "hosted_mode", "gemini_configured", "usda_configured"):
    assert key in s, f"missing {key}"
assert s["hosted_mode"] is False, s["hosted_mode"]
print("   storage_backend=%s hosted_mode=%s" % (s["storage_backend"], s["hosted_mode"]))'

echo "2. history starts empty: no data was imported at build or start"
curl -fsS "$API/meal-plans/user_123" | check 'assert d["items"] == [], d["items"]'
docker compose exec -T api sh -c 'ls -A database' | python3 -c '
import sys
files = sys.stdin.read().split()
assert not any(f.endswith(".json") for f in files), f"JSON history in image: {files}"
print("   database/:", files)'

echo "3. the image carries no local secrets"
docker compose exec -T api sh -c 'test ! -e .env && test ! -e backend/.env && test ! -e .streamlit/secrets.toml'

echo "4. a meal plan is generated offline"
curl -fsS -X POST "$API/generate-meal-plan" -H 'Content-Type: application/json' \
  -d '{"craving": "pasta"}' | check '
assert d["plan_status"] in {"matched", "fallback"}, d["plan_status"]
print("   plan_status=%s" % d["plan_status"])'

echo "5. the Streamlit client is up against the API"
curl -fsS "$UI/_stcore/health" >/dev/null

echo "container smoke test passed"
