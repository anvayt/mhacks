"""Pre-score every metered Ann Arbor residential property (typical year, per UNIT_SQFT apartment)
plus every large residential footprint parcel (≥ 10,000 ft² estimated floor area) for the map/leaderboard.

Run: python -m model.hc.score_buildings → data/processed/buildings_hc.parquet (+ .csv)
"""
import pandas as pd

from model.hc import service
from model.paths import PROCESSED

UNIT_SQFT = service.DEFAULT_UNIT_SQFT_MF


def main():
    r = service._res()
    rows = []
    t = r["targets"]
    for bid, b in t.iterrows():
        try:
            e = service.estimate_hc(lat=b.lat, lon=b.lon, unit_sqft=UNIT_SQFT)
        except Exception as ex:
            print("skip", bid, ex); continue
        rows.append(_row(e, bid))
    # unmetered apartment complexes: named residential footprint groups, plus unnamed single buildings,
    # with ≥ 10,000 ft² estimated floor area
    fp = r["fp"].df
    res = fp[fp.struc_type == "Residential"]
    named = res[res.bldg_name.fillna("").str.strip() != ""]
    groups = named.groupby(["bldg_name", named.lat.round(2), named.lon.round(2)]).agg(
        floor=("floor_area_est_ft2", "sum"), lat=("lat", "mean"), lon=("lon", "mean")).reset_index(drop=True)
    single = res[res.bldg_name.fillna("").str.strip() == ""][["floor_area_est_ft2", "lat", "lon"]].rename(
        columns={"floor_area_est_ft2": "floor"})
    cand = pd.concat([groups, single])
    cand = cand[cand.floor / r["gfa_ratio"] >= service.METER_MODEL_MIN_SQFT]
    print("candidate complexes/buildings:", len(cand))
    for i, p in cand.iterrows():
        try:
            e = service.estimate_hc(lat=p.lat, lon=p.lon, unit_sqft=UNIT_SQFT, heating_fuel="gas")
        except Exception as ex:
            print("skip", i, ex); continue
        if e["method"] == "metered":
            continue
        rows.append(_row(e, f"{e['building'].get('name') or 'bldg'}@{p.lat:.5f},{p.lon:.5f}"))
    df = pd.DataFrame(rows).drop_duplicates("id")
    df.to_parquet(PROCESSED / "buildings_hc.parquet", index=False)
    df.to_csv(PROCESSED / "buildings_hc.csv", index=False)
    print(df.method.value_counts().to_dict(), len(df))
    print(df[["heating_usd_yr", "cooling_usd_yr"]].describe().round(0))


def _row(e, id_):
    s = {x["season"]: x for x in e["seasons"]}
    return {"id": id_, "method": e["method"], "name": e["building"].get("name"),
            "lat": e["location"]["lat"], "lon": e["location"]["lon"],
            "gfa_ft2": e["building"]["gfa_ft2"], "year_built": e["building"]["year_built"],
            "unit_sqft": e["unit_sqft"],
            "heating_usd_yr": e["annual"]["heating_usd"], "cooling_usd_yr": e["annual"]["cooling_usd"],
            **{f"{k}_usd": s[k]["total_usd"] for k in s},
            "hdd65": e["annual"]["hdd65"], "cdd65": e["annual"]["cdd65"], "tmean_f": e["annual"]["tmean_f"]}


if __name__ == "__main__":
    main()
