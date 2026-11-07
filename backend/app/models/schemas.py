"""
Pydantic models for MongoDB documents.
These serve as both API schemas and database document shapes.
"""

import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

# ── Shared validation constants ───────────────────────────────────────────────
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
NAME_REGEX = re.compile(r"^[a-zA-Z\s]{3,50}$")
PASSWORD_UPPER = re.compile(r"[A-Z]")
PASSWORD_LOWER = re.compile(r"[a-z]")
PASSWORD_DIGIT = re.compile(r"[0-9]")
PASSWORD_SPECIAL = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':"+'"'+r"\|,.<>/?`~]")


def _validate_strong_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(v) > 64:
        raise ValueError("Password cannot exceed 64 characters")
    if not PASSWORD_UPPER.search(v):
        raise ValueError("Password must contain at least 1 uppercase letter (A-Z)")
    if not PASSWORD_LOWER.search(v):
        raise ValueError("Password must contain at least 1 lowercase letter (a-z)")
    if not PASSWORD_DIGIT.search(v):
        raise ValueError("Password must contain at least 1 number (0-9)")
    if not PASSWORD_SPECIAL.search(v):
        raise ValueError("Password must contain at least 1 special character (e.g. @, #, $, !)")
    return v


def _validate_clean_name(v: str) -> str:
    cleaned = " ".join(v.strip().split())
    if len(cleaned) < 3:
        raise ValueError("Name must be at least 3 characters long")
    if len(cleaned) > 50:
        raise ValueError("Name cannot exceed 50 characters")
    if not re.match(r"^[a-zA-Z\s]+$", cleaned):
        raise ValueError("Name can only contain alphabetic letters and spaces (no numbers or special characters)")
    return cleaned


# ── Helpers ────────────────────────────────────────────────────────────────────

class PyObjectId(str):
    """Custom type to serialize MongoDB ObjectId as string."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


# ── Enums ──────────────────────────────────────────────────────────────────────

class AlertType(str, Enum):
    NORMAL = "normal"           # Routine Firebase push
    BIG_JUMP = "big_jump"       # Firebase + SMS
    INACTIVE = "inactive"       # SMS only
    CRITICAL = "critical"       # SMS high priority

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class Language(str, Enum):
    ENGLISH = "en"
    KANNADA = "kn"
    HINDI = "hi"
    ODIA = "or"

class ActivityType(str, Enum):
    DISEASE_SCAN = "disease_scan"
    YIELD_PREDICTION = "yield_prediction"
    FERTILIZER_RECOMMENDATION = "fertilizer_recommendation"
    WEATHER_SEARCH = "weather_search"
    CROP_RECOMMENDATION = "crop_recommendation"



# ── User ───────────────────────────────────────────────────────────────────────

class CropPreference(BaseModel):
    commodity: str          # e.g. "Tomato"
    state: str              # e.g. "Karnataka"
    district: str           # e.g. "Bengaluru"
    market: str             # e.g. "Bengaluru"
    alert_enabled: bool = True


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$", description="10-digit Indian mobile number")
    email: Optional[str] = None
    location_state: str
    location_district: str
    village: Optional[str] = None
    language: Language = Language.ENGLISH
    crops: List[CropPreference] = []

    @field_validator("email")
    @classmethod
    def validate_gmail(cls, v):
        if v is not None and v != "" and not GMAIL_REGEX.match(v):
            raise ValueError("Email must be a valid @gmail.com address")
        return v


class UserLogin(BaseModel):
    email: str
    password: str = Field(..., min_length=4)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Please enter a valid email address (e.g. name@gmail.com)")
        return v


class SendEmailOTPRequest(BaseModel):
    email: str
    purpose: str = "Registration"  # "Registration" or "Password Reset"

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Please provide a valid email address (e.g. name@gmail.com)")
        return v


class RegisterWithEmailRequest(BaseModel):
    name: str
    email: str
    password: str
    otp: str = Field(..., min_length=6, max_length=6)
    location_state: str
    location_district: str
    village: Optional[str] = None
    language: Language = Language.ENGLISH
    crops: List[CropPreference] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _validate_clean_name(v)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Please provide a valid email address")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return _validate_strong_password(v)


class EmailForgotPassword(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Please enter a valid email address")
        return v


class EmailVerifyOTP(BaseModel):
    email: str
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        return _validate_strong_password(v)


class UserRegister(UserCreate):
    password: str = Field(..., min_length=8, description="Plain text password (hashed before storage)")

    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        return _validate_strong_password(v)


class UserInDB(BaseModel):
    """Shape of user document stored in MongoDB."""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = None
    hashed_password: str
    location_state: str
    location_district: str
    village: Optional[str] = None
    language: Language = Language.ENGLISH
    crops: List[CropPreference] = []
    fcm_token: Optional[str] = None     # Firebase device token
    is_active: bool = True
    last_active: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class UserResponse(BaseModel):
    """Safe user response (no password)."""
    id: str
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = None
    location_state: str
    location_district: str
    village: Optional[str] = None
    language: Language
    crops: List[CropPreference]
    last_active: datetime
    created_at: datetime


class UpdatePreferences(BaseModel):
    crops: Optional[List[CropPreference]] = None
    language: Optional[Language] = None
    fcm_token: Optional[str] = None
    location_state: Optional[str] = None
    location_district: Optional[str] = None
    village: Optional[str] = None
    email: Optional[str] = None


class ForgotPassword(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")


class VerifyOTP(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    otp: str = Field(..., min_length=4, max_length=6)
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, v):
        return _validate_strong_password(v)


# ── Price ──────────────────────────────────────────────────────────────────────

class PriceRecord(BaseModel):
    """Shape of price document stored in MongoDB (from AgMarket API)."""
    id: Optional[str] = Field(default=None, alias="_id")
    state: str
    district: str
    market: str
    commodity: str
    variety: str = ""
    arrival_date: str               # e.g. "01/07/2025"
    min_price: float
    max_price: float
    modal_price: float              # Most common traded price — primary metric
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class PriceResponse(BaseModel):
    commodity: str
    market: str
    district: str
    state: str
    modal_price: float
    min_price: float
    max_price: float
    arrival_date: str
    change_pct: Optional[float] = None  # % change vs previous record
    trend: Optional[str] = None         # "up" | "down" | "stable"


# ── Notification ───────────────────────────────────────────────────────────────

class NotificationRecord(BaseModel):
    """Stored in MongoDB for notification history."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    alert_type: AlertType
    commodity: str
    market: str
    old_price: float
    new_price: float
    change_pct: float
    message_en: str                 # English message
    message_kn: str = ""            # Kannada message
    firebase_sent: bool = False
    sms_sent: bool = False
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class NotificationResponse(BaseModel):
    id: str
    alert_type: AlertType
    commodity: str
    market: str
    old_price: float
    new_price: float
    change_pct: float
    message_en: str
    firebase_sent: bool
    sms_sent: bool
    status: NotificationStatus
    created_at: datetime


# ── Auth Token ─────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[str] = None
    phone: Optional[str] = None

class FirebaseLoginRequest(BaseModel):
    id_token: str
    name: Optional[str] = None
    email: Optional[str] = None
    location_state: Optional[str] = None
    location_district: Optional[str] = None
    village: Optional[str] = None
    language: Optional[Language] = Language.ENGLISH

# ── Activity History ───────────────────────────────────────────────────────────

class ActivityRecord(BaseModel):
    """Stored in MongoDB for tracking farmer history."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    activity_type: ActivityType
    title: str
    description: str
    data: dict = {}  # Store JSON data of the prediction/result
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class ActivityResponse(BaseModel):
    id: str
    activity_type: ActivityType
    title: str
    description: str
    data: dict
    created_at: datetime
