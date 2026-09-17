# Dataset inventory
Tick [x] every dataset you want documented in the data dictionary.
Leave [ ] for datasets to skip in phase one.

## data/raw
- [x] `raw/bushtel/Com_BushTel_Profile_CMC_2024.json` — JSON, 485.7 KB, 792 features — used — BushTel Community Profile 2024, master list of ~792 NT communities (id, name, lat/long, type, land council, region, electorate, partial population).
- [x] `raw/census_gcp_2021/2021_GCP_all_for_NT_short-header/` — folder of 1,904 CSVs (16 geography levels × 119 tables G01–G62 each), 60 MB total — used — 2021 Census General Community Profile DataPack, NT, short-header CSV; SA1 level (649 in NT) is the one read.
- [x] `raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx` — XLSX, 24.0 KB, 192 rows (1 sheet) — used — National Mobile Coverage guide, all listed mobile sites ("GUIDE only" spreadsheet, ~188 NT rows).
- [ ] `raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx` — XLSX, 13.3 KB, 25 rows (1 sheet) — unused — Remote sites with mobile-phone small-cell coverage, NT.
- [ ] `raw/rict/Com_RICT_Community_NIAA_2024.json` — JSON, 164.1 KB, 535 features — unused — Remote Indigenous Communications (RICT) community list, NIAA, with service indicators.

## data/external (committed)
- [x] `external/mbsp/MBSP - Round {1,2,3,4,5,5A,6,7} Funded Base Stations.kml` — 8 KMLs, 5.9 MB total, 2,710 placemarks — used — Mobile Black Spot Program funded base stations, one KML per funding round.
- [ ] `external/mnhp/` — empty (placeholder `.gitkeep` only, no data acquired) — unused — Mobile Network Hardening Program sites; flagged in data/README.md as not yet acquired.
- [ ] `external/pump/` — empty (placeholder `.gitkeep` only, no data acquired) — unused — undefined dataset ("pump"); flagged in data/README.md as needing clarification.
- [ ] `external/services/_raw/ga_gp_nt.geojson` — GeoJSON, 74.5 KB, 128 features — unused — GA/NHSD general practices & community health centres, NT.
- [ ] `external/services/_raw/ga_hospitals_nt.geojson` — GeoJSON, 6.4 KB, 11 features — unused — GA/NHSD hospitals, NT (11 raw, dedupes to 8 downstream).
- [ ] `external/services/_raw/ga_police_nt.geojson` — GeoJSON, 74.5 KB, 66 features — unused — GA Emergency Management Facilities, police stations/shopfronts, NT.
- [ ] `external/stand/strengthening_telecommunication_against_natural_disaster.json` — JSON, 390.4 KB, 1,255 features — unused — STAND (Strengthening Telecommunications Against Natural Disasters) program sites, national GeoJSON FeatureCollection of points.

## data/external (git-ignored, on disk)
- [ ] `external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/` — shapefile, 56.9 MB, 1,139 records — **parked — dropped 2026-09-06, no unique signal** (SA1 already tags every village with a region; ILOC added an overlapping second one). Not read by any v2 notebook. Safe to delete; left on disk for now. (national; 189 in NT).
- [x] `external/abs_boundaries/RA_2021_AUST.xlsx` — XLSX, 3.1 MB, 61,845 rows (1 sheet) — used — ABS Remoteness Area 2021 correspondence/allocation workbook (SA1 → RA lookup).
- [ ] `external/abs_boundaries/RA_2021_AUST_GDA2020/` — shapefile, 38.8 MB, 54 records — unused — ABS ASGS 2021 Remoteness Area boundary shapefile (national; 5 in NT).
- [x] `external/abs_boundaries/SA1_2021_AUST_GDA2020_SHP/` — shapefile, 184.7 MB, 61,845 records — used — ABS ASGS 2021 SA1 boundary shapefile (national; 649 in NT).
- [ ] `external/abs_boundaries/SAL_2021_AUST_GDA2020_SHP/` — shapefile, 143.3 MB, 15,353 records — unused — ABS ASGS 2021 Suburbs & Localities boundary shapefile (national; 305 in NT).
- [x] `external/acma_rrl/` — folder of 24 CSVs, 572.7 MB total — used (4 of 24 files) — ACMA Register of Radiocommunications Licences, daily national full extract.
  - [] `access_area.csv` — 836 B, 27 rows
  - [] `antenna.csv` — 606.7 KB, 8,658 rows
  - [] `antenna_pattern.csv` — 2.2 MB, 110,271 rows
  - [] `antenna_polarity.csv` — 293 B, 11 rows
  - [] `applic_text_block.csv` — 166.9 MB, 461,102 rows
  - [] `auth_spectrum_area.csv` — 1.5 MB, 3,506 rows
  - [] `auth_spectrum_freq.csv` — 209.4 KB, 3,542 rows
  - [] `bsl.csv` — 203.6 KB, 3,654 rows
  - [] `bsl_area.csv` — 10.8 KB, 560 rows
  - [] `class_of_station.csv` — 447 B, 12 rows
  - [] `client.csv` — 1.6 MB, 14,331 rows — used
  - [] `client_type.csv` — 161 B, 6 rows
  - [x] `device_details.csv` — 366.5 MB, 2,154,998 rows — used (size/rows only, never loaded fully)
  - [] `fee_status.csv` — 63 B, 2 rows
  - [] `industry_cat.csv` — 650 B, 14 rows
  - [x] `licence.csv` — 19.7 MB, 164,204 rows — used
  - [] `licence_service.csv` — 492 B, 27 rows
  - [] `licence_status.csv` — 330 B, 18 rows
  - [] `licence_subservice.csv` — 3.8 KB, 123 rows
  - [] `licensing_area.csv` — 129 B, 4 rows
  - [] `nature_of_service.csv` — 901 B, 15 rows
  - [] `reports_text_block.csv` — 171.6 KB, 529 rows
  - [] `satellite.csv` — 4.0 KB, 146 rows
  - [x] `site.csv` — 13.0 MB, 129,491 rows — used
