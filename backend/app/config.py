"""
Configuration management using Pydantic Settings.
All secrets loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────────────────────
    APP_NAME: str = "Kisaan Mitra"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "t", "yes", "debug")
        return bool(v)
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days for mobile

    # ── MongoDB ────────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "kisaan_mitra"

    # ── Firebase ───────────────────────────────────────────────────────────
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    FIREBASE_CREDENTIALS_JSON: str = ""

    # ── Fast2SMS ───────────────────────────────────────────────────────────
    FAST2SMS_API_KEY: str = ""
    FAST2SMS_SENDER_ID: str = "KISAAN"
    FAST2SMS_BASE_URL: str = "https://www.fast2sms.com/dev/bulkV2"

    # ── AgMarket (data.gov.in) ─────────────────────────────────────────────
    AGMARKET_API_KEY: str = ""
    AGMARKET_BASE_URL: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    AGMARKET_LIMIT: int = 500

    # ── OpenWeatherMap ─────────────────────────────────────────────────────
    OPENWEATHER_API_KEY: str = ""

    # ── Groq AI (Free — crop recommendations) ─────────────────────────────
    GROQ_API_KEY: str = ""

    # ── Gmail SMTP (Email OTP Verification) ────────────────────────────────
    SMTP_EMAIL: str = "subhamkhandual215@gmail.com"
    SMTP_PASSWORD: str = "giev hnng irtn fzyl"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_FROM_NAME: str = "Kisaan Mitra 🌾"

    # ── Alert Thresholds ──────────────────────────────────────────────────
    BIG_JUMP_THRESHOLD: float = 0.10
    CRITICAL_THRESHOLD: float = 0.15
    INACTIVE_DAYS_THRESHOLD: int = 3

    # ── Scheduler ─────────────────────────────────────────────────────────
    PRICE_FETCH_INTERVAL_MINUTES: int = 30
    WEATHER_FETCH_INTERVAL_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
