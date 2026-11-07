"""
Kisaan Mitra — FastAPI Backend
Entry point: registers all routers including crop recommendation.
"""

import sys
import io

# Force UTF-8 console output on Windows to prevent UnicodeEncodeError crashes with agricultural emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import auth, prices, notifications, users, weather, crop_recommendation, fertilizer, history, crop_yield, disease, marketplace, reports
from app.utils.database import connect_db, disconnect_db
from app.scheduler.price_scheduler import start_scheduler, stop_scheduler
from app.scheduler.notifications import start_notification_scheduler, stop_notification_scheduler
from app.utils.seeder import seed_prices


import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_ok = False
    try:
        db_ok = await asyncio.wait_for(connect_db(), timeout=5.0)
    except Exception as e:
        print(f"\n[⚠️  MONGODB WARNING] MongoDB connection timed out or failed: {e}")
        print("[💡 TIP] Check your MONGODB_URL in backend/.env. Using offline DB mode.")

    if db_ok:
        try:
            await seed_prices()
            start_scheduler()
            start_notification_scheduler()
        except Exception as e:
            print(f"[!] Scheduler/seeder warning: {e}")
    else:
        print("[!] Running in offline DB mode: AI/ML models & prediction APIs are active!")

    yield

    if db_ok:
        try:
            stop_scheduler()
            stop_notification_scheduler()
        except Exception:
            pass
    await disconnect_db()


app = FastAPI(
    title="Kisaan Mitra API",
    description="Smart farmer assistant — prices, weather & AI crop recommendations",
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,                prefix="/api/v1", tags=["Authentication"])
app.include_router(prices.router,              prefix="/api/v1", tags=["Prices"])
app.include_router(notifications.router,       prefix="/api/v1", tags=["Notifications"])
app.include_router(users.router,               prefix="/api/v1", tags=["Users"])
app.include_router(weather.router,             prefix="/api/v1", tags=["Weather"])
app.include_router(crop_recommendation.router, prefix="/api/v1", tags=["Crop Recommendation"])
app.include_router(fertilizer.router,          prefix="/api/v1", tags=["Fertilizer"])
app.include_router(history.router,             prefix="/api/v1", tags=["History"])
app.include_router(crop_yield.router,          prefix="/api/v1", tags=["Crop Yield"])
app.include_router(disease.router,             prefix="/api/v1", tags=["Disease Detection"])
app.include_router(marketplace.router,         prefix="/api/v1", tags=["Marketplace"])
app.include_router(reports.router,             prefix="/api/v1", tags=["Reports"])


@app.get("/")
async def root():
    return {"message": "Kisaan Mitra API is running 🌾", "version": "1.2.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
