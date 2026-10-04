"""Build the map widget's mock data from real pipeline outputs (P1's /model), for one demo address.

Every number in the fixture comes from data or P1's model; nothing is typed in by hand. When P2 serves the same
shape from /api, the widget switches from this file to the endpoint (see components/hidden-rent-map/data.ts).

Run from a built P1 heating-cooling checkout (model artifacts present) with P1's environment. Missing caches
(city footprints, mailing addresses) are downloaded on first run; the block-group outline is fetched from Census
TIGERweb each run. Sources, caches and the footprint↔address pairing are written up in web/HOUSE_SCHEMA.md.

    cd ../mhacks-heating-cooling && PYTHONPATH=. .venv/bin/python ../mhacks-map-widget/web/scripts/build_map_fixture.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import STRtree
from shapely.geometry import Point, mapping, shape
from shapely.ops import transform

from model.data_sources import footprints as fp_source
from model.data_sources.arcgis import fetch_all
from model.heating_cooling import service as hc
from model.heating_cooling.building_model import TAU_C, TAU_H_ELEC, TAU_H_GAS
from model.heating_cooling.resstock_model import MULTIFAMILY
from model.paths import PROCESSED

ADDRESS = "912 Mary St, Ann Arbor, MI"
SIMPLIFY_DEG = 4e-6  # ~0.4 m; keeps the citywide layer small without visibly changing footprints
ADDR_SNAP_DEG = 1.1e-4  # ~12 m
CLOUD_SAMPLE = 400
OUT = Path(__file__).resolve().parents[1] / "mocks" / "map" / "912-mary-st.json"
WEB = Path(__file__).resolve().parents[1]
CITY_OUT = WEB / "public" / "data" / "a2-buildings.geojson"
ADDR_CACHE = WEB / "scripts" / ".cache" / "a2_mailing_addresses.json"
ADDRESSES_URL = "https://a2maps.a2gov.org/a2arcgis/rest/services/MailingAddress/FeatureServer/0"
TIGERWEB_BG = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2023/MapServer/10/query"

FOOTPRINTS_SRC = ("City of Ann Arbor building footprints (ABG_BLD_HG: above-ground height from aerial LiDAR; STORIES)",
                  "https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0")
BG_SRC = ("US Census block groups (TIGERweb ACS 2023 outline; ACS 5-year year built and heating fuel)",
          "https://tigerweb.geo.census.gov/")
RESSTOCK_SRC = ("NREL ResStock 2024.2, Michigan baseline (18,756 simulated homes)",
                "https://resstock.nrel.gov/")

# The survey, in the order the widget plays it. Each answer is passed to P1's model and filters the look-alikes.
STEPS = [
    {"id": "heating_fuel", "question": "How is the unit heated?", "answer_label": "Natural gas furnace or boiler",
     "model_kwargs": {"heating_fuel": "gas"}, "filter": ("heating_fuel", "Natural Gas")},
    {"id": "window_panes", "question": "Are the windows single- or double-pane?", "answer_label": "Double-pane",
     "model_kwargs": {"answers": {"window_panes": 2}}, "filter": ("window_panes", 2.0)},
    {"id": "floor_level", "question": "Which floor is the unit on?", "answer_label": "Top floor",
     "model_kwargs": {"answers": {"floor_level": 2}}, "filter": ("floor_level", 2.0)},
]


def to_m(geom):
    """Local equirectangular metres around Ann Arbor (<0.5% area error across the city)."""
    kx = 111_320 * np.cos(np.radians(42.28))
    return transform(lambda x, y, z=None: (x * kx, y * 110_574), geom)


def footprints():
    """City footprints via P1's cached ArcGIS pager (downloads to model/data/raw/arcgis/ on first run)."""
    return fetch_all(fp_source.URL, "a2_footprints", out_fields=fp_source.FIELDS, page=2000)


