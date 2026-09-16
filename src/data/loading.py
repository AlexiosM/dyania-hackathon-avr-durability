import pandas as pd


def load_excel_files(notes_file, labs_file, medications_file):
    notes = pd.read_excel(notes_file)
    labs = pd.read_excel(labs_file)
    medications = pd.read_excel(medications_file)

    return notes, labs, medications
