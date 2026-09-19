# NT Deadzone Explorer

An interactive Streamlit dashboard for the CDU IT Code Fair Data & Innovation
Challenge 2026 (theme: Remote Connectivity). It classifies all 792 BushTel
communities in the Northern Territory into four connectivity-priority
categories using **only** real, documented thresholds and raw counts already
present in the source data — no invented scoring or weights.

Built on top of [Aseem's connectivity research](https://github.com/IT-Code-Fair-2026/DIC)
(`village_gap.csv` from `notebooks/06_village_gap.ipynb`, `sa1_report.csv`
from `notebooks/02_sa1_report.ipynb`).

## Setup & run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Needs `village_gap.csv` and `sa1_report.csv` in the same folder as `app.py`
(both included in this folder). Opens at `http://localhost:8501`.

## What's inside

- **`app.py`** — the whole app: data loading, classification, sidebar
  filters, an interactive map, a scrollable points list, and a lookup panel
  for any single community.
- **`village_gap.csv`** (792 rows, key `community_id`) — Aseem's fully
  denormalized output: one row per BushTel community with every
  infrastructure fact already measured (nearest tower, towers/networks
  within 10 km, NBN footprint, nearest MBSP site, coverage-guide read, RICT
  access).
- **`sa1_report.csv`** (645 rows, key `sa1_code`) — 2021 Census population
  and income per SA1, joined onto each village by `sa1_code`.
- **`.streamlit/config.toml`** — dark theme (background, accent, text
  colors) applied app-wide.
- `folium` + `streamlit-folium` for a real interactive map (OpenStreetMap
  tiles, CSS-inverted for a dark basemap — no API key, no cost).

## How communities are classified

Four categories, checked in this order, using only two named constants from
the source notebook (`GAP_KM = 15`, `BUFFER_KM = 10`):

1. **Beyond gap threshold** — `distance_gap_candidate == True`: more than
   15 km from the nearest tower, with no coverage-guide claim of service.
2. **Single point of failure** — within 15 km, but zero towers fall inside
   the 10 km buffer (`n_towers_10km == 0`) — relies on one tower with no
   backup nearby.
3. **Single network only** — towers exist within 10 km, but only one
   independent network (`n_networks_10km <= 1`) — no redundancy.
4. **Multiple networks** — two or more independent networks within 10 km —
   genuine redundancy.

Verified counts (checked against Aseem's own notebook summary stats, exact
match): **384 / 86 / 221 / 101**, sums to 792.

This mirrors two of the three factors named in the Mobile Black Spot
Program's own Value for Money assessment (service-gap severity, network
redundancy). The third — premises/population benefited — is shown per
community from the 2021 Census but **deliberately does not change the
category**: it's an SA1-level figure shared across every village in that
SA1, not a per-village count, so using it to move a specific village between
tiers would overstate its precision.

## Known caveats (surfaced in the UI, not hidden)

- **"No guide claim" mostly means no data, not confirmed non-coverage.**
  78% of villages (615/792) have no matching row in the NT coverage guide at
  all — that's counted as "no claim" by convention, not verified absence of
  service.
- **Tower universe is ACMA-licensed sites only.** 5 known built MBSP sites
  have no matching ACMA registration, so `km_nearest_tower` slightly
  undercounts real infrastructure in a few spots (Aseem's own open issue).
- **RICT site-type codes are shown raw, undecoded** (`WP`, `CP`, `CPW`,
  `WH`) — their meanings are unverified against NIAA program docs, so the
  app doesn't guess at them.
- All distances are straight-line (EPSG:3577), not drive time — triage,
  not a coverage guarantee.

## Data provenance & what's still not used

See [`docs/erd.svg`](docs/erd.svg) for the full entity relationship diagram.
In short: `village_gap.csv` is already a denormalized join of four upstream
sources (villages, towers, NBN footprint, program sites) — this app reads
only the two final outputs (`village_gap.csv`, `sa1_report.csv`), not the
upstream `towers.csv` / `program_sites.csv` directly.

Not yet used, but available in Aseem's repo (`data/external/services/_raw/`):
hospital (8), police (66), and GP/clinic (128) point locations from
Geoscience Australia, plus a 217-row school list from ACARA. Computing
nearest-distance from each village to these (same nearest-neighbor pattern
already used for towers) would unlock the emergency-services angle the
challenge brief calls out — not yet implemented here.

## Status

- [x] Real Streamlit dashboard: filters, interactive map, points list,
      community lookup — all backed by real thresholds, no invented scoring.
- [x] Population joined in from `sa1_report.csv` (was previously "pending").
- [x] Map click jumps to and auto-expands the matching card.
- [x] Dark, dashboard-styled UI.
- [ ] Hospital/police/GP/school nearest-distance columns.
- [ ] `tier` (T1–T5) is still Aseem's unfilled stub — this app's 4-category
      scheme is a separate classification built from the MBSP guideline
      factors, not a replacement for his eventual tier definition.
