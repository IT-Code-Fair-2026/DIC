# 01_communities - column dictionary

One row per BushTel remote community in the Northern Territory.

| column | meaning |
|---|---|
| community_id | BushTel's stable numeric identifier for the community |
| community_name | BushTel community name (upper case, as published) |
| community_aliases | other names for the community, comma-separated; blank if none |
| community_type | BushTel classification: Family Outstation, Town Camp, Minor, Major, Village, Town, City |
| latitude | community point latitude, decimal degrees (EPSG:4326) |
| longitude | community point longitude, decimal degrees (EPSG:4326) |
| land_council | land council area (e.g. Central Land Council, Northern Land Council) |
| local_govt_council | local government area the community sits in |
| ntg_region | NT Government administrative region |
| ward | local government ward |
| electorate | NT Legislative Assembly electorate |
| main_language | main language spoken, as recorded by BushTel ("Not recorded" if unknown) |
| population_bushtel_2024 | BushTel's own population count; blank for the 335 communities BushTel does not record |
| population_bushtel_source | BushTel's note on where its number came from: "Homelands Service Provider Report 2023", "Based on ABS 2021 Census SA1", or "Not recorded" |
| bushtel_url | link to the community's page on bushtel.nt.gov.au |
