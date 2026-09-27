# Dataset inventory

Reflects the `data/` tree as of **2026-09-27**, after removing every file that no notebook
in `notebooks/` (00a–06) and no other script in the repo actually reads. The audit behind
the `used`/`unused` calls below is `docs/data_use_check.md` — every notebook cell read line
by line, plus a repo-wide grep for any non-notebook consumer (which is how
`remote-small-cell-coverage-nt.xlsx` was caught as used by `Saugat/services/build_small_cells.py`
even though no notebook touches it). `[x]` = used, `[ ]` = not used / not present.

## data/raw
- [x] `raw/bushtel/Com_BushTel_Profile_CMC_2024.json` — JSON, 488K, 792 features — used by `00a`, `01`, `04` — BushTel Community Profile 2024, master list of ~792 NT communities (id, name, lat/long, type, land council, region, electorate, partial population).
- [x] `raw/census_gcp_2021/2021_GCP_all_for_NT_short-header/` — **trimmed 2026-09-27**: was 1,904 CSVs (16 geography levels × up to 119 tables), 60 MB; now 2 CSVs, 228 KB — used by `00a`, `02` — 2021 Census General Community Profile DataPack, NT, short-header CSV. Only `SA1/NT/2021Census_G01_NT_SA1.csv` (649 rows, `Tot_P_P` column) and `2021Census_G02_NT_SA1.csv` (649 rows, `Median_tot_hhd_inc_weekly` + `Average_household_size`) are read. The DataPack's own `Metadata/` and `Readme/` folders are kept alongside (documentation, not data).
- [x] `raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx` — XLSX, 28K, 193 rows (1 sheet) — used by `00b`, `05` — National Mobile Coverage guide, all listed mobile sites ("GUIDE only" spreadsheet, 188 NT rows after the header-row hunt).
- [x] `raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx` — XLSX, 16K — used, but **not by any notebook** — read directly by `Saugat/services/build_small_cells.py`, which writes `Saugat/app/small_cells.csv`.
- [x] `raw/rict/Com_RICT_Community_NIAA_2024.json` — JSON, 168K, 535 features — used by `00b`, `05` — Remote Indigenous Communications (RICT) community list, NIAA, with service indicators. 296 of 535 are NT (`state == "NT"`).

## data/external (kept)
- [x] `external/mbsp/MBSP - Round {1,2,3,4,5,5A,6,7} Funded Base Stations.kml` — 8 KMLs, 6.0M total, 2,710 placemarks — used by `00b`, `05` — Mobile Black Spot Program funded base stations, one KML per funding round; 49 NT sites survive dedupe on `MBSP_ID`.
- [x] `external/abs_boundaries/SA1_2021_AUST_GDA2020_SHP/` — shapefile, 147M (.shp), 61,845 polygons national — used by `00a`, `01`, `02` — ABS ASGS 2021 SA1 boundary shapefile; 649 read for NT via a GDAL `WHERE` clause at read time.
- [x] `external/abs_boundaries/RA_2021_AUST.xlsx` — XLSX, 3.1M, 61,845 rows (1 sheet) — used by `00a`, `01`, `02` — ABS Remoteness Area 2021 correspondence/allocation workbook (SA1 → RA lookup); 649 NT rows kept in-frame.
- [x] `external/acma_rrl/` — **trimmed 2026-09-27**: was 24 CSVs, 573M total; now 4 CSVs, 401M — used by `00b`, `03` — ACMA Register of Radiocommunications Licences, daily national full extract.
  - [x] `site.csv` — 13M, 129,492 rows — used (3,771 `STATE == 'NT'`)
  - [x] `licence.csv` — 20M, 164,205 rows — used (3 columns: `LICENCE_NO`, `CLIENT_NO`, `LICENCE_CATEGORY_NAME`)
  - [x] `client.csv` — 1.7M, 14,332 rows — used (2 columns: `CLIENT_NO`, `LICENCEE`)
  - [x] `device_details.csv` — 367M, 2,154,999 rows — used (read in 200k-row chunks, filtered to NT site ids → 26,767 rows kept)
  - kept regardless of table trimming (licence terms / schema docs, not data): `LICENCE.TXT`, `LICENCE.PDF`, `README.TXT`, `DOC/` (ERD, Oracle DDL, format-summary xlsx)
- [x] `external/nbn/fixedline/nbn_coverage_fixedline.shp` — shapefile, 14M, 35 polygons in the NT bbox — used by `00b`, `04` — NBN fixed-line technology footprint polygons.
- [x] `external/nbn/wireless/nbn_coverage_wireless.shp` — shapefile, 624M, 348 polygons in the NT bbox — used by `00b`, `04` — NBN fixed-wireless technology footprint polygons (Darwin/Tiwi only).

## Removed 2026-09-27 (confirmed unused by every notebook and every other script in the repo)

Each path below was fully removed and replaced with a `.gitkeep` placeholder so the
directory still exists; re-download from the URL in `data/README.md` if needed again.

- `external/stand/strengthening_telecommunication_against_natural_disaster.json` — JSON, 390K, 1,255 features — STAND program sites, national. Both `00b` and `05` state in their own output cells that STAND is deliberately dropped ("no unique signal").
- `external/services/_raw/ga_gp_nt.geojson` — GeoJSON, 75K, 128 features — GA/NHSD general practices & community health centres, NT.
- `external/services/_raw/ga_hospitals_nt.geojson` — GeoJSON, 6.4K, 11 features — GA/NHSD hospitals, NT.
- `external/services/_raw/ga_police_nt.geojson` — GeoJSON, 75K, 66 features — GA Emergency Management Facilities, police stations/shopfronts, NT.
  - None of the three above were ever read by any script. `external/services/README.md` (kept) describes a `src/05_load_services.py` consumer that was never built in this repo; the services layer that does exist (`Saugat/services/`) was built independently from a different set of source files.
