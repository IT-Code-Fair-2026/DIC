# Data folder — what every file is, where it came from, and its map projection

This project keeps a hard line between **data** and **code**:

* `data/raw/`      — files supplied by CDU for the challenge. **Never edited.** Read only.
* `data/external/` — files **we** downloaded from public sources. **Never edited.** Read only.
* `data/processed/` — the **only** folder any script is allowed to write to. One tidy
  CSV or GeoJSON per pipeline step, each with a matching `*.columns.md`.

"CRS" below is the coordinate reference system a spatial file is stored in. Two show up:

* **EPSG:7844** — GDA2020, latitude/longitude in degrees. The ABS 2021 boundary files.
* **EPSG:4283** — GDA94, latitude/longitude in degrees. The NBN footprint shapefiles.
* **EPSG:4326** — WGS84 lat/long. JSON/KML point files (BushTel, RICT, MBSP, STAND) — the
  coordinates are plain lat/long and for our purposes 4326 ≈ 7844 ≈ 4283 (sub-metre).
* Distance maths is always done after reprojecting to **EPSG:3577** (Australian Albers,
  metres) — see `src/06_compute_distances.py`.

Everything large is **git-ignored** (see the repo `.gitignore`); the folder still exists in
the tree via a `.gitkeep` file so paths never break. Re-download from the URL in the table.

---

## `data/raw/` — supplied by CDU (committed; small)

| Path | What it is | Source / URL | Retrieved | Licence | CRS |
|---|---|---|---|---|---|
| `raw/bushtel/Com_BushTel_Profile_CMC_2024.json` | BushTel Community Profile 2024 — the master list of ~792 NT communities: `community_id`, name, aliases, lat/long, `community_type`, land council, region, electorate, and a partial `population_count`. | NT Chief Minister & Cabinet — BushTel (`https://bushtel.nt.gov.au/`) | supplied by CDU 2026-09-03 | NT Government open data | EPSG:4326 (lat/long points) |
| `raw/rict/Com_RICT_Community_NIAA_2024.json` | Remote Indigenous Communications (RICT) community list — communities covered by the Indigenous Communications Program, with service indicators. | National Indigenous Australians Agency (NIAA) 2024 | supplied by CDU 2026-09-03 | Commonwealth open data (CC-BY 4.0) | EPSG:4326 (lat/long points) |
| `raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx` | National Mobile Coverage guide — all listed mobile sites (the "GUIDE only" spreadsheet, ~188 NT rows). | NT Open Data Portal — "Remote Communities with 3G/4G Mobile Coverage" (`https://data.nt.gov.au/dataset/remote-communities-with-mobile-coverage`) | supplied by CDU 2026-09-03 | NT Government open data | tabular; lat/long columns (EPSG:4326) |
| `raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx` | Remote sites with mobile-phone **small-cell** coverage, NT. | NT Open Data Portal — "Remote Sites with Mobile Phone Small Cell Coverage" (`https://data.nt.gov.au/dataset/remote-sites-with-mobile-phone-small-cell-coverage`) | supplied by CDU 2026-09-03 | NT Government open data | tabular; lat/long columns (EPSG:4326) |
| `raw/census_gcp_2021/2021_GCP_all_for_NT_short-header/` | 2021 Census **General Community Profile** DataPack, NT, short-header CSV. Tables G01–G59 at all geographies incl. **SA1** (649 in NT). G01 = total persons + Indigenous persons; G02 = medians + persons-per-bedroom. **git-ignored (large).** | ABS DataPacks (`https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_all_for_NT_short-header.zip`) | 2026-09-03 | CC-BY 4.0, Australian Bureau of Statistics | tabular (CSV, no geometry) |
| `raw/2021_IP_all_for_NT_short-header/` | 2021 Census **Aboriginal & Torres Strait Islander Peoples Profile** DataPack, NT, short-header CSV. Tables I01–I21 at ILOC (189 in NT) / IARE — no SA1. I01A = Indigenous / total persons. **git-ignored (large).** | ABS DataPacks (`https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_IP_all_for_NT_short-header.zip`) | 2026-09-04 | CC-BY 4.0, Australian Bureau of Statistics | tabular (CSV, no geometry) |
| `raw/school_data.xlsx` | **ACARA Australian Schools List** — NT export, 217 open schools with `Latitude`/`Longitude`, `Sector` (Gov/Non-Gov), `Type`, `Geolocation`. One sheet `ASL Search Results` (header on row 2). Read by `05_load_services.py`. | ACARA — `https://asl.acara.edu.au/` (search State=NT → "Download search results as" Excel) | 2026-09-04 | CC-BY 4.0, ACARA | tabular; `Latitude`/`Longitude` columns (EPSG:4326) |

---

## `data/external/` — downloaded by us

### Committed (small)

