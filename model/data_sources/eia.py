"""Michigan residential energy prices from the US EIA (no API key: public spreadsheets).

- Natural gas price ($/Mcf), series N3010MI3: https://www.eia.gov/dnav/ng/hist/n3010mi3m.htm
- Natural gas volume (MMcf), series N3010MI2: https://www.eia.gov/dnav/ng/hist/n3010mi2m.htm
- Electricity revenue/sales/customers (EIA-861M): https://www.eia.gov/electricity/data/eia861m/

EIA's monthly "price" is average revenue per unit, so it includes fixed customer charges. In summer, little gas
is sold and the average price roughly doubles. Heating and cooling are *extra* usage, so we price them at the
**marginal** rate: regress total monthly revenue on monthly volume over the last 24 months. The slope is the
marginal $/unit and the intercept is the fixed charges. Then marginal price for month m = (revenue_m − fixed) / volume_m.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from model.data_sources.http import download
from model.paths import PROCESSED, RAW

NG_PRICE = "https://www.eia.gov/dnav/ng/hist_xls/N3010MI3m.xls"
NG_VOL = "https://www.eia.gov/dnav/ng/hist_xls/N3010MI2m.xls"
ELEC = "https://www.eia.gov/electricity/data/eia861m/xls/sales_revenue.xlsx"
MCF_PER_CCF = 0.1
WINDOW_MONTHS = 24


def _ng(url: str, name: str) -> pd.DataFrame:
    d = pd.read_excel(download(url, RAW / "eia" / name), sheet_name="Data 1", skiprows=2)
    d.columns = ["date", "v"]
    d["date"] = pd.to_datetime(d["date"])
    return d.dropna()


def _marginal(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """df: date, revenue, volume (consistent units) → monthly marginal price + regression stats."""
    df = df.sort_values("date").tail(WINDOW_MONTHS).copy()
    slope, intercept = np.polyfit(df["volume"], df["revenue"], 1)
    pred = slope * df["volume"] + intercept
    r2 = 1 - ((df["revenue"] - pred) ** 2).sum() / ((df["revenue"] - df["revenue"].mean()) ** 2).sum()
    df["avg_price"] = df["revenue"] / df["volume"]
    df["marginal_price"] = (df["revenue"] - intercept) / df["volume"]
    stats = {"slope_marginal": float(slope), "fixed_per_month": float(intercept), "r2": float(r2),
             "window": [df["date"].min().strftime("%Y-%m"), df["date"].max().strftime("%Y-%m")]}
    return df, stats


def gas_prices() -> tuple[pd.DataFrame, dict]:
    p, v = _ng(NG_PRICE, "N3010MI3m.xls"), _ng(NG_VOL, "N3010MI2m.xls")
    m = p.merge(v, on="date", suffixes=("_p", "_v"))
    m = m.rename(columns={"v_v": "volume"})
    m["revenue"] = m["v_p"] * m["volume"]          # $/Mcf × MMcf = k$ (consistent scale)
    return _marginal(m[["date", "revenue", "volume"]])


def elec_prices() -> tuple[pd.DataFrame, dict]:
    e = pd.read_excel(download(ELEC, RAW / "eia" / "sales_revenue.xlsx"), header=None, skiprows=3)
    mi = e[e[2] == "MI"].iloc[:, [0, 1, 4, 5, 6]]
    mi.columns = ["y", "m", "revenue", "volume", "customers"]   # k$, MWh
    mi = mi.dropna()
    mi["date"] = pd.to_datetime(dict(year=mi.y.astype(int), month=mi.m.astype(int), day=15))
    mi["revenue"] = mi["revenue"].astype(float) * 1000 / 1000      # k$ per MWh → $/kWh after division
    mi["volume"] = mi["volume"].astype(float)
    return _marginal(mi[["date", "revenue", "volume"]])


def price_table(refresh: bool = False) -> dict:
    """Marginal and average prices by calendar month (mean over the window), cached as JSON.
    gas: $/ccf, electricity: $/kWh."""
    path = PROCESSED / "prices_mi.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    g, gs = gas_prices()
    e, es = elec_prices()
    g["month"], e["month"] = g.date.dt.month, e.date.dt.month
    gm = g.groupby("month")[["marginal_price", "avg_price"]].mean() * MCF_PER_CCF       # $/Mcf → $/ccf
    em = e.groupby("month")[["marginal_price", "avg_price"]].mean()                     # k$/MWh = $/kWh
    out = {
        "gas_usd_per_ccf": {"marginal": {int(k): round(v, 4) for k, v in gm["marginal_price"].items()},
                            "average": {int(k): round(v, 4) for k, v in gm["avg_price"].items()},
                            "marginal_flat": round(gs["slope_marginal"] * MCF_PER_CCF, 4), "fit": gs},
        "elec_usd_per_kwh": {"marginal": {int(k): round(v, 4) for k, v in em["marginal_price"].items()},
                             "average": {int(k): round(v, 4) for k, v in em["avg_price"].items()},
                             "marginal_flat": round(es["slope_marginal"], 4), "fit": es},
        "sources": [NG_PRICE, NG_VOL, ELEC],
        "method": "marginal = (monthly revenue − fixed charges) / monthly volume; fixed charges = intercept of revenue~volume OLS over the window",
    }
    path.write_text(json.dumps(out, indent=2))
    return out
