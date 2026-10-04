"""Tests for app.links.resolve_link, network mocked with httpx.MockTransport (live test: RUN_LIVE=1)."""

import os
import socket
from urllib.parse import urlencode

import httpx
import pytest

from app import links
from app.listing import parse_listing_url

REAL_CLIENT = httpx.Client
# Redirect targets shaped like real expansions (curl, Oct 3, 2026), moved to Ann Arbor addresses.
GOOGLE_PLACE = ("https://www.google.com/maps/place/520+N+Main+St,+Ann+Arbor,+MI+48104/@42.2866,-83.7495,17z/"
                "data=!3m1!4b1!4m6!3m5!1s0x883cae3b8a1d0b0d:0x2a9b1e5f3c6d7e8f!8m2!3d42.2866021!4d-83.7469224"
                "!16s%2Fg%2F11c1q2w3e4?entry=tts&skid=8ef0ca3a")
APPLE_PLACE = ("https://maps.apple.com/place?address=Arbor%20Club%20Apartments,%201100%20Rabbit%20Run%20Cir,"
               "%20Ann%20Arbor,%20MI%2048103,%20United%20States&coordinate=42.299200,-83.798900"
               "&name=Arbor%20Club%20Apartments&place-id=I7C250D2CDCB364A&map=h")


class NoBody(httpx.SyncByteStream):
    def __iter__(self):
        raise AssertionError("resolve_link must not download response bodies")


@pytest.fixture
def net(monkeypatch, tmp_path):
    """Fake web: net.routes maps URL -> (status, Location). Any other URL fails the test."""

    class Net:
        routes, requests, clients = {}, [], []

    def handler(request):
        Net.requests.append(request)
        status, location = Net.routes[str(request.url)]  # KeyError = a host we must never contact
        return httpx.Response(status, headers={"location": location} if location else {}, stream=NoBody())

    def client(**kw):
        Net.clients.append(kw)
        return REAL_CLIENT(transport=httpx.MockTransport(handler), **kw)

    monkeypatch.setattr(links, "CACHE_PATH", tmp_path / "short_link_cache.json")
    monkeypatch.setattr(httpx, "Client", client)
    return Net


def test_google_short_link(net):
    net.routes = {"https://maps.app.goo.gl/AbCdEf123?g_st=ic": (302, GOOGLE_PLACE)}
    r = links.resolve_link("https://maps.app.goo.gl/AbCdEf123?g_st=ic")
    assert r == {"address": "520 N Main St, Ann Arbor, MI 48104", "unit": None, "zip": "48104",
                 "source": "google_maps", "needs_address": False, "hint": None,
                 "lat": 42.2866021, "lon": -83.7469224, "coords_only": False, "resolved_url": GOOGLE_PLACE}
    assert [q.method for q in net.requests] == ["GET"]  # GET, not HEAD: maps.apple/p 404s on HEAD
    assert net.clients == [{"timeout": 3, "follow_redirects": False}]


def test_apple_short_link_in_imessage_text(net):
    net.routes = {"https://maps.apple/p/U8rE9v8n8iVZjr": (301, APPLE_PLACE)}
    r = links.resolve_link("this one? https://maps.apple/p/U8rE9v8n8iVZjr")
    assert (r["address"], r["lat"], r["lon"], r["resolved_url"]) == (
        "1100 Rabbit Run Cir, Ann Arbor, MI 48103", 42.2992, -83.7989, APPLE_PLACE)


def test_coords_only_after_expansion(net):
    target = "https://www.google.com/maps/place/Arbor+Club+Apartments/@42.30,-83.79,15z/data=!4m6!3m5!8m2!3d42.2992!4d-83.7989"
    net.routes = {"https://maps.app.goo.gl/Pin123": (302, target)}
    r = links.resolve_link("https://maps.app.goo.gl/Pin123")
    assert (r["needs_address"], r["coords_only"], r["lat"], r["lon"], r["hint"]) == (
        False, True, 42.2992, -83.7989, "Arbor Club Apartments")


