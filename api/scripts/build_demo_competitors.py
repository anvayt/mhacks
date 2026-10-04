"""Build api/data/demo_competitors.json: 10 real Ann Arbor homes behind the DEMO leaderboard competitors.

Addresses come only from public Zillow listing URLs (the address is in the URL; pages are never fetched or scraped,
per PLAN.md "parse the URL, never scrape the page"). Each address is placed on its City of Ann Arbor building
footprint (public MailingAddress + BuildingFootprints services, no key) and joined to our own model's city scores
(api/data/city_scores.csv). Those real values are the competitors' baselines. Their behavior (streaks, commitments,
CO2 avoided) is synthetic demo data, labelled demo everywhere; boards show aliases and tracts, never addresses.

Run from the repo root:  python3 api/scripts/build_demo_competitors.py   (stdlib only; needs network)
"""

import csv
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "api/data/city_scores.csv"
OUT = ROOT / "api/data/demo_competitors.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) HiddenRent/1.0"}  # the city services 403 Python's default agent
ADDR = "https://a2maps.a2gov.org/a2arcgis/rest/services/MailingAddress/FeatureServer/0/query"
FOOT = "https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0/query"
WANT = 10

# Public Zillow listing URLs found by web search on Oct 4, 2026 (homedetails pages; only the URL text is used).
LISTINGS = [
    "https://www.zillow.com/homedetails/1035-N-Main-St-Ann-Arbor-MI-48104/24697657_zpid/",
    "https://www.zillow.com/homedetails/1200-Gardner-Ave-Ann-Arbor-MI-48104/24708332_zpid/",
    "https://www.zillow.com/homedetails/314-Mark-Hannah-Pl-Ann-Arbor-MI-48103/24703317_zpid/",
    "https://www.zillow.com/homedetails/815-Sunrise-Ct-Ann-Arbor-MI-48103/24696384_zpid/",
    "https://www.zillow.com/homedetails/710-W-Stadium-Blvd-Ann-Arbor-MI-48103/24706701_zpid/",
    "https://www.zillow.com/homedetails/214-W-Kingsley-St-Ann-Arbor-MI-48103/2080748899_zpid/",
    "https://www.zillow.com/homedetails/401-Hiscock-St-Ann-Arbor-MI-48103/24697630_zpid/",
    "https://www.zillow.com/homedetails/1724-Chandler-Rd-Ann-Arbor-MI-48105/24697977_zpid/",
    "https://www.zillow.com/homedetails/3217-Pinebluff-Ct-Ann-Arbor-MI-48105/24692176_zpid/",
    "https://www.zillow.com/homedetails/3415-Bayswater-Ln-Ann-Arbor-MI-48105/54793038_zpid/",
    "https://www.zillow.com/homedetails/1803-Hill-St-Ann-Arbor-MI-48104/24700628_zpid/",
    "https://www.zillow.com/homedetails/2025-Huron-Pkwy-Ann-Arbor-MI-48104/2080664181_zpid/",
    "https://www.zillow.com/homedetails/1253-Island-Dr-APT-104-Ann-Arbor-MI-48105/24698476_zpid/",
    "https://www.zillow.com/homedetails/1261-Island-Dr-APT-204-Ann-Arbor-MI-48105/24698469_zpid/",
]
ALIASES = ["Maple", "Oak", "Elm", "Pine", "Birch", "Cedar", "Willow", "Aspen", "Spruce", "Hickory"]

# Synthetic behavior, one row per competitor (demo only): share of baseline CO2 avoided, months below normal,
# commitments accepted / verified, daily habit streak / best. Chosen to give the boards a spread, nothing more.
BEHAVIOR = [(0.12, 4, 4, 2, 9, 12), (0.09, 3, 3, 2, 6, 10), (0.07, 2, 3, 1, 5, 8), (0.06, 3, 2, 1, 4, 7),
            (0.05, 1, 4, 1, 3, 9), (0.04, 2, 2, 1, 2, 5), (0.03, 1, 3, 1, 7, 7), (0.08, 0, 2, 1, 1, 4),
            (0.10, 2, 4, 2, 0, 6), (0.02, 1, 1, 1, 3, 3)]

