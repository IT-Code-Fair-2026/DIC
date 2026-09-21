# NT Deadzone Explorer — Services Edition

An extension of `DataScienceChallenge/app.py`, adding the item its own README
listed under "Project Status" as not yet done:

> - [ ] Nearest-distance calculations for hospitals, police stations, clinics,
>   and schools.

Same mobile-tower tier logic as the original (unchanged: `GAP_KM = 15`,
`BUFFER_KM = 10`, verified counts **384 / 86 / 221 / 101 = 792**), plus:

- A second KPI row: how many villages have **no school / no medical facility /
  no emergency facility within 10 km** (565 / 588 / 600 of 792).
- Every community's detail card now also shows nearest school, medical, and
  emergency site (distance + name) and how many of each sit within 10 km.
- An optional map layer (sidebar checkbox) plotting the school/medical/
  emergency points themselves alongside the village tier dots.
- Three new sidebar filters: "No school/medical/emergency within 10km".

Deliberately **does not** fold services into the tier — that's a judgement
call for the report, not something to bake into the app silently. The info
card in the sidebar says so.

## Setup and run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open <http://localhost:8501>.

## Files

| File | What |
|---|---|
| `app.py` | The dashboard. |
| `village_gap_with_services.csv` | `village_gap.csv` (792 rows, nb 06) + 12 columns from `Saugat/notebooks/07_services_gap.ipynb`. |
| `sa1_report.csv` | Unchanged — 2021 Census population/income per SA1 (nb 02). |
| `services_sites_combined.csv` | The 606 school/medical/emergency sites drawn on the optional map layer. |
| `.streamlit/config.toml` | Same dark theme as the original app. |
| `requirements.txt` | Same dependencies as the original — no new libraries needed. |

## Verified before delivery

Ran headless (`streamlit run` + a headless-Chromium check), confirmed:
tier counts match the original app's documented 384/86/221/101 exactly;
the two new services KPI tiles compute 565/588/600 correctly; expanding a
community card and toggling the services map layer both work with no
Streamlit error box or JS exception.

## Caveats (also in the in-app footnote)

Services distances are haversine (great-circle) on WGS84, not the projected
`EPSG:3577` method the tower/MBSP columns use — close enough for triage,
slightly less precise. 9 of 273 schools have no coordinate (4 outstation
schools whose address is literally `tba`, 5 more nothing was found for) and
are excluded from the school distance calc, not guessed.
