import json


SYSTEM_PROMPT = """
You are a clinical information extraction system.

Your task is to extract structured clinical information from de-identified
clinical notes.

You must follow the supplied JSON schema exactly.

Rules:

1. Extract only information explicitly supported by the notes.
2. Do not infer facts that are not documented.
3. Do not diagnose conditions from medications alone.
4. Do not calculate values unless the value is explicitly documented.
5. Preserve raw clinical wording when the schema field ends with _raw.
6. Use null when a scalar field is not documented.
7. Use [] when a list has no documented entries.
8. Do not invent dates.
9. Do not invent valve model, manufacturer, size, material, mechanism,
   or procedural details.
10. Keep different valve positions separate.
11. Keep different procedures separate.
12. Keep serial echocardiograms as separate records.
13. If a note compares an echocardiogram with a previous study, preserve
    the comparison date and comparison text when available.
14. Evidence quotes must be copied from the supplied notes and must support
    the extracted information.
15. Do not classify a patient as having structural valve deterioration merely
    because symptoms, valve failure, valve dysfunction, stenosis, or a
    reintervention is mentioned.
16. Extract explicit statements about structural valve deterioration,
    hemodynamic deterioration, prosthetic valve failure, thrombosis,
    endocarditis, PPM, and nonstructural dysfunction separately.
17. Never use information from one patient to fill information for another.
18. Return JSON only.
"""


def build_messages(patient_id, notes, schema):
    notes_text = []

    for index, note in enumerate(notes, start=1):
        note_id = f"{patient_id}_NOTE_{index}"

        notes_text.append(
            "\n".join(
                [
                    f"NOTE_ID: {note_id}",
                    f"Profile Key: {note.get('Profile Key')}",
                    f"Note Type: {note.get('Note Type')}",
                    f"Type: {note.get('Type')}",
                    f"Service: {note.get('Service')}",
                    f"Signed Status: {note.get('Signed Status')}",
                    f"Authoring Provider Type: {note.get('Authoring Provider Type')}",
                    f"Authoring Provider Specialty: {note.get('Authoring Provider Specialty')}",
                    f"Service Date: {note.get('Service Date')}",
                    f"Creation Date: {note.get('Creation Date')}",
                    f"Last Edited Date: {note.get('Last Edited Date')}",
                    "NOTES:",
                    str(note.get("Notes") or ""),
                ]
            )
        )

    user_prompt = f"""
Patient ID: {patient_id}

Extract all clinically relevant information documented in the notes below.

The goal is high-recall extraction: populate every schema field that is
explicitly supported by the notes.

Do not omit documented information simply because it is not directly related
to aortic valve durability.

Use the exact schema below.

SCHEMA:
{json.dumps(schema, ensure_ascii=False, indent=2)}

CLINICAL NOTES:
{"\n\n".join(notes_text)}
"""

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
