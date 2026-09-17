import json
import re
from pathlib import Path
import requests
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SEED_FILE = ROOT / "data" / "processed" / "patients.json"
SCHEMA_FILE = ROOT / "schema" / "patient_schema_new.json"
OUTPUT_FILE = ROOT / "data" / "processed" / "synthetic_2000_patients.json"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "medgemma:latest"
BATCH_SIZE = 20
TOTAL_PATIENTS = 2000

with SEED_FILE.open(encoding="utf-8") as f:
    seed = json.load(f)

with SCHEMA_FILE.open(encoding="utf-8") as f:
    schema = json.load(f)

validator = Draft202012Validator(schema)

def ask_gemma(start_id, batch_size):
    examples = seed[:min(5, len(seed))]
    prompt = f"""
Generate {batch_size} synthetic patients for a research software test dataset about bioprosthetic aortic valve durability after AVR.

Use the following existing patient JSON records as the style and clinical distribution reference:
{json.dumps(examples, ensure_ascii=False)}

Requirements:
- Patient IDs must be Patient_{start_id:04d} through Patient_{start_id + batch_size - 1:04d}.
- Return ONLY one JSON array.
- Every patient must follow the supplied schema exactly.
- Do not add fields.
- Do not remove fields.
- Use null when information is unavailable.
- Keep the cohort clinically plausible and internally consistent.
- Vary age, sex, body size, comorbidities, procedure type, valve model/size, echo findings and medications.
- Do not copy the example patient IDs.
- This is synthetic data for software/model development, not real clinical data.
"""
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
        },
        timeout=600,
    )
    r.raise_for_status()
    content = r.json()["message"]["content"]
    return json.loads(content)

all_patients = []

for start in range(1, TOTAL_PATIENTS + 1, BATCH_SIZE):
    batch_size = min(BATCH_SIZE, TOTAL_PATIENTS - start + 1)
    batch = ask_gemma(start, batch_size)

    if not isinstance(batch, list) or len(batch) != batch_size:
        raise ValueError(f"Invalid batch at {start}: expected {batch_size} patients")

    for patient in batch:
        errors = list(validator.iter_errors(patient))
        if errors:
            raise ValueError(
                f"{patient.get('patient_id', 'unknown')} failed schema validation: "
                f"{errors[0].message}"
            )

    all_patients.extend(batch)
    print(f"Generated {len(all_patients)}/{TOTAL_PATIENTS}")

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(all_patients, f, ensure_ascii=False, indent=2)

print(f"Saved {OUTPUT_FILE}")

