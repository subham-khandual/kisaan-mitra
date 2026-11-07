import asyncio
import sys
import os
import io

# Force UTF-8 console output on Windows to prevent UnicodeEncodeError crashes with agricultural emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_full_pipeline():
    print("\n" + "="*60)
    print("KISAAN MITRA — FULL ALERT PIPELINE TEST (ALL USERS)")
    print("="*60)

    # -----------------------------
    # 1. MongoDB CONNECTION
    # -----------------------------
    print("\n[1/6] Testing MongoDB connection...")
    try:
        from app.utils.database import connect_db, get_db
        await connect_db()
        db = get_db()
        print("  ✅ Connected to MongoDB")
        print(f"     Users: {await db.users.count_documents({})}")
        print(f"     Prices: {await db.prices.count_documents({})}")
        print(f"     Notifications: {await db.notifications.count_documents({})}")
    except Exception as e:
        print(f"  ❌ DB Error: {e}")
        return

    # -----------------------------
    # 2. API KEY CHECK
    # -----------------------------
    print("\n[2/6] Checking API keys...")
    from app.config import settings
    if not settings.AGMARKET_API_KEY:
        print("  ❌ Missing AgMarket API key")
        return
    else:
        print(f"  ✅ AgMarket API OK: {settings.AGMARKET_API_KEY[:8]}...")

    if not settings.OPENWEATHER_API_KEY:
        print("  ⚠️  Missing OpenWeather API key — weather alerts will be skipped")
    else:
        print(f"  ✅ OpenWeather API OK: {settings.OPENWEATHER_API_KEY[:8]}...")

    # -----------------------------
    # 3. FETCH USERS + CROPS
    # -----------------------------
    print("\n[3/6] Loading users with crops and FCM tokens...")
    users = await db.users.find({
        "is_active": True,
        "crops": {"$exists": True, "$ne": []}
    }).to_list(length=200)

    all_users = await db.users.find({"is_active": True}).to_list(length=200)

    if not users:
        print("  ❌ No users with crops found")
        return
    print(f"  👥 Total active users:      {len(all_users)}")
    print(f"  🌾 Users with crops:        {len(users)}")
    fcm_users = [u for u in all_users if u.get("fcm_token")]
    print(f"  📱 Users with FCM token:    {len(fcm_users)}")

    # -----------------------------
    # 4. PRICE ALERT FULL BLAST
    # -----------------------------
    print("\n[4/6] TRIGGERING PRICE ALERTS FOR ALL USERS")
    print("-"*60)
    from app.services.alert_engine import alert_engine
    before_price = await db.notifications.count_documents({})
    price_triggered = 0

    for user in users:
        print(f"\n👤 USER: {user.get('name')} | {user.get('location_district')}, {user.get('location_state')}")
        for crop in user["crops"]:
            commodity = crop["commodity"]
            state     = crop["state"]
            market    = crop.get("market", "Test Market")
            district  = crop.get("district", "")
            print(f"   🌾 {commodity} | {state} | {market}")
            try:
                before_each = await db.notifications.count_documents({})
                await alert_engine.process_price_update(
                    commodity=commodity,
                    market=market,
                    state=state,
                    district=district,
                    current_price=2500.0,   # FORCE HIGH PRICE
                    previous_price=2000.0   # FORCE 25% JUMP → triggers alert
                )
                after_each = await db.notifications.count_documents({})
                if after_each > before_each:
                    price_triggered += 1
                    print("   ✅ PRICE ALERT CREATED + PUSH SENT")
                else:
                    print("   ⚠️  No alert (check FCM token or threshold)")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")

    after_price = await db.notifications.count_documents({})

    # -----------------------------
    # 5. WEATHER ALERT FULL BLAST
    # -----------------------------
    print("\n[5/6] TRIGGERING WEATHER ALERTS FOR ALL USERS")
    print("-"*60)

    from app.services.firebase_service import firebase_service
    from datetime import datetime

    weather_sent = 0

    # Get all users with FCM tokens
    weather_users = await db.users.find(
        {"is_active": True, "fcm_token": {"$exists": True, "$ne": None}}
    ).to_list(length=500)

    if not weather_users:
        print("  ⚠️  No users with FCM tokens found — skipping weather alerts")
    else:
        # Try to fetch REAL weather first
        try:
            from app.services.weather_service import weather_service

            # Group users by district+state
            location_map = {}
            for user in weather_users:
                district = user.get("location_district", "Bengaluru")
                state    = user.get("location_state", "Karnataka")
                key      = f"{district}|{state}"
                if key not in location_map:
                    location_map[key] = {"district": district, "state": state, "users": []}
                location_map[key]["users"].append(user)

            for loc_key, loc_data in location_map.items():
                district  = loc_data["district"]
                state     = loc_data["state"]
                loc_users = loc_data["users"]

                print(f"\n  📍 Location: {district}, {state} ({len(loc_users)} users)")

                # Fetch real weather
                raw = await weather_service.get_weather_by_district_and_state(district, state)

                if raw:
                    parsed = weather_service.parse_weather(raw)
                    print(f"     🌡️  Real weather: {parsed['temp']}°C, {parsed['description']}, Humidity: {parsed['humidity']}%")

                    # For DEMO: Force a harsh weather alert regardless of actual weather
                    # This ensures push notification is always sent during demo
                    demo_alert = {
                        "title": f"⛈️ Demo Weather Alert — {district}!",
                        "body":  f"Real weather: {parsed['temp']}°C, {parsed['description']}. "
                                 f"Humidity {parsed['humidity']}%. "
                                 f"Kisaan Mitra is monitoring your farm 24/7! 🌾",
                        "alert_type": "demo",
                    }
                else:
                    print(f"     ⚠️  Could not fetch real weather — using demo data")
                    demo_alert = {
                        "title": f"🌧️ Demo Weather Alert — {district}!",
                        "body":  f"Heavy rain expected in {district}, {state}. "
                                 f"Secure your crops and check field drainage immediately!",
                        "alert_type": "demo",
                    }

                # Send to all users in this location
                for user in loc_users:
                    fcm_token = user.get("fcm_token")
                    if not fcm_token:
                        continue

                    sent = await firebase_service.send_price_alert(
                        fcm_token=fcm_token,
                        title=demo_alert["title"],
                        body=demo_alert["body"],
                        data={
                            "type":       "weather_alert",
                            "alert_type": demo_alert["alert_type"],
                            "district":   district,
                            "state":      state,
                        },
                        priority="high",
                    )

                    if sent:
                        weather_sent += 1
                        print(f"     ✅ Weather alert sent to {user.get('name')}")

                        # Save to DB for notification history
                        await db.weather_alerts.insert_one({
                            "user_id":       str(user["_id"]),
                            "alert_type":    "demo",
                            "title":         demo_alert["title"],
                            "body":          demo_alert["body"],
                            "district":      district,
                            "state":         state,
                            "firebase_sent": True,
                            "created_at":    datetime.utcnow(),
                        })
                    else:
                        print(f"     ❌ Failed to send to {user.get('name')} — check FCM token")

        except Exception as e:
            print(f"  ❌ Weather alert error: {e}")
            import traceback
            traceback.print_exc()

    # -----------------------------
    # 6. FINAL RESULT
    # -----------------------------
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULT")
    print("="*60)
    print(f"Users tested:              {len(all_users)}")
    print(f"Price alerts triggered:    {price_triggered}")
    print(f"Price notifications added: {after_price - before_price}")
    print(f"Weather alerts sent:       {weather_sent}")
    print("="*60)
    print("👉 NOW CHECK APP → ALERTS TAB → PULL TO REFRESH")
    print("👉 CHECK PHONE NOTIFICATION PANEL FOR PUSH ALERTS")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())