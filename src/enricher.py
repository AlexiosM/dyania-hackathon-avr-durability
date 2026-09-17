from collections import defaultdict

from .config import (
    ENRICHED_PATIENTS_FILE,
    LABS_CLEAN_FILE,
    MEDICATIONS_CLEAN_FILE,
    PATIENTS_FILE,
)
from .data_loader import load_json, save_json


LAB_FIELD_MAP = {
    "creatinine": [
        "creatinine",
    ],
    "egfr": [
        "egfr",
        "estimated glomerular filtration rate",
    ],
    "urea_or_bun": [
        "urea",
        "bun",
        "blood urea nitrogen",
    ],
    "hba1c": [
        "hba1c",
        "hemoglobin a1c",
        "glycated hemoglobin",
    ],
    "glucose": [
        "glucose",
    ],
    "fasting_insulin": [
        "fasting insulin",
        "insulin",
    ],
    "total_cholesterol": [
        "total cholesterol",
        "cholesterol total",
    ],
    "ldl_cholesterol": [
        "ldl",
        "low density lipoprotein",
    ],
    "hdl_cholesterol": [
        "hdl",
        "high density lipoprotein",
    ],
    "triglycerides": [
        "triglyceride",
    ],
    "apolipoprotein_b": [
        "apolipoprotein b",
        "apob",
    ],
    "lipoprotein_a": [
        "lipoprotein a",
        "lpa",
    ],
    "calcium": [
        "calcium",
    ],
    "phosphate": [
        "phosphate",
        "phosphorus",
    ],
    "parathyroid_hormone": [
        "parathyroid hormone",
        "pth",
    ],
    "crp": [
        "crp",
        "c-reactive protein",
    ],
    "esr": [
        "esr",
        "erythrocyte sedimentation rate",
    ],
    "hemoglobin": [
        "hemoglobin",
        "haemoglobin",
        "hgb",
    ],
    "albumin": [
        "albumin",
    ],
    "bnp": [
        "bnp",
        "brain natriuretic peptide",
    ],
    "nt_pro_bnp": [
        "nt-probnp",
        "nt pro bnp",
        "n-terminal pro bnp",
        "nt-pro bnp",
    ],
    "inr": [
        "inr",
        "international normalized ratio",
    ],
}


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def find_lab_field(record):
    names = [
        record.get("Lab Component Name"),
        record.get("Lab Component Base Name"),
        record.get("Lab Component Common Name"),
        record.get("Lab Abbreviation"),
        record.get("Loinc Name"),
    ]

    text = " ".join(
        normalize_text(value)
        for value in names
        if value is not None
    )

    matches = []

    for field, patterns in LAB_FIELD_MAP.items():
        for pattern in patterns:
            if pattern in text:
                matches.append(field)
                break

    if len(matches) == 1:
        return matches[0]

    return None


def lab_record(record):
    return {
        "value": (
            record.get("Numeric Value")
            if record.get("Numeric Value") is not None
            else record.get("String Value")
        ),
        "unit": record.get("Unit"),
        "date_raw": record.get("Result Date"),
        "lab_name_raw": record.get("Lab Component Name"),
        "lab_abbreviation_raw": record.get("Lab Abbreviation"),
        "flag_raw": record.get("Flag"),
        "is_abnormal": record.get("Is Abnormal"),
        "reference_values_raw": record.get("Reference Values"),
    }


def enrich_labs(patient, labs_by_patient):
    patient_id = patient["patient_id"]

    records = labs_by_patient.get(patient_id, [])

    measurements = patient.setdefault(
        "laboratory_measurements",
        {},
    )

    for field in LAB_FIELD_MAP:
        measurements.setdefault(field, [])

    for record in records:
        field = find_lab_field(record)

        if field is None:
            continue

        measurements[field].append(
            lab_record(record)
        )


def medication_text(record):
    fields = [
        record.get("Proper Name"),
        record.get("Simple Generic Name"),
        record.get("Medication Therapeutic Class"),
        record.get("Medication Pharmaceutical Class"),
        record.get("Medication Pharmaceutical Subclass"),
    ]

    return " ".join(
        normalize_text(value)
        for value in fields
        if value is not None
    )


