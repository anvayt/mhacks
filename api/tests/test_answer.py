"""P2-04: sessions, POST /answer, GET /session/{id}, score/grade, p10/p90 band. P1's model server and P2-01's
address lookup are monkeypatched with bodies shaped like model/heating_cooling/service.py's estimate_hc."""

import httpx
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import score
from app.main import app

client = TestClient(app)
MF = "Multi-Family with 5+ Units"
# multiplier on the annual $ per renter answer (missing = 1.0, as if P1's model sat at its default)
EFFECT = {"window_panes": {"1": 1.25, "2": 1.0, "3": 0.92}, "floor_level": {"0": 1.08, "1": 0.9, "2": 1.12},
          "cooling_code": {"0": 0.97, "1": 1.0, "2": 1.06, "3": 0.95}, "heating_fuel": {"gas": 1.0, "electric": 1.9}}
SHARE = {"winter": 0.55, "spring": 0.15, "summer": 0.18, "fall": 0.12}
MONTH_SHARE = [0.2, 0.17, 0.1, 0.04, 0.02, 0.05, 0.07, 0.06, 0.02, 0.03, 0.09, 0.15]


def fake_hc(params: dict, metered: bool = False) -> dict:
    sqft = float(params["unit_sqft"])
    total = 0.48 * sqft  # about the peer median $/sq ft in buildings_hc.csv
    for q, eff in EFFECT.items():
        if q in params and (q == "heating_fuel" or not metered):  # metered path ignores renter answers (service.py)
            # an interaction, like XGBoost's: on a middle floor the windows matter twice as much
            total *= eff[str(params[q])] ** (2 if q == "window_panes" and str(params.get("floor_level")) == "1" else 1)
    total = round(total)
    err = 0.074 if metered else 0.299
    return {
        "location": {"lat": float(params["lat"]), "lon": float(params["lon"]), "matched_address": None,
                     "block_group": params.get("block_group")},
        "building": {"year_built": 1965, "year_built_source": "ACS 2020-2024 B25035 block group median",
                     "heating_fuel": params.get("heating_fuel", "gas"), "building_type": params["building_type"]},
        "unit_sqft": sqft, "unit_sqft_source": "caller", "mode": "normal",
        "method": "metered" if metered else "resstock",
        "seasons": [{"season": s, "total_usd": round(total * f), "heating": {"usd": round(total * f * 0.8)},
                     "cooling": {"usd": round(total * f * 0.2), "electric_kwh": round(total * f)}} for s, f in SHARE.items()],
        "annual": {"heating_usd": round(total * 0.8), "cooling_usd": round(total * 0.2), "total_usd": float(total),
                   "electric_kwh": float(total)},
        "months": [{"month": i + 1, "total_usd": round(total * f),
                    "cooling": {"usd": round(total * f * 0.2), "electric_kwh": round(total * f)}}
                   for i, f in enumerate(MONTH_SHARE)],
        "accuracy": {"seasonal_gas_median_abs_error": {"all": err, "winter": err}, "basis": "held-out real meters"},
    }


FEATURES = {"lat": 42.2775, "lon": -83.7409, "in.sqft": 850, "in.geometry_building_type_recs": MF,
            "block_group_geoid": "261614003001", "matched_address": "715 ARBOR ST, ANN ARBOR, MI, 48104",
            "sqft_estimated": True, "year_built": 1965, "year_built_source": "ACS block group median",
            "warnings": [], "footprint_geojson": {"type": "Polygon", "coordinates": [[
                [-83.741, 42.2774], [-83.7408, 42.2774], [-83.7408, 42.2776], [-83.741, 42.2776], [-83.741, 42.2774]]]}}


