"""Address -> features. Real Ann Arbor addresses need the footprint cache (scripts/fetch_footprints.py);
the first run also calls the Census geocoder / Census Reporter once, later runs are offline."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.geo import FOOTPRINTS_PATH
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
    assert c.get("/health").json() == {"status": "ok"}
    r = c.get("/debug/features", params={"address": "912 Mary St, Ann Arbor, MI"})
    assert r.status_code == 200 and r.json()["est_units"] == 4
    assert c.get("/debug/features", params={"address": "123 Fake Street, Nowhere, MI"}).status_code == 404


@needs_data
@pytest.mark.parametrize("street", ["2843 Hardwick Rd", "2877 Rayfield Ave",  # North Oaks townhomes
                                    "3422 Burbank Dr", "2685 Arrowwood Trl"])  # Chapel Hill condos, Arrowwood co-op
def test_townhouses_are_single_family_attached(street):
    f = get_features(f"{street}, Ann Arbor, MI")
    assert f["in.geometry_building_type_recs"] == SFA and f["est_units"] >= 4
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
