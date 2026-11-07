import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from app.ml.yield_prediction import CropYieldPredictor

router = APIRouter()

ml_models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml', 'models')
predictor = CropYieldPredictor(ml_models_dir)

class YieldPredictionRequest(BaseModel):
    region: str
    soil_type: str
    crop: str
    rainfall_mm: float
    temperature_celsius: float
    fertilizer_used: bool
    irrigation_used: bool
    weather_condition: str
    days_to_harvest: int

@router.post("/crop-yield/predict")
async def predict_crop_yield(req: YieldPredictionRequest):
    """
    Predict crop yield based on region, soil, crop, weather, and farming practices.
    """
    try:
        result = predictor.predict(
            region=req.region,
            soil_type=req.soil_type,
            crop=req.crop,
            rainfall_mm=req.rainfall_mm,
            temperature_celsius=req.temperature_celsius,
            fertilizer_used=req.fertilizer_used,
            irrigation_used=req.irrigation_used,
            weather_condition=req.weather_condition,
            days_to_harvest=req.days_to_harvest
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/crop-yield/metadata")
async def get_crop_yield_metadata():
    """
    Get unique values for categorical features to populate frontend dropdowns.
    """
    metadata_path = os.path.join(ml_models_dir, 'crop_yield_metadata.json')
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        return {
            "success": True,
            "data": data
        }
    return {
        "success": False,
        "error": "Metadata not found."
    }
