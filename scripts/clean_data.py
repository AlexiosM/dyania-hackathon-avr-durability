import sys

sys.path.insert(0, ".")

from src.config import (
    NOTES_FILE,
    LABS_FILE,
    MEDICATIONS_FILE,
    CLEAN_NOTES_FILE,
    CLEAN_LABS_FILE,
    CLEAN_MEDICATIONS_FILE
)

from src.data.loading import load_excel_files
from src.data.cleaning import clean_all


def main():
    notes, labs, medications = load_excel_files(
        NOTES_FILE,
        LABS_FILE,
        MEDICATIONS_FILE
    )

    print("Before cleaning:")
    print(f"  Notes:        {len(notes)}")
    print(f"  Labs:         {len(labs)}")
    print(f"  Medications:  {len(medications)}")

    notes, labs, medications = clean_all(
        notes,
        labs,
        medications
    )

    print("\nAfter cleaning:")
    print(f"  Notes:        {len(notes)}")
    print(f"  Labs:         {len(labs)}")
    print(f"  Medications:  {len(medications)}")

    CLEAN_NOTES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    notes.to_excel(
        CLEAN_NOTES_FILE,
        index=False
    )

    labs.to_excel(
        CLEAN_LABS_FILE,
        index=False
    )

    medications.to_excel(
        CLEAN_MEDICATIONS_FILE,
        index=False
    )

    print("\nCleaned files written.")


if __name__ == "__main__":
    main()
