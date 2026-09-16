import json


def get_patient_ids(notes, labs, medications):
    return sorted(
        set(notes["Profile Key"].dropna().astype(str))
        |
        set(labs["Patient"].dropna().astype(str))
        |
        set(medications["Patient"].dropna().astype(str))
    )


def get_patient_notes(patient_id, notes):
    patient_notes = notes[
        notes["Profile Key"].astype(str) == patient_id
    ]

    parts = []

    for _, row in patient_notes.iterrows():
        note = row.get("Notes")

        if note is not None:
            text = str(note).strip()

            if text:
                parts.append(text)

    return "\n\n".join(parts)


def parse_model_response(response):
    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model did not return a JSON object")

    return json.loads(
        response[start:end + 1]
    )


def extract_patient(
    client,
    patient_id,
    notes
):
    patient_notes = get_patient_notes(
        patient_id,
        notes
    )

    prompt = build_prompt(
        patient_id,
        patient_notes
    )

    response = client.generate(prompt)

    return parse_model_response(response)


from src.llm.prompts import build_extraction_prompt as build_prompt
