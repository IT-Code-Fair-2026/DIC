NT Deadzone Explorer
An interactive Streamlit dashboard built for the CDU IT Code Fair Data & Innovation Challenge 2026 (Remote Connectivity theme). It organizes all 792 BushTel communities in the Northern Territory into four connectivity priorities using real, documented thresholds and raw counts straight from the source data—no made-up scores or artificial weighting.

This project builds directly on Aseem's connectivity research, using village_gap.csv (from notebooks/06_village_gap.ipynb) and sa1_report.csv (from notebooks/02_sa1_report.ipynb).

Setup & Run
Make sure village_gap.csv and sa1_report.csv are in the same folder as app.py (both are included in the repository).

Bash
pip install -r requirements.txt
streamlit run app.py
Once running, open your browser to http://localhost:8501.

What's Inside
app.py: The main application. Handles data loading, priority classification, sidebar filtering, an interactive map, a scrollable list of points, and a deep-dive lookup for individual communities.

village_gap.csv (792 rows, key: community_id): Aseem's denormalized output dataset containing infrastructure stats per BushTel community (nearest tower distance, towers/networks within 10 km, NBN footprint, nearest MBSP site, coverage guide reads, and RICT access).

sa1_report.csv (645 rows, key: sa1_code): 2021 Census population and income figures by SA1, mapped onto each village via sa1_code.

.streamlit/config.toml: Configures a clean, app-wide dark theme.

Map integration: Uses folium and streamlit-folium with CSS-inverted OpenStreetMap tiles to deliver a dark basemap without requiring external API keys.

Community Classification
Communities are evaluated against two core constants from the research notebook (GAP_KM = 15, BUFFER_KM = 10) in the following order:

Beyond gap threshold: distance_gap_candidate == True (located over 15 km from the nearest tower with no coverage-guide claim of service).

Single point of failure: Located within 15 km, but has zero towers within the 10 km buffer (n_towers_10km == 0), leaving the community reliant on a single distant tower.

Single network only: Towers are present within 10 km, but belong to only one provider (n_networks_10km <= 1), meaning there's no network redundancy.

Multiple networks: Two or more independent networks operate within 10 km, offering true coverage redundancy.

Verified counts across categories: 384 / 86 / 221 / 101 (Total: 792, matching the reference notebook summary exactly).

This setup mirrors key criteria from the Mobile Black Spot Program's Value for Money assessment (service-gap severity and redundancy). While 2021 Census population data is displayed for context, it doesn't shift a village between categories—SA1 metrics cover broader areas, so using them to reclassify individual villages would introduce misleading precision.

Key Caveats
Coverage claims: About 78% of villages (615/792) have no entry in the NT coverage guide. These are categorized as "no claim" by convention rather than verified lack of coverage.

Tower dataset: Relies exclusively on ACMA-licensed sites. Five known operational MBSP sites lack ACMA registration, meaning km_nearest_tower slightly overstates distance in a few locations.

RICT site codes: Codes like WP, CP, CPW, and WH are presented as raw values because their definitions aren't fully verified against NIAA documentation.

Distances: All measurements are straight-line calculations (EPSG:3577), designed for initial triage rather than detailed terrain coverage guarantees.

Data Provenance & Future Additions
For a complete breakdown of data relationships, check out docs/erd.svg.

The app reads village_gap.csv and sa1_report.csv directly. While village_gap.csv combines several raw inputs (villages, towers, NBN footprint, and program sites), additional raw point data is available in the source repository (data/external/services/_raw/), including:

Hospitals (8)

Police stations (66)

GP clinics (128)

Schools (217 via ACARA)

Calculating nearest-facility distances for these points would add valuable emergency-services context to the dashboard.

Project Status
[x] Streamlit dashboard with working filters, interactive map, community points list, and lookup tool.

[x] Joined population data from sa1_report.csv.

[x] Interactive map clicks sync with and expand the corresponding community card.

[x] Dark-mode styling across the UI.

[ ] Nearest-distance calculations for hospitals, police stations, clinics, and schools.

[ ] Integration of Aseem's planned tier (T1–T5) classification once defined.