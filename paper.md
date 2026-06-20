---
title: "MoroccoMetaDB: An open phytochemical database of North African medicinal plants"
tags:
  - phytochemistry
  - medicinal plants
  - North Africa
  - Morocco
  - UPLC-ESI-MS
  - molecular docking
  - ethnobotany
  - open database
  - Python
  - Streamlit
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

MoroccoMetaDB is a structured, open-access SQLite-backed database and Streamlit web interface for curating phytochemical profiles, biological activities, molecular docking results, and ethnobotanical records of medicinal plants from Morocco and North Africa. The database currently contains 32 plant species with over 186 compounds, 122 bioactivity measurements, and 283 literature references sourced from PubMed.

# Statement of need

North African medicinal flora represents an underexplored reservoir of bioactive natural products. Despite a rich ethnobotanical heritage, phytochemical and pharmacological data on Moroccan medicinal plants remain scattered across thousands of journal articles with no centralized, machine-readable repository. MoroccoMetaDB addresses this gap by providing a normalized relational database with a web interface for querying, visualizing, and exporting data, coupled with a literature mining pipeline that integrates PubMed E-utilities and AI-assisted extraction.

# Implementation

The database is built on SQLite with seven normalized tables covering plants, compounds, bioactivities, docking results, ethnobotany records, references, and plant-reference links. The Streamlit frontend enables interactive search, filtering, and CSV/JSON export. A literature mining agent automates PubMed searches and structured data extraction.

# Acknowledgements

The authors acknowledge the support of USMBA and the LBCVB laboratory.
