# Original public-source recovery report

This report records the recovery of source URLs and source metadata from
`长三角钢材配送案例_公开数据校准包_v2.xlsx` (SHA-256
`DA93615FF0A440843378A1763600FC5EEEE0C570585A2811B7188782D234F91B`). The
workbook remains outside the repository; only its record-level provenance is
stored in `metadata/source_recovery_register.csv`.

## Scope

- 16 city-centre coordinate records (`NODE_*`), with GeoNames as the stated
  coordinate source. These are screening coordinates, not enterprise addresses.
- 15 statistical proxy records (`STAT_*`) used to construct demand weights.
- 15 steel-price records (`PRICE_*`) used for screening values.
- 8 warehouse-rent records (`RENT_*`) used for screening values.

All 54 records have a recovered URL or an explicit public-source endpoint in
the register. The URLs are retained as metadata only; no webpage copies,
screenshots, credentials, or external content are redistributed.

## Verification status

`verified_metadata_only` is used where the workbook identifies a stable
publisher endpoint but the value itself is a structured workbook observation.
`pending_manual_review` is used for record-level statistics, price, and rent
pages whose current content, access controls, or historical snapshot still
requires human confirmation. The Jinhua (`M15`) page is recorded as
`verified_page_but_value_unavailable`: it is a page reference, not a direct
Jinhua price observation.

The register is intentionally conservative. HTTP reachability alone is not
treated as proof that a historical value is still visible or unchanged.

### Statistical records (15)

The 2026-08-02 review records 14 `verified_exact`, 0
`verified_metadata_only`, and 1 `pending_manual_review`; no value mismatch was
found. `STAT_M09` retains its original Changzhou government URL and has
supplementary official evidence: the Changzhou Statistics Bureau 2024
economic-operation/statistical-bulletin pages confirm 5139.4 billion CNY even
though automated parsing did not expose the original body value. `STAT_C08`
retains the original Jiaxing Statistics Bureau PDF URL; a public bulletin mirror
cross-checks 3751.81 billion CNY, while the original PDF still requires manual
browser confirmation. `verified_exact` describes an exact page/value match and
does not mean that the page is the official originating source: C05, C07, M13,
and M15 are explicitly marked as media or bulletin mirrors where applicable.

### Steel-price records (15)

The 2026-08-02 review records 6 `verified_exact`, 3
`verified_page_but_value_unavailable`, 0 `content_changed`, and 6
`pending_manual_review`. No recovered numeric value was changed. PRICE_C03 is
supported by a search-indexed historical snapshot; the dynamic regional entry
may show another date when opened later and must not be confused with the
historical snapshot. PRICE_C06 and PRICE_M10 have supplementary same-day
market-flash evidence. PRICE_C08 has a Jiaxing quotation page showing
2026-06-30, HRB400E Φ20, and 3440 CNY/t. PRICE_M09 and PRICE_M11 are exact
historical ranges whose recorded values are the stated two-quotation midpoints.
Dynamic or restricted pages are not treated as exact merely because a URL
responds.

The interval-midpoint records are PRICE_C04 (3310--3370 → 3340), PRICE_M09
(3240--3290 → 3265), and PRICE_M11 (3190--3290 → 3240). PRICE_C06 remains a
brand-specific Zhongtian observation; PRICE_M13 uses a Φ18--22 specification
band. These date/specification/brand qualifications remain in the register.
PRICE_M15 remains a proxy: its value is constructed from PRICE_C05,
PRICE_C08, and PRICE_M12; the linked page is supporting context and not a
direct Jinhua quotation.

## Explicit proxy and licensing notes

- `PRICE_M15` remains a proxy constructed from Hangzhou, Jiaxing, and Shaoxing
  screening observations. It must not be described as an observed Jinhua quote.
- City statistics, steel quotations, and warehouse listings may have publisher
  terms that change. Review those terms before redistribution or commercial use.
- GeoNames data are attributed separately from OSRM routing and OSM map data;
  these sources must not be conflated.
