# generate_test_scenarios.py
"""
Generate three synthetic antimicrobial‑stewardship *test scenarios* using the rich
Dutch data‑generation logic, but write the CSV **filenames** consistently across all
scenarios (`mmi_MedicatieVoorschrift.csv`, `kweken.csv`,
`OrderSpecificatievraagAntwoord.csv`, `mmi_OpnameDeeltraject.csv`).  For the minimal
and alternative scenarios we *omit* files that are not supposed to exist, thereby
simulating missing data sources.

**Folder layout** — the script itself lives in `data/`, so its sibling directory
`raw/` will be created if absent:

```
data/
├─ generate_test_scenarios.py   ◀─ this script
└─ raw/
   ├─ minimal/
   │   ├─ mmi_MedicatieVoorschrift.csv
   │   └─ kweken.csv
   ├─ alternative/
   │   ├─ mmi_MedicatieVoorschrift.csv
   │   └─ kweken.csv
   └─ extended/
       ├─ mmi_MedicatieVoorschrift.csv
       ├─ OrderSpecificatievraagAntwoord.csv
       ├─ mmi_OpnameDeeltraject.csv
       └─ kweken.csv
```

Run with:
```bash
python data/generate_test_scenarios.py
```
All files are overwritten on each run; RNG is seeded for reproducibility.
"""

from __future__ import annotations

import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 0) PATHS & RNG
# ---------------------------------------------------------------------------
# The script is located *inside* the project’s `data/` directory → outputs in `raw/`
PROJECT_ROOT = Path(__file__).resolve().parent           # …/data
OUTPUT_ROOT = PROJECT_ROOT / "raw"                       # …/data/raw

random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# 1) LOOK‑UP TABLES  (identical to the rich generator)
# ---------------------------------------------------------------------------

doel_options = [
    "Therapie (onbekende verwekker)",
    "Therapie (bekende verwekker)",
    "Profylaxe (geen infectie)",
    "IV- orale switch",
]

locatie_options = [
    "Bot/gewicht",
    "CZS",
    "Gastro-enteritis",
    "Gist/schimmelinfectie",
    "Gynaecologische infectie",
    "Huid/weke delen",
    "Intra-abdominale infectie",
    "KNO-gebied of mond",
    "Koorts bij neutropenie",
    "Lijninfectie",
    "Luchtwegen",
    "Mediastinum",
    "Oog",
    "S. aureus bacteriemie",
    "Urineweginfectie",
    "Onbekend/Sepsis eci",
    "Overig/ namelijk:",
]

type_luchtweginfectie_options = [
    "Bronchitis - exacerbate COPD",
    "Comm-acq pneumonie - ernstig",
    "Comm-acq pneumonie - mild tot matig ernstig",
    "Aspiratie-pneumonie",
    "Hospital-acquired pneumonie",
    "Longabces/pleuraempyeem",
    "Overig",
]

antibiotics = [
    "COTRIM",
    "FENETICILLINE",
    "NITROFURANT",
    "TRIMETHOPRIM",
    "FOSFOMYC",
    "ZITHROMAX",
    "ERYTROMYCIN",
    "DOXYCILINE",
    "CLARITROMYCINE",
    "ZITHROM",
    "AZITROM",
    "AMOXICILLIN",
    "VANCOMYCIN",
]

frequencies = [
    "1x per dag",
    "2x per dag",
    "3x per dag",
    "4x per dag",
    "continues",
]

specialisms = [
    "Interne geneeskunde",
    "Chirurgie",
    "Urologie",
    "Kindergeneeskunde",
    "Neurologie",
    "IC",
    "Hema_onco",
]

subspecialisms = [
    "INT - hematologie",
    "INT - oncologie",
    "CHI - kinderchirurgie",
    "NEU - kinderen",
    "URO - kinderen",
    "KIN - kinder IC",
    "Arts Spoedeisende Hulp (SEH)",
]

werkplekken = [
    "AMC INTENSIVE CARE VOLWASSENEN",
    "VUMC INTENSIVE CARE VOLWASSENEN",
    "AFDELING A",
    "AFDELING B",
    "AMC PSYCH MEDIUM INTENSIVE CARE",
    "Klinische genetica",
]

material_choices: List[Tuple[str, str]] = [
    ("Broncho-alveolaire lavage", "Lagere luchtwegen"),
    ("Tracheaspoelsel", "Lagere luchtwegen"),
    ("Sputum", "Lagere luchtwegen"),
    ("Urine", "Urine"),
    ("Bloed", "Bloed"),
    ("Wond", "Huid/weke delen"),
]