@pytest.fixture(autouse=True)
def fakes(monkeypatch, tmp_path):
    monkeypatch.setattr("app.sessions.DB", str(tmp_path / "sessions.sqlite"))
    monkeypatch.setattr("app.estimate.get_features", lambda address, unit_sqft=None: dict(FEATURES))
    calls = []

    def get(url, params=None, timeout=None):
        calls.append(params)
        return httpx.Response(200, json=fake_hc(params, metered="metered" in FEATURES["matched_address"]),
                              request=httpx.Request("GET", url))
    monkeypatch.setattr("app.estimate.httpx.get", get)
    return calls


def _estimate() -> dict:
    r = client.post("/estimate", json={"address": "715 Arbor St, Ann Arbor, MI"})
    assert r.status_code == 200, r.text
    return r.json()


def _answer(sid, q, a) -> dict:
    r = client.post("/answer", json={"session_id": sid, "question_id": q, "answer": a})
    assert r.status_code == 200, r.text
    return r.json()


def _width(e) -> float:
    return e["bill"]["annual"]["p90"] - e["bill"]["annual"]["p10"]


def test_answers_narrow_the_band_and_lock_the_grade():
    e = _estimate()
    sid, b = e["session_id"], e["bill"]
    assert sid and not e["locked"] and len(e["grade_span"]) > 1
    assert b["annual"]["p10"] < b["annual"]["p50"] < b["annual"]["p90"] and "held-out" in b["band_method"]
    assert all(m["p10"] <= m["p50"] <= m["p90"] for m in [*b["seasonal"].values(), *b["monthly"].values()])
    assert [q["id"] for q in e["questions"]][0] == "heating_fuel"  # biggest swing first
    assert {"value": "2", "label": "Double-pane"} in next(q for q in e["questions"] if q["id"] == "window_panes")["options"]
    for q, a in (("heating_fuel", "gas"), ("window_panes", "double pane"), ("floor_level", 1), ("cooling_code", "Window AC")):
        prev, e = e, _answer(sid, q, a)
        assert _width(e) < _width(prev), q
        assert len(e["grade_span"]) <= len(prev["grade_span"]), q
        assert q not in [x["id"] for x in e["questions"]]
    assert e["answers"] == {"heating_fuel": "gas", "window_panes": "2", "floor_level": "1", "cooling_code": "1"}
    assert e["locked"] and e["questions"] == [] and e["grade_span"] == [e["grade"]]
    assert e["bill"]["annual"]["p10"] < e["bill"]["annual"]["p50"]  # the $ range keeps the meter error
    assert e["bill"]["annual"]["p50"] == round(0.48 * 850 * 0.9)  # the answers reached the model


def test_grade_span_excludes_meter_error():
    e = _estimate()
    g, a = e["grade_band_usd"], e["bill"]["annual"]
    assert (a["p10"], a["p90"]) == (round(g["p10"] * (1 - 0.299)), round(g["p90"] * (1 + 0.299)))
    assert e["grade_span"][0] == score.score_for(g["p10"], 850, MF)["grade"]
    assert e["grade_span"][-1] == score.score_for(g["p90"], 850, MF)["grade"]
    assert "meter" in e["grade_span_method"]


def test_band_never_widens_after_an_answer():  # floor=middle makes the open window question swing more
    e = _estimate()
    e2 = _answer(e["session_id"], "floor_level", "middle")
    for k in (lambda x: x["bill"]["annual"], lambda x: x["grade_band_usd"]):
        a, b = k(e), k(e2)
        assert 0 < a["p10"] <= b["p10"] <= b["p50"] <= b["p90"] <= a["p90"]


def test_no_ac_zeroes_cooling():
    e = _estimate()
    no_ac = fake_hc({**e["model_params"], "cooling_code": "0"})["annual"]
    assert e["grade_band_usd"]["p10"] <= no_ac["total_usd"] - no_ac["cooling_usd"]  # No AC counts as $0 cooling
    e = _answer(e["session_id"], "cooling_code", "none")
    hc = e["heating_cooling"]
    assert e["bill"]["annual"]["p50"] == no_ac["total_usd"] - no_ac["cooling_usd"] and hc["annual"]["cooling_usd"] == 0
    assert all(x["cooling"] == {"usd": 0, "electric_kwh": 0} for x in [*hc["seasons"], *hc["months"]])
    assert sum(m["p50"] for m in e["bill"]["monthly"].values()) < no_ac["total_usd"]
    assert e["bill"]["note"].startswith("No AC")


