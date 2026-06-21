---
title: 'MoroccoMetaDB: An open phytochemical database of North African medicinal plants'
tags:
  - Python
  - phytochemistry
  - natural products
  - medicinal plants
  - North Africa
  - database
  - pharmacology
authors:
  - name: Marouane Takie
    orcid: 0009-0009-8621-8548
    affiliation: 1
  - name: Badiaa Lyoussi
    affiliation: 1
  - name: Ahmed Samir Benjelloun
    affiliation: 1
affiliations:
  - name: Laboratory of Biotechnology, Conservation and Valorization of Bioresources (LBCVB), Faculty of Sciences Dhar El Mahraz, Sidi Mohamed Ben Abdallah University (USMBA), Fès, Morocco
    index: 1
date: 20 June 2026
bibliography: paper.bib
---

# Summary

Phytochemical studies of North African medicinal plants generate compound identifications, biological activity measurements, molecular docking results, and ethnobotanical records. These data are published across hundreds of journal articles and exist in no shared, structured repository. MoroccoMetaDB is an open-access database and web application that stores and links this information for plants from Morocco, Algeria, Tunisia, Libya, and Egypt.

Each plant entry holds up to seven data types: taxonomic classification; phytochemical compounds with detection method, m/z values, and molecular formula (from UPLC-ESI-MS or GC-MS); quantitative bioactivity values (IC50, MIC, MBC) for antioxidant, antidiabetic, antimicrobial, and cytotoxic assays; molecular docking results against named protein targets; ethnobotanical uses with preparation method and regional source; literature references with DOIs and PubMed IDs. A Streamlit web interface supports search, filtering, tabbed plant profiles, and CSV/JSON export.

# Statement of need

Established natural product databases — KNApSAcK [@KNApSAcK], LOTUS [@LOTUS], the UNPD [@UNPD] — cover broad global flora. None restricts scope to North Africa, and none links compound identification records to quantitative bioactivity data, docking results, and ethnobotanical notes within a single relational schema. In practice, a researcher working on an Algerian plant runs separate searches for compounds, for IC50 values, for docking literature, and for traditional use records, then assembles the results manually. MoroccoMetaDB makes those four searches one.

The underrepresentation is a data problem as much as a visibility problem. Morocco has approximately 4,500 vascular plant species, around 800 of which appear in traditional medicine [@Moroccan_flora]. Published studies on these plants exist; a database that aggregates them does not. The same applies to the flora of Algeria, Tunisia, Libya, and Egypt.

# Functionality

MoroccoMetaDB uses a SQLite relational database with seven tables. Foreign key constraints link compounds to source plants, bioactivities to compounds or plants, docking results to compounds and targets, and references to plants through a many-to-many join. A query such as "all flavonoids from Lamiaceae species with alpha-glucosidase IC50 below 50 µg/mL, with their docking binding energies against 5NN5" runs against this schema without joining external sources.

A PubMed mining agent calls the NCBI Entrez API for a given plant name, retrieves article metadata, and passes abstract text to the Claude API (Anthropic) to extract compound, bioactivity, and ethnobotanical fields directly into the database tables. Ten plants with 10 papers each can be processed in under 10 minutes.

The Streamlit interface has seven pages: a dashboard showing database coverage by country and compound class; plant search with expandable profiles and five data tabs; compound and bioactivity search with class and value filters; a docking results table with binding energy charts; data entry forms for manual additions; and bulk export in CSV and JSON.

# Current data

The current release contains 53 plant species spanning three North African countries — Morocco (33), Algeria (10), and Tunisia (10) — with 307 phytochemical compounds in five classes (terpenoids 101, flavonoids 99, polyphenols 50, alkaloids 27, other 27, fatty acids 3), 203 bioactivity measurements, and 408 references with verified PubMed identifiers. Chemically notable entries include: *Peganum harmala* (beta-carboline alkaloids: harmine, harmaline, vasicine); *Withania somnifera* (withanolide steroidal lactones, MTT IC50 = 15.8 µg/mL — strongest cytotoxicity in the database); *Pancratium maritimum* (Amaryllidaceae alkaloids: lycorine, pancratistatin, narciclasine, MTT IC50 = 18.4 µg/mL); and *Atriplex halimus* (antidiabetic halophyte with alpha-glucosidase IC50 = 48.3 µg/mL, used across Morocco, Algeria, and Tunisia). The Algerian cohort adds Saharan endemics including *Anvillea radiata* (anvilleain A sesquiterpene lactone) and *Oudneya africana* (glucosinolates); the Tunisian cohort covers coastal species (*Cakile maritima*, sea-rocket glucosinolates) and Mediterranean halophytes (*Suaeda fruticosa*, *Mesembryanthemum crystallinum*).

# Future development

Planned work includes expanding plant coverage to 200+ species across all five North African countries, adding ADMET profiling for each compound record via RDKit and the SwissADME API, and connecting the database to a companion AutoDock Vina pipeline so docking results populate automatically from .log file output. A weekly PubMed alert workflow is also planned to keep the literature coverage current without manual monitoring.

# References
