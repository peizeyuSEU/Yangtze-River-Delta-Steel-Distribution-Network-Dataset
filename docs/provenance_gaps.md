# Provenance gaps and review actions

| gap_id | variables/records | current treatment | risk | next action |
|---|---|---|---|---|
| GAP-001 | city statistics, steel prices, rents | record-level URLs recovered in `metadata/source_recovery_register.csv` | historical pages and terms still require manual confirmation | verify each page/value before a public release |
| GAP-002 | Jinhua steel price | explicit proxy flag | not a direct Jinhua observation | document proxy basis and review suitability |
| GAP-003 | warehouse rents | listing-based records | listing license/status may change | manually review listing provenance |
| GAP-004 | OSRM/OSM cache | cached response and derived distances | attribution/ODbL review required | confirm attribution and redistribution terms |
| GAP-005 | carbon quota C | not generated | requires future E0 model solve | keep as not_yet_generated; do not invent value |

Machine lineage is complete for the generated processed fields, but external source verification is not complete.

The recovery workbook is documented in `docs/source_verification_report.md`. It
was not copied into this repository.
