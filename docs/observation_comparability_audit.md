# Observation comparability audit

Offline analysis only; original dates, values, URLs, and processed data are unchanged.

PRICE records: 15; comparability counts: {'high': 9, 'moderate': 2, 'low': 4}
RENT records: 8; comparability counts: {'high': 3, 'moderate': 3, 'low': 2}
PRICE date range: 2026-05-29 to 2026-07-15 (span 47 days)
PRICE records >7 days from 2026-07-10: PRICE_C04, PRICE_C08, PRICE_M09, PRICE_M12, PRICE_M13
PRICE records >30 days from 2026-07-10: PRICE_C04, PRICE_M09, PRICE_M12

Range midpoint records: PRICE_C04, PRICE_M09, PRICE_M11.
Geographic proxy: PRICE_M15.
Brand-specific: PRICE_C06 (Zhongtian); PRICE_M14 (Anhui Changjiang).
Specification-band record: PRICE_M13 (HRB400E Phi18-22).
Specific rent listings: RENT_C02 and RENT_C07.
Daily-to-monthly rent conversions: RENT_C03, RENT_C04, RENT_C05, RENT_C06, RENT_C08 (daily x 30).

## Appropriate uses

The data support a regional network research case, public-data calibration, screening parameterization of city heterogeneity, and robustness/sensitivity experiments.
They should not be described as a strict same-day cross-sectional steel-price panel, fully same-brand/same-specification transaction prices, uniformly defined warehouse transaction rents, or enterprise actual operating costs.

## Future version strategies

**A: freeze v0.1.0-preview** and disclose screening/calibration limits without rerunning experiments.
**B: build v0.2-candidate** with a common steel-price date/window, HRB400E Phi20, explicit brand policy, and uniform city-average quarterly rents; preserve v0.1.0-preview, regenerate processed/lineage, and rerun downstream experiments. No strategy is selected or implemented in this audit.
