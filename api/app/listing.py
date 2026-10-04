"""Listing URL -> street address, from the URL text only.

PLAN.md §4 step 1: the address is in Zillow/Redfin URLs; parse the URL, never scrape the page.
This module makes no network calls, so short links (redf.in/..., maps.app.goo.gl/...) can't be
expanded here and come back needs_address; app.links.resolve_link expands the map ones.

URL shapes, checked against public listing URLs on Oct 3, 2026 (web search results):
  Zillow          /homedetails/549-Longshore-Dr-APT-A-Ann-Arbor-MI-48105/51177689_zpid/
                  /b/1819-willowtree-ln-ann-arbor-mi-5XqPf4/      (building page; last token is an id)
                  /b/hoover-and-greene-ann-arbor-mi-BPnVFJ/       (building name, not an address)
                  /homes/223-E-Ann-St-Ann-Arbor,-MI-48104_rb/     (address search)
  Redfin          /MI/Ann-Arbor/813-E-Kingsley-St-48104/unit-C1/home/99358421
                  /MI/Ann-Arbor/Arbor-Club-Apartments-Ann-Arbor-MI/apartment/177432919
  Apartments.com  /willowtree-apartments-towers-ann-arbor-mi/jlbtfv5/   (property name)
                  /1218-washtenaw-ct-ann-arbor-mi-unit-1/9r3c5n5/       (unit comes after the state)
  Trulia          /home/520-n-main-st-ann-arbor-mi-48104-24700899
                  /building/618-south-main-apartments-618-s-main-st-ann-arbor-mi-48104-1089090199
                  /p/mi/ann-arbor/<street>-<city>-<st>-<zip>--<id>          (older listing pages)
  Realtor.com     /realestateandhomes-detail/555-E-William-St-Apt-17H_Ann-Arbor_MI_48104_M41741-03633
                  /rentals/details/<street>_<City>_<ST>_<ZIP>_M<id>
  Homes.com       /property/1324-forest-ct-ann-arbor-mi/3ge3zs10x9bdn/
                  /property/1850-washtenaw-ave-ann-arbor-mi-48104/id-600020997889/
  HotPads         /420-hill-st-ann-arbor-mi-48104-w1agra/building, /traver-ridge-ann-arbor-mi-48105-smwbqc/pad
                  /3-bed-10-bath-2850-ann-arbor-mi-48104-w1ajnr/pad       (listing title, not an address)
  Zumper          /apartment-buildings/p23039/715-arbor-st-ann-arbor-mi   (slug can disagree with the
                  listing's real address, e.g. p238, so it is only ever a hint)
  Rent.com        /r/3531-windemere-dr-ann-arbor-mi-lc6218945, /apartment/<name>-ann-arbor-mi-ann-arbor-mi-lc<id>
  Craigslist      annarbor.craigslist.org/apa/d/ann-arbor-bedroom-apt-ann-arbor/7869345271.html
  Google Maps     /maps/place/<text>/@<view>/data=...!3d<lat>!4d<lon>  (!3d/!4d is the pin; @ is the
                  viewport centre, 25 km off at zoom 10), /maps/search/<text>, /maps/dir/../<dest>,
                  /maps/@lat,lon,17z, ?q= ?query= ?daddr= ?destination= (developers.google.com/maps/
                  documentation/urls), short maps.app.goo.gl/<id> and goo.gl/maps/<id> (302 -> google.com/maps)
  Apple Maps      legacy /?address=..&ll=lat,lon&q=..&auid=..; iOS 18.4+ /place?address=..&coordinate=
                  lat,lon&name=..&place-id=.., /search?query=, /directions?destination=; iMessage location
                  shares are CL.loc.vcf vCards holding maps.apple.com/?ll=lat\\,lon (vCard escapes ','); iOS 26
                  short maps.apple/p/<id> (301 -> /place?address=..&coordinate=.. on GET, 404 on HEAD)
Street suffix abbreviations follow USPS Publication 28, Appendix C1.
"""