kweekdoel_options = ["Patientenzorg", "Controle", "Diagnose"]


# ---------------------------------------------------------------------------
# 2) HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def yes_no() -> str:
    return "yes" if random.random() < 0.5 else "no"


def random_datetime_2023() -> datetime:
    start = datetime(2023, 1, 1)
    end = datetime(2023, 12, 31, 23, 59, 59)
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def random_float(low: float, high: float, d: int = 2) -> float:
    return round(random.uniform(low, high), d)


def clamp_to_2023(dt: datetime) -> datetime:
    return max(datetime(2023, 1, 1), min(dt, datetime(2023, 12, 31, 23, 59, 59)))


# ---------------------------------------------------------------------------
# 3) CORE GENERATOR (returns 4 DataFrames)
# ---------------------------------------------------------------------------

def generate_core_frames(num_patients: int = 50):
    pseudo_ids = [f"PSEUDO_{i+1}" for i in range(num_patients)]
    patient_contacts: List[Tuple[str, str]] = [
        (pid, f"CONTACT_{random.randint(1000, 9999)}") for pid in pseudo_ids for _ in range(random.randint(1, 2))
    ]
    mapping = {pid: idx for idx, pid in enumerate(pseudo_ids)}

    # -- mmi_MedicatieVoorschrift
    rows_v: List[dict] = []
    vid = 10_000
    for pid, pcid in patient_contacts:
        for _ in range(random.randint(1, 3)):
            vid += 1
            start = random_datetime_2023()
            stop = clamp_to_2023(start + timedelta(days=random.randint(1, 60)))
            order = clamp_to_2023(start - timedelta(hours=random.randint(1, 24)))
            drug = random.choice(antibiotics)
            rows_v.append(
                {
                    "VoorschriftId": vid,
                    "Pseudo_id": pid,
                    "anon_id": mapping[pid],
                    "PatientContactId": pcid,
                    "SpecialismeOmschrijving": random.choice(specialisms),
                    "SubSpecialismeOmschrijving": random.choice(subspecialisms),
                    "WerkplekOmschrijving": random.choice(werkplekken),
                    "MedicatieStofnaam": drug,
                    "KlinischPoliklinische": random.choice(["klinisch", "poliklinisch"]),
                    "ATCCode": "J01" + "".join(random.choices(list("ACDEFGMX"), k=2)) + str(random.randint(10, 99)),
                    "MedicatieFrequentieOmschrijving": random.choice(frequencies),
                    "ToedieningsRoute": random.choice(["oraal", "intraveneus", "intramusculair"]),
                    "DoseringBerekendEenheidOmschrijving": "mg/kg",
                    "DoseringBerekendMin": random_float(5, 10),
                    "DoseringBerekendMax": random_float(11, 20),
                    "DoseringVoorgeschrevenMin": random_float(100, 500),
                    "OrderStatus": random.choice(["Actief", "Gestopt", "Geannuleerd", "In uitvoering"]),
                    "VoorschrijfDatumTijd": order.isoformat(sep=" "),
                    "StartDatumTijd": start.isoformat(sep=" "),
                    "StopDatumTijd": stop.isoformat(sep=" "),
                    "MedicatieArtikelNaam": drug,
                    "MedicatieArtikelCode": f"ART-{random.randint(1000, 9999)}",
                    "OrderOmschrijving": f"Voorschrift voor {drug}",
                }
            )
    df_v = pd.DataFrame(rows_v)

    # -- OrderSpecificatievraagAntwoord
    rows_o: List[dict] = []
    for r in df_v.itertuples(index=False):
        rows_o.append(
            {
                "Pseudo_id": r.Pseudo_id,
                "anon_id": r.anon_id,
                "OrderId": r.VoorschriftId,
                "OrderOmschrijving": r.OrderOmschrijving,
                "PatientContactId": r.PatientContactId,
                "ZiekenhuisLocatie": f"ZKH_{random.randint(1, 3)}",
                "OrderSpecificatievraagFormulering": "Indicatie antibioticum?",
                "OrderSpecificatievraagAntwoord": random.choice(doel_options),
                "VraagVolgordeNummer": 1,
                "TriggermedicamentVolgnummer": random.randint(1, 20),
                "IsZorgOrderUitvoerbaar": yes_no(),
                "IsZorgOrderParent": yes_no(),
                "IsMedicatieVoorschrift": "yes",
                "IsGerelateerdMedicatieVoorschrift": "yes",
            }
        )
        loc_answer = random.choice(locatie_options)
        rows_o.append(
            {
                "Pseudo_id": r.Pseudo_id,
                "anon_id": r.anon_id,
                "OrderId": r.VoorschriftId,
                "OrderOmschrijving": r.OrderOmschrijving,
                "PatientContactId": r.PatientContactId,
                "ZiekenhuisLocatie": f"ZKH_{random.randint(1, 3)}",
                "OrderSpecificatievraagFormulering": "Locatie van de infectie?",
                "OrderSpecificatievraagAntwoord": loc_answer,
                "VraagVolgordeNummer": 2,
                "TriggermedicamentVolgnummer": random.randint(1, 20),
                "IsZorgOrderUitvoerbaar": yes_no(),
                "IsZorgOrderParent": yes_no(),
                "IsMedicatieVoorschrift": "yes",
                "IsGerelateerdMedicatieVoorschrift": "yes",
            }
        )
        if loc_answer == "Luchtwegen":
            rows_o.append(
                {
                    "Pseudo_id": r.Pseudo_id,
                    "anon_id": r.anon_id,
                    "OrderId": r.VoorschriftId,
                    "OrderOmschrijving": r.OrderOmschrijving,
                    "PatientContactId": r.PatientContactId,
                    "ZiekenhuisLocatie": f"ZKH_{random.randint(1, 3)}",
                    "OrderSpecificatievraagFormulering": "Type luchtweginfectie?",
                    "OrderSpecificatievraagAntwoord": random.choice(type_luchtweginfectie_options),
                    "VraagVolgordeNummer": 3,
                    "TriggermedicamentVolgnummer": random.randint(1, 20),
                    "IsZorgOrderUitvoerbaar": yes_no(),
                    "IsZorgOrderParent": yes_no(),
                    "IsMedicatieVoorschrift": "yes",
                    "IsGerelateerdMedicatieVoorschrift": "yes",
                }
            )
    df_o = pd.DataFrame(rows_o)

    # -- mmi_OpnameDeeltraject
    rows_opn: List[dict] = []
    for pid, pcid in set(patient_contacts):
        start_adm = datetime(2022, 12, random.randint(1, 10), 12)
        end_adm = datetime(2023, 12, random.randint(15, 31), 12)
        rows_opn.append(
            {
                "Pseudo_id": pid,
                "anon_id": mapping[pid],
                "PatientContactId": pcid,
                "OpnamedeeltrajectVolgnummer": random.randint(1, 5),
                "OpnametrajectOpnameDatumTijd": start_adm.isoformat(sep=" "),
                "OpnametrajectOntslagDatumTijd": end_adm.isoformat(sep=" "),
                "IsSEHDeeltraject": yes_no(),
                "IsICDeeltraject": yes_no(),
                "StartDatumTijd": start_adm.isoformat(sep=" "),
                "EindDatumTijd": end_adm.isoformat(sep=" "),
                "Specialisme": random.choice(specialisms),
                "Subspecialisme": random.choice(subspecialisms),
                "Werkplek": random.choice(werkplekken),
                "LigduurUren": (end_adm - start_adm).total_seconds() / 3600,
            }
        )
    df_opn = pd.DataFrame(rows_opn)

    # -- kweken
    rows_k: List[dict] = []
    for rx in df_v.itertuples(index=False):
        for _ in range(random.randint(0, 2)):
            base = datetime.fromisoformat(rx.StartDatumTijd)
            kdt = clamp_to_2023(base + timedelta(seconds=random.randint(-86_400, 86_400)))
            mat_desc, mat_cat = random.choice(material_choices)
            rows_k.append(
                {
                    "patientID_pseudo": rx.Pseudo_id,
                    "anon_id": rx.anon_id,
                    "ordernummer": random.randint(10_000, 99_999),
                    "monsternummer": random.randint(1_000_000, 9_999_999),
                    "afnamedatum": kdt.date().isoformat(),
                    "afnamedatumtijd": kdt,
                    "databron": "MicrobiologieLab",
                    "AUMC_locatie": f"LOC{random.randint(1, 3)}",
                    "afdeling": "Microbiologie",
                    "materiaal_code": f"M{random.randint(100, 999)}",
                    "materiaal_description": mat_desc,
                    "materiaal_catCustom": mat_cat,
                    "kweekdoel": random.choice(kweekdoel_options),
                    "microbe_spotf_isolaatentry": "",
                    "microbe_spotf_isolaatentryCODE": "",
                    "kweek_uitslagDef": "Positief" if random.random() < 0.3 else "Negatief",
                }
            )
    df_k = pd.DataFrame(rows_k)

    return df_v, df_o, df_opn, df_k


