"""
Activity logger for Kissan Mitra Admin Dashboard
Automatically logs farmer activities across the platform
"""
import streamlit as st
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import os
import sys

# Add the src directory to path so we can import db_manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from kissan_mitra.src.database.db_manager import db_manager

def get_client_info() -> Dict[str, str]:
    """Get client IP address and user agent (simplified for Streamlit)"""
    # In a real deployment, you'd get this from request headers
    # For now, we'll use placeholder values
    return {
        "ip_address": "127.0.0.1",  # Placeholder
        "user_agent": "Streamlit App"  # Placeholder
    }

def get_current_farmer_id() -> Optional[int]:
    """Get current farmer ID from session state"""
    # This would be implemented based on how farmer authentication works
    # For now, we'll check if we have farmer info in session
    if hasattr(st.session_state, 'farmer_info') and st.session_state.farmer_info:
        farmer_info = st.session_state.farmer_info
        # Try to find farmer by email or phone
        if 'email' in farmer_info:
            farmer = db_manager.get_farmer_by_email(farmer_info['email'])
            if farmer:
                return farmer['id']
        elif 'phone' in farmer_info:
            farmer = db_manager.get_farmer_by_phone(farmer_info['phone'])
            if farmer:
                return farmer['id']
    return None

def log_farmer_activity(activity_type: str, activity_data: Dict[str, Any] = None):
    """Log a farmer activity"""
    try:
        farmer_id = get_current_farmer_id()
        if not farmer_id:
            # If we can't identify the farmer, we still log the activity but without farmer_id
            # In a real system, you might want to handle this differently
            return None
        
        client_info = get_client_info()
        
        activity_id = db_manager.log_activity(
            farmer_id=farmer_id,
            activity_type=activity_type,
            activity_data=activity_data,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"]
        )
        
        return activity_id
    except Exception as e:
        # In production, you'd want to log this error
        print(f"Error logging activity: {e}")
        return None

# Specific activity logging functions for different platform features
def log_farmer_login(farmer_data: Dict[str, Any]):
    """Log farmer login"""
    activity_data = {
        "login_method": "email_password",  # or social, otp, etc.
        "timestamp": datetime.now().isoformat(),
        "farmer_info": {
            "name": farmer_data.get("name"),
            "email": farmer_data.get("email"),
            "phone": farmer_data.get("phone")
        }
    }
    return log_farmer_activity("login", activity_data)

def log_crop_prediction(input_data: Dict[str, Any], prediction_result: Dict[str, Any]):
    """Log crop prediction usage"""
    activity_data = {
        "input_parameters": input_data,
        "prediction_result": {
            "recommended_crop": prediction_result.get("crop"),
            "confidence": prediction_result.get("confidence"),
            "all_probabilities": prediction_result.get("all_probabilities", {})
        },
        "timestamp": datetime.now().isoformat()
    }
    return log_farmer_activity("crop_prediction", activity_data)

def log_fertilizer_prediction(input_data: Dict[str, Any], prediction_result: Dict[str, Any]):
    """Log fertilizer prediction usage"""
    activity_data = {
        "input_parameters": input_data,
        "prediction_result": {
            "recommended_fertilizer": prediction_result.get("fertilizer"),
            "confidence": prediction_result.get("confidence"),
            "npk_ratio": prediction_result.get("npk"),
            "description": prediction_result.get("description")
        },
        "timestamp": datetime.now().isoformat()
    }
    return log_farmer_activity("fertilizer_prediction", activity_data)

def log_weather_search(location_data: Dict[str, Any], weather_result: Dict[str, Any]):
    """Log weather search"""
    activity_data = {
        "location_query": location_data,
        "weather_result": {
            "temperature": weather_result.get("temp"),
            "humidity": weather_result.get("humidity"),
            "rainfall": weather_result.get("rainfall"),
            "description": weather_result.get("description"),
            "city": weather_result.get("city")
        },
        "timestamp": datetime.now().isoformat()
    }
    return log_farmer_activity("weather_search", activity_data)

def log_ai_chat(message: str, response: str, chat_context: Dict[str, Any] = None):
    """Log AI chatbot usage"""
    activity_data = {
        "user_message": message,
        "ai_response": response,
        "chat_context": chat_context or {},
        "timestamp": datetime.now().isoformat(),
        "message_length": len(message),
        "response_length": len(response)
    }
    return log_farmer_activity("ai_chat", activity_data)

def log_report_download(report_type: str, report_data: Dict[str, Any] = None):
    """Log report download"""
    activity_data = {
        "report_type": report_type,  # crop_advisory, fertilizer_recommendation, weather_report, etc.
        "report_data": report_data or {},
        "timestamp": datetime.now().isoformat()
    }
    return log_farmer_activity("report_download", activity_data)

def log_farmer_registration(farmer_data: Dict[str, Any]):
    """Log new farmer registration"""
    activity_data = {
        "registration_data": {
            "name": farmer_data.get("name"),
            "email": farmer_data.get("email"),
            "phone": farmer_data.get("phone"),
            "state": farmer_data.get("state"),
            "district": farmer_data.get("district"),
            "village": farmer_data.get("village", ""),
            "language": farmer_data.get("language", "en")
        },
        "timestamp": datetime.now().isoformat()
    }
    return log_farmer_activity("registration", activity_data)

# Decorator for automatic activity logging
def log_activity_decorator(activity_type: str):
    """Decorator to automatically log activities"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Execute the original function
            result = func(*args, **kwargs)
            
            # Try to log the activity (don't let logging errors break the function)
            try:
                # This is a simplified approach - in practice you'd want to extract
                # relevant data from the function arguments and result
                log_farmer_activity(activity_type)
            except Exception as e:
                # Silently fail - logging shouldn't break core functionality
                pass
            
            return result
        return wrapper
    return decorator