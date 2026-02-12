"""
Analytics routes - attendance statistics, charts, reports
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
from ..models import get_db_connection
from ..config import Config

analytics_bp = Blueprint('analytics', __name__)


def get_attendance_stats():
    """Get comprehensive attendance statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COUNT(*) as today_count,
               COUNT(DISTINCT reg_no) as unique_students
        FROM attendance 
        WHERE DATE(timestamp) = ?
    ''', (today,))
    today_stats = cursor.fetchone()
    
    # Get weekly attendance
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM attendance 
        WHERE DATE(timestamp) >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (week_ago,))
    weekly_data = cursor.fetchall()
    
    # Get role-wise attendance
    cursor.execute('''
        SELECT u.role, COUNT(a.log_id) as attendance_count
        FROM users u
        LEFT JOIN attendance a ON u.reg_no = a.reg_no 
        AND DATE(a.timestamp) = ?
        GROUP BY u.role
    ''', (today,))
    role_stats = cursor.fetchall()
    
    # Get top performers (highest attendance)
    cursor.execute('''
        SELECT u.name, u.reg_no, COUNT(a.log_id) as attendance_count
        FROM users u
        LEFT JOIN attendance a ON u.reg_no = a.reg_no
        WHERE u.role = 'student'
        GROUP BY u.reg_no, u.name
        ORDER BY attendance_count DESC
        LIMIT 10
    ''')
    top_performers = cursor.fetchall()
    
    conn.close()
    
    return {
        'today_count': today_stats['today_count'] if today_stats else 0,
        'unique_students': today_stats['unique_students'] if today_stats else 0,
        'weekly_data': [dict(row) for row in weekly_data],
        'role_stats': [dict(row) for row in role_stats],
        'top_performers': [dict(row) for row in top_performers]
    }


def get_monthly_trends():
    """Get monthly attendance trends for the past 6 months"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT strftime('%Y-%m', timestamp) as month,
               COUNT(*) as count,
               COUNT(DISTINCT reg_no) as unique_students
        FROM attendance 
        WHERE DATE(timestamp) >= ?
        GROUP BY month
        ORDER BY month
    ''', (six_months_ago,))
    
    monthly_data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return monthly_data


@analytics_bp.route('/analytics')
def analytics():
    """Main analytics dashboard"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    if session['role'] not in ['admin', 'hod', 'staff']:
        return redirect(url_for('auth.index'))
    
    stats = get_attendance_stats()
    monthly_trends = get_monthly_trends()
    
    return render_template('analytics.html', 
                         stats=stats,
                         monthly_trends=monthly_trends,
                         role=session['role'])


@analytics_bp.route('/api/attendance-trends')
def api_attendance_trends():
    """API endpoint for attendance trends chart"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        trends = get_monthly_trends()
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/api/daily-stats')
def api_daily_stats():
    """API endpoint for daily statistics"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        stats = get_attendance_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