def mailing_addresses():
    """City of Ann Arbor mailing-address points (65k), paged from the public FeatureServer and cached locally."""
    if ADDR_CACHE.exists():
        return json.loads(ADDR_CACHE.read_text())
    out, offset = [], 0
    while True:
        q = urllib.parse.urlencode({"where": "1=1", "outFields": "PROPSTREET,TYPE", "outSR": 4326, "f": "geojson",
                                    "orderByFields": "OBJECTID", "resultOffset": offset, "resultRecordCount": 1000})
        req = urllib.request.Request(f"{ADDRESSES_URL}/query?{q}", headers={"User-Agent": "Mozilla/5.0 hidden-rent"})
        with urllib.request.urlopen(req, timeout=60) as r:
            feats = json.load(r)["features"]
        out += [{"street": f["properties"]["PROPSTREET"], "type": f["properties"]["TYPE"],
                 "xy": f["geometry"]["coordinates"]} for f in feats if f.get("geometry")]
        if len(feats) < 1000:
            break
        offset += 1000
    ADDR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    ADDR_CACHE.write_text(json.dumps(out))
    return out


def street_line(s: str) -> str:
    """'912 MARY ST UNIT 2' -> '912 Mary St'."""
    base = re.split(r"\s+(?:UNIT|APT|STE|#)\s*", s.strip(), maxsplit=1)[0]
    return " ".join(w if w[:1].isdigit() else w.capitalize() for w in base.split())


def city_buildings(lat, lon):
    """Every Ann Arbor footprint with its LiDAR height and the mailing addresses that fall inside it."""
    feats = [f for f in footprints() if f.get("geometry")]
    geoms = [shape(f["geometry"]) for f in feats]
    tree = STRtree(geoms)
    lines: list[Counter] = [Counter() for _ in feats]
    for a in mailing_addresses():
        p = Point(a["xy"])
        hit = tree.query(p, predicate="within")
        if not len(hit):  # some address points sit a few metres off the roof (P2-01 saw 5–11 m)
            hit = tree.query_nearest(p, max_distance=ADDR_SNAP_DEG)
        if len(hit):
            lines[hit[0]][street_line(a["street"])] += 1

    pt = Point(lon, lat)
    inside = tree.query(pt, predicate="within")
    mine = int(inside[0]) if len(inside) else int(tree.nearest(pt))

    x0, y0, x1, y1 = (np.array([g.bounds for g in geoms]).min(0)[:2].tolist()
                      + np.array([g.bounds for g in geoms]).max(0)[2:].tolist())
    rows, layer = [], []
    for i, (f, g) in enumerate(zip(feats, geoms)):
        p = f["properties"]
        addr = lines[i].most_common(1)[0][0] if lines[i] else None
        row = {"id": int(p["OBJECTID"]), "address": addr, "units": int(sum(lines[i].values())),
               "height_ft": round(p["ABG_BLD_HG"], 1) if p.get("ABG_BLD_HG") else None,
               "stories": p.get("STORIES"), "residential": p.get("Struc_Type") == "Residential",
               "footprint_sqft": round(to_m(g).area * 10.7639), "center": [round(c, 6) for c in g.centroid.coords[0]]}
        rows.append(row)
        props = {"id": row["id"], "h": row["height_ft"] or 0, "r": int(row["residential"])}
        if addr:
            props["a"] = addr
        layer.append({"type": "Feature", "geometry": round_geom(g.simplify(SIMPLIFY_DEG, preserve_topology=True)),
                      "properties": props})
    CITY_OUT.parent.mkdir(parents=True, exist_ok=True)
    CITY_OUT.write_text(json.dumps({"type": "FeatureCollection", "features": layer}, separators=(",", ":")))
    print(f"wrote {CITY_OUT} ({CITY_OUT.stat().st_size // 1_000_000} MB, {len(layer)} buildings, "
          f"{sum(1 for r in rows if r['address'])} with an address)", file=sys.stderr)
    return rows, rows[mine], geoms[mine], [round(v, 5) for v in (x0, y0, x1, y1)]


def round_geom(g):
    m = mapping(g)
    def r(c):
        return [r(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 6), round(c[1], 6)]
    return {"type": m["type"], "coordinates": r(m["coordinates"])}


