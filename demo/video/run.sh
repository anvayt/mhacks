#!/usr/bin/env bash
set -euo pipefail
VIDEO_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/record.cjs"
export VIDEO_SCRIPT
# npx's executable location also gives Node a reproducible module search path.
# No package.json/package-lock edits, global install, or new app dependencies.
npx --yes --package=playwright@1.63.0 -c 'NODE_PATH="$(dirname "$(dirname "$(command -v playwright)")")" node "$VIDEO_SCRIPT" '"$(printf '%q ' "$@")"
