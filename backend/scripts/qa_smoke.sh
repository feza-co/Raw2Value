#!/usr/bin/env bash
# Raw2Value AI — full QA smoke (G4 gate).
# Pre: docker compose up -d --build && docker compose exec api alembic upgrade head
# Run: bash backend/scripts/qa_smoke.sh
set -euo pipefail

BASE=${BASE:-http://localhost:8000}
EMAIL=${QA_EMAIL:-qa@test.local}
PASS=${QA_PASSWORD:-qatest12345}

ok()   { echo "OK $*"; }
fail() { echo "FAIL $*" >&2; exit 1; }

echo "1. Health"
curl -sf "$BASE/health" | jq . > /dev/null && ok "/health"

echo "2. FX"
curl -sf "$BASE/api/fx/current" | jq . > /dev/null && ok "/api/fx/current"

echo "3. Register + Login"
curl -sf -X POST "$BASE/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\",\"full_name\":\"QA\"}" \
  > /dev/null || true   # Idempotent: 409 dönebilir, sorun değil

TOKEN=$(curl -sf -X POST "$BASE/api/auth/login" \
  -d "username=$EMAIL&password=$PASS" | jq -r .access_token)
[ -n "$TOKEN" ] && [ "$TOKEN" != "null" ] || fail "login token alınamadı"
ok "/api/auth/login token=${TOKEN:0:20}..."

echo "4. Me"
curl -sf "$BASE/api/auth/me" -H "Authorization: Bearer $TOKEN" | jq . > /dev/null && ok "/api/auth/me"

echo "5. Analyze"
curl -sf -X POST "$BASE/api/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"raw_material":"pomza","tonnage":150,"quality":"A","origin_city":"Nevşehir","target_country":"DE","target_city":"Hamburg","transport_mode":"kara","priority":"max_profit","input_mode":"basic"}' \
  | jq -e '.recommended_route and .request_id' > /dev/null && ok "/api/analyze"

echo "6. What-if"
curl -sf -X POST "$BASE/api/what-if" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "base_payload": {"raw_material":"pomza","tonnage":150,"quality":"A","origin_city":"Nevşehir","target_country":"DE","target_city":"Hamburg","transport_mode":"kara","priority":"max_profit","input_mode":"basic"},
    "scenarios": [{"name":"a","fx_scenario_pct":-0.1},{"name":"b","fx_scenario_pct":0.1}]
  }' | jq -e '.results | length == 2' > /dev/null && ok "/api/what-if"

echo "7. Model Evidence"
curl -sf "$BASE/api/model-evidence" | jq -e '.profit_regression.best_model == "catboost"' > /dev/null && ok "/api/model-evidence"

echo
echo "ALL OK (7/7)"
