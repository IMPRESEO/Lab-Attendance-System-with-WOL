import sqlite3
import os

db_path = 'attendance.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        print("Adding photo_path column to users table...")
        cursor.execute('ALTER TABLE users ADD COLUMN photo_path TEXT')
        conn.commit()
        print("Success!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("Column photo_path already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"Database {db_path} not found.")
