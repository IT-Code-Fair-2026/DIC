# Hypothesis-proof notebooks

Formal statistical tests of the three hypotheses framed in the project report
(`report/out/DataChallenge_Team XX_Report.pdf`, Introduction section). These are
**not** part of the numbered `notebooks/00a`–`11` pipeline and are not run by
`run_pipeline.py` — they read the pipeline's already-built outputs from
`data/processed/` and test claims about them; they don't produce any new
`data/processed/` file.

| Notebook | Hypothesis | Method | Result |
|---|---|---|---|
| `H1_fragility_hypothesis.ipynb` | Most communities within reach of a tower have no independent second network as backup | Two one-sided exact binomial tests (village-level and tower-level) + chi-square test of independence vs. remoteness class; SA1-cluster bootstrap robustness check; Census population view by SA1 | **Supported** — 75% of covered places lack a second network (p < 1e-24; bootstrap upper bound 0.32 < 0.5); 33,177 people live in SA1s where no place has one |
| `H2_misallocation_hypothesis.ipynb` | The current MBSP investment backlog is not population-targeted | Two one-sided Monte Carlo tests (10,000 random draws, +1-corrected p): does MBSP-unbuilt beat random (Test A), does greedy (Test B); sensitivity without SA1s that contain a well-covered village | **Supported** — MBSP-unbuilt is indistinguishable from random (p = 0.57 at 40 km, 0.68 at 15 km: no evidence of targeting), greedy beats every random draw (p < 1e-4) |
| `H3_compounding_vulnerability_hypothesis.ipynb` | Connectivity gaps and service (school/medical/emergency) gaps overlap, not occur independently | Mann-Whitney U (rank-biserial effect size) per service type + Fisher's exact test on "zero services within 10 km", for the mobile gap and for `no_connectivity`; SA1-cluster bootstrap | **Strongly supported** — p < 1e-35 on every test, r = 0.54–0.72, every bootstrap interval excludes 0 |

**Data rules followed by all three.** Population is only ever the 2021 Census count per SA1, used
once per SA1 and never split across the villages inside it; BushTel population is never used.
BushTel places are reference points, so village-level counts are counts of *places*, not people.
Villages in one SA1 are not independent, so H1 and H3 also resample whole SA1s to check that their
conclusions do not rest on treating them as independent (H2's demand already works per SA1).

`greedy_algorithm_explained.txt` documents the population-weighted greedy
maximum-coverage algorithm used in `H2` (and in `app/app.py`'s Recommendations
tab): plain-language explanation, the formal submodular-optimisation argument
behind its (1 − 1/e) approximation guarantee, and a fully worked 6-site
numeric example you can check by hand — including a brute-force comparison
showing greedy matching the true optimum on that example.

## Reproducing

Each notebook re-derives its own numbers from `data/processed/*.csv` — nothing
is hand-typed. Re-run after `python run_pipeline.py` if the underlying data
changes:

```bash
py -3 -m jupyter nbconvert --to notebook --execute --inplace hypothesis_proof_notebooks/H1_fragility_hypothesis.ipynb
py -3 -m jupyter nbconvert --to notebook --execute --inplace hypothesis_proof_notebooks/H2_misallocation_hypothesis.ipynb
py -3 -m jupyter nbconvert --to notebook --execute --inplace hypothesis_proof_notebooks/H3_compounding_vulnerability_hypothesis.ipynb
```

(Or open them in Jupyter and Run All — same effect. They only need the
packages already in the root `requirements.txt`: pandas, numpy, scipy,
matplotlib, nbformat/nbconvert/ipykernel.)

## Ethical note

All three notebooks test properties of *infrastructure and service placement*,
not of the communities themselves — see the closing markdown cell of each
notebook, and the project report's Discussion section, for the full framing.
