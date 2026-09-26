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

import altair as alt
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="NT Deadzone Explorer — Services", layout="wide", page_icon="📡")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 3.75rem; padding-bottom: 3rem; }

    /* Title inside Streamlit's top bar (next to Deploy / menu). */
    [data-testid="stHeader"] {
        background: #0E1117; border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stHeader"]::before {
        content: "NT Deadzone Explorer   ·   Remote Connectivity | CDU IT Code Fair, Data Innovation Challenge 2026";
        position: absolute; left: 5rem; top: 50%; transform: translateY(-50%);
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
    .block-container { padding-right: 372px !important; }
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
        .block-container { padding-right: 1rem !important; }
    }
    .st-key-table_box { flex: 0 0 520px; height: 520px; }
    .st-key-table_box [data-testid="stElementContainer"],
    .st-key-table_box [data-testid="stFullScreenFrame"],
    .st-key-table_box [data-testid="stDataFrame"] { height: 100%; }
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
    [data-baseweb="select"] > div:focus-within, button[role="tab"]:focus-visible {
        outline: 2px solid #5B8DEF; outline-offset: 2px;
    }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div { border-radius: 8px; }
    button[role="tab"] { font-weight: 500; }
    button[role="tab"][aria-selected="true"] { color: #EDEDED; }
    [data-baseweb="tab-highlight"] { background: #EDEDED; }
    [data-testid="stDialog"] [role="dialog"]:not(:has(.st-key-close_detail)) {
        background: #0A0A0A; border: 1px solid rgba(255,255,255,0.14); border-radius: 12px; box-shadow: none;
    }
    .st-key-open_search { width: 100%; }
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
        text-align: right; font-size: 0.85rem; font-weight: 400;
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

    .info-card {
        background: #0A0A0A; border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px; padding: 14px 16px; font-size: 0.82rem;
        color: rgba(255,255,255,0.75); line-height: 1.5;
    }
    .info-card .info-card-title { font-weight: 700; color: #E6E8EB; margin-bottom: 8px; font-size: 0.85rem; }
    .info-card ul { margin: 0 0 10px 0; padding-left: 4px; list-style: none; }
    .info-card li { margin-bottom: 5px; }
    .info-card .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px; }
    .info-card p { margin: 8px 0 0 0; }
    .info-card code { background: rgba(255,255,255,0.08); padding: 1px 5px; border-radius: 4px; }

    .footnote {
        background: #0A0A0A; border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px; padding: 10px 16px; font-size: 0.78rem;
        color: rgba(255,255,255,0.55);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_data(path: str = "village_gap_with_services.csv") -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"sa1_code": str})

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
    df = pd.read_csv(path, dtype={"sa1_code": str})
    return df[[
        "sa1_code", "pop_census_2021", "census_pop_suppressed",
        "median_hh_income_weekly", "avg_household_size", "n_villages",
        "village_names",
    ]]


@st.cache_data
def load_services(path: str = "services_sites_combined.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.dropna(subset=["latitude", "longitude"])


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
TIER_ICON = {"beyond": "🔴", "spof": "🟠", "single_net": "🟡", "redundant": "🔵"}

SERVICE_STYLE = {
    "school":    {"label": "School",    "color": "#59A14F", "icon": "🎓"},
    "medical":   {"label": "Medical",   "color": "#E45756", "icon": "🩺"},
    "emergency": {"label": "Emergency", "color": "#4C78A8", "icon": "🚨"},
}


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

data = prepare(raw)
if sa1_report is not None:
    data = data.merge(sa1_report, on="sa1_code", how="left")

HAS_SERVICES = all(c in data.columns for c in (
    "km_nearest_school", "km_nearest_medical", "km_nearest_emergency"
))

# ---------------------------------------------------------------------------
# Map colour modes
# ---------------------------------------------------------------------------

COLOR_MODES = [
    "Tier", "Tower distance", "Population",
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


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

GROUP_NAME = "Team ASTRA" 

st.sidebar.markdown(
    f'<div class="group-name"><span class="group-label">Team</span>{GROUP_NAME}</div>',
    unsafe_allow_html=True,
)
st.sidebar.header("Filters")

FILTER_KEYS = [
    "tier_filter", "type_filter", "remote_filter", "min_tower_filter",
    "no_rict_filter", "guide_covered_filter", "in_nbn_filter",
    "no_school_filter", "no_medical_filter", "no_emergency_filter",
    "show_services_filter",
]
FILTER_DEFAULTS = {
    "tier_filter": [], "type_filter": [], "remote_filter": [],
    "min_tower_filter": 0,
    "no_rict_filter": False, "guide_covered_filter": False, "in_nbn_filter": False,
    "no_school_filter": False, "no_medical_filter": False, "no_emergency_filter": False,
    "show_services_filter": False,
    "color_by": "Tier",
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


st.sidebar.button("↺ Reset filters", width="stretch", on_click=reset_filters)

with st.sidebar:
    # Filters, colour mode and the selected community all live in the address bar,
    # so this copies a link that reopens the exact same view.
    st.iframe(
        """
        <style>
          body { margin: 0; font-family: Inter, sans-serif; }
          button { width: 100%; height: 36px; cursor: pointer; border-radius: 8px;
                   background: transparent; color: #E6E8EB; font: 500 13px Inter, sans-serif;
                   border: 1px solid rgba(255,255,255,0.20); }
          button:hover { border-color: rgba(255,255,255,0.45); }
          button:focus-visible { outline: 2px solid #5B8DEF; outline-offset: 2px; }
        </style>
        <button id="copy" type="button">Copy Link to This View</button>
        <script>
          const btn = document.getElementById('copy');
          btn.addEventListener('click', () => {
            const t = document.createElement('textarea');
            t.value = window.parent.location.href;
            document.body.appendChild(t); t.select();
            let ok = false; try { ok = document.execCommand('copy'); } catch (e) {}
            t.remove();
            btn.textContent = ok ? 'Link Copied' : 'Copy Failed: Use the Address Bar';
            setTimeout(() => { btn.textContent = 'Copy Link to This View'; }, 2000);
          });
        </script>
        """,
        height=44,
    )

tier_filter = st.sidebar.multiselect(
    "Priority tier",
    options=list(TIERS.keys()),
    default=[],
    placeholder="All",
    format_func=lambda t: TIERS[t]["name"],
    key="tier_filter", bind="query-params",
)

type_options = sorted(data["community_type"].unique())
type_filter = st.sidebar.multiselect(
    "Community type", options=type_options, default=[], placeholder="All", key="type_filter",
    bind="query-params",
)

remote_options = sorted(data["remoteness_name"].unique())
remote_filter = st.sidebar.multiselect(
    "Remoteness", options=remote_options, default=[], placeholder="All", key="remote_filter",
    bind="query-params",
)

min_tower = st.sidebar.slider(
    "Nearest tower, at least (km)", 0, 150, 0, key="min_tower_filter",
    bind="query-params",
)

st.sidebar.caption("\"All\" means no filter. Pick options to narrow the list.")

with st.sidebar.expander("More filters"):
    no_rict = st.checkbox("No RICT public access", key="no_rict_filter", bind="query-params")
    guide_covered = st.checkbox("Guide claims coverage", key="guide_covered_filter", bind="query-params")
    in_nbn = st.checkbox("Inside NBN footprint", key="in_nbn_filter", bind="query-params")
    no_school = st.checkbox("No school within 10km", key="no_school_filter", bind="query-params", disabled=not HAS_SERVICES)
    no_medical = st.checkbox("No medical facility within 10km", key="no_medical_filter", bind="query-params", disabled=not HAS_SERVICES)
    no_emergency = st.checkbox("No emergency facility within 10km", key="no_emergency_filter", bind="query-params", disabled=not HAS_SERVICES)

show_services_layer = st.sidebar.checkbox(
    "Show service sites on map (school/medical/emergency)",
    value=False, key="show_services_filter", bind="query-params", disabled=services is None,
)

TIER_DESC = {
    "beyond": "&gt;15 km, no guide claim (GAP_KM)",
    "spof": "within 15 km, 0 towers in 10 km buffer (BUFFER_KM)",
    "single_net": "towers nearby, 1 network",
    "redundant": "2+ networks within 10 km",
}

st.sidebar.divider()
tier_legend_items = "".join(
    f'<li><span class="dot" style="background:{TIERS[tid]["color"]}"></span>'
    f'<b>{TIERS[tid]["name"]}</b> — {TIER_DESC[tid]}</li>'
    for tid in TIERS
)
st.sidebar.markdown(
    f"""
    <div class="info-card">
        <div class="info-card-title">How communities are classified</div>
        <ul>{tier_legend_items}</ul>
        <p>Mobile-tower tier only. <b>Schools/medical/emergency distances</b> are
        shown per community and filterable above, but don't change the tier —
        they come from a separate notebook (<code>07_services_gap.ipynb</code>)
        added after the tower classification was locked in, and mixing the two
        into one score would need a judgement call this app doesn't make for you.</p>
    </div>
    """,
    unsafe_allow_html=True,
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
search_col, count_col = st.columns([1, 1], vertical_alignment="center")
open_palette = search_col.button("Search Communities…", key="open_search")
count_col.markdown(
    f'<div class="result-count">{len(filtered):,} of {len(data):,} communities shown</div>',
    unsafe_allow_html=True,
)

tab_map, tab_table, tab_insights = st.tabs(["Map", "Table", "Insights"])

# ---------------------------------------------------------------------------
# Map + points list
# ---------------------------------------------------------------------------

map_col = tab_map

with map_col:
    color_mode = st.segmented_control(
        "Colour dots by", COLOR_MODES, default="Tier", required=True,
        key="color_by", bind="query-params",
    ) or "Tier"
    dot_color, dot_metric, legend_items = colour_dots(filtered, color_mode)
    legend_html = "".join(
        f'<span class="item"><span class="swatch" style="background:{c}"></span>{label}</span>'
        for c, label in legend_items
    )
    if show_services_layer and services is not None:
        legend_html += "".join(
            f'<span class="item"><span class="swatch" style="background:{s["color"]}"></span>{s["icon"]} {s["label"]}</span>'
            for s in SERVICE_STYLE.values()
        )
    st.markdown(f'<div class="map-legend">{legend_html}</div>', unsafe_allow_html=True)

    m = folium.Map(
        location=[-19.5, 133.5], zoom_start=5, tiles="OpenStreetMap", prefer_canvas=True
    )
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
                    tooltip=f"{style['icon']} {s['name']}",
                ).add_to(m)

    map_state = st_folium(
        m, height=560, use_container_width=True,
        returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
        # Key changes with the filtered set so the map redraws when filters change.
        key=f"deadzone_map_{pd.util.hash_pandas_object(filtered['community_id'], index=False).sum()}_{show_services_layer}_{color_mode}_{st.session_state.get('map_epoch', 0)}",
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
        if clicked_id:
            st.session_state["picked_card_id"] = clicked_id
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
    st.markdown(f"#### {v['community_name']}")
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
    if st.button("✕ Close", key="close_detail", width="content"):
        close_detail_sheet()
        st.rerun()
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(v["community_name"])).strip("_")
    st.download_button(
        "Download Summary", data=community_summary(v), file_name=f"{slug}_summary.txt",
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
            "Download CSV", data=export.to_csv(index=False).encode("utf-8"),
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
            if table_pick is not None:
                st.session_state["picked_card_id"] = table_pick
            st.session_state["_last_table_pick"] = table_pick

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

st.divider()
st.markdown(
    """
    <div class="footnote">
    Triage data, not a coverage guarantee. Every km figure is straight-line,
    not drive time. A tower licence is permission to transmit, not proof a
    site is on air. Services distances (school/medical/emergency) are
    haversine on WGS84, not the projected-CRS method used for towers/MBSP —
    close enough for triage, slightly less precise. 9 of 273 schools have no
    coordinate (4 outstation schools with a literal "tba" address, 5 more
    unresolved) and are excluded from the school distance calc, not guessed.
    </div>
    """,
    unsafe_allow_html=True,
)

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
    function attach() {
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
