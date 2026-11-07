"""
Crop Recommendation API — AI-powered crop recommendations using ML and LLM (Groq).
"""

import os
from fastapi import APIRouter, Query
from typing import Optional
from pydantic import BaseModel

from app.services.crop_recommendation_service import crop_recommendation_service
from app.services.weather_service import weather_service

# Import our custom ML predictor and utilities
from app.ml.prediction import CropPredictor
from app.ml.utils import AgTechUtils
from app.ml.state_crop_mapping import adjust_probabilities_for_state

router = APIRouter()

# Initialize ML Predictor (runs once when FastAPI starts)
ml_models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml', 'models')
predictor = CropPredictor(ml_models_dir)


class RecommendationRequest(BaseModel):
    soil_type: str
    water_availability: str
    previous_crop: Optional[str] = ""
    land_size: Optional[str] = ""
    farming_type: Optional[str] = "Conventional"


class MLCropRequest(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    state: Optional[str] = ""
    district: Optional[str] = ""


@router.post("/crop-recommendation")
async def get_crop_recommendation(req: RecommendationRequest):
    """
    Get AI crop recommendations based on:
    - Soil type, water availability, previous crop
    - Real-time weather from OpenWeatherMap
    - Current season (auto-detected)
    - Location (state + district)
    """

    # Cannot fetch real-time weather without location, so use fallback
    raw_weather = None

    if raw_weather:
        weather = weather_service.parse_weather(raw_weather)
    else:
        # Fallback weather if fetch fails
        weather = {
            "temp": 30, "feels_like": 32, "humidity": 65,
            "condition": "Clear", "description": "clear sky",
            "wind_speed": 10, "rain_1h": 0,
        }

    recommendations = await crop_recommendation_service.get_recommendations(
        soil_type=req.soil_type,
        water_availability=req.water_availability,
        previous_crop=req.previous_crop or "",
        weather=weather,
        land_size=req.land_size,
        farming_type=req.farming_type,
    )

    return {
        "recommendations": recommendations,
        "weather_used": weather,
        "location": "Unknown",
    }


@router.post("/crop-recommendation/predict")
async def get_ml_crop_recommendation(req: MLCropRequest):
    """
    Get machine learning crop recommendations based on soil macronutrients (N, P, K),
    pH level, temperature, humidity, and rainfall.
    """
    try:
        # 1. Calculate prediction from Random Forest
        prediction_result = predictor.predict(
            n=req.N,
            p=req.P,
            k=req.K,
            temperature=req.temperature,
            humidity=req.humidity,
            ph=req.ph,
            rainfall=req.rainfall
        )

        # Re-adjust probabilities based on State geographic logic
        if req.state:
            adjusted_probs = adjust_probabilities_for_state(prediction_result.get("all_probabilities", {}), req.state)
            if adjusted_probs:
                prediction_result["all_probabilities"] = adjusted_probs
                new_top_crop = list(adjusted_probs.keys())[0]
                prediction_result["crop"] = new_top_crop
                prediction_result["confidence"] = adjusted_probs[new_top_crop]

        recommended_crop = prediction_result["crop"]

        # 2. Calculate Soil Health metrics
        soil_analysis = AgTechUtils.analyze_soil_health(
            n=req.N, p=req.P, k=req.K, ph=req.ph
        )
        soil_analysis["details"] = f"Soil pH level is {req.ph} ({soil_analysis['ph_status']}). Macronutrients show a fertile balance with a health index of {soil_analysis['score']}/100."

        # 3. Calculate fertilizer dosage
        fertilizer_advice = AgTechUtils.recommend_fertilizers(
            n=req.N, p=req.P, k=req.K, target_crop=recommended_crop
        )
        
        chemical_remediation = []
        if fertilizer_advice["status"] == "success":
            for rec in fertilizer_advice["recommendations"]:
                if "Balanced" in rec["element"]:
                    continue
                import re
                dose_str = rec.get("dose", "0")
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", dose_str)
                amount = float(numbers[0]) if numbers else 0.0
                
                chemical_remediation.append({
                    "fertilizer": rec.get("fertilizer", "Standard NPK").split(" (")[0],
                    "amount_kg_hectare": round(amount, 2),
                    "application_stage": rec.get("role", "General growth booster")
                })
        
        fertilizer_prescription = {
            "N_deficit": round(float(fertilizer_advice["deficits"]["N"]), 2),
            "P_deficit": round(float(fertilizer_advice["deficits"]["P"]), 2),
            "K_deficit": round(float(fertilizer_advice["deficits"]["K"]), 2),
            "chemical_remediation": chemical_remediation,
            "organic_remediation": fertilizer_advice.get("soil_actions", [])
        }

        # 4. Estimate crop yield
        yield_estimate = AgTechUtils.predict_crop_yield(
            n=req.N,
            p=req.P,
            k=req.K,
            temperature=req.temperature,
            humidity=req.humidity,
            ph=req.ph,
            rainfall=req.rainfall,
            recommended_crop=recommended_crop
        )
        
        yield_forecasting = {
            "expected_yield_tonnes_hectare": float(yield_estimate["expected_yield_t_ha"]),
            "yield_rating": yield_estimate["yield_level"],
            "yield_factors": yield_estimate["reasons"]
        }

        # Extract alternative crops from all_probabilities
        all_probs = prediction_result.get("all_probabilities", {})
        alternatives = []
        for crop_name, prob in list(all_probs.items()):
            if crop_name.lower() == recommended_crop.lower():
                continue
            alternatives.append({
                "crop": crop_name.capitalize(),
                "confidence": round(float(prob * 100), 2)
            })

        # 5. Map the ML output to match a structured format with crop recommendations
        return {
            "success": True,
            "recommended_crop": recommended_crop,
            "confidence": round(float(prediction_result["confidence"] * 100), 2),
            "alternatives": alternatives[:3], # top 3 back-up choices
            "soil_health": soil_analysis,
            "fertilizer_prescription": fertilizer_prescription,
            "yield_forecasting": yield_forecasting,
            "inputs_used": {
                "N": req.N,
                "P": req.P,
                "K": req.K,
                "temperature": req.temperature,
                "humidity": req.humidity,
                "ph": req.ph,
                "rainfall": req.rainfall
            }
        }
    except Exception as e:
        import traceback
        print("CRITICAL ERROR IN ROUTE:", str(e))
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

