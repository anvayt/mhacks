#!/usr/bin/env bash
# Process/credential-loader regression checks; no model requests or messages.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d)
sentinel=
stub_server=
trap '[[ -z "$sentinel" ]] || { kill "$sentinel" 2>/dev/null; wait "$sentinel" 2>/dev/null; } || true; [[ -z "$stub_server" ]] || { kill "$stub_server" 2>/dev/null; wait "$stub_server" 2>/dev/null; } || true; rm -rf "$TMP"' EXIT
export DEMO_LOG_DIR="$TMP/logs"

# macOS Bash3.2: cleanup must retain the original failure with zero owned groups.
status=0
/bin/bash -c 'source "$1/scripts/demo-common.sh"; process_tracking; fail "intentional early failure"' _ "$ROOT" > "$TMP/early.log" 2>&1 || status=$?
[[ "$status" == 1 ]]
! grep -q 'unbound variable' "$TMP/early.log"
printf 'PASS early failure: exit1, zero owned processes, Bash nounset-safe.\n'

printf 'DEMO_LITERAL=$(touch %s)\nDEMO_KEEP=file\nDEMO_QUOTED="value with # hash"\n' "$TMP/unsafe" > "$TMP/env"
DEMO_KEEP=shell /bin/bash -c 'source "$1/scripts/demo-common.sh"; load_env "$2"; [[ "$DEMO_KEEP" == shell && "$DEMO_QUOTED" == "value with # hash" && "$DEMO_LITERAL" == *touch* ]]' _ "$ROOT" "$TMP/env"
[[ ! -e "$TMP/unsafe" ]]
printf 'PASS dotenv: inherited values win; shell expressions stay literal.\n'

sleep 60 & sentinel=$!
/bin/bash -c '
    source "$1/scripts/demo-common.sh"
    process_tracking
    start_owned nested "$1" /bin/bash -c '\''sleep 60 & echo "$!"; sleep 60 & echo "$!"; wait'\''
    sleep 1
    exit 0
' _ "$ROOT" > "$TMP/cleanup.log" 2>&1
kill -0 "$sentinel"
while IFS= read -r pid; do
    [[ "$pid" =~ ^[0-9]+$ ]] || continue
    ! kill -0 "$pid" 2>/dev/null
done < "$TMP/logs/nested.log"
printf 'PASS cleanup: nested child group stopped; unrelated sentinel survived.\n'

# Restart one known group while retaining another; also exercise removal of the
# final group under macOS Bash 3.2 nounset before the EXIT trap runs.
/bin/bash -c '
    source "$1/scripts/demo-common.sh"
    process_tracking
    start_owned first "$1" sleep 60; first=$LAST_PID
    start_owned second "$1" sleep 60; second=$LAST_PID
    stop_owned "$first"
    ! kill -0 "$first" 2>/dev/null
    kill -0 "$second"
    stop_owned "$second"
    ! kill -0 "$second" 2>/dev/null
' _ "$ROOT" > "$TMP/restart.log" 2>&1
kill -0 "$sentinel"
printf 'PASS selective restart: only owned target stopped, peer and unrelated sentinel survived.\n'

# A local HTTP stub exercises the future session/forecast contract. It is only a
# test; demo-warm/check themselves always call real servers and never replay JSON.
"$ROOT/api/.venv/bin/python" - "$TMP" <<'PYTEST' &
import json,sys
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
root=Path(sys.argv[1]); count=0
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def reply(self,body):
        raw=json.dumps(body).encode(); self.send_response(200)
        self.send_header('Content-Type','application/json'); self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path == '/health': return self.reply({'status':'ok'})
        if self.path.startswith('/map/'):
            with (root/'map-calls').open('a') as f:f.write(self.path+'\n')
            return self.reply({'building':{'id':1},'block_group':{},'steps':[]})
        if self.path == '/city': return self.reply({'type':'FeatureCollection','features':[{'type':'Feature'}]})
        with (root/'forecast-calls').open('a') as f:f.write(self.path+'\n')
        self.reply({'days':[{'date':'2026-10-04'}],'week':{'total_usd':3}})
    def do_POST(self):
        global count
        self.rfile.read(int(self.headers['Content-Length'])); count+=1
        row={'session_id':f'test-{count}','bill':{'annual':{'p50':1000}},
             'building':{'lat':42.8+count/10,'lon':-83.7,'type':'home','sqft':1000,'footprint_geojson':{'type':'Polygon'}},
             'heating_cooling':{'location':{'lat':42.21,'lon':-83.71}}}
        if count == 3:row['model_params']={'lat':42.41,'lon':-83.71}
        self.reply(row)
server=HTTPServer(('127.0.0.1',0),Handler)
(root/'port').write_text(str(server.server_port));server.serve_forever()
PYTEST
stub_server=$!
for attempt in 1 2 3 4 5; do [[ ! -s "$TMP/port" ]] || break; sleep 1; done
[[ -s "$TMP/port" ]]
printf 'first\nsecond\nthird\n' > "$TMP/addresses"
API_BASE_URL="http://127.0.0.1:$(cat "$TMP/port")" DEMO_ADDRESSES="$TMP/addresses" DEMO_LOG_DIR="$TMP/warm" bash "$ROOT/scripts/demo-warm.sh" > "$TMP/warm.log"
"$ROOT/api/.venv/bin/python" - "$TMP/forecast-calls" <<'PYTEST'
from pathlib import Path
import sys
assert Path(sys.argv[1]).read_text().splitlines() == ['/forecast/test-1','/forecast/test-3']
assert Path(sys.argv[1]).with_name('map-calls').read_text().splitlines() == ['/map/test-1','/map/test-2','/map/test-3']
PYTEST
printf 'PASS warm: map for every session, city once, one forecast per model cell; model_params wins over model location, which wins over building geocode.\n'
