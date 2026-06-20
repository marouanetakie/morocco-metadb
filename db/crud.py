from db.schema import get_connection


# ── Plants ────────────────────────────────────────────────────────────────

def add_plant(scientific_name, common_name_ar=None, common_name_fr=None,
              common_name_en=None, family=None, genus=None, species=None,
              country=None, region=None, is_endemic=0, traditional_use=None):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT OR IGNORE INTO plants
               (scientific_name, common_name_ar, common_name_fr, common_name_en,
                family, genus, species, country, region, is_endemic, traditional_use)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (scientific_name, common_name_ar, common_name_fr, common_name_en,
             family, genus, species, country, region, is_endemic, traditional_use)
        )
        conn.commit()
        row = conn.execute(
            "SELECT id FROM plants WHERE scientific_name=?", (scientific_name,)
        ).fetchone()
        return row["id"] if row else None
    finally:
        conn.close()


def get_plant(plant_id):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM plants WHERE id=?", (plant_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_plants():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM plants ORDER BY scientific_name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_plants(query=None, country=None, family=None):
    conn = get_connection()
    try:
        sql = "SELECT * FROM plants WHERE 1=1"
        params = []
        if query:
            q = f"%{query}%"
            sql += (" AND (scientific_name LIKE ? OR common_name_en LIKE ?"
                    " OR common_name_ar LIKE ? OR common_name_fr LIKE ?)")
            params.extend([q, q, q, q])
        if country:
            sql += " AND country=?"
            params.append(country)
        if family:
            sql += " AND family=?"
            params.append(family)
        sql += " ORDER BY scientific_name"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Compounds ─────────────────────────────────────────────────────────────