import re
from urllib.parse import parse_qs, unquote, urlsplit

STATES = set(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ "
    "NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR".split()
)
SUFFIXES = {  # USPS Pub 28 abbreviations for common street suffixes
    "st": "St", "street": "St", "ave": "Ave", "av": "Ave", "avenue": "Ave", "rd": "Rd", "road": "Rd",
    "dr": "Dr", "drive": "Dr", "blvd": "Blvd", "boulevard": "Blvd", "ln": "Ln", "lane": "Ln",
    "ct": "Ct", "court": "Ct", "pl": "Pl", "place": "Pl", "cir": "Cir", "circle": "Cir",
    "ter": "Ter", "terrace": "Ter", "pkwy": "Pkwy", "parkway": "Pkwy", "hwy": "Hwy",
    "highway": "Hwy", "trl": "Trl", "trail": "Trl", "way": "Way", "sq": "Sq", "square": "Sq",
}
UNITS = {"apt": "Apt", "apartment": "Apt", "unit": "Unit", "ste": "Ste", "suite": "Ste", "#": "#"}
DIRECTIONS = {"n", "s", "e", "w", "ne", "nw", "se", "sw"}
SMALL_WORDS = {"and", "of", "at", "on", "the", "in"}
# Multi-word city names can't be told apart from a property name in a slug, so we only split off
# cities we know. ponytail: Ann Arbor area + a few MI cities; add more if listings elsewhere matter.
KNOWN_CITIES = sorted(
    (c.split() for c in ("ann arbor", "ypsilanti", "saline", "dexter", "chelsea", "detroit",
                         "lansing", "east lansing", "grand rapids", "kalamazoo")),
    key=len, reverse=True,
)
ZIP = re.compile(r"\d{5}")
URL_IN_TEXT = re.compile(r"(?:https?://)?[\w.-]+\.[a-z]{2,}/\S*", re.I)
LISTING_WORDS = {"bed", "beds", "bedroom", "bedrooms", "bath", "baths", "bathroom", "bathrooms", "sqft"}
PIN_LABELS = {"dropped pin", "my location", "current location", "marked location"}  # not place names
COUNTRY = {"united states", "united states of america", "usa", "us"}
GOOGLE = re.compile(r"(?:www\.|maps\.)?google\.(?:com?\.)?[a-z]{2,3}")
LATLON = re.compile(r"(?:loc:)?(-?\d{1,2}\.\d+),\s*(-?\d{1,3}\.\d+)")
HOUSE_NO = re.compile(r"\d+[a-z]?", re.I)  # '1100', '12b'; not '1st'


def parse_listing_url(url: str) -> dict:
    """Pasted listing link -> {"address", "unit", "zip", "source", "needs_address", "hint"}.

    address is e.g. "123 Main St Apt 4, Ann Arbor, MI 48104" (unit included), or None when the URL
    holds no address; then needs_address is True and hint is a best-effort place string to confirm
    (e.g. "The Courtyards, Ann Arbor, MI"), or None. Also accepts a URL inside a sentence.

    Map links (Google/Apple) add "lat", "lon" and "coords_only" when they carry coordinates. A map
    link with coordinates but no readable address gives address None, needs_address False,
    coords_only True (look the building up by point). Without coordinates these keys are absent.
    """
    url = find_url(url)
    if not url:
        return _needs("unknown")
    parts = urlsplit(url.replace("#", "%23"))  # '#' is a unit marker in Zillow slugs, not a fragment
    host = parts.hostname or ""
    segs = [unquote(s) for s in parts.path.split("/") if s]
    if _on(host, "zillow.com"):
        return _zillow(segs)
    if _on(host, "redfin.com"):
        return _redfin(segs)
    if _on(host, "redf.in"):
        return _needs("redfin")  # share short link: expanding it would need a network call
    if _on(host, "apartments.com"):
        return _apartments(segs)
    if GOOGLE.fullmatch(host) and (host.startswith("maps.") or segs[:1] == ["maps"]):
        return _google(parts, segs)
    if host == "maps.app.goo.gl" or (host == "goo.gl" and segs[:1] == ["maps"]):
        return _needs("google_maps")  # short link: app.links.resolve_link expands it
    if _on(host, "maps.apple.com"):
        return _apple(parts)
    if host == "maps.apple":
        return _needs("apple_maps")  # short link: app.links.resolve_link expands it
    if _on(host, "trulia.com"):
        return _trulia(segs)
    if _on(host, "realtor.com"):
        return _realtor(segs)
    if _on(host, "homes.com"):
        return _homes(segs)
    if _on(host, "hotpads.com"):
        return _hotpads(segs)
    if _on(host, "zumper.com") or _on(host, "rent.com"):
        return _hint_only(host.split(".")[-2], segs)
    if _on(host, "craigslist.org"):  # annarbor.craigslist.org: the region is the only place info
        city = next((c for c in KNOWN_CITIES if "".join(c) == host.split(".")[0]), None)
        return _needs("craigslist", city and _title(city) + ", MI")  # ponytail: KNOWN_CITIES are all MI
    if _on(host, "facebook.com"):
        return _needs("facebook")  # Marketplace: /marketplace/item/<id>/, nothing but an id
    return _needs("unknown")


