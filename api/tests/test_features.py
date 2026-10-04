"""Address -> features. Real Ann Arbor addresses need the footprint cache (scripts/fetch_footprints.py);
the first run also calls the Census geocoder / Census Reporter once, later runs are offline."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.geo import FOOTPRINTS_PATH
from app.geo.features import MF5, MF24, SFD, building_type, get_features, vintage
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
