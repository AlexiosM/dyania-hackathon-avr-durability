import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sksurv.linear_model import CoxnetSurvivalAnalysis
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
        value(
            demographics,
            "age",
            "age_at_implant",
        )
    )

    bmi = number(
        value(
            demographics,
            "bmi",
        )
    )

    weight = number(
        value(
            demographics,
            "weight_kg",
            "weight",
        )
    )

    height = number(
        value(
            demographics,
            "height_cm",
            "height",
        )
    )

    if np.isnan(bmi) and not np.isnan(weight) and not np.isnan(height):
        height_m = height / 100
        if height_m > 0:
            bmi = weight / (height_m ** 2)

    mean_gradient = number(
        value(
            echo,
            "mean_gradient",
            "mean_gradient_mmhg",
        )
    )

    peak_gradient = number(
        value(
            echo,
            "peak_gradient",
            "peak_gradient_mmhg",
        )
    )

    eoa = number(
        value(
            echo,
            "eoa",
            "effective_orifice_area",
        )
    )

    dvi = number(
        value(
            echo,
            "dvi",
            "doppler_velocity_index",
        )
    )

    lvef = number(
        value(
            echo,
            "lvef",
            "lvef_percent",
        )
    )

    implant_years = number(
        value(
            procedure,
            "years_since_implant",
            "time_since_implant_years",
        )
    )

    return {
        "age": age,
        "bmi": bmi,
        "time_since_implant": implant_years,
        "mean_gradient": mean_gradient,
        "peak_gradient": peak_gradient,
        "eoa": eoa,
        "dvi": dvi,
        "lvef": lvef,
        "num_echos": len(echoes) if isinstance(echoes, list) else 0,
    }


def create_survival_target(patient, rng):
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
        time, event = create_survival_target(patient, rng)

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

    rng_split = np.random.default_rng(SEED)
    indices = rng_split.permutation(len(df))

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

    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    model = CoxnetSurvivalAnalysis(
        l1_ratio=0.5,
        alpha_min_ratio=0.01,
        n_alphas=100,
        max_iter=100000,
    )

    model.fit(X_train, y_train)

    best_alpha = None
    best_val_cindex = -np.inf

    for alpha in model.alphas_:
        prediction = model.predict(
            X_val,
            alpha=alpha,
        )

        cindex = concordance_index_censored(
            y_val["event"],
            y_val["time"],
            prediction,
        )[0]

        if cindex > best_val_cindex:
            best_val_cindex = cindex
            best_alpha = alpha

    test_prediction = model.predict(
        X_test,
        alpha=best_alpha,
    )

    test_cindex = concordance_index_censored(
        y_test["event"],
        y_test["time"],
        test_prediction,
    )[0]

    alpha_index = np.argmin(
        np.abs(model.alphas_ - best_alpha)
    )

    coefficients = model.coef_[:, alpha_index]

    print("=" * 60)
    print("ELASTIC-NET COX")
    print("=" * 60)
    print(f"Patients:          {len(df)}")
    print(f"Training:          {len(train_idx)}")
    print(f"Validation:        {len(val_idx)}")
    print(f"Test:              {len(test_idx)}")
    print(f"Best alpha:        {best_alpha:.6f}")
    print(f"Validation C-index:{best_val_cindex:.4f}")
    print(f"Test C-index:      {test_cindex:.4f}")
    print()
    print("Coefficients:")

    for feature, coefficient in zip(feature_cols, coefficients):
        print(f"{feature:30s} {coefficient: .6f}")


if __name__ == "__main__":
    main()