def find_url(text: str) -> str | None:
    """First URL in a message, with a scheme; None if there is none."""
    m = URL_IN_TEXT.search(text) if isinstance(text, str) else None
    if not m:
        return None
    raw = m.group(0).replace("\\", "")  # iMessage CL.loc.vcf vCards escape ',' as '\,'
    return raw if re.match(r"https?://", raw, re.I) else "https://" + raw


def _zillow(segs: list[str]) -> dict:
    for i, s in enumerate(segs):
        if re.fullmatch(r"\d+_zpid", s, re.I):
            if i == 0 or segs[i - 1].lower() == "homedetails":
                return _needs("zillow")  # /homedetails/<id>_zpid/ carries no address
            return _from_tokens("zillow", _tokens(segs[i - 1]))
        if s.lower().endswith("_rb"):
            return _from_tokens("zillow", _tokens(s[:-3]))
    if len(segs) >= 2 and segs[0].lower() == "b":
        return _from_tokens("zillow", _tokens(segs[1])[:-1])  # drop the building id token
    return _needs("zillow")


def _redfin(segs: list[str]) -> dict:
    """/<ST>/<City>/<slug>/[unit-<x>/](home|apartment)/<id>; the slug is '<street>-<ZIP>' or a name."""
    k = next((i for i, s in enumerate(segs) if s.lower() in ("home", "apartment")), None)
    if k not in (3, 4) or segs[0].upper() not in STATES:
        return _needs("redfin")
    state, city, t = segs[0].upper(), _title(_tokens(segs[1])), _tokens(segs[2])
    zip_ = t.pop() if t and ZIP.fullmatch(t[-1]) else None
    if len(t) >= 2 and t[0][0].isdigit():
        unit = None
        if k == 4 and segs[3].lower().startswith("unit-"):
            unit = "Unit " + segs[3][5:].upper()
        return _found("redfin", _fmt_street(t), unit, city, state, zip_)
    return _needs("redfin", _name_hint(t, city, state))


def _apartments(segs: list[str]) -> dict:
    """/<slug>/<id>/. Unit listings put 'unit-<x>' after the state: 1218-washtenaw-ct-ann-arbor-mi-unit-1."""
    t = _tokens(segs[0]) if segs else []
    r = _from_tokens("apartments", t)
    k = next((i for i in range(len(t) - 1, 0, -1) if t[i].lower() == "unit" and t[i - 1].upper() in STATES), None)
    if not r["needs_address"] or k is None:
        return r
    # One token after 'unit' is the unit; more is free text ('unit-3-bedroom-15-bath'), so drop it.
    return _from_tokens("apartments", t[:k], "Unit " + t[k + 1].upper() if len(t) == k + 2 else None)


