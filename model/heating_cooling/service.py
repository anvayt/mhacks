"""P1-06: seasonal heating + cooling point estimates for one location.

    estimate_hc(address="…") or estimate_hc(lat=…, lon=…)
      unit_sqft  – the apartment's size (default: the building, or 854 ft² for a multifamily unit*)
      mode       – "normal" (typical year, 1991–2020), "forecast" (next 12 months), or a past year (e.g. 2024)
      answers    – optional renter answers (model.heating_cooling.resstock_model.ANSWERS)
      heating_fuel – "gas" | "electric" to override the lookup

Routing, most grounded first:
  1. **metered**: the address falls inside an Ann Arbor benchmarked property with a good PRISM fit → that
     building's own change-point model from real monthly meters.
  2. **meter_model+resstock**: unmetered multifamily ≥ 10,000 ft² → geometric mean of the intensity predicted
     from 101 metered Ann Arbor buildings and the meter-calibrated ResStock intensity (best on held-out meters),
     rescaled by local degree-days.
  3. **resstock**: smaller buildings (houses, 2–4 units) → ResStock per-degree-day model (+ renter answers),
     calibrated to real meters for multifamily.
A ResStock cross-check is returned alongside 1 and 2.

Every weather number is at the building's PRISM 800 m cell. Every dollar uses EIA Michigan monthly prices:
marginal gas price (fixed charges removed) and average electricity price.
* ResStock 2024.2 median unit size for Michigan 5+ unit multifamily.
"""
from __future__ import annotations

import json
import pickle
from functools import lru_cache

import numpy as np
import pandas as pd
from shapely import STRtree, wkt
from shapely.geometry import Point

from model import climate
from model.data_sources import census
from model.data_sources.eia import price_table
from model.data_sources.footprints import FootprintIndex, envelope_features
from model.heating_cooling.building_model import TAU_C, TAU_H_ELEC, TAU_H_GAS
from model.heating_cooling.features import BUILDING, building_features
from model.heating_cooling.resstock_model import ANSWERS, BTYPES, MULTIFAMILY
from model.heating_cooling.train import cp_object
from model.paths import ARTIFACTS, PROCESSED, RESULTS

DEFAULT_UNIT_SQFT_MF = 854.0
METER_MODEL_MIN_SQFT = 10_000
KWH_PER_CCF = 103.7 / 3.412
SEASON_ORDER = list(climate.SEASONS)


# ------------------------------------------------------------------ cached resources
@lru_cache(maxsize=1)
def _res():
    def pk(name):
        with open(ARTIFACTS / name, "rb") as f:
            return pickle.load(f)
    meters = pd.read_parquet(PROCESSED / "meters_monthly.parquet")
    targets = pd.read_parquet(PROCESSED / "building_targets.parquet").set_index("building_id")
    cps = pd.read_parquet(PROCESSED / "changepoints.parquet").set_index("building_id")
    from model.data_sources.benchmarking import load_raw
    raw = load_raw()
    polys = raw[raw.AnnArborBenchmarkingID.isin(targets.index)].drop_duplicates("AnnArborBenchmarkingID")
    geoms = [wkt.loads(s) for s in polys.footprint_wkt]
    summary = json.loads((RESULTS / "meters_summary.json").read_text())
    prices = price_table()
    return {
        "targets": targets, "cps": cps, "meters": meters,
        "bench_ids": polys.AnnArborBenchmarkingID.tolist(), "bench_geoms": geoms, "bench_tree": STRtree(geoms),
        "fp": FootprintIndex(),
        "price_by_month": {"gas": {int(k): v for k, v in prices["gas_usd_per_ccf"]["marginal"].items()},
                           "electric": {int(k): v for k, v in prices["elec_usd_per_kwh"]["average"].items()}},
        # non-heating gas (hot water, cooking) per 1,000 ft² per day: median of metered buildings
        "gas_base_ccf_per_1000ft2_day": float((targets.gas_base_ccf / targets.gfa_ft2 * 1000 / 365).median()),
        "bldg_heat": pk("bldg_heat_gas.pkl"), "bldg_cool": pk("bldg_cool_elec.pkl"), "bldg_eheat": pk("bldg_heat_elec.pkl"),
        "resstock": pk("resstock_hc.pkl"),
        "gfa_ratio": summary["gfa_vs_footprint_estimate_median_ratio"],
        "validation": {
            "building_model": json.loads((RESULTS / "building_model_validation.json").read_text()),
            "resstock": json.loads((RESULTS / "resstock_hc_validation.json").read_text()),
            "leakage": json.loads((RESULTS / "leakage_analysis.json").read_text()) if (RESULTS / "leakage_analysis.json").exists() else None,
            "real": json.loads((RESULTS / "validation_real.json").read_text()) if (RESULTS / "validation_real.json").exists() else None,
        },
    }


