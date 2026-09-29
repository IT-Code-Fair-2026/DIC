# Services layer (schools / medical / emergency)

Adds a "services" arm to the pipeline: for each of the 792 communities, how far is the
nearest school, medical facility and emergency facility, and how many sit within 10 km.
Originally built in a separate `Saugat/` folder, it is now notebooks 07–11 of the main pipeline.

## Files

```
data/external/services/trimmed/          inputs (read-only)
├── medical_facilities_trimmed.csv       GA / NHSD medical facilities, NT (181)
├── emergency_facilities_trimmed.csv     GA emergency facilities, NT (152)
└── school_list_trimmed.csv              NT Dept of Education school list (273, no coordinates)

notebooks/
├── 07_services_clean_facilities.ipynb   fix labels/agencies, dedupe, flag mislabelled suburbs
├── 08_services_geocode_schools.ipynb    locality geocoder for schools + cited manual coordinates
├── 09_services_combine_sites.ipynb      one site list with consistent columns
├── 10_small_cells.ipynb                 small-cell sites from the coverage guide (used by the app)
└── 11_services_gap.ipynb                per-village nearest distance + 10 km counts

data/processed/
├── medical_services.csv, emergency_services.csv, school_services.csv
├── services_sites.csv                   all 605 sites (app map layer, nb 11 input)
├── small_cells.csv
├── village_gap_with_services.csv        village_gap.csv + 12 service columns (the app's main table)
└── village_services_gap.csv             compact: community_id + the 12 service columns
```

## About the inputs

The trimmed CSVs are the original raw extracts (`medical_facilities_NT.csv`,
`emergency_facilities_NORTHERN_TERRITORY.csv`, `School_List_Public_2026_09_12_11_12_43.csv`)
cut down to the columns the pipeline uses. The raw extracts themselves are not in the repo.
If they're recovered, put them in `data/external/services/_raw/` and point nb 07/08 at them.

## Headline numbers (nb 11)

- `km_nearest_school`: median 22.4 km, p90 79.4 km, max 244.8 km. **547/792** villages have no school within 10 km.
- `km_nearest_medical`: median 30.2 km, p90 100.4 km, max 286.9 km. **588/792** have none within 10 km.
- `km_nearest_emergency`: median 30.9 km, p90 88.4 km, max 244.9 km. **600/792** have none within 10 km.
- For the 384 `distance_gap_candidate` villages (mobile gap, nb 06), median distance to the nearest
  school / medical / emergency site is 39.2 / 46.2 / 47.7 km.
- Only 162/792 villages have a school **and** a medical **and** an emergency site within 10 km.

## Known limitations (read before quoting these numbers)

- **Schools are geocoded to their locality, not their street address.** Every school in a town
  shares that town's point. `geocode_precision` in `services_sites.csv` says whether a row is
  suburb-, community- or region-level. 1 school (Nawarddeken Academy Kunmayali, address `tba`)
  has no coordinate and is excluded.
- Distances are haversine (great-circle) on WGS84, not the projected-CRS (`EPSG:3577`) method
  nb 03/06 use for towers/MBSP. That's close enough for triage and slightly less precise.
- `type` / `nearest_*_type` means something different per source (school stage, NHSD service
  type, emergency facility class). Don't compare it across sources.
- No population weighting: population lives on `sa1_report.csv` at SA1 level, as in the rest
  of the pipeline.
