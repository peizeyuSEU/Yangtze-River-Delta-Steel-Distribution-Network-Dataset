# Dataset card

## Motivation
An auditable public-data calibration case for a Yangtze River Delta steel distribution network.

## Dataset scope
One supplier, eight candidate DCs, and fifteen markets. Coordinates are city-centre points, not enterprise facilities.

## Entities and network
Supplier-to-DC and DC-to-market arcs include cached OSRM road distances and transparent assumptions.

## Sources and pipeline
Statistics, steel prices, rents, GeoNames coordinates, OSM/OSRM routing cache, and scenario assumptions are separately catalogued. `scripts/build_all.py` reconstructs processed inputs offline.

## Processed files and provenance
The v0.1.0-preview processed files and 918-record lineage bijection are summarized in `metadata/release_manifest.json` and traceable with `scripts/trace_value.py`.

## Quality and comparability
See the data-quality, observation-comparability, third-party, and intracity sensitivity audits. The data are suitable for regional research calibration and sensitivity analysis, not strict same-day panels or enterprise-real operating costs.

## Known limitations and third-party data
Jinhua steel price is a geographic proxy; some rents are listings; time and brand/specification bases vary. GeoNames is CC BY 4.0, OSM is ODbL, and OSRM software is BSD-2-Clause; scope review remains documented.

## Intended and out-of-scope uses
Use for public-data calibration, screening heterogeneity, robustness, and reproducible teaching/research. Do not represent as firm operating data, uniform transaction prices, or licensed formal release.

## Maintenance, citation, and carbon quota
Maintainer: Zeyu Pei (@peizeyuSEU). Versioning preserves preview inputs. No DOI is assigned. Carbon quota is `not_yet_generated` and must come from an external recorded model artifact.