- `external/abs_boundaries/SAL_2021_AUST_GDA2020_SHP/` — shapefile, 143M, 15,353 records national — ABS ASGS 2021 Suburbs & Localities boundary shapefile. Never referenced.
- `external/acma_rrl/` — 20 of 24 CSVs, ~172M: `access_area.csv`, `antenna.csv`, `antenna_pattern.csv`, `antenna_polarity.csv`, `applic_text_block.csv` (167M — the single largest removed file), `auth_spectrum_area.csv`, `auth_spectrum_freq.csv`, `bsl.csv`, `bsl_area.csv`, `class_of_station.csv`, `client_type.csv`, `fee_status.csv`, `industry_cat.csv`, `licence_service.csv`, `licence_status.csv`, `licence_subservice.csv`, `licensing_area.csv`, `nature_of_service.csv`, `reports_text_block.csv`, `satellite.csv`.
- `raw/census_gcp_2021/…/{CED,GCCSA,LGA,POA,RA,SA2,SA3,SA4,SAL,SED,SOS,SOSR,STE,SUA,UCL}/` — 14 of 16 geography levels, 1,902 of 1,904 Census GCP CSVs, ~60M. Only `SA1/NT/2021Census_G01_NT_SA1.csv` and `G02` are read (see `data/raw` above).

## Empty placeholders (unchanged — no data ever acquired)
- [ ] `external/mnhp/` — `.gitkeep` only — Mobile Network Hardening Program sites; flagged in `data/README.md` as not yet acquired, not read by any notebook.
- [ ] `external/pump/` — `.gitkeep` only — undefined dataset ("pump"); flagged in `data/README.md` as needing clarification.

## Missing but still referenced by a notebook
- `external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/` — ABS ASGS 2021 Indigenous Location boundary shapefile (1,139 records national, 189 in NT). **Read by `00a_eda_population_census.ipynb` (EDA only — no output column depends on it), but absent from the working tree** — every file under this path shows deleted in `git status` on this branch, from before the 2026-09-27 cleanup. `00a` cannot currently run past its second cell. See `docs/data_use_check.md` §5.1.
- `external/abs_boundaries/RA_2021_AUST_GDA2020/` — ABS ASGS 2021 Remoteness Area boundary *shapefile* (distinct from `RA_2021_AUST.xlsx`, which is present and used). Not read by any notebook, and was already absent from the working tree before this cleanup.

## data/new_processed (current pipeline — the only folder any notebook writes to)
- [x] `new_processed/villages.csv` — CSV, 216K, 792 rows — written by `01_villages.ipynb`; read by `02_sa1_report.ipynb`.
- [x] `new_processed/villages.geojson` — GeoJSON, 604K, 792 features — written by `01_villages.ipynb`; read by `06_village_gap.ipynb`.
- [x] `new_processed/sa1_report.csv` — CSV, 84K, 649 rows — written by `02_sa1_report.ipynb`.
- [x] `new_processed/sa1_report.geojson` — GeoJSON, 5.0M, 645 features (4 null-geometry SA1s excluded) — written by `02_sa1_report.ipynb`.
- [x] `new_processed/area_with_population_lessthan_5.csv` — CSV, 8.0K, 34 rows — written by `02_sa1_report.ipynb` (ABS-suppressed small-count SA1s).
- [x] `new_processed/towers.csv` — CSV, 64K, 431 rows — written by `03_towers.ipynb`; read by `06_village_gap.ipynb`.
- [x] `new_processed/towers.geojson` — GeoJSON, 216K, 431 features — written by `03_towers.ipynb`.
- [x] `new_processed/nbn_footprint.geojson` — GeoJSON, 860K, 2 features — written by `04_nbn_footprint.ipynb`; read by `06_village_gap.ipynb`.
- [x] `new_processed/program_sites.csv` — CSV, 40K, 533 rows — written by `05_program_sites.ipynb`; read by `06_village_gap.ipynb`.
- [x] `new_processed/program_sites.geojson` — GeoJSON, 236K, 533 features — written by `05_program_sites.ipynb`.
- [x] `new_processed/village_gap.csv` — CSV, 172K, 792 rows — written by `06_village_gap.ipynb`, the pipeline's final output.
- [x] `new_processed/village_gap.geojson` — GeoJSON, 804K, 792 features — written by `06_village_gap.ipynb`.
- [x] `new_processed/village_gap.columns.md` — 8.0K — column-by-column documentation for `village_gap.csv`, written alongside it.

## Not found on disk, no longer documented
The previous version of this inventory listed `data/processed/` (an old pipeline's output —
`communities.csv`, `sa1_boundaries.geojson`, etc.), `raw/2021_IP_all_for_NT_short-header/`,
`raw/school_data.xlsx`, and references to scripts named `05_load_services.py`,
`06_compute_distances.py`, `connecitivity_analysis.ipynb` and
`population_distribution_analsis.ipynb`. None of these exist anywhere in the current repo —
`data/processed/` is not present, and the current pipeline is the `notebooks/00a`–`06` series
writing to `data/new_processed/` described above. They have been dropped from this inventory
rather than carried forward as stale entries.
