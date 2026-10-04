"""Filesystem layout for /model. Raw downloads and caches are git-ignored."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW = DATA / "raw"              # untouched downloads (git-ignored)
CACHE = DATA / "cache"          # HTTP / API response cache (git-ignored)
PROCESSED = DATA / "processed"  # small derived tables (committed when small)
ARTIFACTS = ROOT / "artifacts"  # trained models
RESULTS = ROOT / "results"      # metrics and validation outputs

for _p in (RAW, CACHE, PROCESSED, ARTIFACTS, RESULTS):
    _p.mkdir(parents=True, exist_ok=True)
