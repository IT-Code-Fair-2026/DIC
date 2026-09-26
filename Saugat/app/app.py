"""
NT Deadzone Explorer — Services Edition
Extends the original app.py (DataScienceChallenge/app.py) with the three
service layers its own README listed as not-yet-done:
"[ ] Nearest-distance calculations for hospitals, police stations, clinics,
and schools."

Same tower-based tier logic as the original (GAP_KM = 15, BUFFER_KM = 10,
unchanged, still the primary classification) plus three additive things:
  1. A services KPI row (schools/medical/emergency access within 10 km).
  2. Nearest school / medical / emergency distance + name in every detail card.
  3. Optional map overlay showing the service sites themselves.

Run:
    pip install -r requirements.txt
    streamlit run app.py

Expects village_gap_with_services.csv, sa1_report.csv, and
services_sites_combined.csv in the same folder as this file.
"""

import html
import math
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="NT Deadzone Explorer — Services", layout="wide", page_icon=":material/cell_tower:")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0..1,0&display=block');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 3.75rem; padding-bottom: 1.5rem; }

    /* Title inside Streamlit's top bar (next to Deploy / menu). */
    [data-testid="stHeader"] {
        background: #0E1117; border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stApp"]:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stHeader"]::before { left: 4rem; }
    [data-testid="stHeader"]::before {
        content: "NT Deadzone Explorer   ·   Remote Connectivity | CDU IT Code Fair, Data Innovation Challenge 2026";
        position: absolute; left: 2rem; top: 50%; transform: translateY(-50%);
        max-width: calc(100% - 12rem); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        font-size: 0.95rem; font-weight: 500; letter-spacing: 0.02em;
        color: #E6E8EB; pointer-events: none;
    }

    .hero-eyebrow {
        letter-spacing: 0.12em; text-transform: uppercase; font-size: 0.72rem;
        font-weight: 700; color: #5B8DEF; margin-bottom: 2px;
    }

    /* Right-hand sheet, styled like the left sidebar. */
    .st-key-right_sheet {
        position: fixed; top: 60px; right: 0; bottom: 0; width: 340px; z-index: 99;
        background: #1A1D24; border-left: 1px solid rgba(255,255,255,0.10);
        padding: 1.25rem 1.25rem 2rem 1.25rem; overflow-y: auto; overscroll-behavior: contain;
    }
    .block-container { padding-left: 2rem !important; padding-right: 372px !important; }
    /* st.dialog restyled as a right-hand drawer. The backdrop ignores pointer
       events so the map stays clickable while the drawer is open. */
    [data-testid="stDialog"]:has(.st-key-close_detail) { pointer-events: none; background: transparent !important; }
    [data-testid="stDialog"]:has(.st-key-close_detail) > div { background: transparent !important; align-items: stretch; justify-content: flex-end; }
    [data-testid="stDialog"] [role="dialog"]:has(.st-key-close_detail) {
        pointer-events: auto; position: fixed; top: 60px; right: 0; bottom: 0; left: auto;
        width: var(--detail-w, 420px) !important; min-width: 340px; max-width: 90vw; height: auto; max-height: none;
        margin: 0; border-radius: 0; box-shadow: none;
        background: #1A1D24 !important; opacity: 1; border-left: 1px solid rgba(255,255,255,0.10);
        overflow-y: auto; overscroll-behavior: contain;
        animation: sheet-in 200ms ease-out;
    }
    [data-testid="stDialog"] [data-testid="stMetricValue"] { font-size: 1.05rem; font-weight: 500; }
    [data-testid="stDialog"] [data-testid="stMetricValue"] * { white-space: normal; overflow: visible; text-overflow: clip; }
    [data-testid="stDialog"] [data-testid="stMetricLabel"] { font-size: 0.75rem; color: rgba(255,255,255,0.55); }
    [data-testid="stDialog"] .st-key-close_detail {
        position: absolute; top: 1.85rem; right: 1.25rem; z-index: 6; width: auto;
    }
    [data-testid="stDialog"] .st-key-close_detail button {
        min-height: 28px; padding: 2px 10px; font-size: 0.8rem;
    }
    .sheet-resize-handle {
        position: absolute; top: 0; left: 0; bottom: 0; width: 6px; cursor: col-resize;
        z-index: 5; touch-action: none;
    }
    .sheet-resize-handle:hover, .sheet-resize-handle.dragging { background: rgba(91,141,239,0.55); }
    @keyframes sheet-in { from { transform: translateX(24px); opacity: 0; } to { transform: none; opacity: 1; } }
    @media (prefers-reduced-motion: reduce) { [data-testid="stDialog"] [role="dialog"]:has(.st-key-close_detail) { animation: none; } }
    @media (max-width: 1000px) {
        [data-testid="stDialog"] [role="dialog"]:has(.st-key-close_detail) { top: 0; width: 100vw !important; max-width: 100vw; }
        .st-key-right_sheet { position: static; width: auto; border-left: 0; }
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    }
    .st-key-scripts { position: absolute; width: 0; height: 0; overflow: hidden; }
    .st-key-table_box { flex: 0 0 520px; height: 520px; }
    .st-key-table_box [data-testid="stElementContainer"],
    .st-key-table_box [data-testid="stFullScreenFrame"],
    .st-key-table_box [data-testid="stDataFrame"] { height: 100%; }
    .mi {
        font-family: 'Material Symbols Rounded'; font-weight: normal; font-style: normal;
        font-size: 1.05em; line-height: 1; vertical-align: -0.18em; letter-spacing: normal;
        text-transform: none; white-space: nowrap; font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased;
    }
    .mi.fill { font-variation-settings: 'FILL' 1; }
    .range-row { display: flex; gap: 10px; align-items: flex-start; padding: 8px 0 12px 0; }
    .range-row .mi { font-size: 1.3rem; margin-top: 2px; }
    .near-summary { display: flex; flex-wrap: wrap; gap: 4px 16px; font-size: 0.85rem; color: rgba(255,255,255,0.70); margin: 2px 0 8px 0; }
    .near-summary .n { display: inline-flex; align-items: center; gap: 5px; font-variant-numeric: tabular-nums; }
    .near-summary_ { font-size: 0.85rem; color: rgba(255,255,255,0.70); margin: 2px 0 8px 0; }
    .near-row {
        display: flex; justify-content: space-between; gap: 12px;
        padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .near-name { font-size: 0.85rem; color: #EDEDED; }
    .near-detail { font-size: 0.75rem; color: rgba(255,255,255,0.55); }
    .near-km { font-size: 0.85rem; color: #EDEDED; white-space: nowrap; font-variant-numeric: tabular-nums; }
    .sheet-title {
        font-size: 0.72rem; font-weight: 500; color: rgba(255,255,255,0.50);
        margin: 4px 0 6px 0;
    }
    .stat-row {
        display: flex; justify-content: space-between; align-items: center; gap: 12px;
        padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .stat-row .stat-label {
        display: flex; align-items: center; gap: 8px;
        font-size: 0.85rem; font-weight: 400; color: rgba(255,255,255,0.72);
    }
    .stat-row .stat-dot {
        width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
        background: var(--tier-color, #888);
    }
    .stat-row .stat-value {
        font-size: 0.95rem; font-weight: 500; color: #EDEDED; white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }
    .stat-row .stat-total { font-weight: 400; color: rgba(255,255,255,0.45); margin-left: 4px; }
    .st-key-right_sheet .sheet-title:not(:first-child) { margin-top: 20px; }
    /* Flat, monochrome controls (Vercel-style): 1px borders, no shadows. */
    .stButton > button, .stDownloadButton > button {
        background: #0A0A0A; border: 1px solid rgba(255,255,255,0.14); border-radius: 8px;
        font-size: 0.85rem; font-weight: 500; min-height: 36px; box-shadow: none;
        transition: border-color 150ms ease, background-color 150ms ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #111; border-color: rgba(255,255,255,0.30); color: #EDEDED;
    }
    .stButton > button:focus-visible, .stDownloadButton > button:focus-visible,
    [data-baseweb="select"] > div:focus-within, [data-testid="stTab"]:focus-visible {
        outline: 2px solid #5B8DEF; outline-offset: 2px;
    }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div { border-radius: 8px; }
    [data-testid="stTab"] { font-weight: 500; }
    [data-testid="stTab"][aria-selected="true"], [data-testid="stTab"][aria-selected="true"] * { color: #EDEDED; }
    .react-aria-SelectionIndicator { background: #EDEDED; }
    [data-testid="stDialog"] [role="dialog"]:not(:has(.st-key-close_detail)) {
        background: #0A0A0A; border: 1px solid rgba(255,255,255,0.14); border-radius: 12px; box-shadow: none;
    }
    .st-key-open_search, .st-key-open_search [data-testid="stButton"] {
        width: 100%; display: flex; justify-content: flex-end;
    }
    .st-key-open_search button, .st-key-open_search button * { text-align: left; }
    .st-key-open_search button > div { flex: 1; justify-content: flex-start; }
    .st-key-open_search button span { justify-content: flex-start; }
    .st-key-open_search button {
        width: 100%; max-width: 340px; justify-content: space-between; color: rgba(255,255,255,0.55);
        font-weight: 400;
    }
    .st-key-open_search button::after {
        content: "Ctrl K"; white-space: nowrap; font-size: 0.72rem; color: rgba(255,255,255,0.50);
        border: 1px solid rgba(255,255,255,0.16); border-radius: 5px; padding: 1px 6px;
    }
    html[data-mac="1"] .st-key-open_search button::after { content: "⌘K"; }
    .result-count {
        text-align: left; font-size: 0.85rem; font-weight: 400;
        color: rgba(255,255,255,0.50); font-variant-numeric: tabular-nums;
    }
    /* Compact the sidebar's built-in header so the team name sits near the top. */
    [data-testid="stSidebarHeader"] { height: 2.5rem; min-height: 0; margin-bottom: 0; padding-bottom: 0; }
    .group-name {
        font-size: 1rem; font-weight: 500; color: #EDEDED;
        padding: 0 0 14px 0; margin-bottom: 6px;
        border-bottom: 1px solid rgba(255,255,255,0.10);
    }
    .group-name .group-label {
        display: block; font-size: 0.72rem; font-weight: 400;
        color: rgba(255,255,255,0.50); margin-bottom: 2px;
    }
    h1, h2, h3, h4 { font-weight: 500 !important; letter-spacing: -0.02em; }

    .map-legend { display: flex; gap: 18px; flex-wrap: wrap; margin: 10px 0 2px 0; }
    .map-legend .item { display: flex; align-items: center; gap: 7px; font-size: 0.8rem; color: rgba(255,255,255,0.68); }
    .map-legend .swatch { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex-shrink: 0; }

    /* ---- Left sidebar (Vercel-style): quiet labels, flat controls, hairline dividers ---- */
    [data-testid="stSidebar"] { overscroll-behavior: contain; }
    .side-title {
        display: flex; align-items: baseline; gap: 8px;
        font-size: 0.95rem; font-weight: 500; color: #EDEDED;
        margin-bottom: 12px;
    }
    .side-count { font-size: 0.75rem; font-weight: 400; color: rgba(255,255,255,0.50); font-variant-numeric: tabular-nums; }
    .side-section {
        font-size: 0.72rem; font-weight: 500; color: rgba(255,255,255,0.50);
        margin: 22px 0 8px 0; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.10);
    }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 0.78rem; font-weight: 500; color: rgba(255,255,255,0.65);
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #0A0A0A; border: 1px solid rgba(255,255,255,0.14); min-height: 36px;
        transition: border-color 150ms ease;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover { border-color: rgba(255,255,255,0.30); }
    /* Selected-value chips: the accent is near-white now, so restyle them explicitly. */
    [data-testid="stSidebar"] [data-testid="stMultiSelectTagsContainer"] > span > span {
        background: rgba(255,255,255,0.10) !important; border-radius: 6px;
    }
    [data-testid="stSidebar"] [data-testid="stMultiSelectTagsContainer"] > span > span,
    [data-testid="stSidebar"] [data-testid="stMultiSelectTagsContainer"] > span > span * {
        color: #EDEDED !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] details {
        background: #0A0A0A; border: 1px solid rgba(255,255,255,0.14); border-radius: 8px;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary { font-size: 0.85rem; font-weight: 500; }
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label,
    [data-testid="stSidebar"] [data-testid="stToggle"] label { min-height: 28px; font-size: 0.85rem; }
    [data-testid="stSidebar"] .stButton > button { min-height: 32px; font-size: 0.8rem; }
    [data-testid="stSidebar"] .stButton > button:disabled { opacity: 0.45; }
    .tier-def {
        display: flex; gap: 10px; align-items: flex-start;
        padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .tier-def .stat-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; background: var(--tier-color, #888); }
    .tier-def-name { font-size: 0.85rem; font-weight: 500; color: #EDEDED; }
    .tier-def-text { font-size: 0.78rem; color: rgba(255,255,255,0.55); line-height: 1.45; }
    .tier-def-text code { background: rgba(255,255,255,0.08); color: #EDEDED; padding: 1px 5px; border-radius: 4px; font-size: 0.74rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent  # data files sit next to app.py, whatever the working directory is


@st.cache_data
def load_data(path: str = "village_gap_with_services.csv") -> pd.DataFrame:
    df = pd.read_csv(APP_DIR / path, dtype={"sa1_code": str})

    bool_cols = [
        "is_remote", "in_nbn_fixed_line", "in_nbn_fixed_wireless",
        "has_rict_public_access", "distance_gap_candidate",
        "guide_says_covered", "guide_proximity_only",
    ]
    for c in bool_cols:
        if c in df.columns:
            df[c] = df[c].map({True: True, False: False, "True": True, "False": False})

    return df


@st.cache_data
def load_sa1_report(path: str = "sa1_report.csv") -> pd.DataFrame:
    df = pd.read_csv(APP_DIR / path, dtype={"sa1_code": str})
    return df[[
        "sa1_code", "pop_census_2021", "census_pop_suppressed",
        "median_hh_income_weekly", "avg_household_size", "n_villages",
        "village_names",
    ]]


@st.cache_data
def load_services(path: str = "services_sites_combined.csv") -> pd.DataFrame:
    df = pd.read_csv(APP_DIR / path)
    return df.dropna(subset=["latitude", "longitude"])


@st.cache_data
def load_towers(path: str = "towers.csv") -> pd.DataFrame:
    return pd.read_csv(APP_DIR / path).dropna(subset=["latitude", "longitude"])


@st.cache_data
def load_small_cells(path: str = "small_cells.csv") -> pd.DataFrame:
    return pd.read_csv(APP_DIR / path)


def classify(row: pd.Series) -> tuple[str, str]:
    """Unchanged from the original app — tower-based tier, GAP_KM/BUFFER_KM
    only. The services columns added by 07_services_gap.ipynb are shown
    alongside every result but deliberately don't move a village between
    tiers here, for the same reason the original app keeps Census population
    out of the classification: an SA1-level or best-effort-geocoded figure
    shouldn't be allowed to imply more precision than it has.
    """
    km = row["km_nearest_tower"]
    n_towers = row["n_towers_10km"]
    n_networks = row["n_networks_10km"]

    if row.get("distance_gap_candidate") is True:
        return "beyond", (
            f"{km:.1f} km from the nearest tower — beyond the 15 km triage "
            f"threshold (GAP_KM), with no coverage-guide claim of a real cell."
        )
    if n_towers == 0:
        return "spof", (
            f"Within the 15 km threshold (nearest tower {km:.1f} km), but zero "
            f"towers fall inside the 10 km buffer (BUFFER_KM) — relies on one "
            f"tower with no backup nearby."
        )
    if n_networks <= 1:
        return "single_net", (
            f"{n_towers} tower(s) within 10 km, but only {n_networks} "
            f"independent network — no real redundancy if it goes down."
        )
    return "redundant", (
        f"{n_networks} independent networks within 10 km — genuine redundancy."
    )


TIERS = {
    "beyond":     {"name": "Beyond gap threshold",     "color": "#C23B3B", "rank": 0},
    "spof":       {"name": "Single point of failure",  "color": "#C56A34", "rank": 1},
    "single_net": {"name": "Single network only",      "color": "#D9A441", "rank": 2},
    "redundant":  {"name": "Multiple networks",        "color": "#4A90C4", "rank": 3},
}

SERVICE_STYLE = {
    "school":    {"label": "School",    "color": "#59A14F", "icon": "school"},
    "medical":   {"label": "Medical",   "color": "#E45756", "icon": "stethoscope"},
    "emergency": {"label": "Emergency", "color": "#4C78A8", "icon": "emergency"},
}


def mi(name: str, color: str | None = None) -> str:
    """Inline Material Symbols icon for HTML snippets."""
    style = f' style="color:{color};"' if color else ""
    return f'<span class="mi" aria-hidden="true"{style}>{name}</span>'


@st.cache_data
def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    classified = df.apply(classify, axis=1, result_type="expand")
    df["tier_id"], df["reason"] = classified[0], classified[1]
    df["tier_name"] = df["tier_id"].map(lambda t: TIERS[t]["name"])
    df["tier_color"] = df["tier_id"].map(lambda t: TIERS[t]["color"])
    df["tier_rank"] = df["tier_id"].map(lambda t: TIERS[t]["rank"])
    return df


# ---------------------------------------------------------------------------
# Load + classify
# ---------------------------------------------------------------------------

try:
    raw = load_data()
except FileNotFoundError:
    st.error(
        "village_gap_with_services.csv not found in this folder. Place it next "
        "to app.py (same folder) and refresh."
    )
    st.stop()

try:
    sa1_report = load_sa1_report()
except FileNotFoundError:
    sa1_report = None

try:
    services = load_services()
except FileNotFoundError:
    services = None

try:
    towers = load_towers()
except FileNotFoundError:
    towers = None

try:
    small_cells = load_small_cells()
except FileNotFoundError:
    small_cells = None

PROVIDER_STYLE = {  # colour-blind-safe (Okabe-Ito); every band also has a text label
    "Telstra only": "#0072B2",
    "Optus only": "#E69F00",
    "Other sole provider": "#CC79A7",
    "Multiple providers": "#009E73",
    "No tower within 10 km": "#6B6F76",
}


def attach_providers(df: pd.DataFrame, radius_km: float = 10.0) -> pd.DataFrame:
    """Which network providers have a tower within `radius_km` of each community.

    Uses `networks` from towers.csv (the operator that runs the network, so TPG
    also covers Vodafone), the same definition as the notebook's `n_networks_10km`.
    Straight-line distance to a licensed tower site: triage, not a coverage claim.
    `sole_network` is set when exactly one provider is within reach, i.e. there
    is no backup if it fails.
    """
    df = df.copy()
    if towers is None:
        df["networks_10km"] = [[] for _ in range(len(df))]
    else:
        p = np.pi / 180
        lat, lon = df["latitude"].to_numpy()[:, None], df["longitude"].to_numpy()[:, None]
        tlat, tlon = towers["latitude"].to_numpy()[None, :], towers["longitude"].to_numpy()[None, :]
        a = np.sin((tlat - lat) * p / 2) ** 2 + np.cos(lat * p) * np.cos(tlat * p) * np.sin((tlon - lon) * p / 2) ** 2
        near = (2 * 6371.0088 * np.arcsin(np.sqrt(a))) <= radius_km
        tower_nets = [frozenset(str(n).split(";")) for n in towers["networks"]]
        df["networks_10km"] = [sorted(set().union(*[tower_nets[j] for j in np.flatnonzero(row)])) for row in near]
    n = df["networks_10km"].map(len)
    df["sole_network"] = [nets[0] if len(nets) == 1 else None for nets in df["networks_10km"]]
    df["providers_text"] = df["networks_10km"].map(lambda nets: ", ".join(nets) if nets else "None")
    df["provider_class"] = [
        "No tower within 10 km" if k == 0 else "Multiple providers" if k > 1
        else {"Telstra": "Telstra only", "Optus": "Optus only"}.get(sole, "Other sole provider")
        for k, sole in zip(n, df["sole_network"])
    ]
    return df


data = prepare(raw)
if sa1_report is not None:
    data = data.merge(sa1_report, on="sa1_code", how="left")
data = attach_providers(data)

HAS_SERVICES = all(c in data.columns for c in (
    "km_nearest_school", "km_nearest_medical", "km_nearest_emergency"
))

# ---------------------------------------------------------------------------
# Nearby: everything around a selected community
# ---------------------------------------------------------------------------

NEARBY_KM = 10  # same radius as the "within 10 km" counts elsewhere in the app
NEARBY_ORDER = ["tower", "school", "medical", "emergency"]
KIND_STYLE = {
    "tower": {"label": "Towers", "one": "Tower", "icon": "cell_tower", "color": "#A78BFA"},
    "school": {"label": "Schools", "one": "School", **{k: SERVICE_STYLE["school"][k] for k in ("icon", "color")}},
    "medical": {"label": "Medical sites", "one": "Medical", **{k: SERVICE_STYLE["medical"][k] for k in ("icon", "color")}},
    "emergency": {"label": "Emergency sites", "one": "Emergency", **{k: SERVICE_STYLE["emergency"][k] for k in ("icon", "color")}},
}


def _haversine_km(lat: float, lon: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    p = math.pi / 180
    a = np.sin((lats - lat) * p / 2) ** 2 + math.cos(lat * p) * np.cos(lats * p) * np.sin((lons - lon) * p / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


# Tower range comes from the NT government mobile coverage guide
# (data/raw/nt_mobile_coverage/mobile-coverage-all-sites.xlsx): "macro cell (up to
# 40 km coverage), small cell (up to 5 km coverage) ... Coverage varies according to
# local conditions especially topography and vegetation and this list is a GUIDE
# only." So both figures are upper bounds, not a coverage guarantee.
# The guide names 24 small-cell sites (small_cells.csv). A tower counts as a small
# cell when one of those sites is within 0.5 km AND that provider is among the
# tower's carriers; every other tower is treated as a macro cell. Shared sites
# (e.g. an Optus small cell next to a Telstra macro tower) can therefore be
# labelled by the guide's provider only.
MACRO_KM, SMALL_KM = 40, 5


@st.cache_data
def tower_cell_types() -> pd.Series:
    cells = pd.Series("macro", index=towers.index)
    if small_cells is not None:
        for _, sc in small_cells.iterrows():
            d = _haversine_km(sc["latitude"], sc["longitude"], towers["latitude"].to_numpy(), towers["longitude"].to_numpy())
            has_provider = towers["carriers"].str.contains(str(sc["provider"]), case=False, na=False).to_numpy()
            cells[(d <= 0.5) & has_provider] = "small"
    return cells


@st.cache_data
def nearby_for_id(community_id: int) -> pd.DataFrame:
    """Every tower/school/medical/emergency site with its straight-line km from
    one community, nearest first. Haversine, so it can differ from the notebook's
    projected-CRS distances by a few hundred metres."""
    row = data[data["community_id"] == community_id].iloc[0]
    frames = []
    if towers is not None:
        cell = tower_cell_types()
        detail = (towers["carriers"].str.replace(";", ", ") + " · " + towers["n_transmitters"].astype(str)
                  + " transmitters · " + cell + " cell")
        detail = detail.where(~towers["is_planning_site"], detail + " (planned)")
        frames.append(pd.DataFrame({"kind": "tower", "name": towers["name"], "latitude": towers["latitude"],
                                    "longitude": towers["longitude"], "detail": detail,
                                    "cell": cell, "range_km": cell.map({"macro": MACRO_KM, "small": SMALL_KM})}))
    if services is not None:
        for src in ("school", "medical", "emergency"):
            sub = services[services["source"] == src]
            frames.append(pd.DataFrame({"kind": src, "name": sub["name"], "latitude": sub["latitude"],
                                        "longitude": sub["longitude"], "detail": sub["type"].fillna("")}))
    if not frames:
        return pd.DataFrame(columns=["kind", "name", "latitude", "longitude", "detail", "km"])
    items = pd.concat(frames, ignore_index=True)
    items["km"] = _haversine_km(float(row["latitude"]), float(row["longitude"]),
                                items["latitude"].to_numpy(), items["longitude"].to_numpy())
    return items.sort_values("km").reset_index(drop=True)


NEAREST_WHEN_EMPTY = 3  # how many of the closest sites to list when none are inside the radius


def _near_rows(rows: pd.DataFrame) -> str:
    return "".join(
        f'<div class="near-row"><div><div class="near-name">{html.escape(str(r["name"]))}</div>'
        f'<div class="near-detail">{html.escape(str(r["detail"]))}</div></div>'
        f'<span class="near-km">{r["km"]:.1f}&nbsp;km</span></div>'
        for _, r in rows.iterrows()
    )


def nearby_section(v: pd.Series) -> None:
    items = nearby_for_id(int(v["community_id"]))
    if items.empty:
        return
    within = items[items["km"] <= NEARBY_KM]
    towers_here = items[items["kind"] == "tower"]
    if not towers_here.empty:
        t0 = towers_here.iloc[0]
        reach_km = float(t0["range_km"])
        inside = float(t0["km"]) <= reach_km
        verdict = "Inside guide range" if inside else f"{float(t0['km']) - reach_km:.1f} km beyond guide range"
        st.markdown("**Nearest Tower Range**")
        st.markdown(
            f'<div class="range-row">{mi("check_circle" if inside else "cancel", "#4ADE80" if inside else "#F87171")}'
            f'<div><div class="near-name">{html.escape(str(t0["name"]))}</div>'
            f'<div class="near-detail">{float(t0["km"]):.1f} km away · guide range up to {reach_km:g} km '
            f'({t0["cell"]} cell)</div>'
            f'<div class="near-name">{verdict}</div></div></div>',
            unsafe_allow_html=True,
        )
    nets = list(v.get("networks_10km", []) or [])
    if towers is not None:
        note = "no backup if it fails" if len(nets) == 1 else "none within reach" if not nets else f"{len(nets)} providers"
        st.markdown(
            f'<div class="near-summary"><span class="n">{mi("cell_tower")}Providers within {NEARBY_KM} km: '
            f'{", ".join(nets) if nets else "None"} ({note})</span></div>', unsafe_allow_html=True,
        )
    st.markdown(f"**Nearby Within {NEARBY_KM} km**")
    summary = "".join(
        f'<span class="n" title="{KIND_STYLE[k]["label"]}">{mi(KIND_STYLE[k]["icon"], KIND_STYLE[k]["color"])}'
        f'{int((within["kind"] == k).sum())} {KIND_STYLE[k]["label"]}</span>'
        for k in NEARBY_ORDER if k in set(items["kind"])
    )
    st.markdown(f'<div class="near-summary">{summary}</div>', unsafe_allow_html=True)
    for kind in NEARBY_ORDER:
        of_kind = items[items["kind"] == kind]
        if of_kind.empty:
            continue
        sub = within[within["kind"] == kind]
        style = KIND_STYLE[kind]
        with st.expander(
            f"{style['label']} · {len(sub)}", icon=f":material/{style['icon']}:",
            expanded=len(sub) <= 5,
        ):
            if sub.empty:
                st.caption(f"None within {NEARBY_KM} km. Closest {NEAREST_WHEN_EMPTY}:")
                st.markdown(_near_rows(of_kind.head(NEAREST_WHEN_EMPTY)), unsafe_allow_html=True)
            else:
                st.markdown(_near_rows(sub), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Map colour modes
# ---------------------------------------------------------------------------

COLOR_MODES = [
    "Tier", "Provider", "Tower distance", "Population",
    "School distance", "Medical distance", "Emergency distance",
]
# Cool -> warm ramp reusing the tier hues; every band also has a text label.
DIST_RAMP = ["#4A90C4", "#D9A441", "#C56A34", "#C23B3B"]
POP_RAMP = ["#3E4C63", "#5F80B5", "#8DB3EA", "#D6E6FF"]
NO_DATA = "#6B6F76"
DIST_BINS = {
    "km_nearest_tower": [5, 15, 50],
    "km_nearest_school": [10, 25, 50],
    "km_nearest_medical": [10, 25, 50],
    "km_nearest_emergency": [10, 25, 50],
}
DIST_COL = {
    "Tower distance": ("km_nearest_tower", "Nearest tower"),
    "School distance": ("km_nearest_school", "Nearest school"),
    "Medical distance": ("km_nearest_medical", "Nearest medical"),
    "Emergency distance": ("km_nearest_emergency", "Nearest emergency"),
}
POP_BINS = [100, 300, 600]


def _band_labels(edges: list[int], unit: str) -> list[str]:
    labels = [f"< {edges[0]} {unit}"]
    labels += [f"{a}–{b} {unit}" for a, b in zip(edges, edges[1:])]
    labels.append(f"{edges[-1]}+ {unit}")
    return labels


def colour_dots(df: pd.DataFrame, mode: str):
    """Per-row dot colour + tooltip metric + legend entries for a colour mode."""
    if mode == "Provider":
        colours = df["provider_class"].map(PROVIDER_STYLE)
        metric = df["provider_class"] + " (" + df["providers_text"] + ")"
        return colours, metric, [(c, label) for label, c in PROVIDER_STYLE.items()]

    if mode == "Tier" or (mode in DIST_COL and DIST_COL[mode][0] not in df.columns):
        legend = [(t["color"], t["name"]) for t in TIERS.values()]
        return df["tier_color"], df["tier_name"], legend

    if mode == "Population":
        edges, ramp, unit = POP_BINS, POP_RAMP, "people"
        values = df["pop_census_2021"]
        metric = values.map(lambda x: f"SA1 population {int(x):,}" if pd.notna(x) else "No Census record")
        title = "SA1 population (2021): "
    else:
        col, name = DIST_COL[mode]
        edges, ramp, unit = DIST_BINS[col], DIST_RAMP, "km"
        values = df[col]
        metric = values.map(lambda x: f"{name} {x:.1f} km")
        title = f"{name}: "

    band = pd.cut(values, bins=[-float("inf")] + edges + [float("inf")], right=False, labels=False)
    colours = band.map(lambda b: ramp[int(b)] if pd.notna(b) else NO_DATA)
    labels = _band_labels(edges, unit)
    legend = [(ramp[i], f"{title if i == 0 else ''}{labels[i]}") for i in range(len(ramp))]
    if values.isna().any():
        legend.append((NO_DATA, "No data"))
    return colours, metric, legend


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

# Right-hand sheet (mirrors the left sidebar): stats first, then the details of
# whichever map dot was clicked (filled in further down, after the click is read).
right_sheet = st.container(key="right_sheet")


def stat_row(color: str, label: str, value: str, total: str = "") -> str:
    total_html = f'<span class="stat-total">/&nbsp;{total}</span>' if total else ""
    return (
        f'<div class="stat-row"><span class="stat-label"><span class="stat-dot" '
        f'style="--tier-color:{color};"></span>{label}</span>'
        f'<span class="stat-value">{value}{total_html}</span></div>'
    )


with right_sheet:
    tier_rows = "".join(
        stat_row(TIERS[t]["color"], TIERS[t]["name"], f"{int((data['tier_id'] == t).sum()):,}")
        for t in TIERS
    )
    st.markdown(
        f'<div class="sheet-title">Priority Tiers</div>{tier_rows}', unsafe_allow_html=True
    )
    if HAS_SERVICES:
        svc_kpis = [
            ("school", "n_schools_10km", "No school within 10 km"),
            ("medical", "n_medical_10km", "No medical facility within 10 km"),
            ("emergency", "n_emergency_10km", "No emergency facility within 10 km"),
        ]
        svc_rows = "".join(
            stat_row(SERVICE_STYLE[k]["color"], label, f"{int((data[c] == 0).sum()):,}", "792")
            for k, c, label in svc_kpis
        )
        st.markdown(
            f'<div class="sheet-title">Services</div>{svc_rows}', unsafe_allow_html=True
        )
    if towers is not None:
        prov_rows = "".join(
            stat_row(PROVIDER_STYLE[k], k, f"{int((data['provider_class'] == k).sum()):,}")
            for k in PROVIDER_STYLE if (data["provider_class"] == k).any()
        )
        st.markdown(f'<div class="sheet-title">Provider Within 10 km</div>{prov_rows}', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

GROUP_NAME = "Team ASTRA"

st.sidebar.markdown(
    f'<div class="group-name"><span class="group-label">Team</span>{GROUP_NAME}</div>',
    unsafe_allow_html=True,
)
theme_head = st.sidebar.container()  # flags / artwork / acknowledgement, when the cultural theme is on

FILTER_DEFAULTS = {
    "tier_filter": [], "type_filter": [], "remote_filter": [],
    "min_tower_filter": 0,
    "no_rict_filter": False, "guide_covered_filter": False, "in_nbn_filter": False,
    "no_school_filter": False, "no_medical_filter": False, "no_emergency_filter": False,
    "show_services_filter": False,
    "color_by": "Tier",
    "provider_filter": [], "sole_filter": False,
}


def reset_filters() -> None:
    # A callback runs before the widgets are rebuilt, so setting the values
    # here reliably resets them (popping keys left sliders stale).
    for k, default in FILTER_DEFAULTS.items():
        st.session_state[k] = default
    st.session_state.pop("picked_card_id", None)
    st.session_state.pop("_last_map_click", None)
    st.session_state.pop("lookup_pick", None)
    st.session_state["map_epoch"] = st.session_state.get("map_epoch", 0) + 1


# Header row is filled in after the widgets exist, so it can show how many
# filters are active.
filters_head = st.sidebar.container()

tier_filter = st.sidebar.multiselect(
    "Priority Tier",
    options=list(TIERS.keys()),
    default=[],
    placeholder="All",
    format_func=lambda t: TIERS[t]["name"],
    key="tier_filter", bind="query-params",
)

type_options = sorted(data["community_type"].unique())
type_filter = st.sidebar.multiselect(
    "Community Type", options=type_options, default=[], placeholder="All", key="type_filter",
    bind="query-params",
)

remote_options = sorted(data["remoteness_name"].unique())
remote_filter = st.sidebar.multiselect(
    "Remoteness", options=remote_options, default=[], placeholder="All", key="remote_filter",
    bind="query-params",
)

provider_options = sorted({n for nets in data["networks_10km"] for n in nets})
provider_filter = st.sidebar.multiselect(
    "Provider Within 10 km", options=provider_options, default=[], placeholder="All", key="provider_filter",
    bind="query-params", disabled=not provider_options,
)
sole_only = st.sidebar.checkbox(
    "Sole provider only (no backup)", key="sole_filter", bind="query-params", disabled=not provider_options,
)

min_tower = st.sidebar.slider(
    "Min Distance to Tower (km)", 0, 150, 0, key="min_tower_filter",
    bind="query-params",
)

with st.sidebar.expander("More Filters"):
    no_rict = st.checkbox("No RICT public access", key="no_rict_filter", bind="query-params")
    guide_covered = st.checkbox("Guide claims coverage", key="guide_covered_filter", bind="query-params")
    in_nbn = st.checkbox("Inside NBN footprint", key="in_nbn_filter", bind="query-params")
    no_school = st.checkbox("No school within 10 km", key="no_school_filter", bind="query-params", disabled=not HAS_SERVICES)
    no_medical = st.checkbox("No medical facility within 10 km", key="no_medical_filter", bind="query-params", disabled=not HAS_SERVICES)
    no_emergency = st.checkbox("No emergency facility within 10 km", key="no_emergency_filter", bind="query-params", disabled=not HAS_SERVICES)

active_filters = sum([
    bool(tier_filter), bool(type_filter), bool(remote_filter), bool(provider_filter), sole_only, min_tower > 0,
    no_rict, guide_covered, in_nbn, no_school, no_medical, no_emergency,
])
COPY_LINK_HTML = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap');
  body { margin: 0; }
  button { width: 100%; height: 32px; cursor: pointer; border-radius: 8px;
           display: flex; align-items: center; justify-content: center; gap: 6px;
           background: #0A0A0A; color: #EDEDED; font: 500 12.8px Inter, sans-serif;
           border: 1px solid rgba(255,255,255,0.14);
           transition: border-color 150ms ease, background-color 150ms ease; }
  button:hover { border-color: rgba(255,255,255,0.30); background: #111; }
  button:focus-visible { outline: 2px solid #5B8DEF; outline-offset: 2px; }
  svg { width: 14px; height: 14px; flex-shrink: 0; }
</style>
<button id="copy" type="button" aria-label="Copy link to this view">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
       stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
       <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
  <span id="label">Copy Link</span>
</button>
<script>
  // Filters, colour mode and the selected community all live in the address bar,
  // so this copies a link that reopens the exact same view.
  const btn = document.getElementById('copy'), label = document.getElementById('label');
  btn.addEventListener('click', () => {
    const t = document.createElement('textarea');
    t.value = window.parent.location.href;
    document.body.appendChild(t); t.select();
    let ok = false; try { ok = document.execCommand('copy'); } catch (e) {}
    t.remove();
    label.textContent = ok ? 'Copied' : 'Copy Failed';
    setTimeout(() => { label.textContent = 'Copy Link'; }, 2000);
  });
</script>
"""

with filters_head:
    st.markdown(
        f'<div class="side-title">Filters<span class="side-count">{active_filters} Active</span></div>',
        unsafe_allow_html=True,
    )
    reset_col, copy_col = st.columns(2, vertical_alignment="center")
    reset_col.button(
        "Reset", key="reset_filters", icon=":material/refresh:", on_click=reset_filters,
        disabled=active_filters == 0, width="stretch",
    )
    with copy_col:
        st.iframe(COPY_LINK_HTML, height=32)

st.sidebar.markdown('<div class="side-section">Display</div>', unsafe_allow_html=True)
show_services_layer = st.sidebar.toggle(
    "Show Service Sites on Map", value=False, key="show_services_filter",
    bind="query-params", disabled=services is None,
)
cultural_theme = st.sidebar.toggle("Cultural Theme", value=True, key="cultural_theme", bind="query-params")

# ---------------------------------------------------------------------------
# Cultural theme: Aboriginal and Torres Strait Islander recognition
# ---------------------------------------------------------------------------
#
# Deliberate choices (First Nations Indigenous Cultural and Intellectual Property, ICIP):
# - Colours only, from the Aboriginal flag (black, red, yellow). No generated "Aboriginal
#   style" art or dot patterns: traditional designs belong to specific peoples and
#   Countries and are used only with the artist's or community's permission.
# - Flags are shown ONLY from official artwork the team drops into assets/flags/
#   (unaltered, not recoloured, cropped or redrawn). Nothing is drawn in code.
# - Artwork is shown ONLY if assets/artwork/ has an image AND an attribution.txt naming the
#   artist / community and confirming permission. See assets/README.md.
# - Edit ACK_TEXT to name the local Traditional Custodians (e.g. Larrakia Country for Darwin).
ASSETS_DIR = APP_DIR / "assets"
ACK_TEXT = (
    "We acknowledge the Traditional Custodians of the lands and waters across the Northern "
    "Territory, and pay our respects to Elders past and present. This project uses data about "
    "their communities, and we aim to use it with care."
)
FLAG_FILES = {
    "Aboriginal flag": ("aboriginal_flag.svg", "aboriginal_flag.png"),
    "Torres Strait Islander flag": ("torres_strait_islander_flag.svg", "torres_strait_islander_flag.png"),
}


def _first_existing(folder: Path, names) -> Path | None:
    return next((folder / n for n in names if (folder / n).is_file()), None)


if cultural_theme:
    st.markdown(
        """
        <style>
        /* Flag colours: black, red (Pantone 032), yellow (Pantone 116). Accents only. */
        [data-testid="stHeader"]::after {
            content: ""; position: absolute; left: 0; right: 0; top: 0; height: 4px;
            background: linear-gradient(90deg, #000000 0 33.3%, #EF3340 33.3% 66.6%, #FFCD00 66.6% 100%);
        }
        .react-aria-SelectionIndicator { background: #FFCD00 !important; }
        [data-testid="stTab"][aria-selected="true"], [data-testid="stTab"][aria-selected="true"] * { color: #FFCD00 !important; }
        .side-section, .sheet-title, .group-name .group-label { color: rgba(255,205,0,0.80) !important; }
        .stButton > button:hover, .stDownloadButton > button:hover { border-color: rgba(255,205,0,0.65) !important; }
        .stButton > button:focus-visible, .stDownloadButton > button:focus-visible,
        [data-baseweb="select"] > div:focus-within, [data-testid="stTab"]:focus-visible { outline-color: #FFCD00 !important; }
        .st-key-right_sheet { border-left-color: rgba(239,51,64,0.55) !important; }
        .side-title .side-count { color: rgba(255,205,0,0.80); }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with theme_head:
        flag_paths = [(name, _first_existing(ASSETS_DIR / "flags", files)) for name, files in FLAG_FILES.items()]
        flag_paths = [(n, f) for n, f in flag_paths if f is not None]
        if flag_paths:
            for col, (name, path) in zip(st.columns(len(flag_paths) + 1)[:-1], flag_paths):
                col.image(str(path), caption=name, width=64)
        art_dir = ASSETS_DIR / "artwork"
        art = next((f for f in sorted(art_dir.iterdir()) if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".webp"}), None) if art_dir.is_dir() else None
        credit = ASSETS_DIR / "artwork" / "attribution.txt"
        if art is not None and credit.is_file():  # never show artwork without its attribution
            st.image(str(art), width="stretch")
            st.caption(credit.read_text(encoding="utf-8").strip())
        with st.expander("Acknowledgement of Country", icon=":material/volunteer_activism:"):
            st.write(ACK_TEXT)

TIER_DESC = {
    "beyond": "&gt;&nbsp;15&nbsp;km, no guide claim (<code translate=\"no\">GAP_KM</code>)",
    "spof": "Within 15&nbsp;km, 0 towers in 10&nbsp;km buffer (<code translate=\"no\">BUFFER_KM</code>)",
    "single_net": "Towers nearby, 1 network",
    "redundant": "2+ networks within 10&nbsp;km",
}

# The tier is mobile-tower only. Schools/medical/emergency distances are shown per
# community and filterable, but don't change the tier: they come from a separate
# notebook (07_services_gap.ipynb) added after the tower classification was locked
# in, and mixing the two into one score would need a judgement call this app
# doesn't make for you.
tier_defs = "".join(
    f'<div class="tier-def"><span class="stat-dot" style="--tier-color:{TIERS[tid]["color"]};"></span>'
    f'<div><div class="tier-def-name">{TIERS[tid]["name"]}</div>'
    f'<div class="tier-def-text">{TIER_DESC[tid]}</div></div></div>'
    for tid in TIERS
)
st.sidebar.markdown(
    f'<div class="side-section">How Tiers Work</div>{tier_defs}', unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------

effective_tier = tier_filter or list(TIERS.keys())
effective_type = type_filter or type_options
effective_remote = remote_filter or remote_options

mask = (
    data["tier_id"].isin(effective_tier)
    & data["community_type"].isin(effective_type)
    & data["remoteness_name"].isin(effective_remote)
    & (data["km_nearest_tower"] >= min_tower)
)
if provider_filter:
    chosen = set(provider_filter)
    if sole_only:  # the chosen provider is the ONLY one within reach: its failure leaves no service
        mask &= data["sole_network"].isin(chosen)
    else:
        mask &= data["networks_10km"].map(lambda nets: bool(chosen.intersection(nets)))
elif sole_only:
    mask &= data["sole_network"].notna()
if no_rict:
    mask &= ~data["has_rict_public_access"].fillna(False)
if guide_covered:
    mask &= data["guide_says_covered"] == True  # noqa: E712
if in_nbn:
    mask &= data["in_nbn_fixed_line"].fillna(False) | data["in_nbn_fixed_wireless"].fillna(False)
if HAS_SERVICES:
    if no_school:
        mask &= data["n_schools_10km"] == 0
    if no_medical:
        mask &= data["n_medical_10km"] == 0
    if no_emergency:
        mask &= data["n_emergency_10km"] == 0

filtered = data[mask].copy()
count_col, search_col = st.columns([1, 1], vertical_alignment="center")
open_palette = search_col.button("Search Communities…", key="open_search", icon=":material/search:")
count_col.markdown(
    f'<div class="result-count">{len(filtered):,} of {len(data):,} communities shown</div>',
    unsafe_allow_html=True,
)

tab_map, tab_table, tab_insights, tab_plan = st.tabs(["Map", "Table", "Insights", "Recommendations"])

# ---------------------------------------------------------------------------
# Map + points list
# ---------------------------------------------------------------------------

map_col = tab_map

with map_col:
    color_mode = st.segmented_control(
        "Colour dots by", COLOR_MODES, default="Tier", required=True,
        key="color_by", bind="query-params",
    ) or "Tier"
    _pk = st.session_state.get("picked_card_id")
    focus_view = "Nearby"
    if towers is not None and _pk is not None and (data["community_id"] == _pk).any():
        focus_view = st.segmented_control(
            "Map view", ["Nearby", "Tower range"], default="Nearby", required=True, key="focus_view",
        ) or "Nearby"
    dot_color, dot_metric, legend_items = colour_dots(filtered, color_mode)
    legend_html = "".join(
        f'<span class="item"><span class="swatch" style="background:{c}"></span>{label}</span>'
        for c, label in legend_items
    )
    if show_services_layer and services is not None:
        legend_html += "".join(
            f'<span class="item">{mi(s["icon"], s["color"])} {s["label"]}</span>'
            for s in SERVICE_STYLE.values()
        )
    _picked_now = st.session_state.get("picked_card_id")
    if _picked_now is not None and (data["community_id"] == _picked_now).any():
        legend_html += '<span class="item"><span class="mi fill" style="color:#FFFFFF;">location_on</span> Selected community</span>'
        legend_html += f'<span class="item">{mi("radio_button_unchecked", KIND_STYLE["tower"]["color"])} Nearest tower range</span>'
        legend_html += "".join(
            f'<span class="item">{mi(KIND_STYLE[k]["icon"], KIND_STYLE[k]["color"])} {KIND_STYLE[k]["one"]}</span>' for k in NEARBY_ORDER
        ) + f'<span class="item">Dashed: nearest of each kind · circle: {NEARBY_KM} km</span>'
    st.markdown(f'<div class="map-legend">{legend_html}</div>', unsafe_allow_html=True)

    focus_id = st.session_state.get("picked_card_id")
    focus_rows = data[data["community_id"] == focus_id]
    focus = focus_rows.iloc[0] if not focus_rows.empty else None

    # A selected community re-centres the map on it. The zoom fits the 10 km radius,
    # or zooms out (up to 150 km) so the nearest site of each kind is in view too.
    focus_zoom = 5
    focus_center = [-19.5, 133.5]
    if focus is not None:
        focus_center = [float(focus["latitude"]), float(focus["longitude"])]
        focus_items = nearby_for_id(int(focus["community_id"]))
        reach = float(min(max(focus_items.groupby("kind")["km"].min().max(), NEARBY_KM), 150))
        focus_towers = focus_items[focus_items["kind"] == "tower"]
        if focus_view == "Tower range" and not focus_towers.empty:
            # Frame the nearest tower's whole range ring and the community together.
            t0 = focus_towers.iloc[0]
            focus_center = [(focus_center[0] + float(t0["latitude"])) / 2, (focus_center[1] + float(t0["longitude"])) / 2]
            reach = (float(t0["km"]) / 2 + float(t0["range_km"])) * 1.05
        mpp = reach * 1000 * 1.15 / 270  # metres per pixel that fit `reach` in half the map height
        focus_zoom = int(max(6, min(11, math.floor(math.log2(156543.03 * math.cos(math.radians(focus_center[0])) / mpp)))))
    m = folium.Map(
        location=focus_center,
        zoom_start=focus_zoom, tiles="OpenStreetMap", prefer_canvas=True,
    )
    if focus is not None:
        # Added first so the community dots stay on top and clickable.
        folium.Circle(
            [float(focus["latitude"]), float(focus["longitude"])], radius=NEARBY_KM * 1000,
            color="#EDEDED", weight=1, dash_array="4 6", fill=True, fill_color="#EDEDED", fill_opacity=0.05,
            interactive=False,
        ).add_to(m)
        # Nearest tower's range ring (guide upper bound: 40 km macro, 5 km small cell).
        _tw = nearby_for_id(int(focus["community_id"]))
        _tw = _tw[_tw["kind"] == "tower"]
        if not _tw.empty:
            _t0 = _tw.iloc[0]
            folium.Circle(
                [float(_t0["latitude"]), float(_t0["longitude"])], radius=float(_t0["range_km"]) * 1000,
                color=KIND_STYLE["tower"]["color"], weight=1.5, dash_array="2 6", fill=True,
                fill_color=KIND_STYLE["tower"]["color"], fill_opacity=0.05, interactive=False,
            ).add_to(m)
    m.get_root().header.add_child(folium.Element(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0..1,0&display=block">'
        '<style>.mi{font-family:"Material Symbols Rounded";font-weight:normal;font-style:normal;font-size:15px;'
        'line-height:1;letter-spacing:normal;text-transform:none;white-space:nowrap;font-feature-settings:"liga";'
        '-webkit-font-smoothing:antialiased}.mi.fill{font-variation-settings:"FILL" 1}'
        '.astra-pin-label{background:#0A0A0A;color:#fff;border:1px solid rgba(255,255,255,.65);border-radius:6px;'
        'font:600 12px Inter,system-ui,sans-serif;padding:3px 8px;box-shadow:none}'
        '.astra-pin-label:before{display:none}</style>'
    ))
    m.get_root().header.add_child(folium.Element(
        "<style>.leaflet-tile-pane "
        "{ filter: invert(1) hue-rotate(180deg) brightness(0.92) contrast(0.9); }</style>"
    ))
    tooltip_to_id = {}
    for idx, v in filtered.iterrows():
        tooltip_text = (
            f"{v['community_name']} · {v['tier_name']} · "
            f"{v['km_nearest_tower']:.1f} km"
        )
        if color_mode != "Tier":
            tooltip_text = f"{v['community_name']} · {dot_metric[idx]}"
        tooltip_to_id[tooltip_text] = v["community_id"]
        folium.CircleMarker(
            location=[v["latitude"], v["longitude"]],
            radius=6,
            color="#0E1117",
            weight=1,
            fill=True,
            fill_color=dot_color[idx],
            fill_opacity=0.92,
            tooltip=tooltip_text,
        ).add_to(m)

    if show_services_layer and services is not None:
        for source, style in SERVICE_STYLE.items():
            sub = services[services["source"] == source]
            for _, s in sub.iterrows():
                folium.CircleMarker(
                    location=[s["latitude"], s["longitude"]],
                    radius=3,
                    color=style["color"],
                    weight=1,
                    fill=True,
                    fill_color=style["color"],
                    fill_opacity=0.7,
                    tooltip=f"{style['label']} · {s['name']}",
                ).add_to(m)

    if focus is not None:
        clat, clon = float(focus["latitude"]), float(focus["longitude"])
        items = nearby_for_id(int(focus["community_id"]))
        nearest_each = items.groupby("kind").head(1)
        within_map = items[items["km"] <= NEARBY_KM]
        # A kind with nothing inside the radius still shows its closest few sites.
        empty_kinds = [k for k in NEARBY_ORDER if k in set(items["kind"]) and k not in set(within_map["kind"])]
        closest = items[items["kind"].isin(empty_kinds)].groupby("kind").head(NEAREST_WHEN_EMPTY)
        shown = pd.concat([within_map, nearest_each, closest]).loc[lambda d: ~d.index.duplicated()]
        for _, it in shown.iterrows():
            st_ = KIND_STYLE[it["kind"]]
            folium.Marker(
                [it["latitude"], it["longitude"]],
                icon=folium.DivIcon(
                    html=(f'<div style="width:24px;height:24px;border-radius:50%;background:#0A0A0A;'
                          f'border:1.5px solid {st_["color"]};display:flex;align-items:center;'
                          f'justify-content:center;"><span class="mi" style="color:{st_["color"]};">{st_["icon"]}</span></div>'),
                    icon_size=(24, 24), icon_anchor=(12, 12),
                ),
                tooltip=(f"{st_['one']} · {it['name']} · {it['km']:.1f} km"
                         + (f" · range up to {it['range_km']:g} km" if it["kind"] == "tower" else "")),
            ).add_to(m)
        # Dashed line to the nearest site of each kind, even when it is beyond 10 km.
        for _, it in nearest_each.iterrows():
            st_ = KIND_STYLE[it["kind"]]
            folium.PolyLine(
                [[clat, clon], [it["latitude"], it["longitude"]]],
                color=st_["color"], weight=2, opacity=0.9, dash_array="6 6",
                tooltip=f"Nearest {st_['one'].lower()} · {it['name']} · {it['km']:.1f} km",
            ).add_to(m)
        # The community itself: a large white pin with its name always visible, so it
        # cannot be confused with the tower/service icons around it.
        folium.Marker(
            [clat, clon],
            icon=folium.DivIcon(
                html=('<span class="mi fill" style="font-size:40px;color:#FFFFFF;'
                      'text-shadow:0 0 5px #000,0 0 2px #000;">location_on</span>'),
                icon_size=(40, 40), icon_anchor=(20, 38),
            ),
            tooltip=folium.Tooltip(str(focus["community_name"]), permanent=True, direction="right",
                                   offset=(16, -22), class_name="astra-pin-label"),
            z_index_offset=1000,
        ).add_to(m)

    map_state = st_folium(
        m, height=560, use_container_width=True,
        returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
        # Key changes with the filtered set so the map redraws when filters change.
        key=f"deadzone_map_{pd.util.hash_pandas_object(filtered['community_id'], index=False).sum()}_{show_services_layer}_{color_mode}_{focus_id}_{focus_view}_{st.session_state.get('locate_nonce', 0)}_{st.session_state.get('map_epoch', 0)}",
    )
    clicked = (map_state or {}).get("last_object_clicked")
    current_tooltip = (map_state or {}).get("last_object_clicked_tooltip")
    click_sig = (
        (round(clicked["lat"], 6), round(clicked["lng"], 6), current_tooltip)
        if clicked else None
    )
    if click_sig and click_sig != st.session_state.get("_last_map_click"):
        clicked_id = None
        # Prefer the marker whose coordinates match the click (nearest village);
        # fall back to the tooltip text.
        d2 = (filtered["latitude"] - clicked["lat"]) ** 2 + (filtered["longitude"] - clicked["lng"]) ** 2
        if len(d2) and d2.min() < 1e-6:
            clicked_id = filtered.loc[d2.idxmin(), "community_id"]
        else:
            clicked_id = tooltip_to_id.get(current_tooltip)
        st.session_state["_last_map_click"] = click_sig
        if clicked_id and clicked_id != st.session_state.get("picked_card_id"):
            st.session_state["picked_card_id"] = clicked_id
            st.rerun()  # rebuild the map centred on the new selection
    if click_sig:
        st.session_state["_last_map_click"] = click_sig


def build_stats(v: pd.Series) -> list[tuple[str, object]]:
    """(label, value) pairs shown in the detail view and the summary download."""
    pop = v.get("pop_census_2021")
    stats = [
        ("Nearest tower", f"{v['km_nearest_tower']:.2f} km"),
        ("Carriers there", v["nearest_tower_carriers"]),
        ("Networks there", v["nearest_tower_networks"]),
        ("Spectrum depth", f"{v['nearest_tower_spectrum_depth_khz']} kHz"),
        ("Towers within 10km", v["n_towers_10km"]),
        ("Networks within 10km", v["n_networks_10km"]),
        ("Nearest built MBSP", f"{v['km_nearest_built_mbsp']:.1f} km"),
        ("Nearest unbuilt MBSP", f"{v['km_nearest_unbuilt_mbsp']:.1f} km ({v['nearest_unbuilt_mbsp_round']})"),
        ("RICT sites within 2km", f"{v['n_rict_sites']}" + (f" · {v['rict_site_type']}" if pd.notna(v.get("rict_site_type")) else "")),
        ("NBN footprint", "fixed-line" if v["in_nbn_fixed_line"] else ("fixed-wireless" if v["in_nbn_fixed_wireless"] else "none")),
        ("SA1 population (2021)", f"{int(pop):,}" if pd.notna(pop) else "—"),
        ("Median household income", f"${v['median_hh_income_weekly']:.0f}/wk" if pd.notna(v.get("median_hh_income_weekly")) else "—"),
    ]
    if HAS_SERVICES:
        stats += [
            ("Nearest school", f"{v['km_nearest_school']:.1f} km" + (f" · {v['nearest_school_name']}" if pd.notna(v.get("nearest_school_name")) else "")),
            ("Nearest medical", f"{v['km_nearest_medical']:.1f} km" + (f" · {v['nearest_medical_name']}" if pd.notna(v.get("nearest_medical_name")) else "")),
            ("Nearest emergency", f"{v['km_nearest_emergency']:.1f} km" + (f" · {v['nearest_emergency_name']}" if pd.notna(v.get("nearest_emergency_name")) else "")),
            ("Schools within 10km", int(v["n_schools_10km"])),
            ("Medical within 10km", int(v["n_medical_10km"])),
            ("Emergency within 10km", int(v["n_emergency_10km"])),
        ]
    return stats


def community_summary(v: pd.Series) -> str:
    lines = [f"{v['community_name']} — {v['tier_name']}", "", str(v["reason"]), ""]
    lines += [f"{label}: {val}" for label, val in build_stats(v)]
    lines += [
        "",
        "Population is the whole SA1's 2021 Census count, not a per-village figure.",
        "Distances are straight-line — triage data, not a coverage guarantee.",
        "Source: NT Deadzone Explorer (Team ASTRA).",
    ]
    return "\n".join(lines)


def render_detail(v: pd.Series, cols: int = 4) -> None:
    """Full reasoning + raw stats for one community. Shared by the points
    list and the lookup section below so both show identical detail."""
    name_col, locate_col = st.columns([3, 2], vertical_alignment="center")
    name_col.markdown(f"#### {v['community_name']}")
    if locate_col.button("Locate", key="locate_btn", icon=":material/my_location:", width="stretch"):
        # New map key => the map re-centres on this community even after panning/zooming away.
        st.session_state["locate_nonce"] = st.session_state.get("locate_nonce", 0) + 1
        st.rerun()
    st.markdown(
        f"<span style='background:{v['tier_color']}22; color:{v['tier_color']}; "
        f"padding:4px 12px; border-radius:16px;'>{v['tier_name']}</span>",
        unsafe_allow_html=True,
    )
    st.write(f"**Why this category:** {v['reason']}")

    pop = v.get("pop_census_2021")
    if pd.notna(pop):
        n_villages_sa1 = v.get("n_villages")
        shared_note = (
            f" — shared with {int(n_villages_sa1) - 1} other BushTel "
            f"communit{'y' if n_villages_sa1 == 2 else 'ies'} in this SA1"
            if pd.notna(n_villages_sa1) and n_villages_sa1 > 1 else ""
        )
        suppressed_note = (
            " (ABS-suppressed: fewer than 5 people counted)"
            if v.get("census_pop_suppressed") else ""
        )
        st.write(
            f"**Premises/population benefited:** {int(pop):,} people, 2021 Census "
            f"— this is the whole **SA1's** population, not a per-village count"
            f"{shared_note}{suppressed_note}. The Census only counts population at "
            f"SA1 level, so there's no real per-village figure to show instead."
        )

        village_names_raw = v.get("village_names")
        if pd.notna(village_names_raw) and pd.notna(n_villages_sa1) and n_villages_sa1 > 1:
            names = sorted(
                (n.strip() for n in str(village_names_raw).split(";") if n.strip()),
                key=str.upper,
            )
            st.markdown(f"**Communities in this SA1 ({len(names)})**")
            st.caption(", ".join(
                f"{n} (this one)" if n.upper() == str(v["community_name"]).upper() else n
                for n in names
            ))
    else:
        st.write("**Premises/population benefited:** no Census population record for this SA1.")

    nearby_section(v)

    stat_cols = st.columns(cols)
    stats = build_stats(v)
    for i, (label, val) in enumerate(stats):
        stat_cols[i % cols].metric(label, val)


def close_detail_sheet() -> None:
    st.session_state.pop("picked_card_id", None)
    st.session_state.pop("_last_map_click", None)
    # New map key => the map forgets its last click, so the same dot can be reopened.
    st.session_state["map_epoch"] = st.session_state.get("map_epoch", 0) + 1


@st.dialog("Community Details", width="large", dismissible=False)
def detail_drawer(v: pd.Series) -> None:
    # Not dismissible: an outside click would close it, and the map has to stay
    # clickable while it is open. Close button + Esc (see script below) close it.
    # Close sits at the far right of the title row (positioned by CSS).
    if st.button("Close", key="close_detail", icon=":material/close:", width="content"):
        close_detail_sheet()
        st.rerun()
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(v["community_name"])).strip("_")
    st.download_button(
        "Download Summary", icon=":material/download:", data=community_summary(v), file_name=f"{slug}_summary.txt",
        mime="text/plain", on_click="ignore", key="dl_summary", width="content",
    )
    if v["community_id"] not in set(filtered["community_id"]):
        st.caption("Hidden on the map by the current filters.")
    render_detail(v, cols=2)



# ---------------------------------------------------------------------------
# Table tab
# ---------------------------------------------------------------------------

TIER_ORDER = [TIERS[t]["name"] for t in TIERS]
TIER_RANGE = [TIERS[t]["color"] for t in TIERS]

with tab_table:
    if filtered.empty:
        st.info("No communities match the current filters. Select Reset Filters to start again.")
    else:
        ranked = filtered.sort_values(
            ["tier_rank", "km_nearest_tower"], ascending=[True, False]
        ).reset_index(drop=True)

        columns = {
            "community_name": "Community", "community_type": "Type", "tier_name": "Tier",
            "remoteness_name": "Remoteness", "km_nearest_tower": "Nearest tower (km)",
            "n_towers_10km": "Towers within 10 km", "n_networks_10km": "Networks within 10 km",
            "providers_text": "Providers within 10 km",
            "pop_census_2021": "SA1 population (2021)",
            "median_hh_income_weekly": "Median household income ($/wk)",
        }
        if HAS_SERVICES:
            columns.update({
                "km_nearest_school": "Nearest school (km)",
                "km_nearest_medical": "Nearest medical (km)",
                "km_nearest_emergency": "Nearest emergency (km)",
            })
        view = ranked[list(columns)].rename(columns=columns)

        export = ranked[["community_id", "latitude", "longitude", *columns, "reason"]].rename(
            columns={**columns, "reason": "Why this tier"}
        )

        hint_col, dl_col = st.columns([4, 1])
        hint_col.caption("Select a row to open its details. Select a column header to sort.")
        dl_col.download_button(
            "Download CSV", icon=":material/download:", data=export.to_csv(index=False).encode("utf-8"),
            file_name="nt_communities_filtered.csv", mime="text/csv",
            on_click="ignore", width="stretch",
        )

        dist_max = float(data["km_nearest_tower"].max())
        config = {
            "Nearest tower (km)": st.column_config.ProgressColumn(
                "Nearest tower (km)", min_value=0, max_value=dist_max, format="%.1f"),
            "SA1 population (2021)": st.column_config.ProgressColumn(
                "SA1 population (2021)", min_value=0,
                max_value=int(data["pop_census_2021"].max()), format="%d"),
            "Median household income ($/wk)": st.column_config.NumberColumn(
                "Median household income ($/wk)", format="$%d"),
        }
        for label, col in (("Nearest school (km)", "km_nearest_school"),
                           ("Nearest medical (km)", "km_nearest_medical"),
                           ("Nearest emergency (km)", "km_nearest_emergency")):
            if label in view.columns:
                config[label] = st.column_config.ProgressColumn(
                    label, min_value=0, max_value=float(data[col].max()), format="%.1f")

        # Fixed-height box + a stretching table: 520 px normally, and the table
        # fills the screen in fullscreen (a fixed table height would stay at 520).
        with st.container(key="table_box"):
            event = st.dataframe(
                view, hide_index=True, height="stretch", width="stretch",
                column_config=config, on_select="rerun", selection_mode="single-row",
                key=f"community_table_{st.session_state.get('map_epoch', 0)}",
            )
        rows = event.selection.rows if event and event.selection else []
        table_pick = int(ranked.loc[rows[0], "community_id"]) if rows else None
        if table_pick != st.session_state.get("_last_table_pick"):
            st.session_state["_last_table_pick"] = table_pick
            if table_pick is not None and table_pick != st.session_state.get("picked_card_id"):
                st.session_state["picked_card_id"] = table_pick
                st.rerun()

# ---------------------------------------------------------------------------
# Insights tab
# ---------------------------------------------------------------------------

with tab_insights:
    if filtered.empty:
        st.info("No communities match the current filters. Select Reset Filters to start again.")
    else:
        tier_colour = alt.Color(
            "tier_name:N", title="Tier",
            scale=alt.Scale(domain=TIER_ORDER, range=TIER_RANGE),
            legend=alt.Legend(orient="bottom", columns=1, labelLimit=260),
        )
        if towers is not None:
            counts = filtered["provider_class"].value_counts()
            sole = filtered[filtered["sole_network"].notna()]
            st.markdown("**Provider Dependence Within 10 km**")
            if len(sole):
                top = sole["sole_network"].value_counts()
                st.caption(
                    f"{int(top.iloc[0]):,} of {len(sole):,} single-provider communities depend on "
                    f"{top.index[0]} alone: no backup if it fails."
                )
            prov = pd.DataFrame({"Group": list(PROVIDER_STYLE), "Communities": [int(counts.get(k, 0)) for k in PROVIDER_STYLE]})
            st.altair_chart(
                alt.Chart(prov).mark_bar().encode(
                    y=alt.Y("Group:N", title=None, sort=None, axis=alt.Axis(labelLimit=260, labelOverlap=False)),
                    x=alt.X("Communities:Q"),
                    color=alt.Color("Group:N", legend=None, scale=alt.Scale(
                        domain=list(PROVIDER_STYLE), range=list(PROVIDER_STYLE.values()))),
                    tooltip=["Group:N", "Communities:Q"],
                ).properties(height=200),
                width="stretch",
            )
        left, right = st.columns(2)
        with left:
            st.markdown("**Communities by Remoteness & Tier**")
            by_remote = (
                filtered.groupby(["remoteness_name", "tier_name"]).size().reset_index(name="Communities")
            )
            st.altair_chart(
                alt.Chart(by_remote).mark_bar().encode(
                    y=alt.Y("remoteness_name:N", title=None, sort="-x", axis=alt.Axis(labelLimit=260)),
                    x=alt.X("Communities:Q", title="Communities"),
                    color=tier_colour,
                    tooltip=[alt.Tooltip("remoteness_name:N", title="Remoteness"),
                             alt.Tooltip("tier_name:N", title="Tier"),
                             alt.Tooltip("Communities:Q")],
                ).properties(height=280),
                width="stretch",
            )
        with right:
            st.markdown("**Distance to the Nearest Tower**")
            st.altair_chart(
                alt.Chart(filtered).mark_bar().encode(
                    x=alt.X("km_nearest_tower:Q", bin=alt.Bin(step=10), title="Distance (km)"),
                    y=alt.Y("count():Q", title="Communities"),
                    color=alt.Color("tier_name:N", legend=None, scale=alt.Scale(domain=TIER_ORDER, range=TIER_RANGE)),
                    tooltip=[alt.Tooltip("count():Q", title="Communities")],
                ).properties(height=280),
                width="stretch",
            )
        if HAS_SERVICES:
            st.markdown("**Communities With No Service Within 10 km**")
            gaps = pd.DataFrame({
                "Service": [SERVICE_STYLE[k]["label"] for k in ("school", "medical", "emergency")],
                "Communities": [
                    int((filtered[c] == 0).sum())
                    for c in ("n_schools_10km", "n_medical_10km", "n_emergency_10km")
                ],
            })
            st.altair_chart(
                alt.Chart(gaps).mark_bar().encode(
                    y=alt.Y("Service:N", title=None, sort=None),
                    x=alt.X("Communities:Q", scale=alt.Scale(domain=[0, max(len(filtered), 1)])),
                    color=alt.Color(
                        "Service:N", legend=None,
                        scale=alt.Scale(
                            domain=[SERVICE_STYLE[k]["label"] for k in ("school", "medical", "emergency")],
                            range=[SERVICE_STYLE[k]["color"] for k in ("school", "medical", "emergency")],
                        ),
                    ),
                    tooltip=["Service:N", "Communities:Q"],
                ).properties(height=140),
                width="stretch",
            )
            st.caption(f"Out of {len(filtered):,} communities currently shown.")

# ---------------------------------------------------------------------------
# Recommendations tab: where should new or backup coverage go first?
# ---------------------------------------------------------------------------
#
# Method (kept out of the UI on purpose; this is what the report should describe):
# - Demand = the census population of every SA1 that holds a target community.
#   An SA1's population is counted ONCE, at the centre of its target communities,
#   and never split across villages (project rule 3). BushTel populations are not used.
# - Candidate sites = the target communities themselves (a hub is a real place).
# - A hub "reaches" an SA1 when that SA1's centre is within the service radius.
#   The radii come from the NT coverage guide (small cell up to 5 km, macro cell up to
#   40 km) plus the project's own 15 km gap threshold, so they are upper bounds.
# - Primary algorithm: greedy maximum coverage. Repeatedly pick the site that reaches
#   the most people not yet reached. For this objective greedy is within (1 - 1/e) of
#   the best possible answer (Nemhauser, Wolsey & Fisher, 1978).
# - Baseline: population-weighted k-means (k-means++ start), each centre snapped to the
#   nearest real community, so the two methods are compared on the same objective.
# - Straight-line distances, triage only: not a coverage guarantee and not a costed plan.

PLAN_TARGETS = ["No tower within 10 km", "Sole provider only", "Both"]
PLAN_RADII = {"5 km · small cell": 5, "15 km · gap threshold": 15, "40 km · macro cell": 40}
PLAN_K_MAX = 30


def _hav_matrix(lat1, lon1, lat2, lon2) -> np.ndarray:
    """Great-circle km between every (lat1, lon1) row and (lat2, lon2) column."""
    p = np.pi / 180
    a = (np.sin((lat2[None, :] - lat1[:, None]) * p / 2) ** 2
         + np.cos(lat1[:, None] * p) * np.cos(lat2[None, :] * p) * np.sin((lon2[None, :] - lon1[:, None]) * p / 2) ** 2)
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def _weighted_kmeans_centres(lat, lon, w, k, seed=0, iters=30):
    rng = np.random.default_rng(seed)
    prob = (w + 1e-9) / (w + 1e-9).sum()
    first = rng.choice(len(lat), p=prob)
    centres = [(lat[first], lon[first])]
    for _ in range(1, k):  # k-means++ start, weighted by population
        dist = _hav_matrix(lat, lon, np.array([c[0] for c in centres]), np.array([c[1] for c in centres])).min(1)
        pr = (dist ** 2) * (w + 1e-9)
        pr = pr / pr.sum() if pr.sum() > 0 else prob
        nxt = rng.choice(len(lat), p=pr)
        centres.append((lat[nxt], lon[nxt]))
    c_lat, c_lon = np.array([c[0] for c in centres]), np.array([c[1] for c in centres])
    for _ in range(iters):
        assign = _hav_matrix(lat, lon, c_lat, c_lon).argmin(1)
        for j in range(k):
            m = assign == j
            if m.any():
                c_lat[j], c_lon[j] = np.average(lat[m], weights=w[m] + 1e-9), np.average(lon[m], weights=w[m] + 1e-9)
    return c_lat, c_lon


@st.cache_data
def plan_sites(target: str, radius_km: int) -> dict:
    if target == "No tower within 10 km":
        mask = data["networks_10km"].map(len) == 0
    elif target == "Sole provider only":
        mask = data["sole_network"].notna()
    else:
        mask = (data["networks_10km"].map(len) == 0) | data["sole_network"].notna()
    cand = data[mask].reset_index(drop=True)
    sa1 = cand.groupby("sa1_code").agg(
        pop=("pop_census_2021", "first"), lat=("latitude", "mean"), lon=("longitude", "mean"), n=("community_id", "size"),
    ).reset_index()
    sa1["pop"] = sa1["pop"].fillna(0)
    w = sa1["pop"].to_numpy(float)
    reach = _hav_matrix(sa1["lat"].to_numpy(), sa1["lon"].to_numpy(),
                        cand["latitude"].to_numpy(), cand["longitude"].to_numpy()) <= radius_km  # SA1 x candidate

    order, newly = [], []
    covered = np.zeros(len(sa1), bool)
    for _ in range(min(PLAN_K_MAX, len(cand))):  # greedy maximum coverage
        gain = ((reach & ~covered[:, None]) * w[:, None]).sum(0)
        j = int(gain.argmax())
        if gain[j] <= 0:
            break
        order.append(j)
        newly.append(np.flatnonzero(reach[:, j] & ~covered))
        covered |= reach[:, j]
    greedy_curve = np.cumsum([w[idx].sum() for idx in newly])

    base_curve = []
    for k in range(1, len(order) + 1):  # baseline: population-weighted k-means, snapped to real communities
        c_lat, c_lon = _weighted_kmeans_centres(sa1["lat"].to_numpy(), sa1["lon"].to_numpy(), w, k)
        snapped = _hav_matrix(c_lat, c_lon, cand["latitude"].to_numpy(), cand["longitude"].to_numpy()).argmin(1)
        base_curve.append(w[reach[:, snapped].any(1)].sum())
    return {"cand": cand, "sa1": sa1, "order": order, "newly": newly, "greedy": greedy_curve,
            "base": np.array(base_curve), "total": float(w.sum())}


with tab_plan:
    if towers is None:
        st.info("The tower file is missing, so recommendations can't be calculated.")
    else:
        c1, c2, c3 = st.columns([5, 6, 3], vertical_alignment="bottom")
        plan_target = c1.segmented_control("Who to reach", PLAN_TARGETS, default=PLAN_TARGETS[0], required=True, key="plan_target")
        plan_radius_label = c2.segmented_control("Reach of each site", list(PLAN_RADII), default="40 km · macro cell", required=True, key="plan_radius")
        plan = plan_sites(plan_target or PLAN_TARGETS[0], PLAN_RADII[plan_radius_label or "40 km · macro cell"])
        radius = PLAN_RADII[plan_radius_label or "40 km · macro cell"]
        max_sites = max(len(plan["order"]), 1)
        if st.session_state.get("plan_k", 1) > max_sites:  # a shorter list must not leave the slider out of range
            st.session_state["plan_k"] = max_sites
        sites_k = c3.slider("Sites", 1, max_sites, min(10, max_sites), key="plan_k")

        order = plan["order"][:sites_k]
        cand, sa1 = plan["cand"], plan["sa1"]
        total = plan["total"]
        reached_people = float(plan["greedy"][sites_k - 1]) if len(plan["greedy"]) else 0.0
        hub_lat, hub_lon = cand["latitude"].to_numpy()[order], cand["longitude"].to_numpy()[order]
        village_dist = _hav_matrix(cand["latitude"].to_numpy(), cand["longitude"].to_numpy(), hub_lat, hub_lon)
        village_reached = (village_dist <= radius).any(1)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("People in target areas", f"{int(total):,}")
        m2.metric(f"Reached by {sites_k} sites", f"{int(reached_people):,}")
        m3.metric("Share reached", f"{reached_people / total:.0%}" if total else "—")
        m4.metric("Communities within reach", f"{int(village_reached.sum()):,} of {len(cand):,}")

        if len(order):
            top = ", ".join(str(cand["community_name"].iloc[j]).title() for j in order[:3])
            st.markdown(
                f"**Start with {top}.** {sites_k} sites bring coverage within {radius} km of "
                f"**{int(reached_people):,} people ({reached_people / total:.0%})**."
            )

        left, right = st.columns([1, 1])
        with left:
            st.markdown("**People Reached vs Number of Sites**")
            ks = np.arange(1, len(plan["greedy"]) + 1)
            curve = pd.concat([
                pd.DataFrame({"Sites": ks, "Share": plan["greedy"] / total, "Method": "Greedy max-coverage"}),
                pd.DataFrame({"Sites": ks, "Share": plan["base"] / total, "Method": "Population-weighted k-means"}),
            ])
            line = alt.Chart(curve).mark_line(point=True).encode(
                x=alt.X("Sites:Q", scale=alt.Scale(nice=False)),
                y=alt.Y("Share:Q", axis=alt.Axis(format="%"), title="People reached"),
                color=alt.Color("Method:N", scale=alt.Scale(
                    domain=["Greedy max-coverage", "Population-weighted k-means"], range=["#009E73", "#6B6F76"]),
                    legend=alt.Legend(orient="bottom", columns=1, labelLimit=300)),
                strokeDash=alt.StrokeDash("Method:N", legend=None, scale=alt.Scale(
                    domain=["Greedy max-coverage", "Population-weighted k-means"], range=[[1, 0], [4, 4]])),
                tooltip=["Method:N", "Sites:Q", alt.Tooltip("Share:Q", format=".1%")],
            )
            rule = alt.Chart(pd.DataFrame({"Sites": [sites_k]})).mark_rule(color="#EDEDED", strokeDash=[2, 4]).encode(x="Sites:Q")
            st.altair_chart((line + rule).properties(height=300), width="stretch")
        with right:
            st.markdown("**Recommended Sites**")
            rows, cum = [], 0.0
            for rank, (j, idx) in enumerate(zip(order, plan["newly"][:sites_k]), start=1):
                new_people = float(sa1["pop"].to_numpy()[idx].sum())
                cum += new_people
                r = cand.iloc[j]
                rows.append({
                    "#": rank, "Community": str(r["community_name"]), "New people": int(new_people),
                    "Cumulative share": cum / total if total else 0.0,
                    "Communities within reach": int((village_dist[:, rank - 1] <= radius).sum()),
                    "Providers now": r["providers_text"], "Nearest tower (km)": float(r["km_nearest_tower"]),
                })
            sites_df = pd.DataFrame(rows)
            st.dataframe(
                sites_df, hide_index=True, width="stretch", height=300,
                column_config={
                    "Cumulative share": st.column_config.ProgressColumn("Cumulative share", min_value=0, max_value=1, format="percent"),
                    "New people": st.column_config.NumberColumn("New people", format="%d"),
                    "Nearest tower (km)": st.column_config.NumberColumn("Nearest tower (km)", format="%.1f"),
                },
            )
            st.download_button(
                "Download Sites", icon=":material/download:", data=sites_df.to_csv(index=False).encode("utf-8"),
                file_name="recommended_sites.csv", mime="text/csv", on_click="ignore",
            )

        # Map: target communities (reached = white, not yet reached = grey) and numbered hubs with their reach.
        plan_map = folium.Map(location=[-19.5, 133.5], zoom_start=5, tiles="OpenStreetMap", prefer_canvas=True)
        plan_map.get_root().header.add_child(folium.Element(
            "<style>.leaflet-tile-pane { filter: invert(1) hue-rotate(180deg) brightness(0.92) contrast(0.9); }</style>"
        ))
        for j in range(len(order)):
            folium.Circle([hub_lat[j], hub_lon[j]], radius=radius * 1000, color="#009E73", weight=1,
                          dash_array="4 6", fill=True, fill_color="#009E73", fill_opacity=0.06, interactive=False).add_to(plan_map)
        for i, r in cand.iterrows():
            folium.CircleMarker(
                [r["latitude"], r["longitude"]], radius=3, weight=0, fill=True, fill_opacity=0.9,
                fill_color="#EDEDED" if village_reached[i] else "#6B6F76",
                tooltip=f"{r['community_name']} · {r['providers_text']}",
            ).add_to(plan_map)
        for rank, j in enumerate(order, start=1):
            folium.Marker(
                [hub_lat[rank - 1], hub_lon[rank - 1]],
                icon=folium.DivIcon(
                    html=(f'<div style="width:26px;height:26px;border-radius:50%;background:#009E73;color:#fff;'
                          f'font:700 12px system-ui,sans-serif;display:flex;align-items:center;justify-content:center;'
                          f'border:2px solid #0A0A0A;">{rank}</div>'),
                    icon_size=(26, 26), icon_anchor=(13, 13)),
                tooltip=f"{rank} · {cand['community_name'].iloc[j]}",
                z_index_offset=1000,
            ).add_to(plan_map)
        st_folium(plan_map, height=520, use_container_width=True, returned_objects=[],
                  key=f"plan_map_{plan_target}_{radius}_{sites_k}")

# Data caveats (kept out of the UI on purpose):
# - Triage data, not a coverage guarantee. Every km figure is straight-line, not
#   drive time.
# - A tower licence is permission to transmit, not proof a site is on air.
# - Services distances (school/medical/emergency) are haversine on WGS84, not the
#   projected-CRS method used for towers/MBSP: close enough for triage, slightly
#   less precise.
# - 9 of 273 schools have no coordinate (4 outstation schools with a literal
#   "tba" address, 5 more unresolved) and are excluded from the school distance
#   calc, not guessed.

# ---------------------------------------------------------------------------
# Detail drawer + community deep link (filters/colour sync via bind="query-params")
# ---------------------------------------------------------------------------

def _palette_label(cid: int) -> str:
    r = palette_rows[cid]
    aliases = str(r["community_aliases"])
    names = [] if aliases.startswith("No aliases") or aliases == "nan" else [a.strip().title() for a in aliases.split(",") if a.strip()]
    also = f" · also {', '.join(names[:2])}" + ("…" if len(names) > 2 else "") if names else ""
    return f"{r['community_name']} · {r['tier_name']} · {r['community_type']}{also}"


palette_rows = data.set_index("community_id").to_dict("index")


@st.dialog("Search Communities", width="medium")
def search_palette() -> None:
    # The selectbox filters as you type (client-side), matching name, tier, type
    # and known aliases. Picking a result closes this and opens its drawer.
    choice = st.selectbox(
        "Community", options=sorted(palette_rows, key=lambda c: palette_rows[c]["community_name"]),
        index=None, format_func=_palette_label, key="palette_pick",
        placeholder="Type a name, tier or type…", label_visibility="collapsed",
    )
    st.caption("Searches all 792 communities, whatever the filters are set to.")
    if choice is not None:
        st.session_state["picked_card_id"] = int(choice)
        st.session_state.pop("palette_pick", None)
        st.rerun()


picked_card_id = st.session_state.get("picked_card_id")
picked = data[data["community_id"] == picked_card_id]
if open_palette:
    search_palette()  # only one dialog can open per run, so it takes priority
elif not picked.empty:
    detail_drawer(picked.iloc[0])

# Drag-to-resize handle for the drawer (width is remembered in localStorage).
with st.container(key="scripts"):
    st.iframe(
        """
        <script>
        const doc = window.parent.document;
        const KEY = 'detailSheetWidth';
        try { const w = localStorage.getItem(KEY); if (w) doc.documentElement.style.setProperty('--detail-w', w + 'px'); } catch (e) {}
        function focusPalette() {
          const pal = doc.querySelector('[data-testid="stDialog"] [role="dialog"]:not(:has(.st-key-close_detail))');
          if (!pal) return;
          const input = pal.querySelector('input');
          if (input && input.dataset.astraFocused !== '1') { input.dataset.astraFocused = '1'; input.focus(); }
        }
        // Stretch the map and the table so the active tab ends at the bottom of the window.
        let fitQueued = false;
        function fitHeights() {
          fitQueued = false;
          const room = (el) => Math.max(320, window.parent.innerHeight - el.getBoundingClientRect().top - 24);
          const map = doc.querySelector('iframe[title*="folium"]');
          if (map && map.offsetParent) map.style.setProperty('height', room(map) + 'px', 'important');
          const table = doc.querySelector('.st-key-table_box');
          if (table && table.offsetParent) {
            const h = room(table) + 'px';
            table.style.setProperty('height', h, 'important'); table.style.setProperty('flex-basis', h, 'important');
          }
        }
        function queueFit() { if (!fitQueued) { fitQueued = true; requestAnimationFrame(fitHeights); } }
        doc.addEventListener('click', () => setTimeout(queueFit, 60));
        window.parent.addEventListener('resize', queueFit);
        [300, 1200, 3000].forEach((ms) => setTimeout(queueFit, ms));
        function attach() {
          queueFit();
          focusPalette();
          const dlg = doc.querySelector('[data-testid="stDialog"] [role="dialog"]:has(.st-key-close_detail)');
          if (!dlg || dlg.querySelector('.sheet-resize-handle')) return;
          const h = doc.createElement('div');
          h.className = 'sheet-resize-handle';
          h.setAttribute('role', 'separator'); h.setAttribute('aria-label', 'Resize panel');
          dlg.appendChild(h);
          h.addEventListener('pointerdown', (e) => {
            e.preventDefault(); h.setPointerCapture(e.pointerId); h.classList.add('dragging');
            const move = (ev) => {
              const w = Math.min(Math.max(window.parent.innerWidth - ev.clientX, 340), window.parent.innerWidth * 0.9);
              doc.documentElement.style.setProperty('--detail-w', w + 'px');
            };
            const up = () => {
              h.classList.remove('dragging'); h.removeEventListener('pointermove', move); h.removeEventListener('pointerup', up);
              try { localStorage.setItem(KEY, String(parseInt(getComputedStyle(dlg).width))); } catch (e) {}
            };
            h.addEventListener('pointermove', move); h.addEventListener('pointerup', up);
          });
        }
        // Streamlit marks the page inert while a dialog is open; lift it so the map,
        // tabs and filters stay usable next to the drawer.
        const lift = () => {
          if (!doc.querySelector('.st-key-close_detail')) return;  // only for the drawer
          let e = doc.querySelector('[data-testid="stApp"]');
          while (e && e !== doc.body) { if (e.inert) e.inert = false; e = e.parentElement; }
        };
        new MutationObserver(lift).observe(doc.body, { attributes: true, subtree: true, attributeFilter: ['inert'] });
        lift();
        doc.documentElement.dataset.mac = /Mac|iPhone|iPad/.test(window.parent.navigator.platform) ? '1' : '0';
        if (!window.parent.__astraKeys) {
          window.parent.__astraKeys = true;
          doc.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
              const btn = doc.querySelector('.st-key-open_search button');
              if (btn) { e.preventDefault(); btn.click(); }
            }
          });
        }
        doc.addEventListener('keydown', (e) => {
          if (e.key !== 'Escape') return;
          const btn = [...doc.querySelectorAll('[role="dialog"] button')].find(b => b.innerText.includes('Close'));
          if (btn) btn.click();
        });
        new MutationObserver(attach).observe(doc.body, { childList: true, subtree: true });
        attach();
        </script>
        """,
        height=1,
    )

if "_url_boot" not in st.session_state:
    st.session_state["_url_boot"] = True
    linked = st.query_params.get("community")
    if linked and linked.isdigit() and int(linked) in set(data["community_id"]):
        st.session_state["picked_card_id"] = int(linked)
        st.rerun()

_picked = st.session_state.get("picked_card_id")
if _picked is not None:
    if st.query_params.get("community") != str(_picked):
        st.query_params["community"] = str(_picked)
elif "community" in st.query_params:
    del st.query_params["community"]
