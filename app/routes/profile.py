"""
Student profile routes - individual student information and attendance history
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
from ..models import get_db_connection
from ..config import Config

profile_bp = Blueprint('profile', __name__)


def get_student_details(reg_no):
    """Get detailed student information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student basic info
    cursor.execute('''
        SELECT id, name, reg_no, role, finger_id, mac_address
        FROM users 
        WHERE reg_no = ?
    ''', (reg_no,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return None
    
    # Get attendance history
    cursor.execute('''
        SELECT timestamp, status
        FROM attendance 
        WHERE reg_no = ?
        ORDER BY timestamp DESC
        LIMIT 50
    ''', (reg_no,))
    attendance_history = cursor.fetchall()
    
    # Get attendance statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_sessions,
            COUNT(CASE WHEN DATE(timestamp) = DATE('now') THEN 1 END) as today_sessions,
            COUNT(CASE WHEN DATE(timestamp) >= DATE('now', '-7 days') THEN 1 END) as weekly_sessions,
            COUNT(CASE WHEN DATE(timestamp) >= DATE('now', '-30 days') THEN 1 END) as monthly_sessions
        FROM attendance 
        WHERE reg_no = ?
    ''', (reg_no,))
    stats = cursor.fetchone()
    
    # Get monthly attendance pattern
    cursor.execute('''
        SELECT 
            strftime('%Y-%m', timestamp) as month,
            COUNT(*) as count,
            COUNT(DISTINCT DATE(timestamp)) as days_present
        FROM attendance 
        WHERE reg_no = ?
        AND DATE(timestamp) >= DATE('now', '-6 months')
        GROUP BY strftime('%Y-%m', timestamp)
        ORDER BY month DESC
    ''', (reg_no,))
    monthly_pattern = cursor.fetchall()
    
    conn.close()
    
    return {
        'student': dict(student),
        'attendance_history': [dict(row) for row in attendance_history],
        'stats': dict(stats),
        'monthly_pattern': [dict(row) for row in monthly_pattern]
    }


@profile_bp.route('/profile/<reg_no>')
def student_profile(reg_no):
    """Student profile page"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    if session['role'] not in ['admin', 'hod', 'staff']:
        return redirect(url_for('auth.index'))
    
    student_data = get_student_details(reg_no)
    
    if not student_data:
        return render_template('404.html'), 404
    
    return render_template('student_profile.html', 
                         student_data=student_data,
                         role=session['role'])


@profile_bp.route('/search-students')
def search_students():
    """API endpoint for student search"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT reg_no, name, role
        FROM users 
        WHERE (name LIKE ? OR reg_no LIKE ?)
        AND role = 'student'
        ORDER BY name
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%'))
    
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(students)


@profile_bp.route('/student-directory')
def student_directory():
    """Student directory with search and filtering"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    if session['role'] not in ['admin', 'hod', 'staff']:
        return redirect(url_for('auth.index'))
    
    # Get all students
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT reg_no, name, role, finger_id, mac_address
        FROM users 
        WHERE role = 'student'
        ORDER BY name
    ''')
    students = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('student_directory.html', 
                         students=students,
                         role=session['role'])
