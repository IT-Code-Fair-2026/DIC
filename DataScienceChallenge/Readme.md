# NT Deadzone Explorer

An interactive Streamlit dashboard built for the **CDU IT Code Fair Data & Innovation Challenge 2026**, under the Remote Connectivity theme.

The dashboard organizes all 792 BushTel communities in the Northern Territory into four connectivity priorities using documented thresholds and raw counts from the source data. It does not use invented scores or artificial weighting.

This project builds on Aseem's connectivity research and uses:

- `village_gap.csv`, generated from `notebooks/06_village_gap.ipynb`
- `sa1_report.csv`, generated from `notebooks/02_sa1_report.ipynb`

## Setup and Run

Make sure `village_gap.csv` and `sa1_report.csv` are in the same folder as `app.py`. Both files are included in this repository.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Once the app is running, open [http://localhost:8501](http://localhost:8501) in your browser.

## Project Contents

| File | Description |
| --- | --- |
| `app.py` | Main Streamlit application. Loads data, classifies communities, provides sidebar filters, renders the interactive map, lists community points, and supports individual community lookups. |
| `village_gap.csv` | 792-row denormalized dataset keyed by `community_id`. Contains infrastructure statistics for each BushTel community, including nearest tower distance, towers and networks within 10 km, NBN footprint, nearest MBSP site, coverage-guide results, and RICT access. |
| `sa1_report.csv` | 645-row dataset keyed by `sa1_code`, containing 2021 Census population and income figures mapped onto villages. |
| `.streamlit/config.toml` | App-wide dark theme configuration. |
| `requirements.txt` | Python dependencies required to run the dashboard. |

The map uses `folium` and `streamlit-folium` with CSS-inverted OpenStreetMap tiles, so it does not require an external map API key.

## Community Classification

Communities are evaluated against two core constants from the research notebook:

- `GAP_KM = 15`
- `BUFFER_KM = 10`

Classification is applied in this order:

| Priority | Rule |
| --- | --- |
| **Beyond gap threshold** | `distance_gap_candidate == True`: more than 15 km from the nearest tower with no coverage-guide claim of service. |
| **Single point of failure** | Within 15 km, but `n_towers_10km == 0`; the community has no tower within the 10 km buffer. |
| **Single network only** | Towers are present within 10 km, but `n_networks_10km <= 1`; there is no network redundancy. |
| **Multiple networks** | Two or more independent networks operate within 10 km, providing coverage redundancy. |

The verified category counts are **384 / 86 / 221 / 101**, for a total of **792 communities**. These match the reference notebook summary.

This approach mirrors key criteria from the Mobile Black Spot Program's Value for Money assessment: service-gap severity and network redundancy. The 2021 Census population data is displayed for context, but does not change a community's category. SA1 metrics cover broader areas, so using them to reclassify individual villages would introduce misleading precision.

## Key Caveats

- **Coverage claims:** About 78% of villages (615/792) have no entry in the NT coverage guide. These are categorized as "no claim" by convention, not as verified lack of coverage.
- **Tower dataset:** The dashboard relies exclusively on ACMA-licensed sites. Five known operational MBSP sites lack ACMA registration, so `km_nearest_tower` slightly overstates distance in a few locations.
- **RICT site codes:** Codes such as `WP`, `CP`, `CPW`, and `WH` are shown as raw values because their definitions have not been fully verified against NIAA documentation.
- **Distances:** All measurements are straight-line calculations using EPSG:3577. They are intended for initial triage, not detailed terrain or coverage guarantees.

## Data Provenance and Future Additions

The app reads `village_gap.csv` and `sa1_report.csv` directly. While `village_gap.csv` combines several raw inputs, including villages, towers, NBN footprint, and program sites, the source repository also contains additional raw point data in `data/external/services/_raw/`:

- Hospitals: 8
- Police stations: 66
- GP clinics: 128
- Schools: 217 via ACARA

Calculating nearest-facility distances for these points would add valuable emergency-services context to the dashboard.

## Project Status

- [x] Streamlit dashboard with working filters, interactive map, community points list, and lookup tool
- [x] Population data joined from `sa1_report.csv`
- [x] Map clicks synchronized with the corresponding expanded community card
- [x] Dark-mode styling across the UI
- [ ] Nearest-distance calculations for hospitals, police stations, clinics, and schools
- [ ] Integration of Aseem's planned T1-T5 classification once defined