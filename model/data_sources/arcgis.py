"""Paginated ArcGIS FeatureServer query → list of GeoJSON features (WGS84), cached on disk."""
import json

import requests

from model.data_sources.http import UA
from model.paths import RAW


def fetch_all(layer_url: str, name: str, where: str = "1=1", out_fields: str = "*",
              page: int = 1000, geometry: bool = True, refresh: bool = False) -> list[dict]:
    path = RAW / "arcgis" / f"{name}.geojson"
    if path.exists() and not refresh:
        return json.loads(path.read_text())["features"]
    feats, offset = [], 0
    while True:
        r = requests.get(f"{layer_url}/query", headers=UA, timeout=180, params={
            "where": where, "outFields": out_fields, "returnGeometry": str(geometry).lower(),
            "outSR": 4326, "f": "geojson", "resultOffset": offset, "resultRecordCount": page,
            "orderByFields": "OBJECTID"})
        r.raise_for_status()
        batch = r.json().get("features", [])
        feats += batch
        if len(batch) < page:
            break
        offset += page
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    return feats