# ------------------------------------------------------------------ helpers
def _weather(lat, lon, mode) -> pd.DataFrame:
    w = climate.monthly_weather(lat, lon, mode)
    if "year" not in w.columns:
        w["year"] = None
    return w


def _price(month: int, fuel: str) -> float:
    return _res()["price_by_month"][fuel][int(month)]


def _find_benchmarked(lat, lon) -> str | None:
    r = _res()
    idx = r["bench_tree"].query(Point(lon, lat), predicate="intersects")
    return r["bench_ids"][idx[0]] if len(idx) else None


def _guess_btype(floor_area: float, stories: float) -> str:
    """Heuristic when the caller doesn't say. Footprints don't record unit counts."""
    if floor_area >= METER_MODEL_MIN_SQFT:
        return "Multi-Family with 5+ Units"
    if floor_area >= 4000 or stories >= 3:
        return "Multi-Family with 2 - 4 Units"
    return "Single-Family Detached"


# ------------------------------------------------------------------ per-path monthly energy
def _monthly_metered(bid: str, w: pd.DataFrame, fuel: str) -> pd.DataFrame:
    """Building totals per month from its own PRISM change-point fits."""
    row = _res()["cps"].loc[bid]
    out = pd.DataFrame({"month": w.month, "year": w.year})
    fg, fe = cp_object(row, "gas"), cp_object(row, "elec")
    out["heat_ccf"] = fg.predict(w)["heating"].to_numpy() if (fg is not None and fuel == "gas") else 0.0
    pe = fe.predict(w) if fe is not None else None
    out["heat_kwh"] = pe["heating"].to_numpy() if (pe is not None and fuel == "electric") else 0.0
    out["cool_kwh"] = pe["cooling"].to_numpy() if pe is not None else 0.0
    return out


def _intensity_meter_model(feat: dict) -> dict:
    """Per-degree-day intensities (per 1,000 ft²) from the building-level models trained on metered buildings."""
    r = _res()
    X = building_features(pd.DataFrame([feat]))[BUILDING]
    t = r["targets"]
    hdd_ref, cdd_ref = float(t.hdd_ref.median()), float(t.cdd_ref.median())
    def pred(art):
        if art.get("model") is None:
            return art["median"]
        return float(np.exp(art["model"].predict(X)[0]))
    eheat_ref = float(t.hdd_ref.median())  # same reference set of buildings
    return {"heat_ccf_per_hdd": pred(r["bldg_heat"]) / hdd_ref, "cool_kwh_per_cdd": pred(r["bldg_cool"]) / cdd_ref,
            "heat_kwh_per_hdd": (r["bldg_eheat"]["median"] or 0) / eheat_ref}


