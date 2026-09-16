from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

NOTES_FILE = RAW_DIR / "notes_deidentified.xlsx"
LABS_FILE = RAW_DIR / "labs_deidentified.xlsx"
MEDICATIONS_FILE = RAW_DIR / "medications_deidentified.xlsx"

CLEAN_NOTES_FILE = PROCESSED_DIR / "notes_cleaned.xlsx"
CLEAN_LABS_FILE = PROCESSED_DIR / "labs_cleaned.xlsx"
CLEAN_MEDICATIONS_FILE = PROCESSED_DIR / "medications_cleaned.xlsx"

STRUCTURED_PATIENTS_FILE = PROCESSED_DIR / "patients.json"

ENRICHED_PATIENTS_FILE = PROCESSED_DIR / "patients_enriched.json"

SCHEMA_FILE = ROOT_DIR / "schema" / "patient_schema.json"

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "medgemma"
)
