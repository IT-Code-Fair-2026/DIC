# Code analysis: every notebook and script, what it reads, what it does

**Date of this audit:** 2026-09-29 · branch `cleanup`. Read-only review of every `.ipynb` and
`.py` file in the repo, plus the untracked `data-main/` folder. This is the code-level
companion to the docs already in this folder; it doesn't repeat what they cover well, it
fills the gaps: notebooks 07–11, `app/app.py`, `run_pipeline.py`, and (new) `data-main/`.

| Existing doc | Covers |
|---|---|
| `docs/data_use_check.md` | Line-by-line audit of notebooks `00a`–`06`: every file read, every column touched. Still authoritative; not repeated here. |
| `docs/SERVICES_LAYER.md` | Summary of notebooks `07`–`11` (files, headline numbers, caveats). This doc adds the code-level detail underneath it. |
| `docs/DATASET_INVENTORY.md`, `docs/DATA_DICTIONARY.md`, `data/README.md` | What's on disk, used/unused, provenance, column meanings. |
| `docs/PROJECT_CONTEXT.md` | Why decisions were made, the challenge brief, standing rules. |

---

## 1. Notebooks `00a`–`06` (connectivity half)

No new findings: `docs/data_use_check.md` (2026-09-26) already audited all 8 notebooks that
existed at that time line by line: every file read, every column used, every constant, the
full dependency graph, and 5 named findings (missing ILOC shapefile, since restored; only
2 of 1,904 census CSVs used; datasets on disk but unread; an off-by-one line-count vs.
row-count quirk in `villages.csv`; markdown/code agreement check). Read that file directly
rather than this one for `00a`–`06`. One state change since it was written: the ILOC
shapefile it flagged as missing is present again in the working tree as of this audit
(`data/external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/`, 10 files); `00a` can run.

## 2. Notebooks `07`–`11` (services half)

Verified against `docs/SERVICES_LAYER.md` by reading every code and markdown cell. **All
headline numbers, row counts and file paths in that doc match the code and its stored
outputs exactly**: no material discrepancy.

**Trimmed input columns** (`data/external/services/trimmed/`, confirmed against the raw
files in `data-main/`, see §4):
- `medical_facilities_trimmed.csv`: 8 cols, 181 rows: `source, name, latitude, longitude, medical_class, medical_service_type, medical_suburb, medical_postcode`.
- `emergency_facilities_trimmed.csv`: 8 cols, 152 rows: `source, name, latitude, longitude, emergency_class, emergency_agency, emergency_suburb, emergency_postcode`.
- `school_list_trimmed.csv`: 11 cols, 273 rows, no coordinates: `source, name, school_locality, school_region, school_sector, school_remoteness, school_is_preschool, school_is_primary, school_is_middle, school_is_senior, school_is_faft`.

### `07_services_clean_facilities.ipynb`
Reads the two trimmed facility CSVs (`medical_postcode`/`emergency_postcode` read as `str`).
Asserts all coordinates non-null and inside the NT bbox (`lat ∈ (-26.1, -10.9)`,
`lon ∈ (128.9, 138.1)`).
- `SUBURB_SPREAD_KM = 15`: flags rows >15 km (haversine) from the median lat/lon of same-suburb
  rows → `medical_suburb_far_from_site` (5 flagged, e.g. Ngukurr Health Centre mislabelled
  "Katherine"), `emergency_suburb_far_from_site` (0 flagged). Flags, doesn't fix.
- Medical duplicate org names are kept deliberately (one row per facility-service
  combination); no medical dedup.
- Emergency label fixes: `"Ses Facility"` → `"SES Facility"`; agency
  `"WWW.AFP.GOV.AU"` → `"Australian Federal Police"`; **every** `Ambulance Station` row has
  `emergency_agency` force-set to `"St John Ambulance NT"`, overwriting whatever the source
  said (a documented real-world correction, not derived from the data).
- Emergency dedup: `DUP_KM = 0.5`, greedy same name+class within 0.5 km → 152 → 151 rows
  (drops one duplicate Humpty Doo Metro Fire Facility row).
