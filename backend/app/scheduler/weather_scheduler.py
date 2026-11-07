"""
Weather Scheduler — Runs every 30 minutes.
Fetches weather for ALL active users' locations worldwide.
Sends push alerts for harsh weather conditions.
Only Firebase push notifications — no SMS.
"""

from datetime import datetime
from app.utils.database import get_db
from app.services.weather_service import weather_service
from app.services.firebase_service import firebase_service


async def fetch_and_send_weather_alerts():
    """
    Scheduled job — runs every 30 minutes.
    1. Get all active users with FCM tokens
    2. Fetch weather for their district + state (works for any location)
    3. Send push alert if weather is harsh
    """
    start = datetime.now()
    print(f"\n🌤️  [{start.strftime('%H:%M:%S IST')}] Starting weather alert job...")

    db = get_db()

    # Get all active users with push tokens
    users = await db.users.find(
        {"is_active": True, "fcm_token": {"$exists": True, "$ne": None}}
    ).to_list(length=500)

    if not users:
        print("⚠️  No active users with FCM tokens found")
        return

    print(f"👥 Checking weather for {len(users)} users...")

    # Group users by district+state to avoid duplicate API calls
    location_map: dict = {}
    for user in users:
        district = user.get("location_district", "").strip()
        state    = user.get("location_state", "").strip()

        if not district and not state:
            continue

        # Use district+state as key
        location_key = f"{district}|{state}"
        if location_key not in location_map:
            location_map[location_key] = {
                "district": district,
                "state": state,
                "users": [],
            }
        location_map[location_key]["users"].append(user)

    alerts_sent = 0

    for location_key, location_data in location_map.items():
        district = location_data["district"]
        state    = location_data["state"]
        loc_users = location_data["users"]

        try:
            # Fetch weather using district + state for best accuracy
            raw = await weather_service.get_weather_by_district_and_state(district, state)

            if not raw:
                print(f"  ⚠️  No weather data for {district}, {state}")
                continue

            parsed = weather_service.parse_weather(raw)
            alert  = weather_service.should_send_alert(parsed)

            if not alert:
                print(f"  ✅ {district}, {state}: {parsed['temp']}°C, {parsed['description']} — no alert needed")
                continue

            print(f"  🚨 {district}, {state}: Sending '{alert['title']}' to {len(loc_users)} users")

            # Send push notification to all users in this location
            for user in loc_users:
                fcm_token = user.get("fcm_token")
                if not fcm_token:
                    continue

                sent = await firebase_service.send_price_alert(
                    fcm_token=fcm_token,
                    title=alert["title"],
                    body=alert["body"],
                    data={
                        "type":       "weather_alert",
                        "alert_type": alert["alert_type"],
                        "district":   district,
                        "state":      state,
                        "temp":       str(parsed["temp"]),
                        "condition":  parsed["condition"],
                    },
                    priority="high",
                )

                if sent:
                    alerts_sent += 1

                    # Save to DB for notification history
                    await db.weather_alerts.insert_one({
                        "user_id":    str(user["_id"]),
                        "alert_type": alert["alert_type"],
                        "title":      alert["title"],
                        "body":       alert["body"],
                        "district":   district,
                        "state":      state,
                        "temp":       parsed["temp"],
                        "condition":  parsed["condition"],
                        "wind_speed": parsed["wind_speed"],
                        "humidity":   parsed["humidity"],
                        "firebase_sent": True,
                        "created_at": datetime.utcnow(),
                    })

        except Exception as e:
            print(f"  ❌ Error for {district}, {state}: {e}")
            import traceback
            traceback.print_exc()

    elapsed = (datetime.now() - start).seconds
    print(f"✅ Weather job done. {alerts_sent} alerts sent in {elapsed}s")
