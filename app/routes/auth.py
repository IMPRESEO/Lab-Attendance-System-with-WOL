"""
Authentication routes - login, logout, home pages
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from ..models import (
    get_user_by_credentials, get_recent_attendance, 
    get_total_users, get_today_attendance_count
)
from ..config import HardwareState

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Public home page - shows fingerprint status"""
    recent_logs = get_recent_attendance(5)
    
    return render_template('public_home.html', 
                         total_users=get_total_users(),
                         today_attendance=get_today_attendance_count(),
                         recent_logs=recent_logs,
                         system_status="Online",
                         current_mode=HardwareState.mode)


@auth_bp.route('/home')
def home():
    """Logged-in home screen - shows recent activity"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('index.html', 
                         username=session['username'],
                         role=session['role'],
                         recent_logs=get_recent_attendance(10),
                         total_users=get_total_users(),
                         today_attendance=get_today_attendance_count(),
                         wake_msg=session.pop('wake_msg', None))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Master key check
        if username == 'admin' and password == 'admin123':
            session['username'] = 'System Admin'
            session['role'] = 'admin'
            return redirect(url_for('auth.home'))
        
        # Database check
        user = get_user_by_credentials(username, password)
        
        if user:
            session['username'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('auth.home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('auth.index'))
