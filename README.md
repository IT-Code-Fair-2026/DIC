# NT Connectivity & Services Gap

Which Northern Territory communities are far from mobile coverage, NBN, schools,
medical care and emergency services? This repo turns public datasets into one
village-level table (792 BushTel communities) and a Streamlit dashboard to explore it.

Everything in `data/processed/` is produced by the notebooks, so anyone can rebuild it
from the inputs with one command and get the same result.

## Quick start

```bash
# 1. Get the code AND the data (large files are stored with Git LFS)
git lfs install
git clone <repo-url> DIC
cd DIC

# 2. Python 3.12 environment with the exact package versions
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

# 3. Rebuild every output from the raw data (a few minutes)
python run_pipeline.py

# 4. Open the dashboard
streamlit run app/app.py        # then go to http://localhost:8501
```

`data/processed/` is committed, so you can skip step 3 to just look at the app.
`python run_pipeline.py --from 07` reruns from one notebook onward, and `--only 08` runs a single notebook.

## Layout

```
DIC/
├── README.md            this file
├── requirements.txt     pinned package versions
├── run_pipeline.py      runs notebooks/ in order
├── .streamlit/          dashboard theme (Streamlit reads it from the folder you launch in)
├── app/                 Streamlit dashboard (reads data/processed/ directly)
├── notebooks/           the pipeline, numbered in run order
├── data/
│   ├── raw/             supplied by CDU for the challenge: read-only
│   ├── external/        downloaded by us from public sources: read-only
│   └── processed/       written by the notebooks, and ONLY by the notebooks
├── docs/                data dictionary, dataset inventory, project context, EDA plots
├── report/              generates the submission PDF report straight from data/processed/
└── hypothesis_proof_notebooks/   formal statistical tests of the report's 3 hypotheses
```

## Pipeline

| # | Notebook | Reads | Writes (`data/processed/` unless noted) |
|---|---|---|---|
| 00a | `eda_population_census` | Census GCP, ABS boundaries, BushTel | plots in `docs/eda/` (exploration only) |
| 00b | `eda_connectivity` | ACMA, NBN, MBSP, coverage guide, RICT | plots in `docs/eda/` (exploration only) |
| 01 | `villages` | BushTel, ABS SA1 + remoteness | `villages.csv/.geojson` |
| 02 | `sa1_report` | Census GCP, ABS SA1, `villages.csv` | `sa1_report.csv/.geojson`, `area_with_population_lessthan_5.csv` |
| 03 | `towers` | ACMA radio licence register | `towers.csv/.geojson` |
| 04 | `nbn_footprint` | NBN fixed-line + wireless footprints | `nbn_footprint.geojson` |
| 05 | `program_sites` | MBSP, coverage guide, RICT | `program_sites.csv/.geojson` |
| 06 | `village_gap` | outputs of 01–05 | `village_gap.csv/.geojson` (+ `village_gap.columns.md`) |
| 07 | `services_clean_facilities` | `external/services/trimmed/` | `medical_services.csv`, `emergency_services.csv` |
| 08 | `services_geocode_schools` | `external/services/trimmed/`, 07, BushTel | `school_services.csv` |
| 09 | `services_combine_sites` | 07, 08 | `services_sites.csv` |
| 10 | `small_cells` | `raw/nt_mobile_coverage/` small-cell list | `small_cells.csv` |
| 11 | `services_gap` | `village_gap.csv`, `services_sites.csv` | `village_gap_with_services.csv`, `village_services_gap.csv` |

The dashboard reads `village_gap_with_services.csv`, `sa1_report.csv`, `services_sites.csv`,
`towers.csv` and `small_cells.csv`.

## Checking you got the same result

After `python run_pipeline.py`, these numbers should match (printed in the notebooks):

- 792 villages; tower tiers **384 / 86 / 221 / 101** (nb 06)
- 605 service sites, 604 with coordinates (272 of 273 schools geocoded) (nb 09)
- villages with no school / medical / emergency site within 10 km: **547 / 588 / 600** (nb 11)

`git status` should also show no changes under `data/processed/`.

## Ground rules

1. `data/raw/` and `data/external/` are never edited by hand. If an input changes, record where it came from in `data/README.md`.
2. Only notebooks write to `data/processed/`. Nothing else (the app included) keeps its own copy.
3. New dependency? Add it to `requirements.txt` with an exact version.
4. New step? Add a notebook with the next number. `run_pipeline.py` picks it up automatically.

## Known limitations

- **Services inputs are trimmed snapshots.** The original school, medical and emergency
  downloads aren't in the repo. Notebooks 07–08 start from the trimmed copies in
  `data/external/services/trimmed/`. See `docs/SERVICES_LAYER.md`.
- Distances are straight-line triage numbers, not coverage guarantees. See `docs/PROJECT_CONTEXT.md`.

## More documentation

| File | What |
|---|---|
| `data/README.md` | every input file: source, licence, CRS |
| `docs/DATA_DICTIONARY.md` | column-level descriptions |
| `docs/DATASET_INVENTORY.md` | which files are used by which notebook |
| `docs/PROJECT_CONTEXT.md` | goals, decisions and rules of the analysis |
| `docs/SERVICES_LAYER.md` | how the school / medical / emergency layer was built |
| `app/README.md` | what the dashboard shows |
| `report/README.md` | how to (re)build the submission PDF report from `data/processed/` |
| `hypothesis_proof_notebooks/README.md` | formal statistical tests of the report's 3 hypotheses, and how the greedy algorithm works |
