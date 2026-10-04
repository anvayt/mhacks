"""City score math, endpoint contract, naming rules, and aggregate privacy."""
import gzip
import json
import httpx
import pytest
from fastapi.testclient import TestClient
from app import city
from app.main import app
from scripts import score_city

@pytest.mark.parametrize("score,expected", [(100,"A"),(80,"A"),(79.999,"B"),(60,"B"),(59.999,"C"),(40,"C"),(39.999,"D"),(20,"D"),(19.999,"F"),(0,"F")])
def test_grade_boundaries(score, expected):
    assert city.grade(score) == expected

def test_same_type_midpoint_ties_and_median():
    rows = [{"type":"house", "sqft":1000, "annual_usd":cost} for cost in (1000,2000,2000,3000)]
    rows.append({"type":"apartment", "sqft":500, "annual_usd":5000})
    scored = city.score_rows(rows)
    assert [r["score"] for r in scored] == [87.5,50,50,12.5,50]
    assert [r["grade"] for r in scored] == ["A","C","C","F","C"]
    assert [r["excess_usd_per_sqft"] for r in scored] == [-1,0,0,1,0]
    assert "score" not in rows[0]

@pytest.mark.parametrize("sqft,cost", [(0,100),(-1,100),(100,-1),(float("nan"),100),(100,float("inf"))])
def test_invalid_model_values(sqft, cost):
    with pytest.raises(ValueError):
        city.score_rows([{"type":"house", "sqft":sqft, "annual_usd":cost}])

@pytest.fixture
def table(tmp_path, monkeypatch):
    rows = []
    for i in range(12):
        rows.append({"footprint_id":i+1, "type":"house", "sqft":1000, "annual_usd":1000+100*i,
                     "heating_usd":0 if i == 0 else 700,
                     "block_group":"261614001001" if i < 5 else ("261614001002" if i < 9 else "261614002001"),
                     "benchmark_id":"no-heat" if i == 0 else ("public-home" if i in (1,2) else ""),
                     "benchmark_name":"Missing tenant heat" if i == 0 else ("Public apartments" if i in (1,2) else "")})
    path = tmp_path / "scores.csv"
    score_city.write_table(rows, path)
    geometry = {"type":"Polygon", "coordinates":[[[-83.7,42.2],[-83.69,42.2],[-83.69,42.21],[-83.7,42.2]]]}
    footprints = tmp_path / "footprints.json"
    footprints.write_text(json.dumps({"features":[{"properties":{"OBJECTID":i+1, "Bldg_Name":"Private landlord"}, "geometry":geometry} for i in range(12)]}))
    monkeypatch.setattr(city,"TABLE_PATH",path)
    monkeypatch.setattr(city,"FOOTPRINTS_PATH",footprints)
    for cached in (city._table,city._city_payload,city._leaderboard):
        cached.cache_clear()
    yield path,footprints
    for cached in (city._table,city._city_payload,city._leaderboard):
        cached.cache_clear()

def test_all_geometries_cached_gzipped_without_names(table):
    client = TestClient(app)
    response = client.get("/city",headers={"Accept-Encoding":"gzip"})
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
    assert "Accept-Encoding" in response.headers["vary"]
    body = response.json()
    assert body["type"] == "FeatureCollection" and len(body["features"]) == 12
    assert body["features"][0]["geometry"]["type"] == "Polygon"
    assert set(body["features"][0]["properties"]) == {"score","grade","excess_usd_per_sqft","type"}
    assert "Private landlord" not in response.text and "Public apartments" not in response.text
    raw,compressed = city._city_payload()
    assert gzip.decompress(compressed) == raw
    table[1].unlink()
    assert client.get("/city").status_code == 200
    identity = client.get("/city",headers={"Accept-Encoding":"gzip;q=0, identity"})
    assert "content-encoding" not in identity.headers and identity.json() == body

def test_city_costs_returns_copy(table):
    assert city.city_costs("missing") == []
    values = city.city_costs("house")
    assert len(values) == 12 and values[0] == 1
    values.clear()
    assert len(city.city_costs("house")) == 12

def test_only_public_positive_heat_named_small_groups_suppressed(table):
    body = TestClient(app).get("/leaderboard").json()
    assert len(body["best"]) == 1
    assert body["best"][0]["name"] == "Public apartments"
    assert body["best"][0]["building_count"] == 2
    assert body["best"][0]["source"] == city.BENCHMARK_SOURCE
    assert len(body["worst_blocks"]) == 1
    block = body["worst_blocks"][0]
    assert block["geoid"] == "261614001001" and block["building_count"] == 5
    assert block["area_type"] == "block_group" and "name" not in block and "address" not in block

def test_neighborhood_uses_census_tract_and_minimum_five(table):
    response = TestClient(app).get("/leaderboard?scope=neighborhood")
    assert response.status_code == 200
    groups = response.json()["worst_blocks"]
    assert len(groups) == 1 and groups[0]["geoid"] == "26161400100"
    assert groups[0]["building_count"] == 9 and groups[0]["area_type"] == "census_tract"

def test_bad_scope_and_missing_data_errors(table):
    client = TestClient(app)
    response = client.get("/leaderboard?scope=street")
    assert response.status_code == 422 and response.json()["detail"]["code"] == "bad_scope"
    table[0].unlink()
    for endpoint in ("/city","/leaderboard"):
        response = client.get(endpoint)
        assert response.status_code == 503
        assert set(response.json()["detail"]) == {"code","message"}