def _trulia(segs: list[str]) -> dict:
    """/home/<address>-<id>, /p/<st>/<city>/<address>--<id>, /building/<name>-<address>-<id>."""
    kind = segs[0].lower() if segs else ""
    if kind not in ("home", "p", "building") or len(segs) < 2:
        return _needs("trulia")
    t = _tokens(segs[-1].split("--")[0])
    if t and t[-1].isdigit() and not ZIP.fullmatch(t[-1]):
        t.pop()  # listing id
    if kind != "building":
        return _from_tokens("trulia", t)
    # The name comes first and may hold digits ('618 South Main Apartments'), so the address starts
    # at the rightmost house number that parses. ponytail: 'W 8 Mile Rd' would lose its house number.
    for i in range(len(t) - 1, 0, -1):
        if HOUSE_NO.fullmatch(t[i]) and not (r := _from_tokens("trulia", t[i:]))["needs_address"]:
            return r
    return _needs("trulia", _name_hint(t))


def _realtor(segs: list[str]) -> dict:
    """/realestateandhomes-detail/<street>_<City>_<ST>_<ZIP>_M<id> (also /rentals/details/...)."""
    p = next((s.split("_") for s in segs if s.count("_") >= 2), [])
    if len(p) < 3 or p[2].upper() not in STATES:
        return _needs("realtor")
    city, state = _title(_tokens(p[1])), p[2].upper()
    if not p[0][:1].isdigit():
        return _needs("realtor", _name_hint(_tokens(p[0]), city, state))
    street, unit = _split_unit(_tokens(p[0]))
    zip_ = p[3] if len(p) > 3 and ZIP.fullmatch(p[3]) else None
    return _found("realtor", _fmt_street(street), unit, city, state, zip_)


def _homes(segs: list[str]) -> dict:
    """/property/<street>-<city>-<st>[-<zip>]/<id>/"""
    if len(segs) >= 2 and segs[0].lower() == "property":
        return _from_tokens("homes", _tokens(segs[1]))
    return _needs("homes")


def _hotpads(segs: list[str]) -> dict:
    """/<address or name or listing title>-<city>-<st>-<zip>-<id>/pad (or /building)."""
    if len(segs) >= 2 and segs[-1].lower() in ("pad", "building"):
        return _from_tokens("hotpads", _tokens(segs[0])[:-1])
    return _needs("hotpads")


def _hint_only(source: str, segs: list[str]) -> dict:
    """Zumper, Rent.com: never an address (P2-02b), but a slug ending '-<city>-<st>[-<id>]' is a hint."""
    for s in reversed(segs):
        t = _tokens(s)
        if len(t) > 1 and t[-1].upper() not in STATES and not ZIP.fullmatch(t[-1]):
            t.pop()  # listing id ('lc6218945')
        if hint := _name_hint(t):
            return _needs(source, hint)
    return _needs(source)


def _google(parts, segs: list[str]) -> dict:
    q = _query(parts)
    kind = segs[1] if len(segs) > 1 else ""
    text = None
    if kind in ("place", "search") and len(segs) > 2:
        text = segs[2]
    elif kind == "dir":  # /maps/dir/<origin>/<destination>/@view/data=...
        text = next((s for s in reversed(segs[2:]) if not s.startswith(("@", "data=", "am="))), None)
    texts = [t for t in (text, q("q"), q("query"), q("daddr"), q("destination"))
             if t and not t.startswith(("@", "place_id:"))]
    pin = re.search(r"!3d(-?[\d.]+)!4d(-?[\d.]+)", parts.path)
    view = re.match(r"@(-?[\d.]+),(-?[\d.]+)", kind)  # bare /maps/@lat,lon,17z; ignored on place/search
    return _map_result("google_maps", texts, [pin and f"{pin[1]},{pin[2]}"],
                       [view and f"{view[1]},{view[2]}", q("ll"), q("center")])


