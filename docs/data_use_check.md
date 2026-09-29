# Data-use check — what the notebooks actually read

**Scope:** every cell of all 8 notebooks in `notebooks/`.
**Date of check:** 2026-09-26 · branch `cleanup` (HEAD `163709b`)
**Method:** the notebooks were parsed as JSON and every `source` line of every cell was
extracted to plain text and read — 2,484 lines of code across 131 code cells. Markdown
prose was extracted separately and used only for cross-checking at the end, never as
evidence. Row counts quoted below are the notebooks' own stored execution outputs; file
existence, sizes, shapes and git state were verified against disk.

---

## 1. Verdict

The notebooks read **9 distinct source datasets** (18 files, ~1.1 GB on disk), all of them
local under `data/`. There are **no network calls, no APIs, no download steps and no
absolute paths** anywhere in the 8 notebooks — every path is repo-relative, and each
notebook does `os.chdir("..")` if launched from `notebooks/`.

The 9 datasets:

| # | Dataset | Where | Read by |
|---|---------|-------|---------|
| 1 | **BushTel** Community Profile 2024 (792 NT communities) | `data/raw/bushtel/` | 00a, 01, 04 |
| 2 | **ABS 2021 Census GCP** — G01 + G02, **SA1 level, NT only** | `data/raw/census_gcp_2021/` | 00a, 02 |
| 3 | **ABS ASGS 2021 SA1** boundaries (shapefile) | `data/external/abs_boundaries/` | 00a, 01, 02 |
| 4 | **ABS ASGS 2021 ILOC** boundaries (shapefile) | `data/external/abs_boundaries/` | 00a only |
| 5 | **ABS Remoteness Area 2021** workbook (`RA_2021_AUST.xlsx`, SA1→RA) | `data/external/abs_boundaries/` | 00a, 01, 02 |
| 6 | **ACMA RRL** — 4 of the 27 CSVs (`site`, `licence`, `client`, `device_details`) | `data/external/acma_rrl/` | 00b, 03 |
| 7 | **NBN** fixed-line + fixed-wireless footprints (shapefiles) | `data/external/nbn/` | 00b, 04 |
| 8 | **MBSP** funded base stations — 8 KMLs (rounds 1–7 + 5A) | `data/external/mbsp/` | 00b, 05 |
| 9 | **NT mobile coverage guide** xlsx + **RICT** community JSON | `data/raw/nt_mobile_coverage/`, `data/raw/rict/` | 00b, 05 |

Plus 4 intermediate files the notebooks produce and re-read themselves
(`villages.csv` / `.geojson`, `towers.csv`, `nbn_footprint.geojson`, `program_sites.csv`).

---

## 2. Every file read, line by line

Each notebook concentrates all I/O in cell 2, so this table is exhaustive.

| Source file | Size | Read call | Read-time filter | Rows returned |
|---|---|---|---|---|
| `raw/bushtel/Com_BushTel_Profile_CMC_2024.json` | 488K | `gpd.read_file` | none | 792 points, EPSG:4326 |
| `raw/census_gcp_2021/…/SA1/NT/2021Census_G01_NT_SA1.csv` | 200K | `pd.read_csv(dtype={"SA1_CODE_2021": str})` | none (file is NT/SA1 already) | 649 × 109 cols |
| `raw/census_gcp_2021/…/SA1/NT/2021Census_G02_NT_SA1.csv` | 28K | `pd.read_csv(dtype=…str)` | none | 649 × 9 cols |
| `external/abs_boundaries/SA1_2021_AUST_GDA2020_SHP/….shp` | 147M | `gpd.read_file(where=…)` | `STE_NAME21 = 'Northern Territory'` | 649 of 61,845 |
| `external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/….shp` | — | `gpd.read_file(where=…)` | same WHERE | 189 of 1,139 |
| `external/abs_boundaries/RA_2021_AUST.xlsx` | 3.1M | `pd.read_excel(sheet_name="SA1_RA_2021_AUST")` | read whole, NT filtered in-frame | 61,845 → 649 |
| `external/acma_rrl/site.csv` | 13M | `pd.read_csv(dtype=str)` | read whole | 129,492 (NT: 3,771) |
| `external/acma_rrl/licence.csv` | 20M | `pd.read_csv(usecols=3)` | `LICENCE_NO, CLIENT_NO, LICENCE_CATEGORY_NAME` | 164,205 |
| `external/acma_rrl/client.csv` | 1.6M | `pd.read_csv(usecols=2)` | `CLIENT_NO, LICENCEE` | 14,332 |
| `external/acma_rrl/device_details.csv` | 367M | `pd.read_csv(usecols=12, chunksize=200_000)` | streamed; kept only `SITE_ID` in the NT site-id set | 2.15M → **26,767** |
| `external/nbn/fixedline/nbn_coverage_fixedline.shp` | 14M | `gpd.read_file(bbox=NT_BBOX)` | bbox `(128.9, -26.3, 138.1, -10.8)` | 35 polygons |
| `external/nbn/wireless/nbn_coverage_wireless.shp` | 624M | `gpd.read_file(bbox=NT_BBOX)` | same bbox | 348 polygons |
| `external/mbsp/MBSP - Round *.kml` (8 files) | 6.0M | `glob` + `xml.etree` placemark walk | none at read; `State == "NT"` + dedupe on `MBSP_ID` after | 2,710 → **49** NT |
| `raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx` | 28K | `pd.read_excel(header=None)` | header row found by searching col 0 for `"SITE NAME"` (row index 4) | 193 raw → **188** |
| `raw/rict/Com_RICT_Community_NIAA_2024.json` | 168K | `json.load` → `[f["properties"] …]` | `state == "NT"` after | 535 → **296** NT |