| Path | What it is | Source / URL | Retrieved | Licence | CRS |
|---|---|---|---|---|---|
| `external/mbsp/MBSP - Round *.kml` (8 files: rounds 1–7 + 5A) | Mobile Black Spot Program — funded base stations, one KML per funding round. Point per funded site with round + status attributes. | Dept of Infrastructure, Transport, Regional Development, Communications & the Arts — MBSP (`https://www.infrastructure.gov.au/media-communications-arts/phone/mobile-services-and-coverage/mobile-black-spot-program`) | 2026-09-03 | Commonwealth open data (CC-BY 4.0) | EPSG:4326 (KML is always WGS84) |
| `external/stand/strengthening_telecommunication_against_natural_disaster.json` | STAND — Strengthening Telecommunications Against Natural Disasters — program sites nationally (`Site_ID`, `Jurisdiction`, `LGA`, `Site_Name`, `Site_Address`, `Public_Access`). GeoJSON FeatureCollection of points. | Dept of Infrastructure … Communications & the Arts — STAND program | 2026-09-03 | Commonwealth open data (CC-BY 4.0) | EPSG:4326 (GeoJSON default) |
| `external/services/_raw/ga_police_nt.geojson` | Police stations/shopfronts, NT — 66 points. Fields: `facility_name`, `facility_operationalstatus`, `facility_address`, `abs_suburb`. | Geoscience Australia — Emergency Management Facilities, `POLICING_FACILITY` (layer 2). `https://services.ga.gov.au/gis/rest/services/Emergency_Management_Facilities/MapServer/2/query` (where `facility_state='NORTHERN TERRITORY'`) | 2026-09-04 | © Commonwealth of Australia (Geoscience Australia) 2024 — CC-BY 4.0 | EPSG:4326 |
| `external/services/_raw/ga_hospitals_nt.geojson` | Hospitals, NT — 11 raw -> 8 after 05 dedupes Alice Springs & Katherine and drops the placeholder "Tkc Production" row. Fields: `organisation_name`, `address`, `suburb`, `operationalstatus`, `ga_class`, `nhsd_service_type`. | Geoscience Australia — National HealthDirect Health Facilities, `HOSPITAL` (layer 1), from the National Health Services Directory. `.../National_HealthDirect_Health_Facilities/MapServer/1/query` (where `state='NT'`) | 2026-09-04 | © Commonwealth of Australia (Geoscience Australia) 2024 — CC-BY 4.0 | EPSG:4326 |
| `external/services/_raw/ga_gp_nt.geojson` | General practices / community health centres, NT — 128 points. Includes remote Aboriginal Community Controlled & NT Health centres (spot-checked: clinic ≤ 5 km of Maningrida, Wadeye, Galiwin'ku, Yuendumu, Ngukurr, Borroloola) as well as urban GPs (not filtered). | Geoscience Australia — National HealthDirect Health Facilities, `GENERAL_PRACTICE` (layer 0). `.../National_HealthDirect_Health_Facilities/MapServer/0/query` (where `state='NT'`) | 2026-09-04 | © Commonwealth of Australia (Geoscience Australia) 2024 — CC-BY 4.0 | EPSG:4326 |
Schools come from `raw/school_data.xlsx` (ACARA, see the `data/raw/` table above) — an
earlier OpenStreetMap pull was used only as a cross-check and discarded.

Exact download commands: `data/external/services/README.md`. `05_load_services.py` reads
these `_raw/` files plus `raw/school_data.xlsx` and writes `data/processed/05_services.csv`
(419 points: 217 school, 128 health_clinic, 66 police, 8 hospital).

### git-ignored (large / re-downloadable)

| Path | What it is | Source / URL | Retrieved | Licence | CRS |
|---|---|---|---|---|---|
| `external/abs_boundaries/SA1_2021_AUST_GDA2020_SHP/` | ABS ASGS 2021 (Edition 3) **SA1** boundary shapefile. 61,845 polygons national, **649 in NT**. Fields: `SA1_CODE21`, SA2/SA3/SA4/GCC/STE codes+names, `AREASQKM21`. | ABS digital boundary files — `https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/SA1_2021_AUST_SHP_GDA2020.zip` | 2026-09-03 ~20:22 | CC-BY 4.0, Australian Bureau of Statistics | **EPSG:7844** (GDA2020) |
| `external/abs_boundaries/SAL_2021_AUST_GDA2020_SHP/` | ABS ASGS 2021 **Suburbs & Localities** boundary shapefile. 15,353 polygons national, 305 in NT. Fields: `SAL_CODE21`, `SAL_NAME21`, `STE_*`, `AREASQKM21`. | ABS — `…/SAL_2021_AUST_GDA2020_SHP.zip` (same base path) | 2026-09-03 ~20:22 | CC-BY 4.0, Australian Bureau of Statistics | **EPSG:7844** (GDA2020) |
| `external/abs_boundaries/RA_2021_AUST_GDA2020/` | ABS ASGS 2021 **Remoteness Area** boundary shapefile. 54 polygons national, 5 in NT (Major Cities / Inner Regional / Outer Regional / Remote / Very Remote). Fields: `RA_CODE21`, `RA_NAME21`, `STE_*`. | ABS — `…/RA_2021_AUST_GDA2020.zip` | 2026-09-03 ~20:22 | CC-BY 4.0, Australian Bureau of Statistics | **EPSG:7844** (GDA2020) |
| `external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/` | ABS ASGS 2021 **Indigenous Location** boundary shapefile. 1,139 polygons national, **189 in NT**. One file carries all three Indigenous levels: `ILO_CODE21`+`ILO_NAME21`, `IAR_CODE21`+`IAR_NAME21`, `IRE_CODE21`+`IRE_NAME21`, `STE_*`. | ABS — `…/ILOC_2021_AUST_GDA2020_SHP.zip` | 2026-09-03 ~20:22 | CC-BY 4.0, Australian Bureau of Statistics | **EPSG:7844** (GDA2020) |
| `external/abs_boundaries/RA_2021_AUST.xlsx` | ABS Remoteness Area 2021 correspondence / allocation workbook (SA1 → RA lookup). | ABS ASGS 2021 remoteness structure page (`https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/remoteness-structure`) | 2026-09-04 | CC-BY 4.0, Australian Bureau of Statistics | tabular (no geometry) |
| `external/nbn/fixedline/nbn_coverage_fixedline.shp` (+ .DBF/.PRJ/.SHX) | NBN **fixed-line** technology footprint polygons (where the fixed-line network reaches). | nbn Co open data via data.gov.au — `https://data.gov.au/data/dataset/national-broadband-network/resource/7c527296-0fef-4a90-817e-cbad0c6c7ffc` (extract dated 2024-03-26) | 2026-09-03 | nbn Co open-data terms | **EPSG:4283** (GDA94) — reproject before use |
| `external/nbn/wireless/nbn_coverage_wireless.shp` (+ .DBF/.PRJ/.SHX) | NBN **fixed-wireless** technology footprint polygons. | nbn Co open data via data.gov.au — `https://data.gov.au/data/dataset/national-broadband-network/resource/1cec1e9a-fd08-4e86-b14f-e41d98afa86f` (extract dated 2024-03-26) | 2026-09-03 | nbn Co open-data terms | **EPSG:4283** (GDA94) — reproject before use |
| `external/acma_rrl/` | ACMA **Register of Radiocommunications Licences** — daily national full extract, 27 CSVs. Key tables: `site.csv` (129,492 rows: `SITE_ID`, `LATITUDE`, `LONGITUDE`, `NAME`, `STATE`, `SITE_PRECISION`, `ELEVATION`; 3,771 rows `STATE == 'NT'`), `licence.csv` (164,205), `client.csv` (14,332: licensee names), `device_details.csv` (2,154,999: `SITE_ID`, `FREQUENCY`, `EIRP`, …). Join `device_details.SITE_ID → site.SITE_ID`, `device_details.LICENCE_NO → licence.LICENCE_NO`, `licence.CLIENT_NO → client.CLIENT_NO`. | ACMA — `https://web.acma.gov.au/rrl-updates/spectra_rrl.zip` (301 → `https://cdn.acma.gov.au/rrl/spectra_rrl.zip`); terms at `https://www.acma.gov.au/radiocomms-licence-data` | 2026-09-03 ~20:22 (extract regenerated daily ~6am AEST) | **ACMA RRL Licence** — usage conditions in `external/acma_rrl/LICENCE.TXT`, must be observed (not CC-BY) | `site.csv` has lat/long columns ≈ EPSG:4326; `SITE_PRECISION` flags accuracy |

---

## `data/processed/` — written by our code only

Currently holds three files from the **old** pipeline (`communities.csv`, `communities.geojson`,
`tier_summary.csv`). These will be replaced when the new `src/` scripts run. Every new file
here gets a sibling `<name>.columns.md` describing each column in one line.

---

## Still to acquire (blockers flagged during the step-1 restructure)

| Needed for | Dataset | Where to get it | Notes |
|---|---|---|---|
| `src/03_load_towers.py` / brief §1 folder list | **MNHP** (Mobile Network Hardening Program) sites → `data/external/mnhp/` | Dept of Infrastructure … Communications & the Arts — MNHP program page | Brief lists the folder; no data acquired yet. Confirm whether it is in scope. |
| brief §1 folder list | **`pump/`** → `data/external/pump/` | unknown | Brief lists `mnhp/ stand/ pump/` together but does not define "pump". Needs clarification before acquiring (Peri-Urban Mobile Program?). |

---

## Sources cross-reference

Full download-URL notes and the original verification log for the ABS / ACMA / NBN pulls:
`docs/analysis_logs/07_download_urls.md` and `docs/analysis_logs/08_downloaded_datasets_verification.md`.
General portal links: `docs/DataSources.md`.