def _apple(parts) -> dict:
    q = _query(parts)
    # sll / center are the search area or viewport, not the place, so they're not used.
    texts = [q(k) for k in ("address", "q", "name", "query", "daddr", "destination")]
    return _map_result("apple_maps", texts, [q("coordinate"), q("ll")])


def _map_result(source: str, texts: list, pins: list, views: list = ()) -> dict:
    """First text that reads as a US address wins; coordinates: pin, then coordinate text, then view."""
    texts = [" ".join(t.replace("+", " ").split()) for t in texts if t and t.strip()]
    ll = next((c for c in map(_latlon, [*pins, *texts, *views]) if c), None)
    r = next((a for t in texts if (a := _address_text(source, t))), None)
    if r is None:
        names = (t for t in texts if not _latlon(t) and "°" not in t and t.lower() not in PIN_LABELS)
        r = _needs(source, next(names, None))
        r["needs_address"] = ll is None
    if ll:
        r.update(lat=ll[0], lon=ll[1], coords_only=r["address"] is None)
    return r


def _address_text(source: str, text: str) -> dict | None:
    """'Arbor Club, 1100 Rabbit Run Cir, Ann Arbor, MI 48103, United States' -> found, else None."""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if parts and parts[-1].lower() in COUNTRY:
        parts.pop()
    m = re.fullmatch(r"([A-Za-z]{2})(?:\s+(\d{5})(?:-\d{4})?)?", parts[-1]) if len(parts) >= 3 else None
    # The street is the last part before the city that starts with a house number; earlier parts
    # are a place name ('Apple Inc.'), later ones a unit ('Apt 4').
    k = next((i for i in range(len(parts) - 3, -1, -1) if re.match(r"\d+[a-z]?\s", parts[i], re.I)), None)
    if m and m[1].upper() in STATES and k is not None:
        street, unit = _split_unit(" ".join(parts[k:-2]).replace("#", " # ").split())
        return _found(source, " ".join(street), unit, parts[-2], m[1].upper(), m[2])
    r = _from_tokens(source, _tokens(text))  # no commas: '1100 Rabbit Run Cir Ann Arbor MI'
    return None if r["needs_address"] else r


def _latlon(s: str | None) -> tuple[float, float] | None:
    m = LATLON.fullmatch(s.strip()) if s else None
    if m and abs(float(m[1])) <= 90 and abs(float(m[2])) <= 180:
        return float(m[1]), float(m[2])
    return None


def _query(parts):
    q = parse_qs(parts.query)
    return lambda k: q.get(k, [None])[0]


def _from_tokens(source: str, tokens: list[str], unit: str | None = None) -> dict:
    """Slug tokens '[street.. (unit) city.. ST (ZIP)]' -> found address, else a name hint.

    `unit` is used when the slug has no unit marker of its own (Apartments.com puts it after the state).
    """
    t = list(tokens)
    zip_ = t.pop() if t and ZIP.fullmatch(t[-1]) else None
    if len(t) >= 3 and t[-1].upper() in STATES and t[0][0].isdigit():
        split = _street_unit_city(t[:-1])
        # Without a ZIP, also demand a street suffix: names like "411 Lofts" start with digits too.
        # Listing titles ('3-bed-10-bath-2850-ann-arbor-mi-48104', HotPads) aren't streets.
        if split and (zip_ or split[1] or any(x.lower() in SUFFIXES for x in split[0][1:])) \
                and not any(x.lower() in LISTING_WORDS for x in split[0]):
            street, slug_unit, city = split
            return _found(source, _fmt_street(street), slug_unit or unit, _title(city), t[-1].upper(), zip_)
    return _needs(source, _name_hint(tokens))


