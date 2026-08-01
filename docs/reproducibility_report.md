# Reproducibility report

Command: `python scripts/build_all.py --config config/baseline.json`.

The build completed offline from `data/raw/public` and `data/cache/osrm_response.json`, producing 16 nodes, 8 supplier–DC arcs, 120 DC–market arcs, and 15 market parameter records. No GA-BP, branch-and-price, CPLEX, or network request was used. Pytest was not available in the bundled runtime at build time and must be installed before CI execution.
