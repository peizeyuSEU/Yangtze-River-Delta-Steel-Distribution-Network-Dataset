# Yangtze River Delta Steel Distribution Network Dataset

Version: **v0.1.0-preview**

This is a data-calibrated regional research dataset. It is not a disclosure of a firm's proprietary operating data. The repository documents the complete data lineage from source records and transparent assumptions to the processed dataset. It does not contain GA-BP optimization results. Model solution and computational experiments are maintained separately.

## Rebuild

```bash
python scripts/build_all.py --config config/baseline.json
python -m pytest -q
```

The default build is offline and reads `data/cache/osrm_response.json`. Network access is only intended for an explicit future OSRM refresh script.

## Traceability examples

1. Shanghai demand: `STAT_C01` → `T_DEMAND_WEIGHT_001` → `T_MARKET_DEMAND_001` → `market_params.csv:C01.mu_annual_tonnes`; use `python scripts/trace_value.py --file market_params.csv --record C01 --column mu_annual_tonnes`.
2. A road distance: node coordinates → cached OSRM matrix (metres) → divide by 1000 → `supplier_dc.csv` or `dc_market.csv`.
3. Shanghai net retained price: `PRICE_C01` → production-cost scenario 3000 → `market_params.csv:C01.v_i_baseline`.
4. Nanjing DC cost: `RENT_C02` → 12 months × 10,000 m² × 1.20 → `dc_params.csv:C02.f_j_cny_per_year`.

The network contains one supplier (Ma'anshan), eight candidate DCs, and fifteen markets. Coordinates represent city-centre points, not enterprise warehouse addresses. Jinhua price is a proxy; some rents are listing-based; transport rates, warehouse area, energy intensity, and production costs are transparent calibration/scenario assumptions. Carbon quota `C` is not generated in this preview.
