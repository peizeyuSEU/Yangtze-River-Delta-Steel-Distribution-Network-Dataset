# Reproducibility report

Command: `python scripts/build_all.py --config config/baseline.json`.

The build completed offline from source records, raw public records, and `data/cache/osrm_response.json`, producing 16 nodes, 8 supplier-DC arcs, 120 DC-market arcs, and 15 market parameter records. No GA-BP, branch-and-price, CPLEX, or network request was used.

Clean-clone reproduction used `%TEMP%/ydr-steel-dataset-reproduction`. Existing interim and processed outputs were removed before rebuilding. The rebuilt processed directory contained 8 files and matched the repository release byte-for-byte, including row/column order and JSON structure. No personal absolute path is required by the build.

The isolated environment ran Python 3.12.13 and `pytest -q`: 3 passed, 0 failed, 0 skipped. The repository virtual environment is ignored by Git.

## End-to-end lineage audit

The build now regenerates `metadata/processed_field_inventory.csv`, `metadata/data_dictionary.csv`, `metadata/scenario_registry.csv`, `metadata/record_lineage.csv`, and `metadata/lineage_coverage_report.csv` after processing. The audit covers 42 processed CSV fields, 911 non-empty value rows, and 100% machine lineage coverage. External source verification is intentionally reported as incomplete (`PASS_WITH_DOCUMENTED_GAPS`) because several original URLs and redistribution terms are unavailable in the current materials; see `docs/provenance_gaps.md`.
