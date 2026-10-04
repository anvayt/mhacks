"""Map share short links -> parse_listing_url on the URL they expand to.

The only network code on the listing path, and only for allowlisted short-link hosts
(maps.app.goo.gl, goo.gl/maps, maps.apple). Each hop is one GET whose body is never read (Apple's
short links 404 on HEAD; checked Oct 3, 2026), 3 s timeout, redirects followed by hand: we stop at
the first Location outside the allowlist and parse it as text, so that host is never contacted
(an open redirect like maps.app.goo.gl/?link=https://example.org can't make us fetch anything).
Expansions are cached in the repo-root /data/ dir (git-ignored); failures are not cached.
"""

import json
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

import httpx

from app.listing import find_url, parse_listing_url

CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "short_link_cache.json"
MAX_HOPS = 5


def is_short_link(url: str) -> bool:
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    return host in ("maps.app.goo.gl", "maps.apple") or (host == "goo.gl" and p.path.startswith("/maps/"))


def resolve_link(text: str) -> dict:
    """parse_listing_url(text) plus "resolved_url", expanding a map short link first.

    resolved_url is the URL that was parsed: the expanded one for a short link, else the URL found in
    the text. It is None when there is no URL or the short link couldn't be expanded (network error,
    dead link); the result is then parse_listing_url's needs_address answer for the short link.
    """
    url = find_url(text)
    if not url or not is_short_link(url):
        return {**parse_listing_url(text), "resolved_url": url}
    try:
        cache = json.loads(CACHE_PATH.read_text())
    except (OSError, ValueError):
        cache = {}
    if url not in cache:
        try:
            expanded = _expand(url)
        except httpx.HTTPError:
            expanded = None
        if expanded is None:
            return {**parse_listing_url(url), "resolved_url": None}
        cache[url] = expanded
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE_PATH.with_suffix(f".{id(cache)}.tmp")  # atomic replace: never half a file
        tmp.write_text(json.dumps(cache, indent=1))
        tmp.replace(CACHE_PATH)
    return {**parse_listing_url(cache[url]), "resolved_url": cache[url]}


def _expand(url: str) -> str | None:
    """Follow redirects while they stay on short-link hosts; the first URL off them, or None."""
    with httpx.Client(timeout=3, follow_redirects=False) as client:
        for _ in range(MAX_HOPS):
            with client.stream("GET", url) as r:  # headers only: leaving the block closes the body unread
                if not r.is_redirect:
                    return None
                url = urljoin(url, r.headers["location"])
            p = urlsplit(url)
            if p.hostname == "consent.google.com":  # EU consent wall wraps the maps URL in ?continue=
                url = parse_qs(p.query).get("continue", [url])[0]
            if not is_short_link(url):
                return url
    return None
