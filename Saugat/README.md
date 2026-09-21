# Saugat — services layer (schools / medical / emergency)

Adds the "services" arm of the pipeline that `PROJECT_CONTEXT.md` §9 planned but never
built (`schools / GA police / hosp / GP → 05_services`). Full writeup of how this was
derived and why is in the project's `SERVICES_BRIDGE_NOTES.md`; this README is the short
version for anyone opening this folder in the repo.

## Contents

```
Saugat/
├── services/                        raw-to-trimmed input layer
│   ├── school_services.csv          273 NT DoE schools, geocoded (264/273, 96.7%)
│   ├── medical_services.csv         181 GP/pharmacy/hospital facilities (GA/NHSD)
│   ├── emergency_services.csv       152 police/fire/SES/ambulance facilities (GA/NHSD)
│   ├── services_sites_combined.csv  all three concatenated, program_sites.csv-shaped
│   ├── geocode_schools.py           offline locality geocoder + manual web overrides
│   └── build_trimmed_csvs.py        builds the four CSVs above from the raw data-main files
├── notebooks/
│   └── 07_services_gap.ipynb        real run against data/new_processed/village_gap.csv:
│                                     adds km_nearest_school/medical/emergency,
│                                     nearest_*_name/type, n_schools/medical/emergency_10km
├── data/
│   ├── village_gap_with_services.csv   village_gap.csv (792 rows) + the 12 new columns
│   └── village_services_gap.csv        compact version: just community_id + the new columns
└── app/                              Streamlit dashboard, extends DataScienceChallenge/app.py
    ├── app.py                        same tower tiers + a services KPI row, per-community
    │                                  school/medical/emergency stats, optional map overlay
    ├── requirements.txt, README.md, .streamlit/config.toml
    └── village_gap_with_services.csv, sa1_report.csv, services_sites_combined.csv  (data copies)
```

Run the app: `cd Saugat/app && pip install -r requirements.txt && streamlit run app.py`.
Already smoke-tested headless — tier counts match the original app's documented 384/86/221/101
exactly, no runtime errors. See `Saugat/app/README.md` for what's new in it.

## Headline numbers (from the real run against your actual `village_gap.csv`)

- `km_nearest_school`: median 26.8 km, p90 80.1 km, max 244.8 km — 565/792 villages have
  **no school within 10 km**.
- `km_nearest_medical`: median 30.2 km, p90 100.4 km, max 286.9 km — 588/792 have none within
  10 km.
- `km_nearest_emergency`: median 30.9 km, p90 88.4 km, max 244.9 km — 600/792 have none within
  10 km.
- Of the 384 villages nb 06 already flags `distance_gap_candidate` (mobile tower gap), the
  median distance to the nearest school/medical/emergency site is 42.7 / 46.2 / 47.7 km —
  the mobile gap and the services gap concentrate in the same places.
- Only 161/792 villages (20%) have a school **and** a medical facility **and** an emergency
  facility all within 10 km.

## Known limitations — read before quoting these numbers in the report

- 9 schools (4 outstation schools with a literal `tba` address, 5 more nothing was found for)
  have no coordinate and are excluded from every school distance calc — not biased, just
  absent.
- Distances here are haversine (great-circle) on WGS84, not the projected-CRS (`EPSG:3577`)
  method nb 03/06 use for towers/MBSP — close enough for triage, slightly less precise.
- `nearest_*_type` means something different per source (school stage / NHSD service type /
  emergency facility class) — don't compare it across sources.
- No population weighting anywhere here, same rule as the rest of the pipeline: population
  lives on `sa1_report.csv` at SA1 level, never inferred from a village-level distance table.
