import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sksurv.ensemble import RandomSurvivalForest
from sksurv.metrics import concordance_index_censored
from sksurv.util import Surv


DATA_FILE = Path("data/processed/synthetic_2000_patients.json")
SEED = 20260916


def value(obj, *keys):
    if not isinstance(obj, dict):
        return None

    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]

    return None


def number(value_):
    try:
        return float(value_)
    except (TypeError, ValueError):
        return np.nan


def first_item(value_):
    if isinstance(value_, list):
        return value_[0] if value_ else {}
    if isinstance(value_, dict):
        return value_
    return {}


def extract_features(patient):
    demographics = patient.get("demographics_and_body_size", {})
    procedures = patient.get("aortic_valve_procedures", [])
    echoes = patient.get("echocardiograms", [])

    procedure = first_item(procedures)
    echo = first_item(echoes)

    age = number(
        value(demographics, "age", "age_at_implant")
    )

    bmi = number(
        value(demographics, "bmi")
    )

    weight = number(
        value(demographics, "weight_kg", "weight")
    )

    height = number(
        value(demographics, "height_cm", "height")
    )

    if np.isnan(bmi) and not np.isnan(weight) and not np.isnan(height):
        height_m = height / 100
        if height_m > 0:
            bmi = weight / (height_m ** 2)

    return {
        "age": age,
        "bmi": bmi,
        "time_since_implant": number(
            value(
                procedure,
                "years_since_implant",
                "time_since_implant_years",
            )
        ),
        "mean_gradient": number(
            value(
                echo,
                "mean_gradient",
                "mean_gradient_mmhg",
            )
        ),
        "peak_gradient": number(
            value(
                echo,
                "peak_gradient",
                "peak_gradient_mmhg",
            )
        ),
        "eoa": number(
            value(
                echo,
                "eoa",
                "effective_orifice_area",
            )
        ),
        "dvi": number(
            value(
                echo,
                "dvi",
                "doppler_velocity_index",
            )
        ),
        "lvef": number(
            value(
                echo,
                "lvef",
                "lvef_percent",
            )
        ),
        "num_echos": len(echoes) if isinstance(echoes, list) else 0,
    }


def create_survival_target(rng):
    scenario = rng.choice(
        [
            "stable",
            "slow_svd",
            "rapid_svd",
            "ppm",
            "leaflet_thrombosis",
            "endocarditis",
            "viv_failure",
        ],
        p=[
            0.70,
            0.12,
            0.04,
            0.06,
            0.04,
            0.02,
            0.02,
        ],
    )

    if scenario == "stable":
        return 12.0, False

    if scenario == "slow_svd":
        return rng.uniform(6.0, 12.0), True

    if scenario == "rapid_svd":
        return rng.uniform(2.0, 7.0), True

    return rng.uniform(1.0, 12.0), False


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(DATA_FILE)

    with DATA_FILE.open("r", encoding="utf-8") as f:
        patients = json.load(f)

    rng = np.random.default_rng(SEED)

    rows = []

    for patient in patients:
        features = extract_features(patient)
        time, event = create_survival_target(rng)

        rows.append(
            {
                "patient_id": patient["patient_id"],
                **features,
                "time": time,
                "event": event,
            }
        )

    df = pd.DataFrame(rows)

    feature_cols = [
        "age",
        "bmi",
        "time_since_implant",
        "mean_gradient",
        "peak_gradient",
        "eoa",
        "dvi",
        "lvef",
        "num_echos",
    ]

    indices = rng.permutation(len(df))

    train_end = int(len(df) * 0.60)
    val_end = int(len(df) * 0.80)

    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]

    X_train = df.loc[train_idx, feature_cols]
    X_val = df.loc[val_idx, feature_cols]
    X_test = df.loc[test_idx, feature_cols]

    y_train = Surv.from_arrays(
        df.loc[train_idx, "event"].astype(bool),
        df.loc[train_idx, "time"],
    )

    y_val = Surv.from_arrays(
        df.loc[val_idx, "event"].astype(bool),
        df.loc[val_idx, "time"],
    )

    y_test = Surv.from_arrays(
        df.loc[test_idx, "event"].astype(bool),
        df.loc[test_idx, "time"],
    )

    imputer = SimpleImputer(
        strategy="median",
        keep_empty_features=True,
    )

    X_train = imputer.fit_transform(X_train)
    X_val = imputer.transform(X_val)
    X_test = imputer.transform(X_test)

    model = RandomSurvivalForest(
        n_estimators=500,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        n_jobs=-1,
        random_state=SEED,
    )

    model.fit(
        X_train,
        y_train,
    )

    val_prediction = model.predict(X_val)

    val_cindex = concordance_index_censored(
        y_val["event"],
        y_val["time"],
        val_prediction,
    )[0]

    test_prediction = model.predict(X_test)

    test_cindex = concordance_index_censored(
        y_test["event"],
        y_test["time"],
        test_prediction,
    )[0]

    print("=" * 60)
    print("RANDOM SURVIVAL FOREST")
    print("=" * 60)
    print(f"Patients:           {len(df)}")
    print(f"Training:           {len(train_idx)}")
    print(f"Validation:         {len(val_idx)}")
    print(f"Test:               {len(test_idx)}")
    print(f"Validation C-index: {val_cindex:.4f}")
    print(f"Test C-index:       {test_cindex:.4f}")


if __name__ == "__main__":
    main()