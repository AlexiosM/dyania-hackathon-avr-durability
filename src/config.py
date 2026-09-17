from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
INTERMEDIATE_DIR = ROOT_DIR / "data" / "intermediate"
SCHEMA_FILE = ROOT_DIR / "schema" / "patient_schema_new.json"

NOTES_FILE = RAW_DIR / "notes_deidentified.xlsx"
LABS_FILE = RAW_DIR / "labs_deidentified.xlsx"
MEDICATIONS_FILE = RAW_DIR / "medications_deidentified.xlsx"

NOTES_CLEAN_FILE = PROCESSED_DIR / "notes_clean.json"
LABS_CLEAN_FILE = PROCESSED_DIR / "labs_clean.json"
MEDICATIONS_CLEAN_FILE = PROCESSED_DIR / "medications_clean.json"

PATIENTS_FILE = PROCESSED_DIR / "patients.json"
ENRICHED_PATIENTS_FILE = PROCESSED_DIR / "enriched_patients.json"
VALIDATION_REPORT_FILE = PROCESSED_DIR / "validation_report.json"

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "medgemma:latest"
OLLAMA_TIMEOUT_SECONDS = 600
MAX_RETRIES = 3
