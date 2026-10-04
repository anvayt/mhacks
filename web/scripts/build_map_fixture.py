"""Build the map widget's mock data from real pipeline outputs (P1's /model), for one demo address.

Every number in the fixture comes from data or P1's model; nothing is typed in by hand. When P2 serves the same
shape from /api, the widget switches from this file to the endpoint (see components/hidden-rent-map/data.ts).

Run from a built P1 heating-cooling checkout (model artifacts present) with P1's environment. The block-group
outline is fetched once from Census TIGERweb (public, no key):

    cd ../mhacks-heating-cooling && PYTHONPATH=. .venv/bin/python ../mhacks-map-widget/web/scripts/build_map_fixture.py
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import Point, mapping, shape
from shapely.ops import transform

from model.heating_cooling import service as hc
from model.heating_cooling.building_model import TAU_C, TAU_H_ELEC, TAU_H_GAS
from model.heating_cooling.resstock_model import MULTIFAMILY
from model.paths import PROCESSED

ADDRESS = "912 Mary St, Ann Arbor, MI"
NEIGHBOR_RADIUS_M = 160
CLOUD_SAMPLE = 400
OUT = Path(__file__).resolve().parents[1] / "mocks" / "map" / "912-mary-st.json"
RAW = PROCESSED.parent / "raw" / "arcgis"
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


def load_geojson(name):
    return json.loads((RAW / name).read_text())["features"]


def building_and_neighbors(lat, lon):
    feats = load_geojson("a2_footprints.geojson")
    pt = Point(lon, lat)
    pt_m = to_m(pt)
    mine, neighbors = None, []
    city = [np.inf, np.inf, -np.inf, -np.inf]
    for f in feats:
        if not f.get("geometry"):
            continue
        g = shape(f["geometry"])
        x0, y0, x1, y1 = g.bounds
        city = [min(city[0], x0), min(city[1], y0), max(city[2], x1), max(city[3], y1)]
        if g.contains(pt):
            mine = (f, g)
        elif to_m(g.centroid).distance(pt_m) <= NEIGHBOR_RADIUS_M:
            neighbors.append((f, g))
    if mine is None:  # geocoded point can sit just off the roof: nearest footprint
        mine = min(neighbors, key=lambda fg: to_m(fg[1]).distance(pt_m))
        neighbors.remove(mine)
    nb = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": mapping(g),
         "properties": {"height_ft": round(f["properties"]["ABG_BLD_HG"] or 0, 1)}}
        for f, g in neighbors if f["properties"].get("ABG_BLD_HG")]}
    return mine, nb, [round(float(v), 5) for v in city]


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

    (fp, geom), neighbors, city_bounds = building_and_neighbors(lat, lon)
    props = fp["properties"]
    from_lidar = props.get("STORIES") is None
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
        "building": {
            "footprint": mapping(geom),
            "height_ft": round(props["ABG_BLD_HG"], 1) if props.get("ABG_BLD_HG") else None,
            "height_source": FOOTPRINTS_SRC[0],
            "stories": b["stories"],
            "stories_source": ("LiDAR height ÷ typical floor height (no recorded STORIES)" if from_lidar
                               else "city footprint record (STORIES)"),
            "footprint_sqft": round(to_m(geom).area * 10.7639),
            "floor_area_sqft": round(b["gfa_ft2"]),
            "floor_area_source": b["gfa_source"],
            "unit_sqft": round(unit_sqft),
            "unit_sqft_source": base["unit_sqft_source"],
            "building_type": b["building_type"],
            "building_type_source": b["building_type_source"],
        },
        "neighbors": neighbors,
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
