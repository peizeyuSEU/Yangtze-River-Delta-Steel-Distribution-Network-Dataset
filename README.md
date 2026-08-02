# Yangtze River Delta Steel Distribution Network Dataset

Version: **v0.1.0-preview**

Maintainer: Zeyu Pei
GitHub: [@peizeyuSEU](https://github.com/peizeyuSEU)

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

## Public-source recovery

Record-level source URLs recovered from the calibration workbook are listed in
[`metadata/source_recovery_register.csv`](metadata/source_recovery_register.csv),
with the verification limits and proxy disclosures in
[`docs/source_verification_report.md`](docs/source_verification_report.md).
GeoNames coordinate provenance, OSRM routing, and OSM map attribution are kept
as separate source categories.

## Third-party data and attribution

GeoNames coordinates: CC BY 4.0. Road-network distances: OSRM using map data
from OpenStreetMap contributors, ODbL. Project OSRM software is separately
licensed under BSD-2-Clause. See
[`metadata/third_party_data_inventory.csv`](metadata/third_party_data_inventory.csv),
[`docs/third_party_data_and_attribution.md`](docs/third_party_data_and_attribution.md),
and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Public statistics,
steel-price, and warehouse-rent pages are used for factual extraction only;
publisher terms continue to apply and no full webpages are redistributed.

## Release and limitations

See the [dataset card](DATASET_CARD.md), [release readiness](docs/release_readiness.md), [open issues](metadata/open_issues_register.csv), and [carbon-quota protocol](docs/carbon_quota_generation_protocol.md). The preview has no DOI assigned. Formal licensed release and carbon-quota-dependent model execution remain blocked as documented.

Audits: [data quality](docs/data_quality_audit.md), [observation comparability](docs/observation_comparability_audit.md), [third-party attribution](docs/third_party_attribution_audit.md), and [release readiness](docs/release_readiness_audit.md).
