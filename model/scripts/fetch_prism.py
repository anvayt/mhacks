"""Download + crop PRISM 800 m tmean grids: 1991-2020 monthly normals and monthly 2021-01 .. latest.

Run: python -m model.scripts.fetch_prism [start_yyyymm] [end_yyyymm]
"""
import sys
import time

from model.data_sources.prism import fetch, grid_path


def periods(start: str, end: str):
    y, m = int(start[:4]), int(start[4:])
    while f"{y}{m:02d}" <= end:
        yield f"{y}{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


def main(start="202101", end="202512"):
    todo = [f"norm{m:02d}" for m in range(1, 13)] + list(periods(start, end))
    for p in todo:
        if grid_path("tmean", p).exists():
            continue
        try:
            fetch("tmean", p)
            print("ok", p, flush=True)
        except Exception as e:
            print("FAIL", p, e, flush=True)
        time.sleep(2)  # be polite (PRISM asks for it)


if __name__ == "__main__":
    main(*sys.argv[1:])
