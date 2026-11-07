"""
Admin authentication module for Kissan Mitra Admin Dashboard
"""
import streamlit as st
import bcrypt
import hashlib
import time
from datetime import datetime, timedelta
import json
import os

# Admin credentials (in production, these should be stored in environment variables or a secure database)
ADMIN_CREDENTIALS = {
    "admin@kisanmitra.com": {
        "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "name": "System Administrator",
        "role": "admin"
    }
}

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def init_admin_session_state():
    """Initialize admin session state variables"""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'admin_user' not in st.session_state:
        st.session_state.admin_user = None
    if 'admin_login_time' not in st.session_state:
        st.session_state.admin_login_time = None
    if 'admin_session_timeout' not in st.session_state:
        st.session_state.admin_session_timeout = 30  # minutes

def admin_login_form():
    """Display admin login form"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🔐 Admin Login</h2>
        <p>Please enter your admin credentials to access the dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("admin_login_form"):
        email = st.text_input("Email Address", placeholder="admin@kisanmitra.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if email and password:
                authenticate_admin(email, password)
            else:
                st.error("Please enter both email and password")

def authenticate_admin(email: str, password: str):
    """Authenticate admin user"""
    if email in ADMIN_CREDENTIALS:
        stored_hash = ADMIN_CREDENTIALS[email]["password_hash"]
        if verify_password(password, stored_hash):
            # Successful login
            st.session_state.admin_authenticated = True
            st.session_state.admin_user = {
                "email": email,
                "name": ADMIN_CREDENTIALS[email]["name"],
                "role": ADMIN_CREDENTIALS[email]["role"]
            }
            st.session_state.admin_login_time = time.time()
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Invalid email or password")
    else:
        st.error("Invalid email or password")

def admin_logout():
    """Logout admin user"""
    st.session_state.admin_authenticated = False
    st.session_state.admin_user = None
    st.session_state.admin_login_time = None
    st.rerun()

def check_admin_auth():
    """Check if admin is authenticated and session is valid"""
    init_admin_session_state()
    
    if not st.session_state.admin_authenticated:
        return False
    
    # Check session timeout
    if st.session_state.admin_login_time:
        elapsed_time = (time.time() - st.session_state.admin_login_time) / 60  # minutes
        if elapsed_time > st.session_state.admin_session_timeout:
            admin_logout()
            st.warning("Session expired. Please login again.")
            return False
    
    return True

def show_admin_logout_button():
    """Show admin logout button in sidebar"""
    if st.session_state.admin_authenticated and st.session_state.admin_user:
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**Logged in as:** {st.session_state.admin_user['name']}")
            if st.button("Logout", use_container_width=True):
                admin_logout()