# ---------------------------------------------------------------------------
# 4) BUILDERS FOR EACH TEST SCENARIO
# ---------------------------------------------------------------------------

def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def build_minimal(df_v: pd.DataFrame, df_k: pd.DataFrame, out_dir: Path):
    _ensure_dir(out_dir)
    #   – prescriptions → mmi_MedicatieVoorschrift.csv (English column names, minimal set)
    pres = (
        df_v[[
            "Pseudo_id",
            "PatientContactId",
            "StartDatumTijd",
            "StopDatumTijd",
            "VoorschrijfDatumTijd",
            "MedicatieArtikelNaam",
            "ToedieningsRoute",
            "SpecialismeOmschrijving",
        ]].rename(
            columns={
                "Pseudo_id": "patient_number",
                "PatientContactId": "visit_id",
                "StartDatumTijd": "start_date",
                "StopDatumTijd": "end_date",
                "VoorschrijfDatumTijd": "order_date",
                "MedicatieArtikelNaam": "drug_name",
                "ToedieningsRoute": "route",
                "SpecialismeOmschrijving": "department",
            }
        )
    )
    pres.to_csv(out_dir / "mmi_MedicatieVoorschrift.csv", index=False)

    #   – cultures → kweken.csv (English column names, minimal set)
    cult = (
        df_k[["patientID_pseudo", "afnamedatumtijd", "materiaal_description", "kweek_uitslagDef"]]
        .rename(
            columns={
                "patientID_pseudo": "patient_number",
                "afnamedatumtijd": "collection_time",
                "materiaal_description": "specimen_type",
                "kweek_uitslagDef": "result",
            }
        )
    )
    cult.to_csv(out_dir / "kweken.csv", index=False)



