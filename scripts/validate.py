import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import (
    ENRICHED_PATIENTS_FILE,
    SCHEMA_FILE,
    VALIDATION_REPORT_FILE,
)
from src.data_loader import load_json, save_json
from src.validator import load_schema, validate_patients


def main():
    patients = load_json(
        ENRICHED_PATIENTS_FILE
    )

    schema = load_schema(
        SCHEMA_FILE
    )

    results = validate_patients(
        patients,
        schema,
    )

    valid = sum(
        1
        for result in results
        if result["valid"]
    )

    report = {
        "total_patients": len(results),
        "valid_patients": valid,
        "invalid_patients": len(results) - valid,
        "patients": results,
    }

    save_json(
        report,
        VALIDATION_REPORT_FILE,
    )

    print(
        f"Valid: {valid}/{len(results)}"
    )

    if valid != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