def _intensity_resstock(feat: dict, btype: str, answers: dict) -> dict:
    rs = _res()["resstock"]
    row = {"sqft": feat["unit_sqft"], "year_built": feat["year_built"], "stories": feat["stories_max"],
           "btype_code": float(BTYPES.index(btype)), "renter": 1.0}
    row.update({a: float(answers[a]) if a in answers and answers[a] is not None else np.nan for a in ANSWERS})
    X = pd.DataFrame([row])[rs["features"]]
    cal = rs["calibration"]
    mf = btype in MULTIFAMILY
    m = rs["models"]
    return {"heat_ccf_per_hdd": float(np.exp(m["heat_gas_per_hdd"].predict(X)[0])) * (cal["heat_gas"] if mf else 1.0),
            "heat_kwh_per_hdd": float(np.exp(m["heat_elec_per_hdd"].predict(X)[0])) * cal["heat_elec"],
            "cool_kwh_per_cdd": float(np.exp(m["cool_per_cdd"].predict(X)[0])) * (cal["cool"] if mf else 1.0),
            "calibrated_to_meters": mf}


def _monthly_from_intensity(it: dict, w: pd.DataFrame, area_ft2: float, fuel: str) -> pd.DataFrame:
    k = area_ft2 / 1000
    out = pd.DataFrame({"month": w.month, "year": w.year})
    out["heat_ccf"] = it["heat_ccf_per_hdd"] * w[f"hdd{TAU_H_GAS}"] * k if fuel == "gas" else 0.0
    out["heat_kwh"] = it["heat_kwh_per_hdd"] * w[f"hdd{TAU_H_ELEC}"] * k if fuel == "electric" else 0.0
    out["cool_kwh"] = it["cool_kwh_per_cdd"] * w[f"cdd{TAU_C}"] * k
    return out


def _seasonal(monthly: pd.DataFrame, w: pd.DataFrame, scale: float) -> tuple[list, dict]:
    m = monthly.copy()
    for c in ("heat_ccf", "heat_kwh", "cool_kwh"):
        m[c] = m[c] * scale
    m["heat_usd"] = m.heat_ccf * m.month.map(lambda x: _price(x, "gas")) + m.heat_kwh * m.month.map(lambda x: _price(x, "electric"))
    m["cool_usd"] = m.cool_kwh * m.month.map(lambda x: _price(x, "electric"))
    m["season"] = m.month.map(climate.MONTH_TO_SEASON)
    ws = climate.seasonal(w).set_index("season")
    seasons = []
    for s in SEASON_ORDER:
        g = m[m.season == s]
        if g.empty:
            continue
        seasons.append({
            "season": s, "months": [int(x) for x in g.month],
            "heating": {"usd": round(float(g.heat_usd.sum()), 0), "gas_ccf": round(float(g.heat_ccf.sum()), 1),
                        "electric_kwh": round(float(g.heat_kwh.sum()), 0)},
            "cooling": {"usd": round(float(g.cool_usd.sum()), 0), "electric_kwh": round(float(g.cool_kwh.sum()), 0)},
            "total_usd": round(float(g.heat_usd.sum() + g.cool_usd.sum()), 0),
            "weather": {"tmean_f": round(float(ws.loc[s, "tmean_f"]), 1), "hdd65": round(float(ws.loc[s, "hdd65"]), 0),
                        "cdd65": round(float(ws.loc[s, "cdd65"]), 0), f"hdd{TAU_H_GAS}": round(float(ws.loc[s, f"hdd{TAU_H_GAS}"]), 0)},
        })
    annual = {"heating_usd": round(float(m.heat_usd.sum()), 0), "cooling_usd": round(float(m.cool_usd.sum()), 0),
              "total_usd": round(float(m.heat_usd.sum() + m.cool_usd.sum()), 0),
              "gas_ccf": round(float(m.heat_ccf.sum()), 1), "electric_kwh": round(float(m.heat_kwh.sum() + m.cool_kwh.sum()), 0),
              "hdd65": round(float(w.hdd65.sum()), 0), "cdd65": round(float(w.cdd65.sum()), 0),
              "tmean_f": round(float(climate.c_to_f(np.average(w.tmean_c, weights=w.days))), 1)}
    return seasons, annual


