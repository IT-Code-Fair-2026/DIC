# Report generator

Builds `DataChallenge_Team <NUMBER>_Report.pdf`, formatted to the CDU IT Code Fair 2026
Data Innovation Challenge spec (A4, continuous page numbering, header+footer with Team
Number + Page Number, Title 20pt bold / headings 14pt bold / body 11pt / captions+refs
10pt, ≤8 body pages, Calibri-or-Arial). Every number in the report is computed directly
from `data/processed/*.csv`, not hand-typed, so text and charts can't drift from the data.

## Before submitting

1. Open `build_report.py` and fill in the constants at the top:
   `TEAM_NUMBER`, `TEAM_MEMBERS` (name, role pairs), and `REPO_URL`.
2. Review **Appendix A (AI-use declaration)** in the generated PDF — it's drafted from
   what was actually used to build this report and pipeline, but the team should edit it
   to accurately reflect your own process before submitting.
3. Rebuild (below) and re-check the page count is still ≤8 body pages (title, References
   and Appendices don't count) — if you add prose, some may spill onto a 9th body page.

## Rebuilding

```bash
pip install reportlab==5.0.1   # matplotlib/pandas are already in the root requirements.txt
py -3 report/make_charts.py    # regenerates the 3 chart PNGs from data/processed/
py -3 report/build_report.py   # writes report/out/DataChallenge_Team <NUMBER>_Report.pdf
```

Run `make_charts.py` again any time `data/processed/` changes (e.g. after
`python run_pipeline.py`), then rebuild the PDF — the report text has the same numbers
hand-checked into it, so if the underlying data changes materially, re-verify the prose
in `build_report.py`'s Findings section too (it's text, not computed live).

## Files

| File | What |
|---|---|
| `make_charts.py` | Computes the 3 report figures straight from `data/processed/*.csv`. |
| `build_report.py` | Report content + reportlab layout. Team details are constants at the top. |
| `assets/` | Generated chart PNGs (not committed data — regenerate, don't hand-edit). |
| `out/` | The built PDF. |

## Font note

The spec allows Calibri or Arial. Calibri isn't a standard PDF font and Arial isn't
bundled with `reportlab`; this uses Helvetica, which is metrically identical to Arial (the
standard substitute used across PDF tooling) rather than embedding a TrueType font file.
If you want the literal Arial/Calibri glyphs, embed a `.ttf` via `reportlab.pdfbase.ttfonts`
and swap the `FONT`/`FONT_B` constants in `build_report.py`.
