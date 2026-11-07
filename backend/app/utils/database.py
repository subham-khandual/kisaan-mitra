"""
MongoDB connection manager using Motor (async driver).
Provides a single shared client across the application.
"""

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING
from app.config import settings

# Global client and database references
client: motor.motor_asyncio.AsyncIOMotorClient = None
db: motor.motor_asyncio.AsyncIOMotorDatabase = None


async def connect_db() -> bool:
    """Initialize the MongoDB connection and create indexes."""
    global client, db

    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL, 
            serverSelectionTimeoutMS=4000
        )
        db = client[settings.MONGODB_DB_NAME]

        # Create indexes for performance
        await _create_indexes()
        print(f"[SUCCESS] Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        return True
    except Exception as e:
        print(f"\n[⚠️  MONGODB WARNING] Could not connect to MongoDB: {e}")
        print("[💡 TIP] Check your MONGODB_URL in backend/.env. If using local MongoDB, set: MONGODB_URL=mongodb://127.0.0.1:27017/kisaan_mitra")
        return False


async def disconnect_db():
    """Close the MongoDB connection gracefully."""
    global client
    if client:
        client.close()
        print("[DISCONNECTED] Disconnected from MongoDB")


async def _create_indexes():
    """Create all necessary indexes."""
    # Users: email and phone unique indexes (sparse so nulls don't conflict)
    try:
        await db.users.create_index([("email", ASCENDING)], unique=True, sparse=True)
        await db.users.create_index([("phone", ASCENDING)], unique=True, sparse=True)
        await db.users.create_index([("last_active", DESCENDING)])

        # Phone OTPs
        await db.otps.create_index([("phone", ASCENDING)])
        await db.otps.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

        # Email OTPs: email lookup and automatic cleanup on expiration
        await db.email_otps.create_index([("email", ASCENDING)])
        await db.email_otps.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    except Exception as e:
        print(f"[!] Warning creating index: {e}")

    # Prices: compound index for fast lookups by commodity + mandi + date
    await db.prices.create_index([
        ("commodity", ASCENDING),
        ("state", ASCENDING),
        ("district", ASCENDING),
        ("market", ASCENDING),
        ("arrival_date", DESCENDING),
    ])
    await db.prices.create_index([("fetched_at", DESCENDING)])

    # Notifications: look up by user and status quickly
    await db.notifications.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await db.notifications.create_index([("status", ASCENDING)])

    print("[INFO] MongoDB indexes created")


def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Dependency injection helper for FastAPI routes."""
    return db
