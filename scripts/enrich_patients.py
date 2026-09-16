import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, ".")

from src.config import (
    CLEAN_LABS_FILE,
    CLEAN_MEDICATIONS_FILE,
    STRUCTURED_PATIENTS_FILE,
    ENRICHED_PATIENTS_FILE
)


LAB_PATTERNS = {
    "creatinine": [
        r"\bcreatinine\b"
    ],
    "egfr": [
        r"\begfr\b",
        r"estimated glomerular filtration"
    ],
    "hemoglobin": [
        r"\bhemoglobin\b",
        r"\bhgb\b"
    ],
    "platelets": [
        r"\bplatelet\b",
        r"\bplatelets\b"
    ],
    "glucose": [
        r"\bglucose\b"
    ],
    "hba1c": [
        r"\bhba1c\b",
        r"hemoglobin a1c",
        r"glycated hemoglobin"
    ],
    "bnp": [
        r"\bbnp\b",
        r"brain natriuretic peptide"
    ],
    "nt_probnp": [
        r"nt[- ]?pro[- ]?bnp",
        r"n[- ]?terminal.*pro.*bnp"
    ]
}


MEDICATION_PATTERNS = {
    "anticoagulant": [
        "warfarin",
        "apixaban",
        "rivaroxaban",
        "dabigatran",
        "edoxaban"
    ],
    "antiplatelet": [
        "aspirin",
        "clopidogrel",
        "ticagrelor",
        "prasugrel"
    ],
    "beta_blocker": [
        "metoprolol",
        "carvedilol",
        "bisoprolol",
        "atenolol",
        "nebivolol"
    ],
    "ace_arb_arni": [
        "lisinopril",
        "enalapril",
        "ramipril",
        "losartan",
        "valsartan",
        "irbesartan",
        "candesartan",
        "sacubitril"
    ],
    "diuretic": [
        "furosemide",
        "bumetanide",
        "torsemide",
        "hydrochlorothiazide",
        "chlorthalidone",
        "spironolactone",
        "eplerenone"
    ],
    "statin": [
        "atorvastatin",
        "rosuvastatin",
        "simvastatin",
        "pravastatin",
        "lovastatin"
    ],
    "diabetes_medication": [
        "metformin",
        "insulin",
        "glipizide",
        "glyburide",
        "glimepiride",
        "sitagliptin",
        "empagliflozin",
        "dapagliflozin",
        "semaglutide"
    ]
}


def normalize_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def find_lab_name(row):
    fields = [
        "Lab Component Name",
        "Lab Component Base Name",
        "Lab Component Common Name",
        "Lab Abbreviation",
        "Loinc Name"
    ]

    for field in fields:
        value = normalize_text(row.get(field))

        if not value:
            continue

        for canonical_name, patterns in LAB_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, value):
                    return canonical_name

    return None


def extract_labs(patient_id, labs):
    patient_labs = labs[
        labs["Patient"].astype(str) == patient_id
    ]

    results = []

    for _, row in patient_labs.iterrows():
        canonical_name = find_lab_name(row)

        if canonical_name is None:
            continue

        value = row.get("Numeric Value")

        if pd.isna(value):
            continue

        date = row.get("Result Date")

        if pd.isna(date):
            date = None
        else:
            date = str(date)

        unit = row.get("Unit")

        if pd.isna(unit):
            unit = None
        else:
            unit = str(unit)

        results.append(
            {
                "date": date,
                "name": canonical_name,
                "value": float(value),
                "unit": unit
            }
        )

    results.sort(
        key=lambda item: item["date"] or ""
    )

    return results


def find_medication_class(row):
    fields = [
        "Simple Generic Name",
        "Proper Name",
        "Medication Therapeutic Class",
        "Medication Pharmaceutical Class",
        "Medication Pharmaceutical Subclass"
    ]

    text = " ".join(
        normalize_text(row.get(field))
        for field in fields
    )

    for medication_class, medications in MEDICATION_PATTERNS.items():
        for medication in medications:
            if medication in text:
                return medication_class

    return None


def extract_medications(patient_id, medications):
    patient_medications = medications[
        medications["Patient"].astype(str) == patient_id
    ]

    results = []
    seen = set()

    for _, row in patient_medications.iterrows():
        medication_class = find_medication_class(row)

        if medication_class is None:
            continue

        generic_name = row.get("Simple Generic Name")

        if pd.isna(generic_name):
            generic_name = row.get("Proper Name")

        if pd.isna(generic_name):
            continue

        generic_name = str(generic_name)

        start_date = row.get("Start Date")
        end_date = row.get("End Date")

        if pd.isna(start_date):
            start_date = None
        else:
            start_date = str(start_date)

        if pd.isna(end_date):
            end_date = None
        else:
            end_date = str(end_date)

        key = (
            generic_name.lower(),
            medication_class,
            start_date,
            end_date
        )

        if key in seen:
            continue

        seen.add(key)

        results.append(
            {
                "generic_name": generic_name,
                "medication_class": medication_class,
                "start_date": start_date,
                "end_date": end_date
            }
        )

    return results


def main():
    with open(
        STRUCTURED_PATIENTS_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    labs = pd.read_excel(CLEAN_LABS_FILE)
    medications = pd.read_excel(CLEAN_MEDICATIONS_FILE)

    patients = data["patients"]

    for patient in patients:
        patient_id = patient["patient_id"]

        patient["labs"] = extract_labs(
            patient_id,
            labs
        )

        patient["medications"] = extract_medications(
            patient_id,
            medications
        )

        print(
            f"{patient_id}: "
            f"{len(patient['labs'])} labs, "
            f"{len(patient['medications'])} medications"
        )

    with open(
        ENRICHED_PATIENTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print(
        print(f"Created: {ENRICHED_PATIENTS_FILE}")
    )


if __name__ == "__main__":
    main()