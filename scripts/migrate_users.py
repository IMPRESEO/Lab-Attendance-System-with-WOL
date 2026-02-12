"""
Database migration script to update existing users with department information
"""
import sqlite3
from datetime import datetime

def migrate_existing_users():
    """Update existing users to have department and class information"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Check if users have department info
    cursor.execute('SELECT COUNT(*) FROM users WHERE department IS NULL')
    users_without_dept = cursor.fetchone()[0]
    
    if users_without_dept > 0:
        print(f"Found {users_without_dept} users without department info")
        
        # Update existing users with sample data
        cursor.execute('''
            UPDATE users 
            SET department = 'Computer Science',
                class_name = 'CS-A',
                batch_year = '2023-2024',
                semester = '3'
            WHERE role = 'student' AND department IS NULL
        ''')
        
        cursor.execute('''
            UPDATE users 
            SET department = 'Computer Science',
                class_name = 'Staff',
                batch_year = NULL,
                semester = NULL
            WHERE role = 'staff' AND department IS NULL
        ''')
        
        cursor.execute('''
            UPDATE users 
            SET department = 'Computer Science',
                class_name = 'HOD',
                batch_year = NULL,
                semester = NULL
            WHERE role = 'hod' AND department IS NULL
        ''')
        
        conn.commit()
        print(f"Updated {users_without_dept} users with department information")
    else:
        print("All users already have department information")
    
    conn.close()

if __name__ == '__main__':
    migrate_existing_users()
