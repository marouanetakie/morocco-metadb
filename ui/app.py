# -*- coding: utf-8 -*-
"""
MoroccoMetaDB — Professional Scientific Platform
Streamlit web application for the North African Medicinal Plant Database.
"""
import io
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

from db.schema import init_db, DB_PATH
from db.crud import (
    get_all_plants, search_plants,
    get_compounds, search_compounds,
    get_bioactivities, search_bioactivities,
    get_docking_results,
    get_ethnobotany, get_references, get_stats,
    add_plant, add_compound, add_bioactivity, add_ethnobotany,
)

# RDKit optional
try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

# fpdf2
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoroccoMetaDB",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* Main area */
.stApp { background-color: #f4f9f6; }
.main .block-container { padding-top: 1.5rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0a2d1e !important;
    border-right: 2px solid #1a5c3a;
}
section[data-testid="stSidebar"] * { color: #c8e6c9 !important; }
section[data-testid="stSidebar"] a { color: #69d9a0 !important; }

/* Headings */
h1, h2, h3 { color: #0a2d1e !important; font-weight: 600 !important; }
h4, h5, h6 { color: #1a4a35 !important; }
p, li, label { color: #1a2e22; }

/* Metric cards */
div[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 1px solid #d4e8dd;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(10,45,30,0.08);
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0a2d1e !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #2d9e6b !important;
    font-weight: 500 !important;
}

/* Cards */
.card {
    background: #ffffff;
    border: 1px solid #d4e8dd;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(10,45,30,0.06);
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #0a2d1e 0%, #1a5c3a 60%, #2d9e6b 100%);
    border-radius: 16px;
    padding: 36px 48px;
    margin-bottom: 28px;
    color: white !important;
}
.hero-banner h1 {
    color: #ffffff !important;
    font-size: 2.6rem !important;
    font-weight: 700 !important;
    margin: 0 0 10px 0;
    letter-spacing: -0.5px;
}
.hero-banner .tagline {
    color: #a8d5b5;
    font-size: 1.1rem;
    margin: 0 0 6px 0;
}
.hero-banner .stats-line {
    color: #69d9a0;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Buttons */
.stButton > button {
    background-color: #2d9e6b !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 22px !important;
    transition: background-color 0.2s !important;
}
.stButton > button:hover { background-color: #0a2d1e !important; }
.stDownloadButton > button {
    background-color: #f4f9f6 !important;
    color: #0a2d1e !important;
    border: 1.5px solid #2d9e6b !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border: 1.5px solid #d4e8dd !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    color: #1a2e22 !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    border: 1.5px solid #d4e8dd !important;
    border-radius: 8px !important;
    background: #ffffff !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 2px solid #d4e8dd;
}
.stTabs [data-baseweb="tab"] {
    color: #4a7a5c !important;
    font-weight: 500;
    border-radius: 8px 8px 0 0;
}
.stTabs [aria-selected="true"] {
    color: #0a2d1e !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #2d9e6b !important;
    background: #f4f9f6 !important;
}

/* Expanders */
details {
    background: #ffffff !important;
    border: 1px solid #d4e8dd !important;
    border-radius: 10px !important;
    padding: 4px 2px !important;
    margin-bottom: 8px !important;
}
details summary { color: #0a2d1e !important; font-style: italic; font-weight: 500; }

/* Sidebar footer */
.sidebar-footer {
    position: fixed;
    bottom: 16px;
    font-size: 0.78rem;
    color: #a8d5b5 !important;
    line-height: 1.7;
}
.sidebar-stats {
    background: rgba(45,158,107,0.2);
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
    font-size: 0.85rem;
    color: #69d9a0 !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Init DB & pending_submissions table ───────────────────────────────────
init_db()

def _init_submissions_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_submissions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_type  TEXT,
            data_json        TEXT,
            submitted_at     TEXT DEFAULT (datetime('now')),
            status           TEXT DEFAULT 'pending',
            submitter_email  TEXT
        )
    """)
    conn.commit()
    conn.close()

_init_submissions_table()

# ── Cached DB helpers ─────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cached_stats():
    try:
        return get_stats()
    except Exception as e:
        st.error(f"Stats error: {e}")
        return {"totals": {}, "by_country": [], "by_class": [], "by_assay": [],
                "by_family": [], "most_active_plants": []}

@st.cache_data(ttl=300)
def cached_all_plants():
    try:
        return get_all_plants()
    except Exception as e:
        st.error(f"Plants error: {e}")
        return []

@st.cache_data(ttl=300)
def cached_all_compounds():
    try:
        return search_compounds()
    except Exception as e:
        st.error(f"Compounds error: {e}")
        return []

@st.cache_data(ttl=300)
def cached_all_bioactivities():
    try:
        return search_bioactivities()
    except Exception as e:
        st.error(f"Bioactivities error: {e}")
        return []

@st.cache_data(ttl=300)
def cached_top_cytotoxic(n=10):
    try:
        bio = search_bioactivities(assay_type="MTT")
        df = pd.DataFrame(bio) if bio else pd.DataFrame()
        if df.empty or "value" not in df.columns:
            return pd.DataFrame()
        df = df[df["value"].notna()].sort_values("value")
        cols = [c for c in ["scientific_name", "value", "unit", "value_type"] if c in df.columns]
        return df[cols].head(n).rename(columns={
            "scientific_name": "Plant", "value": "MTT IC50",
            "unit": "Unit", "value_type": "Type"
        })
    except Exception:
        return pd.DataFrame()

# ── Plotly theme helper ────────────────────────────────────────────────────
PLOTLY_COLORS = ["#2d9e6b", "#0a2d1e", "#69d9a0", "#1a5c3a", "#a8d5b5",
                 "#3dbf87", "#d4e8dd", "#4a7a5c", "#c8f0d8", "#0d3d28"]

def _fig_layout(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(family="IBM Plex Sans, sans-serif", color="#1a2e22"),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f4f9f6",
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#e8f2ec", linecolor="#d4e8dd")
    fig.update_yaxes(gridcolor="#e8f2ec", linecolor="#d4e8dd")
    return fig

# ── Sidebar navigation ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px 0;">
        <span style="font-size:2.2rem;">🌿</span><br>
        <strong style="font-size:1.1rem; color:#e8f5e9 !important;">MoroccoMetaDB</strong>
    </div>
    """, unsafe_allow_html=True)

    page = option_menu(
        menu_title=None,
        options=[
            "Dashboard", "Search Plants", "Compare Plants",
            "Compound Explorer", "Bioactivity Charts", "Docking Results",
            "Submit Data", "Download Center", "Add Entry",
        ],
        icons=[
            "house-fill", "search", "bar-chart-steps",
            "eyedropper", "graph-up", "capsule",
            "cloud-upload", "download", "pencil-fill",
        ],
        default_index=0,
        styles={
            "container": {"background-color": "#0a2d1e", "padding": "0"},
            "icon": {"color": "#69d9a0", "font-size": "14px"},
            "nav-link": {
                "color": "#c8e6c9", "font-size": "13px", "font-weight": "500",
                "padding": "10px 16px", "border-radius": "6px",
            },
            "nav-link-selected": {
                "background-color": "#1a5c3a", "color": "#ffffff",
                "font-weight": "700",
            },
            "menu-title": {"color": "#69d9a0"},
        },
    )

    try:
        _s = cached_stats()
        _t = _s.get("totals", {})
        st.markdown(f"""
        <div class="sidebar-stats">
            🌿 {_t.get('plants', 0)} plants &nbsp;·&nbsp; ⚗️ {_t.get('compounds', 0)} compounds
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("""
    <div class="sidebar-footer">
        <strong style="color:#e8f5e9 !important;">Marouane Takie</strong><br>
        USMBA Fès · Morocco<br>
        <a href="https://orcid.org/0009-0009-8621-8548" style="color:#69d9a0 !important;">
            ORCID 0009-0009-8621-8548
        </a>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <h1>🌿 MoroccoMetaDB</h1>
        <p class="tagline">Open phytochemical database of North African medicinal plants</p>
        <p class="stats-line">171 plants &nbsp;·&nbsp; 1,015 compounds &nbsp;·&nbsp; 1,144 references</p>
    </div>
    """, unsafe_allow_html=True)

    stats = cached_stats()
    t = stats.get("totals", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌿 Plants",       t.get("plants", 0),        delta="171 total")
    c2.metric("⚗️ Compounds",    t.get("compounds", 0),     delta="1,015 total")
    c3.metric("📊 Bioactivities", t.get("bioactivities", 0), delta="675 total")
    c4.metric("📚 References",    t.get("references", 0),    delta="1,144 total")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: map + compound classes
    col_map, col_cls = st.columns([3, 2])

    with col_map:
        st.subheader("Plants per Country")
        country_data = pd.DataFrame({
            "iso3":    ["MAR", "DZA", "EGY", "LBY", "TUN"],
            "country": ["Morocco", "Algeria", "Egypt", "Libya", "Tunisia"],
            "plants":  [63, 30, 29, 29, 20],
        })
        fig_map = px.choropleth(
            country_data,
            locations="iso3",
            locationmode="ISO-3",
            color="plants",
            hover_name="country",
            hover_data={"plants": True, "iso3": False},
            color_continuous_scale="Greens",
            title="Plants per country",
            range_color=(0, 70),
        )
        fig_map.update_layout(
            geo=dict(
                scope="africa",
                showframe=False,
                showcoastlines=True,
                coastlinecolor="lightgray",
                showland=True,
                landcolor="#f5f5f5",
                showocean=True,
                oceancolor="#e8f4f8",
                showlakes=False,
                showcountries=True,
                countrycolor="white",
                countrywidth=0.5,
                center=dict(lat=27, lon=18),
                projection_scale=2.8,
                lataxis=dict(range=[14, 38]),
                lonaxis=dict(range=[-18, 42]),
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=440,
            paper_bgcolor="white",
            font=dict(family="IBM Plex Sans", color="#1a2e22"),
            title=dict(
                text="MoroccoMetaDB — Plant coverage across North Africa",
                x=0.5,
                font=dict(size=14, color="#0a2d1e"),
            ),
            coloraxis_colorbar=dict(title="Plants", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_cls:
        st.subheader("Compound Classes")
        cls_data = pd.DataFrame({
            "class": ["flavonoid", "terpenoid", "polyphenol", "alkaloid", "other", "fatty acid"],
            "count": [327, 274, 179, 136, 95, 4],
        }).sort_values("count", ascending=True)
        fig_cls = px.bar(
            cls_data, x="count", y="class", orientation="h",
            color="count", color_continuous_scale="Greens",
            labels={"count": "Compounds", "class": ""},
        )
        fig_cls.update_traces(marker_color=PLOTLY_COLORS[:len(cls_data)])
        _fig_layout(fig_cls, height=360)
        fig_cls.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cls, use_container_width=True)

    # Row 2: bioactivity bar + top cytotoxic
    col_bio, col_cyto = st.columns([3, 2])

    with col_bio:
        st.subheader("Bioactivity Assay Coverage")
        bio_data = pd.DataFrame({
            "assay": ["DPPH", "anti-inflammatory", "MIC", "MTT",
                      "alpha-glucosidase", "ABTS", "alpha-amylase", "gastroprotective"],
            "count": [169, 155, 133, 73, 67, 61, 9, 7],
        }).sort_values("count", ascending=False)
        fig_bio = px.bar(
            bio_data, x="assay", y="count",
            color="count", color_continuous_scale="Greens",
            labels={"assay": "Assay Type", "count": "Records"},
        )
        fig_bio.update_traces(
            marker_color=PLOTLY_COLORS,
            text=bio_data["count"].values,
            textposition="outside",
        )
        _fig_layout(fig_bio, height=340)
        fig_bio.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bio, use_container_width=True)

    with col_cyto:
        st.subheader("Top 10 Most Cytotoxic (MTT IC₅₀)")
        df_cyto = cached_top_cytotoxic(10)
        if not df_cyto.empty:
            st.dataframe(df_cyto, use_container_width=True, hide_index=True)
        else:
            st.info("No MTT data yet.")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2 — SEARCH PLANTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Search Plants":
    st.title("Search Plants")

    all_plants = cached_all_plants()
    countries = sorted({p["country"] for p in all_plants if p.get("country")})
    families  = sorted({p["family"]  for p in all_plants if p.get("family")})
    all_bio   = cached_all_bioactivities()
    assay_types = sorted({b["assay_type"] for b in all_bio if b.get("assay_type")})
    all_cpds  = cached_all_compounds()
    classes   = sorted({c["class"] for c in all_cpds if c.get("class")})

    with st.sidebar:
        st.markdown("---")
        st.markdown("**🔎 Advanced Filters**")
        q_name    = st.text_input("Name (scientific or common)", placeholder="e.g. Erodium")
        q_country = st.multiselect("Country", countries)
        q_family  = st.text_input("Family", placeholder="e.g. Lamiaceae")
        q_class   = st.multiselect("Compound class", classes)
        q_assay   = st.selectbox("Assay type", ["All"] + assay_types)
        q_ic50    = st.slider("Max IC₅₀ (µg/mL)", 0, 500, 500, 5)
        apply = st.button("Apply Filters")

    # Build results
    try:
        results = search_plants(
            query=q_name or None,
            country=q_country[0] if len(q_country) == 1 else None,
            family=q_family or None,
        )
        if len(q_country) > 1:
            results = [p for p in results if p.get("country") in q_country]
        if q_assay != "All" or q_ic50 < 500:
            filtered_bio = search_bioactivities(
                assay_type=None if q_assay == "All" else q_assay,
                max_value=q_ic50 if q_ic50 < 500 else None,
            )
            active_ids = {b["plant_id"] for b in filtered_bio}
            results = [p for p in results if p["id"] in active_ids]
        if q_class:
            cpd_ids = {c["plant_id"] for c in all_cpds if c.get("class") in q_class}
            results = [p for p in results if p["id"] in cpd_ids]
    except Exception as e:
        st.error(f"Search error: {e}")
        results = []

    st.markdown(f"**{len(results)} plant(s) found**")

    for plant in results:
        label = f"🌱 *{plant['scientific_name']}* — {plant.get('common_name_en') or ''}"
        with st.expander(label):
            t1, t2, t3, t4, t5, t6 = st.tabs(
                ["Overview", "Compounds", "Bioactivities", "Docking", "Ethnobotany", "References"]
            )

            with t1:
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown(f"**Scientific name:** *{plant['scientific_name']}*")
                    st.markdown(f"**Family:** {plant.get('family') or '—'}")
                    st.markdown(f"**Country:** {plant.get('country') or '—'}")
                    st.markdown(f"**Region:** {plant.get('region') or '—'}")
                with c_b:
                    st.markdown(f"**English:** {plant.get('common_name_en') or '—'}")
                    st.markdown(f"**French:** {plant.get('common_name_fr') or '—'}")
                    st.markdown(f"**Arabic:** {plant.get('common_name_ar') or '—'}")
                if plant.get("traditional_use"):
                    st.markdown(f"**Traditional use:** {plant['traditional_use']}")

            with t2:
                try:
                    cpds = get_compounds(plant["id"])
                    if cpds:
                        df = pd.DataFrame(cpds)
                        show = [c for c in ["name", "class", "subclass", "detection_method",
                                            "molecular_formula", "mz_observed"] if c in df.columns]
                        st.dataframe(df[show].rename(columns={
                            "name": "Compound", "class": "Class", "subclass": "Subclass",
                            "detection_method": "Method", "molecular_formula": "Formula",
                            "mz_observed": "m/z",
                        }), use_container_width=True, hide_index=True)
                        if RDKIT_AVAILABLE:
                            for row in cpds:
                                if row.get("smiles"):
                                    mol = Chem.MolFromSmiles(row["smiles"])
                                    if mol:
                                        svg = Draw.MolToImage(mol, size=(250, 180))
                                        st.image(svg, caption=row["name"])
                        else:
                            st.caption("2D structure viewer: install RDKit for structure images.")
                    else:
                        st.info("No compounds recorded.")
                except Exception as e:
                    st.error(f"Error loading compounds: {e}")

            with t3:
                try:
                    bioacts = get_bioactivities(plant["id"])
                    if bioacts:
                        df = pd.DataFrame(bioacts)
                        show = [c for c in ["assay_type", "value", "unit", "value_type",
                                            "activity_category"] if c in df.columns]
                        df_show = df[show].rename(columns={
                            "assay_type": "Assay", "value": "Value", "unit": "Unit",
                            "value_type": "Type", "activity_category": "Category",
                        })
                        st.dataframe(df_show, use_container_width=True, hide_index=True)
                        # Chart
                        df_chart = df[df["value"].notna() & df["assay_type"].notna()]
                        if not df_chart.empty:
                            fig = px.bar(
                                df_chart, x="value", y="assay_type", orientation="h",
                                color="assay_type",
                                labels={"value": "IC₅₀ / Value", "assay_type": "Assay"},
                                color_discrete_sequence=PLOTLY_COLORS,
                            )
                            _fig_layout(fig, height=260)
                            fig.update_layout(showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No bioactivities recorded.")
                except Exception as e:
                    st.error(f"Error loading bioactivities: {e}")

            with t4:
                try:
                    all_dock = get_docking_results()
                    plant_dock = [d for d in all_dock if d.get("plant_id") == plant["id"]]
                    if plant_dock:
                        df = pd.DataFrame(plant_dock)
                        show = [c for c in ["compound_name", "target_name", "target_pdb_id",
                                            "binding_energy", "key_residues"] if c in df.columns]
                        st.dataframe(df[show], use_container_width=True, hide_index=True)
                    else:
                        st.info("No docking results recorded.")
                except Exception as e:
                    st.error(f"Error loading docking: {e}")

            with t5:
                try:
                    ethno = get_ethnobotany(plant["id"])
                    if ethno:
                        df = pd.DataFrame(ethno)
                        show = [c for c in ["use_category", "plant_part", "preparation",
                                            "administration"] if c in df.columns]
                        st.dataframe(df[show], use_container_width=True, hide_index=True)
                    else:
                        st.info("No ethnobotanical data recorded.")
                except Exception as e:
                    st.error(f"Error loading ethnobotany: {e}")

            with t6:
                try:
                    refs = get_references(plant["id"])
                    if refs:
                        for ref in refs:
                            doi_link = (
                                f"[{ref.get('doi')}](https://doi.org/{ref.get('doi')})"
                                if ref.get("doi") else "—"
                            )
                            pmid_link = (
                                f"[{ref.get('pmid')}](https://pubmed.ncbi.nlm.nih.gov/{ref.get('pmid')}/)"
                                if ref.get("pmid") else ""
                            )
                            st.markdown(
                                f"- **{ref.get('authors', '')}** ({ref.get('year', '')}). "
                                f"{ref.get('title', '')}. *{ref.get('journal', '')}*. "
                                f"DOI: {doi_link}  {pmid_link}"
                            )
                    else:
                        st.info("No references recorded.")
                except Exception as e:
                    st.error(f"Error loading references: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3 — COMPARE PLANTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Compare Plants":
    st.title("Compare Plants")

    all_plants = cached_all_plants()
    plant_names = [p["scientific_name"] for p in all_plants]
    plant_map   = {p["scientific_name"]: p for p in all_plants}

    selected = st.multiselect(
        "Select 2–4 plants to compare",
        plant_names,
        max_selections=4,
        placeholder="Type to search...",
    )

    if len(selected) < 2:
        st.info("Select at least 2 plants to compare.")
    else:
        # Summary table
        rows = []
        for name in selected:
            p = plant_map[name]
            try:
                cpds  = get_compounds(p["id"])
                bios  = get_bioactivities(p["id"])
                mtt   = [b["value"] for b in bios
                         if b.get("assay_type") == "MTT" and b.get("value") is not None]
                best  = f"{min(mtt):.1f} µg/mL" if mtt else "—"
                rows.append({
                    "Plant":        name,
                    "Family":       p.get("family") or "—",
                    "Country":      p.get("country") or "—",
                    "Compounds":    len(cpds),
                    "Bioactivities":len(bios),
                    "Best MTT IC₅₀":best,
                })
            except Exception:
                rows.append({"Plant": name, "Family": "—", "Country": "—",
                             "Compounds": "—", "Bioactivities": "—", "Best MTT IC₅₀": "—"})

        st.subheader("Side-by-Side Summary")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # IC50 comparison chart
        st.subheader("IC₅₀ Comparison by Assay")
        chart_rows = []
        for name in selected:
            p = plant_map[name]
            try:
                bios = get_bioactivities(p["id"])
                for b in bios:
                    if b.get("value") is not None:
                        chart_rows.append({
                            "Plant":   name,
                            "Assay":   b["assay_type"],
                            "IC50":    b["value"],
                            "Unit":    b.get("unit", ""),
                        })
            except Exception:
                pass

        if chart_rows:
            df_chart = pd.DataFrame(chart_rows)
            fig_cmp = px.bar(
                df_chart, x="Assay", y="IC50", color="Plant", barmode="group",
                color_discrete_sequence=PLOTLY_COLORS,
                labels={"IC50": "Value (µg/mL or %)"},
            )
            _fig_layout(fig_cmp, height=400)
            st.plotly_chart(fig_cmp, use_container_width=True)

        # Compound class overlap
        st.subheader("Compound Class Overlap")
        class_sets = {}
        for name in selected:
            p = plant_map[name]
            try:
                cpds = get_compounds(p["id"])
                class_sets[name] = {c["class"] for c in cpds if c.get("class")}
            except Exception:
                class_sets[name] = set()

        all_classes = set().union(*class_sets.values())
        overlap_data = {
            "Class": list(all_classes),
        }
        for name in selected:
            short = name.split()[0]
            overlap_data[short] = ["✅" if cls in class_sets[name] else "—"
                                   for cls in all_classes]
        st.dataframe(pd.DataFrame(overlap_data), use_container_width=True, hide_index=True)

        # Excel download
        st.subheader("Download Comparison")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            pd.DataFrame(rows).to_excel(writer, sheet_name="Summary", index=False)
            for name in selected:
                p = plant_map[name]
                safe_name = name.replace(" ", "_")[:28]
                try:
                    bios = get_bioactivities(p["id"])
                    if bios:
                        pd.DataFrame(bios).to_excel(writer, sheet_name=safe_name, index=False)
                except Exception:
                    pass
        buf.seek(0)
        st.download_button(
            "⬇️ Download Comparison Excel",
            data=buf.read(),
            file_name="moroccometadb_comparison.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4 — COMPOUND EXPLORER
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Compound Explorer":
    st.title("Compound Explorer")

    all_cpds = cached_all_compounds()
    classes  = sorted({c["class"] for c in all_cpds if c.get("class")})
    methods  = sorted({c["detection_method"] for c in all_cpds if c.get("detection_method")})

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        q_name = st.text_input("Search compound name", placeholder="e.g. Quercetin")
    with col2:
        q_cls  = st.selectbox("Class", ["All"] + classes)
    with col3:
        q_meth = st.selectbox("Detection method", ["All"] + methods)

    try:
        results = search_compounds(
            query=q_name or None,
            class_=None if q_cls == "All" else q_cls,
        )
        if q_meth != "All":
            results = [c for c in results if c.get("detection_method") == q_meth]
    except Exception as e:
        st.error(f"Search error: {e}")
        results = []

    st.markdown(f"**{len(results)} compound(s) found**")

    if results:
        df = pd.DataFrame(results)
        show = [c for c in ["name", "class", "subclass", "molecular_formula",
                             "mz_observed", "detection_method", "scientific_name"]
                if c in df.columns]
        df_show = df[show].rename(columns={
            "name": "Compound", "class": "Class", "subclass": "Subclass",
            "molecular_formula": "Formula", "mz_observed": "m/z",
            "detection_method": "Method", "scientific_name": "Plant",
        })
        st.dataframe(df_show, use_container_width=True, hide_index=True)

        # Expandable row detail
        selected_name = st.selectbox(
            "Expand compound detail:", ["— select —"] + [r["name"] for r in results]
        )
        if selected_name != "— select —":
            cpd_rows = [r for r in results if r["name"] == selected_name]
            if cpd_rows:
                cpd = cpd_rows[0]
                with st.expander(f"🧪 {selected_name}", expanded=True):
                    c_a, c_b = st.columns([1, 2])
                    with c_a:
                        st.markdown(f"**Class:** {cpd.get('class') or '—'}")
                        st.markdown(f"**Subclass:** {cpd.get('subclass') or '—'}")
                        st.markdown(f"**Formula:** {cpd.get('molecular_formula') or '—'}")
                        st.markdown(f"**m/z:** {cpd.get('mz_observed') or '—'}")
                        st.markdown(f"**Method:** {cpd.get('detection_method') or '—'}")
                        if RDKIT_AVAILABLE and cpd.get("smiles"):
                            mol = Chem.MolFromSmiles(cpd["smiles"])
                            if mol:
                                img = Draw.MolToImage(mol, size=(240, 180))
                                st.image(img, caption="2D structure")
                        else:
                            st.caption("Structure not available")
                    with c_b:
                        # Plants containing this compound
                        plant_ids = {r["plant_id"] for r in cpd_rows if r.get("plant_id")}
                        all_plants = cached_all_plants()
                        matching = [p for p in all_plants if p["id"] in plant_ids]
                        if matching:
                            st.markdown(f"**Found in {len(matching)} plant(s):**")
                            for p in matching:
                                st.markdown(f"  - *{p['scientific_name']}* ({p.get('country', '—')})")

                    # Bioactivities for plants containing this compound
                    if plant_ids:
                        all_bio_rows = []
                        for pid in plant_ids:
                            try:
                                bios = get_bioactivities(pid)
                                all_bio_rows.extend(bios)
                            except Exception:
                                pass
                        if all_bio_rows:
                            st.markdown("**Associated bioactivities:**")
                            df_bio = pd.DataFrame(all_bio_rows)
                            show = [c for c in ["assay_type", "value", "unit",
                                                "activity_category"] if c in df_bio.columns]
                            st.dataframe(df_bio[show], use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 5 — BIOACTIVITY CHARTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Bioactivity Charts":
    st.title("Bioactivity Charts")

    all_bio = cached_all_bioactivities()
    assay_types = sorted({b["assay_type"] for b in all_bio if b.get("assay_type")})
    all_plants  = cached_all_plants()
    countries   = sorted({p["country"] for p in all_plants if p.get("country")})

    c1, c2, c3 = st.columns(3)
    with c1:
        sel_assay = st.selectbox("Assay type", assay_types, index=0)
    with c2:
        sel_country = st.selectbox("Country", ["All"] + countries)
    with c3:
        sel_max = st.number_input("Max IC₅₀ (µg/mL)", min_value=1.0, value=500.0, step=10.0)

    # Filter
    try:
        filtered = search_bioactivities(
            assay_type=sel_assay,
            max_value=sel_max if sel_max < 500 else None,
        )
        if sel_country != "All":
            pid_set = {p["id"] for p in all_plants if p.get("country") == sel_country}
            filtered = [b for b in filtered if b.get("plant_id") in pid_set]
    except Exception as e:
        st.error(f"Filter error: {e}")
        filtered = []

    if not filtered:
        st.info("No data matches the current filters.")
    else:
        df_f = pd.DataFrame(filtered)
        df_f = df_f[df_f["value"].notna()].sort_values("value").head(20)

        # Horizontal bar chart — top 20
        st.subheader(f"Top 20 Most Active Plants — {sel_assay}")
        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            x=df_f["value"].values,
            y=df_f["scientific_name"].values if "scientific_name" in df_f.columns else df_f.index,
            orientation="h",
            marker_color="#2d9e6b",
            name="IC₅₀",
            hovertemplate="%{y}<br>%{x:.2f} µg/mL<extra></extra>",
        ))
        _fig_layout(fig_top, height=520)
        fig_top.update_layout(xaxis_title="Value (µg/mL or %)", yaxis_title="")
        st.plotly_chart(fig_top, use_container_width=True)

        # Summary statistics
        st.subheader("Summary Statistics")
        all_assay_stats = []
        for assay in assay_types:
            try:
                rows = search_bioactivities(assay_type=assay)
                vals = [r["value"] for r in rows if r.get("value") is not None]
                if vals:
                    all_assay_stats.append({
                        "Assay": assay,
                        "n": len(vals),
                        "Mean": f"{sum(vals)/len(vals):.1f}",
                        "Median": f"{sorted(vals)[len(vals)//2]:.1f}",
                        "Min": f"{min(vals):.2f}",
                        "Max": f"{max(vals):.1f}",
                    })
            except Exception:
                pass
        if all_assay_stats:
            st.dataframe(pd.DataFrame(all_assay_stats), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 6 — DOCKING RESULTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Docking Results":
    st.title("Molecular Docking Results")

    try:
        all_dock = get_docking_results()
    except Exception as e:
        st.error(f"Error loading docking data: {e}")
        all_dock = []

    targets = sorted({d["target_name"] for d in all_dock if d.get("target_name")})
    sel_target = st.selectbox("Target protein", ["All"] + targets)

    try:
        results = get_docking_results(
            target_name=None if sel_target == "All" else sel_target
        )
    except Exception as e:
        st.error(f"Error: {e}")
        results = []

    st.markdown(f"**{len(results)} docking result(s)**")

    if results:
        df = pd.DataFrame(results)
        show = [c for c in ["compound_name", "scientific_name", "target_name",
                             "target_pdb_id", "binding_energy", "software",
                             "h_bonds", "key_residues"] if c in df.columns]
        df_show = df[show].rename(columns={
            "compound_name": "Compound", "scientific_name": "Plant",
            "target_name": "Target", "target_pdb_id": "PDB ID",
            "binding_energy": "ΔG (kcal/mol)", "software": "Software",
            "h_bonds": "H-bonds", "key_residues": "Key residues",
        })
        st.dataframe(df_show.sort_values("ΔG (kcal/mol)") if "ΔG (kcal/mol)" in df_show.columns
                     else df_show,
                     use_container_width=True, hide_index=True)

        if "binding_energy" in df.columns:
            df_chart = df[df["binding_energy"].notna()].sort_values("binding_energy")
            if not df_chart.empty:
                st.subheader("Binding Energy Comparison")
                fig_dock = px.bar(
                    df_chart,
                    x="compound_name" if "compound_name" in df_chart.columns else df_chart.index,
                    y="binding_energy",
                    color="binding_energy",
                    color_continuous_scale="Greens_r",
                    labels={"binding_energy": "ΔG (kcal/mol)", "compound_name": "Compound"},
                )
                _fig_layout(fig_dock, height=380)
                st.plotly_chart(fig_dock, use_container_width=True)

        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv_buf.getvalue().encode("utf-8"),
            file_name="moroccometadb_docking.csv",
            mime="text/csv",
        )
    else:
        st.info("No docking results in database. Add entries via the Add Entry page or AutoDock Vina pipeline.")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 7 — SUBMIT DATA
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Submit Data":
    st.title("Submit Research Data")

    st.info(
        "📬 **Submit your research data to MoroccoMetaDB for review.** "
        "Submissions are reviewed by the curation team within 7 days before being added to the database."
    )

    tab_sub, tab_admin = st.tabs(["Submit", "Admin Review"])

    with tab_sub:
        sub_type = st.selectbox(
            "Submission type",
            ["Plant", "Compound", "Bioactivity", "Docking Result"],
        )
        st.markdown("---")

        data_fields = {}

        if sub_type == "Plant":
            c1, c2 = st.columns(2)
            data_fields["scientific_name"] = c1.text_input("Scientific name *")
            data_fields["family"]          = c2.text_input("Family")
            c3, c4 = st.columns(2)
            data_fields["common_name_en"]  = c3.text_input("English name")
            data_fields["common_name_fr"]  = c4.text_input("French name")
            data_fields["country"]         = st.selectbox(
                "Country", ["Morocco", "Algeria", "Tunisia", "Libya", "Egypt"]
            )
            data_fields["traditional_use"] = st.text_area("Traditional uses")

        elif sub_type == "Compound":
            c1, c2 = st.columns(2)
            data_fields["compound_name"]   = c1.text_input("Compound name *")
            data_fields["plant_name"]      = c2.text_input("Plant (scientific name)")
            c3, c4 = st.columns(2)
            data_fields["class_"]          = c3.text_input("Class (e.g. flavonoid)")
            data_fields["subclass"]        = c4.text_input("Subclass")
            c5, c6 = st.columns(2)
            data_fields["molecular_formula"] = c5.text_input("Molecular formula")
            data_fields["detection_method"]  = c6.text_input("Detection method")
            data_fields["notes"]           = st.text_area("Notes / references")

        elif sub_type == "Bioactivity":
            c1, c2 = st.columns(2)
            data_fields["plant_name"]      = c1.text_input("Plant (scientific name)")
            data_fields["assay_type"]      = c2.selectbox(
                "Assay type",
                ["DPPH", "ABTS", "FRAP", "MTT", "MIC",
                 "alpha-glucosidase", "alpha-amylase", "anti-inflammatory", "other"]
            )
            c3, c4, c5 = st.columns(3)
            data_fields["value"]           = c3.number_input("Value", 0.0, 10000.0)
            data_fields["unit"]            = c4.text_input("Unit", "µg/mL")
            data_fields["value_type"]      = c5.selectbox(
                "Value type", ["IC50", "MIC", "inhibition%", "other"]
            )
            data_fields["reference"]       = st.text_input("DOI / PMID of source")

        elif sub_type == "Docking Result":
            c1, c2 = st.columns(2)
            data_fields["compound_name"]   = c1.text_input("Compound name")
            data_fields["plant_name"]      = c2.text_input("Plant (scientific name)")
            c3, c4 = st.columns(2)
            data_fields["target_name"]     = c3.text_input("Target protein")
            data_fields["target_pdb_id"]   = c4.text_input("PDB ID")
            c5, c6 = st.columns(2)
            data_fields["binding_energy"]  = c5.number_input("Binding energy (kcal/mol)", -30.0, 0.0, -7.0)
            data_fields["software"]        = c6.text_input("Software", "AutoDock Vina")
            data_fields["key_residues"]    = st.text_input("Key interacting residues")

        st.markdown("---")
        email = st.text_input("Your email (optional — for follow-up)")
        if st.button("Submit for Review"):
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute(
                    """INSERT INTO pending_submissions
                       (submission_type, data_json, submitter_email)
                       VALUES (?, ?, ?)""",
                    (sub_type, json.dumps(data_fields, ensure_ascii=False), email or None),
                )
                conn.commit()
                conn.close()
                st.success(
                    "✅ **Thank you — your submission will be reviewed within 7 days.**  \n"
                    "The curation team will verify the data against primary literature "
                    "before adding it to the database."
                )
            except Exception as e:
                st.error(f"Submission error: {e}")

    with tab_admin:
        pwd = st.text_input("Admin password", type="password")
        if pwd == "admin123":
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM pending_submissions ORDER BY submitted_at DESC"
                ).fetchall()
                conn.close()
                if not rows:
                    st.info("No pending submissions.")
                else:
                    for row in rows:
                        row = dict(row)
                        with st.expander(
                            f"#{row['id']} — {row['submission_type']} "
                            f"({row['submitted_at'][:16]}) — **{row['status'].upper()}**"
                        ):
                            st.json(json.loads(row["data_json"]))
                            st.caption(f"Submitter: {row.get('submitter_email') or 'anonymous'}")
                            c1, c2 = st.columns(2)
                            if c1.button("✅ Approve", key=f"app_{row['id']}"):
                                conn = sqlite3.connect(DB_PATH)
                                conn.execute(
                                    "UPDATE pending_submissions SET status='approved' WHERE id=?",
                                    (row["id"],)
                                )
                                conn.commit(); conn.close()
                                st.rerun()
                            if c2.button("❌ Reject", key=f"rej_{row['id']}"):
                                conn = sqlite3.connect(DB_PATH)
                                conn.execute(
                                    "UPDATE pending_submissions SET status='rejected' WHERE id=?",
                                    (row["id"],)
                                )
                                conn.commit(); conn.close()
                                st.rerun()
            except Exception as e:
                st.error(f"Admin error: {e}")
        elif pwd:
            st.error("Incorrect password.")
        else:
            st.caption("Enter the admin password to view pending submissions.")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 8 — DOWNLOAD CENTER
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Download Center":
    st.title("Download Center")

    # Full database downloads
    st.subheader("Section 1 — Full Database Downloads")
    try:
        plants_df  = pd.DataFrame(cached_all_plants())
        cpds_df    = pd.DataFrame(cached_all_compounds())
        bios_df    = pd.DataFrame(cached_all_bioactivities())
        dock_df    = pd.DataFrame(get_docking_results())
        refs_df    = pd.DataFrame(get_references())
    except Exception as e:
        st.error(f"Error loading data: {e}")
        plants_df = cpds_df = bios_df = dock_df = refs_df = pd.DataFrame()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "🌿 Plants CSV",
            data=plants_df.to_csv(index=False).encode("utf-8"),
            file_name="moroccometadb_plants.csv", mime="text/csv",
            disabled=plants_df.empty,
        )
    with c2:
        st.download_button(
            "⚗️ Compounds CSV",
            data=cpds_df.to_csv(index=False).encode("utf-8"),
            file_name="moroccometadb_compounds.csv", mime="text/csv",
            disabled=cpds_df.empty,
        )
    with c3:
        st.download_button(
            "📊 Bioactivities CSV",
            data=bios_df.to_csv(index=False).encode("utf-8"),
            file_name="moroccometadb_bioactivities.csv", mime="text/csv",
            disabled=bios_df.empty,
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        st.download_button(
            "💊 Docking CSV",
            data=dock_df.to_csv(index=False).encode("utf-8") if not dock_df.empty else b"",
            file_name="moroccometadb_docking.csv", mime="text/csv",
            disabled=dock_df.empty,
        )
    with c5:
        full_json = json.dumps({
            "plants":          plants_df.to_dict("records"),
            "compounds":       cpds_df.to_dict("records"),
            "bioactivities":   bios_df.to_dict("records"),
            "docking_results": dock_df.to_dict("records"),
        }, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            "🗃️ Full JSON",
            data=full_json,
            file_name="moroccometadb_full.json", mime="application/json",
        )
    with c6:
        buf_xl = io.BytesIO()
        with pd.ExcelWriter(buf_xl, engine="openpyxl") as writer:
            if not plants_df.empty: plants_df.to_excel(writer, sheet_name="Plants", index=False)
            if not cpds_df.empty:   cpds_df.to_excel(writer, sheet_name="Compounds", index=False)
            if not bios_df.empty:   bios_df.to_excel(writer, sheet_name="Bioactivities", index=False)
            if not dock_df.empty:   dock_df.to_excel(writer, sheet_name="Docking", index=False)
            if not refs_df.empty:   refs_df.to_excel(writer, sheet_name="References", index=False)
        buf_xl.seek(0)
        st.download_button(
            "📒 Full Excel",
            data=buf_xl.read(),
            file_name="moroccometadb_full.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.markdown("---")

    # Custom query downloads
    st.subheader("Section 2 — Custom Query Downloads")
    all_plants = cached_all_plants()
    countries  = sorted({p["country"] for p in all_plants if p.get("country")})
    all_cpds   = cached_all_compounds()
    classes    = sorted({c["class"] for c in all_cpds if c.get("class")})
    all_bio    = cached_all_bioactivities()
    assays     = sorted({b["assay_type"] for b in all_bio if b.get("assay_type")})

    fc1, fc2, fc3 = st.columns(3)
    f_country = fc1.selectbox("Country", ["All"] + countries, key="dl_country")
    f_class   = fc2.selectbox("Compound class", ["All"] + classes, key="dl_class")
    f_assay   = fc3.selectbox("Assay type", ["All"] + assays, key="dl_assay")

    try:
        f_plants = [p for p in all_plants
                    if f_country == "All" or p.get("country") == f_country]
        f_pid    = {p["id"] for p in f_plants}
        f_cpds   = [c for c in all_cpds
                    if c.get("plant_id") in f_pid and
                    (f_class == "All" or c.get("class") == f_class)]
        f_bios   = [b for b in all_bio
                    if b.get("plant_id") in f_pid and
                    (f_assay == "All" or b.get("assay_type") == f_assay)]
        st.markdown(f"**Preview:** {len(f_plants)} plants · {len(f_cpds)} compounds · {len(f_bios)} bioactivities")
        if f_bios:
            st.dataframe(pd.DataFrame(f_bios).head(10), use_container_width=True, hide_index=True)
        dca, dcb = st.columns(2)
        with dca:
            st.download_button(
                "⬇️ Filtered Bioactivities CSV",
                data=pd.DataFrame(f_bios).to_csv(index=False).encode("utf-8") if f_bios else b"no data",
                file_name="moroccometadb_filtered_bio.csv", mime="text/csv",
            )
        with dcb:
            buf_f = io.BytesIO()
            with pd.ExcelWriter(buf_f, engine="openpyxl") as writer:
                pd.DataFrame(f_plants).to_excel(writer, sheet_name="Plants", index=False)
                pd.DataFrame(f_cpds).to_excel(writer, sheet_name="Compounds", index=False)
                pd.DataFrame(f_bios).to_excel(writer, sheet_name="Bioactivities", index=False)
            buf_f.seek(0)
            st.download_button(
                "⬇️ Filtered Excel",
                data=buf_f.read(),
                file_name="moroccometadb_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    except Exception as e:
        st.error(f"Filter error: {e}")

    st.markdown("---")

    # PDF plant report
    st.subheader("Section 3 — Plant Report (PDF)")
    if not FPDF_AVAILABLE:
        st.warning("fpdf2 not installed. Run: pip install fpdf2")
    else:
        plant_names = [p["scientific_name"] for p in all_plants]
        sel_plant   = st.selectbox("Select plant", plant_names, key="pdf_plant")
        if st.button("Generate PDF Report"):
            plant_obj = next((p for p in all_plants if p["scientific_name"] == sel_plant), None)
            if plant_obj:
                try:
                    cpds_p = get_compounds(plant_obj["id"])
                    bios_p = get_bioactivities(plant_obj["id"])
                    refs_p = get_references(plant_obj["id"])

                    pdf = FPDF()
                    pdf.set_margins(20, 20, 20)
                    pdf.add_page()

                    pdf.set_font("Helvetica", "B", 18)
                    pdf.set_text_color(10, 45, 30)
                    pdf.cell(0, 12, "MoroccoMetaDB — Plant Report", ln=True, align="C")
                    pdf.ln(2)

                    pdf.set_font("Helvetica", "B", 14)
                    pdf.set_text_color(45, 158, 107)
                    pdf.cell(0, 10, sel_plant, ln=True)
                    pdf.ln(2)

                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(26, 46, 34)
                    fields = [
                        ("Family",      plant_obj.get("family") or "—"),
                        ("Country",     plant_obj.get("country") or "—"),
                        ("English",     plant_obj.get("common_name_en") or "—"),
                        ("French",      plant_obj.get("common_name_fr") or "—"),
                        ("Traditional", plant_obj.get("traditional_use") or "—"),
                    ]
                    for label, val in fields:
                        pdf.set_font("Helvetica", "B", 10)
                        pdf.cell(40, 7, f"{label}:", border=0)
                        pdf.set_font("Helvetica", "", 10)
                        pdf.multi_cell(0, 7, str(val)[:120])
                    pdf.ln(4)

                    pdf.set_font("Helvetica", "B", 12)
                    pdf.set_text_color(10, 45, 30)
                    pdf.cell(0, 8, f"Compounds ({len(cpds_p)})", ln=True)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(26, 46, 34)
                    for cpd in cpds_p:
                        line = f"  • {cpd.get('name', '')}  [{cpd.get('class', '')}]"
                        if cpd.get("subclass"):
                            line += f"  — {cpd['subclass']}"
                        pdf.cell(0, 6, line[:110], ln=True)
                    pdf.ln(4)

                    pdf.set_font("Helvetica", "B", 12)
                    pdf.set_text_color(10, 45, 30)
                    pdf.cell(0, 8, f"Bioactivities ({len(bios_p)})", ln=True)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(26, 46, 34)
                    for b in bios_p:
                        val_str = f"{b['value']} {b.get('unit', '')}" if b.get("value") else "—"
                        line = f"  • {b.get('assay_type', '')}:  {val_str}  ({b.get('value_type', '')})"
                        pdf.cell(0, 6, line[:110], ln=True)
                    pdf.ln(4)

                    pdf.set_font("Helvetica", "B", 12)
                    pdf.set_text_color(10, 45, 30)
                    pdf.cell(0, 8, f"References ({len(refs_p)})", ln=True)
                    pdf.set_font("Helvetica", "", 8)
                    pdf.set_text_color(26, 46, 34)
                    for ref in refs_p[:15]:
                        line = f"  [{ref.get('year', '')}] {ref.get('authors', '')[:40]}. {ref.get('title', '')[:60]}..."
                        pdf.multi_cell(0, 5, line[:120])

                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(120, 140, 120)
                    pdf.ln(8)
                    pdf.cell(0, 5, f"Generated by MoroccoMetaDB  •  {datetime.now().strftime('%Y-%m-%d')}  •  Marouane Takie · USMBA Fès", align="C")

                    pdf_bytes = bytes(pdf.output())
                    safe = sel_plant.replace(" ", "_")
                    st.download_button(
                        f"⬇️ Download {safe}_report.pdf",
                        data=pdf_bytes,
                        file_name=f"{safe}_report.pdf",
                        mime="application/pdf",
                    )
                    st.success(f"PDF generated for *{sel_plant}*")
                except Exception as e:
                    st.error(f"PDF generation error: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 9 — ADD ENTRY
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Add Entry":
    st.title("Add New Entry")
    st.markdown(
        '<div class="card">Add phytochemical records directly to the database. '
        "All fields marked * are required.</div>",
        unsafe_allow_html=True,
    )

    tab_plant, tab_cpd, tab_bio, tab_ethno = st.tabs(
        ["🌱 Plant", "🧪 Compound", "📊 Bioactivity", "📖 Ethnobotany"]
    )

    with tab_plant:
        st.subheader("Add Plant")
        with st.form("form_plant"):
            sci_name = st.text_input("Scientific name *", placeholder="Erodium moschatum")
            c1, c2, c3 = st.columns(3)
            ar = c1.text_input("Arabic name")
            fr = c2.text_input("French name")
            en = c3.text_input("English name")
            c4, c5 = st.columns(2)
            family  = c4.text_input("Family")
            genus   = c5.text_input("Genus")
            c6, c7  = st.columns(2)
            country = c6.selectbox("Country",
                                   ["Morocco", "Algeria", "Tunisia", "Libya", "Egypt", "Other"])
            region  = c7.text_input("Region")
            endemic  = st.checkbox("Endemic species")
            trad_use = st.text_area("Traditional use")
            if st.form_submit_button("Add Plant"):
                if not sci_name.strip():
                    st.error("Scientific name is required.")
                else:
                    try:
                        pid = add_plant(
                            scientific_name=sci_name.strip(),
                            common_name_ar=ar or None, common_name_fr=fr or None,
                            common_name_en=en or None, family=family or None,
                            genus=genus or None, country=country,
                            region=region or None, is_endemic=int(endemic),
                            traditional_use=trad_use or None,
                        )
                        st.success(f"✅ Plant added — ID {pid}.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error adding plant: {e}")

    with tab_cpd:
        st.subheader("Add Compound")
        try:
            plants = get_all_plants()
            plant_map = {f"{p['scientific_name']} (id={p['id']})": p["id"] for p in plants}
        except Exception:
            plants = []; plant_map = {}
        with st.form("form_compound"):
            if not plant_map:
                st.warning("No plants in database. Add a plant first.")
                st.form_submit_button("Add Compound", disabled=True)
            else:
                sel = st.selectbox("Plant *", list(plant_map.keys()))
                plant_id_sel = plant_map[sel]
                cname = st.text_input("Compound name *")
                c1, c2 = st.columns(2)
                cls    = c1.text_input("Class", placeholder="flavonoid")
                subcls = c2.text_input("Subclass", placeholder="flavone")
                c3, c4 = st.columns(2)
                formula = c3.text_input("Molecular formula")
                mw      = c4.number_input("MW (Da)", min_value=0.0, value=0.0)
                c5, c6, c7 = st.columns(3)
                mz     = c5.number_input("m/z observed", min_value=0.0, value=0.0)
                mode   = c6.selectbox("Ionization mode", ["negative", "positive"])
                adduct = c7.text_input("Adduct", value="[M-H]-")
                method = st.text_input("Detection method", value="UPLC-ESI-MS")
                if st.form_submit_button("Add Compound"):
                    if not cname.strip():
                        st.error("Compound name is required.")
                    else:
                        try:
                            cid = add_compound(
                                plant_id=plant_id_sel, name=cname.strip(),
                                class_=cls or None, subclass=subcls or None,
                                molecular_formula=formula or None,
                                molecular_weight=mw if mw > 0 else None,
                                mz_observed=mz if mz > 0 else None,
                                ionization_mode=mode, adduct=adduct or None,
                                detection_method=method or None,
                            )
                            st.success(f"✅ Compound added — ID {cid}.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Error adding compound: {e}")

    with tab_bio:
        st.subheader("Add Bioactivity")
        try:
            plants = get_all_plants()
            plant_map = {f"{p['scientific_name']} (id={p['id']})": p["id"] for p in plants}
        except Exception:
            plants = []; plant_map = {}
        with st.form("form_bioactivity"):
            if not plant_map:
                st.warning("No plants in database.")
                st.form_submit_button("Add Bioactivity", disabled=True)
            else:
                sel = st.selectbox("Plant *", list(plant_map.keys()))
                plant_id_sel = plant_map[sel]
                c1, c2 = st.columns(2)
                assay = c1.selectbox(
                    "Assay type *",
                    ["DPPH", "ABTS", "FRAP", "MTT", "MIC",
                     "alpha-glucosidase", "alpha-amylase",
                     "anti-inflammatory", "gastroprotective", "other"],
                )
                category = c2.text_input("Activity category", placeholder="antioxidant")
                c3, c4, c5 = st.columns(3)
                value = c3.number_input("Value", min_value=0.0, value=0.0)
                unit  = c4.text_input("Unit", value="µg/mL")
                vtype = c5.selectbox("Value type", ["IC50", "EC50", "inhibition%", "MIC", "other"])
                c6, c7 = st.columns(2)
                ref_cpd = c6.text_input("Reference compound", placeholder="Ascorbic acid")
                ref_val = c7.number_input("Reference value", min_value=0.0, value=0.0)
                model = st.text_input("Model organism", placeholder="MCF-7 / Wistar rat")
                if st.form_submit_button("Add Bioactivity"):
                    try:
                        bid = add_bioactivity(
                            plant_id=plant_id_sel, assay_type=assay,
                            value=value if value > 0 else None,
                            unit=unit or None, value_type=vtype,
                            activity_category=category or None,
                            reference_compound=ref_cpd or None,
                            reference_value=ref_val if ref_val > 0 else None,
                            model_organism=model or None,
                        )
                        st.success(f"✅ Bioactivity added — ID {bid}.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error adding bioactivity: {e}")

    with tab_ethno:
        st.subheader("Add Ethnobotany")
        try:
            plants = get_all_plants()
            plant_map = {f"{p['scientific_name']} (id={p['id']})": p["id"] for p in plants}
        except Exception:
            plants = []; plant_map = {}
        with st.form("form_ethno"):
            if not plant_map:
                st.warning("No plants in database.")
                st.form_submit_button("Add Ethnobotany", disabled=True)
            else:
                sel = st.selectbox("Plant *", list(plant_map.keys()))
                plant_id_sel = plant_map[sel]
                c1, c2 = st.columns(2)
                use_cat    = c1.text_input("Use category", placeholder="antidiabetic")
                plant_part = c2.text_input("Plant part", placeholder="aerial parts")
                c3, c4 = st.columns(2)
                prep  = c3.text_input("Preparation", placeholder="decoction")
                admin = c4.text_input("Administration", placeholder="oral")
                region_et = st.text_input("Region", placeholder="Fès-Meknès")
                notes_et  = st.text_area("Notes")
                if st.form_submit_button("Add Ethnobotany"):
                    try:
                        eid = add_ethnobotany(
                            plant_id=plant_id_sel,
                            use_category=use_cat or None,
                            plant_part=plant_part or None,
                            preparation=prep or None,
                            administration=admin or None,
                            region=region_et or None,
                            notes=notes_et or None,
                        )
                        st.success(f"✅ Ethnobotany entry added — ID {eid}.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error adding ethnobotany: {e}")
