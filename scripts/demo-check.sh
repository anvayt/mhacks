#!/usr/bin/env bash
source "$(dirname "$0")/demo-common.sh"
need curl
[[ -x "$API_PY" && -x "$MODEL_DIR/.venv/bin/python" ]] || fail 'Prepare api/.venv and point MODEL_DIR at an already-built model checkout.'
process_tracking
CHECK_MODEL_PORT=${DEMO_CHECK_MODEL_PORT:-18001}
CHECK_API_PORT=${DEMO_CHECK_API_PORT:-18000}
[[ "$CHECK_MODEL_PORT" =~ ^[0-9]+$ && "$CHECK_API_PORT" =~ ^[0-9]+$ ]] || fail 'Check ports must be integers.'
[[ "$CHECK_MODEL_PORT" != "$CHECK_API_PORT" && "$CHECK_MODEL_PORT" != 8001 && "$CHECK_API_PORT" != 8000 ]] || fail 'Use separate isolated check ports; production demo ports must stay untouched.'
port_used "$CHECK_MODEL_PORT" && fail "Check model port $CHECK_MODEL_PORT is occupied; leaving it untouched."
port_used "$CHECK_API_PORT" && fail "Check API port $CHECK_API_PORT is occupied; leaving it untouched."
printf 'Offline simulation: isolated API :%s and model :%s; existing :8000/:8001 stay untouched.\n' "$CHECK_API_PORT" "$CHECK_MODEL_PORT"
printf 'Changing this shell cannot block an already-running model. Both isolated Python processes get a socket-level outbound guard.\n'
BLOCK_DIR="$DEMO_LOG_DIR/network-guard"
mkdir -p "$BLOCK_DIR"
cat > "$BLOCK_DIR/sitecustomize.py" <<'PY'
"""Process-local offline simulation, not an OS firewall; loopback remains usable."""
import errno
import ipaddress
import json
import os
import socket
from pathlib import Path

def allowed(host):
    if host is None:
        return True
    if isinstance(host,bytes):
        host=host.decode()
    if str(host).lower() == 'localhost':
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False

def check(host):
    if not allowed(host):
        with open(os.environ['DEMO_OUTBOUND_LOG'],'a') as log:
            log.write(json.dumps({'process':os.environ.get('DEMO_PROCESS','probe'),'host':str(host)})+'\n')
        raise OSError(errno.ENETUNREACH,'demo-check blocked outbound network')

_getaddrinfo=socket.getaddrinfo
_connect=socket.socket.connect
_connect_ex=socket.socket.connect_ex

def getaddrinfo(host,*args,**kwargs):
    check(host)
    return _getaddrinfo(host,*args,**kwargs)

def connect(sock,address):
    if isinstance(address,tuple): check(address[0])
    return _connect(sock,address)

def connect_ex(sock,address):
    if isinstance(address,tuple): check(address[0])
    return _connect_ex(sock,address)

socket.getaddrinfo=getaddrinfo
socket.socket.connect=connect
socket.socket.connect_ex=connect_ex
PY
# Clear inherited proxies so attempted hosts are observable rather than hidden
# behind a proxy. The guard blocks both DNS and direct numeric outbound connects.
export HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy=
export NO_PROXY=localhost,127.0.0.1,::1 no_proxy=localhost,127.0.0.1,::1
export PYTHONPATH="$BLOCK_DIR${PYTHONPATH:+:$PYTHONPATH}"
export DEMO_OUTBOUND_LOG="$DEMO_LOG_DIR/outbound.jsonl"
: > "$DEMO_OUTBOUND_LOG"
"$API_PY" - <<'PY'
import httpx
try:
    httpx.get('https://example.invalid',timeout=2)
except httpx.ConnectError:
    print('PASS outbound guard: external httpx request blocked.')
else:
    raise SystemExit('FAIL: outbound guard did not block httpx')
PY
mv "$DEMO_OUTBOUND_LOG" "$DEMO_LOG_DIR/guard-selftest.jsonl"
: > "$DEMO_OUTBOUND_LOG"
start_owned check-model "$MODEL_DIR" env DEMO_PROCESS=model "$MODEL_DIR/.venv/bin/python" -m uvicorn model.heating_cooling.server:app --host 127.0.0.1 --port "$CHECK_MODEL_PORT"
wait_healthy check-model "http://127.0.0.1:$CHECK_MODEL_PORT/hc/answers" "$LAST_PID" 120
export MODEL_BASE_URL="http://127.0.0.1:$CHECK_MODEL_PORT"
start_owned check-api "$ROOT/api" env DEMO_PROCESS=api "$API_PY" -m uvicorn app.main:app --host 127.0.0.1 --port "$CHECK_API_PORT"
wait_healthy check-api "http://127.0.0.1:$CHECK_API_PORT/health" "$LAST_PID"
export API_BASE_URL="http://127.0.0.1:$CHECK_API_PORT"
export DEMO_WARM_MODE='Checking with outbound blocked'
# The HTTP helper also runs under the guard, using only localhost. These are fresh
# real estimates, not saved-response replay. Continue to summarize blocked hosts.
status=0
bash "$ROOT/scripts/demo-warm.sh" || status=$?
"$API_PY" - "$DEMO_OUTBOUND_LOG" <<'PY'
from collections import Counter
import json,sys
attempts=Counter((r['process'],r['host']) for line in open(sys.argv[1]) if (r:=json.loads(line)))
if attempts:
    print('External calls still attempted (blocked; cached fallbacks may have succeeded):')
    for (process,host),count in sorted(attempts.items()): print(f'  {process}: {host} ({count} attempts)')
else:
    print('No external calls attempted by these five estimates in either isolated Python process.')
print('Scope: Python API/model only; browser assets, npm/tuichat installation, Photon, tunnels, and unavailable endpoints are not certified offline.')
print('Forecast 404 is an explicit skip, not an offline forecast pass. A present forecast route may still need live Open-Meteo; see summary.tsv/outbound.jsonl.')
PY
exit "$status"
