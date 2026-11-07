from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.auth import get_current_user
from app.models.schemas import UserInDB, ActivityResponse, ActivityRecord
from app.utils.database import get_db
from bson import ObjectId
import traceback

router = APIRouter()

@router.get("/history", response_model=List[ActivityResponse])
async def get_user_history(current_user: UserInDB = Depends(get_current_user)):
    """
    Get the complete activity history for the currently logged-in user.
    Ordered from most recent to oldest.
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection failed")

    try:
        cursor = db.activity_history.find({"user_id": str(current_user.id)}).sort("created_at", -1).limit(50)
        history_records = await cursor.to_list(length=50)
        
        # Convert ObjectId back to string for response
        for doc in history_records:
            doc["_id"] = str(doc["_id"])
        
        return history_records
    except Exception as e:
        print(f"Error fetching history: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not fetch history")

@router.post("/history", response_model=ActivityResponse)
async def add_history_record(
    activity: ActivityRecord,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Add a new activity record to the user's history.
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection failed")

    activity.user_id = str(current_user.id)
    doc = activity.model_dump(by_alias=True, exclude={"id"})
    
    try:
        result = await db.activity_history.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc
    except Exception as e:
        print(f"Error saving history: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not save history")