**Intermediates re-read (the notebook-to-notebook contract):**
`new_processed/villages.csv` (→ 02), `villages.geojson` (→ 06), `towers.csv` (→ 06),
`nbn_footprint.geojson` (→ 06), `program_sites.csv` (→ 06).

---

## 3. Which columns are actually touched

Reading a whole file is not the same as using it. Verified field by field:

**BushTel** — 15 fields: `community_id`, `community_name`, `community_aliases`,
`community_type`, `latitude`, `longitude`, `land_council`, `local_govt_council`,
`ntg_region`, `ward`, `electorate`, `main_language`, `bushtel_url`, `population_count`,
`population_source`. The last two are carried as `population_count_bushtel` /
`population_source_bushtel` and explicitly **not** used as the population figure — SA1
census population is the unit (stated in 01's output cell).

**Census G01** — exactly **one** of 109 columns: `Tot_P_P` → `pop_census_2021`, plus the
`SA1_CODE_2021` key. A `< 5` threshold sets `census_pop_suppressed` (34 SA1s).

**Census G02** — 2 of 9: `Median_tot_hhd_inc_weekly`, `Average_household_size`. Zeros are
converted to `NaN` (34 income, 33 household size) because ABS suppresses small counts to 0.

**SA1 shapefile** — `SA1_CODE21`, `SA2_NAME21`, `SA3_NAME21`, `SA4_NAME21`, `geometry`.
`AREASQKM21` is inspected in 00a, but the published `area_sqkm` comes from the RA workbook's
`AREA_ALBERS_SQKM` instead.

**ILOC shapefile** — `ILO_NAME21`, `AREASQKM21`, `geometry`. **EDA only** — nothing from
ILOC reaches any output (01 says as much: no `iloc_*` columns).

**RA workbook** — `SA1_CODE_2021`, `RA_NAME_2021`, `STATE_NAME_2021`, `AREA_ALBERS_SQKM`.
`is_remote` = `RA_NAME_2021` in {Remote Australia, Very Remote Australia}.

**ACMA** — `site.csv`: `SITE_ID`, `NAME`, `LATITUDE`, `LONGITUDE`, `STATE`,
`SITE_PRECISION` (00b notes ~40% are "Unknown" or "Within 100 metres"). `licence.csv`:
`LICENCE_NO`, `CLIENT_NO`, `LICENCE_CATEGORY_NAME`. `client.csv`: `CLIENT_NO`, `LICENCEE`
— string-matched against 7 carrier fragments (TELSTRA, OPTUS, VODAFONE, TPG, HUTCHISON,
PIVOTEL, DENSE AIR), then brands collapsed to physical networks (Vodafone/Hutchison/TPG → TPG).
`device_details.csv`: 12 columns requested, of which `SITE_ID`, `LICENCE_NO`, `DEVICE_TYPE`
(`== "T"`), `FREQUENCY` and `BANDWIDTH` drive the selection; `EIRP`, `TRANSMITTER_POWER`,
`HEIGHT`, `EMISSION`, `POLARISATION` are explored in 00b only.

Tower selection is **frequency-based, not category-based**: a site qualifies if it carries a
carrier transmitter inside one of 5 handset bands (700/850/900/1800/2100 MHz, as explicit Hz
windows). 03 keeps the superseded 16-`LICENCE_CATEGORY_NAME` method alongside purely to
document the delta: 461 sites vs 458, 453 shared, 5 dropped (2.5 GHz capacity-only), 8 added.

**NBN** — **geometry only**. Both shapefiles carry just a polygon id, spelled `polygon_id`
(fixed-line) vs `Polygon_id` (wireless), and no technology or speed field, so `technology`
is assigned from the source filename. Wireless lacks a usable `.prj` in places, so the CRS
is forced to `EPSG:4283`, output as `EPSG:4326`, with areas measured in `EPSG:3577`.

**MBSP KML** — `SimpleData` fields `MBSP_ID`, `State`, `Site_Status`, `Base_Station_Type`
(falling back to `Solution_type`), `Location` (falling back to `Solution_name`), plus the
placemark `coordinates` and the round parsed from the filename. Those two fallbacks are how
schema drift between rounds is absorbed. `Site_Status == "Complete"` → `mbsp_built`
(41 built / 8 not). 5 raw site-type spellings map to 3 (`macro` / `small` / `micro`).

**Coverage guide xlsx** — `SITE NAME`, `SITE TYPE`, `LATITUDE`, `LONGITUDE`, `MACRO CELL`,
`SMALL CELL`, `PROXIMITY TO CELL` (each compared `== "YES"`), and `POPULATION` (carried as
reference only, never used as a population figure).

**RICT JSON** — `objectid`, `community_name`, `state`, `latitude`, `longitude`, `site_type`.
The 4 `site_type` codes (WP 154, CP 106, CPW 23, WH 13) are **not decoded in code** — 00b
records a decision to treat all four as public access; the meanings stay unverified and live
in markdown only.

---

## 4. Notebook dependency graph

```
BushTel ─┬─> 01_villages ──> villages.csv ──> 02_sa1_report ──> sa1_report.csv
SA1 shp ─┤                   villages.geojson ─┐
RA xlsx ─┘                                     │
Census G01/G02 ─────────────> 02_sa1_report    │
ACMA (4 csv) ──────────────> 03_towers ──> towers.csv ───────────┤
NBN (2 shp) ──┬────────────> 04_nbn_footprint ──> nbn_footprint.geojson ─┤
BushTel ──────┘                                                          ├─> 06_village_gap
MBSP + guide + RICT ───────> 05_program_sites ──> program_sites.csv ─────┘      │
                                                                               v
ILOC shp ──> 00a (EDA only, dead end)                            village_gap.csv/.geojson
```

| Notebook | Reads | Writes | Code cells / lines |
|---|---|---|---|
| `00a_eda_population_census` | BushTel, G01, G02, SA1 shp, ILOC shp, RA xlsx | PNGs only (`docs/eda/`) | 20 / 366 |
| `00b_eda_connectivity` | ACMA ×4, NBN ×2, MBSP ×8, guide xlsx, RICT | PNGs only | 24 / 469 |
| `01_villages` | BushTel, SA1 shp, RA xlsx | `villages.csv` (792×20), `villages.geojson` | 14 / 220 |
| `02_sa1_report` | SA1 shp, RA xlsx, G01, G02, `villages.csv` | `sa1_report.csv` (649×14), `.geojson` (645), `area_with_population_lessthan_5.csv` | 16 / 218 |
| `03_towers` | ACMA ×4 | `towers.csv` (431×15), `towers.geojson` | 16 / 404 |
| `04_nbn_footprint` | NBN ×2, BushTel | `nbn_footprint.geojson` (2 rows) | 9 / 139 |
| `05_program_sites` | MBSP ×8, guide xlsx, RICT | `program_sites.csv` (533×14), `.geojson` | 12 / 253 |
| `06_village_gap` | `villages.geojson`, `towers.csv`, `nbn_footprint.geojson`, `program_sites.csv` | `village_gap.csv` (792×31), `.geojson` | 20 / 415 |

All 8 notebooks are stored fully executed, with monotonic `execution_count`, **zero error
outputs**, kernel Python 3.12.3. Every on-disk output shape matches the notebook's own
assertion (verified by re-reading each CSV with pandas).

Analysis constants, all declared in cell 2 and all flagged in-code as triage-only rather
than validated coverage radii: `BUFFER_KM = 10`, `GAP_KM = 15`, `GUIDE_MATCH_KM = 2`,
`RICT_MATCH_KM = 2`, `CLUSTER_M = 100`, distance CRS `EPSG:3577`.

---

## 5. Findings

**5.1 — The ILOC shapefile is missing from the working tree, so `00a` cannot run as it stands.**
`00a` cell 2 reads
`data/external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/ILOC_2021_AUST_GDA2020.shp`.
That directory is tracked in git, but all 10 of its files are staged-deleted on this branch
(`git status` shows ` D` for each), and `find data -iname "*ILOC*"` returns nothing. The same
is true of `external/abs_boundaries/RA_2021_AUST_GDA2020/` (the RA *shapefile*), though no
notebook reads that one. `00a` would fail at cell 2 with a GDAL "No such file" error. Since
nothing from ILOC reaches any output, the fix is either `git restore` of that directory or
dropping the ILOC section from `00a`. Note the RA `.xlsx` — which three notebooks do depend
on — is present and untouched.

**5.2 — Only 2 of 1,904 census CSVs are used.** `data/raw/census_gcp_2021` is 60 MB covering
tables G01–G59 at 16 geography levels. The notebooks read G01 and G02 at SA1/NT only, and
from those two files use 3 columns in total. The other 1,902 files are unused.

**5.3 — Datasets present on disk that no notebook reads.** Not defects, but worth knowing
before anyone assumes they are in the pipeline:

| Path | Status in the notebooks |
|---|---|
| `external/stand/strengthening_telecommunication_against_natural_disaster.json` | Deliberately dropped — 00b and 05 both state "STAND is not read" ("no unique signal") |
| `external/services/_raw/ga_{gp,hospitals,police}_nt.geojson` | Never referenced |
| `raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx` | Never referenced (only `mobile-coverage-all-sites.xlsx` is read) |
| `external/abs_boundaries/SAL_2021_AUST_GDA2020_SHP/` (143 MB) | Never referenced |
| `external/abs_boundaries/RA_2021_AUST_GDA2020/` (shapefile) | Never referenced; also deleted from the tree |
| `external/pump/`, `external/mnhp/` | Empty (`.gitkeep` only) |
| 23 of 27 `external/acma_rrl/*.csv` (including the 167 MB `applic_text_block.csv`) | Never referenced |

Recent git history mentions `small_cells.csv` and provider classification, so the small-cell
xlsx and the services GeoJSONs are most likely consumed by app code outside `notebooks/`.
"Unused" here means unused *by the notebooks*.

**5.4 — `wc -l data/new_processed/villages.csv` says 793, but the file holds 792 records.**
One field on `community_id` 202 (ALI CURUNG) contains an embedded newline inside a quoted
value. Parsed with pandas the shape is exactly (792, 20) and every assertion passes. This is
the same off-by-one that `00a` investigated and attributed to a header row; the actual cause
is the embedded newline, so any downstream consumer that counts lines instead of parsing CSV
will be wrong by one.

**5.5 — Markdown and code agree.** Cross-checking the prose against the code found no
dataset claimed in markdown but absent from the code, and no dataset read by the code but
undocumented. The per-notebook "what it reads / what it writes" headers match cell 2 in
every case, and the row counts quoted in prose match the stored outputs. The one place
markdown goes beyond the code is the RICT `site_type` decode, which markdown itself labels
UNVERIFIED.

---

## 6. Documented provenance

From `data/README.md` — **documented, not verified by this check**. No notebook contacts a
source, so none of these URLs or dates can be confirmed from code:

| Dataset | Publisher | Licence | Retrieved / vintage |
|---|---|---|---|
| BushTel Community Profile 2024 | NT Chief Minister & Cabinet | NT Government open data | supplied by CDU 2026-09-03 |
| RICT community list | National Indigenous Australians Agency | CC-BY 4.0 | supplied by CDU 2026-09-03 |
| NT mobile coverage guide | NT Open Data Portal | NT Government open data | supplied by CDU 2026-09-03 |
| 2021 Census GCP DataPack (NT) | ABS | CC-BY 4.0 | 2026-09-03 |
| ASGS 2021 SA1 / ILOC boundaries, RA workbook | ABS | CC-BY 4.0 | 2026-09-03/04 |
| ACMA RRL full extract (27 CSVs) | ACMA | **ACMA RRL Licence — not CC-BY**; conditions in `external/acma_rrl/LICENCE.TXT` | 2026-09-03, regenerated daily ~6am AEST |
| NBN fixed-line / fixed-wireless footprints | nbn Co via data.gov.au | nbn Co open-data terms | 2026-09-03 (extract dated 2024-03-26) |
| MBSP funded base stations (rounds 1–7, 5A) | Dept of Infrastructure … Communications & the Arts | CC-BY 4.0 | 2026-09-03 |

Two licence points worth carrying forward: the ACMA extract is **not** CC-BY and has usage
conditions of its own, and it is regenerated daily — so the 3,771 NT sites and 461
handset-band sites in these notebooks are a snapshot, not a stable figure.

---

## 7. Coordinate reference systems in play

| CRS | Where |
|---|---|
| `EPSG:4326` (WGS84) | BushTel, RICT, MBSP KML, guide lat/long, all published outputs |
| `EPSG:7844` (GDA2020) | ABS SA1 and ILOC shapefiles as read |
| `EPSG:4283` (GDA94) | NBN shapefiles — forced when `.prj` is absent, reprojected to 4326 |
| `EPSG:3577` (Australian Albers, equal-area) | every distance and area computation |

No notebook computes a distance in degrees; all `sjoin_nearest` and buffer work happens in
EPSG:3577 and is converted to km at the end.
