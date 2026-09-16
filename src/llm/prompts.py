def build_extraction_prompt(patient_id, notes):
    return f"""
You extract clinical facts from medical notes.

Patient ID:
{patient_id}

Medical notes:
{notes}

Return ONLY this JSON object:

{{
  "avr": {{
    "avr_date": null,
    "valve_type": null,
    "valve_model": null,
    "valve_size_mm": null
  }},
  "risk_factors": {{
    "age_at_avr_years": null,
    "sex": "unknown",
    "hypertension": "unknown",
    "diabetes": "unknown",
    "chronic_kidney_disease": "unknown",
    "coronary_artery_disease": "unknown",
    "heart_failure": "unknown"
  }},
  "echo": {{
    "last_echo_date": null,
    "mean_gradient_mmhg": null,
    "peak_gradient_mmhg": null,
    "lvef_percent": null,
    "aortic_regurgitation": null
  }},
  "events": [],
  "outcome": {{
    "prosthetic_valve_failure": "unknown",
    "structural_valve_deterioration": "unknown",
    "reintervention": "unknown",
    "event_date": null
  }}
}}

Rules:

Use ONLY facts explicitly supported by the notes.

Do not invent values.

Do not add fields.

Do not remove fields.

Do not rename fields.

Use null when a numeric or date value is unavailable.

Use "unknown" when a categorical value is unavailable.

Keep events short.

Return ONLY JSON.
""".strip()
