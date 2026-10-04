"""Score the city's residential footprints through P1's existing model server.

From /api: uv run python scripts/score_city.py [--workers 4]
The first call warms the model, then 200 concurrent calls measure throughput. Stop
if the projected full run exceeds 90 minutes. JSONL checkpoints are flushed after
every result; rerun to resume (failed calls retry). --fresh discards the checkpoint
when model/classification changes. The small CSV holds scores; /city also reads cached footprints and mailing addresses.

Sources: City BuildingFootprints + MailingAddress (app.geo), public city energy
benchmarking (BENCHMARK_SOURCE), Census 2020 TIGERweb block groups (BG_SOURCE).
The batch duplicates get_features' footprint-only assembly to avoid thousands of
address geocoder calls; keep it in sync when changing geo classification.
"""

import argparse
import csv
import json
import math
import random
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import httpx
import shapely
from shapely.geometry import shape

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.city import BENCHMARK_SOURCE, TABLE_PATH, score_rows
from app.estimate import MODEL_BASE_URL
from app.geo import DATA_DIR
from app.geo import features as geo
from app.geo.footprints import _addresses_in, _index, mailing_assignment, street_key

# ResStock 2024.2 MI in.sqft bounds / type medians, read from the baseline
# parquet by P2 lookup-fixes (2026-10-04); source: model/data_sources/resstock.py
# and https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F
# Mirror that branch until integration;
# unlike mailing TYPE, these checks reject accessory/nonresidential footprints.
SQFT_MIN = {geo.SFD: 298, geo.SFA: 273, geo.MF24: 322, geo.MF5: 322}
SQFT_MAX = {geo.SFD: 5587, geo.SFA: 7414, geo.MF24: 6348, geo.MF5: 6348}
TYPICAL_SQFT = {geo.SFD: 1698, geo.SFA: 1207, geo.MF24: 854, geo.MF5: 854}

BG_SOURCE = "https://tigerweb.geo.census.gov/arcgis/rest/services/Census2020/tigerWMS_Census2020/MapServer/8"
FIELDS = ("footprint_id", "type", "block_group", "sqft", "annual_usd", "cost_per_sqft", "score", "grade",
          "excess_usd_per_sqft", "heating_usd", "benchmark_id", "benchmark_name")


def fetch_layer(url: str, path: Path, fields: str, where: str = "1=1") -> list[dict]:
    if path.exists():
        return json.loads(path.read_text())["features"]
    rows = []
    with httpx.Client(timeout=120) as client:
        while True:
            response = client.get(url + "/query", params={"where": where, "outFields": fields,
                "outSR": 4326, "f": "geojson", "resultOffset": len(rows), "resultRecordCount": 1000,
                "orderByFields": "OBJECTID", "returnGeometry": "true"})
            response.raise_for_status()
            data = response.json()
            if "features" not in data:
                raise ValueError(f"GIS query failed: {data.get('error', data)}")
            batch = data["features"]
            rows.extend(batch)
            if len(batch) < 1000 and not data.get("exceededTransferLimit"):
                break
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"type": "FeatureCollection", "source": url, "features": rows}))
    return rows


def associated_units(ix, assignments=None) -> dict[int, int]:
    """Street UNIT counts use the same point assignment as /city's map labels."""
    if assignments is None:
        assignments = mailing_assignment(ix)
    result = {}
    for street, units in ix.units_by_street.items():
        i = int(assignments[ix.addr_by_street[street]])
        if i >= 0:
            result[i] = max(result.get(i, 0), units)
    return result


