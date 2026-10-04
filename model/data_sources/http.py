"""Tiny HTTP helpers with an on-disk cache so every external call happens once."""
import hashlib
import json
import time
from pathlib import Path

import requests

from model.paths import CACHE

UA = {"User-Agent": "HiddenRent-MHacks2026/0.1 (research; contact dennisfj@umich.edu)"}


def download(url: str, dest: Path, timeout: int = 600) -> Path:
    """Stream a URL to dest unless it already exists."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=timeout, headers=UA) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(dest)
    return dest


def get_json(url: str, params: dict | None = None, ttl_s: float | None = None,
             namespace: str = "http", retries: int = 3) -> dict:
    """GET JSON with a disk cache keyed by url+params. ttl_s=None caches forever."""
    key = hashlib.sha1(json.dumps([url, params], sort_keys=True).encode()).hexdigest()
    path = CACHE / namespace / f"{key}.json"
    if path.exists() and (ttl_s is None or time.time() - path.stat().st_mtime < ttl_s):
        return json.loads(path.read_text())
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=120, headers=UA)
            r.raise_for_status()
            data = r.json()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data))
            return data
        except Exception as e:  # network hiccup: back off and retry
            last = e
            time.sleep(1.5 * (i + 1))
    if path.exists():  # stale cache beats no answer during a demo
        return json.loads(path.read_text())
    raise last
