# Task: rebuild the NT remote-connectivity pipeline as Jupyter notebooks, EDA first

Read these before writing anything, in this order:
1. `docs/PROJECT_CONTEXT.md` — standing rules and decisions. They are binding.
2. `docs/DATASET_INVENTORY.md` and `docs/DATA_DICTIONARY.md`
3. `connecitivity_analysis.ipynb`, `population_distribution_analsis.ipynb`, `nbn_rict_stand.ipynb` — the current code. These are the source of truth for how files are actually read (header rows, CRS, join keys, filters). `data/README.md` is outdated; ignore it where it disagrees with the notebooks.

Do NOT modify or delete the three existing notebooks. Build the new notebooks alongside them in `notebooks/`.

## Standing rules (from PROJECT_CONTEXT.md — do not violate)

- BushTel `community_id` is the spine. Every people-side fact hangs off a village; every infrastructure fact is *measured from* a village.
- Census 2021 (`Tot_P_P` at SA1) is the only real population. BushTel `population_count` and coverage-guide `POPULATION` are reference only — never summed, never used as population.
- Village is the unit for distance. SA1 is the unit for population and equity. A census figure is never split across villages in an SA1.
- Distances are straight-line triage, not coverage claims. Say so in the markdown cell above every distance calculation.
- Don't assume — inspect the file. If a decision is not covered below, stop and ask me before choosing.
- Read `sa1_code` as string everywhere.
- Never load `device_details.csv` fully (2.15M rows). Filter to NT `SITE_ID`s first or read in chunks with `usecols`.

## The design: sources add COLUMNS to villages, never ROWS to a shared table

The current `mobile_sites` table stacks three different kinds of thing (licensed towers, coverage claims, funding records) as rows with shared column names. That is what we are removing. Each source gets its own tidy notebook and output file; notebook 06 measures each one from the 792 villages and writes the result as columns.

---

## Delivery format — read this section twice

**Everything is a Jupyter notebook (`.ipynb`).** No `.py` files in this phase. Python scripts are a later submission step handled separately.

### Fixed cell layout for every notebook
1. **Cell 1 — title markdown.** Notebook name, one paragraph: what this notebook does, what it reads, what it writes, why it exists.
2. **Cell 2 — all imports.** Every `import` in the whole notebook lives here. Nothing imported anywhere else.
3. **Cell 3 — all file reads.** Every raw/external/processed file the notebook needs is read here, one line each, into a clearly named dataframe:
   `bushtel_communities_df = gpd.read_file("data/raw/bushtel/Com_BushTel_Profile_CMC_2024.json")`
   No file is opened anywhere else in the notebook, at any stage. If a read needs preprocessing (e.g. finding the header row of the coverage-guide xlsx, chunked reading of `device_details`), the raw read still happens here; the tidy-up happens in the next cell.
4. **Middle cells — the work.** A markdown cell before every major step saying what is about to happen and why, in plain English. Inline comments on any line whose intent isn't obvious.
5. **Second-to-last cell — summary print.** 3–5 lines: rows in, rows out, anything dropped and why, asserts passed.
6. **Last cell — all file writes.** Every `.to_csv` / `.to_file` in the notebook lives here and nowhere else. Nothing is written until everything above has run and been checked.

### Naming — the reader must understand intent from the name alone
- Dataframe names say **what the data is**, not where it came from in the code: `coverage_guide_df`, not `raw` / `guide_rows`. `acma_sites_df`, `acma_licences_df`, `acma_devices_df`, `mbsp_funded_sites_df`, `rict_public_access_df`, `census_g01_sa1_df`, `sa1_polygons_gdf`, `iloc_polygons_gdf`.
- Suffix `_df` for pandas, `_gdf` for geopandas.
- When a frame is transformed into something new, the new name says what changed: `coverage_guide_df` → `coverage_guide_nt_df` → `coverage_guide_flags_df`. Never overwrite a name with something that means something different.
- Output file names say what one row is: `villages.csv` (one row per village), `towers.csv` (one row per tower site), `village_gap.csv` (one row per village with gap measures).
- Constants in UPPER_CASE at the top of the cell that uses them, with a comment saying why that value (`GAP_KM = 15  # triage cutoff; not a validated coverage radius`).

