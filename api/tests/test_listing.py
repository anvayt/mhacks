"""Tests for app.listing.parse_listing_url. URLs are real-shaped (public listing URL formats, Oct 2026)."""

import socket

import pytest

from app.listing import find_url, parse_listing_url

FOUND = [
    # Zillow homedetails: APT / UNIT / '#' units (all become 'Unit <x>'), plain houses
    ("https://www.zillow.com/homedetails/549-Longshore-Dr-APT-A-Ann-Arbor-MI-48105/51177689_zpid/",
     "549 Longshore Dr Unit A, Ann Arbor, MI 48105", "Unit A", "48105"),
    ("https://www.zillow.com/homedetails/123-Main-St-APT-4-Ann-Arbor-MI-48104/12345_zpid/",
     "123 Main St Unit 4, Ann Arbor, MI 48104", "Unit 4", "48104"),
    ("https://www.zillow.com/homedetails/223-E-Ann-St-UNIT-7-Ann-Arbor-MI-48104/54793340_zpid/",
     "223 E Ann St Unit 7, Ann Arbor, MI 48104", "Unit 7", "48104"),
    ("https://www.zillow.com/homedetails/123-Main-St-#4-Ann-Arbor-MI-48104/12345_zpid/",
     "123 Main St Unit 4, Ann Arbor, MI 48104", "Unit 4", "48104"),
    ("https://www.zillow.com/homedetails/123-Main-St-%234B-Ann-Arbor-MI-48104/12345_zpid/",
     "123 Main St Unit 4B, Ann Arbor, MI 48104", "Unit 4B", "48104"),
    # no scheme, no www, share query string
    ("zillow.com/homedetails/3518-Carolyn-St-Ann-Arbor-MI-48104/60548563_zpid/?utm_source=share&utm_medium=ios",
     "3518 Carolyn St, Ann Arbor, MI 48104", None, "48104"),
    # mobile domain, uppercase scheme/host, photo fragment, no trailing slash before it
    ("HTTPS://M.ZILLOW.COM/homedetails/2125-Nature-Cove-Ct-APT-108-Ann-Arbor-MI-48104/24717147_zpid/#photo-3",
     "2125 Nature Cove Ct Unit 108, Ann Arbor, MI 48104", "Unit 108", "48104"),
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
    # Apartments.com unit listings put the unit after the state (real URLs, web search Oct 3, 2026);
    # a single token after 'unit' is kept, free text is dropped
    ("https://www.apartments.com/1218-washtenaw-ct-ann-arbor-mi-unit-1/9r3c5n5/",
     "1218 Washtenaw Ct Unit 1, Ann Arbor, MI", "Unit 1", None),
    ("https://www.apartments.com/120-w-washington-st-ann-arbor-mi-unit-ann-arbor/x71gwkm/",
     "120 W Washington St, Ann Arbor, MI", None, None),
    ("https://www.apartments.com/2110-washtenaw-ave-ann-arbor-mi-unit-3-bedroom-15-bath/q5dzgyw/",
     "2110 Washtenaw Ave, Ann Arbor, MI", None, None),
    # URL pasted inside a text message
    ("is this one any good? https://www.zillow.com/homedetails/1261-Island-Dr-APT-204-Ann-Arbor-MI-48105/24698469_zpid/ thx",
     "1261 Island Dr Unit 204, Ann Arbor, MI 48105", "Unit 204", "48105"),
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


# --- P2-02b: more listing sites. Real URLs from web search results (Oct 3, 2026) unless noted. ---
SITES_FOUND = [
    ("https://www.trulia.com/home/520-n-main-st-ann-arbor-mi-48104-24700899",
     "trulia", "520 N Main St, Ann Arbor, MI 48104", None, "48104"),
    # building pages: '<name>-<address>-<id>'; the name may hold digits or the city
    ("https://www.trulia.com/building/arbor-club-apartments-ann-arbor-mi-1100-rabbit-run-cir-ann-arbor-mi-48103-1002083151",
     "trulia", "1100 Rabbit Run Cir, Ann Arbor, MI 48103", None, "48103"),
    ("https://www.trulia.com/building/618-south-main-apartments-618-s-main-st-ann-arbor-mi-48104-1089090199",
     "trulia", "618 S Main St, Ann Arbor, MI 48104", None, "48104"),
    ("https://trulia.com/building/ann-arbor-city-club-apartments-201-s-1st-st-ann-arbor-mi-48104-1001768197",
     "trulia", "201 S 1st St, Ann Arbor, MI 48104", None, "48104"),
    # older /p/ pages (shape from the task brief): '<slug>--<id>'
    ("https://www.trulia.com/p/mi/ann-arbor/520-n-main-st-ann-arbor-mi-48104--2085436738",
     "trulia", "520 N Main St, Ann Arbor, MI 48104", None, "48104"),
    # Realtor.com detail shape, seen on its sister site highrises.com (same /realestateandhomes-detail/ path)
    ("https://www.realtor.com/realestateandhomes-detail/555-E-William-St-Apt-17H_Ann-Arbor_MI_48104_M41741-03633",
     "realtor", "555 E William St Unit 17H, Ann Arbor, MI 48104", "Unit 17H", "48104"),
    ("https://www.realtor.com/rentals/details/3531-Windemere-Dr_Ann-Arbor_MI_48105_M12345-67890",
     "realtor", "3531 Windemere Dr, Ann Arbor, MI 48105", None, "48105"),
    ("https://www.homes.com/property/1324-forest-ct-ann-arbor-mi/3ge3zs10x9bdn/",
     "homes", "1324 Forest Ct, Ann Arbor, MI", None, None),
    ("https://www.homes.com/property/1850-washtenaw-ave-ann-arbor-mi-48104/id-600020997889/",
     "homes", "1850 Washtenaw Ave, Ann Arbor, MI 48104", None, "48104"),
    ("https://hotpads.com/420-hill-st-ann-arbor-mi-48104-w1agra/building",
     "hotpads", "420 Hill St, Ann Arbor, MI 48104", None, "48104"),
    ("https://hotpads.com/3624-middleton-dr-ann-arbor-mi-48105-1kcngv0/pad",
     "hotpads", "3624 Middleton Dr, Ann Arbor, MI 48105", None, "48105"),
]


@pytest.mark.parametrize("url,source,address,unit,zip_", SITES_FOUND)
def test_more_sites_found(url, source, address, unit, zip_):
    assert parse_listing_url(url) == {"address": address, "unit": unit, "zip": zip_, "source": source,
                                      "needs_address": False, "hint": None}


SITES_NEEDS = [
    # HotPads listing titles and names: never an address
    ("https://hotpads.com/3-bed-10-bath-2850-ann-arbor-mi-48104-w1ajnr/pad", "hotpads", "Ann Arbor, MI"),
    ("https://hotpads.com/2-bed-10-bath-630-sqft-1660-ann-arbor-mi-48104-smxmnt/pad", "hotpads", "Ann Arbor, MI"),
    ("https://hotpads.com/arbor-club-apartments-ann-arbor-mi-ann-arbor-mi-48103-skzej3/pad", "hotpads",
     "Arbor Club Apartments, Ann Arbor, MI"),
    ("https://hotpads.com/traver-ridge-ann-arbor-mi-48105-smwbqc/building", "hotpads", "Traver Ridge, Ann Arbor, MI"),
    ("https://www.homes.com/ann-arbor-mi/48104/homes-for-rent/", "homes", None),
    ("https://www.trulia.com/for_rent/Ann_Arbor,MI/", "trulia", None),
    ("https://www.realtor.com/realestateandhomes-detail/M41741-03633", "realtor", None),
    # Zumper / Rent.com: slug is only a hint (Zumper p238's slug names a different street than its listing)
    ("https://www.zumper.com/apartment-buildings/p23039/715-arbor-st-ann-arbor-mi", "zumper",
     "715 Arbor St, Ann Arbor, MI"),
    ("https://www.zumper.com/apartment-buildings/p111536/main-commons-ann-arbor-mi", "zumper",
     "Main Commons, Ann Arbor, MI"),
    ("https://www.rent.com/r/3531-windemere-dr-ann-arbor-mi-lc6218945", "rent", "3531 Windemere Dr, Ann Arbor, MI"),
    ("https://www.rent.com/apartment/arbor-club-apartments-ann-arbor-mi-ann-arbor-mi-lc5969576", "rent",
     "Arbor Club Apartments, Ann Arbor, MI"),
    ("https://annarbor.craigslist.org/apa/d/ann-arbor-bedroom-apt-ann-arbor/7869345271.html", "craigslist",
     "Ann Arbor, MI"),
    ("https://newyork.craigslist.org/brk/apa/d/brooklyn-sunny-2br/7812345678.html", "craigslist", None),
    ("https://www.facebook.com/marketplace/item/1234567890123456/", "facebook", None),
    # map short links: parse_listing_url never expands them (app.links.resolve_link does)
    ("https://maps.app.goo.gl/RvL7iSNSsNaVBRru8", "google_maps", None),
    ("https://goo.gl/maps/Xy7AbC1dEf2", "google_maps", None),
    ("https://maps.apple/p/U8rE9v8n8iVZjr", "apple_maps", None),
    ("https://maps.apple.com/place?auid=7743130967838158422", "apple_maps", None),
    # map link with a name but no pin: the viewport centre '@' is not the place, so no coordinates
    ("https://www.google.com/maps/place/Arbor+Club+Apartments/@42.3,-83.79,15z", "google_maps", "Arbor Club Apartments"),
    ("https://maps.apple.com/?q=Ann%20Arbor", "apple_maps", "Ann Arbor"),
]


@pytest.mark.parametrize("url,source,hint", SITES_NEEDS)
def test_more_sites_need_address(url, source, hint):
    assert parse_listing_url(url) == {"address": None, "unit": None, "zip": None, "source": source,
                                      "needs_address": True, "hint": hint}


# Map links. Google shapes per developers.google.com/maps/documentation/urls and real maps.app.goo.gl
# expansions; Apple per its URL scheme docs, a real maps.apple/p expansion and iMessage CL.loc.vcf.
PIN = "data=!3m1!4b1!4m6!3m5!1s0x883cae3b8a1d0b0d:0x2a9b1e5f3c6d7e8f!8m2!3d42.2866021!4d-83.7469224!16s%2Fg%2F11c1q2w3e4"
MAPS = [
    # address + pin: the pin (!3d/!4d), not the viewport '@', gives the coordinates
    (f"https://www.google.com/maps/place/520+N+Main+St,+Ann+Arbor,+MI+48104/@42.2866,-83.7495,17z/{PIN}?entry=ttu",
     "google_maps", "520 N Main St, Ann Arbor, MI 48104", None, "48104", (42.2866021, -83.7469224)),
    ("https://www.google.com/maps/place/555+E+William+St+%2317H,+Ann+Arbor,+MI+48104/",
     "google_maps", "555 E William St Unit 17H, Ann Arbor, MI 48104", "Unit 17H", "48104", None),
    ("https://maps.google.com/?q=1100+Rabbit+Run+Cir,+Ann+Arbor,+MI+48103",
     "google_maps", "1100 Rabbit Run Cir, Ann Arbor, MI 48103", None, "48103", None),
    ("https://www.google.com/maps/search/?api=1&query=1100%20Rabbit%20Run%20Cir%2C%20Ann%20Arbor%2C%20MI",
     "google_maps", "1100 Rabbit Run Cir, Ann Arbor, MI", None, None, None),
    ("https://www.google.com/maps/search/1100+Rabbit+Run+Cir+Ann+Arbor+MI/@42.29,-83.79,15z",
     "google_maps", "1100 Rabbit Run Cir, Ann Arbor, MI", None, None, None),
    ("https://maps.google.com/maps?daddr=520+N+Main+St,+Ann+Arbor,+MI+48104",
     "google_maps", "520 N Main St, Ann Arbor, MI 48104", None, "48104", None),
    ("https://www.google.com/maps/dir/?api=1&destination=520+N+Main+St+Ann+Arbor+MI+48104",
     "google_maps", "520 N Main St, Ann Arbor, MI 48104", None, "48104", None),
    ("https://www.google.com/maps/dir/Michigan+Union,+530+S+State+St,+Ann+Arbor,+MI+48109/"
     "1100+Rabbit+Run+Cir,+Ann+Arbor,+MI+48103/@42.28,-83.77,13z/data=!4m2!4m1!3e0",
     "google_maps", "1100 Rabbit Run Cir, Ann Arbor, MI 48103", None, "48103", None),
    # Apple legacy share (address + ll pin + auid) and iOS 18.4+ /place (name part dropped)
    ("https://maps.apple.com/?address=520%20N%20Main%20St,%20Ann%20Arbor,%20MI%20%2048104,%20United%20States"
     "&auid=1234567890&ll=42.28655,-83.74625&lsp=9902&q=520%20N%20Main%20St",
     "apple_maps", "520 N Main St, Ann Arbor, MI 48104", None, "48104", (42.28655, -83.74625)),
    ("https://maps.apple.com/place?address=Arbor%20Club%20Apartments,%201100%20Rabbit%20Run%20Cir,%20Ann%20Arbor,"
     "%20MI%2048103,%20United%20States&coordinate=42.299200,-83.798900&name=Arbor%20Club%20Apartments"
     "&place-id=I7C250D2CDCB364A&map=h",
     "apple_maps", "1100 Rabbit Run Cir, Ann Arbor, MI 48103", None, "48103", (42.2992, -83.7989)),
    ("https://maps.apple.com/directions?destination=1218%20Washtenaw%20Ct%20Unit%201,%20Ann%20Arbor,%20MI%2048104",
     "apple_maps", "1218 Washtenaw Ct Unit 1, Ann Arbor, MI 48104", "Unit 1", "48104", None),
]


@pytest.mark.parametrize("url,source,address,unit,zip_,ll", MAPS)
def test_map_links_with_address(url, source, address, unit, zip_, ll):
    r = parse_listing_url(url)
    assert (r["source"], r["address"], r["unit"], r["zip"], r["needs_address"]) == (source, address, unit, zip_, False)
    if ll:
        assert (r["lat"], r["lon"], r["coords_only"]) == (*ll, False)
    else:
        assert "lat" not in r and "coords_only" not in r


VCARD = ("BEGIN:VCARD\nVERSION:3.0\nN:;Current Location;;;\nFN:Current Location\n"
         "item1.URL;type=pref:http://maps.apple.com/?ll=42.280826\\,-83.743038\nitem1.X-ABLabel:map url\nEND:VCARD\n")
COORDS = [
    # Named pins (hint set) need confirming: the name may be a business or a whole city, whose pin is
    # the city centre (real maps.app.goo.gl/N7Qqbomd6kmiEfst6 -> 'Ann Arbor, Michigan, ...').
    ("https://www.google.com/maps/place/Arbor+Club+Apartments/@42.30,-83.79,15z/data=!4m6!3m5!1s0x0:0x1!8m2"
     "!3d42.2992!4d-83.7989!16s", "google_maps", "Arbor Club Apartments", (42.2992, -83.7989), True),
    ("https://www.google.com/maps/place/Ann+Arbor,+Michigan,+USA/@42.2733,-83.8,12z/data=!3m1!4b1!4m6!3m5"
     "!1s0x883cb00ee6c8d5b5:0x2f0ad5d4b22ab9b7!8m2!3d42.2808256!4d-83.7430378!16zL20vMHFwc3k", "google_maps",
     "Ann Arbor, Michigan, USA", (42.2808256, -83.7430378), True),
    ("https://maps.apple.com/place?address=Ann%20Arbor,%20MI,%20United%20States&coordinate=42.2808,-83.743"
     "&name=Ann%20Arbor", "apple_maps", "Ann Arbor, MI, United States", (42.2808, -83.743), True),
    ("https://maps.apple.com/place?coordinate=42.299200,-83.798900&name=Arbor%20Club%20Apartments", "apple_maps",
     "Arbor Club Apartments", (42.2992, -83.7989), True),
    # bare map views: wherever the map was looking, not a chosen point
    ("https://www.google.com/maps/@42.2808,-83.743,17z", "google_maps", None, (42.2808, -83.743), True),
    ("https://www.google.com/maps/@?api=1&map_action=map&center=42.2808%2C-83.743&zoom=17", "google_maps", None,
     (42.2808, -83.743), True),
    # unnamed explicit points: safe to look up by point. Dropped pin text is degrees-minutes-seconds.
    ("https://www.google.com/maps/place/42%C2%B016'50.9%22N+83%C2%B044'34.8%22W/@42.2808,-83.743,17z/data=!3m1"
     "!4b1!4m4!3m3!8m2!3d42.280806!4d-83.743", "google_maps", None, (42.280806, -83.743), False),
    ("https://www.google.com/maps/search/?api=1&query=42.2808,-83.7430", "google_maps", None, (42.2808, -83.743), False),
    ("https://maps.google.com/maps?q=loc:42.2808,-83.7430", "google_maps", None, (42.2808, -83.743), False),
    ("https://maps.apple.com/?ll=42.280826,-83.743038&q=Dropped%20Pin", "apple_maps", None,
     (42.280826, -83.743038), False),
    # iMessage location share: a CL.loc.vcf vCard (commas escaped as '\,')
    (VCARD, "apple_maps", None, (42.280826, -83.743038), False),
    ("sent you my location http://maps.apple.com/?ll=42.280826,-83.743038&q=My%20Location", "apple_maps", None,
     (42.280826, -83.743038), False),
]


@pytest.mark.parametrize("url,source,hint,ll,needs", COORDS)
def test_map_links_coords_only(url, source, hint, ll, needs):
    assert parse_listing_url(url) == {"address": None, "unit": None, "zip": None, "source": source,
                                      "needs_address": needs, "hint": hint, "lat": ll[0], "lon": ll[1],
                                      "coords_only": True}


@pytest.mark.parametrize("text", [
    "is it this one? https://maps.app.goo.gl/N7Qqbomd6kmiEfst6.",
    "(https://maps.app.goo.gl/N7Qqbomd6kmiEfst6)",
    'he said "https://maps.app.goo.gl/N7Qqbomd6kmiEfst6"!',
])
def test_find_url_drops_trailing_punctuation(text):
    assert find_url(text) == "https://maps.app.goo.gl/N7Qqbomd6kmiEfst6"


def test_not_maps():
    # Google search isn't Google Maps; out-of-range "coordinates" aren't coordinates
    assert parse_listing_url("https://www.google.com/search?q=520+N+Main+St+Ann+Arbor")["source"] == "unknown"
    assert "lat" not in parse_listing_url("https://maps.apple.com/?ll=142.28,-83.74")


# One unit format for every site (team decision, Oct 3): '#4', APT-4, UNIT-4, STE-4, unit-4, Apt-17H and
# Trulia's bare number all become "Unit <x>"; the identifier itself is kept. Trulia, Homes.com and HotPads
# URLs below are real (web search, Oct 3, 2026).
UNITS = [
    ("https://www.zillow.com/homedetails/301-E-Liberty-St-STE-4-Ann-Arbor-MI-48104/1_zpid/",
     "301 E Liberty St Unit 4, Ann Arbor, MI 48104", "Unit 4"),
    ("https://www.zillow.com/homedetails/555-E-William-St-APT-1104-1B-Ann-Arbor-MI-48104/1_zpid/",
     "555 E William St Unit 1104-1B, Ann Arbor, MI 48104", "Unit 1104-1B"),
    ("https://www.redfin.com/MI/Ann-Arbor/555-E-William-St-48104/unit-1104-1B/home/1",
     "555 E William St Unit 1104-1B, Ann Arbor, MI 48104", "Unit 1104-1B"),
    ("https://www.realtor.com/realestateandhomes-detail/555-E-William-St-Unit-B1_Ann-Arbor_MI_48104_M1-2",
     "555 E William St Unit B1, Ann Arbor, MI 48104", "Unit B1"),
    ("https://www.trulia.com/p/mi/ann-arbor/336-s-division-st-1-ann-arbor-mi-48104--2543557687",
     "336 S Division St Unit 1, Ann Arbor, MI 48104", "Unit 1"),
    ("https://www.trulia.com/home/321-s-division-st-6-ann-arbor-mi-48104-2123211348",
     "321 S Division St Unit 6, Ann Arbor, MI 48104", "Unit 6"),
    ("https://www.trulia.com/home/555-e-william-st-apt-17h-ann-arbor-mi-48104-1",
     "555 E William St Unit 17H, Ann Arbor, MI 48104", "Unit 17H"),
    ("https://www.trulia.com/home/100-main-st-2-southfield-mi-48075-1",  # bare unit, unknown city
     "100 Main St Unit 2, Southfield, MI 48075", "Unit 2"),
    ("https://www.homes.com/property/6-parkview-place-ann-arbor-mi-unit-4/1ppkhgzjh32zs/",
     "6 Parkview Pl Unit 4, Ann Arbor, MI", "Unit 4"),
    ("https://hotpads.com/1115-willard-st-ann-arbor-mi-48104-w1aj91/101/pad",
     "1115 Willard St Unit 101, Ann Arbor, MI 48104", "Unit 101"),
    ("https://hotpads.com/220-w-ann-st-ann-arbor-mi-48104-1mn4cz3/1/pad",
     "220 W Ann St Unit 1, Ann Arbor, MI 48104", "Unit 1"),
    ("https://maps.apple.com/?address=301%20E%20Liberty%20St%20Ste%20200,%20Ann%20Arbor,%20MI%2048104",
     "301 E Liberty St Unit 200, Ann Arbor, MI 48104", "Unit 200"),
]


@pytest.mark.parametrize("url,address,unit", UNITS)
def test_one_unit_format(url, address, unit):
    r = parse_listing_url(url)
    assert (r["address"], r["unit"], r["needs_address"]) == (address, unit, False)


def test_highway_number_is_not_a_unit():
    assert parse_listing_url("https://www.zillow.com/homedetails/4500-US-Highway-23-Ann-Arbor-MI-48105/1_zpid/")[
        "unit"] is None


def test_new_formats_never_touch_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("parse_listing_url must not make network calls")

    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    for url, *_ in SITES_FOUND + SITES_NEEDS + MAPS + COORDS + UNITS:
        parse_listing_url(url)
