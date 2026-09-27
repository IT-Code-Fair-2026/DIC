# Data folder — what every file is, where it came from, and its map projection

This project keeps a hard line between **data** and **code**:

* `data/raw/`      — files supplied by CDU for the challenge. **Never edited.** Read only.
* `data/external/` — files **we** downloaded from public sources. **Never edited.** Read only.
* `data/processed/` — the **only** folder any notebook is allowed to write to. One tidy
  CSV/GeoJSON pair per pipeline step (see `notebooks/`), with `village_gap.columns.md`
  documenting the final table's columns.

"CRS" below is the coordinate reference system a spatial file is stored in. Four show up:

* **EPSG:7844** — GDA2020, latitude/longitude in degrees. The ABS 2021 SA1 boundary shapefile.
* **EPSG:4283** — GDA94, latitude/longitude in degrees. The NBN footprint shapefiles.
* **EPSG:4326** — WGS84 lat/long. JSON/KML point files (BushTel, RICT, MBSP) — the
  coordinates are plain lat/long and for our purposes 4326 ≈ 7844 ≈ 4283 (sub-metre).
* Distance and area maths is always done after reprojecting to **EPSG:3577** (Australian
  Albers, metres) — see `notebooks/06_village_gap.ipynb`.

Large files are tracked via **git-lfs** (see `.gitattributes` — every `.csv`, `.xlsx`,
`.shp`/`.shx`/`.dbf`/`.prj`, `.geojson`, `.kml`, `.pdf` is LFS-tracked), not git-ignored —
there is no `.gitignore` in this repo. Where a source dataset was trimmed down (see below),
the emptied folder still exists in the tree via a `.gitkeep` file so paths never break.

**2026-09-27 cleanup:** everything a source directory contained but that no notebook (or
`Saugat/services/build_small_cells.py`, since replaced by `notebooks/10_small_cells.ipynb`)
actually uses was removed, freeing ~300 MB. The full file-by-file usage audit this was based
on — every notebook cell read line by line, not just markdown — is `docs/data_use_check.md`;
read that first if a "why isn't X here" question comes up. What follows describes the
**current, trimmed** contents only.

---

## `data/raw/` — supplied by CDU (small)

| Path | What it is | Source / URL | Retrieved | Licence | CRS |
|---|---|---|---|---|---|
| `raw/bushtel/Com_BushTel_Profile_CMC_2024.json` (488K, 792 features) | BushTel Community Profile 2024 — the master list of ~792 NT communities: `community_id`, name, aliases, lat/long, `community_type`, land council, region, electorate, and a partial `population_count`. | NT Chief Minister & Cabinet — BushTel (`https://bushtel.nt.gov.au/`) | supplied by CDU 2026-09-03 | NT Government open data | EPSG:4326 (lat/long points) |
| `raw/rict/Com_RICT_Community_NIAA_2024.json` (168K, 535 features, 296 NT) | Remote Indigenous Communications (RICT) community list — communities covered by the Indigenous Communications Program, with service indicators. | National Indigenous Australians Agency (NIAA) 2024 | supplied by CDU 2026-09-03 | Commonwealth open data (CC-BY 4.0) | EPSG:4326 (lat/long points) |
| `raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx` (28K, 193 rows, 188 NT after header cleanup) | National Mobile Coverage guide — all listed mobile sites (the "GUIDE only" spreadsheet). | NT Open Data Portal — "Remote Communities with 3G/4G Mobile Coverage" (`https://data.nt.gov.au/dataset/remote-communities-with-mobile-coverage`) | supplied by CDU 2026-09-03 | NT Government open data | tabular; lat/long columns (EPSG:4326) |
| `raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx` (16K) | Remote sites with mobile-phone **small-cell** coverage, NT. Read by `notebooks/10_small_cells.ipynb`, which writes `processed/small_cells.csv` for the dashboard. | NT Open Data Portal — "Remote Sites with Mobile Phone Small Cell Coverage" (`https://data.nt.gov.au/dataset/remote-sites-with-mobile-phone-small-cell-coverage`) | supplied by CDU 2026-09-03 | NT Government open data | tabular; lat/long columns (EPSG:4326) |
| `raw/census_gcp_2021/2021_GCP_all_for_NT_short-header/` (228K kept) | 2021 Census **General Community Profile** DataPack, NT, short-header CSV. Originally 1,904 CSVs (16 geography levels × up to 119 tables); **trimmed 2026-09-27 to the 2 files actually read** — `SA1/NT/2021Census_G01_NT_SA1.csv` (649 rows: total + Indigenous persons) and `2021Census_G02_NT_SA1.csv` (649 rows: medians + persons-per-bedroom). The DataPack's own `Metadata/` and `Readme/` folders are kept alongside. | ABS DataPacks (`https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_all_for_NT_short-header.zip`) | 2026-09-03 | CC-BY 4.0, Australian Bureau of Statistics | tabular (CSV, no geometry) |