# ------------------------------------------------------------------ public API
def estimate_hc(address: str | None = None, lat: float | None = None, lon: float | None = None,
                unit_sqft: float | None = None, mode: str | int = "normal", answers: dict | None = None,
                heating_fuel: str | None = None, building_type: str | None = None) -> dict:
    r = _res()
    answers = answers or {}
    loc = {"lat": lat, "lon": lon, "matched_address": None, "block_group": None}
    if address:
        g = census.geocode(address)
        if g is None:
            raise ValueError(f"could not geocode: {address}")
        loc.update(g)
    elif lat is None or lon is None:
        raise ValueError("give an address or lat+lon")
    lat, lon = loc["lat"], loc["lon"]
    w = _weather(lat, lon, mode)
    sources = ["PRISM Climate Group, Oregon State University (800 m tmean)",
               "Open-Meteo (ERA5 reanalysis / forecast / ECMWF SEAS5)",
               "US EIA Michigan residential prices (N3010MI3, N3010MI2, EIA-861M)"]

    bid = _find_benchmarked(lat, lon)
    t = r["targets"]
    building: dict = {}
    method, cross = None, None

    if bid is not None and bid in t.index:
        b = t.loc[bid]
        fuel = heating_fuel or ("electric" if bool(b.electric_heat) else "gas")
        building = {"name": b["name"], "address": b.address, "gfa_ft2": float(b.gfa_ft2), "year_built": int(b.year_built),
                    "year_built_source": "Ann Arbor benchmarking", "stories": float(b.stories_max),
                    "buildings_on_property": int(b.fp_count), "benchmarking_id": bid, "energy_star_score": b.energy_star,
                    "heating_fuel": fuel, "heating_fuel_source": "metered gas vs electric heating response"}
        good = (fuel == "gas" and b.gas_r2 >= 0.7) or (fuel == "electric" and b.elec_r2 >= 0.3)
        if good:
            monthly = _monthly_metered(bid, w, fuel)
            area = float(b.gfa_ft2)
            method = "metered"
            sources.append("City of Ann Arbor energy benchmarking (monthly utility meters, 2021–2023)")
            building["fit"] = {"gas_r2": round(float(b.gas_r2), 3) if pd.notna(b.gas_r2) else None,
                               "elec_r2": round(float(b.elec_r2), 3) if pd.notna(b.elec_r2) else None}
        feat = {"gfa_ft2": b.gfa_ft2, "year_built": b.year_built, "stories_max": b.stories_max,
                "height_ft_max": b.height_ft_max, "surface_to_volume": b.surface_to_volume, "fp_count": b.fp_count,
                "fp_area_ft2": b.fp_area_ft2}
    else:
        fps = r["fp"].at_point(lat, lon)
        env = envelope_features(fps)
        if env.get("fp_count", 0) == 0:
            raise ValueError("no building footprint near this location (footprints cover the City of Ann Arbor)")
        # property = every footprint of the same named complex within 600 m (the city names apartment complexes,
        # e.g. "Greenbrier Apartments"; parcel ids are mostly blank in this layer)
        name = fps.iloc[0].bldg_name
        if isinstance(name, str) and name.strip():
            df = r["fp"].df
            same = df[(df.bldg_name == name) & ((df.lat - lat).abs() < 0.0055) & ((df.lon - lon).abs() < 0.0075)]
            if 1 <= len(same) <= 80:
                fps = same
                env = envelope_features(fps)
        yb, yb_src = census.median_year_built(loc["block_group"]) if loc["block_group"] else (None, "none")
        if yb is None:
            yb, yb_src = float(t.year_built.median()), "median of Ann Arbor benchmarked buildings (no block group)"
        gfa = env["fp_floor_area_est_ft2"] / r["gfa_ratio"]
        hf = census.heating_fuel(loc["block_group"]) if loc["block_group"] else {"fuel": "gas", "source": "default"}
        fuel = heating_fuel or hf["fuel"]
        building = {"name": fps.iloc[0].bldg_name, "gfa_ft2": round(gfa, 0),
                    "gfa_source": f"footprint area × stories ÷ {r['gfa_ratio']:.2f} (median ratio vs reported GFA, 125 benchmarked buildings)",
                    "year_built": int(yb), "year_built_source": yb_src, "stories": env["stories_max"],
                    "buildings_on_property": env["fp_count"],
                    "heating_fuel": fuel, "heating_fuel_source": hf.get("source"),
                    "heating_fuel_shares": {k: hf.get(k) for k in ("gas_share", "electric_share")}}
        feat = {"gfa_ft2": gfa, "year_built": yb, "stories_max": env["stories_max"], "height_ft_max": env["height_ft_max"],
                "surface_to_volume": env["surface_to_volume"], "fp_count": env["fp_count"], "fp_area_ft2": env["fp_area_ft2"]}

    btype = building_type or _guess_btype(float(feat["gfa_ft2"]), float(feat["stories_max"]))
    building["building_type"] = btype
    building["building_type_source"] = "caller" if building_type else "heuristic from floor area and stories"
    is_mf = btype in MULTIFAMILY
    if unit_sqft is None:
        unit_sqft = DEFAULT_UNIT_SQFT_MF if is_mf else float(feat["gfa_ft2"])
        unit_src = "ResStock 2024.2 MI median 5+ unit apartment" if is_mf else "whole building"
    else:
        unit_src = "caller"

    rs_feat = dict(feat, unit_sqft=unit_sqft)
    it_rs = _intensity_resstock(rs_feat, btype, answers)
    if method is None:
        if float(feat["gfa_ft2"]) >= METER_MODEL_MIN_SQFT and is_mf:
            # geometric mean of the meter-trained model and calibrated ResStock: the best no-meter path on
            # held-out real meters (results/validation_real.json)
            im = _intensity_meter_model(feat)
            it = {k: float(np.sqrt(im[k] * it_rs[k])) for k in ("heat_ccf_per_hdd", "cool_kwh_per_cdd")}
            it["heat_kwh_per_hdd"] = im["heat_kwh_per_hdd"]
            parts = {"meter_model": im, "resstock": it_rs, "blend": it}
            method = "meter_model+resstock"
            sources.append("City of Ann Arbor energy benchmarking (101 metered buildings, building-level model)")
        else:
            it = it_rs
            parts = {"resstock": it_rs}
            method = "resstock"
        area = float(feat["gfa_ft2"])
        monthly = _monthly_from_intensity(it, w, area, fuel)
    if method != "resstock":
        cross = _monthly_from_intensity(it_rs, w, unit_sqft, fuel)
    sources.append("NREL ResStock 2024.2 Michigan (18,756 simulated homes)")
    sources.append("City of Ann Arbor building footprints; US Census geocoder + ACS 5-yr (B25037, B25040)")

    # building totals → this unit (floor-area share)
    scale = unit_sqft / area
    seasons, annual = _seasonal(monthly, w, scale)
    detail = _model_detail(method, bid, parts if method != "metered" else None, fuel, area, unit_sqft, w, answers)
    out = {
        "location": loc,
        "building": building,
        "unit_sqft": unit_sqft, "unit_sqft_source": unit_src,
        "mode": str(mode), "method": method,
        "seasons": seasons, "annual": annual,
        "model_detail": detail,
        "weather_source": w.level_source.iloc[0] if "level_source" in w else None,
        "prices": {"gas_usd_per_ccf": "EIA MI residential marginal (fixed charges removed), by month",
                   "electricity_usd_per_kwh": "EIA-861M MI residential average, by month"},
        "sources": sources,
    }
    if cross is not None:
        _, ca = _seasonal(cross, w, 1.0)
        out["cross_check_resstock"] = {"heating_usd": ca["heating_usd"], "cooling_usd": ca["cooling_usd"],
                                       "calibrated_to_meters": it_rs["calibrated_to_meters"]}
    v = r["validation"]
    real = (v.get("real") or {}).get("seasonal_gas_vs_real_meters", {}).get("median_abs_pct_error", {})
    path = {"metered": "metered", "meter_model+resstock": "blend", "resstock": "resstock"}[method]
    out["accuracy"] = {
        "seasonal_gas_median_abs_error": real.get(path),
        "basis": {"metered": "this building's own meters, predicting a held-out year",
                  "blend": "Ann Arbor buildings held out of training (never seen), seasonal gas vs real meters",
                  "resstock": "ResStock applied to held-out real Ann Arbor buildings ≥10k ft²; small buildings have no "
                              "local meter data, so expect at least this error"}[path],
        "cooling_note": "cooling is validated less well than heating (building features barely beat the median)",
    }
    if method == "resstock":
        rv = v["resstock"]["targets"]
        key = "all_answers" if answers else "public_record_only"
        out["accuracy"]["simulation_heldout_median_abs_error"] = {
            "heating": rv["heat_gas_per_hdd"][key]["test_median_ape"], "cooling": rv["cool_per_cdd"][key]["test_median_ape"]}
    return out


