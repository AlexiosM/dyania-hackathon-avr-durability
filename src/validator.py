import json

from jsonschema import Draft202012Validator


def load_schema(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_patient(patient, schema):
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(patient),
        key=lambda error: list(error.path),
    )

    return [
        {
            "path": ".".join(str(part) for part in error.path),
            "message": error.message,
        }
        for error in errors
    ]


def validate_patients(patients, schema):
    results = []

    for patient in patients:
        errors = validate_patient(patient, schema)

        results.append(
            {
                "patient_id": patient.get("patient_id"),
                "valid": len(errors) == 0,
                "errors": errors,
            }
        )

    return results
