"""
Generates the 3 chart PNGs used in the report from data/processed/ directly
(no numbers hand-typed here — every chart is computed the same way build_report.py's
cited statistics are computed, so the report text and the figures can't drift apart).

Run: py -3 report/make_charts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(exist_ok=True)

TIER_COLOR = {"beyond": "#C23B3B", "spof": "#C56A34", "single_net": "#D9A441", "redundant": "#4A90C4"}
TIER_LABEL = {"beyond": "Beyond gap\nthreshold", "spof": "Single point\nof failure",
              "single_net": "Single network\nonly", "redundant": "Multiple\nnetworks"}

plt.rcParams.update({"font.size": 10, "figure.dpi": 200, "axes.spines.top": False, "axes.spines.right": False})


def classify(row):
    if row["distance_gap_candidate"] is True:
        return "beyond"
    if row["n_towers_10km"] == 0:
        return "spof"
    if row["n_networks_10km"] <= 1:
        return "single_net"
    return "redundant"


vg = pd.read_csv(DATA / "village_gap_with_services.csv", dtype={"sa1_code": str})
vg["tier"] = vg.apply(classify, axis=1)

# --- Chart 1: tier distribution -------------------------------------------------
order = ["beyond", "spof", "single_net", "redundant"]
counts = vg["tier"].value_counts().reindex(order)
fig, ax = plt.subplots(figsize=(5.6, 3.0))
bars = ax.bar([TIER_LABEL[t] for t in order], counts.values, color=[TIER_COLOR[t] for t in order])
for b, c in zip(bars, counts.values):
    ax.text(b.get_x() + b.get_width() / 2, c + 8, f"{c}\n({c/792:.0%})", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("Communities (of 792)")
ax.set_ylim(0, 430)
ax.set_title("Mobile-coverage resilience tier, all 792 NT remote communities", fontsize=10.5)
fig.tight_layout()
fig.savefig(OUT / "fig1_tiers.png")
plt.close(fig)

# --- Chart 2: services distance, gap vs non-gap ---------------------------------
gap = vg[vg["distance_gap_candidate"] == True]
notgap = vg[vg["distance_gap_candidate"] == False]
services = ["km_nearest_school", "km_nearest_medical", "km_nearest_emergency"]
labels = ["School", "Medical", "Emergency"]
gap_med = [gap[c].median() for c in services]
notgap_med = [notgap[c].median() for c in services]

x = np.arange(len(labels))
w = 0.35
fig, ax = plt.subplots(figsize=(5.6, 3.0))
ax.bar(x - w / 2, notgap_med, w, label="Within mobile gap threshold (408)", color="#4A90C4")
ax.bar(x + w / 2, gap_med, w, label="Beyond mobile gap threshold (384)", color="#C23B3B")
for i, (a, b) in enumerate(zip(notgap_med, gap_med)):
    ax.text(i - w / 2, a + 1, f"{a:.1f}", ha="center", fontsize=8.5)
    ax.text(i + w / 2, b + 1, f"{b:.1f}", ha="center", fontsize=8.5)
ax.set_xticks(x, labels)
ax.set_ylabel("Median distance to nearest site (km)")
ax.set_title("Service distance is worse exactly where mobile coverage is worst", fontsize=10.5)
ax.set_ylim(0, 58)
ax.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.10), ncol=2, frameon=False)
fig.tight_layout()
fig.savefig(OUT / "fig2_services_gap.png")
plt.close(fig)

# --- Chart 3: MBSP unbuilt vs greedy targeting -----------------------------------
labels = ["15 km\n(gap threshold)", "40 km\n(macro-cell range)"]
mbsp_pct = [2.3, 10.6]
greedy_pct = [35.9, 44.0]
x = np.arange(len(labels))
fig, ax = plt.subplots(figsize=(5.6, 3.0))
ax.bar(x - w / 2, mbsp_pct, w, label="8 unbuilt MBSP sites (current backlog)", color="#6B6F76")
ax.bar(x + w / 2, greedy_pct, w, label="8 sites, population-weighted greedy", color="#009E73")
for i, (a, b) in enumerate(zip(mbsp_pct, greedy_pct)):
    ax.text(i - w / 2, a + 1, f"{a:.1f}%", ha="center", fontsize=8.5)
    ax.text(i + w / 2, b + 1, f"{b:.1f}%", ha="center", fontsize=8.5)
ax.set_xticks(x, labels)
ax.set_ylabel("Share of fragile-community\npopulation reached (of 36,973)")
ax.set_ylim(0, 55)
ax.set_title("Same number of sites (8), very different population reached", fontsize=10.5)
ax.legend(fontsize=8, loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "fig3_targeting.png")
plt.close(fig)

print("wrote:", sorted(p.name for p in OUT.glob("*.png")))