def _model_detail(method, bid, parts, fuel, area, unit_sqft, w, answers) -> dict:
    """The numbers behind the estimate, so a reader can redo the arithmetic:
    season energy = intensity (per 1,000 ft² per degree-day) × season degree-days × building ft²/1,000 × unit share."""
    r = _res()
    rnd = lambda x: None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), 5)
    d = {"method": method, "building_ft2": round(area, 0), "unit_ft2": unit_sqft, "unit_share": rnd(unit_sqft / area),
         "heating_fuel": fuel, "degree_days_year": {f"hdd{TAU_H_GAS}": round(float(w[f"hdd{TAU_H_GAS}"].sum()), 0),
                                                     f"hdd{TAU_H_ELEC}": round(float(w[f"hdd{TAU_H_ELEC}"].sum()), 0),
                                                     f"cdd{TAU_C}": round(float(w[f"cdd{TAU_C}"].sum()), 0)}}
    if method == "metered":
        row = r["cps"].loc[bid]
        gfa = float(r["targets"].loc[bid, "gfa_ft2"])
        g = {k: rnd(row.get(f"gas_{k}")) for k in ("alpha", "beta_h", "tau_h", "r2", "cv_rmse", "n")}
        e = {k: rnd(row.get(f"elec_{k}")) for k in ("alpha", "beta_h", "beta_c", "tau_h", "tau_c", "r2", "cv_rmse", "n")}
        d["equation"] = "monthly use = base/day × days + heating slope × HDD(τh) + cooling slope × CDD(τc)  (fit to this building's 2021–23 meters)"
        d["gas_fit"] = {**g, "unit": "ccf", "heat_ccf_per_1000ft2_per_hdd": rnd((g["beta_h"] or 0) / gfa * 1000)}
        d["elec_fit"] = {**e, "unit": "kWh", "cool_kwh_per_1000ft2_per_cdd": rnd((e["beta_c"] or 0) / gfa * 1000)}
        return d
    names = {"meter_model": "meter-trained model (" + {"mlr": "ridge regression", "random_forest": "random forest", "xgboost": "XGBoost",
                                                         "null_median": "median of metered buildings"}.get(r["bldg_heat"].get("name"), r["bldg_heat"].get("name")) + " heating / "
                            + {"mlr": "ridge regression", "random_forest": "random forest", "xgboost": "XGBoost", "null_median": "median of metered buildings"}.get(r["bldg_cool"].get("name"), r["bldg_cool"].get("name")) + " cooling)",
             "resstock": "ResStock XGBoost" + (" (calibrated to meters)" if parts["resstock"].get("calibrated_to_meters") else ""),
             "blend": "blend = √(meter model × ResStock)"}
    d["equation"] = (f"season energy = intensity × season degree-days × {round(area):,} ft² / 1,000 × unit share "
                     f"{unit_sqft / area:.5f}; heating uses HDD{TAU_H_GAS if fuel == 'gas' else TAU_H_ELEC}, cooling uses CDD{TAU_C}")
    d["intensities"] = [{"model": names[k], "heat_ccf_per_1000ft2_per_hdd": rnd(v.get("heat_ccf_per_hdd")),
                         "heat_kwh_per_1000ft2_per_hdd": rnd(v.get("heat_kwh_per_hdd")),
                         "cool_kwh_per_1000ft2_per_cdd": rnd(v.get("cool_kwh_per_cdd")), "used": k == ("blend" if "blend" in parts else "resstock")}
                        for k, v in parts.items()]
    d["renter_answers_used"] = answers or {}
    return d


