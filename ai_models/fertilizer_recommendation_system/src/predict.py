"""
predict.py - Fertilizer Prediction Module
Loads saved model, preprocesses user inputs, returns fertilizer + confidence
"""

import os
import joblib
import numpy as np

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Fertilizer descriptions / tips
FERTILIZER_INFO = {
    "Urea": {
        "npk": "46-0-0",
        "description": "High nitrogen content. Best for leafy growth and vegetative stage.",
        "tip": "Apply in split doses to avoid nitrogen burn. Do not apply before heavy rain.",
        "organic_alt": "Compost, Cow Dung Manure, Neem Cake",
        "icon": "🌿",
    },
    "DAP": {
        "npk": "18-46-0",
        "description": "Di-Ammonium Phosphate. Excellent nitrogen and phosphorus source.",
        "tip": "Apply at sowing time for root development. Avoid mixing with alkaline fertilizers.",
        "organic_alt": "Bone Meal, Rock Phosphate",
        "icon": "🌱",
    },
    "14-35-14": {
        "npk": "14-35-14",
        "description": "Balanced NPK with high phosphorus. Ideal for fruiting and flowering.",
        "tip": "Best applied during early growth stages.",
        "organic_alt": "Fish Meal, Compost",
        "icon": "🌺",
    },
    "28-28": {
        "npk": "28-28-0",
        "description": "Equal nitrogen and phosphorus blend.",
        "tip": "Use during vegetative growth. Do not over-apply.",
        "organic_alt": "Green Manure, Vermicompost",
        "icon": "🌾",
    },
    "17-17-17": {
        "npk": "17-17-17",
        "description": "Perfectly balanced NPK. Suitable for all soil types.",
        "tip": "Excellent for maintenance fertilization throughout the season.",
        "organic_alt": "Mixed Compost",
        "icon": "⚖️",
    },
    "20-20": {
        "npk": "20-20-0",
        "description": "Equal nitrogen and phosphorus. Good for early crop stages.",
        "tip": "Apply before sowing. Mix well into the soil.",
        "organic_alt": "Poultry Manure, Bone Meal",
        "icon": "🌻",
    },
    "10-26-26": {
        "npk": "10-26-26",
        "description": "Low nitrogen, high phosphorus and potassium. Ideal for fruiting crops.",
        "tip": "Best for flowering and fruiting stages. Promotes strong roots.",
        "organic_alt": "Wood Ash, Banana Peel Compost",
        "icon": "🍅",
    },
}


def load_model():
    data      = joblib.load(os.path.join(MODELS_DIR, "best_fertilizer_model.pkl"))
    le_soil   = joblib.load(os.path.join(MODELS_DIR, "le_soil.pkl"))
    le_crop   = joblib.load(os.path.join(MODELS_DIR, "le_crop.pkl"))
    le_target = joblib.load(os.path.join(MODELS_DIR, "encoder.pkl"))
    scaler    = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    return data["model"], data["name"], le_soil, le_crop, le_target, scaler


def predict_fertilizer(temperature: float, humidity: float, moisture: float,
                        soil_type: str, crop_type: str,
                        nitrogen: float, potassium: float, phosphorous: float):
    """
    Returns:
        fertilizer (str), confidence (float 0-1), info (dict)
    """
    model, model_name, le_soil, le_crop, le_target, scaler = load_model()

    # Encode categoricals
    try:
        soil_enc = le_soil.transform([soil_type])[0]
        crop_enc = le_crop.transform([crop_type])[0]
    except ValueError as e:
        raise ValueError(f"Unknown category: {e}")

    # Feature order must match training: Numerical + Categorical
    raw = np.array([[temperature, humidity, moisture,
                     nitrogen, potassium, phosphorous,
                     soil_enc, crop_enc]])
    X = scaler.transform(raw)

    proba  = model.predict_proba(X)[0]
    pred   = np.argmax(proba)
    fertilizer  = le_target.inverse_transform([pred])[0]
    confidence  = float(proba[pred])
    info        = FERTILIZER_INFO.get(fertilizer, {})

    return fertilizer, confidence, info, model_name


def get_soil_types():
    le_soil = joblib.load(os.path.join(MODELS_DIR, "le_soil.pkl"))
    return list(le_soil.classes_)


def get_crop_types():
    le_crop = joblib.load(os.path.join(MODELS_DIR, "le_crop.pkl"))
    return list(le_crop.classes_)


if __name__ == "__main__":
    fertilizer, confidence, info, model = predict_fertilizer(
        temperature=28, humidity=54, moisture=38,
        soil_type="Sandy", crop_type="Maize",
        nitrogen=37, potassium=0, phosphorous=0
    )
    print(f"\n✅ Recommended Fertilizer : {fertilizer}")
    print(f"📊 Confidence            : {confidence*100:.1f}%")
    print(f"🤖 Model used            : {model}")
    print(f"📋 NPK Ratio             : {info.get('npk', 'N/A')}")
    print(f"💡 Tip                   : {info.get('tip', '')}")
