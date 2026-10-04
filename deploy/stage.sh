#!/usr/bin/env bash
# Stage a Docker build context and deploy one Fly app:  bash deploy/stage.sh api|agents [fly deploy args]
# api: this checkout + trained model files from $MODEL_SRC (default: this checkout) + $DATA_SRC caches.
# Never includes .git, .env files, node_modules or venvs. Trained files are not in git.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
APP=${1:?api|agents}; shift || true
MODEL_SRC=${MODEL_SRC:-$ROOT}
DATA_SRC=${DATA_SRC:-$ROOT/data}
STAGE=${STAGE:-${TMPDIR:-/tmp}/hidden-rent-stage-$APP}
rm -rf "$STAGE"; mkdir -p "$STAGE"
rsync -a --exclude .git --exclude '.env*' --exclude node_modules --exclude .venv --exclude __pycache__ \
  --exclude .next --exclude '/data' --exclude '/model/data' --exclude '/model/artifacts' --exclude '/model/results' \
  --exclude .runtime --exclude web --exclude research --exclude '*.zip' "$ROOT/" "$STAGE/"
if [[ "$APP" == api ]]; then
  for d in model/artifacts model/data model/results; do
    [[ -d "$MODEL_SRC/$d" ]] || { echo "missing $MODEL_SRC/$d (trained model files)"; exit 1; }
    rsync -a --exclude __pycache__ "$MODEL_SRC/$d/" "$STAGE/$d/"
  done
  rsync -a --exclude '*.sqlite*' --exclude demo "$DATA_SRC/" "$STAGE/data/"
else
  rm -rf "$STAGE/api" "$STAGE/model"
fi
cp "$ROOT/deploy/$APP.Dockerfile" "$STAGE/Dockerfile"
cp "$ROOT/deploy/$APP.fly.toml" "$STAGE/fly.toml"
printf '%s\n' .git '**/.env*' '**/node_modules' '**/.venv' '**/__pycache__' > "$STAGE/.dockerignore"
[[ -e "$STAGE/.env" ]] && { echo ".env leaked into stage"; exit 1; }
du -sh "$STAGE"
cd "$STAGE" && fly deploy --remote-only "$@"
