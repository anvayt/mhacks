#!/usr/bin/env bash
# Citywide cache warm for judges' own addresses (api/scripts/warm_city.py). Sequential GETs to the
# model's existing :8001 server, Open-Meteo and TIGERweb; never starts/stops services or sends texts.
source "$(dirname "$0")/demo-common.sh"
[[ -x "$API_PY" ]] || fail 'Run (cd api && uv sync) first.'
cd "$ROOT/api"
"$API_PY" scripts/warm_city.py 2>&1 | tee "$DEMO_LOG_DIR/warm-city.log"
