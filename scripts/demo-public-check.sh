#!/usr/bin/env bash
# Which tunnel provider can work on this network? TCP reachability only: opens no tunnel, exposes nothing.
source "$(dirname "$0")/demo-common.sh"
[[ -x "$API_PY" ]] || fail 'Run (cd api && uv sync) first.'
# $1 host, $2 port, $3 expected banner prefix (empty: connect only). Prints OK or the reason.
probe() {
    "$API_PY" - "$@" <<'PY'
import socket, sys, time
host, port, banner = sys.argv[1], int(sys.argv[2]), sys.argv[3].encode()
t = time.monotonic()
try:  # first IPv4 address only: every edge address shares the network's fate, and each costs a 5 s timeout
    with socket.create_connection(socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)[0][4], 5) as s:
        if banner and not s.recv(64).startswith(banner):
            sys.exit(print(f"BLOCKED: connected but no {banner.decode()} banner (intercepted?)") or 1)
except OSError as e:
    sys.exit(print(f"BLOCKED: {e or type(e).__name__} after {time.monotonic() - t:.1f}s") or 1)
print(f"OK ({time.monotonic() - t:.2f}s)")
PY
}
cf=0 lr=0
printf 'cloudflared   region1.v2.argotunnel.com:7844/tcp  '; probe region1.v2.argotunnel.com 7844 '' && cf=1
printf 'localhostrun  localhost.run:22/tcp (SSH banner)    '; probe localhost.run 22 SSH- && lr=1
command -v cloudflared >/dev/null 2>&1 || { [[ "$cf" == 0 ]] || printf 'cloudflared is not installed: brew install cloudflared\n'; cf=0; }
command -v ssh >/dev/null 2>&1 || lr=0
if [[ "$cf" == 1 ]]; then printf 'Use: make demo-public   (cloudflared, the default)\n'
elif [[ "$lr" == 1 ]]; then printf 'Use: TUNNEL=localhostrun make demo-public\n'
else printf 'Neither provider is reachable here: switch the laptop to a phone hotspot, then rerun make demo-public-check.\n'; exit 1
fi