### Documentation replaces the old docstring convention
No WHAT/READS/WRITES/WHY/RUN block. Instead: the title markdown cell (cell 1) plus a markdown cell above each major step. Together they should let someone who has never seen the repo follow the notebook top to bottom.

### Visual validation of every join — mandatory
Last time joins were only asserted, never looked at. That must not happen again. **Every join** — spatial join, `sjoin_nearest`, `merge`, roll-up/groupby, concat — gets a validation cell immediately after it that makes correctness *visible* using the data itself, for example:
- Row counts before / after, and count of rows that failed to match, printed side by side.
- A map of the joined points over the polygons they were joined to (e.g. villages coloured by `sa1_code` on top of SA1 boundaries; a handful of unmatched or suspicious points highlighted).
- For nearest-neighbour joins: a histogram of the distances, and a map drawing a line from each of ~20 sample villages to its matched tower so the match can be eyeballed.
- For merges on a key: which keys exist on only one side, listed.
- For roll-ups: a spot check — pick 3 SA1s, show the villages in them, show the roll-up row, confirm by eye.
- For distribution-changing steps: a before/after histogram or value_counts.

The same applies to any **filter, aggregation, or derived column** that can be sanity-checked: show how many rows each filter step removed and a sample of what was removed; show the derived column against the inputs that produced it. Don't state that logic is correct — show it.

Use matplotlib / geopandas `.plot()` inline. Keep plots simple and labelled; they are checks, not report figures.

### Guards every notebook keeps (from the original prompt)
- Assert the expected key is unique and the row count matches the table below; fail loudly, never write a wrong-shaped file.
- Never build a column list from a frame other than the one being written (this bug bit us last session). Write column lists out explicitly.
- Summary print in the second-to-last cell.

---

## Notebooks to create, in order

Work **one notebook at a time**. After each: run it top to bottom, show me the summary print, the first 5 rows of each output, and the validation plots that matter most, then **stop and wait for my review** before starting the next.

### Phase A — EDA / data understanding (new, do these first)

#### `00a_eda_population_census.ipynb`
Explore before using: BushTel communities, Census G01 and G02 (SA1, NT), SA1 polygons, ILOC polygons, RA workbook.
Surface at least:
- BushTel: `community_type` counts; how many have `population_count`; what `population_source` values exist; the `community_aliases` field (how many, what they look like); the duplicate `community_id` (793 rows vs 792 features) — find it and show it; points on a map coloured by type.
- Census G01: distribution of `Tot_P_P` across the 649 NT SA1s (histogram, log scale); how many SA1s have 0 or tiny population; where they are (map). G02: distributions of `Median_tot_hhd_inc_weekly`, `Average_household_size`; how many nulls and why (ABS suppression).
- SA1 polygons: area distribution; the 4 codes with no polygon; join `sa1_code` string type check (leading zeros, dtype).
- ILOC: how many NT ILOCs, area distribution, map.
- RA workbook: remoteness counts for NT SA1s; map.
- Data-quality list at the end: every issue found, one line each, with what the pipeline will do about it.
No outputs written by this notebook except plots (save the important ones to `docs/eda/`).

