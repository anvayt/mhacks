"""GET /fixes/{session_id} (PLAN §4 #7, §10): Green Rental Housing fixes ranked by CO₂ saved per net $ after rebates.

Dollars and CO₂ come only from P1's model: the session's /hc/estimate params re-run with one changed input per fix
(concurrently), minus the session's own estimate. Fixes the model has no input for (air sealing, insulation,
thermostat) are listed with null savings and `unpriced: true`. Costs and rebates are cited or null.

GRH points: City of Ann Arbor, Green Rental Housing Checklist (PDF modified Jun 29, 2026; 70 points needed for
inspections Jan 6, 2026 – Jul 5, 2028, 110 after), https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf
"""

from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException

from app import estimate, sessions
from app.co2 import co2_kg
from app.score import score_for

router = APIRouter()

GRH_PDF = "https://www.a2gov.org/media/dxxnmkyt/green-rental-housing-checklist.pdf"
GRH_REQUIRED = 70  # checklist points for inspections Jan 6, 2026 – Jul 5, 2028 (110 after)
EXPIRED = "That session expired. Send the listing again."
NOW_NOTE = "from what you told us: checklist items we can confirm from your answers only"

# Costs/rebates, checked Oct 4, 2026. A per-window figure we can't turn into one unit total stays null, with the
# cited figure in cost_note.
A2ZERO = "https://www.a2gov.org/sustainability-innovations-home/sustainability-me/for-families-individuals/a2zero-rebates/"
A2ZERO_APP = ("https://media-001-us.cdn.govstack.com/a2gov-002-us/media/hkvjrimf/"
              "ann-arbor-her-application-updated-2026-2027-81326.pdf")
DOE_STORM = ("http://web.archive.org/web/20260501010625/https://www.energy.gov/energysaver/"
             "do-it-yourself-savings-project-install-exterior-storm-windows-low-e-coating")
DTE_INSULATION_WINDOWS = ("https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/"
                          "insulation-and-windows.html")
DOE_HP_MIDWEST = "https://bsesc.energy.gov/sites/default/files/2024-12/Heat%20Pumps%20Regional%20Factsheet%20Midwest.pdf"
DTE_THERMOSTAT = ("https://www.dteenergy.com/us/en/residential/save-money-energy/rebates-and-offers/"
                  "wi-fi-enabled-thermostats.html")

# Each fix: GRH checklist item(s) + points, cost/rebate, and the model input it changes. `methods`: P1 estimate paths
# where that input moves the answer (renter answers feed only the ResStock part; a metered building's own meter fit
# ignores them). A2ZERO rebates (City of Ann Arbor, 2026-27) are open to owners and renters (with landlord consent)
# and capped at 90% of cost; we show the market-rate amount.
WINDOWS = {"item": "ENERGY STAR low-e storm windows or windows", "grh_points": 4,
           "grh_item": "Energy Efficient Windows", "change": {"window_panes": 2},
           "methods": {"resstock", "meter_model+resstock"}, "cost_usd": None, "rebate_usd": None,
           "cost_note": "Low-e storm windows cost $60-$200 per window installed (DOE Energy Saver). DTE pays $15 per "
                        "replacement window in homes it heats (2026).",
           "sources": [GRH_PDF, DOE_STORM, DTE_INSULATION_WINDOWS]}
HEAT_PUMP = {"item": "Cold-climate heat pump (all-electric heat and cooling)", "grh_points": 35,
             "grh_item": "Electricity is the Primary Type of Energy Used for Space Heating (15) + Medium-Efficiency "
                         "Cold-Climate Heat Pump with Electric Backup Heat (20)",
             "change": {"heating_fuel": "electric", "cooling_code": 3}, "methods": {"resstock"},
             "cost_usd": (11_300 + 19_500) // 2, "rebate_usd": 4_000,
             "cost_note": "Midpoint of $11,300-$19,500, where most Midwest heat pump retrofits fall (DOE/LBNL, Dec "
                          "2024). Rebate: A2ZERO cold-climate heat pump $4,000 ($5,500 income-qualified). The federal "
                          "25C tax credit ended Dec 31, 2025.",
             "sources": [GRH_PDF, DOE_HP_MIDWEST, A2ZERO, A2ZERO_APP]}
