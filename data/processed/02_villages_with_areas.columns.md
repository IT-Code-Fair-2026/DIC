# 02_villages_with_areas - column dictionary

One row per BushTel community. Columns community_id .. population_bushtel_source are
unchanged from 01_communities (see 01_communities.columns.md). Added here:

| column | meaning |
|---|---|
| sa1_code | ABS 2021 SA1 the community point falls inside |
| sa2_name | name of the SA2 that SA1 belongs to (for orientation) |
| iloc_code | ABS 2021 ILOC (Indigenous Location) the community point falls inside |
| iloc_name | ILOC name |

No census population is attached at village level - see 02_sa1_report for population.
