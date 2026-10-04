#!/usr/bin/env bash
source "$(dirname "$0")/demo-common.sh"
need curl
[[ -x "$API_PY" ]] || fail 'Run (cd api && uv sync) first.'
ADDRESSES=${DEMO_ADDRESSES:-$ROOT/demo/addresses.txt}
[[ -f "$ADDRESSES" ]] || fail "Missing address list: $ADDRESSES"
healthy "$API_BASE_URL/health" || fail "Start the API first (make demo): $API_BASE_URL/health"
printf '%s demo addresses through %s; responses: %s\n' "${DEMO_WARM_MODE:-Warming}" "$API_BASE_URL" "$DEMO_LOG_DIR"
count=0 failures=0 forecast_ok=0 forecast_skipped=0 forecast_reused=0 map_ok=0
: > "$DEMO_LOG_DIR/summary.tsv"
: > "$DEMO_LOG_DIR/forecast-cells.txt"
while IFS= read -r address || [[ -n "$address" ]]; do
    [[ -z "$address" || "$address" == \#* ]] && continue
    count=$((count+1))
    payload="$DEMO_LOG_DIR/$count-request.json"
    response="$DEMO_LOG_DIR/$count-estimate.json"
    "$API_PY" -c 'import json,sys; print(json.dumps({"address":sys.argv[1]}))' "$address" > "$payload"
    status=$(curl --noproxy '*' -sS --connect-timeout 3 --max-time 240 -o "$response" -w '%{http_code} %{time_total}' \
        -H 'Content-Type: application/json' --data-binary "@$payload" "$API_BASE_URL/estimate") || status="000 0"
    timing=${status#* }; status=${status%% *}
    if [[ "$status" != 200 ]]; then
        printf 'FAIL estimate HTTP %s (%ss): %s (see %s)\n' "$status" "$timing" "$address" "$response"
        printf 'estimate\t%s\t%s\n' "$status" "$address" >> "$DEMO_LOG_DIR/summary.tsv"
        failures=$((failures+1)); continue
    fi
    if ! "$API_PY" - "$response" > "$DEMO_LOG_DIR/$count-fields.txt" <<'PY'
import json, math, sys
from urllib.parse import quote
r=json.load(open(sys.argv[1])); b=r['building']; annual=r['bill']['annual']['p50']
assert isinstance(annual,(float,int)) and math.isfinite(annual) and annual >= 0
assert b['type'] and b['sqft'] > 0 and b['footprint_geojson'] and r['heating_cooling']
print(annual)
print(quote(str(r.get('session_id') or '__demo_no_session__'),safe=''))
location=next(loc for loc in (r.get("model_params") or {}, r["heating_cooling"].get("location") or {}, b) if loc.get("lat") is not None and loc.get("lon") is not None)
print(f"{round(round(location['lat']/0.1)*0.1,2):.2f},{round(round(location['lon']/0.1)*0.1,2):.2f}")
PY
    then
        printf 'FAIL invalid estimate response: %s\n' "$address"
        failures=$((failures+1)); continue
    fi
    annual=$(sed -n '1p' "$DEMO_LOG_DIR/$count-fields.txt")
    session=$(sed -n '2p' "$DEMO_LOG_DIR/$count-fields.txt")
    cell=$(sed -n '3p' "$DEMO_LOG_DIR/$count-fields.txt")
    printf 'PASS estimate (%ss): %s | annual heating+cooling $%s | weather cell %s\n' "$timing" "$address" "$annual" "$cell"
    printf 'estimate\t200\t%s\n' "$address" >> "$DEMO_LOG_DIR/summary.tsv"
    map_response="$DEMO_LOG_DIR/$count-map.json"
    status=$(curl --noproxy '*' -sS --connect-timeout 3 --max-time 300 -o "$map_response" -w '%{http_code} %{time_total}' \
        "$API_BASE_URL/map/$session") || status="000 0"
    timing=${status#* }; status=${status%% *}
    if [[ "$status" == 200 ]] && "$API_PY" -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["building"] and "steps" in r and "block_group" in r' "$map_response"; then
        printf 'PASS map (%ss): %s\n' "$timing" "$address"
        map_ok=$((map_ok+1))
    else
        printf 'FAIL map HTTP %s (%ss): %s (see %s)\n' "$status" "$timing" "$address" "$map_response"
        failures=$((failures+1))
    fi
    printf 'map\t%s\t%s\n' "$status" "$address" >> "$DEMO_LOG_DIR/summary.tsv"
    # Warm one returned session per model weather cell, not every listing.
    if grep -Fxq -- "$cell" "$DEMO_LOG_DIR/forecast-cells.txt"; then
        printf 'SKIP forecast: weather cell %s already checked in this run.\n' "$cell"
        forecast_reused=$((forecast_reused+1))
        printf 'forecast\treused_cell\t%s\n' "$address" >> "$DEMO_LOG_DIR/summary.tsv"
        continue
    fi
    printf '%s\n' "$cell" >> "$DEMO_LOG_DIR/forecast-cells.txt"
    forecast="$DEMO_LOG_DIR/$count-forecast.json"
    status=$(curl --noproxy '*' -sS --connect-timeout 3 --max-time 300 -o "$forecast" -w '%{http_code} %{time_total}' \
        "$API_BASE_URL/forecast/$session") || status="000 0"
    timing=${status#* }; status=${status%% *}
    if [[ "$status" == 404 ]]; then
        printf 'SKIP forecast HTTP 404: %s (route/session unavailable)\n' "$address"
        forecast_skipped=$((forecast_skipped+1))
    elif [[ "$status" == 200 ]] && "$API_PY" -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["days"] and "total_usd" in r["week"]' "$forecast"; then
        printf 'PASS forecast (%ss): %s\n' "$timing" "$address"
        forecast_ok=$((forecast_ok+1))
    else
        printf 'FAIL forecast HTTP %s (%ss): %s (see %s)\n' "$status" "$timing" "$address" "$forecast"
        failures=$((failures+1))
    fi
    printf 'forecast\t%s\t%s\n' "$status" "$address" >> "$DEMO_LOG_DIR/summary.tsv"
done < "$ADDRESSES"
city_response="$DEMO_LOG_DIR/city.json"
status=$(curl --noproxy '*' -sS --compressed --connect-timeout 3 --max-time 300 -o "$city_response" -w '%{http_code} %{time_total}' "$API_BASE_URL/city") || status="000 0"
timing=${status#* }; status=${status%% *}
if [[ "$status" == 200 ]] && "$API_PY" -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["type"] == "FeatureCollection" and r["features"]' "$city_response"; then
    printf 'PASS city (%ss)\n' "$timing"
else
    printf 'FAIL city HTTP %s (%ss; see %s)\n' "$status" "$timing" "$city_response"
    failures=$((failures+1))
fi
printf 'city\t%s\tcitywide\n' "$status" >> "$DEMO_LOG_DIR/summary.tsv"
printf 'Map warm: %s/%s sessions.\n' "$map_ok" "$count"
printf 'RESULT: %s addresses; %s forecast successes; %s forecast 404 skips; %s cells reused; %s failures.\n' "$count" "$forecast_ok" "$forecast_skipped" "$forecast_reused" "$failures"
[[ "$count" -gt 0 && "$failures" == 0 ]]
