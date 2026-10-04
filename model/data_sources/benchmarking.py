"""Ann Arbor Energy Benchmarking (Portfolio Manager submissions under the city's
benchmarking ordinance): whole-building monthly electricity and natural gas, 2021-2023.

Source: https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0
Public map: https://a2gov.org/benchmarkingmap
"""
import pandas as pd
from shapely.geometry import shape

from model.data_sources.arcgis import fetch_all

URL = ("https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/"
       "rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_raw(refresh: bool = False) -> pd.DataFrame:
    """One row per building-year, monthly columns as published, plus centroid + polygon."""
    feats = fetch_all(URL, "a2_benchmarking", refresh=refresh)
    rows = []
    for f in feats:
        a = dict(f["properties"])
        g = f.get("geometry")
        if g:
            geom = shape(g)
            c = geom.representative_point()
            a.update(lat=c.y, lon=c.x, footprint_wkt=geom.wkt)
        rows.append(a)
    return pd.DataFrame(rows)
