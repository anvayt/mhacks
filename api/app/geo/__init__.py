"""Address -> building features. All external responses are cached under the repo-root /data/ dir (git-ignored)."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
FOOTPRINTS_PATH = DATA_DIR / "a2_footprints.geojson"
ADDRESSES_PATH = DATA_DIR / "a2_mailing_addresses.geojson"
