# Data quality audit

Generated: 2026-08-02 (offline)

Total checks: 215
Passed: 215
Warnings: 0
Failed: 0

## Scope and findings

Dataset scale: 16 nodes (1 supplier, 8 candidate DCs, 15 markets), 8 supplier-DC arcs, 120 DC-market arcs.
Road distance range: 0.000--554.816 km; Haversine/road anomalies: 0 (same-city zero-distance is retained as a warning).
Demand, price, rent, fixed-cost, and transport-cost formula checks are included in the CSV.
Time basis differs across sources: 2024 second-industry statistics, 2026 price observations, and 2026 rent observations; these are screening/calibration inputs.
Proxy values: Jinhua PRICE_M15 (mean of PRICE_C05, PRICE_C08, PRICE_M12).
Specific listings: RENT_C02 Nanjing and RENT_C07 Feixi/Hefei; they are not city averages.
No processed value should be modified as a result of this audit. Any future correction would affect the corresponding processed parameter file, lineage records, and downstream validation reports.
The audit is offline and does not invoke network access, GA-BP, BP, CPLEX, or any solver.
