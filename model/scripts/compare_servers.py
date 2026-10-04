#!/usr/bin/env python3
"""Compare legacy numeric output of two model servers, sequentially and read-only.

Run only when the lead has started the isolated model/API. This script never
starts/stops servers or edits model artifacts. It POSTs only to the isolated API
to prepare five demo sessions; every request to either model is a GET. Additional
new-model fields are allowed. Existing numeric JSON tokens must match exactly
(including 1 versus 1.0); this is not a whole-response byte-equality assertion.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261004
ENDPOINTS = ("estimate", "bill_check", "weather")


class Number(str):
    """A JSON numeric token retaining its exact spelling, distinct from text."""


def parse_numbers(text: str):
    return json.loads(text, parse_int=Number, parse_float=Number, parse_constant=Number)


def numeric_leaves(value, path=()):
    if isinstance(value, Number):
        yield path, str(value)
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from numeric_leaves(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from numeric_leaves(child, (*path, index))


def pointer(path):
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in path)


def compare_numeric(old, new):
    """All old numeric leaves must exist at the same path with identical tokens."""
    diffs = []
    for path, token in numeric_leaves(old):
        current = new
        try:
            for part in path:
                # A list index must not accidentally resolve a dictionary key, or vice versa.
                if isinstance(part, int):
                    if not isinstance(current, list):
                        raise TypeError
                elif not isinstance(current, dict):
                    raise TypeError
                current = current[part]
        except (KeyError, IndexError, TypeError):
            diffs.append({"path": pointer(path), "old": token, "reason": "missing_numeric_leaf"})
            continue
        if not isinstance(current, Number) or str(current) != token:
            diffs.append({"path": pointer(path), "old": token,
                          "new": str(current) if isinstance(current, Number) else current,
                          "reason": "numeric_token_changed" if isinstance(current, Number) else "numeric_type_changed"})
    return diffs


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(base, path, *, params=None, payload=None, timeout=180):
    """No credentials or response headers enter this report."""
    url = base.rstrip("/") + path
    if params:
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(url, data=data, headers={"Content-Type": "application/json"} if data else {},
                      method="POST" if data else "GET")
    start = time.monotonic()
    status, text, error = None, "", None
    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            text = response.read().decode("utf-8")
    except HTTPError as exc:
        status = exc.code
        text = exc.read().decode("utf-8", errors="replace")
        error = f"HTTP {status}"
    except (URLError, TimeoutError, OSError) as exc:
        error = type(exc).__name__ + ": " + str(exc)
    result = {"status": status, "elapsed_seconds": round(time.monotonic() - start, 3),
              "response_sha256": hashlib.sha256(text.encode()).hexdigest()}
    if error:
        result["error"] = error
    parsed = None
    if status == 200:
        try:
            parsed = parse_numbers(text)
            leaves = list(numeric_leaves(parsed))
            result["numeric_count"] = len(leaves)
            result["numeric_leaves"] = {pointer(p): token for p, token in leaves}
        except (ValueError, TypeError):
            result["error"] = "invalid_json"
    return result, parsed, text


def demo_case(address, api_url, timeout):
    case = {"kind": "demo", "id": address, "preparation": []}
    try:
        result, _, body = fetch(api_url, "/estimate", payload={"address": address}, timeout=timeout)
        case["preparation"].append({k: v for k, v in result.items() if k != "numeric_leaves"})
        if result["status"] != 200 or result.get("error"):
            raise ValueError("isolated API /estimate failed")
        session_id = json.loads(body)["session_id"]
        result, _, body = fetch(api_url, f"/session/{session_id}", timeout=timeout)
        case["preparation"].append({k: v for k, v in result.items() if k != "numeric_leaves"})
        if result["status"] != 200 or result.get("error"):
            raise ValueError("isolated API /session failed")
        params = json.loads(body)["model_params"]
        required = ("lat", "lon", "unit_sqft", "building_type", "block_group")
        case["params"] = {k: params[k] for k in required}
        case["parameter_source"] = "isolated API /estimate then /session: exact saved model_params"
    except (KeyError, ValueError, TypeError) as exc:
        case["preparation_error"] = str(exc)
    return case


def footprint_cases(table, footprints):
    """Fixed-seed sample is chosen before any geometry lookup; failures remain cases."""
    with table.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) < 20:
        raise ValueError("city score table has fewer than 20 rows")
    selected = random.Random(SEED).sample(rows, 20)
    shapes, geometry_error = {}, None
    try:
        from shapely.geometry import shape
        document = json.loads(footprints.read_text())
        wanted = {int(row["footprint_id"]) for row in selected}
        for feature in document["features"]:
            object_id = int(feature["properties"]["OBJECTID"])
            if object_id in wanted:
                shapes[object_id] = feature["geometry"]
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        geometry_error = type(exc).__name__ + ": " + str(exc)
    cases = []
    for row in selected:
        case = {"kind": "city_footprint", "id": row["footprint_id"],
                "parameter_source": "city_scores.csv + cached OBJECTID geometry representative_point"}
        try:
            if geometry_error:
                raise ValueError(geometry_error)
            point = shape(shapes[int(row["footprint_id"])]).representative_point()
            if point.is_empty:
                raise ValueError("empty footprint geometry")
            case["params"] = {"lat": point.y, "lon": point.x, "unit_sqft": float(row["sqft"]),
                              "building_type": row["type"], "block_group": row["block_group"]}
        except (ValueError, KeyError, TypeError) as exc:
            case["preparation_error"] = str(exc)
        cases.append(case)
    return cases


def endpoint_params(name, params):
    if name == "weather":
        return {"lat": params["lat"], "lon": params["lon"], "mode": "normal"}
    if name == "bill_check":
        # These are the legacy endpoint's accepted parameters. Deliberately omit
        # noise_basis: its original cross-building error must remain unchanged.
        return {k: params[k] for k in ("lat", "lon", "unit_sqft")} | {"year": 2026, "month": 2, "gas_ccf": 100}
    return params | {"mode": "normal"}


def run_case(case, args):
    results = []
    for endpoint in ENDPOINTS:
        if "preparation_error" in case:
            results.append({"endpoint": endpoint, "pass": False, "error": "case_preparation_failed"})
            continue
        params = endpoint_params(endpoint, case["params"])
        old_result, old, _ = fetch(args.old_model_url, f"/hc/{endpoint}", params=params, timeout=args.timeout)
        new_result, new, _ = fetch(args.new_model_url, f"/hc/{endpoint}", params=params, timeout=args.timeout)
        usable = (old_result["status"] == new_result["status"] == 200
                  and not old_result.get("error") and not new_result.get("error")
                  and old_result.get("numeric_count", 0) > 0)
        diffs = compare_numeric(old, new) if usable else []
        result = {"endpoint": endpoint, "params": params, "old": old_result, "new": new_result,
                  "pass": bool(usable and not diffs), "diffs": diffs}
        if not usable:
            result["error"] = "request_failed_invalid_json_or_no_old_numbers"
        results.append(result)
        print(f"{'PASS' if result['pass'] else 'FAIL'} {case['kind']} {case['id']} /hc/{endpoint} "
              f"old={old_result['status']} new={new_result['status']} diffs={len(diffs)}", flush=True)
    return {**case, "results": results}


def save(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-model-url", default="http://localhost:8001")
    parser.add_argument("--new-model-url", default="http://localhost:8011")
    parser.add_argument("--api-url", default="http://localhost:8061")
    parser.add_argument("--output", type=Path, default=ROOT / "model/results/finish/compatibility.json")
    parser.add_argument("--addresses", type=Path, default=ROOT / "demo/addresses.txt")
    parser.add_argument("--city-scores", type=Path, default=ROOT / "api/data/city_scores.csv")
    parser.add_argument("--footprints", type=Path, default=ROOT / "data/a2_footprints.geojson")
    parser.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()
    if args.new_model_url.rstrip("/") == args.old_model_url.rstrip("/"):
        parser.error("old and new model URLs must differ")
    if args.api_url.rstrip("/") == args.old_model_url.rstrip("/") or urlparse(args.api_url).port == 8001:
        parser.error("API preparation may not POST to the live model")
    addresses = [s.strip() for s in args.addresses.read_text().splitlines() if s.strip() and not s.startswith("#")]
    if len(addresses) != 5:
        parser.error("addresses file must contain exactly five demo addresses")
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "old_model_url": args.old_model_url,
              "new_model_url": args.new_model_url, "api_url": args.api_url, "random_seed": SEED,
              "comparison": "Exact JSON numeric token equality at every old numeric path; new fields allowed; "
                            "text and boolean fields not compared. Default legacy bill noise basis only.",
              "expected_cases": 25, "expected_endpoint_checks": 75, "pass": False, "cases": [],
              "input_sha256": {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha256(p)
                               for p in (args.addresses, args.city_scores, args.footprints) if p.exists()},
              "artifact_sha256": {p.name: sha256(p) for p in sorted((ROOT / "model/artifacts").glob("*.pkl"))}}
    save(args.output, report)
    try:
        random_cases = footprint_cases(args.city_scores, args.footprints)
        # Prepare and compare one demo at a time; no concurrent load on the live model.
        for address in addresses:
            report["cases"].append(run_case(demo_case(address, args.api_url, args.timeout), args))
            save(args.output, report)
        for case in random_cases:
            report["cases"].append(run_case(case, args))
            save(args.output, report)
    except Exception as exc:
        report["fatal_error"] = type(exc).__name__ + ": " + str(exc)
    all_results = [r for c in report["cases"] for r in c["results"]]
    report["successful_endpoint_checks"] = sum(r["pass"] for r in all_results)
    report["failed_endpoint_checks"] = len(all_results) - report["successful_endpoint_checks"]
    report["missing_endpoint_checks"] = 75 - len(all_results)
    report["pass"] = len(report["cases"]) == 25 and len(all_results) == 75 and all(r["pass"] for r in all_results)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    save(args.output, report)
    print(f"{'PASS' if report['pass'] else 'FAIL'}: {report['successful_endpoint_checks']}/75 endpoint checks; "
          f"report {args.output}", flush=True)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
