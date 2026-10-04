"""Map contract, ordered model prefixes, GIS identity, and cached TIGERweb fetches."""
from copy import deepcopy
import json
from types import SimpleNamespace

import httpx
import numpy as np
import pytest
import shapely
from fastapi import HTTPException
from fastapi.testclient import TestClient
from shapely.geometry import Point, box, mapping

from app import estimate, map_widget as mw
from app.geo.footprints import _project
from app.main import app

client = TestClient(app)


def model_result(params):
    total = 1000 - (200 if params.get("heating_fuel") == "gas" else 0) - (100 if params.get("window_panes") == "2" else 0)
    return {"annual": {"total_usd": total, "cooling_usd": 100, "electric_kwh": 500},
            "seasons": [{"season": season, "total_usd": total / 4, "cooling": {"usd": 25, "electric_kwh": 10}}
                        for season in ("winter", "spring", "summer", "fall")],
            "model_detail": {"heating_fuel": params.get("heating_fuel", "electric")}, "method": "resstock",
            "accuracy": {"seasonal_gas_median_abs_error": {"all": .299}, "basis": "held-out meters"},
            "building": {"gfa_ft2": 8000, "gfa_source": "calibrated footprint area", "year_built": 1965,
                         "year_built_source": "ACS B25037 block group", "heating_fuel_shares": {"gas_share": .4, "electric_share": .6},
                         "heating_fuel_source": "ACS B25040"}, "weather_source": "PRISM normals"}


def index():
    wgs = np.array([box(-83.7422, 42.2705, -83.742, 42.2707), box(-83.7418, 42.2705, -83.7416, 42.2707)])
    utm = _project(wgs)
    props = [{"OBJECTID": 1317, "ABG_BLD_HG": 23.7, "STORIES": 3, "Struc_Type": "Residential"},
             {"OBJECTID": 6, "ABG_BLD_HG": 22, "STORIES": 3, "Struc_Type": "Residential"}]
    return SimpleNamespace(wgs=wgs, utm=utm, tree=shapely.STRtree(utm), props=props, ft_offset=1.4, ft_per_story=11.1)


@pytest.fixture(autouse=True)
def caches():
    mw._model_step.cache_clear()
    mw._block_group.cache_clear()
    mw._city_data.cache_clear()
    yield
    mw._model_step.cache_clear()


@pytest.fixture
def env(monkeypatch):
    ix = index()
    rows = [{"id": p["OBJECTID"], "address": "912 Mary St" if n == 0 else "914 Mary St",
             "center": list(g.centroid.coords[0]), "height_ft": p["ABG_BLD_HG"], "stories": p["STORIES"],
             "residential": True, "footprint_sqft": round(u.area * mw.SQFT_PER_M2)}
            for n, (p, g, u) in enumerate(zip(ix.props, ix.wgs, ix.utm))]
    # Original geocode and model point in other roof: the saved session footprint still wins.
    s = {"session_id": "mary", "model_params": {"lat": 42.2706, "lon": -83.7417, "unit_sqft": 850,
                                               "building_type": "Multi-Family with 2 - 4 Units", "block_group": "261614005003"},
         "building": {"address": "912 MARY ST, ANN ARBOR, MI", "lat": 42.2706, "lon": -83.7417,
                      "footprint_geojson": mapping(ix.wgs[0]), "sqft_estimated": True,
                      "type": "Multi-Family with 2 - 4 Units"}, "answers": {}}
    calls = []
    def hc(params):
        calls.append(deepcopy(params))
        return model_result(params)
    monkeypatch.setattr(mw.sessions, "get", lambda key: deepcopy(s) if key == "mary" else None)
    monkeypatch.setattr(estimate, "_hc", hc)
    monkeypatch.setattr(mw, "_city_data", lambda: (ix, rows, [-83.8, 42.2, -83.6, 42.4]))
    monkeypatch.setattr(mw, "_block_group", lambda geoid: mapping(box(-83.75, 42.26, -83.73, 42.28)))
    return s, calls, ix


