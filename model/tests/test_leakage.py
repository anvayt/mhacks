# Air-leakage model tests: disabled, leakage is not part of the demo.
# """Run: python -m pytest model/tests/test_leakage.py -q  (needs: python -m model.leakage.train && python -m model.leakage.predict --all)"""
# import json

# import pandas as pd

# from model.leakage.data import load
# from model.leakage.predict import predict_leakage
# from model.paths import PROCESSED, RESULTS


# def test_training_data_is_real_and_clean():
#     d, log = load()
#     assert len(d) > 900 and set(d.source) == {"rsbs2015", "rbsa2018"}
#     assert d.cfm50.gt(0).all() and d.ach50.between(0.5, 60).all()


# def test_model_beats_baseline_on_held_out_regions():
#     v = json.loads((RESULTS / "leakage_validation.json").read_text())
#     g = v["tests"]["grouped_leave_one_region_out"]
#     assert g["families"][g["chosen"]]["medape"] < g["families"]["baseline_median"]["medape"] - 0.1


# def test_detached_house_gets_estimate_and_apartment_does_not():
#     t = pd.read_parquet(PROCESSED / "leakage_ann_arbor.parquet")
#     h = t[(t.home_type == "detached") & t.in_training_range].iloc[0]
#     r = predict_leakage(lat=h.lat, lon=h.lon)
#     assert r["estimate"]["cfm50"] and r["inputs"]["home_type"] == "detached"
#     a = t[t.home_type == "apartment_5plus"].iloc[0]
#     assert predict_leakage(lat=a.lat, lon=a.lon)["estimate"]["cfm50"] is None
