# NT Deadzone Explorer — Services Edition

An extension of `DataScienceChallenge/app.py`, adding the item its own README
listed under "Project Status" as not yet done:

> - [ ] Nearest-distance calculations for hospitals, police stations, clinics,
>   and schools.

Same mobile-tower tier logic as the original (unchanged: `GAP_KM = 15`,
`BUFFER_KM = 10`, verified counts **384 / 86 / 221 / 101 = 792**), plus:

- A second KPI row: how many villages have **no school / no medical facility /
  no emergency facility within 10 km** (547 / 588 / 600 of 792).
- Every community's detail card now also shows nearest school, medical, and
  emergency site (distance + name) and how many of each sit within 10 km.
- An optional map layer (sidebar checkbox) plotting the school/medical/
  emergency points themselves alongside the village tier dots.
- Three new sidebar filters: "No school/medical/emergency within 10km".

Deliberately **does not** fold services into the tier — that's a judgement
call for the report, not something to bake into the app silently. The info
card in the sidebar says so.

## Setup and run

From the repo root (see the root `README.md` for the full setup):

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

Then open <http://localhost:8501>. Launch from the repo root so Streamlit picks up the
theme in `.streamlit/config.toml`.

## Files

| File | What |
|---|---|
| `app.py` | The dashboard. |
| `assets/` | Optional flags/artwork for the cultural theme (see `assets/README.md`). |

The app keeps **no data of its own**. It reads the pipeline's outputs from `data/processed/`:

| File | Written by |
|---|---|
| `village_gap_with_services.csv` | nb 11: `village_gap.csv` (nb 06) + 12 service columns |
| `sa1_report.csv` | nb 02: 2021 Census population/income per SA1 |
| `services_sites.csv` | nb 09: the 605 school/medical/emergency sites for the optional map layer |
| `towers.csv` | nb 03 |
| `small_cells.csv` | nb 10: the coverage guide's 24 small-cell sites |

## What you should see

Tier counts **384 / 86 / 221 / 101** (= 792 communities) and services KPI tiles of
**547 / 588 / 600** villages with no school / medical / emergency site within 10 km.

## Caveats (also in the in-app footnote)

Services distances are haversine (great-circle) on WGS84, not the projected
`EPSG:3577` method the tower/MBSP columns use — close enough for triage,
slightly less precise. School coordinates are locality-level (all schools in
one town share a point). 1 of 273 schools (Nawarddeken Academy Kunmayali,
address `tba`) has no coordinate and is excluded from the school distance
calc, not guessed.
