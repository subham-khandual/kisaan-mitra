import os
import io
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image

import tensorflow as tf
from tensorflow import keras

router = APIRouter()

CLASS_NAMES = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "models", "plant_disease.keras")

TREATMENTS = {
    "Apple scab": "Apply Captan or Mancozeb fungicide. Prune affected branches and remove fallen leaves.",
    "Apple black rot": "Spray Thiophanate-methyl or Myclobutanil. Remove infected fruit and cankers.",
    "Apple cedar apple rust": "Apply Sulfur-based or Propiconazole fungicide. Remove nearby juniper bushes.",
    "Apple healthy": "No treatment needed. Continue standard apple care.",
    "Blueberry healthy": "No treatment needed. Maintain acidic soil pH (4.5-5.5).",
    "Cherry powdery mildew": "Apply Sulfur fungicide or Potassium bicarbonate. Improve air circulation.",
    "Cherry healthy": "No treatment needed. Continue standard cherry tree care.",
    "Corn cercospora leaf spot": "Apply Pyraclostrobin or Azoxystrobin fungicide at first sign.",
    "Corn common rust": "Apply Mancozeb or Prothioconazole fungicide. Use resistant hybrids.",
    "Corn northern leaf blight": "Apply Azoxystrobin or Propiconazole fungicide. Rotate crops.",
    "Corn healthy": "No treatment needed. Continue standard corn crop management.",
    "Grape black rot": "Apply Mancozeb or Myclobutanil. Remove mummified fruit.",
    "Grape esca": "No chemical cure. Remove infected vines. Apply Boron and Calcium supplements.",
    "Grape leaf blight": "Apply Copper-based fungicide. Ensure good trellising for air flow.",
    "Grape healthy": "No treatment needed. Maintain regular pruning and monitoring.",
    "Orange haunglongbing": "No cure available. Remove infected trees immediately. Control psyllid vectors.",
    "Peach bacterial spot": "Apply Copper-based bactericide. Prune in dry weather.",
    "Peach healthy": "No treatment needed. Continue standard peach tree care.",
    "Pepper bacterial spot": "Apply Copper fungicide. Use disease-free seeds.",
    "Pepper healthy": "No treatment needed. Continue standard bell pepper practices.",
    "Potato early blight": "Apply Mancozeb or Chlorothalonil. Practice crop rotation.",
    "Potato late blight": "Apply Metalaxyl or Mancozeb immediately. Destroy infected plants.",
    "Potato healthy": "No treatment needed. Continue standard potato management.",
    "Raspberry healthy": "No treatment needed. Maintain regular pruning and trellising.",
    "Soybean healthy": "No treatment needed. Continue standard soybean management.",
    "Squash powdery mildew": "Apply Sulfur fungicide or Neem oil. Ensure good spacing.",
    "Strawberry leaf scorch": "Apply Captan or Iprodione fungicide. Remove infected leaves.",
    "Strawberry healthy": "No treatment needed. Maintain proper spacing.",
    "Tomato bacterial spot": "Apply Copper bactericide. Use disease-free transplants.",
    "Tomato early blight": "Spray Chlorothalonil or Copper fungicide. Remove lower infected leaves.",
    "Tomato late blight": "Apply Metalaxyl or Mancozeb immediately. Remove infected plants.",
    "Tomato leaf mold": "Improve ventilation. Apply Chlorothalonil or Copper fungicide.",
    "Tomato septoria leaf spot": "Apply Mancozeb or Chlorothalonil. Remove infected leaves.",
    "Tomato spider mites": "Apply insecticidal soap or Neem oil. Keep plants well-watered.",
    "Tomato target spot": "Apply Chlorothalonil or Mancozeb. Ensure proper spacing.",
    "Tomato yellow leaf curl virus": "Control whiteflies with Imidacloprid. Remove infected plants.",
    "Tomato mosaic virus": "Remove infected plants. Use resistant varieties.",
    "Tomato healthy": "No treatment needed. Continue standard tomato care."
}


_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"Model not found at {MODEL_PATH}. Run train_disease_model.py first.")
        _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    return _model


