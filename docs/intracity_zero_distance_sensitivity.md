# Intracity zero-distance sensitivity analysis

Offline, non-destructive analysis only. Candidate distances are not written to processed data or model inputs.

Arcs analysed: C01|C01, C02|C02, C03|C03, C04|C04, C05|C05, C06|C06, C07|C07, C08|C08

| Candidate distance (km) | Aggregate annual cost increment (CNY) | Aggregate annual emission increment (tCO2e) |
|---:|---:|---:|
| 0 | 0.00 | 0.000000 |
| 5 | 1,371,709.32 | 246.063548 |
| 10 | 2,743,418.63 | 492.127096 |
| 15 | 4,115,127.95 | 738.190645 |
| 20 | 5,486,837.27 | 984.254193 |
| 30 | 8,230,255.90 | 1,476.381289 |

## Interpretation

The values are scale calculations assuming all local annual demand is served by the corresponding same-city DC. They are not an optimization assignment.

The largest annual impacts are associated with the markets having the largest annual demand, especially Suzhou, Shanghai, and Ningbo under the same candidate distance.

## Treatment options

**A. Retain 0 km:** valid only if the model explicitly excludes intra-city last-mile delivery.

**B. Apply a common lower bound:** requires public evidence or a robustness study; this analysis does not recommend a particular distance.

**C. Use representative DC and market coordinates:** more realistic, but requires collecting logistics-park/warehouse coordinates and recomputing the road network distances.

No option is recommended here; the sensitivity table is provided to make the assumption transparent.
