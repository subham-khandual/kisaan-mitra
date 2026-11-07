import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.utils.database import get_db

notification_scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

async def check_weather_and_prices():
    """
    Background task runner checking for weather/price changes.
    Simulates checks and generates in-app notifications.
    """
    db = get_db()
    if db is None:
        return

    print(f"\n🔔 [{datetime.now().strftime('%H:%M:%S IST')}] Checking for smart notifications...")

    try:
        # Example: Generate a mock weather alert for all users in a specific region
        # In a real scenario, this would call Weather API and compare with past data
        users_cursor = db.users.find({"is_active": True})
        users = await users_cursor.to_list(length=100)

        for user in users:
            alert_doc = {
                "user_id": str(user["_id"]),
                "alert_type": "critical", # Map to AlertType schema
                "commodity": "Weather",
                "market": user.get('location_district', 'Local'),
                "old_price": 0,
                "new_price": 0,
                "change_pct": 0,
                "message_en": f"Heavy rainfall expected in {user.get('location_district', 'your area')} tomorrow. Please delay pesticide application.",
                "message_kn": "",
                "firebase_sent": True,
                "sms_sent": False,
                "status": "sent",
                "created_at": datetime.utcnow()
            }
            
            existing = await db.notifications.find_one({
                "user_id": str(user["_id"]),
                "message_en": alert_doc["message_en"]
            })

            if not existing:
                await db.notifications.insert_one(alert_doc)
                print(f"Sent smart weather alert to {user.get('name')}")
                
    except Exception as e:
        print(f"Error in smart notifications scheduler: {e}")

def start_notification_scheduler():
    notification_scheduler.add_job(
        check_weather_and_prices,
        trigger=IntervalTrigger(minutes=60), # Check every hour
        id="smart_notifications",
        name="Smart Notifications for Weather/Prices",
        replace_existing=True,
        max_instances=1
    )
    notification_scheduler.start()
    print("🔔 Smart Notification Scheduler started")

def stop_notification_scheduler():
    if notification_scheduler.running:
        notification_scheduler.shutdown(wait=False)
        print("🛑 Smart Notification Scheduler stopped")
