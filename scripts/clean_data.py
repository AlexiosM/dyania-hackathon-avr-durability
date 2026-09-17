import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import (
    LABS_CLEAN_FILE,
    LABS_FILE,
    MEDICATIONS_CLEAN_FILE,
    MEDICATIONS_FILE,
    NOTES_CLEAN_FILE,
    NOTES_FILE,
    PROCESSED_DIR,
)
from src.data_loader import load_excel, save_json


def clean_file(source, destination):
    print(f"Reading {source}")

    records = load_excel(source)

    save_json(
        records,
        destination,
    )

    print(
        f"  {len(records)} records -> {destination}"
    )


def main():
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    clean_file(
        NOTES_FILE,
        NOTES_CLEAN_FILE,
    )

    clean_file(
        LABS_FILE,
        LABS_CLEAN_FILE,
    )

    clean_file(
        MEDICATIONS_FILE,
        MEDICATIONS_CLEAN_FILE,
    )


if __name__ == "__main__":
    main()