def heldout(fuel: str | None = None) -> list[dict]:
    """Held-out building-season rows (real meters vs every estimate path), from model.heating_cooling.validate."""
    d = pd.read_parquet(RESULTS / "heldout_seasonal.parquet")
    if fuel:
        d = d[d.fuel == fuel]
    return json.loads(d.round(2).to_json(orient="records"))


def metered_list() -> list[dict]:
    r = _res()
    t = r["targets"]
    return [{"building_id": bid, "name": b["name"], "address": b.address, "gfa_ft2": float(b.gfa_ft2),
             "year_built": int(b.year_built), "gas_r2": None if pd.isna(b.gas_r2) else round(float(b.gas_r2), 3),
             "elec_r2": None if pd.isna(b.elec_r2) else round(float(b.elec_r2), 3)}
            for bid, b in t.sort_values("name").iterrows()]


def metered_building(bid: str) -> dict:
    """Month by month for one metered property: actual meter readings vs the change-point model.
    'fit' = fitted on all of 2021–23 (in-sample); 'heldout' = fitted on the other two years only (what the
    model would have predicted for a year it never saw). Dollars = usage × the same monthly prices the
    estimates use (gas marginal, electricity average), so they exclude fixed customer charges."""
    from model.heating_cooling import changepoint
    r = _res()
    m = pd.read_parquet(PROCESSED / "meters_weather.parquet")
    g = m[m.building_id == bid].sort_values(["year", "month"])
    if g.empty:
        raise ValueError(f"unknown metered building {bid}")
    row = r["cps"].loc[bid] if bid in r["cps"].index else None
    out = g[["year", "month", "days", "hdd60", "hdd65", "cdd65", "tmean_c"]].copy()
    out["tmean_f"] = climate.c_to_f(out.tmean_c)
    for fuel, col, ok, outl, heat, cool in (("gas", "gas_ccf", "gas_ok", "gas_ccf_outlier", True, False),
                                             ("elec", "elec_kwh", "elec_ok", "elec_kwh_outlier", True, True)):
        good = g[ok] & ~g[outl]
        out[f"{fuel}_actual"] = g[col].where(good)
        f = cp_object(row, fuel) if row is not None else None
        if f is not None:
            p = f.predict(g)
            out[f"{fuel}_fit"] = p.total.to_numpy()
            out[f"{fuel}_fit_base"] = p.base.to_numpy()
            out[f"{fuel}_fit_heat"] = np.asarray(p.heating, dtype=float) if np.ndim(p.heating) else 0.0
            out[f"{fuel}_fit_cool"] = np.asarray(p.cooling, dtype=float) if np.ndim(p.cooling) else 0.0
        ho = []
        for yr in sorted(g.year.unique()):
            tr = g[(g.year != yr) & good]
            fh = changepoint.fit(tr, col, heating=heat, cooling=cool) if len(tr) >= 9 else None
            ho.append(fh.predict(g[g.year == yr]).total if fh is not None else pd.Series(np.nan, index=g[g.year == yr].index))
        out[f"{fuel}_heldout"] = pd.concat(ho).reindex(g.index).to_numpy()
        price = r["price_by_month"]["gas" if fuel == "gas" else "electric"]
        for c in ("actual", "fit", "heldout"):
            if f"{fuel}_{c}" in out:
                out[f"{fuel}_{c}_usd"] = out[f"{fuel}_{c}"] * out.month.map(price)
    t = r["targets"].loc[bid] if bid in r["targets"].index else None
    info = {"building_id": bid, "name": g.name.iloc[0], "address": g.address.iloc[0], "gfa_ft2": float(g.gfa_ft2.iloc[0]),
            "year_built": int(g.year_built.iloc[0]), "lat": float(g.lat.iloc[0]), "lon": float(g.lon.iloc[0])}
    if row is not None:
        for fuel in ("gas", "elec"):
            f = cp_object(row, fuel)
            info[f"{fuel}_fit"] = None if f is None else {k: (None if v is None else round(float(v), 4))
                                                            for k, v in f.to_dict().items()}
    return {"building": info, "monthly": json.loads(out.drop(columns=["tmean_c"]).round(3).to_json(orient="records"))}