def test_model_call_inputs_and_annual_p50():
    row = {"footprint_id":12,"type":"house","sqft":1000,"lat":42.2,"lon":-83.7,"block_group":"261614001001"}
    def handler(request):
        assert request.url.path == "/hc/estimate"
        assert dict(request.url.params) == {"lat":"42.2","lon":"-83.7","unit_sqft":"1000","building_type":"house","block_group":"261614001001"}
        return httpx.Response(200,json={"annual":{"total_usd":1001,"heating_usd":900,"cooling_usd":100}})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = score_city.score_one(client,row,"http://model")
    assert result["annual_usd"] == 1001 and result["heating_usd"] == 900

def test_resume_recovers_truncated_final_record(tmp_path):
    path = tmp_path / "checkpoint.jsonl"
    path.write_text('{"footprint_id":1,"annual_usd":123}\n{"footprint_')
    assert score_city.read_checkpoint(path)[1]["annual_usd"] == 123
    with path.open("a") as stream:
        stream.write('{"footprint_id":2}\n')
    assert set(score_city.read_checkpoint(path)) == {1,2}
    path.write_text('broken\n{"footprint_id":2}\n')
    with pytest.raises(json.JSONDecodeError):
        score_city.read_checkpoint(path)

@pytest.mark.parametrize("use,accessory,sqft,addresses,expected", [
    ("Office",None,2000,["10 MAIN ST"],None),
    ("Public",None,2000,["10 MAIN ST"],None),
    ("Residential"," Garage ",2000,["10 MAIN ST"],None),
    ("Residential","Carport",2000,[],None),
    ("Residential","Canopy",2000,[],None),
    ("Residential","Parking Deck",2000,[],None),
    ("Commercial",None,16000,["10 MAIN ST"],None),
    ("Commercial",None,2000,["10 MAIN ST"],2000),
    ("Residential",None,8036,["10 MAIN ST"],1698),
    ("Residential",None,200,["10 MAIN ST"],1698),
    ("Residential",None,400,["10 MAIN ST","12 MAIN ST"],1207),
    ("Residential",None,20000,["10 MAIN ST UNIT 1","10 MAIN ST UNIT 2"],854),
])
def test_batch_residential_rules_match_lookup_fixes(monkeypatch, use, accessory, sqft, addresses, expected):
    import numpy as np
    from collections import Counter
    from types import SimpleNamespace
    from shapely.geometry import box
    ix = SimpleNamespace(props=[{"OBJECTID":1,"Struc_Type":use,"PackedPin":accessory,"STORIES":1}],
                         addr_tree=SimpleNamespace(query=lambda *args,**kwargs: []), addr_street=np.array(addresses),
                         units_by_street=Counter(), utm=[SimpleNamespace(area=sqft/score_city.geo.SQFT_PER_M2)],
                         wgs=[box(-83.7,42.2,-83.69,42.21)])
    monkeypatch.setattr(score_city,"_addresses_in",lambda index,i: addresses)
    row = score_city.footprint_inputs(ix,0)
    if expected is None:
        assert row is None
    else:
        assert row["sqft"] == expected


@pytest.mark.parametrize("fid", [1526,1564,27464,31174,32339,15669,52651])
def test_city_all_type_unit_rows_keep_known_apartments_multifamily(fid):
    from app.geo import FOOTPRINTS_PATH, ADDRESSES_PATH
    if not FOOTPRINTS_PATH.exists() or not ADDRESSES_PATH.exists():
        pytest.skip("run scripts/fetch_footprints.py")
    ix = score_city._index()
    i = next(i for i,p in enumerate(ix.props) if p["OBJECTID"] == fid)
    row = score_city.footprint_inputs(ix,i)
    assert row["type"] == score_city.geo.MF5


def test_city_courtyards_units_outside_footprint_use_same_25m_assignment():
    from app.geo import FOOTPRINTS_PATH, ADDRESSES_PATH
    if not FOOTPRINTS_PATH.exists() or not ADDRESSES_PATH.exists():
        pytest.skip("run scripts/fetch_footprints.py")
    ix = score_city._index()
    i = next(i for i,p in enumerate(ix.props) if p["OBJECTID"] == 17797)
    unit_counts = score_city.associated_units(ix)
    row = score_city.footprint_inputs(ix,i,unit_counts.get(i,0))
    assert (row["type"],row["sqft"]) == (score_city.geo.MF5,1263)


def test_slow_benchmark_stops_and_next_run_resumes_exact_inputs(tmp_path, monkeypatch):
    from types import SimpleNamespace
    rows = [{"footprint_id":i, "type":"house", "sqft":1000, "lat":42.2, "lon":-83.7,
             "block_group":"261614001001", "benchmark_id":"", "benchmark_name":""} for i in range(202)]
    calls = []
    monkeypatch.setattr(score_city,"candidates",lambda: rows)
    def model(client,row,url):
        calls.append(row["footprint_id"])
        return {**row,"annual_usd":row["sqft"],"heating_usd":900}
    monkeypatch.setattr(score_city,"score_one",model)
    ticks = iter([0,1,6001,6002])
    monkeypatch.setattr(score_city,"time",SimpleNamespace(monotonic=lambda: next(ticks)))
    output,checkpoint = tmp_path/"scores.csv",tmp_path/"checkpoint.jsonl"
    args = ["--output",str(output),"--checkpoint",str(checkpoint)]
    assert score_city.main(args) == 2
    report = json.loads(output.with_suffix(".json").read_text())
    assert report["scored"] == 201 and not report["complete"]
    assert report["stopped_after_benchmark"] and len(calls) == 201
    ticks = iter([0,1,2,3])
    assert score_city.main(args) == 0
    report = json.loads(output.with_suffix(".json").read_text())
    assert report["scored"] == 202 and report["complete"] and len(calls) == 202
    rows[0]["sqft"] = 2000
    ticks = iter([0,1,2,3])
    assert score_city.main(args) == 0
    assert len(calls) == 203 and calls[-1] == 0
    assert score_city.read_checkpoint(checkpoint)[0]["annual_usd"] == 2000
