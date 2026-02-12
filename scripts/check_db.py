import sqlite3

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Check if departments table exists and has data
cursor.execute('SELECT COUNT(*) FROM departments')
dept_count = cursor.fetchone()[0]
print('Department count:', dept_count)

# Check if classes table exists and has data
cursor.execute('SELECT COUNT(*) FROM classes')
class_count = cursor.fetchone()[0]
print('Class count:', class_count)

# Check if users table has new columns
cursor.execute('PRAGMA table_info(users)')
columns = cursor.fetchall()
print('User table columns:')
for col in columns:
    print(f'  {col[1]} - {col[2]}')

conn.close()
