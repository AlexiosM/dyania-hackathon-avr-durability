def clean_notes(notes):
    return notes.drop_duplicates(
        subset=["Profile Key", "Notes", "Service Date"]
    ).copy()


def clean_labs(labs):
    return labs.drop_duplicates(
        subset=[
            "Patient",
            "Lab Component Name",
            "Result Date",
            "Numeric Value"
        ]
    ).copy()


def clean_medications(medications):
    return medications.drop_duplicates(
        subset=[
            "Patient",
            "Simple Generic Name",
            "Start Date",
            "End Date",
            "Dose"
        ]
    ).copy()


def clean_all(notes, labs, medications):
    return (
        clean_notes(notes),
        clean_labs(labs),
        clean_medications(medications)
    )
