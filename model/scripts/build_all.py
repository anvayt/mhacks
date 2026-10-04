"""Rebuild every P1 artifact from scratch (uses the on-disk caches; downloads only what's missing).

Run: python -m model.scripts.build_all   (≈ 2–3 min warm; first run downloads ResStock, footprints,
benchmarking, PRISM grids and Open-Meteo history)
"""
from model.data_sources.eia import price_table
from model.hc import building_model, leakage_analysis, resstock_model, score_buildings, train, validate
from model.scripts import build_meters, fetch_prism, reproduce_resstock


def main():
    fetch_prism.main("202101", "202312")   # grids needed for training (+ normals)
    reproduce_resstock.main()               # P1-02 checkpoint numbers
    build_meters.main()                     # P1-04
    price_table(refresh=True)               # EIA prices
    train.main()                            # P1-05 change-points + panel comparison
    building_model.main()                   # P1-05 building-level models
    resstock_model.main()                   # P1-07
    leakage_analysis.main()                 # P1-07 analysis
    validate.main()                         # NOAA normals + seasonal accuracy on real meters
    score_buildings.main()                  # P1-06 map table


if __name__ == "__main__":
    main()
