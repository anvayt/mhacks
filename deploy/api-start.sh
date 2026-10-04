#!/usr/bin/env bash
# ponytail: supervisor = bash. If either process dies the container exits and Fly restarts it (restart policy always).
set -euo pipefail
trap 'kill 0' EXIT
cd /app
python -m uvicorn model.heating_cooling.server:app --host 127.0.0.1 --port 8001 &
(cd api && exec .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000) &
wait -n
exit 1
