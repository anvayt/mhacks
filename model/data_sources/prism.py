"""PRISM Climate Group (Oregon State University) gridded temperature at 800 m (30 arc-sec).

Web service docs: https://prism.oregonstate.edu/documents/PRISM_downloads_web_service.pdf
  https://services.nacse.org/prism/data/get/us/800m/tmean/<YYYYMM>
Normals (1991-2020, 800 m): https://prism.oregonstate.edu/normals/
Terms: cite "PRISM Climate Group, Oregon State University, https://prism.oregonstate.edu".

The service allows each file to be downloaded at most twice per 24 h, so every grid is downloaded once,
cropped to Michigan, and kept as a small GeoTIFF under data/raw/prism/.
"""
import io
import zipfile
from pathlib import Path

import numpy as np
import rasterio
import requests
from rasterio.windows import from_bounds

from model.data_sources.http import UA
from model.paths import RAW

SERVICE = "https://services.nacse.org/prism/data/get/us/800m"
NORMALS = "https://data.prism.oregonstate.edu/normals/us/800m/{var}/monthly/prism_{var}_us_30s_2020{mm}_avg_30y.zip"
MI_BOUNDS = (-90.6, 41.6, -82.1, 48.4)  # lon_min, lat_min, lon_max, lat_max (lower peninsula + UP)
DIR = RAW / "prism"


def _crop_zip_to_mi(blob: bytes, out: Path) -> Path:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        name = next(n for n in z.namelist() if n.endswith((".tif", ".bil")))
        tmp = DIR / "_tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        z.extractall(tmp)
    src_path = tmp / name
    with rasterio.open(src_path) as src:
        win = from_bounds(*MI_BOUNDS, transform=src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=win)
        prof = src.profile.copy()
        prof.update(height=arr.shape[0], width=arr.shape[1], transform=src.window_transform(win),
                    driver="GTiff", compress="deflate", tiled=False)
        prof.pop("blockxsize", None); prof.pop("blockysize", None)
        out.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(out, "w", **prof) as dst:
            dst.write(arr, 1)
    for p in tmp.iterdir():
        p.unlink()
    return out


def grid_path(var: str, period: str) -> Path:
    """period: 'YYYYMM' (monthly time series) or 'normMM' (1991-2020 normal for month MM)."""
    return DIR / var / f"{period}.tif"


def fetch(var: str, period: str) -> Path:
    out = grid_path(var, period)
    if out.exists():
        return out
    if period.startswith("norm"):
        url = NORMALS.format(var=var, mm=period[4:])
    else:
        url = f"{SERVICE}/{var}/{period}"
    r = requests.get(url, headers=UA, timeout=600)
    r.raise_for_status()
    if not r.content[:2] == b"PK":
        raise RuntimeError(f"PRISM returned non-zip for {url}: {r.content[:200]!r}")
    return _crop_zip_to_mi(r.content, out)


_open: dict = {}


def sample(var: str, period: str, lats, lons) -> np.ndarray:
    """Values at points (nearest 800 m cell). Requires the grid to be fetched already."""
    p = grid_path(var, period)
    if p not in _open:
        with rasterio.open(p) as src:
            _open[p] = (src.read(1).astype("float64"), src.transform, src.nodata)
    arr, tf, nod = _open[p]
    lats = np.atleast_1d(np.asarray(lats, float)); lons = np.atleast_1d(np.asarray(lons, float))
    cols = np.floor((lons - tf.c) / tf.a).astype(int)
    rows = np.floor((lats - tf.f) / tf.e).astype(int)
    rows = np.clip(rows, 0, arr.shape[0] - 1); cols = np.clip(cols, 0, arr.shape[1] - 1)
    v = arr[rows, cols]
    if nod is not None:
        v = np.where(v == nod, np.nan, v)
    v = np.where(v < -1000, np.nan, v)
    return v


def available(var: str = "tmean") -> list[str]:
    d = DIR / var
    return sorted(p.stem for p in d.glob("*.tif")) if d.exists() else []