def test_contract_and_objectid_from_session_footprint(env):
    r = client.get("/map/mary")
    assert r.status_code == 200, r.text
    x = r.json()
    assert set(x) == {"address", "center", "city_bounds", "building", "buildings_url", "similar", "block_group",
                      "lookalikes", "steps", "accuracy_basis", "sources"}
    assert x["building"]["id"] == 1317 and x["building"]["height_ft"] == 23.7
    assert x["building"]["unit_sqft"] == 850 and "estimate" in x["building"]["unit_sqft_source"]
    assert x["buildings_url"] == "/data/a2-buildings.geojson"
    assert x["block_group"]["geoid"] == "261614005003" and x["block_group"]["gas_heat_share"] == .4
    assert x["similar"]["items"][0]["id"] == 6 and "not ranked" in x["similar"]["rule"]
    assert x["steps"][0]["id"] == "public_record" and x["steps"][0]["question"] is None
    assert x["steps"][0]["estimate"] == {"annual_usd": 1000, "seasons": dict.fromkeys(estimate.SEASONS, 250),
                                         "heating_fuel": "electric", "typical_error": .299, "method": "resstock"}
    assert x["steps"][0]["lookalikes"] == {"count": 0, "usd_yr": [], "p10": None, "p50": None, "p90": None}
    assert x["lookalikes"]["pool_size"] == 0 and "pending P1" in x["lookalikes"]["rule"]
    assert all(source["url"].startswith("https://") for source in x["sources"])


def test_answer_order_cumulative_steps_and_prefix_cache(env):
    s, calls, _ = env
    s["model_params"]["heating_fuel"] = "gas"  # baseline strips answers even if left in params
    s["answers"] = {"window_panes": "2", "heating_fuel": "gas"}
    x = client.get("/map/mary").json()
    assert [st["id"] for st in x["steps"]] == ["public_record", "window_panes", "heating_fuel"]
    assert [st["estimate"]["annual_usd"] for st in x["steps"]] == [1000, 900, 700]
    assert [st["answer_label"] for st in x["steps"]] == [None, "Double-pane", "Gas"]
    assert "heating_fuel" not in calls[0] and "window_panes" not in calls[0]
    assert calls[1]["window_panes"] == "2" and "heating_fuel" not in calls[1]
    assert calls[2]["window_panes"] == "2" and calls[2]["heating_fuel"] == "gas"
    assert all(c["unit_sqft"] == 850 and c["block_group"] == "261614005003" for c in calls)
    assert client.get("/map/mary").json() == x and len(calls) == 3
    s["answers"]["floor_level"] = "2"
    assert len(client.get("/map/mary").json()["steps"]) == 4 and len(calls) == 4
    s["answers"]["window_panes"] = "3"
    client.get("/map/mary")
    assert len(calls) == 7  # only changed prefix and suffixes rerun


def test_skips_and_no_ac_match_answer_endpoint(env):
    s, calls, _ = env
    s["answers"] = {"window_panes": None, "cooling_code": "0"}
    x = client.get("/map/mary").json()
    assert x["steps"][1]["answer_label"] == "Skipped" and x["steps"][1]["estimate"]["annual_usd"] == 1000
    assert "window_panes" not in calls[1]
    assert x["steps"][2]["answer_label"] == "No AC" and x["steps"][2]["estimate"]["annual_usd"] == 900
    assert list(x["steps"][2]["estimate"]["seasons"].values()) == [225] * 4


def test_metered_building_without_gfa_source_or_acs_never_invents_block_stats(env, monkeypatch):
    def metered(params):
        r = model_result(params)
        r["method"] = "metered"
        r["building"].pop("gfa_source")
        r["building"].pop("heating_fuel_shares")
        r["building"]["year_built_source"] = "Ann Arbor benchmarking"
        return r
    monkeypatch.setattr(estimate, "_hc", metered)
    r = client.get("/map/mary")
    assert r.status_code == 200, r.text
    x = r.json()
    assert "benchmarking" in x["building"]["floor_area_source"]
    assert x["block_group"]["median_year_built"] is None
    assert "unavailable" in x["block_group"]["median_year_built_source"]
    assert x["block_group"]["gas_heat_share"] is None