def test_multi_hop_and_consent_wall(net):
    net.routes = {
        "https://goo.gl/maps/Old123": (301, "https://maps.app.goo.gl/New456"),
        "https://maps.app.goo.gl/New456": (302, "https://consent.google.com/ml?" + urlencode({"continue": GOOGLE_PLACE})),
    }
    r = links.resolve_link("https://goo.gl/maps/Old123")
    assert r["address"] == "520 N Main St, Ann Arbor, MI 48104"
    assert len(net.requests) == 2  # consent.google.com itself is never contacted


def test_open_redirect_target_is_never_fetched(net):
    net.routes = {"https://maps.app.goo.gl/?link=https://example.org": (302, "https://example.org/")}
    r = links.resolve_link("https://maps.app.goo.gl/?link=https://example.org")
    assert (r["source"], r["needs_address"], r["resolved_url"]) == ("unknown", True, "https://example.org/")
    assert [q.url.host for q in net.requests] == ["maps.app.goo.gl"]


def test_cached_on_disk(net):
    net.routes = {"https://maps.app.goo.gl/AbCdEf123": (302, GOOGLE_PLACE)}
    first = links.resolve_link("https://maps.app.goo.gl/AbCdEf123")
    net.routes = {}
    assert links.resolve_link("https://maps.app.goo.gl/AbCdEf123") == first
    assert len(net.requests) == 1 and links.CACHE_PATH.exists()


def test_dead_link_and_network_error_fall_back_and_are_not_cached(net, monkeypatch):
    net.routes = {"https://maps.app.goo.gl/Gone": (404, None)}
    r = links.resolve_link("https://maps.app.goo.gl/Gone")
    assert r == {**parse_listing_url("https://maps.app.goo.gl/Gone"), "resolved_url": None}

    def timeout(request):
        raise httpx.ConnectTimeout("timed out", request=request)

    monkeypatch.setattr(httpx, "Client", lambda **kw: REAL_CLIENT(transport=httpx.MockTransport(timeout), **kw))
    r = links.resolve_link("https://maps.apple/p/Slow")
    assert (r["source"], r["needs_address"], r["resolved_url"]) == ("apple_maps", True, None)
    assert not links.CACHE_PATH.exists()


@pytest.mark.parametrize("text", [
    "https://www.zillow.com/homedetails/549-Longshore-Dr-APT-A-Ann-Arbor-MI-48105/51177689_zpid/",
    GOOGLE_PLACE, APPLE_PLACE, "https://redf.in/aBc123", "https://bit.ly/3xYzAbC", "https://goo.gl/AbCd",
    "123 Main St, Ann Arbor, MI", None,
])
def test_other_hosts_never_touch_network(net, monkeypatch, text):
    def boom(*a, **k):
        raise AssertionError("only allowlisted short links may use the network")

    monkeypatch.setattr(socket, "getaddrinfo", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    r = links.resolve_link(text)
    assert {k: v for k, v in r.items() if k != "resolved_url"} == parse_listing_url(text)
    assert net.requests == []


@pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="live network test; set RUN_LIVE=1")
def test_live(monkeypatch, tmp_path):
    monkeypatch.setattr(links, "CACHE_PATH", tmp_path / "short_link_cache.json")
    apple = links.resolve_link("https://maps.apple/p/U8rE9v8n8iVZjr")  # Apple Park, from Apple's dev forums
    assert apple["address"] == "1 Apple Park Way, Cupertino, CA 95014" and apple["lat"] == pytest.approx(37.33, abs=0.01)
    google = links.resolve_link("https://maps.app.goo.gl/RvL7iSNSsNaVBRru8")  # a public short link on GitHub
    assert google["coords_only"] and google["lat"] == pytest.approx(33.56, abs=0.01)