- Emergency renaming: town-only names (no word matching
  `POLICE|STATION|FIRE|BRIGADE|SES|RESCUE|AMBULANCE|EMERGENCY|OFFICE|CENTRE|UNIT|POST`) get a
  class-derived suffix (69 rows); still-duplicate names after that get `(suburb)` appended (2
  Alice Springs fire stations). Asserts `name` unique afterward.
- **Writes:** `data/processed/medical_services.csv` (181 rows), `emergency_services.csv`
  (151 rows).

### `08_services_geocode_schools.ipynb`
Reads `school_list_trimmed.csv` (273 rows, asserts `name` unique), nb07's two outputs (for
suburb centroids, excluding rows flagged `*_far_from_site`), and
`data/raw/bushtel/Com_BushTel_Profile_CMC_2024.json` (792 communities + aliases).
**Geocoding is a locality gazetteer lookup, not a geocoding API call.** Priority order per
school: (1) medical suburb centroid, (2) emergency suburb centroid, (3) BushTel community
name, (4) BushTel alias. Gazetteer holds 2,156 names (712 BushTel + 1,301 aliases + 101
medical suburbs + 42 emergency suburbs).
- 23 hardcoded `MANUAL_OVERRIDES` for Darwin/Palmerston-area suburbs not otherwise
  resolvable, each cited to a source (mostly Wikipedia, two to lat/long lookup sites); these
  take priority over the gazetteer.
- Match tiers, each stamped into `school_geocode_method`/`school_geocode_precision`:
  manual (44) → exact gazetteer (216) → prefix/shortened-locality (4) → BushTel-name
  substring-in-school-name, whole-word ≥5 letters (7) → region fallback (1, coarse) →
  unmatched (1). Fuzzy matching was deliberately rejected: the notebook records that short
  Darwin suburb names kept fuzzy-matching to distant BushTel aliases.
- `REGION_FALLBACK` is a hardcoded per-DoE-region main town; "Top End" has **no** fallback
  entry on purpose: any future unmatched school in that region would silently fall through
  to `unmatched`.
- Result: 272/273 geocoded (99.6%); precision: suburb 229, community 42, region 1, none 1.
  Unmatched: *Nawarddeken Academy Kunmayali School* (address literally `tba`).
- Validation: all coords in NT bbox; regression check that 9 Katherine schools land within
  5 km of Katherine Hospital.
- **Writes:** `data/processed/school_services.csv` (273 rows, 15 cols).
- Caveats stated in-notebook: locality-only precision (every school in a town shares one
  point); `school_sector` blank for ~60 government preschools; `school_remoteness` blank for
  non-government schools (NTG remoteness is only defined for government schools); both
  attributed to the source data, not a pipeline bug.

### `09_services_combine_sites.ipynb`
Reads only nb07/nb08's three outputs (never touches the trimmed files directly). Maps each
source onto one shared schema: `service_site_id, source, name, latitude, longitude,
geocode_method, geocode_precision, type, facility_class, operator, region, suburb, postcode`.
`service_site_id` = `school-<slug>` / `medical-<i>` / `emergency-<i>`. School `type` =
offered-stage list joined `"; "` (or `"Specialist / other"` if none flagged). Medical/
emergency rows get `geocode_method = "source_supplied"`, `geocode_precision = "site"`: this
means the source gave a coordinate directly, **not** that the coordinate has been verified
accurate (nb07 only flags suburb-*label* mismatches, not raw coordinate error). Validates
`service_site_id` uniqueness, `type` non-null, coords in bbox.
**Writes:** `data/processed/services_sites.csv`: 605 rows (273 school + 181 medical + 151
emergency), 604 with coordinates (the 1 unmatched school excluded).

