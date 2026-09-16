import json
import sys

sys.path.insert(0, ".")

from src.config import (
    CLEAN_NOTES_FILE,
    CLEAN_LABS_FILE,
    CLEAN_MEDICATIONS_FILE,
    STRUCTURED_PATIENTS_FILE,
    OLLAMA_URL,
    OLLAMA_MODEL
)

from src.data.loading import load_excel_files
from src.llm.client import OllamaClient
from src.llm.extraction import (
    get_patient_ids,
    extract_patient
)


def build_patient_record(
    patient_id,
    extracted,
    patient_labs,
    patient_medications
):
    labs = []

    for row_id, row in patient_labs.iterrows():
        labs.append(
            {
                "date": None if row.get("Result Date") is None else str(row.get("Result Date")),
                "name": row.get("Lab Component Name"),
                "value": row.get("Numeric Value"),
                "unit": row.get("Unit"),
                "abnormal_flag": row.get("Flag"),
                "source": "labs_deidentified.xlsx",
                "source_row_id": int(row_id)
            }
        )

    medications = []

    for row_id, row in patient_medications.iterrows():
        medications.append(
            {
                "generic_name": row.get("Simple Generic Name"),
                "medication_class": row.get("Medication Therapeutic Class"),
                "start_date": None if row.get("Start Date") is None else str(row.get("Start Date")),
                "end_date": None if row.get("End Date") is None else str(row.get("End Date")),
                "dose": row.get("Dose"),
                "dose_unit": row.get("Dose Unit"),
                "frequency": row.get("Frequency"),
                "source": "medications_deidentified.xlsx",
                "source_row_id": int(row_id)
            }
        )

    return {
        "patient_id": patient_id,
        "avr": extracted.get("avr", {}),
        "risk_factors": extracted.get("risk_factors", {}),
        "echo": extracted.get("echo", {}),
        "events": extracted.get("events", []),
        "outcome": extracted.get("outcome", {}),
        "labs": labs,
        "medications": medications
    }


def save_results(results):
    STRUCTURED_PATIENTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        STRUCTURED_PATIENTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            {"patients": results},
            f,
            ensure_ascii=False,
            indent=2,
            default=str
        )


def main():
    notes, labs, medications = load_excel_files(
        CLEAN_NOTES_FILE,
        CLEAN_LABS_FILE,
        CLEAN_MEDICATIONS_FILE
    )

    patients = get_patient_ids(
        notes,
        labs,
        medications
    )

    client = OllamaClient(
        OLLAMA_URL,
        OLLAMA_MODEL
    )

    results = []

    for index, patient_id in enumerate(
        patients,
        start=1
    ):
        if index == 4:
            break

        print(
            f"[{index}] Processing {patient_id}..."
        )

        try:
            extracted = extract_patient(
                client,
                patient_id,
                notes
            )

            patient_labs = labs[
                labs["Patient"].astype(str) == patient_id
            ]

            patient_medications = medications[
                medications["Patient"].astype(str) == patient_id
            ]

            result = build_patient_record(
                patient_id,
                extracted,
                patient_labs,
                patient_medications
            )

            results.append(result)

            save_results(results)

            print(
                f"  ✓ {patient_id} saved"
            )

        except Exception as error:
            print(
                f"  ✗ {patient_id}: {error}"
            )

    print("\nExtraction complete.")
    print(
        f"Patients extracted: {len(results)}"
    )
    print(
        f"Output: {STRUCTURED_PATIENTS_FILE}"
    )


if __name__ == "__main__":
    main()
