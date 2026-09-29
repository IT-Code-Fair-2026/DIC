# Hypothesis-proof notebooks

Formal statistical tests of the three hypotheses framed in the project report
(`report/out/DataChallenge_Team XX_Report.pdf`, Introduction section). These are
**not** part of the numbered `notebooks/00a`–`11` pipeline and are not run by
`run_pipeline.py` — they read the pipeline's already-built outputs from
`data/processed/` and test claims about them; they don't produce any new
`data/processed/` file.

| Notebook | Hypothesis | Method | Result |
|---|---|---|---|
| `H1_fragility_hypothesis.ipynb` | Most communities within reach of a tower have no independent second network as backup | Two one-sided exact binomial tests (village-level and tower-level) + chi-square test of independence vs. remoteness class | **Supported** — p < 1e-24 at both levels |
| `H2_misallocation_hypothesis.ipynb` | The current MBSP investment backlog is not population-targeted | Monte Carlo permutation test (10,000 random draws) comparing MBSP-unbuilt reach and greedy-selected reach against the empirical random-selection distribution | **Supported** — MBSP-unbuilt underperforms the median random draw; greedy beats ~100% of random draws |
| `H3_compounding_vulnerability_hypothesis.ipynb` | Mobile-coverage gaps and service (school/medical/emergency) gaps overlap, not occur independently | Mann-Whitney U per service type + Fisher's exact test on "zero services within 10 km" | **Strongly supported** — p < 1e-54 on every test |

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
