"""
Weather API — Real-time weather + Dynamic farming tips.
No paid API needed — tips generated from real weather data.
"""

from fastapi import APIRouter, Query
from typing import Optional

from app.services.weather_service import weather_service
from app.services.dynamic_farming_tips_service import dynamic_farming_tips_service

router = APIRouter()


@router.get("/weather")
async def get_weather(
    lat:     Optional[float] = Query(None),
    lon:     Optional[float] = Query(None),
    city:    Optional[str]   = Query(None),
    state:   Optional[str]   = Query(None),
    country: Optional[str]   = Query("IN"),
    crops:   Optional[str]   = Query(None, description="Comma separated crop names e.g. Maize,Rice"),
):
    """
    Get current weather + dynamic farming tips for any location worldwide.
    Tips are personalized based on exact weather values + user's crops.
    """
    raw = None

    if lat and lon:
        raw = await weather_service.get_current_weather(lat, lon)
    elif city and state:
        raw = await weather_service.get_weather_by_district_and_state(city, state)
    elif city:
        raw = await weather_service.get_weather_by_city(city, country=country or "IN")
    else:
        raw = await weather_service.get_weather_by_city("Bengaluru", country="IN")

    if not raw:
        return {"error": "Could not fetch weather data. Please try again."}

    parsed = weather_service.parse_weather(raw)
    alert  = weather_service.should_send_alert(parsed)

    # Parse crops list
    crop_list = [c.strip() for c in crops.split(",")] if crops else []

    # Generate dynamic farming tips — FREE, no API needed
    farming_tips = dynamic_farming_tips_service.generate_tips(
        weather=parsed,
        crops=crop_list,
        district=city or "your area",
        state=state or "",
    )

    return {
        "weather":      parsed,
        "alert":        alert,
        "farming_tips": farming_tips,
    }


@router.get("/weather/test-alert")
async def test_weather_alert():
    """Manually trigger weather alert job for all users."""
    from app.scheduler.weather_scheduler import fetch_and_send_weather_alerts
    await fetch_and_send_weather_alerts()
    return {"message": "Weather alert job triggered!"}


@router.get("/weather/force-alert")
async def force_weather_alert():
    """Send a test push notification to all users immediately."""
    from app.utils.database import get_db
    from app.services.firebase_service import firebase_service

    db = get_db()
    users = await db.users.find(
        {"is_active": True, "fcm_token": {"$exists": True, "$ne": None}}
    ).to_list(length=100)

    sent = 0
    for user in users:
        result = await firebase_service.send_price_alert(
            fcm_token=user["fcm_token"],
            title="🌧️ Test Weather Alert!",
            body="Heavy rain expected in your area! Secure your crops.",
            data={"type": "weather_alert", "alert_type": "test"},
            priority="high",
        )
        if result:
            sent += 1

    return {"message": f"Force alert sent to {sent} users!"}
