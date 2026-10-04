"""Single-worker public-demo guard. Limits are operational budgets, not model thresholds.

RATE_LIMIT_PER_MIN defaults to 120 model requests/minute per visitor; 3 photos/10
minutes limits the two paid vision calls per photo. Trust Cloudflare's client header only
on the launcher-only loopback socket (uvicorn --no-proxy-headers); on Fly (FLY_APP_NAME set)
trust Fly-Client-IP, which Fly's proxy always sets.
"""
import hmac
import ipaddress
import json
import os
import time
from collections import deque
from urllib.parse import parse_qs

from starlette.responses import JSONResponse

MAX_BODY = 8 * 1024 * 1024 + 64 * 1024  # 8 MiB base64 photo plus JSON/typed bill metadata
MAX_PHOTO = 8 * 1024 * 1024


def protected(method, path, query_string=b""):
    path = path.rstrip("/")
    if method == "GET" and (path == "/leaderboard/position" or path.startswith("/leaderboard/position/")):
        # Plain positions are cached reads; catalog_ids asks for a modeled what-if.
        # Parse query names, including percent escapes and empty/repeated values.
        return "catalog_ids" in parse_qs(query_string.decode("utf-8", errors="replace"), keep_blank_values=True)
    return (method == "POST" and path in {
        "/estimate", "/answer", "/compare", "/calibrate", "/projection", "/properties", "/auth/web/start",
        "/simulate/fast-forward",  # runs the same what-if as /projection
    }) or (method == "GET" and any(path == p or path.startswith(p + "/") for p in (
        "/map", "/forecast", "/fixes", "/debug/features", "/narration",  # narration: paid xAI TTS on a cache miss
    )))


class PublicGuard:
    def __init__(self, app, limit=None, window=60, photo_limit=3, photo_window=600, clock=time.monotonic):
        self.app = app
        if limit is None:
            limit = int(os.environ.get("RATE_LIMIT_PER_MIN", "120"))
        if limit < 1:
            raise ValueError("RATE_LIMIT_PER_MIN must be a positive integer")
        self.limit, self.window = limit, window
        self.photo_limit, self.photo_window = photo_limit, photo_window
        self.clock = clock
        self.visitors = {}  # bounded; a busy table fails closed for new visitors

    def agent(self, headers):
        key = os.environ.get("AGENT_API_KEY", "")
        return bool(key) and hmac.compare_digest(headers.get(b"x-agent-key", b""), key.encode())

    def visitor(self, scope, headers):
        peer = (scope.get("client") or ("unknown",))[0]
        if os.environ.get("FLY_APP_NAME"):
            # Behind Fly's proxy the peer is the proxy. Fly sets Fly-Client-IP and
            # overwrites any client-supplied value, so it is the visitor.
            try:
                return str(ipaddress.ip_address(headers.get(b"fly-client-ip", b"").decode()))
            except (ValueError, UnicodeDecodeError):
                pass
        if os.environ.get("PUBLIC_TUNNEL") == "1":
            try:
                if ipaddress.ip_address(peer).is_loopback:
                    return str(ipaddress.ip_address(headers.get(b"cf-connecting-ip", b"").decode()))
            except (ValueError, UnicodeDecodeError):
                pass
        return peer

    def allow(self, visitor, photo):
        now = self.clock()
        # Drop whole inactive buckets; cap memory even under many distinct IPs.
        for ip, (_, _, seen) in list(self.visitors.items()):
            if now - seen >= max(self.window, self.photo_window):
                del self.visitors[ip]
        if visitor not in self.visitors:
            if len(self.visitors) >= 10000:
                return False
            self.visitors[visitor] = (deque(), deque(), now)
        regular, photos, _ = self.visitors[visitor]
        while regular and now - regular[0] >= self.window:
            regular.popleft()
        while photos and now - photos[0] >= self.photo_window:
            photos.popleft()
        self.visitors[visitor] = (regular, photos, now)
        if len(regular) >= self.limit or (photo and len(photos) >= self.photo_limit):
            return False
        regular.append(now)
        if photo:
            photos.append(now)
        return True

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope["headers"])
        # Cap every request, including agent requests. Count actual chunks, not a
        # caller's Content-Length; no uploaded photo reaches handlers above cap.
        async def reject(status, code, message):
            response = JSONResponse({"detail": {"code": code, "message": message}}, status_code=status,
                                    headers={"Retry-After": str(self.photo_window if photo else self.window)}
                                    if status == 429 else None)
            await response(scope, receive, send)

        photo = False
        try:
            length = int(headers.get(b"content-length", b"0"))
        except ValueError:
            length = 0
        if length > MAX_BODY:
            return await reject(413, "bill_too_large", "That upload is too large. Use a smaller photo or type the numbers from your bill.")
        chunks, size = [], 0
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            chunk = event.get("body", b"")
            size += len(chunk)
            if size > MAX_BODY:
                return await reject(413, "bill_too_large", "That upload is too large. Use a smaller photo or type the numbers from your bill.")
            chunks.append(chunk)
            if not event.get("more_body", False):
                break
        body = b"".join(chunks)
        if scope["method"] == "POST" and scope["path"].rstrip("/") == "/calibrate":
            try:
                value = json.loads(body)
                photo = isinstance(value, dict) and bool(value.get("bill_image_base64"))
                if photo and isinstance(value["bill_image_base64"], str) and len(value["bill_image_base64"]) > MAX_PHOTO:
                    return await reject(413, "bill_too_large", "That photo is too large. Use a smaller photo or type the numbers from your bill.")
            except RecursionError:
                return await reject(422, "bad_bill", "That bill request is too complex. Try a photo or type the numbers from your bill.")
            except (ValueError, UnicodeDecodeError):
                pass  # The endpoint supplies its normal malformed-JSON error.
        if protected(scope["method"], scope["path"], scope.get("query_string", b"")) and not self.agent(headers):
            if not self.allow(self.visitor(scope, headers), photo):
                return await reject(429, "slow_down", "Please give us a moment before trying again. You can keep reading your current report.")

        delivered = False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()
        await self.app(scope, replay, send)
