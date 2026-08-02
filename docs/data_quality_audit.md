# Data quality audit

Generated: 2026-08-02 (offline)

Total checks: 238
Passed: 226
Warnings: 12
Failed: 0
warning_record_count: 12
warning_category_count: 5

## Scope and findings

Hard checks passed: 226; failed checks: 0.
Dataset scale: 16 nodes (1 supplier, 8 candidate DCs, 15 markets), 8 supplier-DC arcs, 120 DC-market arcs.
Road distance range: 0.000--554.816 km; Haversine/road anomalies: 0.
Documented same-city zero-distance arcs (8): C01|C01, C02|C02, C03|C03, C04|C04, C05|C05, C06|C06, C07|C07, C08|C08; these are warnings, not data errors.
Processed non-empty values: 918; record_lineage rows: 918; exact processed-to-lineage bijection and foreign-key checks passed.
Demand, price, rent, fixed-cost, transport-cost, emission-parameter, schema, configuration, and lineage checks are included in the CSV.
Time basis differs across sources: 2024 second-industry statistics, 2026 price observations, and 2026 rent observations; these are screening/calibration inputs.
Proxy values: Jinhua PRICE_M15 (mean of PRICE_C05, PRICE_C08, PRICE_M12).
Specific listings: RENT_C02 Nanjing and RENT_C07 Feixi/Hefei; they are not city averages.
Warnings are documented in five categories: same-city structural zero, Jinhua price proxy, specific-listing rents, mixed source dates, and carbon quota not generated. WARN-001 is a passed category summary and is excluded from warning counts.
No processed value should be modified as a result of this audit. Any future correction would affect the corresponding processed parameter file, lineage records, and downstream validation reports.
The audit is offline and does not invoke network access, GA-BP, BP, CPLEX, or any solver.
