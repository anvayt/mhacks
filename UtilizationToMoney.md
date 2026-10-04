Energy use becomes dollars by multiplying it by a Michigan price per unit for each month: dollars per ccf of gas (100 cubic
  feet), and dollars per kWh of electricity. Both prices come from the U.S. Energy Information Administration's (EIA) public
  monthly data. This happens in P1's model/data_sources/eia.py, and the map widget reuses it through estimate_hc.

  The formula. For each month m:

    cost_m = gas ccf_m × p^gas_m + electric kWh_m × p^elec_m

  The yearly and seasonal costs are sums over the months. The energy amounts come from the model: energy per degree-day × the
  local degree-days for that month × floor area. The prices come from EIA:

  ┌─────────┬──────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────┐
  │ Fuel    │ Government data                                                          │ Price used                              │
  ├─────────┼──────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┤
  │ Natural │ EIA series N3010MI3 (Michigan residential price, \$/Mcf) and N3010MI2    │ "Marginal" price, converted to \$/ccf   │
  │ gas     │ (volume sold, MMcf), monthly                                             │ (1 Mcf = 10 ccf)                        │
  ├─────────┼──────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┤
  │ Electri │ EIA-861M sales and revenue, Michigan residential rows, monthly           │ Average price, \$/kWh (revenue ÷ kWh    │
  │ city    │                                                                          │ sold)                                   │
  └─────────┴──────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────┘

  Why gas uses a "marginal" price. EIA's price is total revenue ÷ total volume, so it includes fixed monthly customer charges. In
  summer, little gas is sold, so those fixed charges get spread over a small volume. The average price nearly doubles: \$1.88/ccf
  in June versus \$0.97 in January. Heating is extra use on top of the base bill, so P1 strips the fixed charges out:
  1. Over the last 24 months (Aug 2024 – Jul 2026), regress total revenue on volume. The slope is the cost of one more unit, and
     the intercept is the fixed charges. The fit is very tight: R² = 0.99.
  2. Each month's marginal price = (revenue − fixed charges) ÷ volume, averaged by calendar month. That gives \$0.77–\$0.97/ccf,
     about \$0.91 over the year.

  Why electricity uses the average price. The same regression for electricity gives negative fixed charges, which can't be real.
  So P1 falls back to EIA's average price, \$0.19–\$0.22/kWh by month. That likely overstates the cost of extra electricity a bit,
  since some fixed charges are baked in.

  Caveats:
  • These are statewide prices across all Michigan residential customers, not DTE's actual tariff with tiers, riders and the
    customer charge. The team decided in notes/requests.md to reuse this EIA pricing rather than build DTE tariffs.
  • Only heating and cooling are priced. Hot water, appliances and fixed charges aren't included, so the figures aren't a full
    utility bill. The /estimate API labels this with bill.covers.
  • Prices are cached in model/data/processed/prices_mi.json, which lists the source spreadsheets. They're rebuilt by
    price_table(refresh=True).