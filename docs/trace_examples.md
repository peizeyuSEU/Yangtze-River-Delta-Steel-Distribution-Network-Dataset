# Trace examples

The following were executed from the repository virtual environment.

| Value | Command | Result |
|---|---|---|
| Shanghai annual demand | `python scripts/trace_value.py --file market_params.csv --record C01 --column mu_annual_tonnes` | `136835.573955 tonnes/year` |
| Shanghai baseline net retained price | `python scripts/trace_value.py --file market_params.csv --record C01 --column v_i_baseline` | `150 CNY/tonne` |
| Shanghai DC to Shanghai market distance | `python scripts/trace_value.py --file dc_market.csv --record C01 --column road_distance_km` | `0 km` |
| Nanjing DC fixed cost | `python scripts/trace_value.py --file dc_params.csv --record C02 --column f_j_cny_per_year` | `3024000 CNY/year` |

Each value is linked to the source records and transformations listed in `metadata/record_lineage.csv` and `metadata/transformation_registry.csv`.
