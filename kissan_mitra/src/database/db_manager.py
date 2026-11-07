"""
Database manager for Kissan Mitra Admin Dashboard
Handles storage and retrieval of farmer data, activities, and predictions
"""
import sqlite3
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "kissan_mitra/data/farmers.db"):
        """Initialize database manager with SQLite database"""
        self.db_path = db_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Farmers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                state TEXT,
                district TEXT,
                village TEXT,
                language TEXT DEFAULT 'en',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Farmer activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmer_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER,
                activity_type TEXT NOT NULL,  -- login, crop_prediction, fertilizer_prediction, weather_search, ai_chat, report_download
                activity_data TEXT,  -- JSON string of activity details
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_id) REFERENCES farmers (id)
            )
        ''')
        
        # Admin users table (for admin authentication)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Insert default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM admin_users WHERE email = ?", ("admin@kisanmitra.com",))
        if cursor.fetchone()[0] == 0:
            # Hash password: admin123
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO admin_users (email, password_hash, name, role)
                VALUES (?, ?, ?, ?)
            ''', ("admin@kisanmitra.com", password_hash, "System Administrator", "admin"))
        
        conn.commit()
        conn.close()
    
    # Farmer management methods
    def add_farmer(self, farmer_data: Dict[str, Any]) -> int:
        """Add a new farmer to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO farmers (name, email, phone, state, district, village, language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            farmer_data.get('name'),
            farmer_data.get('email'),
            farmer_data.get('phone'),
            farmer_data.get('state'),
            farmer_data.get('district'),
            farmer_data.get('village', ''),
            farmer_data.get('language', 'en')
        ))
        
        farmer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return farmer_id
    
    def get_farmer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get farmer by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM farmers WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_farmer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get farmer by phone"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM farmers WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_farmers(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all farmers with pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM farmers 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_farmers(self, search_term: str = "", state: str = "", district: str = "") -> List[Dict[str, Any]]:
        """Search farmers by name, email, phone, state, or district"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM farmers WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if state:
            query += " AND state = ?"
            params.append(state)
        
        if district:
            query += " AND district = ?"
            params.append(district)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_farmer_activity(self, farmer_id: int):
        """Update farmer's last active timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE farmers 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (farmer_id,))
        
        conn.commit()
        conn.close()
    
    def delete_farmer(self, farmer_id: int) -> bool:
        """Delete a farmer (soft delete by setting is_active to 0)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE farmers 
            SET is_active = 0 
            WHERE id = ?
        ''', (farmer_id,))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    # Activity logging methods
    def log_activity(self, farmer_id: int, activity_type: str, activity_data: Dict[str, Any] = None, 
                    ip_address: str = "", user_agent: str = "") -> int:
        """Log farmer activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        activity_json = json.dumps(activity_data) if activity_data else None
        
        cursor.execute('''
            INSERT INTO farmer_activities (farmer_id, activity_type, activity_data, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (farmer_id, activity_type, activity_json, ip_address, user_agent))
        
        activity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Update farmer's last active timestamp
        self.update_farmer_activity(farmer_id)
        
        return activity_id
    
    def get_farmer_activities(self, farmer_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get activities for a specific farmer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM farmer_activities 
            WHERE farmer_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (farmer_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in rows:
            activity = dict(row)
            if activity['activity_data']:
                activity['activity_data'] = json.loads(activity['activity_data'])
            activities.append(activity)
        
        return activities
    
    def get_recent_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent activities across all farmers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fa.*, f.name as farmer_name, f.email as farmer_email
            FROM farmer_activities fa
            JOIN farmers f ON fa.farmer_id = f.id
            ORDER BY fa.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in rows:
            activity = dict(row)
            if activity['activity_data']:
                activity['activity_data'] = json.loads(activity['activity_data'])
            activities.append(activity)
        
        return activities
    
    # Analytics methods
    def get_farmer_count(self) -> int:
        """Get total number of farmers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM farmers WHERE is_active = 1")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_active_users_count(self, hours: int = 24) -> int:
        """Get number of active users in last X hours"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM farmers 
            WHERE is_active = 1 
            AND last_active >= datetime('now', '-{} hours')
        '''.format(hours))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_activity_counts(self) -> Dict[str, int]:
        """Get counts of different activity types"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT activity_type, COUNT(*) as count 
            FROM farmer_activities 
            GROUP BY activity_type
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return {row['activity_type']: row['count'] for row in rows}
    
    def get_activities_by_type(self, activity_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get activities by type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fa.*, f.name as farmer_name, f.email as farmer_email
            FROM farmer_activities fa
            JOIN farmers f ON fa.farmer_id = f.id
            WHERE fa.activity_type = ?
            ORDER BY fa.created_at DESC
            LIMIT ?
        ''', (activity_type, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in rows:
            activity = dict(row)
            if activity['activity_data']:
                activity['activity_data'] = json.loads(activity['activity_data'])
            activities.append(activity)
        
        return activities
    
    def get_daily_registrations(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily farmer registrations for the last X days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM farmers 
            WHERE is_active = 1 
            AND created_at >= date('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date
        '''.format(days))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'date': row['date'], 'count': row['count']} for row in rows]
    
    def get_state_wise_distribution(self) -> List[Dict[str, Any]]:
        """Get farmer distribution by state"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT state, COUNT(*) as count
            FROM farmers 
            WHERE is_active = 1 AND state IS NOT NULL AND state != ''
            GROUP BY state
            ORDER BY count DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'state': row['state'], 'count': row['count']} for row in rows]
    
    # Admin authentication methods
    def authenticate_admin(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate admin user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT * FROM admin_users 
            WHERE email = ? AND password_hash = ? AND is_active = 1
        ''', (email, password_hash))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            admin = dict(row)
            # Update last login
            self.update_admin_last_login(admin['id'])
            return admin
        return None
    
    def update_admin_last_login(self, admin_id: int):
        """Update admin's last login timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE admin_users 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (admin_id,))
        
        conn.commit()
        conn.close()
    
    def get_admin_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get admin by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM admin_users WHERE email = ? AND is_active = 1", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

# Global database instance
db_manager = DatabaseManager()