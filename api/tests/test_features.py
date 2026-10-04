"""Address -> features. Real Ann Arbor addresses need the footprint cache (scripts/fetch_footprints.py);
the first run also calls the Census geocoder / Census Reporter once, later runs are offline."""

import json
from collections import Counter

import httpx
import numpy as np
import shapely
from shapely.geometry import Point, box, mapping
import pytest
from fastapi.testclient import TestClient

from app.geo import FOOTPRINTS_PATH
from app.geo import features, footprints, geocode as geocoder
from app.geo.features import MF5, MF24, SFA, SFD, building_type, get_features, snap_stories, townhouse_row, vintage
from app.geo.footprints import street_key
from app.main import app

VINTAGES = {"<1940", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s"}  # ResStock 2024.2
needs_data = pytest.mark.skipif(not FOOTPRINTS_PATH.exists(), reason="run: uv run python scripts/fetch_footprints.py")


def test_vintage_bins():
    assert vintage(1880) == "<1940"
    assert vintage(1939) == "<1940"  # ACS codes "1939 or earlier" as 1939
    assert vintage(1940) == "1940s"
    assert vintage(1964) == "1960s"
    assert vintage(2019) == "2010s"
    assert vintage(2024) == "2010s"  # ResStock 2024.2 has no 2020s bin
    assert {vintage(y) for y in range(1900, 2030)} == VINTAGES


def test_building_type_mapping():
    assert building_type("Residential", 1) == SFD
    assert building_type("Residential", 0) == SFD
    assert building_type("Residential", 2) == MF24
    assert building_type("Residential", 4) == MF24
    assert building_type("Residential", 5) == MF5
    assert building_type("Commercial", 12) == MF5  # apartments above shops
    assert building_type("Public", 0) is None
    assert building_type("Office", 1) is None
    assert building_type("Office", 5) is None
    assert building_type("Public", 12) is None


def test_stories_snap_to_resstock_categories():
    raw = (1, 3, 15, 16, 17, 18, 20, 21, 26, 28, 29, 40)
    assert [snap_stories(n) for n in raw] == [1, 3, 15, 15, 15, 20, 20, 21, 21, 21, 35, 35]  # 28: tie 21/35 -> 21


def test_townhouse_rule():
    row = ["2841 HARDWICK RD", "2843 HARDWICK RD"]
    assert townhouse_row("Residential", row, 0, 3)
    assert not townhouse_row("Residential", row, 0, 4)  # too tall for a townhouse
    assert not townhouse_row("Commercial", row, 0, 2)  # shopfronts with apartments above
    assert not townhouse_row("Residential", row, 2, 2)  # street line has UNIT rows
    assert not townhouse_row("Residential", ["912 MARY ST", "912 1/2 MARY ST"], 0, 2)  # shared house number
    assert not townhouse_row("Residential", ["912 MARY ST UNIT 1", "912 MARY ST UNIT 2"], 0, 3)
    assert not townhouse_row("Residential", ["1514 MORTON AVE"], 0, 2)


def test_street_key():
    assert street_key("1300 South University Avenue Apt 9, Ann Arbor, MI") == "1300 S UNIVERSITY AVE"
    assert street_key("912 Mary St. #3") == "912 MARY ST"
    assert street_key("500 S STATE ST, ANN ARBOR, MI, 48109") == "500 S STATE ST"


@needs_data
def test_single_family_house():
    f = get_features("1514 Morton Ave, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == SFD
    assert f["in.geometry_stories"] == "2"
    assert not f["is_multi_unit"] and f["est_units"] == 1
    assert 1500 < f["in.sqft"] == f["building_sqft"] < 4000
    assert f["in.vintage"] in VINTAGES and f["in.county_name"] == "Washtenaw County"
    assert f["footprint_geojson"]["type"] == "Polygon"


@needs_data
def test_two_to_four_unit():
    f = get_features("912 Mary St, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == MF24
    assert f["in.geometry_stories"] == "3"
    assert f["est_units"] == 4 and f["is_multi_unit"] and f["sqft_estimated"]
    assert 4000 < f["building_sqft"] < 15000
    assert f["in.sqft"] == round(f["building_sqft"] / 4)


@needs_data
def test_large_apartment_near_campus():
    f = get_features("1300 S University Ave, Ann Arbor, MI")  # Landmark Apartments
    assert f["in.geometry_building_type_recs"] == MF5
    assert f["in.geometry_stories"] == "13"
    assert f["est_units"] > 100 and f["building_sqft"] > 100_000
    assert 400 < f["in.sqft"] < 3000


@needs_data
def test_tower_with_units_outside_footprint_or_vacant_type():
    f = get_features("721 S Forest Ave, Ann Arbor, MI")  # Verve: its 218 UNIT rows are TYPE "Vacant"
    assert f["in.geometry_building_type_recs"] == MF5 and f["est_units"] > 100


@needs_data
def test_implausible_unit_sqft_falls_back_to_median():
    f = get_features("405 S Main St, Ann Arbor, MI")  # The Standard: unit points in a 2-story podium
    assert f["in.sqft"] >= 322 and f["warnings"] and f["sqft_estimated"]


@needs_data
def test_caller_overrides():
    f = get_features("912 Mary St, Ann Arbor, MI", unit_sqft=850, year_built=2015)
    assert f["in.sqft"] == 850 and not f["sqft_estimated"]
    assert f["in.vintage"] == "2010s" and f["year_built_source"].startswith("given")


@needs_data
def test_non_residential_building():
    f = get_features("500 S State St, Ann Arbor, MI")  # UM LSA Building
    assert f["in.geometry_building_type_recs"] is None and f["in.sqft"] is None and f["warnings"]


@needs_data
def test_works_offline_after_first_fetch(monkeypatch):
    get_features("1514 Morton Ave, Ann Arbor, MI")  # warm caches

    def no_network(*a, **k):
        raise AssertionError("network call made")

    monkeypatch.setattr(httpx, "get", no_network)
    assert get_features("1514 Morton Ave, Ann Arbor, MI")["est_units"] == 1


@needs_data
def test_api_endpoints():
    c = TestClient(app)
    health = c.get("/health").json()
    assert health["status"] in {"ok", "degraded"}
    assert isinstance(health["model"]["available"], bool)
    r = c.get("/debug/features", params={"address": "912 Mary St, Ann Arbor, MI"})
    assert r.status_code == 200 and r.json()["est_units"] == 4
    assert c.get("/debug/features", params={"address": "123 Fake Street, Nowhere, MI"}).status_code == 404


@needs_data
@pytest.mark.parametrize("street", ["2843 Hardwick Rd", "2877 Rayfield Ave",  # North Oaks townhomes
                                    "3422 Burbank Dr", "2685 Arrowwood Trl",  # Chapel Hill condos, Arrowwood co-op
                                    "506 Packard St"])  # side-by-side duplex (RECS: SFA)
def test_townhouses_are_single_family_attached(street):
    f = get_features(f"{street}, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == SFA and f["est_units"] >= 2
    assert f["sources"]["in.geometry_building_type_recs"].startswith("townhouse rule")
    assert 800 < f["in.sqft"] < 4000 and f["sqft_estimated"]


@needs_data
@pytest.mark.parametrize("street,btype", [("912 Mary St", MF24), ("2901 Northbrook Pl", MF5),  # apartments
                                          ("1514 Morton Ave", SFD), ("2121 Vinewood Blvd", SFD)])  # detached
def test_townhouse_rule_leaves_apartments_and_houses_alone(street, btype):
    f = get_features(f"{street}, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == btype
    assert f["sources"]["in.geometry_building_type_recs"].startswith("unit-count rule")


@needs_data
def test_tall_tower_stories_snapped():
    f = get_features("555 E William St, Ann Arbor, MI")  # Tower Plaza, 26 stories
    assert f["stories_raw"] == 26 and f["in.geometry_stories"] == "21"
    assert "snapped" in f["sources"]["in.geometry_stories"] and f["sources"]["stories_raw"]


@needs_data
@pytest.mark.parametrize("street,btype", [("1500 Gilbert Ct", MF5),  # Escher Co-op, 10 addresses
                                          ("1205 Hill St", MF24)])  # AEPhi sorority, 2 addresses
def test_townhouse_guard_big_floor_area_per_address(street, btype):
    f = get_features(f"{street}, Ann Arbor, MI")
    src = f["sources"]["in.geometry_building_type_recs"]
    assert f["in.geometry_building_type_recs"] == btype
    assert src.startswith("unit-count rule") and "townhouse rule skipped by guard" in src


@needs_data
@pytest.mark.parametrize("street", ["2500 Packard St", "3600 Green Ct", "1300 Victors Way"])
def test_office_addresses_are_not_homes(street):
    f = get_features(f"{street}, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] is None
    assert f["in.sqft"] is None and f["warnings"]
    assert "Office" in f["sources"]["in.geometry_building_type_recs"]
    # A supplied size cannot turn a known office into a home.
    assert get_features(f"{street}, Ann Arbor, MI", unit_sqft=850)["in.sqft"] is None


@needs_data
def test_633_church_residential_oversize_is_estimated():
    f = get_features("633 Church St, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == SFD  # city marks this Residential, not Office
    assert f["in.sqft"] == 1698 and f["sqft_estimated"]
    assert "median" in f["sources"]["in.sqft"]
    assert get_features("633 Church St, Ann Arbor, MI", unit_sqft=2838)["in.sqft"] == 2838


@needs_data
@pytest.mark.parametrize("street,btype", [("2843 Hardwick Rd", SFA), ("912 Mary St", MF24)])
def test_gross_floor_area_requires_unit_size(street, btype):
    f = get_features(f"{street}, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == btype and f["sqft_estimated"]
    assert any("garages" in warning and "conditioned" in warning for warning in f["warnings"])
    known = get_features(f"{street}, Ann Arbor, MI", unit_sqft=1000)
    assert known["in.sqft"] == 1000 and not known["sqft_estimated"]


@needs_data
def test_1780_broadway_uses_city_point_and_all_units():
    f = get_features("1780 Broadway St, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == MF5
    assert f["est_units"] == 105 and f["in.sqft"] == 1263
    assert "OBJECTID 17797" in f["sources"]["footprint"]
    assert f["sources"]["lat_lon"].startswith("City of Ann Arbor")


@needs_data
def test_2865_bolgos_is_absent_from_both_sources():
    # No 2865 BOLGOS CIR in the 65,138-point city cache (2026-10-04). Do not guess
    # 3265 Bolgos Cir or 2865 Barclay Way; neither is the requested address.
    assert footprints.city_address("2865 Bolgos Cir, Ann Arbor, MI") is None
    with pytest.raises(LookupError, match="Census geocoder and city MailingAddress"):
        get_features("2865 Bolgos Cir, Ann Arbor, MI")


@needs_data
def test_ashley_mews_replaces_displaced_census_point_and_block_group():
    f = get_features("143 Ashley Mews, Ann Arbor, MI")
    assert f["matched_address"].startswith("143 ASHLEY MEWS,")
    assert "OBJECTID 34711" in f["sources"]["footprint"]
    assert f["in.geometry_building_type_recs"] == SFA
    assert f["block_group_geoid"] == "261614005006"  # displaced S Ashley was 261614001001


@pytest.mark.parametrize("btype,units,area_sqft,expected", [(SFD, 1, 9000, 1698), (MF5, 5, 40000, 854),
                                                          (MF24, 4, 400, 854)])
def test_implausible_residential_sizes_fall_back_offline(monkeypatch, btype, units, area_sqft, expected):
    b = footprints.Building({"OBJECTID": 1, "STORIES": 1, "Struc_Type": "Residential", "PackedPin": None},
                            mapping(box(-83.75, 42.27, -83.74, 42.28)), area_sqft / features.SQFT_PER_M2,
                            [f"1 MAIN ST UNIT {i}" for i in range(units)], "fixture", 0, "1 MAIN ST", units)
    monkeypatch.setattr(features, "find_building", lambda *a, **k: b)
    monkeypatch.setattr(features, "geocode", lambda a: {"lon": -83.75, "lat": 42.27,
                                                        "matched_address": a, "block_geoid": None})
    f = get_features("1 Main St", year_built=1960)
    assert f["in.geometry_building_type_recs"] == btype
    assert f["in.sqft"] == expected and f["sqft_estimated"]


@pytest.mark.parametrize("struc_type,packed_pin", [("Commercial", None), ("Residential", "Garage"),
                                                  ("Residential", "Carport")])
def test_non_home_use_and_implausible_commercial_area(monkeypatch, struc_type, packed_pin):
    b = footprints.Building({"OBJECTID": 1, "STORIES": 1, "Struc_Type": struc_type, "PackedPin": packed_pin},
                            mapping(box(-83.75, 42.27, -83.74, 42.28)), 10000,
                            ["1 MAIN ST"], "fixture", 0, "1 MAIN ST", 0)
    monkeypatch.setattr(features, "find_building", lambda *a, **k: b)
    monkeypatch.setattr(features, "geocode", lambda a: {"lon": -83.75, "lat": 42.27,
                                                        "matched_address": a, "block_geoid": None})
    f = get_features("1 Main St", year_built=1960)
    assert f["in.geometry_building_type_recs"] is None and f["in.sqft"] is None


@pytest.fixture
def local_city_index(monkeypatch, tmp_path):
    # Metre-based fixture: a nearer unrelated building and a requested-address building 70 m away.
    origin = footprints._TO_UTM.transform(-83.75, 42.28)
    x, y = origin
    polygons = np.array([box(x + 30, y - 5, x + 40, y + 5), box(x + 70, y - 5, x + 80, y + 5)])
    points = np.array([Point(x + 35, y), Point(x + 75, y)])
    ix = footprints._Index([{"OBJECTID": 1}, {"OBJECTID": 2}], polygons, polygons, shapely.STRtree(polygons),
                           np.array(["2 MAIN ST", "1 MAIN ST UNIT 1"]), np.array([True, True]), points,
                           points,  # addr_wgs (city-layer); unused by these lookups
                           shapely.STRtree(points), {"1 MAIN ST": 1}, Counter({"1 MAIN ST": 1}), 11.1, 1.4)
    monkeypatch.setattr(footprints, "_index", lambda: ix)
    cache = tmp_path / "city.geojson"
    cache.write_text("{}")
    monkeypatch.setattr(footprints, "FOOTPRINTS_PATH", cache)
    monkeypatch.setattr(footprints, "ADDRESSES_PATH", cache)
    return ix


def test_city_point_requires_exact_address_and_locality(local_city_index):
    assert footprints.city_address("1 Main St, Ann Arbor, MI") is not None
    assert footprints.city_address("1 Main St, Detroit, MI") is None
    assert footprints.city_address("1 Main St, Ann Arbor, CA") is None
    assert footprints.city_address("1 Main St, Ann Arbor, MI 48104") is not None
    assert footprints.city_address("3 Main St, Ann Arbor, MI") is None


def test_wider_search_only_accepts_matching_address(local_city_index):
    local_city_index.addr_by_street.clear()  # exercise fallback without a city point
    b = footprints.find_building(-83.75, 42.28, ["1 Main St, Ann Arbor, MI"])
    assert b.props["OBJECTID"] == 2 and b.distance_m == 70
    assert "expanded search" in b.match
    with pytest.raises(LookupError, match="no matching-address footprint"):
        footprints.find_building(-83.75, 42.28, ["3 Main St, Ann Arbor, MI"])


@pytest.mark.parametrize("census_hit", [None, {"matched_address": "1 WRONG ST", "lon": -83.76,
                                             "lat": 42.29, "block_geoid": "wrong"}])
def test_city_geocoder_fallback_and_offline_cache(monkeypatch, tmp_path, local_city_index, census_hit):
    address = "1 Main St, Ann Arbor, MI"
    cache = tmp_path / "geocode.json"
    cache.write_text(json.dumps({geocoder._key(address): census_hit}))
    monkeypatch.setattr(geocoder, "CACHE_PATH", cache)
    calls = []

    def coordinate_response(url, **kwargs):
        calls.append((url, kwargs))
        assert url.endswith("/coordinates")
        return httpx.Response(200, request=httpx.Request("GET", url),
                              json={"result": {"geographies": {"2020 Census Blocks": [{"GEOID": "261614005006000"}]}}})

    monkeypatch.setattr(httpx, "get", coordinate_response)
    hit = geocoder.geocode(address)
    assert hit["matched_address"] == "1 MAIN ST, ANN ARBOR, MI"
    assert hit["block_geoid"] == "261614005006000" and len(calls) == 1
    assert geocoder.geocode(address) == hit and len(calls) == 1


def test_city_point_survives_census_outage_without_wrong_block(monkeypatch, tmp_path, local_city_index):
    monkeypatch.setattr(geocoder, "CACHE_PATH", tmp_path / "empty.json")

    def unavailable(*a, **k):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "get", unavailable)
    hit = geocoder.geocode("1 Main St, Ann Arbor, MI")
    assert hit["block_geoid"] is None and hit["source"].startswith("City of Ann Arbor")
    with pytest.raises(httpx.ConnectError):
        geocoder.geocode("1 Main St, Detroit, MI")