def test_similar(rows, me, n=10, seed=0):
    """Stand-in for a future ranking: residential buildings with an address, the same number of floors and a
    footprint within ±25% of the selected one. A seeded random sample, so it's reproducible; not a ranking."""
    pool = [r for r in rows if r["residential"] and r["address"] and r["id"] != me["id"]
            and r["stories"] == me["stories"] and r["height_ft"]
            and abs(r["footprint_sqft"] / me["footprint_sqft"] - 1) <= 0.25]
    rng = np.random.default_rng(seed)
    pick = [pool[i] for i in sorted(rng.choice(len(pool), size=min(n, len(pool)), replace=False))]
    rule = (f"test sample: {n} of {len(pool):,} residential buildings with {me['stories']:g} floors and a footprint "
            f"within ±25% of this one ({me['footprint_sqft']:,} sq ft); random, not ranked")
    keep = ("id", "address", "center", "height_ft", "stories", "footprint_sqft")
    return {"rule": rule, "items": [{k: r[k] for k in keep} for r in pick]}


def block_group(geoid):
    q = urllib.parse.urlencode({"where": f"GEOID='{geoid}'", "outFields": "GEOID", "outSR": 4326, "f": "geojson"})
    with urllib.request.urlopen(f"{TIGERWEB_BG}?{q}", timeout=30) as r:
        feats = json.load(r)["features"]
    if not feats:
        raise SystemExit(f"block group {geoid} not found in TIGERweb")
    return feats[0]["geometry"]


