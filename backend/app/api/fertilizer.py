"""
fertilizer.py - FastAPI router for fertilizer recommendation
"""

import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Resolve path to the fertilizer_recommendation_system/src
FERT_SRC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "ai_models", "fertilizer_recommendation_system", "src"
)
if FERT_SRC not in sys.path:
    sys.path.insert(0, FERT_SRC)

router = APIRouter()

# ── Request / Response models ──────────────────────────────────────────────

class FertilizerRequest(BaseModel):
    temperature: float = Field(..., ge=0, le=60, example=28)
    humidity:    float = Field(..., ge=0, le=100, example=54)
    moisture:    float = Field(..., ge=0, le=100, example=38)
    soil_type:   str   = Field(..., example="Sandy")
    crop_type:   str   = Field(..., example="Maize")
    nitrogen:    float = Field(..., ge=0, le=100, example=37)
    potassium:   float = Field(..., ge=0, le=100, example=0)
    phosphorous: float = Field(..., ge=0, le=100, example=0)


class FertilizerResponse(BaseModel):
    fertilizer:   str
    confidence:   float
    npk:          str
    description:  str
    tip:          str
    organic_alt:  str
    icon:         str
    model_used:   str
    soil_health:  dict
    warnings:     list


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/fertilizer/predict", response_model=FertilizerResponse, tags=["Fertilizer"])
async def predict_fertilizer_endpoint(req: FertilizerRequest):
    """Predict best fertilizer for given soil/crop parameters."""
    try:
        from predict import predict_fertilizer
        from fertilizer_service import soil_health_check, get_overuse_warnings

        fertilizer, confidence, info, model_name = predict_fertilizer(
            req.temperature, req.humidity, req.moisture,
            req.soil_type, req.crop_type,
            req.nitrogen, req.potassium, req.phosphorous
        )

        health   = soil_health_check(req.nitrogen, req.potassium, req.phosphorous)
        warnings = get_overuse_warnings(req.nitrogen, req.potassium, req.phosphorous)

        return FertilizerResponse(
            fertilizer  = fertilizer,
            confidence  = round(confidence, 4),
            npk         = info.get("npk", "N/A"),
            description = info.get("description", ""),
            tip         = info.get("tip", ""),
            organic_alt = info.get("organic_alt", ""),
            icon        = info.get("icon", "🌱"),
            model_used  = model_name,
            soil_health = health,
            warnings    = warnings,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Fertilizer model not trained yet. Run train_pipeline.py first."
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")


@router.get("/fertilizer/options", tags=["Fertilizer"])
async def get_options():
    """Return available soil types and crop types."""
    try:
        from predict import get_soil_types, get_crop_types
        return {
            "soil_types": get_soil_types(),
            "crop_types": get_crop_types(),
        }
    except FileNotFoundError:
        # Return hardcoded defaults if model not trained yet
        return {
            "soil_types": ["Sandy", "Loamy", "Black", "Red", "Clayey"],
            "crop_types": ["Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
                           "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco", "Wheat"],
        }
