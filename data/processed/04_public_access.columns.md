# 04_public_access - column dictionary

One row per public / last-resort access point in the NT (RICT and STAND combined).

| column | meaning |
|---|---|
| source | `rict` (Remote Indigenous Communications payphone / Wi-Fi phone, NIAA) or `stand` (Strengthening Telecommunications Against Natural Disasters site) |
| name | community name (rict) or site name (stand) |
| latitude / longitude | point location, EPSG:4326 |
| detail | rict: site_type code (e.g. WP = Wi-Fi phone); stand: the Public_Access description |

The NBN footprint polygons are in the sibling file 04_nbn_footprint.geojson
(one dissolved polygon per `technology`: fixed_line, fixed_wireless).
