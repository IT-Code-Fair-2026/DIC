# Agent guidance — NT Connectivity & Services Gap

Read this before touching anything in this repo. It's a data pipeline for a CDU IT Code Fair
submission (deadline 2026-09-30) — 11 numbered notebooks turn public NT datasets into one
792-row village table, plus a Streamlit dashboard (`app/app.py`) that reads the result.

## Read these first, in this order

1. `docs/PROJECT_CONTEXT.md` — why decisions were made, the challenge brief, standing rules
   (population unit, distance rules, what was dropped on purpose and why).
2. `README.md` — quick start, pipeline table, ground rules.
3. `docs/CODE_ANALYSIS.md` — what every notebook/script actually does at the code level
   (fills the gap between the docs below and the raw `.ipynb` files).
4. `docs/data_use_check.md` — line-by-line audit of notebooks `00a`–`06`.
5. `docs/SERVICES_LAYER.md` — the schools/medical/emergency layer (notebooks `07`–`11`).
6. `data/README.md`, `docs/DATASET_INVENTORY.md`, `docs/DATA_DICTIONARY.md` — what's on disk,
   used/unused, column meanings, provenance/licence per file.
7. `report/README.md` and `hypothesis_proof_notebooks/README.md` — the submission report
   generator and the formal statistical tests behind its three headline hypotheses.

Don't redo the audits these already contain. If a question is "does notebook X read file Y,"
check `docs/data_use_check.md` or `docs/CODE_ANALYSIS.md` before opening the notebook JSON
yourself.

## Ground rules (binding, from `README.md` / `docs/PROJECT_CONTEXT.md`)

1. **`data/raw/` and `data/external/` are read-only.** Never edit by hand. If a source
   changes, record where it came from in `data/README.md`.
2. **Only notebooks write to `data/processed/`.** Nothing else — including `app/app.py` —
   keeps its own copy or writes there.
3. **Notebooks are the source of truth**, numbered in run order (`00a`, `00b`, `01`…`11`).
   `run_pipeline.py` globs and sorts by filename — a new step is a new numbered notebook, no
   separate manifest to update.
4. **BushTel `community_id` is the spine.** Every people-side fact hangs off a village; every
   infrastructure fact is measured *from* a village.
5. **Census 2021 is the only real population figure, and it only exists at SA1 level.**
   BushTel `population_count` / the coverage guide's `POPULATION` are reference-only, never
   summed as population. A census figure is never split across the villages inside an SA1.
6. **Distances are triage, not coverage guarantees.** Straight-line, no roads/terrain/signal.
   Connectivity notebooks (`03`/`06`) project to `EPSG:3577` first; the services notebook
   (`11`) and the app's live recomputations use haversine on WGS84 instead — both are
   documented as "close enough for triage," not as an inconsistency to fix.
7. New dependency → add it to `requirements.txt` with an exact pinned version.
8. Don't assume — inspect the file, or check `docs/data_use_check.md` / `docs/CODE_ANALYSIS.md`
   first, or ask.

## Things that will bite you if you don't know them

- **`data-main/` is not part of the pipeline.** It's an untracked, orphaned folder (predates
  the 2026-09-27 repo restructure) containing 3 standalone EDA notebooks and — importantly —
  the **raw, untrimmed versions of the services CSVs** that `docs/SERVICES_LAYER.md` and
  `data/README.md` both describe as "not in the repo." See `docs/CODE_ANALYSIS.md` §5 for the
  full comparison. Do not wire its notebooks into the numbered pipeline. Its 3 CSVs
  (`medical_facilities_NT.csv`, `emergency_facilities_NORTHERN_TERRITORY.csv`,
  `School_List_Public_2026_09_12_11_12_43.csv`) are confirmed matches for the documented gap
  at `data/external/services/_raw/` (currently empty, `.gitkeep` only) — moving them there
  would close that gap, but treat it as a repo-structure change to confirm with the user
  first, not something to do silently.
- **Every notebook re-runs from scratch via `run_pipeline.py`, and it overwrites the `.ipynb`
  file in place** (refreshed outputs, kernel metadata) even on failure, so the traceback is
  preserved. If you hand-edit a notebook's cells, re-run it (`python run_pipeline.py --only
  NN`) rather than trusting stale stored output — `notebooks/11_services_gap.ipynb`'s current
  stored output has a different collaborator's absolute path in it (`C:\Users\Aseem\...`),
  meaning it hasn't been re-executed in this checkout; the numbers are presumably still right
  since inputs haven't changed, but don't cite that path string.
- **Git LFS is required.** `.gitattributes` LFS-tracks every `.csv`, `.xlsx`, shapefile
  component, `.geojson`, `.kml`, `.pdf` — there is no `.gitignore` for data, everything real is
  either tracked (small) or LFS-tracked (large) or trimmed down with a `.gitkeep` placeholder
  where a large source was removed as unused (see `docs/DATASET_INVENTORY.md` for exactly
  what was removed and why, and the re-download URL in `data/README.md` if it's needed again).
- **The ACMA licence register (`data/external/acma_rrl/`) is not CC-BY** — usage conditions
  live in `external/acma_rrl/LICENCE.TXT`. It's also a daily-regenerated extract, so the
  3,771 NT sites / 461 handset-band sites notebook `03` reports are a snapshot, not a stable
  count.
- **The app's tier classification is tower-only, by design.** `app/app.py`'s `classify()`
  uses only `distance_gap_candidate` / `n_towers_10km` / `n_networks_10km` from notebook `06`.
  Services distances (school/medical/emergency, from notebook `11`) are shown everywhere in
  the UI but deliberately never move a village between tiers — don't "fix" this by folding
  them in; it's a stated judgement call left for the report, not the app.
- **Small cells (`notebooks/10_small_cells.ipynb` → `small_cells.csv`) are not used by
  notebook `11`'s gap calculation at all.** They only feed `app/app.py`'s tower/cell-type
  labelling (macro vs. small-cell range rings). Don't assume small-cell coverage affects any
  gap number in `village_gap_with_services.csv`.
- **`app/app.py` recomputes some distances live** (haversine, in `nearby_for_id()` /
  `attach_providers()`) rather than only reading notebook-precomputed columns — these can
  differ from the notebook's stored values by a few hundred metres. That's documented in the
  app's own docstrings as expected, not a bug to reconcile.
- **`hypothesis_proof_notebooks/` and `report/` are not part of the `notebooks/00a`–`11`
  pipeline** — they're downstream consumers of `data/processed/`, not producers of it.
  `run_pipeline.py`'s glob only sees `notebooks/*.ipynb`, so these two folders are correctly
  never picked up by it; don't add them there. If `data/processed/` changes, re-run the
  hypothesis notebooks and `report/make_charts.py` by hand (see each folder's README) — their
  numbers are computed at build time, not live.

## Working in this repo

- Python 3.12, exact versions pinned in `requirements.txt`. Install with
  `pip install -r requirements.txt`.
- Rebuild everything: `python run_pipeline.py` (a few minutes; the ACMA register read in
  notebook `03` is the slow step, hence the 1800s per-cell timeout in `run_pipeline.py`).
  `--from NN` / `--only NN` for partial runs.
- Run the dashboard: `streamlit run app/app.py` from the repo root (so `.streamlit/config.toml`
  is picked up).
- After a full rebuild, `git status` should show no changes under `data/processed/` — if it
  does, something upstream changed and the committed outputs are stale.
- Every notebook does its own root-detection / `os.chdir` so it works whether launched from
  the repo root or from inside `notebooks/` — don't hardcode paths when adding a new step;
  follow the existing pattern.
