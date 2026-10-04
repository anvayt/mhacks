"""Download Ann Arbor building footprints (+ mailing-address points) once into /data/.

Sources (City of Ann Arbor ArcGIS REST, no key):
- Footprints: https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0
  (35,007 polygons on 2026-10-03; maxRecordCount 2000)
- Mailing addresses: https://a2maps.a2gov.org/a2arcgis/rest/services/MailingAddress/FeatureServer/0
  (65,138 points incl. "... UNIT 101" rows; maxRecordCount 1000). Used to count units per building,
  because Struc_Type only says Residential/Commercial/Office/Public. Owner fields are NOT downloaded.

Run from /api:  uv run python scripts/fetch_footprints.py
"""

import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.geo import ADDRESSES_PATH, FOOTPRINTS_PATH  # noqa: E402

A2 = "https://a2maps.a2gov.org/a2arcgis/rest/services"
LAYERS = [
    (f"{A2}/OSI/BuildingFootprints/FeatureServer/0",
     "OBJECTID,ABG_BLD_HG,Struc_Type,Bldg_Name,PackedPin,STORIES", 2000, FOOTPRINTS_PATH),
    (f"{A2}/MailingAddress/FeatureServer/0", "OBJECTID,PIN,PROPSTREET,TYPE", 1000, ADDRESSES_PATH),
]


def fetch_layer(url: str, fields: str, page: int, out: Path) -> None:
    """Page through an ArcGIS FeatureServer layer (resultOffset) and save one GeoJSON in WGS84."""
    features: list[dict] = []
    with httpx.Client(timeout=120) as client:
        while True:
            r = client.get(f"{url}/query", params={
                "where": "1=1", "outFields": fields, "outSR": 4326, "f": "geojson",
                "orderByFields": "OBJECTID", "resultOffset": len(features), "resultRecordCount": page,
            })
            r.raise_for_status()
            batch = r.json()["features"]
            features += batch
            print(f"{out.name}: {len(features)}", flush=True)
            if len(batch) < page:
                break
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"type": "FeatureCollection", "source": url, "features": features}))


if __name__ == "__main__":
    for layer in LAYERS:
        fetch_layer(*layer)
