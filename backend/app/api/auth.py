"""
Authentication routes: register, login, token refresh.
"""
import random
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt as _bcrypt
from bson import ObjectId

import httpx
import time

from app.models.schemas import (
    UserRegister, UserLogin, Token, UserResponse, UserInDB, 
    ForgotPassword, VerifyOTP, SendEmailOTPRequest, RegisterWithEmailRequest,
    EmailForgotPassword, EmailVerifyOTP
)
from app.utils.database import get_db
from app.config import settings
from app.services.sms_service import sms_service
from app.services.email_service import email_service

router = APIRouter()


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: str, db=None):
    """Decode JWT and return user document. Used as a dependency."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if db is None:
        db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return user


# Create OTP collection indexes on startup
async def _create_otp_indexes():
    """Create OTP collection indexes."""
    db = get_db()
    await db.otps.create_index([("phone", 1)])
    await db.otps.create_index([("expires_at", 1)], expireAfterSeconds=0)


# ── POST /register ─────────────────────────────────────────────────────────────
@router.post("/register", response_model=Token, status_code=201)
async def register(user_data: UserRegister, db=Depends(get_db)):
    """
    Register a new farmer.
    Stores hashed password and returns a JWT token immediately.
    """
    # Check if phone already registered
    existing = await db.users.find_one({"phone": user_data.phone})
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered. Please login.",
        )

    # Build user document
    user_doc = {
        "name": user_data.name,
        "phone": user_data.phone,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "location_state": user_data.location_state,
        "location_district": user_data.location_district,
        "village": user_data.village,
        "language": user_data.language.value,
        "crops": [c.model_dump() for c in user_data.crops],
        "fcm_token": None,
        "is_active": True,
        "last_active": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    token = create_access_token({"sub": str(result.inserted_id), "phone": user_data.phone})

    return Token(
        access_token=token,
        user=_format_user(user_doc),
    )


# ── POST /auth/send-email-otp ──────────────────────────────────────────────────
@router.post("/auth/send-email-otp")
async def send_email_otp(data: SendEmailOTPRequest, db=Depends(get_db)):
    """
    Generate and send 6-digit OTP to user's email via Gmail SMTP.
    Valid for 10 minutes.
    """
    email = data.email.strip().lower()
    purpose = data.purpose

    if purpose.lower() in ("registration", "register"):
        existing = await db.users.find_one({"email": email})
        if existing:
            raise HTTPException(
                status_code=400,
                detail="This email is already registered. Please login or reset password.",
            )
    elif purpose.lower() in ("password reset", "forgot_password"):
        existing = await db.users.find_one({"email": email})
        if not existing:
            raise HTTPException(
                status_code=404,
                detail="No registered farmer found with this email.",
            )

    otp = str(random.randint(100000, 999999))
    otp_doc = {
        "email": email,
        "otp": otp,
        "purpose": purpose,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
    }

    await db.email_otps.update_one(
        {"email": email},
        {"$set": otp_doc},
        upsert=True
    )

    try:
        await email_service.send_otp_email(to_email=email, otp=otp, purpose=purpose)
    except Exception as e:
        print(f"[!] Email sending failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not send OTP email. Please verify SMTP settings or try again."
        )

    return {
        "success": True,
        "message": f"Verification code sent to {email}"
    }


# ── POST /auth/register-with-email ─────────────────────────────────────────────
@router.post("/auth/register-with-email", response_model=Token, status_code=201)
async def register_with_email(user_data: RegisterWithEmailRequest, db=Depends(get_db)):
    """
    Verify Email OTP and register a new farmer.
    Returns JWT access token directly upon successful verification.
    """
    email = user_data.email.strip().lower()

    # 1. Verify OTP
    otp_record = await db.email_otps.find_one({"email": email})
    if not otp_record:
        raise HTTPException(
            status_code=400, 
            detail="Verification code not found. Please click 'Send OTP' first."
        )

    if otp_record["expires_at"] < datetime.utcnow():
        await db.email_otps.delete_one({"email": email})
        raise HTTPException(
            status_code=400, 
            detail="Verification code has expired. Please request a new one."
        )

    if user_data.otp.strip() != otp_record["otp"].strip():
        raise HTTPException(
            status_code=400, 
            detail="Invalid verification code. Please check your inbox and try again."
        )

    # 2. Check if already registered
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered. Please login.",
        )

    # 3. Create farmer user document
    user_doc = {
        "name": user_data.name.strip(),
        "email": email,
        "phone": "",
        "hashed_password": hash_password(user_data.password),
        "location_state": user_data.location_state,
        "location_district": user_data.location_district,
        "village": user_data.village or "",
        "language": user_data.language.value if hasattr(user_data.language, 'value') else str(user_data.language),
        "crops": [c.model_dump() for c in user_data.crops],
        "fcm_token": None,
        "is_active": True,
        "last_active": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Clean up consumed OTP
    await db.email_otps.delete_one({"email": email})

    token = create_access_token({"sub": str(result.inserted_id), "email": email})

    return Token(
        access_token=token,
        user=_format_user(user_doc),
    )


# ── POST /login ────────────────────────────────────────────────────────────────
@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db=Depends(get_db)):
    """
    Login with Email + Password only.
    Returns JWT access token valid for 30 days.
    """
    email = credentials.email.strip().lower()
    user = await db.users.find_one({"email": email})

    if not user or not verify_password(credentials.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password",
        )

    # Update last_active timestamp
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_active": datetime.utcnow()}},
    )

    token = create_access_token({
        "sub": str(user["_id"]), 
        "email": user.get("email", ""),
    })

    return Token(
        access_token=token,
        user=_format_user(user),
    )


# ── POST /auth/email/forgot-password ───────────────────────────────────────────
@router.post("/auth/email/forgot-password")
async def email_forgot_password(data: EmailForgotPassword, db=Depends(get_db)):
    """Send password reset OTP to user's registered email."""
    email = data.email.strip().lower()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="No user found with this email.")

    otp = str(random.randint(100000, 999999))
    otp_doc = {
        "email": email,
        "otp": otp,
        "purpose": "Password Reset",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
    }

    await db.email_otps.update_one(
        {"email": email},
        {"$set": otp_doc},
        upsert=True
    )

    try:
        await email_service.send_otp_email(to_email=email, otp=otp, purpose="Password Reset")
    except Exception as e:
        print(f"[!] Email send error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send password reset email.")

    return {"message": "Password reset code sent to your email."}


