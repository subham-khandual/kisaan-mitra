"""
preprocess.py - Data Preprocessing for Fertilizer Recommendation System
Handles loading, cleaning, encoding, scaling, and train-test split
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "Fertilizer Prediction.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Feature/target column names
NUMERICAL_FEATURES = ["Temperature", "Humidity", "Moisture", "Nitrogen", "Potassium", "Phosphorous"]
CATEGORICAL_FEATURES = ["Soil Type", "Crop Type"]
TARGET = "Fertilizer Name"


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load dataset and fix known column name issues."""
    df = pd.read_csv(path)

    # Fix typo in 'Temparature' → 'Temperature' and strip trailing spaces
    df.columns = [c.strip() for c in df.columns]
    df.rename(columns={"Temparature": "Temperature"}, inplace=True)

    print(f"✅ Loaded dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates, handle missing values, strip strings."""
    initial = len(df)
    df = df.drop_duplicates()
    df = df.dropna()

    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    print(f"✅ Cleaned data: {initial} → {len(df)} rows")
    return df.reset_index(drop=True)


def encode_and_scale(df: pd.DataFrame, fit: bool = True,
                     le_soil=None, le_crop=None, le_target=None, scaler=None):
    """
    Encode categorical columns and scale numerical features.
    If fit=True: fit encoders/scaler and return them.
    If fit=False: use provided encoders/scaler.
    Returns: X (np.ndarray), y (np.ndarray), encoders, scaler
    """
    df = df.copy()

    if fit:
        le_soil   = LabelEncoder()
        le_crop   = LabelEncoder()
        le_target = LabelEncoder()
        scaler    = StandardScaler()

        df["Soil Type"] = le_soil.fit_transform(df["Soil Type"])
        df["Crop Type"] = le_crop.fit_transform(df["Crop Type"])
        y = le_target.fit_transform(df[TARGET])
    else:
        df["Soil Type"] = le_soil.transform(df["Soil Type"])
        df["Crop Type"] = le_crop.transform(df["Crop Type"])
        y = le_target.transform(df[TARGET]) if TARGET in df.columns else None

    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X_raw = df[feature_cols].values

    if fit:
        X = scaler.fit_transform(X_raw)
    else:
        X = scaler.transform(X_raw)

    return X, y, le_soil, le_crop, le_target, scaler


def split_data(X, y, test_size=0.2, random_state=42):
    """80/20 train-test split."""
    return train_test_split(X, y, test_size=test_size,
                            random_state=random_state, stratify=y)


def save_encoders(le_soil, le_crop, le_target, scaler):
    """Persist encoders and scaler to disk."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(le_soil,   os.path.join(MODELS_DIR, "le_soil.pkl"))
    joblib.dump(le_crop,   os.path.join(MODELS_DIR, "le_crop.pkl"))
    joblib.dump(le_target, os.path.join(MODELS_DIR, "encoder.pkl"))
    joblib.dump(scaler,    os.path.join(MODELS_DIR, "scaler.pkl"))
    print("✅ Encoders and scaler saved to models/")


def load_encoders():
    """Load persisted encoders and scaler."""
    le_soil   = joblib.load(os.path.join(MODELS_DIR, "le_soil.pkl"))
    le_crop   = joblib.load(os.path.join(MODELS_DIR, "le_crop.pkl"))
    le_target = joblib.load(os.path.join(MODELS_DIR, "encoder.pkl"))
    scaler    = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    return le_soil, le_crop, le_target, scaler


def get_prepared_data():
    """Full pipeline: load → clean → encode/scale → split."""
    df = load_data()
    df = clean_data(df)
    X, y, le_soil, le_crop, le_target, scaler = encode_and_scale(df, fit=True)
    save_encoders(le_soil, le_crop, le_target, scaler)
    X_train, X_test, y_train, y_test = split_data(X, y)
    print(f"✅ Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
    return X_train, X_test, y_train, y_test, le_target


if __name__ == "__main__":
    get_prepared_data()
