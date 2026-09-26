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
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; }

    .hero-eyebrow {
        letter-spacing: 0.12em; text-transform: uppercase; font-size: 0.72rem;
        font-weight: 700; color: #5B8DEF; margin-bottom: 2px;
    }

    .stat-tile {
        background: #161A21; border: 1px solid rgba(255,255,255,0.08);
        border-left: 4px solid var(--tier-color, #5B8DEF);
        border-radius: 12px; padding: 14px 18px; height: 100%;
    }
    .stat-tile .stat-label {
        font-size: 0.8rem; color: rgba(255,255,255,0.62); font-weight: 500;
        display: flex; align-items: center; gap: 6px; margin-bottom: 6px;
    }
    .stat-tile .stat-value { font-size: 1.9rem; font-weight: 800; line-height: 1; color: #E6E8EB; }

    .map-legend { display: flex; gap: 18px; flex-wrap: wrap; margin: 10px 0 2px 0; }
    .map-legend .item { display: flex; align-items: center; gap: 7px; font-size: 0.8rem; color: rgba(255,255,255,0.68); }
    .map-legend .swatch { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex-shrink: 0; }

    .info-card {
        background: #161A21; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px; padding: 14px 16px; font-size: 0.82rem;
        color: rgba(255,255,255,0.75); line-height: 1.5;
    }
    .info-card .info-card-title { font-weight: 700; color: #E6E8EB; margin-bottom: 8px; font-size: 0.85rem; }
    .info-card ul { margin: 0 0 10px 0; padding-left: 4px; list-style: none; }
    .info-card li { margin-bottom: 5px; }
    .info-card .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px; }
    .info-card p { margin: 8px 0 0 0; }
    .info-card code { background: rgba(255,255,255,0.08); padding: 1px 5px; border-radius: 4px; }

    .footnote {
        background: #161A21; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px; padding: 10px 16px; font-size: 0.78rem;
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
# Header
# ---------------------------------------------------------------------------

st.markdown('<div class="hero-eyebrow">📡 NT Deadzone Explorer · Services Edition</div>', unsafe_allow_html=True)
st.markdown("## 792 communities, mobile coverage + schools/medical/emergency reach")
st.caption(
    "Tower tiers use only GAP_KM = 15 and BUFFER_KM = 10, already defined in the "
    "source notebook. Services distances (07_services_gap.ipynb) are new — shown "
    "for context, not folded into the tier."
)

st.write("")
kpi_cols = st.columns(4)
for col, tier_id in zip(kpi_cols, TIERS):
    count = int((data["tier_id"] == tier_id).sum())
    tier = TIERS[tier_id]
    with col:
        st.markdown(
            f"""
            <div class="stat-tile" style="--tier-color:{tier['color']};">
                <div class="stat-label">{TIER_ICON[tier_id]} {tier['name']}</div>
                <div class="stat-value">{count:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if HAS_SERVICES:
    st.write("")
    svc_cols = st.columns(3)
    svc_kpis = [
        ("school", "🎓 No school within 10km"),
        ("medical", "🩺 No medical facility within 10km"),
        ("emergency", "🚨 No emergency facility within 10km"),
    ]
    for col, (prefix, label) in zip(svc_cols, svc_kpis):
        n_col = "n_schools_10km" if prefix == "school" else f"n_{prefix}_10km"
        count = int((data[n_col] == 0).sum())
        with col:
            st.markdown(
                f"""
                <div class="stat-tile" style="--tier-color:{SERVICE_STYLE[prefix]['color']};">
                    <div class="stat-label">{SERVICE_STYLE[prefix]['icon']} {label}</div>
                    <div class="stat-value">{count:,} <span style="font-size:0.95rem; font-weight:500; color:rgba(255,255,255,0.5);">/ 792</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.divider()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.header("Filters")

FILTER_KEYS = [
    "tier_filter", "type_filter", "remote_filter", "min_tower_filter",
    "no_rict_filter", "guide_covered_filter", "in_nbn_filter",
    "no_school_filter", "no_medical_filter", "no_emergency_filter",
    "show_services_filter",
]
if st.sidebar.button("↺ Reset filters", use_container_width=True):
    for k in FILTER_KEYS:
        st.session_state.pop(k, None)
    st.rerun()

tier_filter = st.sidebar.multiselect(
    "Priority tier",
    options=list(TIERS.keys()),
    default=list(TIERS.keys()),
    format_func=lambda t: TIERS[t]["name"],
    key="tier_filter",
)

type_options = sorted(data["community_type"].unique())
type_filter = st.sidebar.multiselect(
    "Community type", options=type_options, default=type_options, key="type_filter"
)

remote_options = sorted(data["remoteness_name"].unique())
remote_filter = st.sidebar.multiselect(
    "Remoteness", options=remote_options, default=remote_options, key="remote_filter"
)

min_tower = st.sidebar.slider(
    "Nearest tower, at least (km)", 0, 150, 0, key="min_tower_filter"
)

st.sidebar.caption("Clearing a filter shows every option for that category, not zero.")

with st.sidebar.expander("More filters"):
    no_rict = st.checkbox("No RICT public access", key="no_rict_filter")
    guide_covered = st.checkbox("Guide claims coverage", key="guide_covered_filter")
    in_nbn = st.checkbox("Inside NBN footprint", key="in_nbn_filter")
    no_school = st.checkbox("No school within 10km", key="no_school_filter", disabled=not HAS_SERVICES)
    no_medical = st.checkbox("No medical facility within 10km", key="no_medical_filter", disabled=not HAS_SERVICES)
    no_emergency = st.checkbox("No emergency facility within 10km", key="no_emergency_filter", disabled=not HAS_SERVICES)

show_services_layer = st.sidebar.checkbox(
    "Show service sites on map (school/medical/emergency)",
    value=False, key="show_services_filter", disabled=services is None,
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
st.write(f"**{len(filtered)}** of {len(data)} communities shown")

# ---------------------------------------------------------------------------
# Map + points list
# ---------------------------------------------------------------------------

map_col, points_col = st.columns([2, 1])

with map_col:
    st.subheader("Map")
    st.caption("Click a dot — its details appear on the right.")
    legend_html = "".join(
        f'<span class="item"><span class="swatch" style="background:{t["color"]}"></span>{t["name"]}</span>'
        for t in TIERS.values()
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
    for _, v in filtered.iterrows():
        tooltip_text = (
            f"{v['community_name']} · {v['tier_name']} · "
            f"{v['km_nearest_tower']:.1f} km"
        )
        tooltip_to_id[tooltip_text] = v["community_id"]
        folium.CircleMarker(
            location=[v["latitude"], v["longitude"]],
            radius=6,
            color="#0E1117",
            weight=1,
            fill=True,
            fill_color=v["tier_color"],
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
        key="deadzone_map",
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
    for i, (label, val) in enumerate(stats):
        stat_cols[i % cols].metric(label, val)


with points_col:
    picked_card_id = st.session_state.get("picked_card_id")
    picked = data[data["community_id"] == picked_card_id]
    if not picked.empty:
        render_detail(picked.iloc[0], cols=2)

# ---------------------------------------------------------------------------
# Detail expander for a selected community
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Look up a community")

names_sorted = filtered["community_name"].sort_values().tolist()
if names_sorted:
    if st.session_state.get("lookup_pick") not in names_sorted:
        st.session_state["lookup_pick"] = names_sorted[0]

    pick = st.selectbox(
        "Choose a community for its full reasoning and raw stats",
        options=names_sorted,
        key="lookup_pick",
    )
    v = filtered[filtered["community_name"] == pick].iloc[0]
    render_detail(v, cols=4)
else:
    st.caption("No communities match the current filters.")

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
