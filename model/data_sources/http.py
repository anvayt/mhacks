"""HTTP helpers. Every external call goes through here: it hits the disk cache first, and every real network
request is appended to data/cache/requests.log, so `wc -l` there shows exactly how many calls we made."""
import datetime as dt
import hashlib
import json
import time
from pathlib import Path

import requests

from model.paths import CACHE

UA = {"User-Agent": "HiddenRent-MHacks2026/0.1 (research; contact dennisfj@umich.edu)"}
LOG = CACHE / "requests.log"


def log_request(url: str, params: dict | None = None, status: int | str = "") -> None:
    with open(LOG, "a") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{status}\t{url}\t{json.dumps(params or {})}\n")


def download(url: str, dest: Path, timeout: int = 600, refresh: bool = False) -> Path:
    """Stream a URL to dest unless it already exists (refresh=True forces a re-download)."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0 and not refresh:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=timeout, headers=UA) as r:
        log_request(url, None, r.status_code)
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(dest)
    return dest


def get_json(url: str, params: dict | None = None, ttl_s: float | None = None,
             namespace: str = "http", retries: int = 3, cache: bool = True) -> dict:
    """GET JSON with a disk cache keyed by url+params. ttl_s=None caches forever.
    cache=False: the caller persists the result itself (e.g. an incremental parquet), so don't store a copy."""
    key = hashlib.sha1(json.dumps([url, params], sort_keys=True).encode()).hexdigest()
    path = CACHE / namespace / f"{key}.json"
    if cache and path.exists() and (ttl_s is None or time.time() - path.stat().st_mtime < ttl_s):
        return json.loads(path.read_text())
    last: Exception | None = None
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=120, headers=UA)
            log_request(url, params, r.status_code)
            if r.status_code == 429:  # rate limited (Open-Meteo counts long ranges as many calls): wait it out
                last = requests.HTTPError("429 Too Many Requests")
                time.sleep(65)
                continue
            r.raise_for_status()
            data = r.json()
            if cache:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data))
            return data
        except Exception as e:  # network hiccup: back off and retry
            last = e
            time.sleep(1.5 * (i + 1))
    if cache and path.exists():  # stale cache beats no answer during a demo
        return json.loads(path.read_text())
    raise last or RuntimeError(f"request failed: {url}")
