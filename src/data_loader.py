import json
from pathlib import Path

import pandas as pd


def clean_value(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return value


def dataframe_to_records(df):
    records = []

    for row in df.to_dict(orient="records"):
        cleaned = {
            str(key): clean_value(value)
            for key, value in row.items()
        }
        records.append(cleaned)

    return records


def load_excel(path: Path):
    df = pd.read_excel(path)
    return dataframe_to_records(df)


def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
