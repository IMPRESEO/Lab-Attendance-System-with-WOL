"""
Dashboard routes - user management, admin panel
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from ..models import (
    add_user_enhanced, get_all_users, get_next_finger_id, delete_user, 
    update_user_mac, clear_user_fingerprint, get_all_departments, get_db_connection
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def dashboard():
    """Enhanced dashboard with department and class management"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    if session['role'] not in ['admin', 'hod']:
        return redirect(url_for('auth.index'))
    
    return render_template('dashboard.html', 
                         users=get_all_users(),
                         next_finger_id=get_next_finger_id(),
                         departments=get_all_departments(),
                         role=session['role'],
                         just_enrolled_id=session.pop('just_enrolled_id', None))


@dashboard_bp.route('/add_user', methods=['POST'])
def add_user_route():
    """Register new user (Legacy endpoint preserved or redirected)"""
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    # Adapt to enhanced version if needed, but keeping legacy for now if simple
    from ..models import add_user
    name = request.form['name']
    reg_no = request.form['reg_no']
    role = request.form['role']
    password = request.form['password']
    
    add_user(name, reg_no, role, password)
    return redirect(url_for('dashboard.dashboard'))


import os
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@dashboard_bp.route('/add-student-enhanced', methods=['POST'])
def add_student_enhanced_route():
    """Add student with optional password and immediate enrollment option"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session['role'] != 'admin':
        return jsonify({'error': 'Only administrators can add users'}), 403
    
    try:
        # Get form data
        name = request.form.get('name')
        reg_no = request.form.get('reg_no')
        role = request.form.get('role')
        department = request.form.get('department')
        batch_year = request.form.get('batch_year')
        password = request.form.get('password')
        enroll_now = request.form.get('enroll_now') == 'true'
        
        # Validation: password only required for non-student roles
        if role != 'student' and not password:
            return jsonify({'error': 'Password is required for staff/admin roles'}), 400
            
        if not all([name, reg_no, role, department]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Handle Photo Upload
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{reg_no}_{file.filename}")
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                photo_path = f"uploads/profile_photos/{filename}"
        
        # Add user
        from ..models import get_next_finger_id
        next_finger_id = get_next_finger_id()
        
        result = add_user_enhanced(
            name, reg_no, role, department, batch_year, password, photo_path=photo_path, finger_id=next_finger_id
        )
        
        if isinstance(result, dict) and 'success' in result:
            user_id = result['user_id']
            flash(f'User {name} added successfully!', 'success')
            
            # Immediate Enrollment Logic
            if enroll_now:
                from ..config import HardwareState
                HardwareState.set_enroll_mode(next_finger_id)
                return jsonify({
                    'success': True, 
                    'user_id': user_id, 
                    'enroll_now': True, 
                    'finger_id': next_finger_id
                })
                
            return jsonify({'success': True, 'user_id': user_id})
        else:
            error_msg = result.get('error', 'Unknown database error') if isinstance(result, dict) else 'Database error'
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/delete_user/<int:user_id>')
def delete_user_route(user_id):
    """Delete user (Admin only)"""
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    delete_user(user_id)
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/update_mac', methods=['POST'])
def update_mac():
    """Update MAC address for a user"""
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    user_id = request.form['user_id']
    mac_address = request.form['mac_address']
    
    update_user_mac(user_id, mac_address)
    
    # Clear enrollment notification when other actions happen
    session.pop('just_enrolled_id', None)
    
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/delete_fingerprint/<int:user_id>')
def delete_fingerprint(user_id):
    """Delete fingerprint enrollment for a user (Admin only)"""
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    clear_user_fingerprint(user_id)
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/api/get-classes-by-department/<department>')
def api_get_classes_by_department(department):
    """API endpoint to get classes by department"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        classes = conn.execute('''
            SELECT * FROM classes 
            WHERE department = ? 
            ORDER BY name
        ''', (department,)).fetchall()
        conn.close()
        
        return jsonify([dict(cls) for cls in classes])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/get-departments')
def api_get_departments():
    """API endpoint to get all departments"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        departments = get_all_departments()
        return jsonify([dict(dept) for dept in departments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/get-batches-by-department/<department>')
def api_get_batches_by_department(department):
    """API endpoint to get batch years by department"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        batches = conn.execute('''
            SELECT DISTINCT batch_year 
            FROM users 
            WHERE department = ? AND batch_year IS NOT NULL
            ORDER BY batch_year DESC
        ''', (department,)).fetchall()
        conn.close()
        
        return jsonify([{'batch_year': batch['batch_year']} for batch in batches])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