# Rough annual CO2 from the model's dollars, for the demo baseline only (labelled approximate):
# gas $/ccf ≈ 0.91 (P1 marginal Michigan price, UtilizationToMoney.md), electricity $/kWh ≈ 0.205 (EIA-861M MI
# average 0.19–0.22); factors from api/app/co2.py (EPA 5.306 kg/therm, 1.037 therm/ccf, eGRID2023 RFCM 0.4403 kg/kWh).
GAS_USD_PER_CCF, ELEC_USD_PER_KWH = 0.91, 0.205
KG_PER_CCF, KG_PER_KWH = 1.037 * 5.306, 0.4403


def get(url: str, params: dict) -> dict:
    req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def street(listing: str) -> str:
    """'…/homedetails/1253-Island-Dr-APT-104-Ann-Arbor-MI-48105/…' → '1253 ISLAND DR' (unit dropped)."""
    slug = listing.split("/homedetails/")[1].split("/")[0]
    slug = re.sub(r"-Ann-Arbor-MI-\d{5}$", "", slug)
    slug = re.sub(r"-(APT|UNIT|STE)-.*$", "", slug, flags=re.I)
    return slug.replace("-", " ").upper()


def footprint(addr: str) -> int | None:
    pts = get(ADDR, {"where": f"PROPSTREET LIKE '{addr}%'", "outFields": "PROPSTREET", "outSR": 4326,
                     "returnGeometry": "true", "f": "json", "resultRecordCount": 1}).get("features", [])
    if not pts:
        return None
    x, y = pts[0]["geometry"]["x"], pts[0]["geometry"]["y"]
    for extra in ({}, {"distance": 12, "units": "esriSRUnit_Meter"}):  # inside, else snap (points sit 5–11 m off)
        hit = get(FOOT, {"geometry": f"{x},{y}", "geometryType": "esriGeometryPoint", "inSR": 4326,
                         "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID", "f": "json", **extra})
        if hit.get("features"):
            return int(hit["features"][0]["attributes"]["OBJECTID"])
    return None


def main() -> None:
    scores = {int(r["footprint_id"]): r for r in csv.DictReader(SCORES.open())}
    homes = []
    for url in LISTINGS:
        addr = street(url)
        fid = footprint(addr)
        row = scores.get(fid) if fid else None
        print(f"{addr:28} footprint {fid}  {'scored' if row else 'not scored, skipped'}")
        if not row or any(h["basis"]["footprint_id"] == fid for h in homes):
            continue
        heating = float(row["heating_usd"])
        cooling = max(0.0, float(row["annual_usd"]) - heating)
        baseline = round(heating / GAS_USD_PER_CCF * KG_PER_CCF + cooling / ELEC_USD_PER_KWH * KG_PER_KWH)
        i = len(homes)
        share, streak, accepted, verified, habit, best = BEHAVIOR[i]
        homes.append({
            "alias": "Demo " + ALIASES[i],
            "basis": {"listing_url": url, "street": addr.title(), "footprint_id": fid, "type": row["type"],
                      "block_group": row["block_group"], "sqft": int(float(row["sqft"])),
                      "annual_usd": float(row["annual_usd"]), "heating_usd": heating, "score": float(row["score"]),
                      "grade": row["grade"], "source": "api/data/city_scores.csv (our model's city batch)"},
            "home": ["demo", str(fid)], "tract": row["block_group"][:11],
            "baseline_co2_kg_yr": baseline, "baseline_note": "approximate, from the model's $ (see script header)",
            "co2_kg_avoided": round(baseline * share), "streak_months": streak, "accepted": accepted,
            "verified": verified, "verified_impact_count": 1 if verified else 0, "habit_streak": habit,
            "habit_best": best, "demo": True, "named": True,
        })
        if len(homes) == WANT:
            break
    if len(homes) < WANT:
        raise SystemExit(f"only {len(homes)} listings matched a scored footprint; add more LISTINGS")
    OUT.write_text(json.dumps({"note": __doc__.strip().splitlines()[0], "built_from": "Zillow listing URLs (URL text only) "
                               "+ City of Ann Arbor GIS + api/data/city_scores.csv", "competitors": homes}, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(homes)} demo competitors")


if __name__ == "__main__":
    main()
