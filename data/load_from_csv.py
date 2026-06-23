"""
Load pre-exported CSV snapshots into the SQLite database.
Called on Streamlit Cloud startup when the DB is empty.
"""
import os
import pandas as pd
from db.schema import init_db, get_connection

_DATA_DIR = os.path.join(os.path.dirname(__file__))

_TABLES = [
    ("plants",            "plants_export.csv"),
    ("compounds",         "compounds_export.csv"),
    ("bioactivities",     "bioactivities_export.csv"),
    ("ethnobotany",       "ethnobotany_export.csv"),
    ("references_",       "references_export.csv"),
    ("docking_results",   "docking_results_export.csv"),
]


def load_all_data():
    init_db()
    conn = get_connection()
    try:
        for table, fname in _TABLES:
            fpath = os.path.join(_DATA_DIR, fname)
            if not os.path.exists(fpath):
                print(f"  [skip] {fname} not found")
                continue
            df = pd.read_csv(fpath)
            if df.empty:
                print(f"  [skip] {fname} is empty")
                continue
            # Use append so init_db() schema (FK constraints, indexes) is preserved
            df.to_sql(table, conn, if_exists="append", index=False)
            print(f"  Loaded {len(df):>5} rows -> {table}")
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    load_all_data()
