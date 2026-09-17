# 03_mobile_sites - column dictionary

One row per mobile site. `source` says which layer it came from; the source-specific
columns are only meaningful for that source (and are False/blank otherwise).

| column | meaning |
|---|---|
| source | `acma` (carrier cellular site from the ACMA licence register), `guide` (NT coverage guide spreadsheet), or `mbsp` (Mobile Black Spot Program funded site) |
| name | site name / location |
| latitude / longitude | point location, EPSG:4326 |
| site_type | guide: VILLAGE / HOMELAND / ROADHOUSE etc; mbsp: base-station type text; blank for acma |
| carriers | `;`-separated. acma: carriers with a licensed device on the site; guide: the guide's PROVIDER field; mbsp: the grant recipient |
| n_carriers | number of carriers in `carriers` (only used downstream for acma) |
| guide_macro / guide_small / guide_proximity | guide rows only: the guide flags this site as macro-cell coverage / small-cell coverage / near coverage |
| mbsp_round | mbsp rows only: funding round |
| mbsp_is_small | mbsp rows only: the funded solution is a small / micro cell |
| mbsp_built | mbsp rows only: Site_Status is 'Complete' |
