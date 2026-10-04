"""Listing URL -> street address, from the URL text only.

PLAN.md §4 step 1: the address is in Zillow/Redfin URLs; parse the URL, never scrape the page.
This module makes no network calls, so short links (redf.in/...) can't be expanded and come back
needs_address.

URL shapes, checked against public listing URLs on Oct 3, 2026 (web search results):
  Zillow          /homedetails/549-Longshore-Dr-APT-A-Ann-Arbor-MI-48105/51177689_zpid/
                  /b/1819-willowtree-ln-ann-arbor-mi-5XqPf4/      (building page; last token is an id)
                  /b/hoover-and-greene-ann-arbor-mi-BPnVFJ/       (building name, not an address)
                  /homes/223-E-Ann-St-Ann-Arbor,-MI-48104_rb/     (address search)
  Redfin          /MI/Ann-Arbor/813-E-Kingsley-St-48104/unit-C1/home/99358421
                  /MI/Ann-Arbor/Arbor-Club-Apartments-Ann-Arbor-MI/apartment/177432919
  Apartments.com  /willowtree-apartments-towers-ann-arbor-mi/jlbtfv5/   (property name)
                  /1218-washtenaw-ct-ann-arbor-mi-unit-1/9r3c5n5/       (unit comes after the state)
Street suffix abbreviations follow USPS Publication 28, Appendix C1.
"""

import re
from urllib.parse import unquote, urlsplit

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


def parse_listing_url(url: str) -> dict:
    """Pasted listing link -> {"address", "unit", "zip", "source", "needs_address", "hint"}.

    address is e.g. "123 Main St Apt 4, Ann Arbor, MI 48104" (unit included), or None when the URL
    holds no address; then needs_address is True and hint is a best-effort place string to confirm
    (e.g. "The Courtyards, Ann Arbor, MI"), or None. Also accepts a URL inside a sentence.
    """
    m = URL_IN_TEXT.search(url) if isinstance(url, str) else None
    if not m:
        return _needs("unknown")
    raw = m.group(0)
    if not re.match(r"https?://", raw, re.I):
        raw = "https://" + raw
    parts = urlsplit(raw.replace("#", "%23"))  # '#' is a unit marker in Zillow slugs, not a fragment
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
    return _needs("unknown")


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


def _from_tokens(source: str, tokens: list[str], unit: str | None = None) -> dict:
    """Slug tokens '[street.. (unit) city.. ST (ZIP)]' -> found address, else a name hint.

    `unit` is used when the slug has no unit marker of its own (Apartments.com puts it after the state).
    """
    t = list(tokens)
    zip_ = t.pop() if t and ZIP.fullmatch(t[-1]) else None
    if len(t) >= 3 and t[-1].upper() in STATES and t[0][0].isdigit():
        split = _street_unit_city(t[:-1])
        # Without a ZIP, also demand a street suffix: names like "411 Lofts" start with digits too.
        if split and (zip_ or split[1] or any(x.lower() in SUFFIXES for x in split[0][1:])):
            street, slug_unit, city = split
            return _found(source, _fmt_street(street), slug_unit or unit, _title(city), t[-1].upper(), zip_)
    return _needs(source, _name_hint(tokens))


def _street_unit_city(t: list[str]) -> tuple[list[str], str | None, list[str]] | None:
    """Split '[street.. (unit marker + value) city..]' tokens; None if no split is found."""
    low = [x.lower() for x in t]
    for i in range(2, len(t) - 1):
        if low[i] in UNITS:
            label, value = UNITS[low[i]], t[i + 1].upper()
            return t[:i], f"#{value}" if label == "#" else f"{label} {value}", t[i + 2:]
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
    name = " ".join(w.lower() if k and w.lower() in SMALL_WORDS else w.capitalize() for k, w in enumerate(t))
    return ", ".join(p for p in (name, city, state) if p)


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
