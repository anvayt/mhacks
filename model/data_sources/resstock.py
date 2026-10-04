"""NREL ResStock 2024.2 (TMY3 release 2), Michigan baseline: 18,756 simulated homes.

Source: https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2024%2Fresstock_tmy3_release_2%2F
"""
import pandas as pd

from model.data_sources.http import download
from model.paths import RAW

URL = ("https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/"
       "end-use-load-profiles-for-us-building-stock/2024/resstock_tmy3_release_2/"
       "metadata_and_annual_results/by_state/state=MI/parquet/"
       "MI_baseline_metadata_and_annual_results.parquet")
PATH = RAW / "resstock" / "MI_baseline_metadata_and_annual_results.parquet"


def load(gas_only: bool = False) -> pd.DataFrame:
    d = pd.read_parquet(download(URL, PATH))
    if gas_only:
        d = d[d["in.heating_fuel"] == "Natural Gas"].copy()
    return d