def footprint_inputs(ix, i: int, associated_street_units: int = 0, address_indices=None) -> dict | None:
    """P2-01 assembly plus the concurrent lookup-fixes residential/size guards."""
    p = ix.props[i]
    if p["Struc_Type"] in {"Office", "Public"} or str(p.get("PackedPin") or "").strip().lower() in {"garage", "carport", "canopy", "parking deck"}:
        return None
    if address_indices is None:
        address_indices = ix.addr_tree.query(ix.utm[i], predicate="contains")
        addresses = _addresses_in(ix, i)
    else:
        hits = {ix.addr_street[j] for j in address_indices if ix.addr_residential[j]}
        bases = {a.split(" UNIT ")[0] for a in hits if " UNIT " in a}
        addresses = sorted(hits - bases)
    # UNIT rows may be TYPE Vacant (Verve/721 S Forest, 625 Church, Hubbard).
    # P2-01 counts street UNIT rows of every TYPE; use the common spatial assignment.
    streets = [*addresses, *(ix.addr_street[j] for j in address_indices)]
    street_units = max((ix.units_by_street[street_key(a)] for a in streets), default=0)
    street_units = max(street_units, associated_street_units)
    units = max(len(addresses), street_units)
    if units == 0 and p["Struc_Type"] == "Residential":
        units = 1
    stories = int(p["STORIES"]) if p["STORIES"] else geo.stories_from_height(p["ABG_BLD_HG"])
    area = round(float(ix.utm[i].area) * geo.SQFT_PER_M2 * stories)
    row = geo.townhouse_row(p["Struc_Type"], addresses, street_units, stories)
    if row and round(area / len(addresses)) <= geo.SQFT_MAX[geo.SFD]:
        kind = geo.SFA
    else:
        kind = geo.building_type(p["Struc_Type"], units)
    if kind is None:
        return None
    sqft = round(area / units) if units >= 2 else area
    if p["Struc_Type"] == "Commercial" and not SQFT_MIN[kind] <= area / max(units, 1) <= SQFT_MAX[kind]:
        return None
    if not SQFT_MIN[kind] <= sqft <= SQFT_MAX[kind]:
        sqft = TYPICAL_SQFT[kind]
    if sqft <= 0:
        raise ValueError(f"Nonpositive unit area for footprint {p['OBJECTID']}")
    point = ix.wgs[i].representative_point()
    return {"footprint_id": int(p["OBJECTID"]), "type": kind, "sqft": sqft, "lat": point.y, "lon": point.x}


def candidates() -> list[dict]:
    ix = _index()
    groups = fetch_layer(BG_SOURCE, DATA_DIR / "city_block_groups.geojson", "GEOID", "STATE='26' AND COUNTY='161'")
    benchmarks = fetch_layer(BENCHMARK_SOURCE, DATA_DIR / "city_benchmarks.geojson",
                              "AnnArborBenchmarkingID,PropertyName")
    # Multiple public reporting years share a geometry and identifier; choose one
    # deterministically, and never take names from unrestricted footprint metadata.
    unique = {}
    for feature in benchmarks:
        props = feature["properties"]
        bid = str(props.get("AnnArborBenchmarkingID") or "")
        if bid and props.get("PropertyName") and feature.get("geometry"):
            unique.setdefault(bid, feature)
    benchmarks = list(unique.values())
    group_tree = shapely.STRtree([shape(f["geometry"]) for f in groups])
    bench_tree = shapely.STRtree([shape(f["geometry"]) for f in benchmarks])
    rows = []
    assignments = mailing_assignment(ix)
    unit_counts = associated_units(ix, assignments)
    address_groups = {}
    for j, i in enumerate(assignments):
        if i >= 0:
            address_groups.setdefault(int(i), []).append(j)
    for i in range(len(ix.props)):
        row = footprint_inputs(ix, i, unit_counts.get(i, 0), address_groups.get(i, []))
        if row is None:
            continue
        point = ix.wgs[i].representative_point()
        hits = group_tree.query(point, predicate="intersects")
        if not len(hits):
            raise ValueError(f"No Census block group for footprint {row['footprint_id']}")
        row["block_group"] = sorted(groups[j]["properties"]["GEOID"] for j in hits)[0]
        hits = bench_tree.query(point, predicate="intersects")
        row.update(benchmark_id="", benchmark_name="")
        if len(hits):
            public = min((benchmarks[j]["properties"] for j in hits), key=lambda p: str(p["AnnArborBenchmarkingID"]))
            row.update(benchmark_id=str(public["AnnArborBenchmarkingID"]), benchmark_name=public["PropertyName"])
        rows.append(row)
    print(f"{len(ix.props):,} cached footprints; {len(rows):,} residential candidates: {dict(Counter(r['type'] for r in rows))}", flush=True)
    return rows


def score_one(client: httpx.Client, row: dict, model_url: str) -> dict:
    response = client.get(model_url.rstrip("/") + "/hc/estimate", params={
        "lat": row["lat"], "lon": row["lon"], "unit_sqft": row["sqft"],
        "building_type": row["type"], "block_group": row["block_group"]})
    response.raise_for_status()
    hc = response.json()
    # annual.total_usd is P1's rounded sum of unrounded heating and cooling,
    # exactly the p50 that app.estimate returns (the rounded parts can differ $1).
    annual, heating = float(hc["annual"]["total_usd"]), float(hc["annual"]["heating_usd"])
    if not math.isfinite(annual) or annual < 0 or not math.isfinite(heating) or heating < 0:
        raise ValueError("Model returned invalid annual costs")
    return {**row, "annual_usd": annual, "heating_usd": heating}


