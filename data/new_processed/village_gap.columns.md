# `village_gap.csv` — column reference

Written by `notebooks/06_village_gap.ipynb` (built 2026-09-07). **792 rows, one per BushTel
village. Key: `community_id` (unique).** Point geometry in the sibling `village_gap.geojson`
(EPSG:4326).

**Reads only** the outputs of notebooks 01 / 03 / 04 / 05 (`villages.geojson`, `towers.csv`,
`nbn_footprint.geojson`, `program_sites.csv`).

## What this table is / isn't

- **Every `km_*` column is a straight-line (great-circle) distance computed in EPSG:3577
  (metres), rounded to 2 dp.** It is *triage* — "is a service plausibly within reach" — and
  **not** a coverage claim, a drive time, a signal-strength prediction, or a service
  guarantee.
- **No population column.** Population is an SA1 fact; it lives on `sa1_report.csv` (nb 02)
  and is joined at SA1 level in nb 07. Do not infer per-village population from anything here.
- A carrier licence is *permission to transmit*, not proof a site is on air.
- `tier` is an unfilled stub (see below).

## Constants used (defined in the notebook)

| name | value | meaning |
|---|---|---|
| `GAP_KM` | 15 | `distance_gap_candidate` distance cutoff — a named triage threshold, **not** a validated coverage radius |
| `BUFFER_KM` | 10 | radius of the disc for the `*_10km` neighbourhood counts |
| `GUIDE_MATCH_KM` | 2 | a coverage-guide place this close is treated as "this village" |
| `RICT_MATCH_KM` | 2 | a RICT site this close is treated as serving the village |

---

## Columns

### Identity & location — pass-through from `villages.csv` (nb 01)

| column | type | null | description |
|---|---|---|---|
| `community_id` | int | 0 | BushTel's stable community id. The key. Not sequential (values up to ~14.2M). |
| `community_name` | string | 0 | BushTel community name. **Not unique** — 2 villages share a name; join on `community_id`. |
| `community_aliases` | string | 0 | Comma-separated alternate names, verbatim from BushTel. May be the literal sentinel `"No aliases recorded with NTG DIPL"` (180 rows) — treated as empty by the guide name match. |
| `community_type` | string | 0 | BushTel category: `Family Outstation` (630), `Major`, `Town Camp`, `Minor`, `Village`, `Town`, `City`. |
| `latitude` / `longitude` | float | 0 | WGS84 (EPSG:4326) point coordinates. |
| `sa1_code` | string | 0 | 11-digit ABS SA1 2021 code the village point falls inside. **Read as string.** 179 distinct. Join key to `sa1_report.csv` in nb 07. |
| `remoteness_name` | string | 0 | ABS Remoteness Area of that SA1: `Very Remote Australia` / `Remote Australia` / `Outer Regional Australia`. |
| `is_remote` | bool | 0 | `True` when `remoteness_name` is Remote or Very Remote; `False` for Outer Regional (NT ≈ greater Darwin). 779 `True`. |

### Nearest carrier tower — from `towers.csv` (nb 03)

Nearest of the **430** carrier handset-band tower rows (the 1 `is_planning_site` placeholder
is excluded from distance work).

| column | type | unit | null | description |
|---|---|---|---|---|
| `km_nearest_tower` | float | km | 0 | Straight-line distance to the nearest tower. median ≈ 14.1, p90 ≈ 53, max ≈ 149.6. |
| `nearest_tower_carriers` | string | — | 0 | `;`-joined licensee **brands** at that nearest tower (e.g. `Optus;TPG;Telstra`). |
| `nearest_tower_networks` | string | — | 0 | Same, collapsed to **physical networks** (Vodafone + Hutchison + TPG → `TPG`). |
| `nearest_tower_spectrum_depth_khz` | float | kHz | 0 | That tower's `spectrum_depth_khz` — summed **distinct** handset-band channel width. A *relative capacity indicator*, not a speed. |

### Towers within 10 km — from `towers.csv` (nb 03)

Count of tower rows whose point is within `BUFFER_KM` (10 km) of the village. `0` for a
village with none.

| column | type | null | description |
|---|---|---|---|
| `n_towers_10km` | int | 0 | Distinct tower sites within 10 km. 0 for **470** villages; max 80 (Darwin). |
| `n_carriers_10km` | int | 0 | Distinct licensee brands across those towers (0–4). |
| `n_networks_10km` | int | 0 | Distinct physical networks across those towers (0–3). The redundancy number. |

