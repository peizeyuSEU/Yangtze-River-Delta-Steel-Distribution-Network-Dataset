# Third-party data and attribution

This document distinguishes repository-produced metadata and processed model
inputs from third-party data, software, services, and publisher content. The
machine-readable inventory is `metadata/third_party_data_inventory.csv`.

## Components

- GeoNames city-centre coordinates are attributed to GeoNames under CC BY 4.0.
- Road-network distances use OSRM with OpenStreetMap map data. OpenStreetMap
  attribution is required under ODbL; the repository does not redistribute the
  complete OSM road database and does not assert a legal Produced Work/Derived
  Database classification for the cached matrix; conservative scope review is
  retained.
- Project OSRM software is separately identified as BSD-2-Clause. OSRM's
  software license does not replace the OSM data license.
- The public OSRM demo service is a service dependency used to generate the
  cached response. The current build is offline and does not promise future
  service availability.
- Statistics, steel-price, and warehouse-rent pages are factual extraction
  sources. Only URLs, factual values, verification metadata, and derived
  parameters are stored; full webpages, images, tables, or article text are not
  redistributed. Publisher/platform terms continue to apply.

## Suggested attribution

Geographical coordinates are derived from GeoNames and are provided with
attribution to GeoNames under CC BY 4.0.

Road-network distances were computed using OSRM with map data from
OpenStreetMap contributors, available under the Open Database License (ODbL).

This is a data-management description, not legal advice. Users must check the
current terms of each third-party platform before redistribution or commercial
use. No blanket relicensing of the repository is asserted.
