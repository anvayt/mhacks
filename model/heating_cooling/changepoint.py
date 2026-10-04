"""PRISM: the Princeton Scorekeeping Method (Fels 1986, Energy and Buildings 9:5-18), applied per building.

Per-day model, fitted to monthly meter reads:
    use/day = α + βh · HDD(τh)/day + βc · CDD(τc)/day
The balance-point temperatures τh, τc are chosen from a grid by best R². Every term has a physical meaning:
α is baseload (hot water, cooking, lights, plugs), βh·HDD is space heating and βc·CDD is space cooling.
Normalized annual consumption (NAC) = 365·α + βh·HDD_normal(τh) + βc·CDD_normal(τc).

We fit gas (heating only) and electricity (heating + cooling, so electric-heat buildings are captured).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from model.climate import CDD_BASES_F, HDD_BASES_F


@dataclass
class CPFit:
    alpha: float          # baseload per day
    beta_h: float         # per HDD
    beta_c: float         # per CDD
    tau_h: int | None     # heating balance point (°F)
    tau_c: int | None     # cooling balance point (°F)
    r2: float
    n: int
    cv_rmse: float        # ASHRAE Guideline 14 style CV(RMSE) on monthly totals

    def predict(self, w: pd.DataFrame) -> pd.DataFrame:
        """w: rows with days, hddXX, cddXX → base, heating, cooling, total (same units as fitted)."""
        out = pd.DataFrame(index=w.index)
        out["base"] = self.alpha * w["days"]
        out["heating"] = self.beta_h * w[f"hdd{self.tau_h}"] if self.tau_h else 0.0
        out["cooling"] = self.beta_c * w[f"cdd{self.tau_c}"] if self.tau_c else 0.0
        out["total"] = out.sum(axis=1)
        return out

    def to_dict(self):
        return asdict(self)


def _ols(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b, y - X @ b


def fit(df: pd.DataFrame, col: str, heating: bool = True, cooling: bool = True, min_months: int = 9) -> CPFit | None:
    """df: building-months with `col`, days, hddXX, cddXX. Returns the best non-negative change-point fit."""
    d = df.dropna(subset=[col])
    d = d[d[col] > 0]
    if len(d) < min_months:
        return None
    y = (d[col] / d["days"]).to_numpy()
    days = d["days"].to_numpy()
    best = None
    hs = list(HDD_BASES_F) if heating else [None]
    cs = list(CDD_BASES_F) if cooling else [None]
    for th in hs:
        for tc in cs:
            cols = [np.ones(len(d))]
            if th:
                cols.append(d[f"hdd{th}"].to_numpy() / days)
            if tc:
                cols.append(d[f"cdd{tc}"].to_numpy() / days)
            X = np.column_stack(cols)
            b, r = _ols(y, X)
            # physically invalid slopes (negative heating/cooling, negative base): drop that term and refit
            if (th and b[1] < 0) or (tc and b[-1] < 0) or b[0] < 0:
                continue
            ss = 1 - r.var() / y.var() if y.var() > 0 else 0.0
            if best is None or ss > best[0]:
                best = (ss, th, tc, b, r)
    if best is None:  # nothing weather-sensitive: baseload only
        a = float(y.mean())
        resid = (y - a) * days
        return CPFit(a, 0.0, 0.0, None, None, 0.0, len(d), float(np.sqrt(np.mean(resid ** 2)) / (y * days).mean()))
    ss, th, tc, b, r = best
    bh = float(b[1]) if th else 0.0
    bc = float(b[-1]) if tc else 0.0
    monthly_resid = r * days
    cv = float(np.sqrt(np.mean(monthly_resid ** 2)) / (y * days).mean())
    return CPFit(float(b[0]), bh, bc, th, tc, float(ss), len(d), cv)