### NBN fixed footprint — from `nbn_footprint.geojson` (nb 04)

Point-in-polygon, **not** a distance.

| column | type | null | description |
|---|---|---|---|
| `in_nbn_fixed_line` | bool | 0 | Village point sits inside the dissolved NBN fixed-line footprint. `True` for 30. |
| `in_nbn_fixed_wireless` | bool | 0 | Inside the NBN fixed-wireless footprint. `True` for 1. |

### Mobile Black Spot Program — from `program_sites.csv` `source == "mbsp"` (nb 05)

49 NT MBSP sites split into 41 **built** (`Site_Status == "Complete"`) and 8 **funded but not
built**. Straight-line distance to the nearest of each. With only 8 unbuilt sites these
distances can be very large — **there is no cutoff**; the km value is the qualifier.

| column | type | unit | null | description |
|---|---|---|---|---|
| `km_nearest_built_mbsp` | float | km | 0 | Distance to the nearest **built** MBSP site. median ≈ 102. |
| `km_nearest_unbuilt_mbsp` | float | km | 0 | Distance to the nearest **funded-but-unbuilt** MBSP site. median ≈ 219. |
| `nearest_unbuilt_mbsp_round` | string | — | 0 | Funding round of that nearest unbuilt site: `Round 7` (778 villages) or `Round 5` (14). |

### Coverage-guide read — from `program_sites.csv` `source == "guide"` (nb 05)

The **nearest** guide place to the village. It is a *match* if within `GUIDE_MATCH_KM` **or**
its `SITE NAME` equals the village's `community_name` or one of its `community_aliases`.
When `guide_matched_by == "neither"` (615 villages) the four guide columns below are **NaN**.

| column | type | unit | null | description |
|---|---|---|---|---|
| `guide_match_name` | string | — | 615 | `SITE NAME` of the matched guide place (160 distinct; some matched by >1 village). NaN if unmatched. |
| `guide_match_km` | float | km | 615 | Distance to the matched guide place (≤ 1.98 in practice). NaN if unmatched. |
| `guide_matched_by` | string | — | 0 | How the match was made: `distance` (16), `name` (0), `both` (161), `neither` (615). Always present. |
| `guide_says_covered` | bool¹ | — | 615 | The matched place has `MACRO CELL` **or** `SMALL CELL` = YES. 77 `True`. NaN if unmatched. |
| `guide_proximity_only` | bool¹ | — | 615 | The matched place has `PROXIMITY TO CELL` = YES **and not** macro/small — the guide claims coverage "from a cell elsewhere". 100 `True`. NaN if unmatched. Kept **separate** from the measured `km_nearest_tower` (00b found 10 such places are >15 km from any real tower). |

¹ Written by pandas as `True` / `False` / empty; re-reads as an `object` column, not `bool`. Compare with `== True`.

### RICT public access — from `program_sites.csv` `source == "rict"` (nb 05)

All four RICT `site_type` codes count as public access. A site "serves" the village if within
`RICT_MATCH_KM` (2 km).

| column | type | null | description |
|---|---|---|---|
| `has_rict_public_access` | bool | 0 | ≥1 RICT site within 2 km. `True` for 274 villages. |
| `n_rict_sites` | int | 0 | How many RICT sites within 2 km (0–6). |
| `rict_site_type` | string | 518 | `;`-joined **distinct** raw codes of those sites (e.g. `CP;WP`). NaN when `n_rict_sites == 0`. Codes **not decoded** — UNVERIFIED: `CP` community phone · `WP` Wi-Fi phone · `CPW` both · `WH` Wi-Fi hotspot (confirm against NIAA program docs). |

### Derived

| column | type | null | description |
|---|---|---|---|
| `distance_gap_candidate` | bool | 0 | `True` when the guide does **not** claim macro/small coverage for this village (unmatched counts as "no claim") **and** `km_nearest_tower > GAP_KM` (15). **384 villages**, all `is_remote`. A triage shortlist, **not** a verdict — proximity claims are ignored on purpose and there is no population in it. (Renamed from the old `likely_gap`.) |
| `tier` | (empty) | 792 | **Unfilled stub.** T1–T5 to be defined after review of this table; reads back as an all-NaN float column until then. |
