from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

from app.utils.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import UserInDB

router = APIRouter()

class MarketplaceListing(BaseModel):
    title: str
    description: str
    category: str # "crop", "seed", "fertilizer", "equipment"
    price: float
    unit: str # "kg", "quintal", "packet", "piece"
    location_state: str
    location_district: str
    contact_whatsapp: str
    contact_email: Optional[str] = ""

class ListingResponse(MarketplaceListing):
    id: str
    seller_id: str
    seller_name: str
    created_at: datetime

@router.post("/marketplace", response_model=ListingResponse)
async def create_listing(
    listing: MarketplaceListing,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Create a new listing in the Farmer Marketplace.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection failed")

    doc = listing.model_dump()
    doc["seller_id"] = str(current_user.id)
    doc["seller_name"] = current_user.name
    doc["created_at"] = datetime.utcnow()

    try:
        result = await db.marketplace.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        doc.pop("_id")
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not create listing")

@router.get("/marketplace", response_model=List[ListingResponse])
async def get_listings(
    category: Optional[str] = None,
    state: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """
    Get marketplace listings with optional filtering.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection failed")

    filter_query = {}
    if category:
        filter_query["category"] = category
    if state:
        filter_query["location_state"] = state
    if query:
        filter_query["title"] = {"$regex": query, "$options": "i"}

    cursor = db.marketplace.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
    listings = await cursor.to_list(length=limit)

    for doc in listings:
        doc["id"] = str(doc.pop("_id"))

    return listings
