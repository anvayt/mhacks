#!/usr/bin/env bash
# Install every dependency the demo needs (no data downloads, no model build).
#   model/  -> $ROOT/.venv     (pip, model/requirements.txt; same as `make -C model setup`)
#   api/    -> api/.venv       (uv sync if uv exists, else venv + pip pinned from api/uv.lock)
#   web/, agent/ -> node_modules (npm ci)
# Override the interpreter with PYTHON=/path/to/python3.12.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PYTHON=${PYTHON:-python3}

fail() { printf 'install: %s\n' "$*" >&2; exit 1; }
step() { printf '\n==> %s\n' "$*"; }

command -v "$PYTHON" >/dev/null || fail "$PYTHON not found; install Python 3.12."
"$PYTHON" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))' \
    || fail "api/ needs Python 3.12 ($PYTHON is $("$PYTHON" -V 2>&1)); set PYTHON=/path/to/python3.12."
command -v npm >/dev/null || fail 'npm not found; install Node 20+.'
node -e 'process.exit(Number(process.versions.node.split(".")[0] < 20))' || fail 'Node 20+ required.'

if [[ $(uname) == Darwin ]] && command -v brew >/dev/null && ! brew list libomp >/dev/null 2>&1; then
    step 'Installing libomp (needed by xgboost/lightgbm on macOS)'
    brew install libomp
fi

step 'model: creating .venv and installing model/requirements.txt'
[[ -x "$ROOT/.venv/bin/python" ]] || "$PYTHON" -m venv --system-site-packages "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install -q -r "$ROOT/model/requirements.txt"

step 'api: creating api/.venv'
if command -v uv >/dev/null; then
    (cd "$ROOT/api" && uv sync)
else
    # No uv: install the exact versions recorded in uv.lock with plain pip.
    [[ -x "$ROOT/api/.venv/bin/python" ]] || "$PYTHON" -m venv "$ROOT/api/.venv"
    pins=$("$PYTHON" - "$ROOT/api/uv.lock" <<'EOF'
import sys, tomllib
lock = tomllib.load(open(sys.argv[1], "rb"))
for p in lock["package"]:
    if "registry" in p.get("source", {}):
        print(f'{p["name"]}=={p["version"]}')
EOF
)
    "$ROOT/api/.venv/bin/pip" install -q --upgrade pip
    # shellcheck disable=SC2086
    "$ROOT/api/.venv/bin/pip" install -q $pins
fi

for dir in web agent; do
    step "$dir: npm ci"
    (cd "$ROOT/$dir" && npm ci)
done

[[ -f "$ROOT/agent/.env" ]] || { cp "$ROOT/agent/.env.example" "$ROOT/agent/.env" 2>/dev/null && echo 'Created agent/.env from example.'; } || true

cat <<EOF

Dependencies installed. One-time data setup (needs network), if not done yet:
  (cd api && .venv/bin/python scripts/fetch_footprints.py)   # city GIS, ~30 s
  make -C model build                                        # long; see README
Then: make demo
EOF
