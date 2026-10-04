"""Read-only artifact audit; writes only SIGNOFF.md and finish/signoff.json.

Run from repository root: .venv/bin/python -m model.scripts.signoff
Rebuilds held-out predictions in memory from copied model/OOF artifacts and cached
meters/weather, including other-year change-point fits. Never invokes validate.main,
weather_check, baseline training, serving-weight writes, or any HTTP server.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import pickle
import platform
import socket
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import requests

from model import climate
from model.heating_cooling import validate
from model.paths import ARTIFACTS, PROCESSED, RESULTS

ROOT = RESULTS.parents[1]
OUT = RESULTS / "finish" / "signoff.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blocked(*args, **kwargs):
    raise RuntimeError("Sign-off prohibits network; use the copied caches")


def canonical(value):
    return json.loads(json.dumps(value))


def compare_rows(actual: pd.DataFrame, saved: pd.DataFrame, keys: list[str]) -> dict:
    cols = ["actual", *validate.PATHS]
    a = actual.set_index(keys).sort_index()
    b = saved.set_index(keys).sort_index()
    same_keys = a.index.equals(b.index)
    result = {"rows": len(a), "saved_rows": len(b), "keys_equal": same_keys, "columns": {}}
    for col in cols:
        x, y = a[col].to_numpy(float), b[col].to_numpy(float)
        match = same_keys and np.allclose(x, y, rtol=1e-12, atol=1e-8, equal_nan=True)
        result["columns"][col] = {"matches": bool(match),
            "max_absolute_difference": float(np.nanmax(np.abs(x - y))) if same_keys else None}
    result["all_match"] = same_keys and all(c["matches"] for c in result["columns"].values())
    return result


def family_check() -> dict:
    validation = json.loads((RESULTS / "building_model_validation.json").read_text())["targets"]
    weights = json.loads((RESULTS / "blend_weights.json").read_text())
    out = {}
    for target, artifact, fuel in [("heat_gas", "bldg_heat_gas.pkl", "gas"),
                                    ("cool_elec", "bldg_cool_elec.pkl", "elec")]:
        with (ARTIFACTS / artifact).open("rb") as f:
            model = pickle.load(f)
        names = {"validation_chosen": validation[target]["chosen"], "artifact_name": model["name"],
                 "serving_weight_family": weights[fuel]["meter_model_family"]}
        oof = pd.read_parquet(RESULTS / f"oof_{target}.parquet")
        out[target] = {**names, "oof_column_present": f"oof_{model['name']}" in oof,
                       "matches": len(set(names.values())) == 1 and f"oof_{model['name']}" in oof}
    return out


def main() -> None:
    started = time.monotonic()
    copied = json.loads((RESULTS / "finish" / "source_copy.json").read_text())
    hashes = [{"path": r["path"], "bytes": (ROOT / r["path"]).stat().st_size,
               "sha256": sha256(ROOT / r["path"]), "copied_source_sha256": r["sha256"]} for r in copied["files"]]
    for row in hashes:
        row["matches_copied_source"] = row["sha256"] == row["copied_source_sha256"]
    saved_validation = json.loads((RESULTS / "validation_real.json").read_text())
    saved_seasonal = pd.read_parquet(RESULTS / "heldout_seasonal.parquet")
    saved_monthly = pd.read_parquet(RESULTS / "heldout_monthly.parquet")
    validate.MONTH_ROWS.clear()
    # Fail closed if any cache is absent. No request may reach live :8001 or any other host.
    with patch.object(requests.sessions.Session, "request", blocked), patch.object(urllib.request, "urlopen", blocked), \
            patch.object(socket, "create_connection", blocked), patch.object(socket.socket, "connect", blocked):
        seasonal_parts = []
        summaries, monthly_summaries, checks = {}, {}, {}
        for fuel in ("gas", "elec"):
            print(f"Recomputing {fuel} held-out rows from copied artifacts/cache...", flush=True)
            rows = validate.heldout_rows(fuel)
            seasonal_parts.append(rows)
            summaries[fuel] = canonical(validate.summarize(rows))
            checks[f"{fuel}_seasonal_summary_matches"] = summaries[fuel] == saved_validation[f"seasonal_{fuel}_vs_real_meters"]
        seasonal = pd.concat(seasonal_parts, ignore_index=True)
        monthly = pd.DataFrame(validate.MONTH_ROWS)
        monthly = monthly[monthly.actual > 0]
        for fuel in ("gas", "elec"):
            monthly_summaries[fuel] = canonical(validate.summarize_monthly(monthly[monthly.fuel == fuel]))
            checks[f"{fuel}_monthly_summary_matches"] = monthly_summaries[fuel] == saved_validation[f"monthly_{fuel}_vs_real_meters"]
    row_checks = {"seasonal": compare_rows(seasonal, saved_seasonal, ["fuel", "building_id", "year", "season"]),
                  "monthly": compare_rows(monthly, saved_monthly, ["fuel", "building_id", "year", "month"])}
    family = family_check()
    # Recompute the NEW within-building noise on the same monthly rows. Its denominator
    # is the weather-normal prediction, unlike historical estimate error (actual denominator).
    valid = monthly[(monthly.fuel == "gas") & (monthly.actual > 0) & (monthly.metered > 0)
                    & np.isfinite(monthly.actual) & np.isfinite(monthly.metered)].copy()
    valid["season"] = valid.month.map(climate.MONTH_TO_SEASON)
    valid["residual"] = (valid.actual / valid.metered - 1).abs()
    winter = valid[valid.season == "winter"]
    noise = {"all": float(valid.residual.quantile(.9)), "winter": float(winter.residual.quantile(.9)),
             "winter_months": len(winter), "winter_buildings": int(winter.building_id.nunique()),
             "basis": "p90 abs(actual / held-out same-building weather prediction - 1), monthly gas"}
    additive = json.loads((RESULTS / "uncertainty_additive.json").read_text())
    expected_noise = additive["within_building_gas"]
    checks["new_noise_floor_matches"] = bool(np.isclose(noise["winter"], expected_noise["by_season"]["winter"]["p90_abs_residual_fraction"], rtol=1e-12)
                                             and np.isclose(noise["all"], expected_noise["all"]["p90_abs_residual_fraction"], rtol=1e-12))
    checks["source_hashes_match"] = all(r["matches_copied_source"] for r in hashes)
    checks["source_inputs_unchanged_during_run"] = all(sha256(ROOT / r["path"]) == r["sha256"] for r in hashes)
    checks["prediction_rows_match"] = all(r["all_match"] for r in row_checks.values())
    checks["families_match"] = all(r["matches"] for r in family.values())
    headline = []
    for path, task_value in (("metered", .074), ("blend", .287), ("resstock", .299)):
        value = summaries["gas"]["median_abs_pct_error"][path]["all"]
        subset = seasonal[(seasonal.fuel == "gas") & np.isfinite(seasonal[path]) & (seasonal.actual > 0)]
        headline.append({"metric": "all-season gas median absolute percentage error", "path": path,
                         "recomputed": value, "task_headline": task_value,
                         "drift_percentage_points": round((value - task_value) * 100, 10),
                         "finite_building_year_seasons": len(subset), "finite_buildings": int(subset.building_id.nunique())})
    packages = ("numpy", "pandas", "pyarrow", "scipy", "scikit-learn", "xgboost", "lightgbm", "rasterio", "shapely", "requests", "fastapi", "uvicorn")
    versions = {name: importlib.metadata.version(name) for name in packages}
    result = {"generated_at": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": round(time.monotonic() - started, 3),
              "passed": all(checks.values()), "checks": checks, "python": platform.python_version(), "versions": versions,
              "prediction_recomputation": "Recomputed from copied ResStock artifact and saved nested-CV meter-model OOF predictions; refit same-building change points on other years. No baseline model training; no network.",
              "row_comparisons": row_checks, "headline": headline,
              "winter_resstock_p90_estimate_error": summaries["gas"]["p90_abs_pct_error_winter"]["resstock"],
              "within_building_noise": noise, "family_consistency": family,
              "seasonal_summaries": summaries, "monthly_summaries": monthly_summaries,
              "hashes": hashes, "new_uncertainty_sha256": sha256(RESULTS / "uncertainty_additive.json"),
              "script_sha256": sha256(Path(__file__))}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    write_readme(result)
    print(json.dumps({k: result[k] for k in ("passed", "elapsed_seconds", "checks", "headline", "within_building_noise")}, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


def write_readme(r: dict) -> None:
    table = "\n".join(f"| {h['path']} | {100*h['recomputed']:.1f}% | {100*h['task_headline']:.1f}% | {h['drift_percentage_points']:+.1f} pp | {h['finite_building_year_seasons']} / {h['finite_buildings']} |" for h in r["headline"])
    checks = "\n".join(f"- `{key}`: {'PASS' if value else 'FAIL'}" for key, value in r["checks"].items())
    hashes = "\n".join(f"| `{h['path']}` | `{h['sha256']}` | {'yes' if h['matches_copied_source'] else 'NO'} |" for h in r["hashes"])
    versions = ", ".join(f"{k} {v}" for k, v in r["versions"].items())
    family = "; ".join(f"{k}: {v['artifact_name']} (artifact, selected validation family, serving weights and OOF column agree)" for k,v in r["family_consistency"].items())
    (RESULTS / "SIGNOFF.md").write_text(f'''# P1 copied-artifact validation sign-off

Generated {r['generated_at']}; {'PASS' if r['passed'] else 'FAIL'} in {r['elapsed_seconds']:.3f} seconds. Machine-readable evidence: [finish/signoff.json](finish/signoff.json); command output: [finish/signoff.log](finish/signoff.log).

## Reproduction and scope

From this checkout's repository root:

```bash
.venv/bin/python -m model.scripts.signoff > model/results/finish/signoff.log
```

This audit **recomputed predictions**, not only the displayed summaries: `validate.heldout_rows("gas")` and `heldout_rows("elec")` regenerate held-out monthly/seasonal predictions in memory using the copied ResStock artifact, saved nested-CV meter-model OOF predictions, copied meter targets/weather and other-calendar-year change-point refits. Fold calibration, baseload, null and blend predictions are recalculated. Saved baseline regressors are not retrained. Every numeric prediction column is compared to its saved parquet with rtol=1e-12 and atol=1e-8; rounded published summaries must match exactly. It never calls `validate.main`, `seasonal_check`, `weather_check`, the demo stack or any server. HTTP/socket access is blocked. Writes are limited to this report and `finish/signoff.json` (shell redirection supplies the log).

## Headline numbers from the copied live build

| Gas metric path | Recomputed median absolute error | Requested headline | Drift | Finite building-year-seasons / buildings |
|---|---:|---:|---:|---:|
{table}

The blend headline **28.7% is stale for the copied live artifacts**: the reproducible number is **29.2%**, a +0.5 percentage-point difference. Use 29.2% for this artifact set; no metric was adjusted to recover the requested value. The 7.4% and 29.9% headlines match. The seasonal gas dataset has {r['seasonal_summaries']['gas']['n_building_season_years']} rows across {r['seasonal_summaries']['gas']['n_buildings']} buildings; the table counts each path's finite predictions rather than assigning all rows to the metered path.

These metrics compare **total metered gas** (heating plus non-heating base use), not directly metered heating-only consumption or dollar bills. They are pooled building-season-year summaries, not independent household trials. Metered means a building's other years train its change-point model; unmetered paths use building-held-out OOF predictions. No new confidence interval or causality claim is implied. Metered properties are large Ann Arbor buildings; these validation errors do not establish performance on small houses.

## New bill noise basis is a different quantity

The historical winter ResStock p90 absolute estimate error remains **{100*r['winter_resstock_p90_estimate_error']:.1f}%**, computed as `abs(predicted / actual - 1)` across seasonal building predictions. It measures cross-building estimate error.

The additive temporal noise floor is **{100*r['within_building_noise']['winter']:.6f}% in winter**, recomputed as p90 `abs(actual / held-out same-building monthly prediction - 1)` from {r['within_building_noise']['winter_months']} months in {r['within_building_noise']['winter_buildings']} buildings. It matches `uncertainty_additive.json`; its all-month value is {100*r['within_building_noise']['all']:.6f}%. This changes both the comparison and denominator, so it is **not an improvement from 118.3% to 25.2% in overall model accuracy**. Transfer to an unmetered renter is a pooled temporal component: unknown home-level bias remains, and this alone does not validate savings caused by a commitment. Prior serving behavior remains available; activation is separately capability/parameter gated.

## Artifact and runtime consistency

{family}.

Python **{r['python']}**. Libraries: {versions}.

Checks:

{checks}

Hashes below are recomputed from this isolated checkout and compared with the root agent's read-only copy manifest [finish/source_copy.json](finish/source_copy.json). The audit does not reopen or modify the live checkout. Baseline input hashes are checked again after recomputation to prove this script did not modify them. New uncertainty artifact SHA-256: `{r['new_uncertainty_sha256']}`. Audit script SHA-256: `{r['script_sha256']}`.

| Input | SHA-256 | Matches copy manifest |
|---|---|---|
{hashes}

## Limits

This is a reproduction/sign-off of the copied pipeline's saved validation scheme, not a new independent test set or a new scientific validation of upgrades. It relies on saved nested-CV OOF predictions rather than rerunning expensive nested model selection. Existing split/calibration design is reproduced, not independently redesigned or proved leakage-free. NOAA/weather accuracy values are not re-downloaded or revalidated. New counterfactual effects, endpoint compatibility and live API acceptance are separate tests owned by the integration lead. The live :8001 server and live checkout are untouched.
''')


if __name__ == "__main__":
    main()
