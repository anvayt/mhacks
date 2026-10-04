#!/usr/bin/env bash
# Share downloaded inputs and the trained models (model/artifacts/*.pkl from one build) so teammates skip the downloads and the training.
# The bundle always lives at model-data.zip in the repo root.
#   model-data.sh pack     zip this checkout's raw downloads, caches, city GIS and trained models
#   model-data.sh unpack   extract it (make install does this when the file is present); never overwrites
#                          existing data, and installs the bundled models only if none are trained here yet
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ZIP=$ROOT/model-data.zip
PATHS=(model/data/raw model/data/cache data/a2_footprints.geojson data/a2_mailing_addresses.geojson)
# One training run: the server reads these together, so they always travel (and install) as a set.
MODEL_PATHS=(model/artifacts model/data/processed model/results)
MODEL_PKL=model/artifacts/resstock_hc.pkl
MODEL_TABLE=model/data/processed/buildings_hc.parquet  # gone after pulling the commit that untracked processed/

case "${1:-}" in
pack)
    for p in "${PATHS[@]}" "$MODEL_PKL" "$MODEL_TABLE"; do
        [[ -e "$ROOT/$p" ]] || { echo "Missing $p; run make install first" >&2; exit 1; }
    done
    rm -f "$ZIP"
    (cd "$ROOT" && zip -qr "$ZIP" "${PATHS[@]}" "${MODEL_PATHS[@]}" -x '*/_tmp/*' '*.DS_Store')
    printf 'Wrote %s (%s). Share it; teammates put it in their repo root and run make install.\n' "$ZIP" "$(du -h "$ZIP" | cut -f1)"
    ;;
unpack)
    src=$ZIP
    [[ -f $src ]] || { echo "No $src" >&2; exit 1; }
    echo "==> data: extracting $src"
    unzip -q -n "$src" -d "$ROOT" -x 'model/artifacts/*' 'model/data/processed/*' 'model/results/*'
    if [[ -f "$ROOT/$MODEL_PKL" && -f "$ROOT/$MODEL_TABLE" ]]; then
        echo "==> data: keeping the models already trained here"
    elif unzip -l "$src" "$MODEL_PKL" >/dev/null 2>&1; then
        echo "==> data: installing the bundled trained models"
        unzip -q -o "$src" -d "$ROOT" 'model/artifacts/*' 'model/data/processed/*' 'model/results/*'
    fi
    ;;
*)
    sed -n '2,6p' "$0" >&2; exit 1 ;;
esac