- [x] `external/nbn/fixedline/nbn_coverage_fixedline.shp` — shapefile, 14.0 MB, 5,316 records — unused — NBN fixed-line technology footprint polygons.
- [x] `external/nbn/wireless/nbn_coverage_wireless.shp` — shapefile, 636.1 MB, 505,615 records — unused — NBN fixed-wireless technology footprint polygons.

## data/processed  (old pipeline)
- [ ] `processed/01_communities.csv` — CSV, 188.7 KB, 793 rows — unused — old-pipeline output, village table (communities).
- [ ] `processed/01_communities.geojson` — GeoJSON, 494.0 KB, 792 features — unused — old-pipeline output, village table as points.
- [ ] `processed/02_sa1_boundaries.geojson` — GeoJSON, 4.8 MB, 649 features — unused — old-pipeline output, NT SA1 polygons.
- [ ] `processed/02_sa1_report.csv` — CSV, 86.3 KB, 649 rows — unused — old-pipeline output, SA1-level report.
- [ ] `processed/02_villages_with_areas.csv` — CSV, 232.7 KB, 793 rows — unused — old-pipeline output, villages tagged with SA1/ILOC/RA area codes.
- [ ] `processed/02_villages_with_areas.geojson` — GeoJSON, 586.1 KB, 792 features — unused — old-pipeline output, same as above as points.
- [ ] `processed/03_mobile_sites.csv` — CSV, 75.7 KB, 695 rows — unused — old-pipeline output, combined mobile site inventory (ACMA + NT guide + MBSP).
- [ ] `processed/03_mobile_sites.geojson` — GeoJSON, 288.4 KB, 695 features — unused — old-pipeline output, same as above as points.
- [ ] `processed/04_nbn_footprint.geojson` — GeoJSON, 859.6 KB, 2 features — unused — old-pipeline output, NBN fixed-line/wireless footprint (dissolved).
- [ ] `processed/04_public_access.csv` — CSV, 23.4 KB, 384 rows — unused — old-pipeline output, RICT + STAND public-access points.
- [ ] `processed/04_public_access.geojson` — GeoJSON, 84.4 KB, 384 features — unused — old-pipeline output, same as above as points.

## data/new_processed  (current pipeline)
- [ ] `new_processed/communities.csv` — CSV, 188.7 KB, 793 rows — unused — not read or written under this name by either notebook (stale copy of `01_communities.csv`).
- [ ] `new_processed/communities.geojson` — GeoJSON, 494.0 KB, 792 features — unused — not read or written under this name by either notebook (stale copy of `01_communities.geojson`).
- [x] `new_processed/community_connectivity_priority.csv` — CSV, 18.4 KB, 188 rows — used (written) — connectivity-priority shortlist (nearest MBSP gap etc.), written by `connecitivity_analysis.ipynb`.
- [x] `new_processed/mobile_sites.csv` — CSV, 76.4 KB, 695 rows — used (written) — combined mobile site inventory, written by `connecitivity_analysis.ipynb`.
- [x] `new_processed/mobile_sites.geojson` — GeoJSON, 301.7 KB, 695 features — used (written) — same as above as points, written by `connecitivity_analysis.ipynb`.
- [x] `new_processed/sa1_boundaries.geojson` — GeoJSON, 4.8 MB, 649 features — used (written) — NT SA1 polygons, written by `population_distribution_analsis.ipynb`.
- [ ] `new_processed/sa1_report.csv` — CSV, 78.2 KB, 649 rows — unused — write call is commented out in `population_distribution_analsis.ipynb`; file on disk is stale.
- [ ] `new_processed/sa1_report.geojson` — GeoJSON, 4.9 MB, 645 features — unused — not read or written by either notebook.
- [x] `new_processed/villages_with_areas.csv` — CSV, 237.8 KB, 793 rows — used (written) — villages tagged with SA1/ILOC/RA codes, written by `population_distribution_analsis.ipynb`.
- [x] `new_processed/villages_with_areas.geojson` — GeoJSON, 623.5 KB, 792 features — used (written) — same as above as points, written by `population_distribution_analsis.ipynb`.

## Other data-like folders found (outside the requested list)
- [ ] `work/communities_v0.csv` — CSV, 94.1 KB, 792 rows — unused — earlier v0 tiering script's output, no description available (no README).

## Not found on disk (listed in README but missing)
- `external/census_ip_2021/` — gitignored placeholder path (`.gitignore` line `/data/external/census_ip_2021/*`); no folder present on disk.
- `raw/2021_IP_all_for_NT_short-header/` — 2021 Census Aboriginal & Torres Strait Islander Peoples Profile DataPack, NT (per `data/README.md`); not present on disk.
- `raw/school_data.xlsx` — ACARA Australian Schools List, NT export (per `data/README.md`, meant to be read by `05_load_services.py`); not present on disk.
