"""Ann Arbor building-footprint lookup (offline, from the /data/ cache made by scripts/fetch_footprints.py).

Sources:
- City of Ann Arbor BuildingFootprints FeatureServer (OSI/BuildingFootprints/FeatureServer/0):
  polygons with STORIES, ABG_BLD_HG (height above ground, feet), Struc_Type.
- City of Ann Arbor MailingAddress FeatureServer (MailingAddress/FeatureServer/0): one point per
  postal address, incl. unit rows ("2567 AVANT AVE UNIT 101"). Units = the larger of the "General Mailing"
  addresses inside the footprint and the "... UNIT n" rows (any TYPE) for the address's street line, because
  some buildings' unit rows are TYPE "Vacant" (721 S Forest Ave) or sit 5-11 m outside the footprint
  (2901 Northbrook Pl, 1770 Broadway St).
Geometry is projected to UTM 17N (EPSG:32617) so areas and distances are in metres.
"""

import json
import re
from collections import Counter
from dataclasses import dataclass
from functools import cache

import numpy as np
import shapely
from pyproj import Transformer
from shapely.geometry import Point, mapping, shape

from app.geo import ADDRESSES_PATH, FOOTPRINTS_PATH

NEAREST_MAX_M = 25.0
CITY_POINT_MAX_M = 250.0
# Reuse the existing 250 m city-point tolerance only for footprints containing this exact street line.
# This is an address-constrained fallback, never a wider nearest-building guess.
ADDRESS_SEARCH_MAX_M = CITY_POINT_MAX_M
# USPS street-suffix / directional abbreviations, matching the city's PROPSTREET style ("1300 S UNIVERSITY AVE")
_ABBR = {"STREET": "ST", "AVENUE": "AVE", "ROAD": "RD", "DRIVE": "DR", "BOULEVARD": "BLVD", "COURT": "CT",
         "PLACE": "PL", "LANE": "LN", "CIRCLE": "CIR", "TERRACE": "TER", "PARKWAY": "PKWY", "HIGHWAY": "HWY",
         "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
_TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32617", always_xy=True)


def street_key(address: str) -> str:
    """'1300 South University Avenue Apt 9, Ann Arbor' -> '1300 S UNIVERSITY AVE' (street line, no unit)."""
    line = re.sub(r"\s*(?:#|\b(?:APT|UNIT|STE|SUITE)\b)\s*\S*\s*$", "", address.split(",")[0].upper())
    return " ".join(_ABBR.get(w, w) for w in line.replace(".", " ").split())


def _project(geoms):
    """WGS84 lon/lat geometries -> UTM 17N metres (vectorised)."""
    return shapely.transform(geoms, lambda xy: np.column_stack(_TO_UTM.transform(xy[:, 0], xy[:, 1])))


@dataclass
class Building:
    props: dict            # raw footprint attributes
    geojson: dict          # footprint geometry, WGS84
    area_m2: float         # footprint area in UTM 17N
    addresses: list[str]   # residential ("General Mailing") addresses inside the footprint
    match: str             # how the footprint was found
    distance_m: float      # 0 if the point is inside the footprint
    street: str | None     # street line whose city point located the footprint (None: geocoder point used)
    street_units: int      # "<street> UNIT n" rows in the city layer for `street`, any TYPE


@dataclass
class _Index:
    props: list[dict]
    wgs: np.ndarray
    utm: np.ndarray
    tree: shapely.STRtree
    addr_street: np.ndarray
    addr_residential: np.ndarray  # TYPE == "General Mailing" (not University/Public School/Vacant/...)
    addr_utm: np.ndarray
    addr_tree: shapely.STRtree
    addr_by_street: dict[str, int]
    units_by_street: Counter[str]
    ft_per_story: float
    ft_offset: float


@cache
def _index() -> _Index:
    if not FOOTPRINTS_PATH.exists() or not ADDRESSES_PATH.exists():
        raise RuntimeError("Footprint cache missing. From /api run: uv run python scripts/fetch_footprints.py")
    fp = json.loads(FOOTPRINTS_PATH.read_text())["features"]
    props = [f["properties"] for f in fp]
    wgs = np.array([shape(f["geometry"]) for f in fp])
    utm = _project(wgs)

    ad = [a for a in json.loads(ADDRESSES_PATH.read_text())["features"] if a["geometry"]]
    street = np.array([a["properties"]["PROPSTREET"].strip().upper() for a in ad])
    residential = np.array([a["properties"]["TYPE"] == "General Mailing" for a in ad])
    addr_utm = _project(np.array([shape(a["geometry"]) for a in ad]))

    # Height -> stories: least-squares fit of ABG_BLD_HG (ft) on STORIES over the footprints that
    # have both (14,9xx rows; ~11.1 ft/story + 1.4 ft). 85% exact, 99% within one story on those rows.
    hs = np.array([(p["ABG_BLD_HG"], p["STORIES"]) for p in props if p["STORIES"] and p["ABG_BLD_HG"]])
    slope, offset = np.polyfit(hs[:, 1], hs[:, 0], 1)

    return _Index(props, wgs, utm, shapely.STRtree(utm), street, residential, addr_utm, shapely.STRtree(addr_utm),
                  _first_by_key(street), Counter(street_key(s) for s in street if " UNIT " in s),
                  float(slope), float(offset))


def _first_by_key(streets) -> dict[str, int]:
    out: dict[str, int] = {}
    for i, s in enumerate(streets):
        out.setdefault(street_key(s), i)  # "912 MARY ST UNIT 1" is also findable as "912 MARY ST"
    return out


def city_address(address: str) -> dict | None:
    """Exact city MailingAddress street line, including unit rows; never substitute another house number.

    Bare street lines are local (this API serves Ann Arbor). An explicit different town must not
    borrow an Ann Arbor point with the same street line, even when Census cannot find the address.
    """
    locality = address.split(",")[1:]
    if locality and not re.fullmatch(r"\s*ANN ARBOR(?:\s+(?:MI|MICHIGAN)(?:\s+\d{5})?)?\s*", locality[0], re.I):
        return None
    if len(locality) > 1 and not re.fullmatch(r"\s*(?:MI|MICHIGAN)(?:\s+\d{5}(?:-\d{4})?)?\s*", locality[1], re.I):
        return None
    if not FOOTPRINTS_PATH.exists() or not ADDRESSES_PATH.exists():
        return None
    ix = _index()
    key = street_key(address)
    i = ix.addr_by_street.get(key)
    if i is None:
        return None
    lon, lat = _TO_UTM.transform(ix.addr_utm[i].x, ix.addr_utm[i].y, direction="INVERSE")
    return {"matched_address": f"{key}, ANN ARBOR, MI", "lon": lon, "lat": lat,
            "block_geoid": None, "source": "City of Ann Arbor MailingAddress (exact street line)"}


def stories_from_height(height_ft: float) -> int:
    """Estimate stories from ABG_BLD_HG using the fit above (used only when STORIES is null)."""
    ix = _index()
    return max(1, round((height_ft - ix.ft_offset) / ix.ft_per_story))


def height_fit() -> tuple[float, float]:
    """(feet per story, offset feet) of the height->stories fit, for source notes."""
    ix = _index()
    return ix.ft_per_story, ix.ft_offset


def _addresses_in(ix: _Index, i: int) -> list[str]:
    j = ix.addr_tree.query(ix.utm[i], predicate="contains")
    hits = set(ix.addr_street[j[ix.addr_residential[j]]])
    # A building listed both as "12 MAIN ST" and "12 MAIN ST UNIT 1..n" has n units, not n+1.
    bases = {s.split(" UNIT ")[0] for s in hits if " UNIT " in s}
    return sorted(hits - bases)


def find_building(lon: float, lat: float, streets: list[str] = ()) -> Building:
    """Footprint for an address.

    Point used: the city's mailing-address point (any TYPE) for the first of `streets` that the city
    knows within 250 m of the geocode (typed address first, then the geocoder's match), because it
    usually sits inside the building; else the geocoded lon/lat (interpolated along the
    street, so it often lands outside the footprint). Then: footprint containing the point, else the
    nearest footprint within 25 m, preferring footprints that hold a mailing address (houses over
    garages). If none is within 25 m, search up to 250 m but only accept footprints containing
    this exact street line. geocode() corrects displaced Census points before this lookup.
    """
    ix = _index()
    pt, how, key = _project(np.array([Point(lon, lat)]))[0], "census geocoder point", None
    # Same street line in another town would match too, so the city point must be near the geocode.
    # ponytail: 250 m guard, generous vs. the <40 m geocoder offsets seen on test addresses.
    for k in map(street_key, streets):
        i = ix.addr_by_street.get(k)
        if i is not None and shapely.distance(ix.addr_utm[i], pt) <= CITY_POINT_MAX_M:
            pt, how, key = ix.addr_utm[i], f"city mailing-address point for {k!r}", k
            break

    near = ix.tree.query(pt, predicate="dwithin", distance=NEAREST_MAX_M)
    if len(near) == 0:
        keys = {street_key(s) for s in streets}
        nearby = ix.tree.query(pt, predicate="dwithin", distance=ADDRESS_SEARCH_MAX_M)
        near = [i for i in nearby if keys.intersection(street_key(a) for a in _addresses_in(ix, i))]
        if not near:
            raise LookupError(f"No Ann Arbor building footprint within {NEAREST_MAX_M:.0f} m of this address; "
                              f"no matching-address footprint within {ADDRESS_SEARCH_MAX_M:.0f} m")
        how += ", expanded search limited to footprints holding the same street line"
    cands = [(shapely.distance(ix.utm[i], pt), not _addresses_in(ix, i), i) for i in near]
    inside = [c for c in cands if c[0] == 0]
    # Containing footprint wins; among several (or among nearest), one holding addresses wins, then distance.
    dist, _, i = min(inside or cands, key=lambda c: (c[1], c[0]))
    return Building(
        props=ix.props[i],
        geojson=mapping(ix.wgs[i]),
        area_m2=float(ix.utm[i].area),
        addresses=_addresses_in(ix, i),
        match=f"{how}, {'inside footprint' if dist == 0 else f'nearest footprint {dist:.1f} m away'}",
        distance_m=round(float(dist), 1),
        street=key,
        street_units=ix.units_by_street[key] if key else 0,
    )
