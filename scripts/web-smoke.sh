#!/usr/bin/env bash
# Web integration smoke test (tasks/P3-INT-00-web-shared.md). Covers the 5 demo addresses in demo/addresses.txt:
# address -> survey -> skip sign-in -> grade -> board (rank, modeled commitment -> ghost marker) -> typed therms,
# /compare 624 Church St vs 1022 S Forest Ave, /share, /map, plus needs_address, not_a_home and API-down paths.
#
#   scripts/web-smoke.sh api   # API calls only (curl-level: what the web should call), no browser
#   scripts/web-smoke.sh web   # drive the pages in Chrome via Playwright (playwright npm pkg via npx, system Chrome)
#   scripts/web-smoke.sh       # both
#
# Env: API (default http://localhost:8033), WEB (default http://localhost:3004), HEADED=1, PW_CHANNEL (default chrome).
# Optional phone sign-in check (USE_MOCKS=1 API, fictional number): SMOKE_SIGNIN=1 with AGENT_API_KEY in the env.
# Uses the real public 30/min budget: starts after a clean minute, counts Node + browser requests,
# and logs PACE waits between browser flows. Run against an otherwise idle test API.
# Browser requests never receive X-Agent-Key; any 429 fails instead of being retried.
# Start the API:  cd api && MODEL_BASE_URL=http://localhost:8001 USE_MOCKS=1 WEB_ORIGINS=http://localhost:3004 \
#   SESSIONS_DB=/tmp/rev-s.sqlite APP_DB=/tmp/rev-a.sqlite uv run --env-file ../.env uvicorn app.main:app --port 8033
# Start the web:  cd web && NEXT_PUBLIC_API_BASE_URL=http://localhost:8033 npm run dev -- -p 3004
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
if [ "${1:-all}" = api ]; then exec node "$here/web-smoke.mjs" api; fi
# ponytail: playwright comes from the npx cache (no repo dependency); browsers = system Chrome.
exec npx -y -p playwright@1.61.1 sh -c 'PW="$(dirname "$(command -v playwright)")/../playwright/index.mjs" exec node "$0" "$1"' \
  "$here/web-smoke.mjs" "${1:-all}"
