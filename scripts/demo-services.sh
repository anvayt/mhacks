#!/usr/bin/env bash
# Private supervisor for make demo and make demo-public. The command mailbox is
# cooperative: only this process ever stops its own in-memory process groups.
source "$(dirname "$0")/demo-common.sh"
need curl; need npm
[[ -x "$API_PY" ]] || fail 'Run (cd api && uv sync) first.'
[[ -d "$ROOT/web/node_modules" && -d "$ROOT/agent/node_modules" ]] || fail 'Run npm ci in web and agent first.'
mkdir -p "$ROOT/data/demo"
CONTROL="$ROOT/data/demo/services.lock"
mkdir "$CONTROL" 2>/dev/null || fail "Another service supervisor owns $CONTROL; stop its make demo terminal first. If it crashed, remove that directory only after checking :8000/:3000/:8787."
printf '%s\n' "$$" > "$CONTROL/owner"
process_tracking
cleanup_extra() { rm -rf "$CONTROL"; }
export API_BASE_URL=http://localhost:8000 ONBOARD_PORT=8787
export NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL:-$API_BASE_URL}
export NEXT_PUBLIC_ONBOARD_URL=${NEXT_PUBLIC_ONBOARD_URL:-http://localhost:8787}
export PUBLIC_URL=${PUBLIC_URL:-http://localhost:8787}
export WEB_ORIGINS=${WEB_ORIGINS:-http://localhost:3000}
export WEB_ORIGIN=${WEB_ORIGIN:-http://localhost:3000}
BASE_WEB_ORIGINS=$WEB_ORIGINS
API_PID= WEB_PID= ONBOARD_PID=
start_services() {
    if [[ -z "$API_PID" ]] && healthy "$API_BASE_URL/health"; then printf 'Reusing healthy API on :8000 (cannot reconfigure).\n'
    else
        port_used 8000 && fail 'Port 8000 is occupied; leaving it untouched.'
        start_owned api "$ROOT/api" "$API_PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-proxy-headers
        API_PID=$LAST_PID
        wait_healthy api "$API_BASE_URL/health" "$API_PID"
    fi
    if [[ -z "$WEB_PID" ]] && healthy 'http://localhost:3000'; then printf 'Reusing healthy web on :3000 (cannot reconfigure).\n'
    else
        port_used 3000 && fail 'Port 3000 is occupied; leaving it untouched.'
        start_owned web "$ROOT/web" npm run dev -- --hostname 127.0.0.1 --port 3000
        WEB_PID=$LAST_PID
        wait_healthy web 'http://localhost:3000' "$WEB_PID" 120
    fi
    if [[ -z "$ONBOARD_PID" ]] && healthy 'http://localhost:8787'; then printf 'Reusing healthy onboarding on :8787 (cannot reconfigure).\n'
    else
        port_used 8787 && fail 'Port 8787 is occupied; leaving it untouched.'
        start_owned onboard "$ROOT/agent" npm run onboard
        ONBOARD_PID=$LAST_PID
        wait_healthy onboard 'http://localhost:8787' "$ONBOARD_PID"
    fi
}
start_services
# No secrets in the mailbox. A public restart requires all three services to be
# owned; reused services are never signalled, even when their port looks healthy.
if [[ -n "$API_PID" && -n "$WEB_PID" && -n "$ONBOARD_PID" ]]; then echo owned > "$CONTROL/ready"
else echo reused > "$CONTROL/ready"; fi
while true; do
    if [[ -f "$CONTROL/request" ]]; then
        IFS= read -r command < "$CONTROL/request" || true
        rm -f "$CONTROL/request"
        if [[ $(cat "$CONTROL/ready") != owned ]]; then echo 'error: unowned services cannot be reconfigured' > "$CONTROL/result"; continue; fi
        if [[ "$command" != public && "$command" != local ]]; then echo 'error: bad command' > "$CONTROL/result"; continue; fi
        if [[ "$command" == public ]]; then
            if [[ -z "${AGENT_API_KEY:-}" || "${USE_MOCKS:-0}" =~ ^(1|true|yes)$ ]]; then
                echo 'error: public mode requires AGENT_API_KEY and USE_MOCKS=0 in the service launcher' > "$CONTROL/result"; continue
            fi
            unset NEXT_PUBLIC_API_BASE_URL NEXT_PUBLIC_ONBOARD_URL PUBLIC_URL WEB_ORIGINS WEB_ORIGIN PUBLIC_TUNNEL
            load_env "$ROOT/data/demo/public.env"
            [[ "${PUBLIC_TUNNEL:-}" == 1 ]] || { echo 'error: missing public environment' > "$CONTROL/result"; continue; }
        else
            export NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 NEXT_PUBLIC_ONBOARD_URL=http://localhost:8787
            export PUBLIC_URL=http://localhost:8787 WEB_ORIGINS=$BASE_WEB_ORIGINS WEB_ORIGIN=http://localhost:3000 PUBLIC_TUNNEL=0
        fi
        export NEXT_PUBLIC_API_BASE_URL NEXT_PUBLIC_ONBOARD_URL PUBLIC_URL WEB_ORIGINS WEB_ORIGIN PUBLIC_TUNNEL
        stop_owned "$ONBOARD_PID"; stop_owned "$WEB_PID"; stop_owned "$API_PID"
        # Nonempty IDs mean start_services must start fresh, not reuse a port.
        start_services
        echo "$command" > "$CONTROL/result"
    fi
    sleep 1
done