def medication_category(record):
    text = medication_text(record)

    if any(
        value in text
        for value in [
            "warfarin",
            "apixaban",
            "rivaroxaban",
            "dabigatran",
            "edoxaban",
            "anticoagulant",
        ]
    ):
        return "oral_anticoagulants"

    if any(
        value in text
        for value in [
            "aspirin",
            "clopidogrel",
            "prasugrel",
            "ticagrelor",
            "antiplatelet",
        ]
    ):
        return "antiplatelet_agents"

    if any(
        value in text
        for value in [
            "statin",
            "atorvastatin",
            "rosuvastatin",
            "simvastatin",
            "pravastatin",
            "ezetimibe",
            "lipid lowering",
        ]
    ):
        return "lipid_lowering_therapy"

    if any(
        value in text
        for value in [
            "insulin",
            "metformin",
            "glp-1",
            "glp1",
            "sulfonylurea",
            "diabetes",
            "antidiabetic",
        ]
    ):
        return "diabetes_therapy"

    if any(
        value in text
        for value in [
            "ace inhibitor",
            "angiotensin converting enzyme",
            "arb",
            "angiotensin receptor blocker",
            "beta blocker",
            "calcium channel blocker",
            "amlodipine",
            "losartan",
            "valsartan",
            "lisinopril",
            "ramipril",
            "antihypertensive",
        ]
    ):
        return "antihypertensive_therapy"

    if any(
        value in text
        for value in [
            "sacubitril",
            "valsartan",
            "entresto",
            "diuretic",
            "furosemide",
            "bumetanide",
            "spironolactone",
            "eplerenone",
            "heart failure",
        ]
    ):
        return "heart_failure_or_diuretic_therapy"

    if any(
        value in text
        for value in [
            "calcium",
            "phosphate",
            "parathyroid",
            "calcitriol",
            "cinacalcet",
        ]
    ):
        return "calcium_phosphate_or_parathyroid_therapy"

    return None


def medication_record(record):
    return {
        "name_raw": record.get("Proper Name"),
        "generic_name_raw": record.get("Simple Generic Name"),
        "strength_raw": record.get("Medication Strength"),
        "form_raw": record.get("Medication Form"),
        "route_raw": record.get("Route"),
        "dose_raw": record.get("Dose"),
        "dose_unit_raw": record.get("Dose Unit"),
        "frequency_raw": record.get("Frequency"),
        "start_date_raw": record.get("Start Date"),
        "administration_date_raw": record.get("Administration Date"),
        "end_date_raw": record.get("End Date"),
        "discontinued_date_raw": record.get("Discontinued Date"),
        "mode_raw": record.get("Mode"),
        "discontinued_reason_raw": record.get("Discontinued Reason"),
        "therapeutic_class_raw": record.get(
            "Medication Therapeutic Class"
        ),
        "pharmaceutical_class_raw": record.get(
            "Medication Pharmaceutical Class"
        ),
        "pharmaceutical_subclass_raw": record.get(
            "Medication Pharmaceutical Subclass"
        ),
        "prescribing_provider_specialty_raw": record.get(
            "Prescribing Provider Specialty"
        ),
    }


def enrich_medications(patient, medications_by_patient):
    patient_id = patient["patient_id"]

    records = medications_by_patient.get(
        patient_id,
        [],
    )

    medications = patient.setdefault(
        "relevant_medications",
        {},
    )

    fields = [
        "oral_anticoagulants",
        "antiplatelet_agents",
        "lipid_lowering_therapy",
        "diabetes_therapy",
        "antihypertensive_therapy",
        "heart_failure_or_diuretic_therapy",
        "calcium_phosphate_or_parathyroid_therapy",
    ]

    for field in fields:
        medications.setdefault(field, [])

    for record in records:
        category = medication_category(record)

        if category is None:
            continue

        medications[category].append(
            medication_record(record)
        )


def enrich():
    patients = load_json(PATIENTS_FILE)
    labs = load_json(LABS_CLEAN_FILE)
    medications = load_json(MEDICATIONS_CLEAN_FILE)

    labs_by_patient = defaultdict(list)
    medications_by_patient = defaultdict(list)

    for record in labs:
        patient_id = record.get("Patient")

        if patient_id:
            labs_by_patient[str(patient_id)].append(record)

    for record in medications:
        patient_id = record.get("Patient")

        if patient_id:
            medications_by_patient[str(patient_id)].append(record)

    enriched = []

    for patient in patients:
        patient_id = patient.get("patient_id")

        enrich_labs(
            patient,
            labs_by_patient,
        )

        enrich_medications(
            patient,
            medications_by_patient,
        )

        enriched.append(patient)

    save_json(
        enriched,
        ENRICHED_PATIENTS_FILE,
    )

    print(
        f"Enriched patients: {len(enriched)}"
    )
    print(
        f"Output: {ENRICHED_PATIENTS_FILE}"
    )


if __name__ == "__main__":
    enrich()
