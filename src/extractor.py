from collections import defaultdict

from .config import (
    NOTES_CLEAN_FILE,
    PATIENTS_FILE,
    SCHEMA_FILE,
)
from .data_loader import load_json, save_json
from .llm_client import OllamaClient
from .prompts import build_messages
from .validator import load_schema, validate_patient


def group_notes(notes):
    grouped = defaultdict(list)

    for note in notes:
        patient_id = note.get("Profile Key")

        if patient_id:
            grouped[str(patient_id)].append(note)

    return dict(sorted(grouped.items()))


def force_patient_id(patient, patient_id):
    patient["patient_id"] = patient_id
    return patient


def extract_patients():
    notes = load_json(NOTES_CLEAN_FILE)
    schema = load_schema(SCHEMA_FILE)

    grouped = group_notes(notes)

    client = OllamaClient()

    patients = []
    failures = []

    total = len(grouped)

    for index, (patient_id, patient_notes) in enumerate(
        grouped.items(),
        start=1,
    ):
        if index > 5:
            break
        print(
            f"[{index}/{total}] Extracting {patient_id} "
            f"({len(patient_notes)} notes)"
        )

        try:
            messages = build_messages(
                patient_id,
                patient_notes,
                schema,
            )

            patient = client.extract_with_retry(
                messages,
                patient_id,
            )

            patient = force_patient_id(
                patient,
                patient_id,
            )

            errors = validate_patient(
                patient,
                schema,
            )

            if errors:
                print(
                    f"  validation failed: {len(errors)} errors"
                )

                failures.append(
                    {
                        "patient_id": patient_id,
                        "errors": errors,
                    }
                )
            else:
                patients.append(patient)
                print("  OK")

        except Exception as exc:
            print(f"  FAILED: {exc}")

            failures.append(
                {
                    "patient_id": patient_id,
                    "errors": [
                        {
                            "path": "",
                            "message": str(exc),
                        }
                    ],
                }
            )

    save_json(
        patients,
        PATIENTS_FILE,
    )

    save_json(
        failures,
        PATIENTS_FILE.with_name("extraction_failures.json"),
    )

    print()
    print(f"Successful patients: {len(patients)}")
    print(f"Failed patients: {len(failures)}")
    print(f"Output: {PATIENTS_FILE}")


if __name__ == "__main__":
    extract_patients()