def add_compound(plant_id, name, class_=None, subclass=None,
                 molecular_formula=None, molecular_weight=None,
                 smiles=None, inchikey=None, pubchem_cid=None,
                 detection_method=None, mz_observed=None,
                 ionization_mode=None, rt_min=None,
                 fragment_ions=None, adduct=None, notes=None):
    conn = get_connection()
    try:
        c = conn.execute(
            """INSERT INTO compounds
               (plant_id, name, class, subclass, molecular_formula,
                molecular_weight, smiles, inchikey, pubchem_cid,
                detection_method, mz_observed, ionization_mode,
                rt_min, fragment_ions, adduct, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (plant_id, name, class_, subclass, molecular_formula,
             molecular_weight, smiles, inchikey, pubchem_cid,
             detection_method, mz_observed, ionization_mode,
             rt_min, fragment_ions, adduct, notes)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()


def get_compounds(plant_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM compounds WHERE plant_id=? ORDER BY name", (plant_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_compounds(query=None, class_=None):
    conn = get_connection()
    try:
        sql = """SELECT c.*, p.scientific_name
                 FROM compounds c JOIN plants p ON c.plant_id=p.id
                 WHERE 1=1"""
        params = []
        if query:
            sql += " AND c.name LIKE ?"
            params.append(f"%{query}%")
        if class_:
            sql += " AND c.class=?"
            params.append(class_)
        sql += " ORDER BY c.name"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Bioactivities ─────────────────────────────────────────────────────────

def add_bioactivity(plant_id, assay_type, value=None, unit=None,
                    value_type=None, compound_id=None, activity_category=None,
                    extract_type=None, reference_compound=None,
                    reference_value=None, reference_unit=None,
                    model_organism=None, notes=None):
    conn = get_connection()
    try:
        c = conn.execute(
            """INSERT INTO bioactivities
               (plant_id, compound_id, assay_type, activity_category, value,
                unit, value_type, extract_type, reference_compound,
                reference_value, reference_unit, model_organism, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (plant_id, compound_id, assay_type, activity_category, value,
             unit, value_type, extract_type, reference_compound,
             reference_value, reference_unit, model_organism, notes)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()


def get_bioactivities(plant_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM bioactivities WHERE plant_id=? ORDER BY assay_type",
            (plant_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_bioactivities(assay_type=None, max_value=None):
    conn = get_connection()
    try:
        sql = """SELECT b.*, p.scientific_name
                 FROM bioactivities b JOIN plants p ON b.plant_id=p.id
                 WHERE 1=1"""
        params = []
        if assay_type:
            sql += " AND b.assay_type=?"
            params.append(assay_type)
        if max_value is not None:
            sql += " AND b.value<=?"
            params.append(max_value)
        sql += " ORDER BY b.value"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Docking results ───────────────────────────────────────────────────────

def add_docking_result(compound_id, target_name, plant_id=None,
                       target_pdb_id=None, software=None,
                       binding_energy=None, rmsd_lb=None, rmsd_ub=None,
                       h_bonds=None, hydrophobic=None, key_residues=None,
                       docking_mode=None, notes=None):
    conn = get_connection()
    try:
        c = conn.execute(
            """INSERT INTO docking_results
               (compound_id, plant_id, target_name, target_pdb_id, software,
                binding_energy, rmsd_lb, rmsd_ub, h_bonds, hydrophobic,
                key_residues, docking_mode, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (compound_id, plant_id, target_name, target_pdb_id, software,
             binding_energy, rmsd_lb, rmsd_ub, h_bonds, hydrophobic,
             key_residues, docking_mode, notes)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()


def get_docking_results(target_name=None):
    conn = get_connection()
    try:
        sql = """SELECT d.*, c.name AS compound_name, p.scientific_name
                 FROM docking_results d
                 JOIN compounds c ON d.compound_id=c.id
                 LEFT JOIN plants p ON d.plant_id=p.id
                 WHERE 1=1"""
        params = []
        if target_name:
            sql += " AND d.target_name=?"
            params.append(target_name)
        sql += " ORDER BY d.binding_energy"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Ethnobotany ───────────────────────────────────────────────────────────

def add_ethnobotany(plant_id, use_category=None, plant_part=None,
                    preparation=None, administration=None, region=None,
                    source_ref=None, notes=None):
    conn = get_connection()
    try:
        c = conn.execute(
            """INSERT INTO ethnobotany
               (plant_id, use_category, plant_part, preparation,
                administration, region, source_ref, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (plant_id, use_category, plant_part, preparation,
             administration, region, source_ref, notes)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()


def get_ethnobotany(plant_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM ethnobotany WHERE plant_id=?", (plant_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── References ────────────────────────────────────────────────────────────

def add_reference(doi=None, title=None, authors=None, journal=None,
                  year=None, volume=None, pages=None, pmid=None,
                  url=None, notes=None):
    conn = get_connection()
    try:
        c = conn.execute(
            """INSERT OR IGNORE INTO references_
               (doi, title, authors, journal, year, volume, pages, pmid, url, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (doi, title, authors, journal, year, volume, pages, pmid, url, notes)
        )
        conn.commit()
        if c.rowcount > 0:
            return c.lastrowid
        if doi:
            row = conn.execute(
                "SELECT id FROM references_ WHERE doi=?", (doi,)
            ).fetchone()
            return row["id"] if row else None
        return None
    finally:
        conn.close()


def link_plant_reference(plant_id, reference_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO plant_references (plant_id, reference_id) VALUES (?,?)",
            (plant_id, reference_id)
        )
        conn.commit()
    finally:
        conn.close()


def get_references(plant_id=None):
    conn = get_connection()
    try:
        if plant_id is not None:
            rows = conn.execute(
                """SELECT r.* FROM references_ r
                   JOIN plant_references pr ON r.id=pr.reference_id
                   WHERE pr.plant_id=? ORDER BY r.year DESC""",
                (plant_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM references_ ORDER BY year DESC"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Stats (dashboard) ─────────────────────────────────────────────────────

def get_stats():
    conn = get_connection()
    try:
        totals = {
            "plants":         conn.execute("SELECT COUNT(*) FROM plants").fetchone()[0],
            "compounds":      conn.execute("SELECT COUNT(*) FROM compounds").fetchone()[0],
            "bioactivities":  conn.execute("SELECT COUNT(*) FROM bioactivities").fetchone()[0],
            "docking_results":conn.execute("SELECT COUNT(*) FROM docking_results").fetchone()[0],
            "references":     conn.execute("SELECT COUNT(*) FROM references_").fetchone()[0],
        }
        by_country = conn.execute(
            """SELECT country, COUNT(*) AS n FROM plants
               WHERE country IS NOT NULL GROUP BY country ORDER BY n DESC"""
        ).fetchall()
        by_family = conn.execute(
            """SELECT family, COUNT(*) AS n FROM plants
               WHERE family IS NOT NULL GROUP BY family ORDER BY n DESC LIMIT 10"""
        ).fetchall()
        by_class = conn.execute(
            """SELECT class, COUNT(*) AS n FROM compounds
               WHERE class IS NOT NULL GROUP BY class ORDER BY n DESC LIMIT 10"""
        ).fetchall()
        by_assay = conn.execute(
            """SELECT assay_type, COUNT(*) AS n FROM bioactivities
               GROUP BY assay_type ORDER BY n DESC"""
        ).fetchall()
        by_target = conn.execute(
            """SELECT target_name, COUNT(*) AS n FROM docking_results
               GROUP BY target_name ORDER BY n DESC LIMIT 10"""
        ).fetchall()
        most_active = conn.execute(
            """SELECT p.scientific_name, COUNT(b.id) AS n_activities
               FROM plants p LEFT JOIN bioactivities b ON p.id=b.plant_id
               GROUP BY p.id ORDER BY n_activities DESC LIMIT 10"""
        ).fetchall()
        return {
            "totals":              totals,
            "by_country":          [dict(r) for r in by_country],
            "by_family":           [dict(r) for r in by_family],
            "by_class":            [dict(r) for r in by_class],
            "by_assay":            [dict(r) for r in by_assay],
            "by_target":           [dict(r) for r in by_target],
            "most_active_plants":  [dict(r) for r in most_active],
        }
    finally:
        conn.close()