def build_alternative(df_v: pd.DataFrame, df_k: pd.DataFrame, out_dir: Path):
    _ensure_dir(out_dir)
    # prescriptions with hospital‑style names
    pres_alt = (
        df_v[[
            "Pseudo_id",
            "PatientContactId",
            "StartDatumTijd",
            "StopDatumTijd",
            "VoorschrijfDatumTijd",
            "MedicatieStofnaam",
            "ToedieningsRoute",
            "SpecialismeOmschrijving",
        ]].rename(
            columns={
                "Pseudo_id": "mrn",
                "PatientContactId": "encounter_id",
                "StartDatumTijd": "medication_start",
                "StopDatumTijd": "medication_stop",
                "VoorschrijfDatumTijd": "order_timestamp",
                "MedicatieStofnaam": "generic_name",
                "ToedieningsRoute": "admin_route",
                "SpecialismeOmschrijving": "ordering_dept",
            }
        )
    )
    pres_alt.to_csv(out_dir / "mmi_MedicatieVoorschrift.csv", index=False)

    cult_alt = (
        df_k[["patientID_pseudo", "afnamedatumtijd", "materiaal_description", "kweek_uitslagDef"]]
        .rename(
            columns={
                "patientID_pseudo": "mrn",
                "afnamedatumtijd": "specimen_datetime",
                "materiaal_description": "source",
                "kweek_uitslagDef": "culture_finding",
            }
        )
    )
    cult_alt.to_csv(out_dir / "kweken.csv", index=False)



def build_extended(
    df_v: pd.DataFrame,
    df_o: pd.DataFrame,
    df_opn: pd.DataFrame,
    df_k: pd.DataFrame,
    out_dir: Path,
):
    _ensure_dir(out_dir)
    df_v.to_csv(out_dir / "mmi_MedicatieVoorschrift.csv", index=False)
    df_o.to_csv(out_dir / "OrderSpecificatievraagAntwoord.csv", index=False)
    df_opn.to_csv(out_dir / "mmi_OpnameDeeltraject.csv", index=False)
    df_k.to_csv(out_dir / "kweken.csv", index=False)


# ---------------------------------------------------------------------------
# 5) MAIN
# ---------------------------------------------------------------------------

def main():
    print("Generating synthetic test scenarios…")
    df_v, df_o, df_opn, df_k = generate_core_frames()

    print("  • minimal", end="…", flush=True)
    build_minimal(df_v, df_k, OUTPUT_ROOT / "minimal")
    print("done")

    print("  • alternative", end="…", flush=True)
    build_alternative(df_v, df_k, OUTPUT_ROOT / "alternative")
    print("done")

    print("  • extended", end="…", flush=True)
    build_extended(df_v, df_o, df_opn, df_k, OUTPUT_ROOT / "extended")
    print("done")

    print("All scenarios created under", OUTPUT_ROOT)


if __name__ == "__main__":
    main()
