# 02_sa1_report - column dictionary

One row per NT SA1 (649 total: 179 contain at least one BushTel village, 470 do not).
Gap measures (people_per_serving_asset, share_villages_unserved, the shortlist flag)
and asset counts are added later by 08_make_tables, once the asset layers are loaded.

| column | meaning |
|---|---|
| sa1_code | ABS 2021 SA1 code |
| sa2_name / sa3_name / sa4_name | the larger ABS areas this SA1 sits in (orientation) |
| remoteness_name | ABS 2021 Remoteness Area class (Outer Regional / Remote / Very Remote / ...) |
| area_sqkm | SA1 area in km2 (Albers equal-area) |
| pop_census_2021 | 2021 Census total persons, place of usual residence |
| indigenous_pop_2021 | 2021 Census Aboriginal and/or Torres Strait Islander persons |
| indigenous_share | indigenous_pop_2021 / pop_census_2021 (0-1); blank if SA1 has no people |
| median_hh_income_weekly | 2021 Census median weekly total household income, $ |
| avg_persons_per_bedroom | 2021 Census average persons per bedroom (overcrowding proxy) |
| avg_household_size | 2021 Census average persons per household |
| n_villages | number of BushTel villages whose point falls in this SA1 |
| n_villages_with_bushtel_pop | how many of those villages have a BushTel population figure |
| village_bushtel_pop_sum | sum of the BushTel population figures that exist for those villages |
| village_names | the village names, '; '-separated |
| village_bushtel_pops | the BushTel population per village, same order, 'n/a' where not recorded |
