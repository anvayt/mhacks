"""CO₂ from P1's heating + cooling energy (PLAN §6 #4). Dollars stay P1's (EIA prices); this module is CO₂ only.

Factors (also cited in api/README.md; checked Oct 4, 2026):
- Gas: 53.06 kg CO₂/mmBtu = 5.306 kg/therm. EPA GHG Emission Factors Hub 2025 (Jan 15, 2025), Table 1 Stationary
  Combustion, Natural Gas. https://www.epa.gov/system/files/documents/2025-01/ghg-emission-factors-hub-2025.pdf
- ccf → therm: 1 ccf = 1.037 therms (2025 US average heat content, 1,037 Btu/cf). EIA FAQ "What are Ccf, Mcf, Btu, and
  therms?" https://www.eia.gov/tools/faqs/faq.php?id=45&t=8 (P1 uses the same 103.7 kBtu/ccf).
- Electricity: 970.6 lb CO₂/MWh = 0.4403 kg/kWh, eGRID2023 (rev 2, Jun 12, 2025; latest EPA release) RFCM (RFC
  Michigan) CO₂ total output emission rate, Summary Tables Table 1.
  https://www.epa.gov/system/files/documents/2025-06/summary_tables_rev2.pdf
"""

KG_PER_THERM = 5.306
THERMS_PER_CCF = 1.037
KG_PER_KWH = 970.6 * 0.45359237 / 1000


def co2_kg(gas_ccf: float, kwh: float) -> float:
    return gas_ccf * THERMS_PER_CCF * KG_PER_THERM + kwh * KG_PER_KWH


def co2_t(hc: dict, bill: dict | None = None) -> dict:
    """Tonnes CO₂ a year from P1's heating_cooling body (annual.gas_ccf, annual.electric_kwh: heating + cooling only).
    P1 gives one point estimate, so p10/p90 = p50 × the bill's annual p10/p50 and p90/p50 when present, else null."""
    a = hc["annual"]
    p50 = co2_kg(a["gas_ccf"], a["electric_kwh"]) / 1000
    band = (bill or {}).get("annual") or {}
    mid = band.get("p50")
    scale = lambda q: round(p50 * q / mid, 2) if q is not None and mid else None
    return {"p10": scale(band.get("p10")), "p50": round(p50, 2), "p90": scale(band.get("p90"))}
