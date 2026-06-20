# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db.schema import init_db
from db.crud import (
    add_plant, get_all_plants, add_compound, add_bioactivity,
    add_ethnobotany, add_reference, link_plant_reference,
)


def seed():
    init_db()

    if get_all_plants():
        print("Database already seeded — skipping.")
        return

    # ── Plant 1: Erodium moschatum ─────────────────────────────────────────
    ero_id = add_plant(
        scientific_name="Erodium moschatum",
        common_name_ar="أبو قنديل",
        common_name_fr="Érodium musqué",
        common_name_en="Musk stork's-bill",
        family="Geraniaceae",
        genus="Erodium",
        species="moschatum",
        country="Morocco",
        region="Fès-Meknès",
        is_endemic=0,
        traditional_use="Antidiabetic, antioxidant, wound healing",
    )

    geraniin_id = add_compound(
        plant_id=ero_id, name="Geraniin",
        class_="polyphenol", subclass="ellagitannin",
        molecular_formula="C41H28O27", molecular_weight=952.59,
        detection_method="UPLC-ESI-MS", mz_observed=951.1,
        ionization_mode="negative", adduct="[M-H]-",
    )
    ellagic_id = add_compound(
        plant_id=ero_id, name="Ellagic acid",
        class_="polyphenol", subclass="ellagitannin",
        molecular_formula="C14H6O8", molecular_weight=302.19,
        detection_method="UPLC-ESI-MS", mz_observed=301.0,
        ionization_mode="negative", adduct="[M-H]-",
    )
    apigenin_id = add_compound(
        plant_id=ero_id, name="Apigenin",
        class_="flavonoid", subclass="flavone",
        molecular_formula="C15H10O5", molecular_weight=270.24,
        detection_method="UPLC-ESI-MS", mz_observed=269.0,
        ionization_mode="negative", adduct="[M-H]-",
    )
    quercetin_id = add_compound(
        plant_id=ero_id, name="Quercetin",
        class_="flavonoid", subclass="flavonol",
        molecular_formula="C15H10O7", molecular_weight=302.24,
        detection_method="UPLC-ESI-MS", mz_observed=301.0,
        ionization_mode="negative", adduct="[M-H]-",
    )
    gallic_ero_id = add_compound(
        plant_id=ero_id, name="Gallic acid",
        class_="polyphenol", subclass="phenolic acid",
        molecular_formula="C7H6O5", molecular_weight=170.12,
        detection_method="UPLC-ESI-MS", mz_observed=169.0,
        ionization_mode="negative", adduct="[M-H]-",
    )

    add_bioactivity(
        plant_id=ero_id, assay_type="DPPH", activity_category="antioxidant",
        value=45.2, unit="µg/mL", value_type="IC50",
        reference_compound="Ascorbic acid", reference_value=12.4, reference_unit="µg/mL",
    )
    add_bioactivity(
        plant_id=ero_id, assay_type="ABTS", activity_category="antioxidant",
        value=38.7, unit="µg/mL", value_type="IC50",
        reference_compound="Trolox", reference_value=8.9, reference_unit="µg/mL",
    )
    add_bioactivity(
        plant_id=ero_id, assay_type="alpha-glucosidase", activity_category="antidiabetic",
        value=62.4, unit="µg/mL", value_type="IC50",
        reference_compound="Acarbose", reference_value=28.5, reference_unit="µg/mL",
    )
    add_bioactivity(
        plant_id=ero_id, assay_type="MTT", activity_category="cytotoxicity",
        value=128.5, unit="µg/mL", value_type="IC50",
        model_organism="MCF-7",
    )

    add_ethnobotany(
        plant_id=ero_id, use_category="antidiabetic",
        plant_part="aerial parts", preparation="decoction",
        administration="oral", region="Fès-Meknès",
    )

    ref1_id = add_reference(
        doi="10.1016/j.sciaf.2026.e03252",
        title="Phytochemical profiling and biological activities of Erodium moschatum",
        authors="Takie M. et al.",
        journal="Scientific African",
        year=2026,
    )
    link_plant_reference(ero_id, ref1_id)

    # ── Plant 2: Reseda alba ───────────────────────────────────────────────
    res_id = add_plant(
        scientific_name="Reseda alba",
        common_name_ar="الرازقي الأبيض",
        common_name_fr="Réséda blanc",
        common_name_en="White mignonette",
        family="Resedaceae",
        genus="Reseda",
        species="alba",
        country="Morocco",
        region="Fès-Meknès",
        is_endemic=0,
        traditional_use="Antidiabetic, anti-inflammatory, gastroprotective",
    )

    add_compound(
        plant_id=res_id, name="Catechin",
        class_="flavonoid", subclass="flavan-3-ol",
        molecular_formula="C15H14O6", molecular_weight=290.27,
        detection_method="UPLC-ESI-MS", mz_observed=289.1,
        ionization_mode="negative", adduct="[M-H]-",
    )
    add_compound(
        plant_id=res_id, name="Gallic acid",
        class_="polyphenol", subclass="phenolic acid",
        molecular_formula="C7H6O5", molecular_weight=170.12,
        detection_method="UPLC-ESI-MS", mz_observed=169.0,
        ionization_mode="negative", adduct="[M-H]-",
    )
    add_compound(
        plant_id=res_id, name="p-Coumaric acid",
        class_="polyphenol", subclass="hydroxycinnamic acid",
        molecular_formula="C9H8O3", molecular_weight=164.16,
        detection_method="UPLC-ESI-MS", mz_observed=163.0,
        ionization_mode="negative", adduct="[M-H]-",
    )

    add_bioactivity(
        plant_id=res_id, assay_type="DPPH", activity_category="antioxidant",
        value=52.1, unit="µg/mL", value_type="IC50",
        reference_compound="Ascorbic acid", reference_value=12.4, reference_unit="µg/mL",
    )
    add_bioactivity(
        plant_id=res_id, assay_type="alpha-amylase", activity_category="antidiabetic",
        value=78.3, unit="µg/mL", value_type="IC50",
        reference_compound="Acarbose", reference_value=28.5, reference_unit="µg/mL",
    )
    add_bioactivity(
        plant_id=res_id, assay_type="gastroprotective", activity_category="gastroprotective",
        value=68.5, unit="%", value_type="inhibition%",
        model_organism="Wistar rat",
    )

    ref2_id = add_reference(
        doi="10.1002/fsn3.71853",
        title="Biological activities and phytochemical analysis of Reseda alba",
        authors="Takie M. et al.",
        journal="Food Science & Nutrition",
        year=2026,
    )
    link_plant_reference(res_id, ref2_id)

    print("Seed complete.")
    print(f"  Erodium moschatum  id={ero_id}  |  5 compounds, 4 bioactivities")
    print(f"  Reseda alba        id={res_id}  |  3 compounds, 3 bioactivities")
    print(f"  References: 2")


if __name__ == "__main__":
    seed()