---

## `data/external/` — downloaded by us

| Path | What it is | Source / URL | Retrieved | Licence | CRS |
|---|---|---|---|---|---|
| `external/mbsp/MBSP - Round *.kml` (8 files, 6.0M total, 2,710 placemarks, 49 in NT) | Mobile Black Spot Program — funded base stations, one KML per funding round (1–7, 5A). Point per funded site with round + status attributes. | Dept of Infrastructure, Transport, Regional Development, Communications & the Arts — MBSP (`https://www.infrastructure.gov.au/media-communications-arts/phone/mobile-services-and-coverage/mobile-black-spot-program`) | 2026-09-03 | Commonwealth open data (CC-BY 4.0) | EPSG:4326 (KML is always WGS84) |
| `external/abs_boundaries/SA1_2021_AUST_GDA2020_SHP/` (147M .shp, 61,845 polygons national, 649 read for NT via a `WHERE` clause) | ABS ASGS 2021 (Edition 3) **SA1** boundary shapefile. Fields used: `SA1_CODE21`, `SA2_NAME21`, `SA3_NAME21`, `SA4_NAME21`, `geometry`. | ABS digital boundary files — `https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/SA1_2021_AUST_SHP_GDA2020.zip` | 2026-09-03 ~20:22 | CC-BY 4.0, Australian Bureau of Statistics | **EPSG:7844** (GDA2020) |
| `external/abs_boundaries/RA_2021_AUST.xlsx` (3.1M, 61,845 rows all-AU → 649 NT) | ABS Remoteness Area 2021 correspondence/allocation workbook (SA1 → RA lookup). Sheet `SA1_RA_2021_AUST`; columns used: `SA1_CODE_2021`, `RA_NAME_2021`, `STATE_NAME_2021`, `AREA_ALBERS_SQKM`. | ABS ASGS 2021 remoteness structure page (`https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/remoteness-structure`) | 2026-09-04 | CC-BY 4.0, Australian Bureau of Statistics | tabular (no geometry) |
| `external/nbn/fixedline/nbn_coverage_fixedline.shp` (+ .DBF/.PRJ/.SHX, 14M, 35 polygons in the NT bbox) | NBN **fixed-line** technology footprint polygons (where the fixed-line network reaches). Geometry only — no technology/speed attribute, so the notebook labels `technology` from the source filename. | nbn Co open data via data.gov.au — `https://data.gov.au/data/dataset/national-broadband-network/resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc` (extract dated 2024-03-26) | 2026-09-03 | nbn Co open-data terms | **EPSG:4283** (GDA94) — reproject before use |
| `external/nbn/wireless/nbn_coverage_wireless.shp` (+ .DBF/.PRJ/.SHX, 624M, 348 polygons in the NT bbox) | NBN **fixed-wireless** technology footprint polygons. Same geometry-only caveat as fixed-line; sits entirely around Darwin/Tiwi. | nbn Co open data via data.gov.au — `https://data.gov.au/data/dataset/national-broadband-network/resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f` (extract dated 2024-03-26) | 2026-09-03 | nbn Co open-data terms | **EPSG:4283** (GDA94) — reproject before use |
| `external/acma_rrl/` (4 CSVs kept, 401M total) | ACMA **Register of Radiocommunications Licences** — daily national full extract. Originally 27 CSVs; **trimmed 2026-09-27 to the 4 actually joined**: `site.csv` (13M, 129,492 rows: `SITE_ID`, `LATITUDE`, `LONGITUDE`, `NAME`, `STATE`, `SITE_PRECISION`; 3,771 rows `STATE == 'NT'`), `licence.csv` (20M, 164,205 rows: `LICENCE_NO`, `CLIENT_NO`, `LICENCE_CATEGORY_NAME`), `client.csv` (1.7M, 14,332 rows: licensee names), `device_details.csv` (367M, 2,154,999 rows, read in 200k-row chunks and filtered to NT site ids → 26,767 rows kept: `FREQUENCY`, `BANDWIDTH`, `EIRP`, …). Join `device_details.SITE_ID → site.SITE_ID`, `device_details.LICENCE_NO → licence.LICENCE_NO`, `licence.CLIENT_NO → client.CLIENT_NO`. `LICENCE.TXT`/`LICENCE.PDF` (usage terms), `README.TXT` and `DOC/` (ACMA's own schema docs) are kept regardless of which tables are present. | ACMA — `https://web.acma.gov.au/rrl-updates/spectra_rrl.zip` (301 → `https://cdn.acma.gov.au/rrl/spectra_rrl.zip`); terms at `https://www.acma.gov.au/radiocomms-licence-data` | 2026-09-03 ~20:22 (extract regenerated daily ~6am AEST) | **ACMA RRL Licence** — usage conditions in `external/acma_rrl/LICENCE.TXT`, must be observed (not CC-BY) | `site.csv` has lat/long columns ≈ EPSG:4326; `SITE_PRECISION` flags accuracy |
| `external/services/trimmed/` (3 CSVs, ~70K) | School list (273, no coordinates), GA/NHSD medical facilities (181) and GA emergency facilities (152), NT, **already trimmed** to the columns the pipeline uses. The original raw extracts (`School_List_Public_2026_09_12_11_12_43.csv`, `medical_facilities_NT.csv`, `emergency_facilities_NORTHERN_TERRITORY.csv`) are not in the repo. | NT Dept of Education school list; Geoscience Australia / National Health Services Directory | 2026-09-12 | NT Government / CC-BY 4.0 | lat/long columns (EPSG:4326); schools have none |

### Removed 2026-09-27 (unused by any notebook or script; verified against the whole repo, not just notebooks)

Each of these directories was emptied and left as a `.gitkeep` placeholder so the path
still resolves; re-download from the URL if the data is needed again.

| Path | What it was | Why removed |
|---|---|---|
| `external/stand/` | STAND — Strengthening Telecommunications Against Natural Disasters, national program-sites GeoJSON | Explicitly dropped by `notebooks/00b_eda_connectivity.ipynb` and `05_program_sites.ipynb` ("no unique signal"); never read |
| `external/services/_raw/` | 3 Geoscience Australia GeoJSONs — police (66 pts), hospitals (11 pts), GP/health (128 pts), NT | Never read by any script. `external/services/README.md` describes a `src/05_load_services.py` consumer that was never built — the services layer that does exist (notebooks 07–11) was built from a different, independently-sourced set of files (`external/services/trimmed/`) |
| `external/abs_boundaries/SAL_2021_AUST_GDA2020_SHP/` | ABS ASGS 2021 Suburbs & Localities boundary shapefile (143M, 15,353 polygons national) | Never referenced by any notebook or script |
| `external/abs_boundaries/RA_2021_AUST_GDA2020/` | ABS ASGS 2021 Remoteness Area boundary *shapefile* (distinct from the `.xlsx` lookup above, which is kept) | Never referenced; was already removed from the working tree before this cleanup |
| `external/acma_rrl/` — 20 of 24 CSVs | `access_area`, `antenna`, `antenna_pattern`, `antenna_polarity`, `applic_text_block` (167M), `auth_spectrum_area`, `auth_spectrum_freq`, `bsl`, `bsl_area`, `class_of_station`, `client_type`, `fee_status`, `industry_cat`, `licence_service`, `licence_status`, `licence_subservice`, `licensing_area`, `nature_of_service`, `reports_text_block`, `satellite` | None of these tables are joined or read by `03_towers.ipynb` or `00b_eda_connectivity.ipynb` |
| `raw/census_gcp_2021/…/{CED,GCCSA,LGA,POA,RA,SA2,SA3,SA4,SAL,SED,SOS,SOSR,STE,SUA,UCL}/` | 14 of 16 Census geography levels, 1,902 of 1,904 CSVs | Only the SA1-level G01/G02 tables are read; everything else in the DataPack was unused |

### ILOC boundaries (restored)

`external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/` (ABS Indigenous Location boundaries) had
been deleted in the 2026-09-27 cleanup, although `00a_eda_population_census.ipynb` still reads it.
It was restored from git history so that every notebook runs end-to-end.

---

## `data/processed/` — written by the notebooks (current pipeline)

The only folder any notebook writes to. Each CSV has a GeoJSON sibling with the same rows;
`village_gap.csv` also has `village_gap.columns.md` documenting every column.

| File | Rows | Written by |
|---|---|---|
| `villages.csv` / `.geojson` (216K / 604K) | 792 | `01_villages.ipynb` |
| `sa1_report.csv` / `.geojson` (84K / 5.0M, 645 polygons) | 649 | `02_sa1_report.ipynb` |
| `area_with_population_lessthan_5.csv` (8.0K) | 34 (ABS-suppressed SA1s) | `02_sa1_report.ipynb` |
| `towers.csv` / `.geojson` (64K / 216K) | 431 | `03_towers.ipynb` |
| `nbn_footprint.geojson` (860K) | 2 (fixed_line, fixed_wireless) | `04_nbn_footprint.ipynb` |
| `program_sites.csv` / `.geojson` (40K / 236K) | 533 | `05_program_sites.ipynb` |
| `village_gap.csv` / `.geojson` (172K / 804K) | 792 | `06_village_gap.ipynb` |
| `medical_services.csv` / `emergency_services.csv` | 181 / 151 | `07_services_clean_facilities.ipynb` |
| `school_services.csv` | 273 (272 geocoded) | `08_services_geocode_schools.ipynb` |
| `services_sites.csv` | 605 (schools + medical + emergency) | `09_services_combine_sites.ipynb` |
| `small_cells.csv` | 24 | `10_small_cells.ipynb` |
| `village_gap_with_services.csv` / `village_services_gap.csv` | 792 | `11_services_gap.ipynb` |

---

## Still to acquire

| Needed for | Dataset | Where to get it | Notes |
|---|---|---|---|
| — | **MNHP** (Mobile Network Hardening Program) sites → `data/external/mnhp/` | Dept of Infrastructure … Communications & the Arts — MNHP program page | Folder exists (`.gitkeep` only); no data acquired, not read by any current notebook. Confirm whether it is in scope before fetching. |
| — | `data/external/pump/` | unknown | Folder exists (`.gitkeep` only); the dataset this was meant to hold was never defined. Needs clarification before acquiring. |

---

## Sources cross-reference

The full, line-by-line record of what every notebook actually reads — every file, every
column, every filter, cross-checked against the whole repo (not just the notebooks) for any
other consumer — is `docs/data_use_check.md`. Original per-file provenance for the ABS /
ACMA / NBN pulls is in the tables above; there is no separate download log in this repo.
