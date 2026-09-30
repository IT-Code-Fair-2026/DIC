# Data dictionary

Column-level reference for every dataset ticked `[x]` in `docs/DATASET_INVENTORY.md`
(2026-09-05 pass). Column descriptions are drawn from `data/README.md`,
`data/external/services/README.md`, the ACMA RRL DDL (`data/external/acma_rrl/DOC/cr_tables_oracle.sql`),
shapefile `.dbf` headers, and the actual read/write/transform code in
`connecitivity_analysis.ipynb` and `population_distribution_analsis.ipynb`. Where a
notebook only reads a subset of a table's columns, that subset is noted.

Datasets are grouped as **inputs** (raw/external, read only) and **current-pipeline
outputs** (`data/processed/`, written by the two notebooks).

---

## Inputs

### `raw/bushtel/Com_BushTel_Profile_CMC_2024.json`
GeoJSON FeatureCollection, 792 features (points, WGS84). BushTel Community Profile 2024:
master list of NT remote communities. Read by `population_distribution_analsis.ipynb`.

| Column | Type | Description |
|---|---|---|
| `objectid` | int | Sequential row id from the source system; not a stable identifier. |
| `community_id` | int | BushTel's stable numeric community identifier. |
| `community_name` | string | Community name as recorded by BushTel. |
| `community_aliases` | string | Comma-separated alternate/historical names for the community. |
| `community_type` | string | BushTel category, e.g. `Family Outstation`, `Community`, `Town`. |
| `latitude` / `longitude` | float | WGS84 coordinates (duplicated in the feature's `geometry`). |
| `land_council` | string | Land council area the community falls under. |
| `local_govt_council` | string | Local government (shire) council area. |
| `ntg_region` | string | NT Government administrative region. |
| `ward` | string | Local government ward. |
| `electorate` | string | NT Legislative Assembly electorate. |
| `main_language` | string | Main language spoken, as recorded by BushTel; `Not recorded` is common. |
| `population_count` | int (partial) | BushTel's own population figure; populated for 457 of 792 communities. |
| `population_source` | string | Source/reference note for `population_count`. |
| `bushtel_url` | string | Link to the community's BushTel profile page. |

---

### `raw/census_gcp_2021/2021_GCP_all_for_NT_short-header/.../SA1/NT/` (G01 + G02 only)
2021 Census General Community Profile DataPack, NT, short-header CSV. The full folder holds
1,904 CSVs (16 geographies × tables G01–G62); only the **SA1**-level `G01` and `G02` tables
are read, by `population_distribution_analsis.ipynb`. Counts are place-of-usual-residence on
Census night (9 Aug 2021); small counts are randomly perturbed by the ABS for confidentiality.

**Key**: `SA1_CODE_2021` (11-digit ABS SA1 2021 code) in both tables.

**`2021Census_G01_NT_SA1.csv`**: Selected Person Characteristics by Sex, 137 columns. Every
count repeats three times with a suffix: `_M` (male), `_F` (female), `_P` (persons/total).
Column groups (suffix pattern applies to all):

| Column group (prefix) | Description |
|---|---|
| `Tot_P` | Total persons in the SA1. |
| `Age_0_4_yr` … `Age_85ov` | Age-band counts (11 bands from 0–4 to 85+). |
| `Counted_Census_Night_home` / `Count_Census_Nt_Ewhere_Aust` | Counted at home vs elsewhere in Australia on Census night. |
| `Indigenous_psns_Aboriginal` / `..._Torres_Strait_Is` / `..._Bth_Abor_Torres_St_Is` / `Indigenous_P_Tot` | Aboriginal-only, Torres Strait Islander-only, both, and total Indigenous counts. |
| `Birthplace_Australia` / `Birthplace_Elsewhere` | Country of birth. |
| `Lang_used_home_Eng_only` / `..._Oth_Lang` | Language spoken at home. |
| `Australian_citizen` | Count of Australian citizens. |
| `Age_psns_att_educ_inst_*` | Persons attending an educational institution, by age band (0–4, 5–14, 15–19, 20–24, 25+). |
| `High_yr_schl_comp_Yr_12_eq` … `..._D_n_g_sch` | Highest year of school completed (Yr12-eq down to Yr8-or-below, or did-not-go-to-school). |
| `Count_psns_occ_priv_dwgs` / `Count_Persons_other_dwgs` | Persons in private dwellings vs other (non-private) dwellings. |

**`2021Census_G02_NT_SA1.csv`**: Selected Medians and Averages, 9 columns:

| Column | Description |
|---|---|
| `SA1_CODE_2021` | Join key. |
| `Median_age_persons` | Median age, years. |
| `Median_mortgage_repay_monthly` | Median monthly mortgage repayment, $. |
| `Median_tot_prsnl_inc_weekly` | Median total personal income, $/week. |
| `Median_rent_weekly` | Median weekly rent, $. |
| `Median_tot_fam_inc_weekly` | Median total family income, $/week. |
| `Average_num_psns_per_bedroom` | Overcrowding proxy: average persons per bedroom. |
| `Median_tot_hhd_inc_weekly` | Median total household income, $/week. |
| `Average_household_size` | Average household size, persons. |

---

### `raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx`
XLSX, 1 sheet ("Communities with Mobile"), 188 data rows. NT Open Data Portal "Remote
Communities with 3G/4G Mobile Coverage" guide. Read by `connecitivity_analysis.ipynb`
(`header=None`; rows 1–4 are an explanation banner and blanks, the real header is row 5).

| Column | Type | Description |
|---|---|---|
| `SITE NAME` | string | Community/place name. |
| `SITE TYPE` | string | `VILLAGE` / `COMMUNITY` / `HIGHWAY` / `TOURISM`. |
| `POPULATION` | int | Population figure per the guide (its own estimate, not Census). |
| `MACRO CELL` | `YES`/blank | Macro cell (up to ~40 km) covers the site. |
| `SMALL CELL` | `YES`/blank | Small cell (up to ~5 km) covers the site. |
| `PROXIMITY TO CELL` | `YES`/blank | Close enough to a macro cell elsewhere to get coverage without its own site. |
| `PROVIDER` | string | Carrier(s), slash-separated (e.g. `OPTUS/TELSTRA`). |
| `LATITUDE` / `LONGITUDE` | float | WGS84 coordinates. |

---

### `external/mbsp/MBSP - Round {1,2,3,4,5,5A,6,7} Funded Base Stations.kml`
8 KMLs, one per Mobile Black Spot Program funding round; each `Placemark` is one funded
site. Read by `connecitivity_analysis.ipynb` (filtered to `State == "NT"`, deduped by
`MBSP_ID`). **The field schema changes across rounds**; not every column exists in every
file:

| Column | Present in | Description |
|---|---|---|
| `MBSP_ID` | all rounds | Stable per-site funding identifier; used as the de-dupe key (each site appears twice per KML). |
| `Location` | R1–R6 | Site/place name. |
| `Solution_name` | R7 only | Replaces `Location` in Round 7. |
| `Solution_category` | R7 only | New in Round 7; not read by the notebook. |
| `Grantee` | all rounds | Carrier awarded the funding for the site. |
| `State` | all rounds | State/territory; notebook filters to `NT`. |
| `Electorate_2022` | R1–R5A | Federal electorate. |
| `Electorate` | R6, R7 | Same concept, renamed. |
| `Local_Government_Area` | all rounds | LGA the site falls in. |
| `Remoteness` | all rounds | Remoteness classification as labelled by the program (not the ABS RA). |
| `Base_Station_Type` | R1–R6 | Infrastructure type, e.g. Macro/Small/Micro cell. |
| `Solution_type` | R7 only | Replaces `Base_Station_Type` in Round 7. |
| `Site_Status` | all rounds | e.g. `Complete`; notebook derives `mbsp_built` from this. |
| `Completion_Date` | all rounds | Date the site was/is due to be completed. |
| `MNHP_funded` | R1, R2 only | Whether the site was also funded under the Mobile Network Hardening Program; not read by the notebook. |
| geometry (`<coordinates>`) | all rounds | Point, WGS84 (KML is always WGS84). |

The notebook reads `Base_Station_Type` and `Solution_type` interchangeably (falls back to
whichever is present) to get one `site_type` value per row across all 8 schemas.

---

### `external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/`
Shapefile, 1,139 polygon records nationally (189 in NT). ABS ASGS 2021 Indigenous Location
boundaries: one file carries all three nested Indigenous geography levels. CRS: EPSG:7844
(GDA2020). Read by `population_distribution_analsis.ipynb` to tag each village with its ILOC.

| Column | Description |
|---|---|
| `ILO_CODE21` / `ILO_NAME21` | Indigenous Location code/name (finest level). |
| `IAR_CODE21` / `IAR_NAME21` | Indigenous Area code/name (contains one or more ILOCs). |
| `IRE_CODE21` / `IRE_NAME21` | Indigenous Region code/name (contains one or more IAREs). |
| `STE_CODE21` / `STE_NAME21` | State/territory code/name. |
| `AUS_CODE21` / `AUS_NAME21` | Country code/name (always Australia). |
| `AREASQKM21` | Polygon area, km². |
| `LOCI_URI21` | ABS linked-data URI for the polygon. |
| `SHAPE_Leng` / `SHAPE_Area` | Shapefile-computed perimeter/area (native CRS units), not to be confused with `AREASQKM21`. |

---

### `external/abs_boundaries/RA_2021_AUST.xlsx`
XLSX, sheet `SA1_RA_2021_AUST`, 61,845 data rows. ABS Remoteness Area 2021 correspondence
(SA1 → RA lookup). Read by `population_distribution_analsis.ipynb`.

| Column | Description |
|---|---|
| `SA1_CODE_2021` | Join key to the SA1 shapefile / Census tables. |
| `RA_CODE_2021` | Remoteness Area code (`10`/`11`/`12`/`13`/`14`). |
| `RA_NAME_2021` | Remoteness Area name: Major Cities / Inner Regional / Outer Regional / Remote / Very Remote of Australia. |
| `STATE_CODE_2021` / `STATE_NAME_2021` | State/territory of the SA1. |
| `AUS_CODE_2021` / `AUS_NAME_2021` | Country code/name (always Australia). |
| `AREA_ALBERS_SQKM` | SA1 area, km², computed in an Albers equal-area projection. |
| `ASGS_LOCI_URI_2021` | ABS linked-data URI for the SA1. |

---

### `external/abs_boundaries/SA1_2021_AUST_GDA2020_SHP/`
Shapefile, 61,845 polygon records nationally (649 in NT). ABS ASGS 2021 (Edition 3) SA1
boundaries: the population/equity reporting unit for this project. CRS: EPSG:7844
(GDA2020). Read by `population_distribution_analsis.ipynb`.

| Column | Description |
|---|---|
| `SA1_CODE21` | 11-digit SA1 code; primary join key across Census, RA and village tables. |
| `CHG_FLAG21` / `CHG_LBL21` | Flag/label for how this SA1 changed vs. the prior ASGS edition. |
| `SA2_CODE21` / `SA2_NAME21` | Containing Statistical Area Level 2 code/name. |
| `SA3_CODE21` / `SA3_NAME21` | Containing Statistical Area Level 3 code/name. |
| `SA4_CODE21` / `SA4_NAME21` | Containing Statistical Area Level 4 code/name. |
| `GCC_CODE21` / `GCC_NAME21` | Containing Greater Capital City Statistical Area code/name. |
| `STE_CODE21` / `STE_NAME21` | State/territory code/name. |
| `AUS_CODE21` / `AUS_NAME21` | Country code/name (always Australia). |
| `AREASQKM21` | Polygon area, km². |
| `LOCI_URI21` | ABS linked-data URI for the SA1. |

---

### `external/acma_rrl/`: `site.csv`, `licence.csv`, `device_details.csv`
ACMA Register of Radiocommunications Licences, daily national full extract (3 of the 24
CSVs in the folder are selected here). Read by `connecitivity_analysis.ipynb` to build the
"carrier cellular site" layer: a site counts if its devices sit under a licence held by a
mobile carrier (`client.LICENCEE`, from the now-unticked `client.csv`) in a mobile band
(`licence.LICENCE_CATEGORY_NAME`). Column types below are from the ACMA DDL
(`DOC/cr_tables_oracle.sql`); "used" marks columns the notebook actually loads.

**`site.csv`**: 129,491 rows, one row per licensed site (3,771 in NT). All 10 columns read
(`dtype=str`, no `usecols`):

| Column | Type | Used | Description |
|---|---|---|---|
| `SITE_ID` | VARCHAR2(31) | ✓ | Site identifier; join key to `device_details.SITE_ID`. |
| `LATITUDE` / `LONGITUDE` | NUMBER | ✓ | Site coordinates, ≈ WGS84. |
| `NAME` | VARCHAR2(767) | ✓ | Site name. |
| `STATE` | VARCHAR2(80) | ✓ | State/territory; notebook filters to NT. |
| `LICENSING_AREA_ID` | NUMBER | ✓ | ACMA licensing area code. |
| `POSTCODE` | VARCHAR2(18) | ✓ | Site postcode. |
| `SITE_PRECISION` | VARCHAR2(31) | ✓ | Coding of how precisely the coordinates are known. |
| `ELEVATION` | NUMBER | ✓ | Site elevation. |
| `HCIS_L2` | VARCHAR2(31) | ✓ | ACMA height/clearance information surface code. |

**`licence.csv`**: 164,204 rows, one row per licence. Notebook reads only 3 of 16 columns
(`usecols=["LICENCE_NO","CLIENT_NO","LICENCE_CATEGORY_NAME"]`):

| Column | Type | Used | Description |
|---|---|---|---|
| `LICENCE_NO` | VARCHAR2(63) | ✓ | Licence number; join key to `device_details.LICENCE_NO`. |
| `CLIENT_NO` | NUMBER | ✓ | Licensee client id; join key to `client.CLIENT_NO`. |
| `SV_ID` / `SS_ID` | NUMBER(10) | | Service / subservice ids (see `licence_service.csv` / `licence_subservice.csv`). |
| `LICENCE_TYPE_NAME` | VARCHAR2(63) | | Licence type (e.g. Apparatus, Spectrum). |
| `LICENCE_CATEGORY_NAME` | VARCHAR2(95) | ✓ | Licence category/band; notebook matches this against `settings.ACMA_CELLULAR_BANDS` to identify mobile-band licences. |
| `DATE_ISSUED` / `DATE_OF_EFFECT` / `DATE_OF_EXPIRY` | DATE | | Licence lifecycle dates. |
| `STATUS` / `STATUS_TEXT` | VARCHAR2 | | Licence status code/label. |
| `AP_ID` | NUMBER(10) | | Related apparatus/project id. |
| `AP_PRJ_IDENT` | VARCHAR2(511) | | Apparatus/project identifier text. |
| `SHIP_NAME` | VARCHAR2(255) | | Vessel name, for maritime licences only. |
| `BSL_NO` | VARCHAR2(31) | | Broadcasting service licence number, where applicable. |
| `AWL_TYPE` | VARCHAR2(511) | | Amateur/wireless licence subtype, where applicable. |

**`device_details.csv`**: 2,154,998 rows (never loaded in full: size/row count only;
notebook uses `usecols=["LICENCE_NO","SITE_ID"]` purely to link a licence to its site(s)):

| Column | Type | Used | Description |
|---|---|---|---|
| `SDD_ID` | NUMBER(10) | | Device-detail row id. |
| `LICENCE_NO` | VARCHAR2(63) | ✓ | Join key to `licence.LICENCE_NO`. |
| `DEVICE_REGISTRATION_IDENTIFIER` / `FORMER_DEVICE_IDENTIFIER` | VARCHAR2(63) | | Device registration id, current and former. |
| `AUTHORISATION_DATE` | DATE | | Date the device was authorised. |
| `CERTIFICATION_METHOD` | VARCHAR2(255) | | How the device was certified. |
| `GROUP_FLAG` | VARCHAR2(255) | | Grouped-device indicator. |
| `SITE_RADIUS` | NUMBER | | Radius of operation, where the device isn't a fixed point. |
| `FREQUENCY` | NUMBER | | Operating frequency. |
| `BANDWIDTH` | NUMBER | | Channel bandwidth. |
| `CARRIER_FREQ` | NUMBER | | Carrier frequency. |
| `EMISSION` | VARCHAR2(63) | | Emission designator. |
| `DEVICE_TYPE` | VARCHAR2(1) | | Device type code (transmitter/receiver/etc.). |
| `TRANSMITTER_POWER` / `TRANSMITTER_POWER_UNIT` | NUMBER / VARCHAR2(31) | | Transmitter power and its unit. |
| `SITE_ID` | VARCHAR2(31) | ✓ | Join key to `site.SITE_ID`. |
| `ANTENNA_ID` | VARCHAR2(31) | | Join key to `antenna.csv` (not selected in this pass). |
| `POLARISATION` | VARCHAR2(3) | | Antenna polarisation. |
| `AZIMUTH` / `HEIGHT` / `TILT` | NUMBER | | Antenna orientation and mounting height. |
| `FEEDER_LOSS` | NUMBER | | Feeder cable loss. |
| `LEVEL_OF_PROTECTION` | NUMBER | | Interference protection level. |
| `EIRP` / `EIRP_UNIT` | NUMBER / VARCHAR2(31) | | Effective isotropic radiated power and its unit. |
| `SV_ID` / `SS_ID` | NUMBER(10) | | Service/subservice ids. |
| `EFL_ID` / `EFL_FREQ_IDENT` / `EFL_SYSTEM` | VARCHAR2 | | Earth/fixed-link identifiers, where applicable. |
| `LEQD_MODE` | VARCHAR2(1) | | Equipment mode code. |
| `RECEIVER_THRESHOLD` | NUMBER | | Receiver sensitivity threshold. |
| `AREA_AREA_ID` / `AREA_DESCRIPTION` | NUMBER(10) / VARCHAR2(9) | | Coverage/service area id and description. |
| `CALL_SIGN` | VARCHAR2(255) | | Radio call sign, where applicable. |
| `AP_ID` | NUMBER(10) | | Related apparatus/project id. |
| `CLASS_OF_STATION_CODE` | VARCHAR2(31) | | Join key to `class_of_station.csv`. |
| `SUPPLIMENTAL_FLAG` | VARCHAR2(199) | | Supplemental licence indicator (ACMA's spelling). |
| `EQ_FREQ_RANGE_MIN` / `EQ_FREQ_RANGE_MAX` | NUMBER | | Equipment frequency range. |
| `NATURE_OF_SERVICE_ID` | VARCHAR2(3) | | Join key to `nature_of_service.csv`. |
| `HOURS_OF_OPERATION` | VARCHAR2(11) | | Permitted operating hours. |
| `SA_ID` | NUMBER(10) | | Join key to `satellite.csv`, for satellite services. |
| `RELATED_EFL_ID` | NUMBER | | Related earth/fixed-link id. |
| `EQP_ID` | NUMBER(10) | | Equipment id. |
| `ANTENNA_MULTI_MODE` | VARCHAR2(3) | | Multi-mode antenna indicator. |
| `POWER_IND` | VARCHAR2(14) | | Power indicator code. |
| `LPON_CENTER_LONGITUDE` / `LPON_CENTER_LATITUDE` | NUMBER | | Centre point for a licensed point-of-operation-not-a-fixed-site record. |
| `TCS_ID` / `TECH_SPEC_ID` / `DROPTHROUGH_ID` | various | | Technical/cross-reference ids. |
| `STATION_TYPE` | VARCHAR2(511) | | Station type description. |
| `STATION_NAME` | VARCHAR2(63) | | Station name. |

---

### `external/nbn/fixedline/nbn_coverage_fixedline.shp`
Shapefile, 5,316 polygon records. NBN fixed-line technology footprint. CRS: EPSG:4283
(GDA94). Reproject before use per `data/README.md`. Not currently read by either notebook.

| Column | Type | Description |
|---|---|---|
| `polygon_id` | string (20) | Footprint polygon identifier; the only attribute column: no technology/speed tier field. |

### `external/nbn/wireless/nbn_coverage_wireless.shp`
Shapefile, 505,615 polygon records. NBN fixed-wireless technology footprint. CRS: EPSG:4283
(GDA94). Reproject before use. Not currently read by either notebook.

| Column | Type | Description |
|---|---|---|
| `Polygon_id` | numeric (18) | Footprint polygon identifier; the only attribute column. |

---

## Current-pipeline outputs (`data/processed/`)

### `processed/mobile_sites.csv` / `.geojson`
695 rows/features, WGS84 points. Combined mobile-site inventory from three sources (ACMA
carrier towers + NT coverage guide + MBSP funded sites), written by
`connecitivity_analysis.ipynb`. Column descriptions are the notebook's own `column_notes`
(also saved to `processed/03_mobile_sites.columns.md`):

| Column | Description |
|---|---|
| `source` | Which layer this row came from: `acma` (licensed carrier tower), `guide` (NT coverage guide entry), or `mbsp` (Mobile Black Spot Program funded site). |
| `name` | Site or place name as given by the source. |
| `latitude` / `longitude` | WGS84 coordinates. |
| `site_type` | Meaning differs by source: for `guide` rows it's the PLACE type (VILLAGE/COMMUNITY/HIGHWAY/TOURISM); for `mbsp` rows it's the INFRASTRUCTURE type (Macro/Small/Micro cell); for `acma` rows it's blank (not recorded in the licence register). Don't group across sources on this column without filtering by `source` first. |
| `carriers` | Semicolon-separated carrier name(s) at the site (acma/guide), or the MBSP grantee (mbsp). |
| `n_carriers` | Count of carriers in the `carriers` field. |
| `population` | Only populated for `guide` rows (from the coverage guide's `POPULATION` column); blank elsewhere. |
| `guide_macro` / `guide_small` / `guide_proximity` | Coverage-guide flags; only meaningful for `guide` rows. |
| `mbsp_round` | MBSP funding round label; only populated for `mbsp` rows. |
| `mbsp_is_small` | Whether the funded MBSP station is small/micro cell; only populated for `mbsp` rows. |
| `mbsp_built` | Whether the MBSP site's status was `Complete`; only populated for `mbsp` rows. |

---

### `processed/community_connectivity_priority.csv`
188 rows: one per NT coverage-guide site (`source == "guide"` rows from `mobile_sites`),
sorted by `likely_gap` then `population` descending. Written by `connecitivity_analysis.ipynb`.

| Column | Description |
|---|---|
| `name` | Community/place name (from the coverage guide). |
| `latitude` / `longitude` | WGS84 coordinates. |
| `site_type` | Coverage-guide PLACE type (VILLAGE/COMMUNITY/HIGHWAY/TOURISM). |
| `population` | Population per the coverage guide. |
| `has_macro` / `has_small` | Guide's own macro-cell / small-cell coverage flags. |
| `proximity_only` | Guide's "close enough to a macro cell elsewhere" flag. |
| `nearest_tower_km` | Great-circle (haversine) distance, km, to the nearest ACMA-licensed carrier cellular site. |
| `nearest_tower_carrier` | Carrier name at that nearest tower. |
| `nearest_mbsp_km` | Haversine distance, km, to the nearest MBSP-funded site. |
| `nearest_mbsp_round` | MBSP funding round of that nearest site. |
| `nearest_mbsp_built` | Whether that nearest MBSP site's status was `Complete`. |
| `likely_gap` | Triage flag: `True` when the guide shows no macro/small coverage **and** the nearest real tower is >15 km away. The notebook's own comment flags this as "a starting-point triage flag, not a validated verdict"; the 15 km cutoff should be checked against whatever the guide treats as "in range" before use. |

---

### `processed/sa1_boundaries.geojson`
649 polygon features, one per NT SA1. Reprojected to WGS84 (CRS84) for the GeoJSON.
Written by `population_distribution_analsis.ipynb`.

| Column | Description |
|---|---|
| `sa1_code` | 11-digit ABS SA1 2021 code (from `SA1_CODE21`). |
| `sa2_name` / `sa3_name` / `sa4_name` | Containing SA2/SA3/SA4 names (from the SA1 shapefile's `SA2_NAME21`/`SA3_NAME21`/`SA4_NAME21`), carried through for map labelling. |

---

### `processed/villages_with_areas.csv` / `.geojson`
793 rows/features, WGS84 points: the 792 BushTel communities (one duplicate id noted in
the row count), each tagged with its containing SA1/ILOC area and that SA1's Census
population. Written by `population_distribution_analsis.ipynb`.

| Column | Description |
|---|---|
| `community_id` … `bushtel_url` | Passed through unchanged from `raw/bushtel/Com_BushTel_Profile_CMC_2024.json` (see that section above): `community_id`, `community_name`, `community_aliases`, `community_type`, `latitude`, `longitude`, `land_council`, `local_govt_council`, `ntg_region`, `ward`, `electorate`, `main_language`, `bushtel_url`. |
| `population_bushtel_2024` | BushTel's own population figure (renamed from `population_count`); partial coverage. |
| `population_bushtel_source` | Renamed from `population_source`. |
| `sa1_code` | ABS SA1 2021 code the village point falls inside (spatial join against the SA1 shapefile). |
| `sa2_name` | Name of the SA2 containing that SA1. |
| `iloc_code` / `iloc_name` | ABS Indigenous Location code/name the village point falls inside (spatial join against the ILOC shapefile). |
| `pop_census_2021` | 2021 Census total persons (`Tot_P_P` from census `G01`) for the **SA1** this village sits in; the same figure repeats for every village sharing that SA1; it is not a per-village population. |
| `n_villages_in_sa1` | Count of BushTel villages that fall within the same SA1 as this one. |

---

## Notes on scope

- Only the datasets ticked in `docs/DATASET_INVENTORY.md` are covered. In particular, only
  3 of the 24 `acma_rrl` CSVs (`site`, `licence`, `device_details`) are documented: `client.csv`
  was deliberately left unticked even though the notebook currently reads it too (to link a
  licence's `CLIENT_NO` to a carrier name via `LICENCEE`); flag if that link should be added
  back in.
- The old pipeline's outputs and the un-selected `communities.*` /
  `sa1_report.*` files are not documented here: see `docs/DATASET_INVENTORY.md` for why each
  is marked unused/stale.