#### `00b_eda_connectivity.ipynb`
Explore before using: ACMA `site`, `licence`, `client`, `device_details` (NT subset only); NBN fixed-line and fixed-wireless shapefiles; MBSP KMLs; coverage-guide xlsx; RICT JSON.
Surface at least:
- ACMA: NT site count; `DEVICE_TYPE` code values and what they mean (inspect, don't assume); `FREQUENCY` and `BANDWIDTH` units and distributions; which `LICENCE_CATEGORY_NAME` values carrier licences fall in; how many sites per carrier; how the current 16-band list breaks down into handset bands vs everything else; sites with a neighbour within 100 m (how many, sample); `SITE_PRECISION` values.
- NBN: attribute columns (there's only a polygon id — confirm); polygon count inside the NT bbox; map of the footprint.
- MBSP: field schema per round (which columns exist in which files); the 5 spellings of `site_type`; built vs not; map.
- Coverage guide: header row position; `SITE TYPE` counts; how the MACRO / SMALL / PROXIMITY flags combine (crosstab); the contradiction where `PROXIMITY` is YES but no tower is nearby — quantify it against ACMA sites.
- RICT: **print every property key** and value counts for `site_type` and any service-indicator fields, and **stop** — I will decide which to keep before the pipeline notebook uses them.
- Overlay map: ACMA sites, MBSP built / unbuilt, coverage-guide places, all in different colours over NT.
- Data-quality list at the end, same format as 00a.

### Phase B — pipeline notebooks (same sequence as before)

| Notebook | Reads | Writes to `data/new_processed/` | Key, expected rows |
|---|---|---|---|
| `01_villages.ipynb` | BushTel JSON; SA1 shp; ILOC shp; RA xlsx | `villages.csv` + `.geojson` | `community_id`, 792 |
| `02_sa1_report.ipynb` | SA1 shp; RA xlsx; Census G01, G02; `villages.csv` | `sa1_report.csv` + `.geojson` | `sa1_code`, 649 (geojson 645) |
| `03_towers.ipynb` | ACMA `site`, `licence`, `client`, `device_details` | `towers.csv` + `.geojson` | `site_id`, 1 per site with ≥1 carrier transmitter in a handset band |
| `04_nbn_footprint.ipynb` | NBN fixedline + wireless shp | `nbn_footprint.geojson` | `technology`, 2 polygons |
| `05_program_sites.ipynb` | MBSP KMLs; coverage-guide xlsx; RICT JSON | `program_sites.csv` + `.geojson` | `program_site_id`, 1 per site, `source` ∈ {mbsp, guide, rict} |
| `06_village_gap.ipynb` | **only** outputs of 01, 03, 04, 05 | `village_gap.csv` + `.geojson` | `community_id`, 792 |
| `07_sa1_gap.ipynb` | **only** `village_gap.csv` + `sa1_report.csv` | `sa1_gap.csv` + `.geojson` | `sa1_code`, 649 |

Rule: notebooks 01–05 read raw/external only. 06–07 read `new_processed/` only.

#### 01_villages.ipynb
Port from `population_distribution_analsis.ipynb` steps 01–02. Spatial-join (within) villages to SA1 and ILOC polygons in EPSG:7844; join RA workbook on `SA1_CODE_2021` for `remoteness_name`. Rename `population_count` → `population_bushtel_2024` (reference only). Assert 0 unmatched. Handle the duplicate `community_id` the way we decide after 00a. **Validate:** map of villages coloured by `sa1_code` over SA1 polygons; map over ILOC polygons; count of villages per SA1 as a bar chart; list of any village whose SA1 and ILOC disagree on region.

#### 02_sa1_report.ipynb
Port the `sa1_report` build. Columns as in PROJECT_CONTEXT §5. Roll-up from `villages.csv`: `n_villages`, `village_names`. Merge polygons with `validate="1:1"`, drop null geometry for the geojson. **Validate:** keys on one side only (census vs shapefile vs RA); spot-check 3 SA1s' roll-up rows against their villages; choropleth of `pop_census_2021` and `n_villages`.

#### 03_towers.ipynb — the one that changes most
Keep the carrier-name matching (`client.LICENCEE` contains TELSTRA/OPTUS/VODAFONE/TPG/HUTCHISON/PIVOTEL/DENSE AIR). From `device_details` restricted to NT sites and those licences, keep only transmitters (`DEVICE_TYPE` code found in 00b) with `FREQUENCY` in handset bands (700, 850, 900, 1800, 2100 MHz; unit confirmed in 00b). Add `handset_band` boolean so nothing is dropped silently. Group to one row per `SITE_ID`: `latitude`, `longitude`, `name`, `carriers` (semicolon list), `n_carriers`, `n_transmitters`, `bands`, `spectrum_depth_khz` (sum of `BANDWIDTH` across handset-band transmitters), `max_eirp`, `max_height`, `is_pivotel`. Markdown must say `spectrum_depth` is a *relative* capacity indicator, not a speed, and a licence is permission to transmit, not proof the site is on air. **Validate:** a funnel chart/print of site counts after each filter; the old 458 "acma" sites vs the new set — which dropped and why (by band); map of the new towers coloured by carrier; histogram of `spectrum_depth_khz`.

#### 04_nbn_footprint.ipynb
Port from `nbn_rict_stand.ipynb`. NT bbox, EPSG:4283 → 4326, dissolve per technology. **Validate:** polygon count before/after dissolve; map of both footprints over NT with the villages on top.

#### 05_program_sites.ipynb
One tidy schema: `program_site_id, source, name, latitude, longitude` plus source-prefixed columns.
- **mbsp**: dedupe on `MBSP_ID`; normalise `site_type` → macro / small / micro (show me the mapping); `mbsp_built`, `mbsp_round`.
- **guide**: `guide_macro`, `guide_small`, `guide_proximity`, `guide_place_type`, `guide_population` (reference only).
- **rict**: columns decided after 00b.
STAND is dropped. Do not read it. **Validate:** row counts per source before/after dedupe; map coloured by source; MBSP built vs unbuilt on a map.

#### 06_village_gap.ipynb — the answer table
One row per village. All distance work in EPSG:3577 with `gpd.sjoin_nearest`. Columns:
- from 01: pass-through id/name/type/lat/lon, `sa1_code`, `iloc_code`, `remoteness_name`
- from 03: `km_nearest_tower`, `nearest_tower_carriers`, `nearest_tower_spectrum_depth_khz`, `n_towers_10km`, `n_carriers_10km`
- from 04: `in_nbn_fixed_line`, `in_nbn_fixed_wireless`
- from 05 mbsp: `km_nearest_built_mbsp`, `km_nearest_unbuilt_mbsp`, `nearest_unbuilt_mbsp_round`
- from 05 guide: `guide_match_name`, `guide_match_km`, `guide_says_covered`, `guide_proximity_only`. Match nearest guide place ≤ 2 km, then check `community_name` / `community_aliases` against `SITE NAME`. Unmatched → NaN.
- from 05 rict: `has_rict_public_access`
- `distance_gap_candidate` = no guide macro/small AND `km_nearest_tower` > `GAP_KM` (default 15). Not `likely_gap`.
- `tier` — stub returning NaN with a TODO; I define T1–T5 after seeing the columns.
No population column here. **Validate every join:** histogram of `km_nearest_tower`; map with lines from ~20 sample villages to their nearest tower; guide-match breakdown (matched by distance / by name / both / neither) as a table and a map of the unmatched; villages inside vs outside NBN footprint on a map; crosstab of `distance_gap_candidate` vs `guide_proximity_only`.

#### 07_sa1_gap.ipynb
Roll `village_gap.csv` to `sa1_code`: `n_villages`, `n_villages_gap_candidate`, `share_villages_gap_candidate`, `median_km_nearest_tower`, `n_villages_in_nbn_fixed`, `n_villages_with_rict`, `n_towers_in_sa1`. Join `sa1_report.csv`; `people_per_tower` (NaN when 0 towers — no divide by zero). Geojson = polygons + these columns. **Validate:** keys on one side only; spot-check 3 SA1s against their `village_gap` rows; choropleths of `share_villages_gap_candidate` and `people_per_tower`.

---

## Housekeeping (after 07 runs clean and I confirm)
- Move the three old notebooks to `archive/`.
- Move `data/processed/` and stale `new_processed/` files (`communities.*`, old `sa1_report.geojson`, `mobile_sites.*`, `community_connectivity_priority.csv`, `public_access.*`, `03_mobile_sites.columns.md`) to `archive/data/` — list them, ask, then move.
- Update `docs/DATASET_INVENTORY.md`: add a "read by" column naming the notebook; untick STAND ("parked — dropped, no unique signal").
- Regenerate `docs/DATA_DICTIONARY.md` for the seven output files only, plus a join-key page.
- `README.md` at repo root: how to run the notebooks in order, where inputs sit, what each output is, ≤ 60 lines.

## How to work
- One notebook at a time; run it end to end; show me summary, head(5) of outputs, and key validation plots; stop for review.
- Stop and ask at every point marked "ask", "stop", "tell me", "show me", or "decide".
- Plain English in every markdown cell and comment. No jargon without a one-line explanation.
- If the fixed cell layout (imports cell 2, reads cell 3, writes last cell) is impossible for a notebook, say why and ask before deviating.
