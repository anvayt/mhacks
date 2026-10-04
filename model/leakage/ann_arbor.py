"""Ann Arbor house features for the leakage model, all from public data cached on disk (no per-house API calls).

- Building footprints (City of Ann Arbor): footprint area; stories = recorded STORIES where present (≈14% of houses),
  else from LiDAR roof height using thresholds calibrated on the houses that do have STORIES (midpoints between the
  median roof height of 1-, 2- and 3-story houses). Footprints include attached garages and porches, so floor area
  (footprint × stories) is biased high; see results/leakage_validation.json → ann_arbor.
- Mailing addresses (City of Ann Arbor, 65k points): number of addresses inside a footprint = number of units
  → home type (1 = detached, 2–4 = attached/2–4 unit, 5+ = apartment building: outside the training data).
- Census block groups (TIGERweb, Washtenaw County) + ACS 5-yr B25037: median year built of renter-occupied homes in the
  block group. Per-house year built is not public in Washtenaw County, so this is the best available proxy.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from shapely import STRtree
from shapely.geometry import Point, shape

from model.data_sources import census
from model.data_sources.arcgis import fetch_all
from model.data_sources.footprints import load as load_footprints

BG_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2023/MapServer/10"
ADDR_URL = "https://a2maps.a2gov.org/a2arcgis/rest/services/MailingAddress/FeatureServer/0"
ANN_ARBOR_CLIMATE_ZONE = 5  # IECC 5A (Washtenaw County)


@lru_cache(maxsize=1)
def _block_groups():
    feats = fetch_all(BG_URL, "washtenaw_block_groups", where="STATE='26' AND COUNTY='161'", out_fields="GEOID")
    geoms = [shape(f["geometry"]) for f in feats]
    return [f["properties"]["GEOID"] for f in feats], geoms, STRtree(geoms)


def block_group_of(lats, lons) -> np.ndarray:
    ids, geoms, tree = _block_groups()
    out = []
    for la, lo in zip(np.atleast_1d(lats), np.atleast_1d(lons)):
        hit = tree.query(Point(lo, la), predicate="intersects")
        out.append(ids[hit[0]] if len(hit) else None)
    return np.array(out, dtype=object)


def block_group_year_built(lats, lons) -> np.ndarray:
    return np.array([census.median_year_built(bg)[0] if bg else np.nan for bg in block_group_of(lats, lons)], dtype=float)


@lru_cache(maxsize=1)
def _addresses():
    feats = fetch_all(ADDR_URL, "a2_mailing_addresses", out_fields="OBJECTID,PROPSTREET,TYPE", page=1000)
    pts = [(f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][1], f["properties"].get("PROPSTREET"))
           for f in feats if f.get("geometry")]
    return pd.DataFrame(pts, columns=["lon", "lat", "street"])


def stories_from_height(fp: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Calibrate LiDAR height → stories on residential footprints with a recorded STORIES value (1–3)."""
    lab = fp[fp.stories.between(1, 3) & fp.height_ft.notna()]
    med = lab.groupby("stories").height_ft.median()
    cuts = [(med[1] + med[2]) / 2, (med[2] + med[3]) / 2]
    def rule(h):
        return np.where(h < cuts[0], 1.0, np.where(h < cuts[1], 2.0, 3.0))
    acc = float((rule(lab.height_ft.to_numpy()) == lab.stories.to_numpy()).mean())
    est = pd.Series(rule(fp.height_ft.fillna(med[2]).to_numpy()), index=fp.index)
    st = fp.stories.where(fp.stories.between(1, 6)).fillna(est)
    return st, {"labelled_houses": int(len(lab)), "median_height_by_stories": {int(k): float(v) for k, v in med.items()},
                "cuts_ft": [float(c) for c in cuts], "rule_accuracy_on_labelled": acc,
                "share_with_recorded_stories": float(fp.stories.between(1, 6).mean())}


def house_table() -> pd.DataFrame:
    """One row per residential footprint that has ≥ 1 mailing address (garages/sheds have none)."""
    fp = load_footprints()
    fp = fp[fp.struc_type == "Residential"].reset_index(drop=True)
    a = _addresses()
    tree = STRtree(list(fp.geometry))
    counts = np.zeros(len(fp), int)
    for lo, la in zip(a.lon.to_numpy(), a.lat.to_numpy()):
        hit = tree.query(Point(lo, la), predicate="intersects")
        if len(hit):
            counts[hit[0]] += 1
    fp["units"] = counts
    fp = fp[fp.units > 0].copy()
    fp["home_type"] = np.where(fp.units == 1, "detached", np.where(fp.units <= 4, "attached_or_2to4", "apartment_5plus"))
    fp["stories_est"], _ = stories_from_height(fp)
    fp["floor_area_ft2"] = fp.area_ft2 * fp.stories_est   # above-grade floor area estimate (footprint × stories)
    fp["year_built_bg"] = block_group_year_built(fp.lat.to_numpy(), fp.lon.to_numpy())
    fp["climate_zone"] = ANN_ARBOR_CLIMATE_ZONE
    return fp.drop(columns=["geometry"]).reset_index(drop=True)