### `10_small_cells.ipynb`
Reads `data/raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx` via a hand-rolled
`zipfile` + `xml.etree.ElementTree` parse of `xl/sharedStrings.xml` +
`xl/worksheets/sheet1.xml`: **deliberately not** `openpyxl`/`pandas.read_excel`, to avoid the
dependency. Locates the data block by finding the row starting "Location of Small Cell" and
taking the rows below with ≥4 non-empty cells (24 of 26 raw rows) → columns `name, latitude,
longitude, provider`. Validates bbox + no duplicate `(name, provider)` pairs.
**Writes:** `data/processed/small_cells.csv` (24 rows: 20 Optus, 4 Telstra).
**Not consumed by nb11**: this file only feeds the Streamlit app's tower/cell labelling
(`app/app.py`'s `tower_cell_types()`). Small-cell coverage has no effect on the nb11 gap
numbers.

### `11_services_gap.ipynb`
Reads `data/processed/village_gap.csv` (nb06 output, 792 rows, asserts `community_id`
unique) and `data/processed/services_sites.csv` (drops null-coordinate rows → 604 usable: 272
school + 181 medical + 151 emergency). **Method: haversine (great-circle, WGS84) nearest
neighbour, brute-force `np.argmin` per village per source**: explicitly *not* the
`EPSG:3577` projected-CRS method nb03/nb06 use for towers/MBSP; the notebook states this
itself as a known, accepted limitation. `BUFFER_KM = 10`, matching the constant used
elsewhere in the pipeline.
Per source (school/medical/emergency): `km_nearest_<source>`, `nearest_<source>_name`,
`nearest_<source>_type`, `n_<source>_10km`.
Results (verified against stored output): school median 22.44 km / p90 79.36 / max 244.78,
547/792 none within 10 km; medical median 30.18 / p90 100.38 / max 286.94, 588/792 none;
emergency median 30.93 / p90 88.43 / max 244.89, 600/792 none. Of nb06's 384
`distance_gap_candidate` villages, median distance to nearest school/medical/emergency is
39.2/46.2/47.7 km. 162/792 villages have all three within 10 km. The notebook explicitly does
**not** create a combined gap flag; its own words: folding mobile-gap and services-gap
together is "a judgement call for the report, not something to bake into the pipeline
silently."
**Writes:** `data/processed/village_gap_with_services.csv` (792 × 43 cols, nb06's 31 + 12
new), `data/processed/village_services_gap.csv` (792 × 14 cols, compact).

### Discrepancies / oddities found in 07–11 (for a future agent)
1. **nb11's own markdown has a stale filename**: it refers to `services_sites_combined.csv`,
   but nb09 actually writes `services_sites.csv`. `docs/SERVICES_LAYER.md` already has the
   correct name: only nb11's internal prose is wrong. Cosmetic; fix if editing nb11 anyway.
2. **nb11's last stored cell output shows a different machine/user's absolute path**
   (`C:\Users\Aseem\Desktop\DIC\...`, not the current `Saugat Poudel` checkout at
   `C:\projects\codefair\DIC`). This is not a hardcoded path in the *code*: every notebook
   07–11 auto-detects its root by walking up to find a `data/raw` directory; it's just a
   leftover output cell from a collaborator's last run, meaning nb11 hasn't been re-executed
   in this checkout since being pulled in. The row/column counts in that stale output are
   presumably still correct (inputs haven't changed), but don't trust the literal path
   string, and re-run it via `run_pipeline.py --only 11` if you need a clean stored output.
3. **No `try`/`except` anywhere** in any of 07–11 (same fail-fast, assert-heavy style as
   00a–06): a missing/malformed input raises a raw traceback, by design.

## 3. `app/app.py`: the Streamlit dashboard (1,811 lines)

Read directly (full file). Single-file Streamlit app, "NT Deadzone Explorer - Services
Edition," Team ASTRA. Keeps **no data of its own**: reads 5 files straight from
`data/processed/` (`village_gap_with_services.csv`, `sa1_report.csv`, `services_sites.csv`,
`towers.csv`, `small_cells.csv`) via `@st.cache_data`-wrapped loaders, all resolved from
`APP_DIR.parent / "data" / "processed"` so it works from any launch directory.

**Structure:**
- **Tier classification** (`classify()`): unchanged from the original tower-only app:
  `distance_gap_candidate` → "beyond" tier; `n_towers_10km == 0` → "spof" (single point of
  failure); `n_networks_10km <= 1` → "single_net"; else "redundant". Services columns are
  shown everywhere but **never** move a village between tiers: the code comment explains
  this mirrors the project's own rule against letting SA1-level or best-effort-geocoded data
  imply precision it doesn't have.
- **`attach_providers()`**: for every village, which network *operators* (not brands; TPG
  folds in Vodafone/Hutchison per nb03's convention) have a tower within 10 km, via a
  vectorised numpy haversine matrix (not a loop). Drives the `provider_class` filter/colour
  mode and the "sole provider, no backup" framing.
- **`nearby_for_id()` / `nearby_section()`**: per-community nearest tower/school/medical/
  emergency list with live haversine distances (independently recomputed in the app, so can
  differ from nb11's stored values by a few hundred metres: documented in the app's own
  docstring). Tower "cell type" (macro 40 km vs. small 5 km range) is inferred by proximity
  (≤0.5 km) to a `small_cells.csv` site with a matching provider; every other tower is treated
  as macro.
- **Four tabs**: Map (folium, colour-by Tier/Provider/4 distance metrics/Population, click a
  dot to open a detail drawer), Table (sortable/filterable, CSV export), Insights (Altair
  charts: provider dependence, remoteness × tier, tower-distance histogram, service-gap
  counts), **Recommendations** (see below).
- **Recommendations tab siting algorithm**: not just a display feature, actual computation:
  candidate sites = target communities (no-tower or sole-provider villages); demand = each
  candidate's SA1 census population, counted once per SA1 (never split across villages, per
  the project's own population rule). Primary method: **greedy maximum coverage** (proven
  within `(1 - 1/e)` of optimal for this objective, cited to Nemhauser/Wolsey/Fisher 1978).
  Baseline for comparison: population-weighted k-means (k-means++ seeding), each centroid
  snapped to the nearest real community. Both computed with vectorised haversine matrices, not
  a real routing/cost model: explicitly triage, not a costed plan (stated in a code comment
  block kept out of the UI on purpose).
- **Cultural theme**: Aboriginal flag colours as CSS accents only; flag *images* and artwork
  are shown only if the team drops official, unaltered files into `app/assets/flags/` /
  `app/assets/artwork/` (with an `attribution.txt` for artwork); nothing is drawn/generated in
  code. Currently both asset folders hold only `.gitkeep`: no images present, so this part of
  the UI silently does nothing yet.
- Deep-linkable via `st.query_params` (filters, colour mode, selected community all persist
  in the URL) with a "Copy Link" button using a tiny inline JS snippet.

No file writes anywhere in `app.py`: every `download_button` builds its payload in memory
from data already loaded. No network calls except the two Google Fonts `@import` URLs in the
injected CSS and the OpenStreetMap tile server folium points at by default.

## 4. `run_pipeline.py` (62 lines)

Thin CLI wrapper around `nbformat` + `nbconvert.preprocessors.ExecutePreprocessor`. Globs
`notebooks/*.ipynb`, sorts by filename (the `00a`…`11` numbering *is* the run order, no
separate manifest), executes each in place with `metadata.path = ROOT` so every notebook's
relative paths resolve from the repo root regardless of where `run_pipeline.py` is invoked
from, and **overwrites the notebook file** with refreshed outputs after every run (including
on failure, so a traceback is preserved for inspection). `--from NN` / `--only NN` match
notebook filenames by prefix. Per-cell timeout 1800 s (nb03's ~400 MB ACMA register read is
the reason it's that high). Stops at the first failing notebook.

## 5. `data-main/`: untracked folder, confirmed origin of the "missing" raw services files

`data-main/data-main/` (note the doubled folder name) is **untracked** (`git status` shows
`??`), not referenced by any notebook, script, or doc anywhere else in the repo, and not
covered by `.gitignore` (it isn't ignored, it's simply never been `git add`ed). It contains:

```
data-main/data-main/
├── emergency_services_eda.ipynb   (28 code cells, 5.3 MB, embedded plot images)
├── medical_facilities_nt_eda.ipynb (30 code cells, 534 KB)
├── school_eda.ipynb               (31 code cells, 566 KB)
├── emergency_findings.md          (polished write-up of the emergency EDA)
├── medical_findings.md            (polished write-up of the medical EDA)
├── school_findings.md             (polished write-up of the school EDA)
├── emergency_facilities_NORTHERN_TERRITORY.csv   (152 rows, 30 columns)
├── medical_facilities_NT.csv                     (181 rows, 16 columns)
└── School_List_Public_2026_09_12_11_12_43.csv    (273 rows, 16 columns)
```

### The CSVs are the documented missing raw extracts: confirmed, high confidence

`docs/SERVICES_LAYER.md` states: *"The trimmed CSVs are the original raw extracts
(`medical_facilities_NT.csv`, `emergency_facilities_NORTHERN_TERRITORY.csv`,
`School_List_Public_2026_09_12_11_12_43.csv`) cut down to the columns the pipeline uses. The
original raw extracts themselves are not in the repo... put them in
`data/external/services/_raw/`"*, and that target directory exists right now holding only a
`.gitkeep`. The three CSVs in `data-main/` have **exactly those filenames**, matching row
counts (152/181/273, identical to both the trimmed files and the numbers `SERVICES_LAYER.md`
quotes), and their first data rows match the trimmed files' values field-for-field (e.g. the
same facility name, same lat/long to float precision, same class). This is the same
underlying extract, not a different vintage: the raw file is simply the pre-trim, full-column
version:

| File | Raw columns (16–30) | Trimmed columns kept (8–11) |
|---|---|---|
| emergency | `OBJECTID, FEATURETYPE, DESCRIPTON, CLASS, FACILITY_NAME, FACILITY_OPERATIONALSTATUS, FACILITY_ADDRESS, ABS_SUBURB, FACILITY_STATE, ABS_POSTCODE, FACILITY_ATTRIBUTE_SOURCE, FACILITY_ATTRIBUTE_DATE, FACILITY_SOURCE, FACILITY_DATE, FACILITY_SPATIAL_CONFIDENCE, FACILITY_REVISED, COMMENT, FACILITY_LAT, FACILITY_LONG, VALIDATED, GNAF_BUILDING_NAME, GNAF_ADDRESS_DETAIL_PID, GNAF_FORMATTED_ADDRESS, GNAF_CONFIDENCE, GNAF_POSTCODE, GNAF_SUBURB, DISTANCE_TO_GNAF, GNAF_LAT, GNAF_LONG, POSTCODE_MATCH` (30) | `source, name, latitude, longitude, emergency_class, emergency_agency, emergency_suburb, emergency_postcode` |
| medical | `OBJECTID, OPERATIONALSTATUS, ORGANISATION_NAME, ADDRESS, SUBURB, STATE, POSTCODE, LONGITUDE, LATITUDE, NHSD_SERVICE_ID, NHSD_SERVICE_TYPE, GNAF_ADDRESS_DETAIL_PID, GA_CLASS, GA_SOURCE_DATE, GEOM_LONGITUDE, GEOM_LATITUDE` (16) | `source, name, latitude, longitude, medical_class, medical_service_type, medical_suburb, medical_postcode` |
| school | `Name, Physical Address, Postal Address, Region, URI, Email, Telephone Number, Fax Number, Sector, Is FAFT School, Is Pre School, Is Primary School, Is Middle School, Is Senior School, Principal, NTG Remote Definition` (16) | `source, name, school_locality, school_region, school_sector, school_remoteness, school_is_preschool, school_is_primary, school_is_middle, school_is_senior, school_is_faft` |

### The 3 notebooks + findings.md are superseded exploratory work, not part of the pipeline

- File mtimes (2026-09-17, 14:29–16:10) align with this repo's very first commit
  (2026-09-17, "Initial commit"), **predating** the 2026-09-27 "Refined repo structure" commit
  that established the current numbered `notebooks/00a`–`11` pipeline and its docs.
- All three notebooks hardcode the original author's local path
  (`C:\Users\saugat.poudel\Downloads\...\govhack\...`); not portable, not rerunnable as-is
  from this repo.
- They are pure exploratory data-quality EDA (missingness matrices, GNAF match-rate analysis,
  representativeness sampling, disguised-missing-value detection); **no `to_csv` / no output
  write anywhere in any of the three**. They read the raw CSVs and produce plots + the three
  `findings.md` write-ups, nothing else.
- They do not duplicate `07_services_clean_facilities.ipynb` / `08_services_geocode_schools.ipynb`'s
  logic (those are integration-oriented: trim, clean, dedup, geocode, write `data/processed/`
  outputs), but their conclusions appear to have already been absorbed into 07/08's cleaning
  rules (e.g. nb07's `"Ses Facility"` → `"SES Facility"` fix is exactly the kind of issue this
  EDA style would have surfaced first).
- Nothing in the current pipeline reads from `data-main/`, and nothing in `data-main/` writes
  anywhere in the pipeline. It is an orphaned, self-contained side-branch of investigation.

### Recommendation

- **Move the 3 raw CSVs** into `data/external/services/_raw/` (they will pick up Git LFS via
  the existing `*.csv` rule in `.gitattributes` automatically): this closes the exact gap
  `docs/SERVICES_LAYER.md` already documents and names. This is a real, low-risk fix but is a
  repo-structure change the user should confirm before it's done, since it means `git add`ing
  ~70 KB of new tracked data.
- **Treat the 3 EDA notebooks and `findings.md` files as historical/archival**, not as
  something to renumber into the `notebooks/00a`–`11` sequence. If kept, they belong somewhere
  clearly separate (e.g. an `archive/` or `notebooks/exploratory/` folder) so a future agent
  doesn't mistake them for live pipeline steps. **This document does not make that move on its
  own: it's a recommendation, not an action taken.**

## 6. File-by-file status summary

| File | Status | Reads from | Writes to |
|---|---|---|---|
| `notebooks/00a_eda_population_census.ipynb` | Active: EDA, pipeline dead-end | BushTel, Census G01/G02, SA1/ILOC shp, RA xlsx | `docs/eda/*.png` only |
| `notebooks/00b_eda_connectivity.ipynb` | Active: EDA, pipeline dead-end | ACMA, NBN, MBSP, guide, RICT | `docs/eda/*.png` only |
| `notebooks/01_villages.ipynb` | Active: pipeline step 1 | BushTel, SA1 shp, RA xlsx | `villages.csv/.geojson` |
| `notebooks/02_sa1_report.ipynb` | Active: pipeline step 2 | SA1 shp, RA xlsx, Census G01/G02, `villages.csv` | `sa1_report.csv/.geojson`, `area_with_population_lessthan_5.csv` |
| `notebooks/03_towers.ipynb` | Active: pipeline step 3 | ACMA (4 CSVs) | `towers.csv/.geojson` |
| `notebooks/04_nbn_footprint.ipynb` | Active: pipeline step 4 | NBN shapefiles, BushTel | `nbn_footprint.geojson` |
| `notebooks/05_program_sites.ipynb` | Active: pipeline step 5 | MBSP, guide, RICT | `program_sites.csv/.geojson` |
| `notebooks/06_village_gap.ipynb` | Active: pipeline step 6, main connectivity output | outputs of 01/03/04/05 | `village_gap.csv/.geojson` |
| `notebooks/07_services_clean_facilities.ipynb` | Active: pipeline step 7 | `services/trimmed/` (medical, emergency) | `medical_services.csv`, `emergency_services.csv` |
| `notebooks/08_services_geocode_schools.ipynb` | Active: pipeline step 8 | `services/trimmed/school`, nb07 outputs, BushTel | `school_services.csv` |
| `notebooks/09_services_combine_sites.ipynb` | Active: pipeline step 9 | nb07 + nb08 outputs | `services_sites.csv` |
| `notebooks/10_small_cells.ipynb` | Active: pipeline step 10, app-only consumer | `remote-small-cell-coverage-nt.xlsx` | `small_cells.csv` |
| `notebooks/11_services_gap.ipynb` | Active: pipeline step 11, final services output | `village_gap.csv`, `services_sites.csv` | `village_gap_with_services.csv`, `village_services_gap.csv` |
| `run_pipeline.py` | Active: orchestrator | - | executes notebooks in place |
| `app/app.py` | Active: dashboard | `data/processed/*` (5 files) | nothing (in-memory downloads only) |
| `data-main/data-main/*.ipynb`, `*_findings.md` | **Orphaned / superseded**: not wired into anything | local Downloads-folder CSVs (hardcoded, author's machine) | nothing |
| `data-main/data-main/*.csv` | **Orphaned but valuable**: matches a documented gap | - | - (candidate to move into `data/external/services/_raw/`) |