UNPRICED = [
    {"item": "Air sealing (blower-door tested)", "grh_points": 9, "grh_item": "Air Sealing",
     "cost_usd": None, "rebate_usd": 500,
     "cost_note": "Rebate: A2ZERO air sealing $500 ($1,000 income-qualified), plus a $1,500 bonus with two insulation "
                  "measures.",
     "sources": [GRH_PDF, A2ZERO, A2ZERO_APP]},
    {"item": "Attic insulation to R-50", "grh_points": 9, "grh_item": "Attic or Non-attic Roof Areas are Insulated",
     "cost_usd": None, "rebate_usd": 500,
     "cost_note": "Rebate: A2ZERO attic insulation $500 ($1,000 income-qualified). DTE pays $600 for 500+ sq ft of "
                  "attic in DTE-heated homes of up to 2 units (2026).",
     "sources": [GRH_PDF, A2ZERO, A2ZERO_APP, DTE_INSULATION_WINDOWS]},
    {"item": "ENERGY STAR smart thermostat", "grh_points": 4,
     "grh_item": "Use a Programmable Thermostat (2) + Use an ENERGY STAR Certified Smart Thermostat (2)",
     "cost_usd": None, "rebate_usd": 50, "cost_note": "Rebate: DTE $50 per household (2026).",
     "sources": [GRH_PDF, DTE_THERMOSTAT]},
]


def _fail(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status, {"code": code, "message": message})


def _candidates(s: dict) -> list[dict]:
    """Model-priced fixes that don't match what the unit already has."""
    p, hc = estimate.session_params(s), s["heating_cooling"]
    fuel = p.get("heating_fuel") or hc["building"].get("heating_fuel")
    out = []
    if (p.get("window_panes") or 0) < 2:
        out.append(WINDOWS)
    if fuel == "electric" and p.get("cooling_code") != 3:
        # resistance → heat pump: the model's heat-pump input prices it; "electricity is primary" (15) already earned
        out.append(dict(HEAT_PUMP, grh_points=20,
                        grh_item="Medium-Efficiency Cold-Climate Heat Pump with Electric Backup Heat"))
    elif fuel != "electric":
        # ponytail: gas → electric in P1's model means Michigan's electric-heated stock (near resistance; 1514 Morton
        # Ave came out +$6,800/yr), not a cold-climate heat pump, so it's listed unpriced until P1 models one.
        out.append(dict(HEAT_PUMP, methods=set()))
    return out


def _priced(fix: dict, base: dict, new: dict, b: dict) -> dict:
    d_gas, d_kwh = base["gas_ccf"] - new["annual"]["gas_ccf"], base["electric_kwh"] - new["annual"]["electric_kwh"]
    return dict(fix, unpriced=False, co2_kg_saved=round(co2_kg(d_gas, d_kwh)),
                usd_saved_yr=round(base["total_usd"] - new["annual"]["total_usd"]),
                new_grade=score_for(new["annual"]["total_usd"], b["sqft"], b["type"])["grade"])


def _unpriced(f: dict) -> dict:
    return dict(f, unpriced=True, co2_kg_saved=None, usd_saved_yr=None, new_grade=None)


def _net(f: dict) -> float | None:
    return None if f["cost_usd"] is None else f["cost_usd"] - (f["rebate_usd"] or 0)


def _rank(f: dict) -> tuple:
    """Priced first, by CO₂ saved per net $ (free after rebates = best); unknown cost next; unpriced last."""
    net = _net(f)
    if f["unpriced"] or net is None:
        return f["unpriced"], True, 0.0
    return False, False, -(float("inf") if net <= 0 else f["co2_kg_saved"] / net)


