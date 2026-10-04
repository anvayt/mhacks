#!/usr/bin/env bash
source "$(dirname "$0")/demo-common.sh"
command -v cloudflared >/dev/null 2>&1 || fail 'Install cloudflared first: brew install cloudflared'
need curl; need npm
[[ -x "$API_PY" ]] || fail 'Run (cd api && uv sync) first.'
[[ -n "${AGENT_API_KEY:-}" ]] || fail 'Set a private AGENT_API_KEY in .env before exposing the account API.'
[[ ! "${USE_MOCKS:-0}" =~ ^(1|true|yes)$ ]] || fail 'Public auth cannot use USE_MOCKS=1. Set USE_MOCKS=0.'
mkdir -p "$ROOT/data/demo"
CONTROL="$ROOT/data/demo/services.lock"
PUBLIC_LOCK="$ROOT/data/demo/public.lock"
mkdir "$PUBLIC_LOCK" 2>/dev/null || fail 'A public launcher already holds data/demo/public.lock. Stop that launcher before starting another.'
process_tracking
RECONFIGURED=0 OWN_SUPERVISOR=0
request_mode() {
    local mode=$1 attempt
    [[ -d "$CONTROL" ]] || return 1
    rm -f "$CONTROL/result"
    printf '%s\n' "$mode" > "$CONTROL/request.tmp"
    mv "$CONTROL/request.tmp" "$CONTROL/request"
    for ((attempt=0; attempt<180; attempt++)); do
        if [[ -s "$CONTROL/result" ]]; then
            [[ $(cat "$CONTROL/result") == "$mode" ]] && return 0
            cat "$CONTROL/result" >&2; return 1
        fi
        [[ -d "$CONTROL" ]] || return 1
        sleep 1
    done
    printf 'Supervisor did not acknowledge %s; no unowned process was signalled.\n' "$mode" >&2
    return 1
}
cleanup_before() {
    if [[ "$RECONFIGURED" == 1 && "$OWN_SUPERVISOR" == 0 ]]; then
        printf 'Restoring launcher-owned services to local URLs...\n'
        request_mode local || printf 'Local URL restore failed; inspect the make demo terminal before continuing.\n' >&2
    fi
}
cleanup_extra() { rm -rf "$PUBLIC_LOCK"; rm -f "$ROOT/data/demo/public.env"; }
if [[ ! -d "$CONTROL" ]]; then
    for port in 8000 3000 8787; do
        port_used "$port" && fail "Port $port is already owned elsewhere. Run make demo from this checkout, or stop its owner yourself; no process was changed."
    done
    start_owned services "$ROOT" bash "$ROOT/scripts/demo-services.sh"
    OWN_SUPERVISOR=1
    for ((attempt=0; attempt<180; attempt++)); do
        [[ ! -s "$CONTROL/ready" ]] || break
        kill -0 "$LAST_PID" 2>/dev/null || fail "Services exited; see $DEMO_LOG_DIR/services.log"
        sleep 1
    done
fi
[[ -s "$CONTROL/ready" && $(cat "$CONTROL/ready") == owned ]] || fail 'The make demo supervisor must own all three services. Reused services cannot be restarted for public URLs.'

start_tunnel() {
    local name=$1 port=$2 attempt url
    start_owned "$name-tunnel" "$ROOT" cloudflared tunnel --no-autoupdate --protocol http2 --url "http://127.0.0.1:$port"
    for ((attempt=0; attempt<90; attempt++)); do
        url=$(sed -nE 's|.*(https://[a-z0-9-]+\.trycloudflare\.com).*|\1|p' "$DEMO_LOG_DIR/$name-tunnel.log" | head -1)
        if [[ -n "$url" ]]; then TUNNEL_URL=$url; return; fi
        kill -0 "$LAST_PID" 2>/dev/null || fail "$name tunnel exited; see $DEMO_LOG_DIR/$name-tunnel.log"
        sleep 1
    done
    fail "$name tunnel did not provide a URL; see $DEMO_LOG_DIR/$name-tunnel.log"
}
start_tunnel web 3000; WEB_URL=$TUNNEL_URL
start_tunnel api 8000; API_URL=$TUNNEL_URL
start_tunnel onboard 8787; ONBOARD_URL=$TUNNEL_URL
umask 077
cat > "$ROOT/data/demo/public.env.tmp" <<EOF
NEXT_PUBLIC_API_BASE_URL=$API_URL
NEXT_PUBLIC_ONBOARD_URL=$ONBOARD_URL
PUBLIC_URL=$ONBOARD_URL
WEB_ORIGINS=${WEB_ORIGINS:-http://localhost:3000},$WEB_URL
WEB_ORIGIN=$WEB_URL
PUBLIC_TUNNEL=1
EOF
mv "$ROOT/data/demo/public.env.tmp" "$ROOT/data/demo/public.env"
RECONFIGURED=1  # A failed restart may still have applied env; restore on exit.
request_mode public || fail 'Could not apply public URLs to the owned services.'
for url in "$WEB_URL" "$API_URL/health" "$ONBOARD_URL"; do
    ok=0
    for ((attempt=0; attempt<30; attempt++)); do
        if healthy "$url"; then ok=1; break; fi
        sleep 2
    done
    [[ "$ok" == 1 ]] || fail "Tunnel is not reachable: $url"
    printf 'PASS public HTTP: %s\n' "$url"
done
printf '\nJudge URL: %s\nAPI: %s\nOnboarding: %s\n' "$WEB_URL" "$API_URL" "$ONBOARD_URL"
(cd "$ROOT/agent" && node -e 'require("qrcode").toString(process.argv[1],{type:"terminal",small:true},(error,qr)=>{if(error)throw error;process.stdout.write(qr)})' "$WEB_URL")
printf '\nReprint P4\047s table card now: %s/card\nURLs change on every run. Keep this terminal open; Ctrl-C closes only these tunnels and restores local services.\n' "$ONBOARD_URL"
printf 'Model health (API is live even if its model is down): '
curl --noproxy '*' -fsS --max-time 5 "$API_URL/health"; printf '\n'
# This launcher does not start/restart the model or agent and never calls /join.
while true; do
    sleep 2
    for pid in "${OWNED_PIDS[@]}"; do kill -0 "$pid" 2>/dev/null || fail 'A public launcher process exited; closing its tunnels.'; done
    [[ -d "$CONTROL" ]] || fail 'The service supervisor stopped; closing the public tunnels.'
done
