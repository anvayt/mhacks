"""Tests for app.listing.parse_listing_url. URLs are real-shaped (public listing URL formats, Oct 2026)."""

import socket

import pytest

from app.listing import parse_listing_url

FOUND = [
    # Zillow homedetails: APT / UNIT / '#' units, plain houses
    ("https://www.zillow.com/homedetails/549-Longshore-Dr-APT-A-Ann-Arbor-MI-48105/51177689_zpid/",
     "549 Longshore Dr Apt A, Ann Arbor, MI 48105", "Apt A", "48105"),
    ("https://www.zillow.com/homedetails/123-Main-St-APT-4-Ann-Arbor-MI-48104/12345_zpid/",
     "123 Main St Apt 4, Ann Arbor, MI 48104", "Apt 4", "48104"),
    ("https://www.zillow.com/homedetails/223-E-Ann-St-UNIT-7-Ann-Arbor-MI-48104/54793340_zpid/",
     "223 E Ann St Unit 7, Ann Arbor, MI 48104", "Unit 7", "48104"),
    ("https://www.zillow.com/homedetails/123-Main-St-#4-Ann-Arbor-MI-48104/12345_zpid/",
     "123 Main St #4, Ann Arbor, MI 48104", "#4", "48104"),
    ("https://www.zillow.com/homedetails/123-Main-St-%234B-Ann-Arbor-MI-48104/12345_zpid/",
     "123 Main St #4B, Ann Arbor, MI 48104", "#4B", "48104"),
    # no scheme, no www, share query string
    ("zillow.com/homedetails/3518-Carolyn-St-Ann-Arbor-MI-48104/60548563_zpid/?utm_source=share&utm_medium=ios",
     "3518 Carolyn St, Ann Arbor, MI 48104", None, "48104"),
    # mobile domain, uppercase scheme/host, photo fragment, no trailing slash before it
    ("HTTPS://M.ZILLOW.COM/homedetails/2125-Nature-Cove-Ct-APT-108-Ann-Arbor-MI-48104/24717147_zpid/#photo-3",
     "2125 Nature Cove Ct Apt 108, Ann Arbor, MI 48104", "Apt 108", "48104"),
    # city not in KNOWN_CITIES: split after the street suffix
    ("https://www.zillow.com/homedetails/22266-Civic-Center-Dr-Southfield-MI-48033/111_zpid/",
     "22266 Civic Center Dr, Southfield, MI 48033", None, "48033"),
    # lowercase full-word suffix gets abbreviated
    ("https://www.zillow.com/homedetails/123-main-street-ann-arbor-mi-48104/1_zpid",
     "123 Main St, Ann Arbor, MI 48104", None, "48104"),
    # Zillow address search and building page with a street address
    ("https://www.zillow.com/homes/223-E-Ann-St-Ann-Arbor,-MI-48104_rb/",
     "223 E Ann St, Ann Arbor, MI 48104", None, "48104"),
    ("https://www.zillow.com/b/1819-willowtree-ln-ann-arbor-mi-5XqPf4/",
     "1819 Willowtree Ln, Ann Arbor, MI", None, None),
    # Redfin: unit segment, task example, house with trailing slash + query
    ("https://www.redfin.com/MI/Ann-Arbor/813-E-Kingsley-St-48104/unit-C1/home/99358421",
     "813 E Kingsley St Unit C1, Ann Arbor, MI 48104", "Unit C1", "48104"),
    ("https://www.redfin.com/MI/Ann-Arbor/123-Main-St-48104/unit-4/home/12345",
     "123 Main St Unit 4, Ann Arbor, MI 48104", "Unit 4", "48104"),
    ("https://m.redfin.com/MI/Ann-Arbor/3518-Carolyn-St-48104/home/60548563/?utm_source=android_share",
     "3518 Carolyn St, Ann Arbor, MI 48104", None, "48104"),
    # Apartments.com single-home listing whose slug is an address
    ("https://www.apartments.com/1819-willowtree-ln-ann-arbor-mi/abc1234/",
     "1819 Willowtree Ln, Ann Arbor, MI", None, None),
    # URL pasted inside a text message
    ("is this one any good? https://www.zillow.com/homedetails/1261-Island-Dr-APT-204-Ann-Arbor-MI-48105/24698469_zpid/ thx",
     "1261 Island Dr Apt 204, Ann Arbor, MI 48105", "Apt 204", "48105"),
]


