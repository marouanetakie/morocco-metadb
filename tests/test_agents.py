from db.schema import init_db
from db.crud import (add_plant, get_plant, search_plants,
    add_compound, get_compounds, add_bioactivity,
    get_bioactivities, get_stats)

def test_db_init():
    init_db()

def test_add_and_get_plant():
    pid = add_plant("Test plant", family="Testaceae", country="Morocco")
    plant = get_plant(pid)
    assert plant["scientific_name"] == "Test plant"
    assert plant["family"] == "Testaceae"

def test_search_plants():
    results = search_plants("Erodium")
    assert len(results) >= 1
    assert results[0]["scientific_name"] == "Erodium moschatum"

def test_add_compound():
    pid = search_plants("Erodium")[0]["id"]
    cid = add_compound(pid, "Test compound", compound_class="flavonoid")
    compounds = get_compounds(pid)
    assert any(c["name"] == "Test compound" for c in compounds)

def test_add_bioactivity():
    pid = search_plants("Erodium")[0]["id"]
    bid = add_bioactivity(pid, "DPPH", 45.2, "µg/mL", "IC50")
    bio = get_bioactivities(pid)
    assert any(b["assay_type"] == "DPPH" for b in bio)

def test_get_stats():
    stats = get_stats()
    assert stats["total_plants"] >= 32
    assert stats["total_compounds"] >= 186
    assert stats["total_references"] >= 283
