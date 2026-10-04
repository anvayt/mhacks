#!/usr/bin/env bash
source "$(dirname "$0")/demo-common.sh"
need curl; need npm; need make; need script
[[ -x "$API_PY" ]] || fail 'Run (cd api && uv sync) first.'
[[ -d "$ROOT/web/node_modules" && -d "$ROOT/agent/node_modules" ]] || fail 'Run npm ci in web and agent first.'
process_tracking
printf 'Demo logs: %s\n' "$DEMO_LOG_DIR"

if healthy 'http://localhost:8001/hc/answers'; then
    printf 'Reusing healthy model on :8001 (not owned by this run).\n'
else
    port_used 8001 && fail 'Port 8001 is occupied but the model health check failed; leaving it untouched.'
    [[ -x "$MODEL_DIR/.venv/bin/python" && -f "$MODEL_DIR/model/artifacts/resstock_hc.pkl" ]] || fail 'MODEL_DIR must point to an already-built model checkout; this command never builds it.'
    start_owned model "$MODEL_DIR" make -C model dashboard
    wait_healthy model 'http://localhost:8001/hc/answers' "$LAST_PID" 120
fi
export MODEL_BASE_URL=http://localhost:8001
export API_BASE_URL=http://localhost:8000
export NEXT_PUBLIC_API_BASE_URL=$API_BASE_URL
export NEXT_PUBLIC_ONBOARD_URL=${NEXT_PUBLIC_ONBOARD_URL:-http://localhost:8787}
export ONBOARD_PORT=8787
export WEB_ORIGINS=${WEB_ORIGINS:-http://localhost:3000}

# This child owns the three restartable services and accepts cooperative public
# URL updates while the agent keeps its terminal/Photon connection.
start_owned services "$ROOT" bash "$ROOT/scripts/demo-services.sh"
SERVICE_PID=$LAST_PID
for ((attempt=0; attempt<180; attempt++)); do
    [[ ! -s "$ROOT/data/demo/services.lock/ready" || $(cat "$ROOT/data/demo/services.lock/owner" 2>/dev/null) != "$SERVICE_PID" ]] || break
    kill -0 "$SERVICE_PID" 2>/dev/null || fail "Service supervisor exited; see $DEMO_LOG_DIR/services.log"
    sleep 1
done
[[ -s "$ROOT/data/demo/services.lock/ready" && $(cat "$ROOT/data/demo/services.lock/owner" 2>/dev/null) == "$SERVICE_PID" ]] || fail 'Services did not become ready.'
printf 'API, web and onboarding ready. Public URL updates: make demo-public in another terminal.\n'

# Explicit terminal mode always wins. Missing either credential selects terminal
# even if the copied .env example contains AGENT_TERMINAL=0.
if [[ -z "${PHOTON_PROJECT_ID:-}" || -z "${PHOTON_PROJECT_SECRET:-}" ]]; then export AGENT_TERMINAL=1; fi
if [[ "${AGENT_TERMINAL:-0}" =~ ^(1|true|yes)$ ]]; then
    printf 'Starting terminal chat with real API estimates. Ctrl-C exits; no iMessages are sent.\n'
else
    printf 'Starting Photon agent using configured credentials. Ctrl-C exits.\n'
fi
# script provides and records a real PTY for Spectrum tuichat, not a stdout pipe.
# This is the newest job; fg gives its process group terminal input when available.
if [[ $(uname) == Darwin ]]; then
    (cd "$ROOT/agent" && exec script -q "$DEMO_LOG_DIR/agent.log" npm run agent) &
else
    (cd "$ROOT/agent" && exec script -q -e -c 'npm run agent' "$DEMO_LOG_DIR/agent.log") &
fi
track_owned "$!" agent
if [[ -t 0 ]]; then fg %+; else wait "$LAST_PID"; fi