@pytest.mark.parametrize("url,address,unit,zip_", FOUND)
def test_address_found(url, address, unit, zip_):
    r = parse_listing_url(url)
    assert r["address"] == address
    assert r["unit"] == unit
    assert r["zip"] == zip_
    assert r["needs_address"] is False
    assert r["hint"] is None


NEEDS = [
    # property names -> hint
    ("https://www.apartments.com/the-courtyards-ann-arbor-mi/abc123/", "apartments", "The Courtyards, Ann Arbor, MI"),
    ("https://www.apartments.com/willowtree-apartments-towers-ann-arbor-mi/jlbtfv5/", "apartments",
     "Willowtree Apartments Towers, Ann Arbor, MI"),
    # unknown multi-word-or-not city: no guess at where the name ends
    ("https://www.apartments.com/willow-tree-apartments-southfield-mi/gfxpqvy/", "apartments",
     "Willow Tree Apartments Southfield, MI"),
    # starts with a digit but no ZIP and no street suffix: a name, not an address
    ("https://www.apartments.com/411-lofts-ann-arbor-mi/xyz9876/", "apartments", "411 Lofts, Ann Arbor, MI"),
    ("https://www.zillow.com/b/hoover-and-greene-ann-arbor-mi-BPnVFJ/", "zillow", "Hoover and Greene, Ann Arbor, MI"),
    ("https://www.redfin.com/MI/Ann-Arbor/Arbor-Club-Apartments-Ann-Arbor-MI/apartment/177432919", "redfin",
     "Arbor Club Apartments, Ann Arbor, MI"),
    # no address in the URL at all
    ("https://www.zillow.com/homedetails/51177689_zpid/", "zillow", None),
    ("https://redf.in/aBc123", "redfin", None),
    ("https://www.redfin.com/city/782/MI/Ann-Arbor/apartments-for-rent", "redfin", None),
    ("https://www.zillow.com/ann-arbor-mi/apartments/", "zillow", None),
    ("https://www.apartments.com/houses/ann-arbor-mi/", "apartments", None),
    ("https://www.apartments.com/", "apartments", None),
]


@pytest.mark.parametrize("url,source,hint", NEEDS)
def test_needs_address(url, source, hint):
    r = parse_listing_url(url)
    assert r == {"address": None, "unit": None, "zip": None, "source": source, "needs_address": True, "hint": hint}


@pytest.mark.parametrize("junk", [
    None, 42, "", "   ", "not a url", "123 Main St, Ann Arbor, MI",
    "https://www.google.com/search?q=zillow+ann+arbor", "http://[", "zillow", "https://", "📎",
])
def test_junk(junk):
    r = parse_listing_url(junk)
    assert r["source"] == "unknown"
    assert r["needs_address"] is True
    assert r["address"] is None


def test_source_tags():
    assert parse_listing_url("https://www.zillow.com/homedetails/123-Main-St-Ann-Arbor-MI-48104/1_zpid/")["source"] == "zillow"
    assert parse_listing_url("https://www.redfin.com/MI/Ann-Arbor/123-Main-St-48104/home/1")["source"] == "redfin"
    assert parse_listing_url("https://www.apartments.com/the-courtyards-ann-arbor-mi/abc123/")["source"] == "apartments"


def test_never_touches_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("parse_listing_url must not make network calls")

    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    for url, *_ in FOUND + NEEDS:
        parse_listing_url(url)
