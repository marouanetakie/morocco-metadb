# MoroccoMetaDB 🌿

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20778483.svg)](https://doi.org/10.5281/zenodo.20778483)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://marouanetakie-morocco-metadb.streamlit.app)

**Open phytochemical database of North African medicinal plants**

MoroccoMetaDB is a structured, open-access SQLite-backed database and Streamlit web interface for curating UPLC-ESI-MS phytochemical profiles, biological activities (DPPH, ABTS, MTT, MIC…), molecular docking results (AutoDock Vina), and ethnobotanical records of medicinal plants from Morocco and North Africa.

**Currently covers:** *Erodium moschatum* (Geraniaceae) and *Reseda alba* (Resedaceae).

---

## Live demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://marouanetakie-morocco-metadb.streamlit.app)

---

## Features

- 🌿 **Plant records** — taxonomy, country/region, endemism, traditional use
- 🧪 **Compounds** — UPLC-ESI-MS data: m/z, RT, adduct, ionization mode, SMILES
- 📊 **Bioactivities** — IC50/EC50 for DPPH, ABTS, FRAP, MTT, alpha-glucosidase, gastroprotective assays
- 🔬 **Docking results** — AutoDock Vina binding energies, H-bonds, key residues
- 📚 **References** — DOI-linked literature per plant
- 📥 **Export** — CSV per table + full JSON

---

## Installation

```bash
git clone https://github.com/marouanetakie/morocco-metadb.git
cd morocco-metadb
pip install -r requirements.txt
cp .env.example .env        # add your API keys
python data/seeds/seed_data.py
streamlit run ui/app.py
```

---

## Project structure

```
morocco-metadb/
├── db/
│   ├── schema.py           # SQLite schema (7 tables) + init_db()
│   └── crud.py             # All CRUD + get_stats()
├── agents/
│   └── literature_agent.py # PubMed search + Claude summarisation
├── ui/
│   └── app.py              # Streamlit web interface
├── data/seeds/
│   └── seed_data.py        # Real research data (Erodium, Reseda)
├── .streamlit/
│   └── config.toml         # Dark green theme
├── .env.example
├── requirements.txt
└── CITATION.cff
```

---

## Data schema

| Table | Key fields |
|---|---|
| `plants` | scientific_name, family, country, region, traditional_use |
| `compounds` | name, class, molecular_formula, m/z, adduct, ionization_mode |
| `bioactivities` | assay_type, value, unit, value_type, reference_compound |
| `docking_results` | target_name, binding_energy (kcal/mol), key_residues |
| `ethnobotany` | use_category, plant_part, preparation, administration |
| `references_` | doi, title, authors, journal, year |
| `plant_references` | plant–reference join table |

---

## Citation

If you use MoroccoMetaDB in your research, please cite:

```
Takie, M. (2026). MoroccoMetaDB: Open phytochemical database of North African
medicinal plants (Version 1.0.0). https://github.com/marouanetakie/morocco-metadb
```

GitHub displays a **"Cite this repository"** button automatically from the `CITATION.cff` file.

---

## Related publications

- Takie M. et al. (2026). Phytochemical profiling and biological activities of *Erodium moschatum*. *Scientific African*. [DOI: 10.1016/j.sciaf.2026.e03252](https://doi.org/10.1016/j.sciaf.2026.e03252)
- Takie M. et al. (2026). Biological activities and phytochemical analysis of *Reseda alba*. *Food Science & Nutrition*. [DOI: 10.1002/fsn3.71853](https://doi.org/10.1002/fsn3.71853)

---

## Author

**Marouane Takie**
PhD candidate, Phytochemistry & Computational Chemistry
Université Sidi Mohamed Ben Abdellah (USMBA), Fès, Morocco
[ORCID: 0009-0009-8621-8548](https://orcid.org/0009-0009-8621-8548) · [marouane.takie@usmba.ac.ma](mailto:marouane.takie@usmba.ac.ma)

---

## License

MIT © 2026 Marouane Takie
