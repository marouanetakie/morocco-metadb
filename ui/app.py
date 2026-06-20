import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import streamlit as st
import pandas as pd

from db.schema import init_db
from db.crud import (
    get_all_plants, search_plants,
    get_compounds, search_compounds,
    get_bioactivities, search_bioactivities,
    get_docking_results,
    get_ethnobotany, get_references, get_stats,
    add_plant, add_compound, add_bioactivity, add_ethnobotany,
)

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoroccoMetaDB",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme / CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif !important; }

.stApp { background-color: #0f3d2e; }

section[data-testid="stSidebar"] {
    background-color: #0a2d20 !important;
    border-right: 1px solid #1a5c3a;
}
section[data-testid="stSidebar"] * { color: #a8d5b5; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] strong { color: #e8f5e9 !important; }

h1, h2, h3, h4, h5, h6 { color: #e8f5e9 !important; }
p, li { color: #c8e6c9; }

div[data-testid="metric-container"] {
    background-color: #1a5c3a;
    border: 1px solid #2d9c6e;
    border-radius: 10px;
    padding: 16px 20px;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #69d9a0 !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #a8d5b5 !important;
}

details {
    background-color: #1a4a35 !important;
    border: 1px solid #2d9c6e !important;
    border-radius: 8px !important;
    padding: 4px 0 !important;
}
details summary { color: #e8f5e9 !important; font-style: italic; }

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #1a4a35 !important;
    color: #e8f5e9 !important;
    border: 1px solid #2d9c6e !important;
    border-radius: 6px !important;
}
.stSelectbox > div > div {
    background-color: #1a4a35 !important;
    border: 1px solid #2d9c6e !important;
    border-radius: 6px !important;
    color: #e8f5e9 !important;
}

.stButton > button {
    background-color: #2d9c6e !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
}
.stButton > button:hover { background-color: #3dbf87 !important; }

.stDownloadButton > button {
    background-color: #1a5c3a !important;
    color: #69d9a0 !important;
    border: 1px solid #2d9c6e !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover { background-color: #1a4a35 !important; }

.stTabs [data-baseweb="tab-list"] {
    background-color: #0a2d20 !important;
    border-radius: 8px 8px 0 0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] { color: #a8d5b5 !important; }
.stTabs [aria-selected="true"] {
    color: #69d9a0 !important;
    border-bottom: 2px solid #2d9c6e !important;
}

.stDataFrame, .dataframe { background-color: #1a4a35 !important; }

.stForm > div {
    background-color: #1a4a35 !important;
    border: 1px solid #2d9c6e !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

.stCheckbox label { color: #c8e6c9 !important; }
.stRadio label { color: #a8d5b5 !important; }

.hero-banner {
    background: linear-gradient(135deg, #1a5c3a 0%, #0a2d20 100%);
    border: 1px solid #2d9c6e;
    border-radius: 12px;
    padding: 32px 40px;
    margin-bottom: 24px;
}
.hero-banner h1 { font-size: 2.2rem !important; margin: 0 0 10px 0; }
.hero-banner p { color: #a8d5b5; font-size: 1.05rem; margin: 0; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# Initialise DB on every cold start
init_db()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 MoroccoMetaDB")
    st.markdown("*Open phytochemical database of North African medicinal plants*")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "Search plants",
            "Search compounds",
            "Search bioactivities",
            "Docking results",
            "Add entry",
            "Export data",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<small>🎓 <strong>Marouane Takie</strong><br>"
        "PhD candidate · USMBA Fès, Morocco<br>"
        "<a href='https://orcid.org/0009-0009-8621-8548' style='color:#69d9a0'>"
        "ORCID 0009-0009-8621-8548</a></small>",
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <h1>🌿 MoroccoMetaDB</h1>
        <p>
        Open phytochemical database of North African medicinal plants — curated
        UPLC-ESI-MS profiles, bioactivities (DPPH · ABTS · MTT · MIC),
        molecular docking results, and ethnobotanical records for
        <em>Erodium moschatum</em> and <em>Reseda alba</em>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_stats()
    t = stats["totals"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Plants",        t["plants"])
    c2.metric("Compounds",     t["compounds"])
    c3.metric("Bioactivities", t["bioactivities"])
    c4.metric("Docking hits",  t["docking_results"])
    c5.metric("References",    t["references"])

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.subheader("Plants by Country")
        if stats["by_country"]:
            df_c = pd.DataFrame(stats["by_country"])
            st.bar_chart(df_c.set_index("country")["n"])
        else:
            st.info("No data yet.")

        st.subheader("Top Families")
        if stats["by_family"]:
            df_f = pd.DataFrame(stats["by_family"]).rename(
                columns={"family": "Family", "n": "Plants"}
            )
            st.dataframe(df_f, use_container_width=True, hide_index=True)
        else:
            st.info("No data yet.")

    with right:
        st.subheader("Compound Classes")
        if stats["by_class"]:
            df_cl = pd.DataFrame(stats["by_class"])
            st.bar_chart(df_cl.set_index("class")["n"])
        else:
            st.info("No data yet.")

        st.subheader("Most Active Plants")
        if stats["most_active_plants"]:
            df_a = pd.DataFrame(stats["most_active_plants"]).rename(
                columns={"scientific_name": "Plant", "n_activities": "Activities"}
            )
            st.dataframe(df_a, use_container_width=True, hide_index=True)
        else:
            st.info("No data yet.")

# ═══════════════════════════════════════════════════════════════════════════
# SEARCH PLANTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Search plants":
    st.title("Search Plants")

    all_plants = get_all_plants()
    countries = sorted({p["country"] for p in all_plants if p.get("country")})
    families  = sorted({p["family"]  for p in all_plants if p.get("family")})

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        query = st.text_input("Name (scientific or common)", placeholder="e.g. Erodium")
    with col2:
        country = st.selectbox("Country", ["All"] + countries)
    with col3:
        family = st.selectbox("Family", ["All"] + families)

    results = search_plants(
        query=query or None,
        country=None if country == "All" else country,
        family=None if family == "All" else family,
    )
    st.markdown(f"**{len(results)} plant(s) found**")

    for plant in results:
        label = f"🌱 *{plant['scientific_name']}* — {plant.get('common_name_en', '')}"
        with st.expander(label):
            info_col, meta_col = st.columns([2, 1])
            with info_col:
                st.markdown(f"**Arabic:** {plant.get('common_name_ar') or '—'}")
                st.markdown(f"**French:** {plant.get('common_name_fr') or '—'}")
                st.markdown(f"**Family:** {plant.get('family') or '—'}")
                st.markdown(
                    f"**Region:** {plant.get('region') or '—'}, "
                    f"{plant.get('country') or '—'}"
                )
                if plant.get("traditional_use"):
                    st.markdown(f"**Traditional use:** {plant['traditional_use']}")
            with meta_col:
                st.markdown(f"**Endemic:** {'Yes' if plant.get('is_endemic') else 'No'}")
                st.markdown(f"**Added:** {(plant.get('created_at') or '')[:10]}")

            t1, t2, t3, t4, t5 = st.tabs(
                ["Compounds", "Bioactivities", "Ethnobotany", "Docking", "References"]
            )
            with t1:
                cpds = get_compounds(plant["id"])
                if cpds:
                    show_cols = ["name", "class", "subclass", "molecular_formula",
                                 "mz_observed", "adduct", "ionization_mode"]
                    df = pd.DataFrame(cpds)[[c for c in show_cols if c in pd.DataFrame(cpds).columns]]
                    df.columns = ["Compound", "Class", "Subclass", "Formula",
                                  "m/z", "Adduct", "Mode"][:len(df.columns)]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No compounds recorded.")

            with t2:
                bioacts = get_bioactivities(plant["id"])
                if bioacts:
                    show_cols = ["assay_type", "activity_category", "value", "unit",
                                 "value_type", "reference_compound", "reference_value",
                                 "model_organism"]
                    df = pd.DataFrame(bioacts)[[c for c in show_cols
                                                if c in pd.DataFrame(bioacts).columns]]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No bioactivities recorded.")

            with t3:
                ethno = get_ethnobotany(plant["id"])
                if ethno:
                    show_cols = ["use_category", "plant_part", "preparation",
                                 "administration", "region"]
                    df = pd.DataFrame(ethno)[[c for c in show_cols
                                              if c in pd.DataFrame(ethno).columns]]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No ethnobotanical data recorded.")

            with t4:
                all_docking = get_docking_results()
                plant_docking = [d for d in all_docking if d.get("plant_id") == plant["id"]]
                if plant_docking:
                    show_cols = ["compound_name", "target_name", "target_pdb_id",
                                 "binding_energy", "software", "key_residues"]
                    df = pd.DataFrame(plant_docking)[[c for c in show_cols
                                                      if c in pd.DataFrame(plant_docking).columns]]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No docking results recorded.")

            with t5:
                refs = get_references(plant["id"])
                if refs:
                    for ref in refs:
                        doi_link = (
                            f"[{ref.get('doi')}](https://doi.org/{ref.get('doi')})"
                            if ref.get("doi") else "—"
                        )
                        st.markdown(
                            f"- **{ref.get('authors', '')}** ({ref.get('year', '')}). "
                            f"{ref.get('title', '')}. *{ref.get('journal', '')}*. "
                            f"DOI: {doi_link}"
                        )
                else:
                    st.info("No references recorded.")

# ═══════════════════════════════════════════════════════════════════════════
# SEARCH COMPOUNDS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Search compounds":
    st.title("Search Compounds")

    all_cpds = search_compounds()
    classes  = sorted({c["class"] for c in all_cpds if c.get("class")})

    col1, col2 = st.columns([3, 2])
    with col1:
        query = st.text_input("Compound name", placeholder="e.g. Quercetin")
    with col2:
        class_ = st.selectbox("Class", ["All"] + classes)

    results = search_compounds(
        query=query or None,
        class_=None if class_ == "All" else class_,
    )
    st.markdown(f"**{len(results)} compound(s) found**")

    if results:
        df = pd.DataFrame(results)
        show_cols = ["name", "class", "subclass", "molecular_formula",
                     "molecular_weight", "mz_observed", "adduct",
                     "ionization_mode", "scientific_name"]
        df = df[[c for c in show_cols if c in df.columns]]
        df = df.rename(columns={
            "name": "Compound", "class": "Class", "subclass": "Subclass",
            "molecular_formula": "Formula", "molecular_weight": "MW (Da)",
            "mz_observed": "m/z", "adduct": "Adduct",
            "ionization_mode": "Mode", "scientific_name": "Plant",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# SEARCH BIOACTIVITIES
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Search bioactivities":
    st.title("Search Bioactivities")

    all_bio     = search_bioactivities()
    assay_types = sorted({b["assay_type"] for b in all_bio if b.get("assay_type")})

    col1, col2 = st.columns([2, 2])
    with col1:
        assay = st.selectbox("Assay type", ["All"] + assay_types)
    with col2:
        max_ic50 = st.number_input(
            "Max value (IC50 / µg/mL)", min_value=0.0, value=1000.0, step=10.0
        )

    results = search_bioactivities(
        assay_type=None if assay == "All" else assay,
        max_value=max_ic50 if max_ic50 < 1000.0 else None,
    )
    st.markdown(f"**{len(results)} result(s) found**")

    if results:
        df = pd.DataFrame(results)
        show_cols = ["scientific_name", "assay_type", "activity_category",
                     "value", "unit", "value_type",
                     "reference_compound", "reference_value", "model_organism"]
        df = df[[c for c in show_cols if c in df.columns]]
        df = df.rename(columns={
            "scientific_name": "Plant", "assay_type": "Assay",
            "activity_category": "Category", "value": "Value",
            "unit": "Unit", "value_type": "Type",
            "reference_compound": "Ref. compound",
            "reference_value": "Ref. value", "model_organism": "Model",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# DOCKING RESULTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Docking results":
    st.title("Molecular Docking Results")

    all_docking = get_docking_results()
    targets = sorted({d["target_name"] for d in all_docking if d.get("target_name")})

    target = st.selectbox("Target protein", ["All"] + targets)
    results = get_docking_results(target_name=None if target == "All" else target)
    st.markdown(f"**{len(results)} docking result(s)**")

    if results:
        df = pd.DataFrame(results)
        show_cols = ["compound_name", "scientific_name", "target_name",
                     "target_pdb_id", "binding_energy", "software",
                     "h_bonds", "key_residues"]
        df_display = df[[c for c in show_cols if c in df.columns]].rename(columns={
            "compound_name": "Compound", "scientific_name": "Plant",
            "target_name": "Target", "target_pdb_id": "PDB ID",
            "binding_energy": "ΔG (kcal/mol)", "software": "Software",
            "h_bonds": "H-bonds", "key_residues": "Key residues",
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        if "binding_energy" in df.columns and len(df) > 1:
            st.subheader("Binding Energy Comparison")
            chart_df = df[["compound_name", "binding_energy"]].dropna()
            if not chart_df.empty:
                st.bar_chart(chart_df.set_index("compound_name")["binding_energy"])
    else:
        st.info("No docking results in database. Add entries via the Add entry page.")

# ═══════════════════════════════════════════════════════════════════════════
# ADD ENTRY
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Add entry":
    st.title("Add New Entry")

    tab_plant, tab_cpd, tab_bio, tab_ethno = st.tabs(
        ["🌱 Plant", "🧪 Compound", "📊 Bioactivity", "📖 Ethnobotany"]
    )

    # ── Add plant ──────────────────────────────────────────────────────
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
            country = c6.text_input("Country", value="Morocco")
            region  = c7.text_input("Region")
            endemic  = st.checkbox("Endemic species")
            trad_use = st.text_area("Traditional use")
            if st.form_submit_button("Add Plant"):
                if not sci_name.strip():
                    st.error("Scientific name is required.")
                else:
                    pid = add_plant(
                        scientific_name=sci_name.strip(),
                        common_name_ar=ar or None, common_name_fr=fr or None,
                        common_name_en=en or None, family=family or None,
                        genus=genus or None, country=country or None,
                        region=region or None, is_endemic=int(endemic),
                        traditional_use=trad_use or None,
                    )
                    st.success(f"Plant added — ID {pid}.")

    # ── Add compound ───────────────────────────────────────────────────
    with tab_cpd:
        st.subheader("Add Compound")
        plants = get_all_plants()
        plant_map = {f"{p['scientific_name']} (id={p['id']})": p["id"] for p in plants}
        with st.form("form_compound"):
            if not plant_map:
                st.warning("No plants in database. Add a plant first.")
                plant_id_sel = None
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
                        cid = add_compound(
                            plant_id=plant_id_sel, name=cname.strip(),
                            class_=cls or None, subclass=subcls or None,
                            molecular_formula=formula or None,
                            molecular_weight=mw if mw > 0 else None,
                            mz_observed=mz if mz > 0 else None,
                            ionization_mode=mode, adduct=adduct or None,
                            detection_method=method or None,
                        )
                        st.success(f"Compound added — ID {cid}.")

    # ── Add bioactivity ────────────────────────────────────────────────
    with tab_bio:
        st.subheader("Add Bioactivity")
        plants = get_all_plants()
        plant_map = {f"{p['scientific_name']} (id={p['id']})": p["id"] for p in plants}
        with st.form("form_bioactivity"):
            if not plant_map:
                st.warning("No plants in database.")
                plant_id_sel = None
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
                vtype = c5.selectbox(
                    "Value type",
                    ["IC50", "EC50", "inhibition%", "MIC", "other"],
                )
                c6, c7 = st.columns(2)
                ref_cpd = c6.text_input("Reference compound", placeholder="Ascorbic acid")
                ref_val = c7.number_input("Reference value", min_value=0.0, value=0.0)
                model = st.text_input("Model organism", placeholder="MCF-7 / Wistar rat")
                if st.form_submit_button("Add Bioactivity"):
                    bid = add_bioactivity(
                        plant_id=plant_id_sel, assay_type=assay,
                        value=value if value > 0 else None,
                        unit=unit or None, value_type=vtype,
                        activity_category=category or None,
                        reference_compound=ref_cpd or None,
                        reference_value=ref_val if ref_val > 0 else None,
                        model_organism=model or None,
                    )
                    st.success(f"Bioactivity added — ID {bid}.")

    # ── Add ethnobotany ────────────────────────────────────────────────
    with tab_ethno:
        st.subheader("Add Ethnobotany")
        plants = get_all_plants()
        plant_map = {f"{p['scientific_name']} (id={p['id']})": p["id"] for p in plants}
        with st.form("form_ethno"):
            if not plant_map:
                st.warning("No plants in database.")
                plant_id_sel = None
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
                    eid = add_ethnobotany(
                        plant_id=plant_id_sel,
                        use_category=use_cat or None,
                        plant_part=plant_part or None,
                        preparation=prep or None,
                        administration=admin or None,
                        region=region_et or None,
                        notes=notes_et or None,
                    )
                    st.success(f"Ethnobotany entry added — ID {eid}.")

# ═══════════════════════════════════════════════════════════════════════════
# EXPORT DATA
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Export data":
    st.title("Export Data")
    st.markdown("Download any table as CSV, or the entire database as a single JSON file.")

    plants_data  = get_all_plants()
    cpds_data    = search_compounds()
    bioacts_data = search_bioactivities()
    docking_data = get_docking_results()
    refs_data    = get_references()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            label="Plants CSV",
            data=pd.DataFrame(plants_data).to_csv(index=False).encode("utf-8"),
            file_name="morocco_metadb_plants.csv",
            mime="text/csv",
            disabled=not plants_data,
        )
    with c2:
        st.download_button(
            label="Compounds CSV",
            data=pd.DataFrame(cpds_data).to_csv(index=False).encode("utf-8"),
            file_name="morocco_metadb_compounds.csv",
            mime="text/csv",
            disabled=not cpds_data,
        )
    with c3:
        st.download_button(
            label="Bioactivities CSV",
            data=pd.DataFrame(bioacts_data).to_csv(index=False).encode("utf-8"),
            file_name="morocco_metadb_bioactivities.csv",
            mime="text/csv",
            disabled=not bioacts_data,
        )

    c4, c5, _ = st.columns(3)
    with c4:
        st.download_button(
            label="Docking CSV",
            data=pd.DataFrame(docking_data).to_csv(index=False).encode("utf-8") if docking_data else b"",
            file_name="morocco_metadb_docking.csv",
            mime="text/csv",
            disabled=not docking_data,
        )
    with c5:
        st.download_button(
            label="References CSV",
            data=pd.DataFrame(refs_data).to_csv(index=False).encode("utf-8") if refs_data else b"",
            file_name="morocco_metadb_references.csv",
            mime="text/csv",
            disabled=not refs_data,
        )

    st.markdown("---")
    st.subheader("Full JSON Export")
    full_json = json.dumps(
        {
            "plants":          plants_data,
            "compounds":       cpds_data,
            "bioactivities":   bioacts_data,
            "docking_results": docking_data,
            "references":      refs_data,
        },
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    st.download_button(
        label="Download Full Database JSON",
        data=full_json,
        file_name="morocco_metadb_full.json",
        mime="application/json",
    )

    st.markdown("**Records available for export:**")
    for label, data in [
        ("Plants", plants_data), ("Compounds", cpds_data),
        ("Bioactivities", bioacts_data), ("Docking results", docking_data),
        ("References", refs_data),
    ]:
        st.markdown(f"- {label}: **{len(data)}**")
