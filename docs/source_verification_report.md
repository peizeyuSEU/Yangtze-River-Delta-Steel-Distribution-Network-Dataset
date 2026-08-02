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

The 2026-08-02 review records 11 `verified_exact`, 3
`verified_page_but_value_unavailable`, 0 `content_changed`, and 1
`pending_manual_review`. No recovered numeric value was changed. PRICE_C01,
PRICE_C02, PRICE_C05, and PRICE_C07 are supported by the same-day national
city market table; PRICE_M14 is supported by a same-day Wuhu city market table.
Supplementary evidence never replaces the original source URL. PRICE_C03 is
supported by a search-indexed historical snapshot; the dynamic regional entry
may show another date when opened later and must not be confused with the
historical snapshot. PRICE_C06 and PRICE_M10 have supplementary same-day
market-flash evidence. PRICE_C08 has a Jiaxing quotation page showing
2026-06-30, HRB400E Φ20, and 3440 CNY/t. PRICE_M09 and PRICE_M11 are exact
historical ranges whose recorded values are the stated two-quotation midpoints.
Dynamic or restricted pages are not treated as exact merely because a URL
responds.

The supplementary review did not upgrade PRICE_C04 or PRICE_M13 because the
available evidence was not fully machine-readable for the recorded historical
rows. C04 retains its 3310--3370 midpoint (3340); the Mysteel supplementary
URL returned a restricted response. M13 retains its 3260 value and Phi18--22
band; the indexed Huzhou page is supporting evidence, but the retrievable page
does not expose the 2026-06-18 row. Both records therefore remain
`verified_page_but_value_unavailable`, with original URLs and values unchanged.

The interval-midpoint records are PRICE_C04 (3310--3370 → 3340), PRICE_M09
(3240--3290 → 3265), and PRICE_M11 (3190--3290 → 3240). PRICE_C06 remains a
brand-specific Zhongtian observation; PRICE_M13 uses a Φ18--22 specification
band. These date/specification/brand qualifications remain in the register.
PRICE_M15 remains a proxy: its value is constructed from PRICE_C05,
PRICE_C08, and PRICE_M12; the linked page is supporting context and not a
direct Jinhua quotation.

### Warehouse-rent records (8)

The 2026-08-02 review records 6 `verified_exact`, 0
`verified_page_but_value_unavailable`, 0 `blocked`, 0 `dead_link`, 0
`content_changed`, and 2 `pending_manual_review`; no numeric mismatch was
found. RENT_C01 is a CBRE Shanghai citywide logistics-market average. RENT_C03,
RENT_C04, RENT_C05, RENT_C06, and RENT_C08 are 58.com city-average trend
observations; they are not transaction rents. Their monthly values are the
stated 30-day conversions from the daily values (0.75→22.5, 0.66→19.8,
0.70→21, 0.74→22.2, and 0.50→15 CNY/m²/month). RENT_C02 remains a specific
Nanjing listing and RENT_C07 remains a Feixi high-standard listing; both need
manual browser or historical-snapshot confirmation and must not be described
as city averages. All rent values remain screening/calibration inputs.

## Explicit proxy and licensing notes

- `PRICE_M15` remains a proxy constructed from Hangzhou, Jiaxing, and Shaoxing
  screening observations. It must not be described as an observed Jinhua quote.
- City statistics, steel quotations, and warehouse listings may have publisher
  terms that change. Review those terms before redistribution or commercial use.
- GeoNames data are attributed separately from OSRM routing and OSM map data;
  these sources must not be conflated.