def test_metered_building_asks_only_no_ac(monkeypatch):  # meters, not renter answers, drive the metered path
    monkeypatch.setitem(FEATURES, "matched_address", "1 metered way")
    e = _estimate()
    assert [q["id"] for q in e["questions"]] == ["cooling_code"]  # only "No AC" changes a metered estimate
    e = _answer(e["session_id"], "cooling_code", "central")
    a = e["bill"]["annual"]
    assert e["questions"] == [] and e["locked"]
    assert a["p10"] == round(a["p50"] * (1 - 0.074)) and a["p90"] == round(a["p50"] * (1 + 0.074))


def test_session_round_trip():
    e = _estimate()
    assert client.get(f"/session/{e['session_id']}").json() == e
    e2 = _answer(e["session_id"], "window_panes", "skip")  # skipped: not asked again, still unknown in the band
    assert e2["answers"] == {"window_panes": None} and "window_panes" not in [q["id"] for q in e2["questions"]]
    assert _width(e2) == _width(e)
    assert client.get(f"/session/{e['session_id']}").json() == e2
    r = client.get("/session/nope1234")
    assert r.status_code == 404 and r.json()["detail"] == {"code": "not_found", "message": "That session expired. Send the listing again."}


@pytest.mark.parametrize("q,a", [("window_panes", "purple"), ("window_panes", "pane"), ("cooling_code", "ac"),
                                 ("heating_fuel", 7), ("occupants", "2")])
def test_bad_answers(q, a):
    sid = _estimate()["session_id"]
    r = client.post("/answer", json={"session_id": sid, "question_id": q, "answer": a})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "bad_answer"
    if q == "window_panes":
        assert "Single-pane, Double-pane or Triple-pane" in r.json()["detail"]["message"]


def test_answer_unknown_session():
    r = client.post("/answer", json={"session_id": "gone0000", "question_id": "window_panes", "answer": "2"})
    assert r.status_code == 404 and r.json()["detail"]["code"] == "not_found"


def test_score_math_on_known_rows():
    peers = score.peer_costs(MF)
    assert len(peers) == 589  # 591 buildings minus 2 with $0 heating
    assert not np.isclose(peers, 114 / 854).any()  # Sequoia Place: $0 heat (tenant-metered) + $114 cooling
    med = float(np.median(peers))
    s = score.score_for(med * 854, 854, MF)
    assert 45 <= s["score"] <= 55 and s["grade"] == "C" and s["hidden_rent_usd_mo"] == 0
    assert s["percentile_peers"] == pytest.approx(s["score"] / 100, abs=0.006)
    assert score.score_for(med * 854 + 120, 854, MF)["hidden_rent_usd_mo"] == 10
    assert score.score_for(peers.min() * 854 * 0.5, 854, MF)["score"] == 100
    worst = score.score_for(peers.max() * 854 * 2, 854, MF)
    assert (worst["score"], worst["grade"], worst["percentile_peers"]) == (0, "F", 0.0)
    # Huron Towers (metered, $413 heat + $93 cool per 854 sq ft) scores the same at any size: $/sq ft
    assert score.score_for(506, 854, MF)["score"] == score.score_for(506 * 2, 854 * 2, MF)["score"]


@pytest.mark.parametrize("s,g", [(100, "A"), (80, "A"), (79, "B"), (60, "B"), (59, "C"), (40, "C"), (39, "D"),
                                 (20, "D"), (19, "F"), (0, "F")])
def test_grade_bands(s, g):
    assert score.grade_of(s) == g