def weather(lat: float, lon: float, mode: str | int = "normal") -> dict:
    w = _weather(lat, lon, mode)
    s = climate.seasonal(w)
    return {"lat": lat, "lon": lon, "mode": str(mode),
            "monthly": json.loads(w.round(2).to_json(orient="records")),
            "seasons": json.loads(s.round(2).to_json(orient="records"))}


def bill_check(year: int, month: int, gas_ccf: float, unit_sqft: float, address: str | None = None,
               lat: float | None = None, lon: float | None = None) -> dict:
    """Compare one real monthly gas bill with what this location's actual weather that month predicts.
    Expected = heating (degree-days of that month at the PRISM cell) + non-heating gas baseload (median of
    metered Ann Arbor buildings). The noise floor is the out-of-year winter-month error on real meters."""
    est = estimate_hc(address=address, lat=lat, lon=lon, unit_sqft=unit_sqft, mode=year)
    w = climate.monthly_weather_years(est["location"]["lat"], est["location"]["lon"], [year])
    row = w.loc[w.month == month].iloc[0]
    season = climate.MONTH_TO_SEASON[month]
    s = next(x for x in est["seasons"] if x["season"] == season)
    share = float(row[f"hdd{TAU_H_GAS}"]) / max(s["weather"][f"hdd{TAU_H_GAS}"], 1)
    heat = s["heating"]["gas_ccf"] * share
    base = _res()["gas_base_ccf_per_1000ft2_day"] * unit_sqft / 1000 * float(row["days"])
    expected = heat + base
    # noise floor = p90 winter-month error of this estimate path on held-out real meters
    real = _res()["validation"]["real"]["seasonal_gas_vs_real_meters"]["p90_abs_pct_error_winter"]
    path = {"metered": "metered", "meter_model+resstock": "blend", "resstock": "resstock"}[est["method"]]
    noise = real[path] if month in (12, 1, 2) else None
    pct = gas_ccf / expected - 1
    return {"year": year, "month": month, "actual_gas_ccf": gas_ccf,
            "expected_gas_ccf": round(expected, 1), "expected_heating_ccf": round(heat, 1), "expected_base_ccf": round(base, 1),
            "pct_vs_expected_for_weather": round(pct, 3), "hdd65_that_month": round(float(row["hdd65"]), 0),
            "tmean_f_that_month": round(float(climate.c_to_f(row["tmean_c"])), 1),
            "noise_floor": noise,
            "meaningful": (abs(pct) > noise) if noise else None,
            "method": est["method"],
            "note": "only winter months are judged (heating dominates). noise_floor = p90 winter error of this estimate path on held-out real Ann Arbor meters; a bill inside it is consistent with the estimate"}
