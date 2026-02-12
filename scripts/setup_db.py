"""
Database Setup Script
Creates fresh database with sample data for testing
"""

import sqlite3
import os

DATABASE = 'attendance.db'

def setup_database():
    """Wipe and recreate database with sample data"""
    
    # Remove existing database
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print("✓ Removed existing database")
    
    # Create connection
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reg_no TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            finger_id INTEGER UNIQUE,
            mac_address TEXT,
            password TEXT NOT NULL
        )
    ''')
    print("✓ Created users table")
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE attendance (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reg_no TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT DEFAULT 'Present'
        )
    ''')
    print("✓ Created attendance table")
    
    # Insert sample users
    sample_users = [
        ('System Admin', 'ADMIN001', 'admin', None, None, 'admin123'),
        ('Dr. Ravi Kumar', 'HOD001', 'hod', None, None, 'hod123'),
        ('Prof. Priya Sharma', 'STAFF001', 'staff', None, None, 'staff123'),
        ('Buvanesh K', 'A23CS001', 'student', 1, 'D4-5D-64-A1-B2-C3', 'student123'),
        ('Arun Prakash', 'A23CS002', 'student', 2, 'E8-6E-75-B2-C3-D4', 'student123'),
        ('Deepika M', 'A23CS003', 'student', 3, 'F9-7F-86-C3-D4-E5', 'student123'),
        ('Karthik Raja', 'A23CS004', 'student', 4, 'A1-B2-C3-D4-E5-F6', 'student123'),
        ('Lakshmi Priya', 'A23CS005', 'student', 5, 'B2-C3-D4-E5-F6-A7', 'student123'),
    ]
    
    cursor.executemany('''
        INSERT INTO users (name, reg_no, role, finger_id, mac_address, password)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_users)
    print(f"✓ Inserted {len(sample_users)} sample users")
    
    # Insert sample attendance logs
    sample_logs = [
        ('Buvanesh K', 'A23CS001', '2024-02-05 09:15:23', 'Present'),
        ('Arun Prakash', 'A23CS002', '2024-02-05 09:16:45', 'Present'),
        ('Deepika M', 'A23CS003', '2024-02-05 09:18:12', 'Present'),
        ('Karthik Raja', 'A23CS004', '2024-02-05 09:20:33', 'Present'),
        ('Buvanesh K', 'A23CS001', '2024-02-04 10:05:11', 'Present'),
        ('Lakshmi Priya', 'A23CS005', '2024-02-04 10:07:22', 'Present'),
    ]
    
    cursor.executemany('''
        INSERT INTO attendance (name, reg_no, timestamp, status)
        VALUES (?, ?, ?, ?)
    ''', sample_logs)
    print(f"✓ Inserted {len(sample_logs)} sample attendance logs")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("\n✅ Database setup complete!")
    print("\n📋 Login Credentials:")
    print("   Admin:  admin / admin123")
    print("   HOD:    Dr. Ravi Kumar / hod123")
    print("   Staff:  Prof. Priya Sharma / staff123")
    print("\n🔧 Sample Students with Finger IDs:")
    print("   Buvanesh K (ID: 1) - MAC: D4-5D-64-A1-B2-C3")
    print("   Arun Prakash (ID: 2) - MAC: E8-6E-75-B2-C3-D4")
    print("   Deepika M (ID: 3) - MAC: F9-7F-86-C3-D4-E5")

if __name__ == '__main__':
    setup_database()