def analyze_health_by_color(img):
    green_pixels = 0
    spot_pixels = 0
    other_plant_pixels = 0
    total = img.width * img.height

    for r, g, b in img.getdata():
        if (g > r) and (g > b):
            green_pixels += 1
        elif (r > g + 15 and r > b + 15) or (r > 120 and g > 60 and b < 80) or (r < 50 and g < 50 and b < 50):
            spot_pixels += 1
        elif (r > 100) and (g > 60) and (b < 120):
            other_plant_pixels += 1

    green_ratio = green_pixels / max(total, 1)
    spot_ratio = spot_pixels / max(total, 1)
    other_ratio = other_plant_pixels / max(total, 1)

    if green_ratio < 0.1 and (spot_ratio + other_ratio) > 0.5:
        has_disease = True
    elif green_ratio > 0:
        has_disease = (spot_pixels / max(green_pixels, 1)) > 0.08
    else:
        has_disease = True

    return has_disease, green_ratio, spot_ratio


def find_treatment(crop_name, disease_name):
    is_healthy = "healthy" in disease_name.lower()
    if is_healthy:
        for key, val in TREATMENTS.items():
            if crop_name.lower() in key.lower() and "healthy" in key.lower():
                return val
        return f"No treatment needed. {crop_name} appears healthy."

    for key, val in TREATMENTS.items():
        if disease_name.lower() in key.lower() or key.lower() in disease_name.lower():
            return val
    for key, val in TREATMENTS.items():
        if crop_name.lower() in key.lower():
            return val

    return "Consult local agricultural extension officer for region-specific recommendations."


@router.post("/disease/detect")
async def detect_disease(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    image_bytes = await file.read()

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img_rgb = img.convert('RGB')
        thumb = img_rgb.copy()
        thumb.thumbnail((100, 100))

        plant_pixels = 0
        total_pixels = thumb.width * thumb.height
        for r, g, b in thumb.getdata():
            is_green = (g > r) and (g > b)
            is_yellow_orange = (r > 120) and (g > 60) and (b < 100)
            is_brown = (r > 60) and (g > 20) and (b < 60) and (r > g)
            is_dark = (r < 40) and (g < 40) and (b < 40)
            if is_green or is_yellow_orange or is_brown or is_dark:
                plant_pixels += 1

        if total_pixels > 0 and (plant_pixels / total_pixels) < 0.10:
            raise HTTPException(
                status_code=400,
                detail="Image does not appear to be a plant leaf. Please upload a clearer photo focused on the crop."
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    try:
        model = get_model()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        img_resized = img_rgb.resize((224, 224))
        input_data = np.expand_dims(np.array(img_resized, dtype=np.float32) / 255.0, axis=0)

        predictions = model.predict(input_data, verbose=0)[0]
        top_idx = int(np.argmax(predictions))
        confidence = float(predictions[top_idx]) * 100

        raw_class = CLASS_NAMES[top_idx]
        parts = raw_class.split('___')
        crop_raw = parts[0].replace('_', ' ')
        disease_raw = parts[1].replace('_', ' ') if len(parts) > 1 else "Unknown"

        crop_clean = crop_raw.replace('(maize)', '').replace(' bell', '').replace('(Citrus greening)', '')
        crop_clean = crop_clean.replace('  ', ' ').strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease detection failed: {str(e)}")

    has_disease_color, green_ratio, spot_ratio = analyze_health_by_color(thumb)

    color_suggests_disease = has_disease_color
    model_says_healthy = "healthy" in disease_raw.lower()

    if confidence < 15.0:
        crop_clean = "Plant"
        confidence = 0.0
        if color_suggests_disease:
            disease = "Disease Detected"
        else:
            disease = "Healthy"
        is_healthy = not color_suggests_disease
    elif confidence < 30.0:
        if color_suggests_disease:
            disease = "Disease Detected"
        else:
            disease = "Healthy"
        is_healthy = not color_suggests_disease
    else:
        disease = disease_raw
        is_healthy = model_says_healthy

    treatment = find_treatment(crop_clean, disease)

    return {
        "success": True,
        "data": {
            "crop": crop_clean,
            "disease": disease,
            "confidence": round(confidence, 2),
            "treatment": treatment,
            "action_required": not is_healthy
        }
    }