def _grh_now(s: dict) -> int:
    """Checklist points the renter's own answers confirm."""
    p = estimate.session_params(s)
    pts = 15 if p.get("heating_fuel") == "electric" else 0  # Electricity is the Primary ... Space Heating
    return pts + (2 if p.get("cooling_code") in (2, 3) else 0)  # Space Cooling is Provided (central AC/heat pump)


def _usd(n: int) -> str:
    return f"${n:,}"


def landlord_email(address: str, fixes: list[dict], now: int, after: int) -> str:
    """Deterministic template (no LLM), so every number is the API's own."""
    lines = []
    for i, f in enumerate(fixes[:3], 1):
        parts = [f"+{f['grh_points']} Green Rental Housing points ({f['grh_item']})"]
        if f["usd_saved_yr"] is not None:
            usd = f["usd_saved_yr"]
            more_less = f"{_usd(usd)}/yr less" if usd >= 0 else f"{_usd(-usd)}/yr more"
            parts.insert(0, f"about {more_less} to heat and cool, {f['co2_kg_saved']:,} kg less CO2 a year")
        if f["rebate_usd"]:
            parts.append(f"rebate {_usd(f['rebate_usd'])}")
        lines.append(f"{i}. {f['item']}: " + "; ".join(parts))
    return (f"Subject: Energy upgrades for {address}\n\n"
            f"Hi,\n\nI rent {address}. Hidden Rent (estimates from NREL ResStock and local weather) suggests these "
            "upgrades:\n\n" + "\n".join(lines) + "\n\n"
            "Ann Arbor's Green Rental Housing ordinance (in effect since Jan 6, 2026) asks rentals to reach "
            f"{GRH_REQUIRED} checklist points at inspection (110 after Jul 5, 2028). From what I know of the unit, it "
            f"has {now} confirmed points; these fixes would bring it to {after}.\n\n"
            "Could we talk about scheduling them?\n\nThanks,")


def fixes_for(session_id: str) -> dict:
    s = sessions.get(session_id)
    if s is None:
        raise _fail(404, "not_found", EXPIRED)
    hc, b = s["heating_cooling"], s["building"]
    cands = _candidates(s)
    todo = [f for f in cands if hc["method"] in f["methods"]]
    with ThreadPoolExecutor(max_workers=max(len(todo), 1)) as ex:
        # _hc_ac: same model call as /estimate (No AC never sends cooling_code=0; cooling stays $0)
        runs = list(ex.map(lambda f: estimate._hc_ac({**estimate.session_params(s), **f["change"]}), todo))
    out = [_priced(f, hc["annual"], new, b) for f, new in zip(todo, runs)]
    # model says it doesn't cut CO₂ here (noise: double-pane on 912 Mary St's electric path came out +$29/yr): keep
    # the points and rebate, not the numbers
    out = [f if f["co2_kg_saved"] > 0 else _unpriced(f) for f in out]
    out += [_unpriced(f) for f in cands if f not in todo] + [_unpriced(f) for f in UNPRICED]
    out.sort(key=_rank)
    out = [{k: v for k, v in f.items() if k not in ("change", "methods")} for f in out]
    sessions.save({**s, "used_fixes": True})  # badges: leak-hunter
    now = _grh_now(s)
    after = now + sum(f["grh_points"] for f in out)
    return {"fixes": out, "grh_points_now": now, "grh_points_after": after, "grh_points_now_note": NOW_NOTE,
            "grh_points_required": GRH_REQUIRED,
            "landlord_email": landlord_email(b.get("address") or "my unit", out, now, after)}


@router.get("/fixes/{session_id}")
def get_fixes(session_id: str) -> dict:
    """PLAN §10 /fixes. 404 not_found for an unknown session, 503 model_unavailable if P1's model is down."""
    return fixes_for(session_id)
