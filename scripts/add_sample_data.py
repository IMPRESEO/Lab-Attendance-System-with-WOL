import sqlite3
from datetime import datetime

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Add sample students with department and class info
sample_students = [
    ('Ravi Kumar', 'A23CS001', 'student', 'Computer Science', '2023-2024', 'ravi123'),
    ('Priya Sharma', 'A23CS002', 'student', 'Computer Science', '2023-2024', 'priya123'),
    ('Amit Patel', 'A23CS003', 'student', 'Computer Science', '2023-2024', 'amit123'),
    ('Sneha Reddy', 'A23EC001', 'student', 'Electronics', '2023-2024', 'sneha123'),
    ('Vikram Singh', 'A23EC002', 'student', 'Electronics', '2023-2024', 'vikram123'),
    ('Anita Kumar', 'A23ME001', 'student', 'Mechanical', '2023-2024', 'anita123'),
    ('Rahul Verma', 'A23ME002', 'student', 'Mechanical', '2023-2024', 'rahul123'),
    ('Divya Patel', 'A23CE001', 'student', 'Civil', '2023-2024', 'divya123'),
    ('Rohit Sharma', 'A23EE001', 'student', 'Electrical', '2023-2024', 'rohit123'),
    ('Kavita Reddy', 'A23IT001', 'student', 'Information Technology', '2023-2024', 'kavita123'),
]

# Check if users already exist
cursor.execute('SELECT COUNT(*) FROM users WHERE role="student"')
existing_students = cursor.fetchone()[0]

if existing_students == 0:
    for student in sample_students:
        cursor.execute('''
            INSERT INTO users (name, reg_no, role, department, batch_year, password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', student)
    print(f'Added {len(sample_students)} sample students')
else:
    print(f'Students already exist: {existing_students}')

# Add some attendance records
cursor.execute('SELECT COUNT(*) FROM attendance')
existing_attendance = cursor.fetchone()[0]

if existing_attendance == 0:
    # Add sample attendance for today
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('SELECT reg_no, name, department FROM users WHERE role="student"')
    students = cursor.fetchall()
    
    for student in students:
        cursor.execute('''
            INSERT INTO attendance (name, reg_no, timestamp, status, department)
            VALUES (?, ?, ?, 'Present', ?)
        ''', (student[1], student[0], today, student[2]))
    
    print(f'Added {len(students)} attendance records')
else:
    print(f'Attendance records already exist: {existing_attendance}')

conn.commit()
conn.close()
print('Sample data added successfully!')