def lookalike_pool(building, unit_sqft):
    """Rented simulated homes of the same type, era and size as this unit."""
    d = pd.read_parquet(PROCESSED / "resstock_frame.parquet")
    yb = building["year_built"]
    lo_yr, hi_yr = (yb // 10) * 10 - 10, (yb // 10) * 10 + 19   # its decade ± one decade
    lo_ft, hi_ft = round(unit_sqft * 0.65), round(unit_sqft * 1.5)
    pool = d[(d.btype == building["building_type"]) & (d.renter == 1)
             & d.year_built.between(lo_yr, hi_yr) & d.sqft.between(lo_ft, hi_ft)
             & d.heating_fuel.isin(["Natural Gas", "Electricity"])]
    kind = {"Single-Family Detached": "rented houses", "Single-Family Attached": "rented townhouses",
            "Multi-Family with 2 - 4 Units": "rented units in 2–4-unit buildings",
            "Multi-Family with 5+ Units": "rented apartments in 5+ unit buildings",
            "Mobile Home": "rented mobile homes"}[building["building_type"]]
    rule = (f"{kind}, built {int(lo_yr)}–{int(hi_yr)}, {lo_ft:,}–{hi_ft:,} sq ft, "
            f"heated with gas or electricity")
    return pool, rule


def price_cloud(pool, lat, lon, unit_sqft, btype):
    """Each look-alike's heating + cooling $/yr if it sat here: its simulated intensity × local typical-year
    degree-days × this unit's size × monthly EIA prices. Same equation and calibration as P1's estimate_hc."""
    w = hc._weather(lat, lon, "normal")
    cal = hc._res()["resstock"]["calibration"]
    mf = btype in MULTIFAMILY
    k = unit_sqft / 1000
    gas_w = float(sum(w[f"hdd{TAU_H_GAS}"] * w.month.map(lambda m: hc._price(m, "gas"))))
    eh_w = float(sum(w[f"hdd{TAU_H_ELEC}"] * w.month.map(lambda m: hc._price(m, "electric"))))
    c_w = float(sum(w[f"cdd{TAU_C}"] * w.month.map(lambda m: hc._price(m, "electric"))))
    gas = pool.heating_fuel == "Natural Gas"
    heat = np.where(gas, pool.heat_gas_per_hdd.astype(float) * (cal["heat_gas"] if mf else 1.0) * gas_w,
                    pool.heat_elec_per_hdd.astype(float) * cal["heat_elec"] * eh_w)
    cool = pool.cool_per_cdd.astype(float) * (cal["cool"] if mf else 1.0) * c_w
    return (heat + cool) * k


def summarize_cloud(usd):
    usd = np.sort(np.asarray(usd, dtype=float))
    idx = np.unique(np.linspace(0, len(usd) - 1, min(CLOUD_SAMPLE, len(usd))).round().astype(int))
    return {"count": int(len(usd)), "usd_yr": [round(float(v)) for v in usd[idx]],
            "p10": round(float(np.percentile(usd, 10))), "p50": round(float(np.percentile(usd, 50))),
            "p90": round(float(np.percentile(usd, 90)))}


def estimate_summary(r):
    err = r["accuracy"]["seasonal_gas_median_abs_error"]["all"]
    return {"annual_usd": round(r["annual"]["total_usd"]),
            "seasons": {s["season"]: round(s["total_usd"]) for s in r["seasons"]},
            "heating_fuel": r["model_detail"]["heating_fuel"],
            "typical_error": err, "method": r["method"]}


def main():
    base = hc.estimate_hc(address=ADDRESS)
    loc, b = base["location"], base["building"]
    lat, lon, unit_sqft = loc["lat"], loc["lon"], base["unit_sqft"]

    rows, me, geom, city_bounds = city_buildings(lat, lon)
    from_lidar = me["stories"] is None
    bg_geom = block_group(loc["block_group"])

    pool, rule = lookalike_pool(b, unit_sqft)
    steps = [{"id": "public_record", "question": None, "answer_label": None,
              "estimate": estimate_summary(base),
              "lookalikes": summarize_cloud(price_cloud(pool, lat, lon, unit_sqft, b["building_type"]))}]
    kwargs: dict = {"answers": {}}
    for st in STEPS:
        mk = st["model_kwargs"]
        kwargs = {**kwargs, **{k: v for k, v in mk.items() if k != "answers"},
                  "answers": {**kwargs["answers"], **mk.get("answers", {})}}
        r = hc.estimate_hc(lat=lat, lon=lon, building_type=b["building_type"], **kwargs)
        col, val = st["filter"]
        pool = pool[pool[col] == val]
        steps.append({"id": st["id"], "question": st["question"], "answer_label": st["answer_label"],
                      "estimate": estimate_summary(r),
                      "lookalikes": summarize_cloud(price_cloud(pool, lat, lon, unit_sqft, b["building_type"]))})

    out = {
        "_mock": "Built by web/scripts/build_map_fixture.py from P1's model and cached public data; "
                 "stands in for the /api map-widget payload until P2 serves it.",
        "address": loc["matched_address"],
        "center": [lon, lat],
        "city_bounds": city_bounds,
        "buildings_url": "/data/a2-buildings.geojson",
        "building": {
            "id": me["id"],
            "footprint": mapping(geom),
            "height_ft": me["height_ft"],
            "height_source": FOOTPRINTS_SRC[0],
            "stories": b["stories"],
            "stories_source": ("LiDAR height ÷ typical floor height (no recorded STORIES)" if from_lidar
                               else "city footprint record (STORIES)"),
            "footprint_sqft": me["footprint_sqft"],
            "floor_area_sqft": round(b["gfa_ft2"]),
            "floor_area_source": b["gfa_source"],
            "unit_sqft": round(unit_sqft),
            "unit_sqft_source": base["unit_sqft_source"],
            "building_type": b["building_type"],
            "building_type_source": b["building_type_source"],
        },
        "similar": test_similar(rows, me),
        "block_group": {
            "geoid": loc["block_group"],
            "geometry": bg_geom,
            "median_year_built": b["year_built"],
            "median_year_built_source": b["year_built_source"],
            "gas_heat_share": b["heating_fuel_shares"]["gas_share"],
            "electric_heat_share": b["heating_fuel_shares"]["electric_share"],
            "heating_fuel_source": b["heating_fuel_source"],
        },
        "lookalikes": {"pool_size": 18756, "rule": rule},
        "steps": steps,
        "accuracy_basis": base["accuracy"]["basis"],
        "sources": [
            {"label": FOOTPRINTS_SRC[0], "url": FOOTPRINTS_SRC[1]},
            {"label": "City of Ann Arbor mailing addresses (matched to the footprint they fall inside)",
             "url": ADDRESSES_URL},
            {"label": BG_SRC[0], "url": BG_SRC[1]},
            {"label": RESSTOCK_SRC[0], "url": RESSTOCK_SRC[1]},
            {"label": base["weather_source"], "url": "https://prism.oregonstate.edu/"},
            {"label": "EIA Michigan residential gas and electricity prices", "url": "https://www.eia.gov/"},
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)", file=sys.stderr)
    for s in steps:
        print(s["id"], s["estimate"]["annual_usd"], s["lookalikes"]["count"], s["lookalikes"]["p10"],
              s["lookalikes"]["p50"], s["lookalikes"]["p90"], file=sys.stderr)


if __name__ == "__main__":
    main()
