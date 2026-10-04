"""Warm every cache a judge's own Ann Arbor address can hit, citywide (make demo-warm-city).

From /api: uv run python scripts/warm_city.py
Writes this checkout's git-ignored /data caches, which the API started from this checkout reads.
One request at a time, with a short pause after each network call:
- P1 model, per 0.1 deg weather cell holding a scored home (api/data/city_scores.csv): the same
  /hc/estimate (typical and mode=forecast) and /hc/weather?mode=forecast calls /estimate and /forecast
  make, for one home in the cell. Timed: a cold cell is the slow one.
- Open-Meteo per cell: the 1991-2020 daily history (/forecast's disk cache) and the last-good 7-day
  forecast (/forecast's offline fallback).
- TIGERweb outline for every block group /map can hit: the scored homes' block groups plus every
  block group intersecting the city's footprint bounds.
- ACS B25035 county table (one call, only if missing).
Not warmable: the Census geocoder (one call per never-seen address, cached after).
"""

import sys
import time
from pathlib import Path

import httpx
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import city, estimate, forecast, map_widget  # noqa: E402
from app.geo import DATA_DIR, census  # noqa: E402
from app.geo.footprints import _index  # noqa: E402

PAUSE = 0.3  # seconds after each network call: these are free public services


def step(label: str, cached: bool, fn) -> bool:
    t = time.monotonic()
    try:
        fn()
    except Exception as e:  # report and continue: one failed cell must not hide the rest
        print(f"FAIL {label} ({time.monotonic() - t:.2f}s): {getattr(e, 'detail', e)}", flush=True)
        return False
    print(f"{'CACHED' if cached else 'PASS'} {label} ({time.monotonic() - t:.2f}s)", flush=True)
    if not cached:
        time.sleep(PAUSE)
    return True


def main() -> int:
    started = time.monotonic()
    ix = _index()
    row_of = {int(p["OBJECTID"]): i for i, p in enumerate(ix.props)}
    cells: dict[tuple, dict] = {}
    for r in city._table():  # sorted by footprint_id: the first scored home stands for its cell
        pt = ix.wgs[row_of[r["footprint_id"]]].representative_point()  # the point /estimate sends P1
        cells.setdefault((forecast._grid(pt.y), forecast._grid(pt.x)), {
            "lat": pt.y, "lon": pt.x, "unit_sqft": round(r["sqft"]), "building_type": r["type"],
            "block_group": r["block_group"]})
    geoids = {r["block_group"] for r in city._table()}
    xmin, ymin, xmax, ymax = shapely.total_bounds(ix.wgs)
    try:
        r = httpx.get(map_widget.TIGERWEB_BG, timeout=60, params={
            "geometry": f"{xmin},{ymin},{xmax},{ymax}", "geometryType": "esriGeometryEnvelope", "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects", "outFields": "GEOID", "returnGeometry": "false", "f": "json"})
        r.raise_for_status()
        geoids |= {f["attributes"]["GEOID"] for f in r.json()["features"]}
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as e:
        print(f"WARN TIGERweb city-bounds list failed ({e!r}); warming the scored homes' block groups only", flush=True)
    print(f"{len(cells)} weather cells, {len(geoids)} block groups; caches in {DATA_DIR}", flush=True)

    acs = census.CACHE_PATH.exists()
    results = [step("ACS B25035 Washtenaw table", acs, census._table)]
    for n, ((lat, lon), p) in enumerate(sorted(cells.items()), 1):
        cell = f"[cell {n}/{len(cells)} {lat:.2f},{lon:.2f}]"
        history = DATA_DIR / f"openmeteo_daily_1991_2020_{lat:.2f}_{lon:.2f}.json"
        results += [
            step(f"{cell} model /hc/estimate typical", False, lambda: estimate._hc(p)),
            step(f"{cell} model /hc/estimate forecast", False, lambda: estimate._hc({**p, "mode": "forecast"})),
            step(f"{cell} model /hc/weather forecast", False, lambda: forecast._get(
                f"{estimate.MODEL_BASE_URL}/hc/weather", {"lat": p["lat"], "lon": p["lon"], "mode": "forecast"},
                "model_unavailable", estimate.MODEL_DOWN)),
            step(f"{cell} Open-Meteo 1991-2020 history", history.exists(), lambda: forecast._history(lat, lon)),
            step(f"{cell} Open-Meteo 7-day forecast (last-good fallback)", False,
                 lambda: forecast._daily_forecast(lat, lon)),
        ]
    fetched = 0
    for n, geoid in enumerate(sorted(geoids), 1):
        cached = (map_widget.BG_CACHE / f"{geoid}.geojson").exists()
        results.append(step(f"[block group {n}/{len(geoids)} {geoid}] TIGERweb outline", cached,
                            lambda: map_widget._block_group(geoid)))
        fetched += results[-1] and not cached
    failed = results.count(False)
    print(f"RESULT: {len(cells)} weather cells (model + history + forecast), {len(geoids)} block-group outlines "
          f"({fetched} fetched now), ACS {'cached' if acs else 'fetched'}; {len(results) - failed} ok, "
          f"{failed} failed, {time.monotonic() - started:.0f}s.", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