# ── POST /auth/email/verify-otp ────────────────────────────────────────────────
@router.post("/auth/email/verify-otp")
async def email_verify_otp(data: EmailVerifyOTP, db=Depends(get_db)):
    """Verify email OTP and set new password."""
    email = data.email.strip().lower()

    otp_record = await db.email_otps.find_one({"email": email})
    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP not found or expired.")

    if otp_record["expires_at"] < datetime.utcnow():
        await db.email_otps.delete_one({"email": email})
        raise HTTPException(status_code=400, detail="OTP has expired.")

    if data.otp.strip() != otp_record["otp"].strip():
        raise HTTPException(status_code=400, detail="Invalid OTP code.")

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    new_hashed = hash_password(data.new_password)
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": new_hashed}}
    )

    await db.email_otps.delete_one({"email": email})

    return {"message": "Password reset successfully. You can now login with your new password."}


# ── POST /forgot-password ──────────────────────────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db=Depends(get_db)):
    """
    Send OTP via SMS for forgot password.
    """
    user = await db.users.find_one({"phone": data.phone})
    if not user:
        # Don't reveal if user exists or not for security
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP in database with expiration (5 minutes)
    otp_doc = {
        "phone": data.phone,
        "otp": otp,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }
    
    # Store in database
    await db.otps.update_one(
        {"phone": data.phone},
        {"$set": otp_doc},
        upsert=True
    )
    
    # Send OTP via SMS
    try:
        message = f"Your Kisaan Mitra OTP for password reset is: {otp}. Valid for 5 minutes."
        await sms_service.send_sms(
            phone=data.phone,
            message=message
        )
    except Exception as e:
        # Log the error but don't expose details to user
        print(f"Failed to send SMS: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP. Please try again later."
        )
    
    return {"message": "OTP sent successfully to your mobile number"}


# ── POST /verify-otp ───────────────────────────────────────────────────────────
@router.post("/verify-otp")
async def verify_otp(data: VerifyOTP, db=Depends(get_db)):
    """
    Verify OTP and reset password.
    """
    # Find OTP record
    otp_record = await db.otps.find_one({"phone": data.phone})
    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP not found or expired")
    
    # Check if OTP is expired
    if otp_record["expires_at"] < datetime.utcnow():
        await db.otps.delete_one({"phone": data.phone})
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # Verify OTP
    if data.otp != otp_record["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Find user
    user = await db.users.find_one({"phone": data.phone})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    new_hashed = hash_password(data.new_password)
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": new_hashed}}
    )
    
    # Delete used OTP
    await db.otps.delete_one({"phone": data.phone})
    
    return {"message": "Password reset successfully"}


# ── Helpers ────────────────────────────────────────────────────────────────────
def _format_user(user_doc: dict) -> UserResponse:
    return UserResponse(
        id=str(user_doc["_id"]),
        name=user_doc["name"],
        phone=user_doc["phone"],
        email=user_doc.get("email"),
        location_state=user_doc.get("location_state"),
        location_district=user_doc.get("location_district"),
        village=user_doc.get("village"),
        language=user_doc.get("language", "en"),
        crops=user_doc.get("crops", []),
        last_active=user_doc.get("last_active", datetime.utcnow()),
        created_at=user_doc.get("created_at", datetime.utcnow()),
    )