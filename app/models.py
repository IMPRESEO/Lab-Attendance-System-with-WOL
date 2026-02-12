"""
Database models and operations
"""
import sqlite3
import os
from datetime import datetime
from .config import Config


def get_db_connection():
    """Create database connection with row factory"""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(Config.DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table with enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                reg_no TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                batch_year TEXT,
                finger_id INTEGER UNIQUE,
                mac_address TEXT,
                password TEXT NOT NULL,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create attendance table with enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                reg_no TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'Present',
                department TEXT,
                batch_year TEXT,
                session_type TEXT DEFAULT 'Regular',
                lab_name TEXT
            )
        ''')
        
        # Create departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                hod_name TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    # Apply migrations if database exists
    conn = get_db_connection()
    cursor = conn.cursor()
    # Migrate existing users table if photo_path is missing
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN photo_path TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.close()


# ============================================
# DEPARTMENT OPERATIONS
# ============================================

def get_all_departments():
    """Get all departments"""
    conn = get_db_connection()
    departments = conn.execute('SELECT * FROM departments ORDER BY name').fetchall()
    conn.close()
    return departments

def get_department_stats(department_name):
    """Get statistics for a specific department"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student count
    cursor.execute('''
        SELECT COUNT(*) as student_count
        FROM users 
        WHERE department = ? AND role = 'student'
    ''', (department_name,))
    student_count = cursor.fetchone()['student_count']
    
    # Get today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COUNT(*) as attendance_count
        FROM attendance 
        WHERE department = ? AND DATE(timestamp) = ?
    ''', (department_name, today))
    attendance_count = cursor.fetchone()['attendance_count']
    
    conn.close()
    return {
        'student_count': student_count,
        'attendance_count': attendance_count,
        'attendance_percentage': (attendance_count / student_count * 100) if student_count > 0 else 0
    }

# ============================================
# BATCH OPERATIONS
# ============================================