def read_checkpoint(path: Path) -> dict[int, dict]:
    rows = {}
    if path.exists():
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                # Only an interrupted final write is recoverable; earlier damage is not.
                if i != len(lines) - 1:
                    raise
                path.write_text("\n".join(lines[:i]) + ("\n" if i else ""))
                break
            rows[int(row["footprint_id"])] = row
    return rows


def write_table(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(score_rows(rows), key=lambda row: row["footprint_id"]))
    temporary.replace(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model-url", default=MODEL_BASE_URL)
    parser.add_argument("--output", type=Path, default=TABLE_PATH)
    parser.add_argument("--checkpoint", type=Path, default=DATA_DIR / "city_score_checkpoint.jsonl")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--benchmark-only", action="store_true")
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error("--workers must be positive")
    started = time.monotonic()
    inputs = candidates()
    if args.fresh:
        args.checkpoint.unlink(missing_ok=True)
    done = read_checkpoint(args.checkpoint)
    # Removed/reclassified footprints and changed inputs must never reuse stale costs.
    valid = {row["footprint_id"]: row for row in inputs}
    done = {fid: row for fid, row in done.items() if fid in valid and
            all(row.get(k) == v for k, v in valid[fid].items())}
    reused = len(done)
    pending = [row for row in inputs if row["footprint_id"] not in done]
    random.Random(2026).shuffle(pending)  # benchmark covers the city, not one spatially clustered ID range.
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    print(f"Resume: {len(done):,} completed, {len(pending):,} pending; {args.workers} workers", flush=True)
    with httpx.Client(timeout=180, limits=httpx.Limits(max_connections=args.workers)) as client, args.checkpoint.open("a") as checkpoint:
        def save(row):
            done[row["footprint_id"]] = row
            checkpoint.write(json.dumps(row, separators=(",", ":")) + "\n")
            checkpoint.flush()

        def batch(rows):
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(score_one, client, row, args.model_url): row for row in rows}
                for future in as_completed(futures):
                    row = futures[future]
                    try:
                        save(future.result())
                    except (httpx.HTTPError, ValueError, KeyError) as exc:
                        failures.append({"footprint_id": row["footprint_id"], "error": str(exc)[:300]})
                        print(f"Failed {row['footprint_id']}: {type(exc).__name__}", flush=True)
                    if len(done) % 500 == 0:
                        print(f"{len(done):,}/{len(inputs):,} scored; {(time.monotonic()-started)/60:.1f} min", flush=True)

        if pending:
            # Warm resource loading once so concurrent requests do not duplicate the
            # model's lru_cache initialization or cold file/network reads.
            print("Warming model with one footprint...", flush=True)
            save(score_one(client, pending.pop(), args.model_url))
        benchmark = pending[:200]
        pending = pending[200:]
        benchmark_start = time.monotonic()
        batch(benchmark)
        elapsed = time.monotonic() - benchmark_start
        projected_minutes = elapsed / len(benchmark) * len(inputs) / 60 if benchmark else 0
        print(f"Benchmark: {len(benchmark)} calls in {elapsed:.1f}s; projected full run {projected_minutes:.1f} min", flush=True)
        stopped = projected_minutes > 90 or args.benchmark_only
        if stopped:
            print("Stopped after benchmark. Faster proposal: cache predictions by weather cell × type × size × "
                  "vintage/fuel/envelope bucket, preserve metered-property predictions, then scale area. "
                  "This is approximate and needs validation; it is not silently enabled.", flush=True)
        else:
            batch(pending)
    write_table(list(done.values()), args.output)
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "scored": len(done), "candidates": len(inputs), "seconds": round(time.monotonic() - started, 2),
              "benchmark_calls": len(benchmark), "benchmark_seconds": round(elapsed, 2),
              "complete": len(done) == len(inputs), "reused": reused, "scored_this_run": len(done) - reused,
              "stopped_after_benchmark": stopped,
              "projected_minutes": round(projected_minutes, 2), "failures": failures,
              "sources": {"benchmark": BENCHMARK_SOURCE, "block_groups": BG_SOURCE},
              "mailing_assignment": "P3 HOUSE_SCHEMA section 3: inside, else nearest within 1.1e-4 WGS84 degrees; all mailing TYPEs; same as /city labels",
              "percentile": "midpoint empirical: 100 * (less + 0.5 * equal) / N, within building type",
              "notes": "Predicted heating + cooling only; P2-01 plus lookup-fixes residential/size guards; census tracts proxy neighborhoods."}
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    return 2 if projected_minutes > 90 else (1 if failures else 0)


if __name__ == "__main__":
    raise SystemExit(main())
