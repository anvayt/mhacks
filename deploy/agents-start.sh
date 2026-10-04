#!/usr/bin/env bash
# ponytail: supervisor = bash. If any process dies the container exits and Fly restarts it (restart policy always).
set -euo pipefail
trap 'kill 0' EXIT
cd /app/agent && npm run onboard &
cd /app/agent && npm run agent &
cd /app/asi-agent && uv run --frozen --no-dev python agent.py &
wait -n
exit 1