def _street_unit_city(t: list[str]) -> tuple[list[str], str | None, list[str]] | None:
    """Split '[street.. (unit marker + value) city..]' tokens; None if no split is found."""
    low = [x.lower() for x in t]
    for i in range(2, len(t) - 1):
        if low[i] in UNITS:
            return t[:i], _unit(t[i], t[i + 1]), t[i + 2:]
    n = _city_len(t, KNOWN_CITIES)
    if n and len(t) - n >= 2:
        return t[:-n], None, t[-n:]
    # ponytail: last suffix wins, so "St Clair Ave" works but city "St Clair Shores" needs KNOWN_CITIES
    for j in range(len(t) - 2, 0, -1):
        if low[j] in SUFFIXES:
            if low[j + 1] in DIRECTIONS and j + 2 < len(t):
                j += 1  # "Main St NE"
            return t[: j + 1], None, t[j + 1:]
    return None


def _name_hint(tokens: list[str], city: str | None = None, state: str | None = None) -> str | None:
    """Property-name slug -> 'The Courtyards, Ann Arbor, MI'. None without a state (e.g. search pages)."""
    t = list(tokens)
    if t and ZIP.fullmatch(t[-1]):
        t.pop()
    if t and t[-1].upper() in STATES:
        state = t.pop().upper()
    if not state:
        return None
    n = _city_len(t, [city.lower().split()] if city else KNOWN_CITIES)
    if n:
        city = city or _title(t[-n:])
        t = t[:-n]
        if [x.lower() for x in t[-n - 1:]] == city.lower().split() + [state.lower()]:
            t = t[:-n - 1]  # HotPads/Rent.com repeat the place: '<name>-<city>-<st>-<city>-<st>'
    if any(w.lower() in LISTING_WORDS for w in t):
        t = []  # a listing title ('3 bed 1 bath $2850'), not a place name
    name = " ".join(w.lower() if k and w.lower() in SMALL_WORDS else w.capitalize() for k, w in enumerate(t))
    return ", ".join(p for p in (name, city, state) if p)


def _split_unit(t: list[str]) -> tuple[list[str], str | None]:
    """['555', 'E', 'William', 'St', 'Apt', '17H'] -> (['555', 'E', 'William', 'St'], 'Apt 17H')."""
    i = next((i for i in range(2, len(t) - 1) if t[i].lower() in UNITS), None)
    return (t, None) if i is None else (t[:i], _unit(t[i], t[i + 1]))


def _unit(marker: str, value: str) -> str:
    label = UNITS[marker.lower()]
    return f"#{value.upper()}" if label == "#" else f"{label} {value.upper()}"


def _city_len(t: list[str], cities: list[list[str]]) -> int:
    """How many trailing tokens of t spell one of `cities`, leaving at least one token before it."""
    low = [x.lower() for x in t]
    return next((len(c) for c in cities if len(t) > len(c) and low[-len(c):] == c), 0)


def _tokens(slug: str) -> list[str]:
    """'223-E-Ann-St-#4' -> ['223', 'E', 'Ann', 'St', '#', '4']."""
    return [x for x in re.split(r"[-\s,+.]+", slug.replace("#", " # ")) if x]


def _fmt_street(t: list[str]) -> str:
    """['123', 'n', 'main', 'street'] -> '123 N Main St' (suffix abbreviated only in last position)."""
    end = len(t) - 2 if len(t) > 2 and t[-1].lower() in DIRECTIONS else len(t) - 1
    out = []
    for k, w in enumerate(t):
        lw = w.lower()
        if k == 0 or lw in DIRECTIONS:
            out.append(w.upper())
        elif k == end and lw in SUFFIXES:
            out.append(SUFFIXES[lw])
        else:
            out.append(w.capitalize())
    return " ".join(out)


def _title(t: list[str]) -> str:
    return " ".join(w.capitalize() for w in t)


def _on(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def _found(source: str, street: str, unit: str | None, city: str, state: str, zip_: str | None) -> dict:
    line = f"{street} {unit}" if unit else street
    address = ", ".join(p for p in (line, city, f"{state} {zip_}" if zip_ else state) if p)
    return {"address": address, "unit": unit, "zip": zip_, "source": source, "needs_address": False, "hint": None}


def _needs(source: str, hint: str | None = None) -> dict:
    return {"address": None, "unit": None, "zip": None, "source": source, "needs_address": True, "hint": hint}
