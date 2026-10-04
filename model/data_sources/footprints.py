"""City of Ann Arbor building footprints (35,007 polygons; height from LiDAR `ABG_BLD_HG` in ft, `STORIES`).

Source: https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0
"""
import numpy as np
import pandas as pd
from shapely import STRtree
from shapely.geometry import shape

from model.data_sources.arcgis import fetch_all

URL = "https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0"
FIELDS = "OBJECTID,ABG_BLD_HG,Struc_Type,Bldg_Name,PackedPin,STORIES,FacilityID,Shape__Area,Shape__Length"
FT_PER_STORY = 10.0  # typical floor-to-floor height used only when STORIES is missing


def load() -> pd.DataFrame:
    feats = fetch_all(URL, "a2_footprints", out_fields=FIELDS, page=2000)
    rows, geoms = [], []
    for f in feats:
        if not f.get("geometry"):
            continue
        g = shape(f["geometry"])
        p = f["properties"]
        c = g.representative_point()
        rows.append({"fp_id": p["OBJECTID"], "height_ft": p["ABG_BLD_HG"], "stories": p["STORIES"],
                     "struc_type": p["Struc_Type"], "bldg_name": p["Bldg_Name"], "pin": p["PackedPin"],
                     "area_ft2": p["Shape__Area"], "perim_ft": p["Shape__Length"], "lat": c.y, "lon": c.x})
        geoms.append(g)
    df = pd.DataFrame(rows)
    df["geometry"] = geoms
    st = df["stories"].where(df["stories"] > 0)
    df["stories_est"] = st.fillna((df["height_ft"] / FT_PER_STORY).round().clip(lower=1)).fillna(1)
    df["floor_area_est_ft2"] = df["area_ft2"] * df["stories_est"]
    return df


def envelope_features(fps: pd.DataFrame) -> dict:
    """Aggregate a set of footprints (one property) into physics-motivated features."""
    if fps.empty:
        return {"fp_count": 0}
    a = fps["area_ft2"].sum()
    h = np.nanmax([fps["height_ft"].max(), 10.0])
    wall = (fps["perim_ft"] * fps["height_ft"].fillna(fps["stories_est"] * FT_PER_STORY)).sum()
    vol = (fps["area_ft2"] * fps["height_ft"].fillna(fps["stories_est"] * FT_PER_STORY)).sum()
    return {"fp_count": int(len(fps)), "fp_area_ft2": float(a), "fp_floor_area_est_ft2": float(fps["floor_area_est_ft2"].sum()),
            "height_ft_max": float(h), "stories_max": float(fps["stories_est"].max()),
            "stories_mean": float(np.average(fps["stories_est"], weights=fps["area_ft2"])),
            # envelope (walls + roof) per unit volume: higher = leakier shape, more heat loss per ft³
            "surface_to_volume": float((wall + a) / vol) if vol > 0 else np.nan}


class FootprintIndex:
    def __init__(self, df: pd.DataFrame | None = None):
        self.df = load() if df is None else df
        self.tree = STRtree(list(self.df["geometry"]))

    def within(self, geom) -> pd.DataFrame:
        idx = self.tree.query(geom, predicate="intersects")
        sub = self.df.iloc[idx]
        # keep footprints mostly inside the polygon (property polygons can clip neighbours' edges)
        keep = [geom.intersection(g).area / g.area > 0.5 for g in sub["geometry"]] if len(sub) else []
        return sub[keep] if len(sub) else sub

    def at_point(self, lat: float, lon: float, radius_m: float = 60) -> pd.DataFrame:
        from shapely.geometry import Point
        pt = Point(lon, lat)
        idx = self.tree.query(pt, predicate="intersects")
        if len(idx):
            return self.df.iloc[idx]
        deg = radius_m / 111_000
        idx = self.tree.query(pt.buffer(deg))
        if not len(idx):
            return self.df.iloc[[]]
        sub = self.df.iloc[idx]
        d = sub["geometry"].apply(lambda g: g.distance(pt))
        return sub.loc[[d.idxmin()]]
