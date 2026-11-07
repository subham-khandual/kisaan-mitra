"""
User preference management routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from bson import ObjectId
from datetime import datetime

from app.models.schemas import UpdatePreferences, UserResponse
from app.utils.database import get_db
from app.api.auth import get_current_user
from app.config import settings
from jose import jwt, JWTError

router = APIRouter()


async def _get_user_from_header(
    authorization: str = Header(..., description="Bearer <token>"),
    db=Depends(get_db),
):
    """Extract and validate user from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    return await get_current_user(token, db)


@router.post("/user/preferences")
async def update_preferences(
    prefs: UpdatePreferences,
    user=Depends(_get_user_from_header),
    db=Depends(get_db),
):
    """
    Update user crop preferences, language, and FCM token.
    Called when farmer changes watched crops or language in settings.
    """
    update_data = {k: v for k, v in prefs.model_dump().items() if v is not None}

    # Convert CropPreference objects to dicts
    if "crops" in update_data:
        update_data["crops"] = [c.model_dump() if hasattr(c, 'model_dump') else c for c in update_data["crops"]]

    if not update_data:
        raise HTTPException(status_code=400, detail="No preferences to update")

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": update_data},
    )
    return {"message": "Preferences updated successfully"}


@router.get("/user/profile", response_model=UserResponse)
async def get_profile(
    user=Depends(_get_user_from_header),
    db=Depends(get_db),
):
    """Get the current user's profile."""
    # Update last_active
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_active": datetime.utcnow()}},
    )
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        phone=user["phone"],
        location_state=user["location_state"],
        location_district=user["location_district"],
        language=user.get("language", "en"),
        crops=user.get("crops", []),
        last_active=user.get("last_active", datetime.utcnow()),
        created_at=user.get("created_at", datetime.utcnow()),
    )


@router.post("/user/fix-crop-states")
async def fix_crop_states(
    user=Depends(_get_user_from_header),
    db=Depends(get_db),
):
    """
    One-time fix: updates all of the user's saved crops to use their
    actual registered state instead of the old hardcoded 'Karnataka' default.

    Call this once from the app after the CropSelectionScreen fix is deployed.
    Farmers who registered from non-Karnataka states had crops saved with
    state='Karnataka', which caused the alert engine to never match them.
    """
    actual_state = user.get("location_state")
    actual_district = user.get("location_district")

    if not actual_state:
        raise HTTPException(status_code=400, detail="User has no location_state set")

    crops = user.get("crops", [])
    if not crops:
        return {"message": "No crops to fix", "fixed": 0}

    fixed = 0
    updated_crops = []
    for crop in crops:
        # Case-insensitive comparison — handles "karnataka" vs "Karnataka"
        if crop.get("state", "").strip().lower() != actual_state.strip().lower():
            crop["state"] = actual_state
            crop["district"] = actual_district or crop.get("district", "")
            fixed += 1
        updated_crops.append(crop)

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"crops": updated_crops}},
    )

    return {
        "message": f"Fixed {fixed} crops — state updated to '{actual_state}'",
        "fixed": fixed,
        "total_crops": len(crops),
    }

@router.put("/user/fcm-token")
async def update_fcm_token(
    token_data: dict,
    user=Depends(_get_user_from_header),
    db=Depends(get_db),
):
    """
    Update device FCM token.
    Called when the React Native app receives a new FCM token from Firebase.
    """
    fcm_token = token_data.get("fcm_token")
    if not fcm_token:
        raise HTTPException(status_code=400, detail="fcm_token is required")

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"fcm_token": fcm_token}},
    )
    return {"message": "FCM token updated"}