def test_expired_session_never_calls_model(env):
    r = client.get("/map/expired")
    assert r.status_code == 404
    assert r.json() == {"detail": {"code": "not_found", "message": "That session expired. Send the listing again."}}
    assert not env[1]


@pytest.mark.parametrize("error", [httpx.ConnectError("down"), HTTPException(422, {"code": "not_found"}),
                                   HTTPException(503, {"code": "model_unavailable"})])
def test_model_failure_is_friendly_503(env, monkeypatch, error):
    def broken(params):
        raise error
    monkeypatch.setattr(estimate, "_hc", broken)
    r = client.get("/map/mary")
    assert r.status_code == 503 and r.json()["detail"]["code"] == "model_unavailable"
    assert mw._model_step.cache_info().currsize == 0


def test_tiger_geometry_cached_on_disk_and_in_memory(tmp_path, monkeypatch):
    monkeypatch.setattr(mw, "BG_CACHE", tmp_path)
    calls = []
    geometry = mapping(box(-83.75, 42.26, -83.73, 42.28))
    def get(url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, json={"features": [{"geometry": geometry}]}, request=httpx.Request("GET", url))
    monkeypatch.setattr(mw.httpx, "get", get)
    first = mw._block_group("261614005003")
    assert mw._block_group("261614005003") == first
    mw._block_group.cache_clear()
    assert mw._block_group("261614005003") == first and len(calls) == 1
    assert calls[0][1]["params"]["where"] == "GEOID='261614005003'"
    assert (tmp_path / "261614005003.geojson").exists()


@pytest.mark.parametrize("body", [{"features": []}, {"error": {"message": "down"}}])
def test_tiger_failure_not_cached(tmp_path, monkeypatch, body):
    monkeypatch.setattr(mw, "BG_CACHE", tmp_path)
    monkeypatch.setattr(mw.httpx, "get", lambda url, **kw: httpx.Response(200, json=body, request=httpx.Request("GET", url)))
    with pytest.raises(HTTPException) as err:
        mw._block_group("261614005003")
    assert err.value.status_code == 503 and not list(tmp_path.iterdir())


def test_p3_labels_containing_then_nearest_all_types_and_most_common(tmp_path, monkeypatch):
    ix = SimpleNamespace(wgs=np.array([box(0, 0, .0001, .0001), box(.0003, 0, .0004, .0001)]))
    rows = [(Point(.00005, .00005), "912 MARY ST UNIT 1", "General Mailing"),
            (Point(.00006, .00006), "912 MARY ST UNIT 2", "Vacant"),
            (Point(.0004, .00005), "914 MARY ST", "University"),  # boundary nearest, distance zero
            (Point(.00049, .00005), "914 MARY ST APT 1", "Vacant"),  # snap <1.1e-4 degrees
            (Point(.00052, .00005), "999 FAR ST", "General Mailing")]
    path = tmp_path / "addresses.geojson"
    path.write_text(json.dumps({"features": [{"geometry": mapping(point), "properties": {"PROPSTREET": street, "TYPE": kind}}
                                             for point, street, kind in rows]}))
    monkeypatch.setattr(mw, "ADDRESSES_PATH", path)
    assert mw._mailing_labels(ix) == {0: "912 Mary St", 1: "914 Mary St"}


def test_similar_repeatable_and_excludes_selected_or_outside_size(env):
    _, rows, _ = mw._city_data()
    large = {**rows[1], "id": 100, "footprint_sqft": rows[0]["footprint_sqft"] * 2}
    assert mw._similar([*rows, large], rows[0]) == mw._similar([*rows, large], rows[0])
    assert [b["id"] for b in mw._similar([*rows, large], rows[0])["items"]] == [6]
