"""Optional P1 features, negotiated over HTTP so the old live model remains safe.

A missing, malformed or temporarily unavailable endpoint advertises nothing. Cache
both success and failure briefly; a model upgrade becomes visible without an API restart.
"""

from copy import deepcopy
from threading import Lock
from time import monotonic

import httpx

from app import estimate

TTL_SECONDS = 30
TIMEOUT_SECONDS = 3
_lock = Lock()
_cache: dict[str, tuple[float, dict]] = {}


def reset_cache() -> None:
    """Clear discovery state (tests and explicit operator refresh)."""
    with _lock:
        _cache.clear()


def capabilities() -> dict:
    url = f"{estimate.MODEL_BASE_URL.rstrip('/')}/hc/capabilities"
    with _lock:
        cached = _cache.get(url)
        if cached and monotonic() < cached[0]:
            return deepcopy(cached[1])
        body = {}
        try:
            with estimate.MODEL_SLOTS:
                response = httpx.get(url, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                candidate = response.json()
                lists = ("estimate_params", "endpoints", "bill_check_params", "bill_noise_bases")
                if (isinstance(candidate, dict) and any(k in candidate for k in lists)
                        and all(isinstance(candidate.get(k, []), list)
                                and all(isinstance(v, str) for v in candidate.get(k, [])) for k in lists)
                        and isinstance(candidate.get("details", {}), dict)):
                    body = candidate
        except (httpx.HTTPError, ValueError):
            pass  # Optional discovery must not make a formerly working estimate fail.
        _cache[url] = (monotonic() + TTL_SECONDS, body)
        return deepcopy(body)
