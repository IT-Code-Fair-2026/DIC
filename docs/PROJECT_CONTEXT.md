# NT Remote Connectivity — project context

Snapshot of everything established in the first working session (2026-09-05).
Read this before any new chat in the project. Update it when a decision changes.

---

## 1. The challenge

**CDU IT Code Fair — Data Innovation Challenge 2026.** Theme: Remote Connectivity.
Link: https://itcodefair.cdu.edu.au/data-innovation-challenge/

- **Submission deadline: Wed 30 Sep 2026**, by email to `itcodefair@cdu.edu.au` (a ZIP of the
  report + source code). **Registration closed 18 Sep 2026, 5pm** (was previously noted here
  as 15 Sep — corrected 2026-09-29 against the official page). Challenge Day **Wed 7 Oct 2026,
  09:00–17:00**, Festival Learning Space 1.12, Danala, ECP Darwin, CDU. Awards 5 Nov.
- Teams of 2–4 enrolled CDU IT coursework students (undergrad, postgrad, TAFE, short courses).
  **HDR students are not eligible.**
- **Email subject line format:** `Data Innovation Challenge Submission – [Group] – IT Code
  Fair 2026`. Name the group properly and include every required file in the ZIP.
- **Four submission deliverables** (confirmed 2026-09-29, resolves the earlier "check which
  applies" note below):
  1. Data-analysis report — PDF only.
  2. 5-minute presentation slide deck (a separate artefact from the 10+5 min live session below).
  3. Interactive prototype solution (this repo's Streamlit app).
  4. Python source (`.py` / notebooks, no package restrictions) with a README giving
     reproducing instructions — this repo's root `README.md`.
  - **Datasets themselves don't need to be submitted** — link to them in the report/appendix
    instead (this repo already does this in `data/README.md`).
- **Report format, exactly as specified:**
  - File type PDF only; **max 8 pages** (excludes title page, references, appendices);
    ~2,500 words as a *guideline*, not a hard limit.
  - Page setup: A4, continuous page numbering; **header AND footer** must both carry Team
    Number and Page Number (previously noted as header-only here — corrected).
  - Fonts: Calibri or Arial. Title 20pt bold · section headings 14pt bold · body 11pt regular
    · captions & references 10pt.
  - File name: `DataChallenge_Team xx_Report.pdf` (xx = team number).
  - Structure: title page (title, team number, members + roles, date, challenge name) →
    150–250 word summary (problem/gap, approach, key findings, ethical/cultural/community
    impacts, recommendations) → Introduction → Methodology → Findings → Discussion (ethical,
    cultural, community impacts) → Recommendations (government / industry / community) →
    References → Appendices (AI-use declaration, source code, dataset links).
- **Presentation on Challenge Day: 10-minute pitch + 5-minute Q&A per team, face-to-face with
  industry judges.** (The separate "5-minute slide deck" above is a submitted file, not the
  live session's time limit — both are real, they're not in conflict.)
- Tasks the brief names: find the gaps; make them understandable; integrate multiple sources;
  ethical/cultural/community impacts; solutions usable offline / low-connectivity.
- **Judging criteria:** datasets, overall creativity & originality, technical sophistication,
  contextual relevance & practicality, ethical considerations, presentation. First winner and
  runner-up only (no further placings). Judging panel: Sandeep Rasali and David Winslade
  (Dept of Corporate & Digital Development NTG), Mohammad Aurangzeb Khan (Data Warehouse
  Developer, NTG), Dr Cat Kutay (Senior Lecturer IT, CDU).
- **Officially suggested datasets** (participants aren't limited to these; listed so it's
  clear which of *our* sources map to which suggestion): NT Remote Areas Mobile Coverage →
  our `raw/nt_mobile_coverage/` guide xlsx; National Broadband Network → our
  `external/nbn/` footprints; ACMA Site Location Map → our `external/acma_rrl/` register.
  **Not currently used by this project** (confirm before the deadline whether they're worth
  adding, or note the gap in the report's Discussion/Recommendations): ADII Dashboard
  (Australian Digital Inclusion Index), ACCC Mobile Infrastructure Report data release,
  Tropical cyclone reports, First Nations Connectivity Mapping Tool, ABS TableBuilder.

---

## 2. Standing rules (agreed)

1. **BushTel `community_id` is the spine.** Every people-side fact hangs off a village; every infrastructure fact is measured *from* a village.
2. **Census 2021 is the only real population.** It exists only at SA1 level, so population lives on the SA1. BushTel `population_count` and coverage-guide `POPULATION` are **reference only**, never summed as population.
3. **Village is the unit for distance.** SA1 is the unit for population / equity numbers. A census figure is never split across the villages inside an SA1.
4. **Notebooks are the source of truth.** `README.md` is outdated (folder names, file names, CRS rule). Don't treat README-vs-notebook differences as bugs.
5. **Distances are triage, not coverage claims.** Straight-line, no roads/terrain/signal.
6. **Don't assume — inspect the file or ask.**
7. Indigenous share was dropped **on purpose** (whole-community view). Be ready to justify this in the Discussion section since judges score cultural impact.
8. Highway / tourism rows in the coverage guide are **kept, tagged**, for the "funding lands here, villagers get nothing" angle — but excluded from community rankings.

---

## 3. Repo layout (as actually used)

```
data/raw/            supplied by CDU, read-only
data/external/       downloaded by us, read-only
data/processed/      written by the notebooks (was data/new_processed/ until 2026-09-27)
notebooks/           00a … 11, run in order by run_pipeline.py
app/                 Streamlit dashboard, reads data/processed/
docs/                DATASET_INVENTORY.md, DATA_DICTIONARY.md/.pdf (to be built by Claude Code)
connecitivity_analysis.ipynb            -> mobile_sites, community_connectivity_priority
population_distribution_analsis.ipynb   -> villages_with_areas, sa1_report(.csv/.geojson)
```

Old pipeline outputs in `data/processed/` (01_…, 02_…, 03_…, 04_…) are stale and unused.

---

## 4. Datasets

### Raw (CDU-supplied)
| File | What | Notes |
|---|---|---|
| `raw/bushtel/Com_BushTel_Profile_CMC_2024.json` | 792 NT communities, points | spine. 457 have BushTel pop. Types: 630 Family Outstation, 59 Major, 45 Town Camp, 37 Minor, 13 Village, 7 Town, 1 City. Has `community_aliases` (use for name matching). |
| `raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx` | 188 NT places, "GUIDE only" | header a few rows down (find "SITE NAME"). Cols: SITE NAME, SITE TYPE (148 COMMUNITY / 17 HIGHWAY / 15 TOURISM / 8 VILLAGE), POPULATION, MACRO CELL, SMALL CELL, PROXIMITY TO CELL, PROVIDER, LAT, LONG. |
| `raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx` | small-cell sites | unused, columns unknown |
| `raw/rict/Com_RICT_Community_NIAA_2024.json` | RICT communities + service indicators | unused, columns unknown |
| `raw/census_gcp_2021/…/SA1/NT/2021Census_G01_NT_SA1.csv` | G01 | uses `Tot_P_P`. Indigenous cols available, unused by choice. |
| `raw/census_gcp_2021/…/SA1/NT/2021Census_G02_NT_SA1.csv` | G02 | uses `Median_tot_hhd_inc_weekly`, `Average_household_size`. |
| `raw/school_data.xlsx` | ACARA schools, 217 NT | sheet "ASL Search Results", header row 2. Unused so far. |

### External (downloaded)
| File | What | Notes |
|---|---|---|
| `external/abs_boundaries/SA1_2021_AUST_GDA2020_SHP/` | 649 NT SA1 polygons | EPSG:7844. Key `SA1_CODE21`. |
| `external/abs_boundaries/ILOC_2021_AUST_GDA2020_SHP/` | 189 NT ILOC polygons | also carries IARE/IREG codes |
| `external/abs_boundaries/RA_2021_AUST.xlsx` | SA1 → Remoteness Area | sheet `SA1_RA_2021_AUST`; `RA_NAME_2021`, `AREA_ALBERS_SQKM` |
| `external/abs_boundaries/SAL_…`, `RA_…_SHP` | suburbs, RA polygons | unused |
| `external/mbsp/MBSP - Round *.kml` (8) | Mobile Black Spot Program funded sites | 49 NT after dedupe on `MBSP_ID` (each site listed twice per KML). 41 built / 8 not. |
| `external/acma_rrl/` | ACMA licence register, 27 CSVs | `site` (3,771 NT), `licence`, `client`, `device_details` (2.15M rows — never load fully). Joins: `device_details.SITE_ID→site.SITE_ID`, `device_details.LICENCE_NO→licence.LICENCE_NO`, `licence.CLIENT_NO→client.CLIENT_NO`. |
| `external/nbn/fixedline/*.shp`, `external/nbn/wireless/*.shp` | NBN footprints, EPSG:4283 | unused so far; attribute fields unknown |
| `external/stand/*.json` | STAND program sites | unused |
| `external/services/_raw/ga_{police,hospitals,gp}_nt.geojson` | 66 / 11→8 / 128 points | unused so far; `05_services.csv` (419 pts) exists per README but not seen |

CRS: ABS = EPSG:7844, NBN = EPSG:4283, JSON/KML = 4326; all ≈ equal at sub-metre. Distance work: haversine now; move to EPSG:3577 + `sjoin_nearest`.

---

## 5. Processed outputs (`data/processed/`)

### `villages_with_areas.csv` / `.geojson` — 792 rows × 21 cols ✅ fixed 2026-09-05
`community_id, community_name, community_aliases, community_type, latitude, longitude, land_council, local_govt_council, ntg_region, ward, electorate, main_language, bushtel_url, population_bushtel_2024, population_bushtel_source, sa1_code, sa2_name, iloc_code, iloc_name, pop_census_2021, n_villages_in_sa1`
- `pop_census_2021` = **the SA1's total**, repeated on every village in that SA1. Not a village count. Consider renaming `sa1_pop_census_2021`.
- 179 distinct SA1s, 154 ILOCs. 0 villages missing a tag.

**Rebuild (v2, `notebooks/01_villages.ipynb` → `villages.csv`):**
- **792 rows, `community_id` unique — there is no duplicate.** BushTel has 792 features / 792 distinct ids; the "793" seen last session was a header-inclusive CSV line count. nb 01 asserts `is_unique` **and** `len == 792`; no dedupe step. (00a EDA, 2026-09-06.)
- `population_count` → **`population_count_bushtel`**, `population_source` → `population_source_bushtel`: kept in the table but **not used anywhere downstream**.
- **ILOC dropped** (decision 2026-09-06): no `iloc_code` / `iloc_name`. SA1 is the only region tag. ILOC shapefile unticked in `DATASET_INVENTORY.md`.
- Remoteness reality (00a finding 11): "Outer Regional" in the NT = greater Darwin — 355 SA1s but only ~0.2% of NT land and **13 of 792 villages**. **673 / 792 villages are Very Remote**, 106 Remote. Report/prototype framing keys on Remote + Very Remote; per-class comparisons quote village counts, not SA1 counts.

### `sa1_report.csv` / `sa1_report.geojson` — 649 rows (645 polygons; 4 offshore/no-address codes have no geometry)
`sa1_code, sa2_name, sa3_name, sa4_name, remoteness_name, area_sqkm, pop_census_2021, median_hh_income_weekly, avg_household_size, n_villages, n_villages_with_bushtel_pop, village_bushtel_pop_sum, village_names, village_bushtel_pops`
- Remoteness: 355 Outer Regional, 131 Remote, 159 Very Remote, 4 special.
- Top village-bearing SA1s hold 34–44 villages over 10,000–87,000 km² (Tanami, West Arnhem, Sandover-Plenty, Petermann-Simpson). This is the "300 people, 30,000 km², one tower" picture.
- GeoJSON version = polygons joined to report; use this in kepler, not the bare `sa1_boundaries.geojson`.

**Rebuild (v2, `notebooks/02_sa1_report.ipynb` → `sa1_report.csv`):**
- **Decision (revised 2026-09-06):** **keep all 649 rows**, merge polygons with `validate="1:1"`. Add boolean **`census_pop_suppressed = Tot_P_P < 5`** (34 rows True). Still write those 34 rows to `data/processed/area_with_population_lessthan_5.csv` as a side list. Set `Median_tot_hhd_inc_weekly` and `Average_household_size` **`0 → NaN`** (ABS suppression, 34 / 33 rows).
- Reason the drop was reversed: **30 inhabited BushTel outstations sit in 4 of the suppressed (`Tot_P_P == 0`) SA1s** — Tanami `70201105311` (8), Yuendumu-Anmatjere `70201105402` (11), Gulf `70205106609` (10), Sandover-Plenty `70201105205` (1). Dropping the SA1 would strand them with no population reference. Their SA1's `sa1_report` row has `pop_census_2021 = 0` and `census_pop_suppressed = True`.
- **`villages.csv` does not carry a census population column** — population lives only on `sa1_report` (SA1 is the unit for population, §2). villages.csv carries `sa1_code` / `sa2_name` / `remoteness_name` / `is_remote` / `n_villages_in_sa1`; population is joined at SA1 level in nb 07.
- `is_remote` (bool) = `remoteness_name` in {Remote, Very Remote} → `True`; Outer Regional → `False`. 779 of 792 villages are `True`.
- SA1 key aligns 1:1 across SA1 shapefile / RA workbook / Census G01 & G02 (649 identical codes); 4 offshore / no-usual-address codes have null geometry (GeoJSON = 645). Those 4 still carry population (No usual address = 3,500; the three Migratory codes 78 / 14 / 0) so they stay in the CSV.
- **v2 columns (14):** `sa1_code, sa2_name, sa3_name, sa4_name, remoteness_name, is_remote, area_sqkm, pop_census_2021, census_pop_suppressed, median_hh_income_weekly, avg_household_size, n_villages, n_villages_with_bushtel_pop, village_names`. Built & run 2026-09-06: 649 rows, every merge `validate="1:1"`, `sum(n_villages) == 792`, `sum(pop_census_2021) == 232,565`.
- **Dropped from the old column list:** `village_bushtel_pop_sum` and `village_bushtel_pops` — they summed / listed BushTel `population_count`, which §2 says is reference only and must never be summed. `n_villages_with_bushtel_pop` (a *count*, not a sum) is kept for data-completeness.

### `mobile_sites.csv` / `.geojson` — 695 rows
`source (acma 458 / guide 188 / mbsp 49), name, latitude, longitude, site_type, carriers, n_carriers, population, guide_macro, guide_small, guide_proximity, mbsp_round, mbsp_is_small, mbsp_built`
- `site_type` means different things per source — always filter by `source` first.
- ACMA rows: carrier licence in a "cellular" band at that site. Band list currently includes 3.4/3.6 GHz, 26/28 GHz, AWL — too wide (see open issues).
- MBSP `site_type` has 5 spellings for 3 categories.

### `community_connectivity_priority.csv` — 188 rows (guide places only)
`name, latitude, longitude, site_type, population, has_macro, has_small, proximity_only, nearest_tower_km, nearest_tower_carrier, nearest_mbsp_km, nearest_mbsp_round, nearest_mbsp_built, likely_gap`
- `likely_gap` = no macro AND no small AND nearest ACMA tower > 15 km. 10 rows flagged. **Reference point, not truth.**
- Nearest tower: median 1.9 km, p75 6.6 km, max 55 km. 68 places sit on a tower (<0.5 km).

---

## 6. How the pipeline works today

**population_distribution_analsis.ipynb**
01 load BushTel → tidy table, `population_count`→`population_bushtel_2024`.
02 spatial-join villages (within) to NT SA1 and ILOC polygons; assert 0 unmatched. Merge G01 `Tot_P_P` by `sa1_code`; add `n_villages_in_sa1`. Build `sa1_report` from RA workbook + shapefile names + G02 + G01 + village roll-up. Write CSV + GeoJSON for both.

**connecitivity_analysis.ipynb**
03 ACMA: NT sites with a device under a licence held by Telstra/Optus/Vodafone/TPG/Hutchison/Pivotel/Dense Air in a listed band. Guide: booleans from MACRO/SMALL/PROXIMITY, split PROVIDER on "/". MBSP: NT placemarks, dedupe on MBSP_ID. `pd.concat` → `mobile_sites`.
05 for each guide row, haversine to every ACMA site → argmin = nearest; same vs all MBSP sites → `community_connectivity_priority`.

---

## 7. Fixes applied this session
- ✅ `villages_with_areas` was dropping `sa1_code/sa2_name/iloc_code/iloc_name` (column list built from pre-join frame). Fixed: build from `village_out`/`merged`, with assert guard.
- ✅ `sa1_report.geojson` now = polygons + report fields (merge on `sa1_code`, `validate="1:1"`, drop null geometry).
- ✅ Village GeoJSON now built from `merged` (carries census + n_villages cols).
- ✅ `sa1_report.csv` write un-commented.
- Haversine + loop documented with plain-language comments.

---

## 8. Open issues / decisions still to make
1. **Spine mismatch (biggest):** gap table is built on 188 guide places, not 792 BushTel villages. Rebuild on BushTel; attach guide read by nearest-match (≤2 km) + name/alias check. Unmatched villages get `guide_* = NaN`.
2. **Tower set for distance** should be ACMA ∪ built MBSP ∪ guide macro/small, deduped within ~100 m (58 ACMA sites have a neighbour that close). Currently ACMA only; 5 built MBSP sites have no ACMA match.
3. **Handset-band flag:** add `handset_band` (700/850/900/1800/2100 MHz = True; 3.4/3.6/26/28 GHz, AWL = False). Distance uses True only. Pivotel is a different kind of carrier — check.
4. **Proximity contradiction:** all 10 `likely_gap` rows have `proximity_only=True` yet 15–43 km to nearest ACMA site. Guide and ACMA disagree; decide a rule. Population not yet in the flag.
5. **`nearest_mbsp_*` mixes built/unbuilt** (46 of 188 nearest are unbuilt). Split into nearest-built and nearest-funded-unbuilt.
6. Rename `likely_gap` → `distance_gap_candidate`; keep 15 km as a named constant; compute after population join.
7. Normalise MBSP `site_type` → macro / small / micro.
8. Rename `pop_census_2021` on village rows → `sa1_pop_census_2021`.
9. Stale docstrings/markdown in step 02 (mention Indigenous share, unit-of-analysis wording) — update to match rules in §2.
10. Move nearest-neighbour from Python loop to `gpd.sjoin_nearest` in EPSG:3577; add buffer counts (`n_towers_10km`, `carriers_10km`).
11. Datasets not yet used that the brief rewards: NBN footprints, RICT, STAND, services (schools/clinics/police/hospitals), remoteness, income. Offline-first prototype not started.
12. Claim that BushTel population is Indigenous-only needs a citable source (`population_bushtel_source` = "Homelands Service Provider Report 2023").
13. Empty SA1s in the interior have no villages — not a gap; say so in the report.
14. Verify: 10-min vs 5-min presentation; whether MNHP and "pump" folders are in scope.

---

## 9. Target pipeline

```
bushtel ──────────────────────────► 01_villages
SA1 shp / ILOC shp / RA xlsx ──────► 02_villages_with_areas (+ sa1_code, iloc_code)   ─┐
Census G01 / G02 ──────────────────► 02_sa1_report (.csv + .geojson)                     │
ACMA / guide / MBSP ───────────────► 03_mobile_sites (+ handset_band, clean site_type)   │
                                     03b_existing_towers (acma ∪ built mbsp ∪ guide, 3577)│
NBN fixedline / wireless ──────────► 04_nbn_footprint (NT only, 3577)                     ├──► 07_village_gap (792 rows: nearest handset tower,
schools / GA police / hosp / GP ───► 05_services (419 pts)                               │     mbsp built / unbuilt, in NBN?, km to each service,
RICT / STAND ──────────────────────► 06_programs                                         ┘     guide read, buffer counts, tier T1–T5)
                                                                                                        │
                                                                                                        ▼
                                                                                          08_sa1_gap_summary (roll to SA1, join 02_sa1_report:
                                                                                          people per tower, share of villages in gap, equity)
                                                                                                        │
                                                                                                        ▼
                                                                                              viewer / offline-first map
```

---

## 10. Tooling notes
- **kepler.gl:** a GeoJSON with `latitude`/`longitude` columns creates both a Point and a GeoJSON layer of the same data — keep the Point layer, hide the other. Colour `mobile_sites` by `source`. Colour `sa1_report.geojson` polygons by `pop_census_2021` / `remoteness_name`. Distinguish "no BushTel pop" from "tiny". Turn on tooltips.
- **Claude Code:** two prompts prepared — (1) build `docs/DATASET_INVENTORY.md` checklist; (2) build `docs/DATA_DICTIONARY.md/.pdf` from ticked datasets only, with a join-key page and available-but-unused fields section.
- Read `sa1_code` as **string** everywhere (`dtype={"sa1_code": str}`).

---

## 11. Decisions locked in the 00a / 00b EDA review (2026-09-06)

Binding for the v2 notebooks. Full evidence is in `notebooks/00a_*` and `notebooks/00b_*` (data-quality tables) and the plots in `docs/eda/`.

**People side (nb 01 / 02)**
- No duplicate `community_id` — 792 features, 792 ids. Assert unique + `len == 792`; no dedupe.
- `population_count` → `population_count_bushtel`, `population_source` → `population_source_bushtel`; kept, never used downstream.
- **ILOC dropped** — no `iloc_code` / `iloc_name` anywhere; unticked in `DATASET_INVENTORY.md`; shapefile left on disk.
- `sa1_report` keeps all **649** rows; add `census_pop_suppressed = Tot_P_P < 5`; G02 income & household size `0 → NaN`; still emit `area_with_population_lessthan_5.csv`.
- Remoteness framing keys on Remote + Very Remote (673 + 106 of 792 villages); "Outer Regional" NT = greater Darwin.

**ACMA towers (nb 03)** — built & run 2026-09-06 → `towers.csv` / `towers.geojson`, **431 rows**, key `site_id`.
- Tower = a site with ≥1 carrier transmitter (`DEVICE_TYPE == 'T'`) whose `FREQUENCY` is in a handset band (700 / 850 / 900 / 1800 / 2100 MHz; Hz). Windows non-overlapping: 850 = 824–890 MHz, 900 = 890–960 MHz.
- `max_eirp` / `max_height` **dropped** (2026-09-06) — not used downstream, register values are unreliable.
- `is_planning_site` (name contains Planning / Nominal / Proposed) flags register placeholders, not built towers. **1** in the NT ("Nominal Planning Site Blake Street DARWIN", Telstra). Kept, not dropped — nb 06 decides whether to exclude it from distance.
- Funnel: 3,771 NT sites → 7,387 carrier tx → 5,485 handset-band carrier tx → **461** sites. Old 16-category method = **458** (reproduced); 453 kept by both, 5 only-old (2.5 GHz-only), 8 only-new (handset tx filed under `Point to Point`).
- Pivotel: 2 tx at 2 sites, both **1875 MHz** (PMTS Class B) → band 1800, so Pivotel counts.
- `carriers` / `n_carriers` = raw licensee **brands**. `networks` / `n_networks` fold same-network brands: **Vodafone + Hutchison + TPG → `TPG`**; Telstra / Optus / Pivotel / Dense Air unchanged. nb 06 uses `n_networks` for redundancy. Distribution: `n_networks` 1→331, 2→70, 3→30; 21 towers carry 4 brands but 3 networks.
- **Co-location clustering:** connected components on handset-tower pairs within **100 m** (EPSG:3577). 461 → **431** rows; 30 clusters merge 2 sites each. `carriers` / `bands` unioned, `n_transmitters` summed, `max_*` maxed, `is_pivotel` any, `n_colocated` + `colocated_site_ids` added, representative `site_id` = most transmitters.
- **`spectrum_depth_khz` recomputed post-cluster** as the sum of *distinct* `carrier × frequency × bandwidth` channels (repeated sectors and the same channel on two co-located `SITE_ID`s counted once). Territory total raw 79.3M kHz → deduped 26.7M kHz; per-tower median ~**45k**, max ~**268k**. (e.g. Howard Springs compound 846,990 → 247,330 kHz.)
- Columns (15): `site_id, name, latitude, longitude, carriers, n_carriers, networks, n_networks, n_transmitters, bands, spectrum_depth_khz, is_pivotel, is_planning_site, n_colocated, colocated_site_ids`.

**NBN footprint (nb 04)** — built & run 2026-09-06 → `nbn_footprint.geojson`, **2 features**, key `technology`.
- Each shapefile read within the NT bbox, CRS set to EPSG:4283 if the `.prj` is missing, reprojected to 4326, all attributes dropped, `technology` set from the source file, dissolved to one polygon. `fixed_line` 35→1 (227 km²), `fixed_wireless` 348→1 (1,279 km², all around Darwin).
- Villages inside a footprint: fixed-line **30**, fixed-wireless **1**, either **31 of 792**. So **761 villages (96%) have no NBN fixed option** — nb 06 `in_nbn_fixed_line` / `in_nbn_fixed_wireless` are `False` for almost every remote village; that is the finding, not a bug.

**Program sites (nb 05)** — built & run 2026-09-06 → `program_sites.csv` / `.geojson`, **533 rows**, key `program_site_id` (`mbsp-<MBSP_ID>` / `guide-<name-slug>` e.g. `guide-ali-curung` / `rict-<objectid>`), `source` ∈ {mbsp 49, guide 188, rict 296}.
- Common cols `program_site_id, source, name, latitude, longitude`; then source-prefixed (null for other sources): mbsp `mbsp_site_type, mbsp_built, mbsp_round`; guide `guide_place_type, guide_macro, guide_small, guide_proximity, guide_population`; rict `rict_site_type`.
- **MBSP** 2,710 placemarks → 98 NT → **49** deduped on `MBSP_ID`. `site_type` map: {Macro cell, Macrocell}→macro (11), {Small cell, Small Cell}→small (33), {Microcell}→micro (5). `mbsp_built` = `Site_Status == "Complete"` → **41 built / 8 not**. Rounds 1/2/4/5/7 (3/5A/6 none).
- **guide** header at row index 4 → **188** rows. `guide_place_type` COMMUNITY 148 / HIGHWAY 17 / TOURISM 15 / VILLAGE 8. `guide_population` (155 rows) reference only. HIGHWAY/TOURISM kept, tagged, out of community rankings (§2.8).
- **RICT** 535 → **296** NT (row with `state == 'a'` is WA, excluded). `rict_site_type` raw: WP 154 / CP 106 / CPW 23 / WH 13. 258 communities, 38 with >1 site. Codes **not decoded** — UNVERIFIED: `CP` community phone · `WP` Wi-Fi phone · `CPW` both · `WH` Wi-Fi hotspot (confirm vs NIAA docs).

**Village gap (nb 06)** — built & run 2026-09-06 → `village_gap.csv` / `.geojson`, **792 rows**, key `community_id`, **31 columns**. Constants: `GAP_KM=15`, `BUFFER_KM=10`, `GUIDE_MATCH_KM=2`, `RICT_MATCH_KM=2`; all distances straight-line in EPSG:3577.
- Reads only 01/03/04/05 outputs. No population column.
- **towers**: nearest of 430 (1 `is_planning_site` excluded). `km_nearest_tower` median **14.1**, p90 53, max 150; **384 villages > 15 km**. `n_towers_10km` = 0 for **470** villages. Carries `nearest_tower_carriers/networks/spectrum_depth_khz`, `n_towers_10km`, `n_carriers_10km`, `n_networks_10km`.
- **NBN**: `in_nbn_fixed_line` 30, `in_nbn_fixed_wireless` 1 (matches nb 04).
- **MBSP**: `km_nearest_built_mbsp` median ~102 km, `km_nearest_unbuilt_mbsp` median ~219 km, `nearest_unbuilt_mbsp_round` (778 → Round 7, 14 → Round 5).
- **guide**: nearest guide place; `guide_matched_by` ∈ {distance, name, both, neither} = **neither 615, both 161, distance 16, name 0**. Matched → `guide_match_name/km`, `guide_says_covered` (77 True), `guide_proximity_only` (100 True); unmatched → those 4 are NaN.
- **RICT**: `has_rict_public_access` True for **274** villages; `n_rict_sites`, `rict_site_type` (`;`-joined codes). 12 RICT sites have no village within 2 km.
- **`distance_gap_candidate`** = guide does not claim macro/small (unmatched counts as no-claim) AND `km_nearest_tower > 15` → **384 villages**, all Remote/Very Remote. 9 of them also carry `guide_proximity_only=True` (the "covered by proximity" vs >15 km contradiction); 375 are guide-unmatched.
- **`tier`** = stub `<NA>` — **TODO: define T1–T5 after review.**

**STAND** — not read anywhere. Dropped, no unique signal.
