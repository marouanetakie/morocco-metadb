# -*- coding: utf-8 -*-
"""
Batch literature mining script for 10 North African medicinal plants.
Usage: python3 mine_batch.py
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents.literature_agent import mine_plant
from db.schema import init_db
from db.crud import (
    add_plant, add_compound, add_bioactivity, add_ethnobotany,
    add_reference, link_plant_reference, get_all_plants, get_stats,
)

PLANTS = [
    # Batch 1
    "Lavandula stoechas",
    "Artemisia herba-alba",
    "Thymus maroccanus",
    "Mentha pulegium",
    "Rosmarinus officinalis",
    "Origanum compactum",
    "Cistus monspeliensis",
    "Pistacia lentiscus",
    "Tetraclinis articulata",
    "Argania spinosa",
    # Batch 2
    "Nigella sativa",
    "Opuntia ficus-indica",
    "Ziziphus lotus",
    "Ficus carica",
    "Urtica dioica",
    "Marrubium vulgare",
    "Salvia officinalis",
    "Globularia alypum",
    "Retama monosperma",
    "Peganum harmala",
]


def save_mined_plant(data: dict) -> int:
    p = data["plant"]
    plant_id = add_plant(
        scientific_name=p["scientific_name"],
        common_name_en=p.get("common_name_en"),
        common_name_fr=p.get("common_name_fr"),
        common_name_ar=p.get("common_name_ar"),
        family=p.get("family"),
        country=p.get("country", "Morocco"),
        region=p.get("region"),
        traditional_use=p.get("traditional_use"),
    )

    for cpd in data.get("compounds", []):
        add_compound(
            plant_id=plant_id,
            name=cpd["name"],
            class_=cpd.get("class"),
            subclass=cpd.get("subclass"),
            detection_method=cpd.get("detection_method"),
            notes=cpd.get("notes"),
        )

    for bio in data.get("bioactivities", []):
        add_bioactivity(
            plant_id=plant_id,
            assay_type=bio["assay_type"],
            value=bio.get("value"),
            unit=bio.get("unit"),
            value_type=bio.get("value_type"),
            activity_category=bio.get("activity_category"),
        )

    for ethno in data.get("ethnobotany", []):
        add_ethnobotany(
            plant_id=plant_id,
            use_category=ethno.get("use_category"),
            plant_part=ethno.get("plant_part"),
            preparation=ethno.get("preparation"),
            administration=ethno.get("administration"),
        )

    for ref in data.get("references", []):
        year = ref.get("year")
        try:
            year = int(year) if year and str(year).strip().isdigit() else None
        except (ValueError, TypeError):
            year = None

        ref_id = add_reference(
            doi=ref.get("doi"),
            title=ref.get("title"),
            authors=ref.get("authors"),
            journal=ref.get("journal"),
            year=year,
            pmid=ref.get("pmid"),
        )
        if ref_id:
            link_plant_reference(plant_id, ref_id)

    return plant_id


def main():
    init_db()

    # Skip plants already in DB
    existing = {p["scientific_name"] for p in get_all_plants()}
    to_mine  = [p for p in PLANTS if p not in existing]

    print(f"Mining {len(to_mine)} plants ({len(existing)} already in DB)...\n")

    for i, plant in enumerate(to_mine, 1):
        print(f"[{i}/{len(to_mine)}] {plant} ...", end=" ", flush=True)
        try:
            data     = mine_plant(plant, max_papers=10)
            plant_id = save_mined_plant(data)
            n_cpd    = len(data["compounds"])
            n_bio    = len(data["bioactivities"])
            n_ref    = len(data["references"])
            print(f"id={plant_id}  {n_cpd} compounds  {n_bio} activities  {n_ref} refs")
        except Exception as e:
            print(f"ERROR -- {e}")

        if i < len(to_mine):
            time.sleep(0.4)   # polite NCBI pause

    # Final stats
    stats = get_stats()
    t     = stats["totals"]

    print("\n" + "=" * 50)
    print("FINAL DATABASE TOTALS")
    print("=" * 50)
    print(f"  Plants:         {t['plants']}")
    print(f"  Compounds:      {t['compounds']}")
    print(f"  Bioactivities:  {t['bioactivities']}")
    print(f"  Docking hits:   {t['docking_results']}")
    print(f"  References:     {t['references']}")

    print("\nBy assay type:")
    for row in stats["by_assay"]:
        print(f"  {row['assay_type']:<22} {row['n']}")

    print("\nBy compound class:")
    for row in stats["by_class"]:
        print(f"  {row['class']:<22} {row['n']}")

    print("\nMost active plants:")
    for row in stats["most_active_plants"][:12]:
        print(f"  {row['scientific_name']:<30} {row['n_activities']} activities")


if __name__ == "__main__":
    main()