def get_batch_stats():
    """Get statistics by batch year"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT batch_year, COUNT(*) as student_count
        FROM users 
        WHERE role = 'student' AND batch_year IS NOT NULL
        GROUP BY batch_year
        ORDER BY batch_year DESC
    ''')
    batch_stats = cursor.fetchall()
    
    # Get attendance for each batch
    today = datetime.now().strftime('%Y-%m-%d')
    for batch in batch_stats:
        cursor.execute('''
            SELECT COUNT(*) as attendance_count
            FROM attendance 
            WHERE batch_year = ? AND DATE(timestamp) = ?
        ''', (batch['batch_year'], today))
        batch['attendance_count'] = cursor.fetchone()['attendance_count']
        batch['attendance_percentage'] = (batch['attendance_count'] / batch['student_count'] * 100) if batch['student_count'] > 0 else 0
    
    conn.close()
    return [dict(row) for row in batch_stats]

# ============================================
# ENHANCED USER OPERATIONS
# ============================================

def add_user(name, reg_no, role, password=None, department=None, batch_year=None, finger_id=None, photo_path=None):
    """
    Unified function to add a new user to the system.
    Handles basic, enhanced, and photo-enabled registration flows.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if reg_no already exists
        existing_user = cursor.execute('SELECT id FROM users WHERE reg_no = ?', (reg_no,)).fetchone()
        if existing_user:
            return {'error': 'Duplicate Register Number'}

        # If no finger_id is provided, get the next one
        if finger_id is None:
            finger_id = get_next_finger_id()
        else:
            # Check if finger_id already exists if provided
            existing_finger = cursor.execute('SELECT id FROM users WHERE finger_id = ?', (finger_id,)).fetchone()
            if existing_finger:
                return {'error': 'Duplicate Finger ID'}
            
        cursor.execute('''
            INSERT INTO users (name, reg_no, role, department, batch_year, finger_id, password, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, reg_no, role, department, batch_year, finger_id, password or '', photo_path))
        
        user_id = cursor.lastrowid
        conn.commit()
        return {'success': True, 'user_id': user_id}
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if 'reg_no' in error_msg:
            return {'error': 'Duplicate Register Number'}
        elif 'finger_id' in error_msg:
            return {'error': 'Duplicate Finger ID'}
        return {'error': f"Database integrity error: {error_msg}"}
    except Exception as e:
        return {'error': f"Error adding user: {str(e)}"}
    finally:
        conn.close()



def add_user_enhanced(name, reg_no, role, department, batch_year, password=None, photo_path=None, finger_id=None):
    """Wrapper for backward compatibility or explicit enhanced calls"""
    return add_user(name, reg_no, role, password, department, batch_year, finger_id=finger_id, photo_path=photo_path)



def get_users_by_department(department):
    """Get all users in a specific department"""
    conn = get_db_connection()
    users = conn.execute('''
        SELECT * FROM users 
        WHERE department = ? 
        ORDER BY role, name
    ''', (department,)).fetchall()
    conn.close()
    return users


def get_users_by_batch(batch_year):
    """Get all users in a specific batch"""
    conn = get_db_connection()
    users = conn.execute('''
        SELECT * FROM users 
        WHERE batch_year = ? 
        ORDER BY name
    ''', (batch_year,)).fetchall()
    conn.close()
    return users


def get_all_users():
    """Get all users ordered by ID"""
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY id').fetchall()
    conn.close()
    return users


def get_user_by_credentials(username, password):
    """Get user by username and password"""
    conn = get_db_connection()
    user = conn.execute('''
        SELECT * FROM users 
        WHERE name = ? AND password = ?
    ''', (username, password)).fetchone()
    conn.close()
    return user


def get_user_by_finger_id(finger_id):
    """Get user by fingerprint ID"""
    conn = get_db_connection()
    user = conn.execute('''
        SELECT * FROM users 
        WHERE finger_id = ?
    ''', (finger_id,)).fetchone()
    conn.close()
    return user


def get_next_finger_id():
    """Get next available finger ID"""
    conn = get_db_connection()
    max_finger = conn.execute('SELECT MAX(finger_id) as max_id FROM users').fetchone()
    conn.close()
    return (max_finger['max_id'] or 0) + 1


def get_total_users():
    """Get total user count"""
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    conn.close()
    return count


def delete_user(user_id):
    """Delete user by ID"""
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


def update_user_mac(user_id, mac_address):
    """Update MAC address for a user"""
    conn = get_db_connection()
    conn.execute('''
        UPDATE users 
        SET mac_address = ? 
        WHERE id = ?
    ''', (mac_address, user_id))
    conn.commit()
    conn.close()


def clear_user_fingerprint(user_id):
    """Clear fingerprint ID for a user"""
    conn = get_db_connection()
    conn.execute('UPDATE users SET finger_id = NULL WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


# ============================================
# ATTENDANCE OPERATIONS
# ============================================

def get_all_attendance():
    """Get all attendance logs"""
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT * FROM attendance 
        ORDER BY timestamp DESC
    ''').fetchall()
    conn.close()
    return logs


def get_recent_attendance(limit=10):
    """Get recent attendance logs"""
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT * FROM attendance 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return logs


def get_today_attendance_count():
    """Get count of today's attendance"""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    count = conn.execute('''
        SELECT COUNT(*) as count FROM attendance 
        WHERE DATE(timestamp) = ?
    ''', (today,)).fetchone()['count']
    conn.close()
    return count


def log_attendance(name, reg_no):
    """Log attendance entry"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO attendance (name, reg_no, timestamp, status)
        VALUES (?, ?, ?, 'Present')
    ''', (name, reg_no, timestamp))
    conn.commit()
    conn.close()


def delete_attendance(log_id):
    """Delete attendance log by ID"""
    conn = get_db_connection()
    conn.execute('DELETE FROM attendance WHERE log_id = ?', (log_id,))
    conn.commit()
    conn.close()
