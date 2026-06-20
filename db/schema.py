import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "morocco_metadb.sqlite"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS plants (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            scientific_name  TEXT NOT NULL UNIQUE,
            common_name_ar   TEXT,
            common_name_fr   TEXT,
            common_name_en   TEXT,
            family           TEXT,
            genus            TEXT,
            species          TEXT,
            country          TEXT,
            region           TEXT,
            is_endemic       INTEGER DEFAULT 0,
            traditional_use  TEXT,
            created_at       TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ethnobotany (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id       INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
            use_category   TEXT,
            plant_part     TEXT,
            preparation    TEXT,
            administration TEXT,
            region         TEXT,
            source_ref     TEXT,
            notes          TEXT
        );

        CREATE TABLE IF NOT EXISTS compounds (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id         INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
            name             TEXT NOT NULL,
            class            TEXT,
            subclass         TEXT,
            molecular_formula TEXT,
            molecular_weight  REAL,
            smiles           TEXT,
            inchikey         TEXT,
            pubchem_cid      INTEGER,
            detection_method TEXT,
            mz_observed      REAL,
            ionization_mode  TEXT,
            rt_min           REAL,
            fragment_ions    TEXT,
            adduct           TEXT,
            notes            TEXT
        );

        CREATE TABLE IF NOT EXISTS bioactivities (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id           INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
            compound_id        INTEGER REFERENCES compounds(id),
            assay_type         TEXT NOT NULL,
            activity_category  TEXT,
            value              REAL,
            unit               TEXT,
            value_type         TEXT,
            extract_type       TEXT,
            reference_compound TEXT,
            reference_value    REAL,
            reference_unit     TEXT,
            model_organism     TEXT,
            notes              TEXT
        );

        CREATE TABLE IF NOT EXISTS docking_results (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            compound_id    INTEGER NOT NULL REFERENCES compounds(id) ON DELETE CASCADE,
            plant_id       INTEGER REFERENCES plants(id),
            target_name    TEXT NOT NULL,
            target_pdb_id  TEXT,
            software       TEXT,
            binding_energy REAL,
            rmsd_lb        REAL,
            rmsd_ub        REAL,
            h_bonds        TEXT,
            hydrophobic    TEXT,
            key_residues   TEXT,
            docking_mode   TEXT,
            notes          TEXT
        );

        CREATE TABLE IF NOT EXISTS references_ (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            doi     TEXT UNIQUE,
            title   TEXT,
            authors TEXT,
            journal TEXT,
            year    INTEGER,
            volume  TEXT,
            pages   TEXT,
            pmid    TEXT,
            url     TEXT,
            notes   TEXT
        );

        CREATE TABLE IF NOT EXISTS plant_references (
            plant_id     INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
            reference_id INTEGER NOT NULL REFERENCES references_(id) ON DELETE CASCADE,
            PRIMARY KEY (plant_id, reference_id)
        );

        CREATE INDEX IF NOT EXISTS idx_plants_country    ON plants(country);
        CREATE INDEX IF NOT EXISTS idx_plants_family     ON plants(family);
        CREATE INDEX IF NOT EXISTS idx_compounds_class   ON compounds(class);
        CREATE INDEX IF NOT EXISTS idx_bioact_assay      ON bioactivities(assay_type);
        CREATE INDEX IF NOT EXISTS idx_docking_target    ON docking_results(target_name);
    """)
    conn.commit()
    conn.close()
