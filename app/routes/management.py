"""
Unified Department and User Management
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime
from ..models import (
    get_all_departments, get_department_stats, get_batch_stats, 
    get_users_by_department, get_users_by_batch, add_user_enhanced, 
    get_db_connection, get_all_users
)

management_bp = Blueprint('management', __name__)


# ============================================
# DEPARTMENT MANAGEMENT
# ============================================

@management_bp.route('/department-management')
def department_management():
    """Department management dashboard"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    if session['role'] not in ['admin', 'hod']:
        return redirect(url_for('auth.index'))
    
    departments = get_all_departments()
    department_stats = {}
    
    for dept in departments:
        department_stats[dept['name']] = get_department_stats(dept['name'])
    
    return render_template('department_management.html', 
                         departments=departments,
                         department_stats=department_stats,
                         role=session['role'])


@management_bp.route('/department/add', methods=['GET', 'POST'])
def add_department():
    """Add a new department"""
    if 'username' not in session or session['role'] != 'admin':
        flash('Unauthorized access', 'error')
        return redirect(url_for('management.department_management'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        hod_name = request.form.get('hod_name')
        description = request.form.get('description')
        
        if not all([name, hod_name]):
            flash('Name and HOD are required', 'error')
            return render_template('add_department.html', role=session['role'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check for duplicate name
            cursor.execute('SELECT id FROM departments WHERE name = ?', (name,))
            if cursor.fetchone():
                flash(f'Department {name} already exists!', 'error')
                return render_template('add_department.html', role=session['role'])
                
            cursor.execute('''
                INSERT INTO departments (name, hod_name, description)
                VALUES (?, ?, ?)
            ''', (name, hod_name, description))
            conn.commit()
            flash(f'Department {name} added successfully!', 'success')
            return redirect(url_for('management.department_management'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.close()
            
    return render_template('add_department.html', role=session['role'])


@management_bp.route('/department/edit/<department_name>', methods=['GET', 'POST'])
def edit_department(department_name):
    """Edit department details"""
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('management.department_management'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        hod_name = request.form.get('hod_name')
        description = request.form.get('description')
        
        if not all([name, hod_name]):
            flash('Name and HOD are required', 'error')
            return redirect(url_for('management.edit_department', department_name=department_name))
        
        try:
            cursor.execute('''
                UPDATE departments 
                SET name = ?, hod_name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (name, hod_name, description, department_name))
            conn.commit()
            flash(f'Department {name} updated!', 'success')
            return redirect(url_for('management.department_management'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    cursor.execute('SELECT * FROM departments WHERE name = ?', (department_name,))
    department = cursor.fetchone()
    conn.close()
    
    if not department:
        return redirect(url_for('management.department_management'))
    
    return render_template('edit_department.html', department=department, role=session['role'])


@management_bp.route('/department/delete/<department_name>', methods=['POST'])
def delete_department(department_name):
    """Delete a department"""
    if 'username' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM users WHERE department = ? AND role = "student"', (department_name,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'Cannot delete department with active students'}), 400
        
        cursor.execute('DELETE FROM departments WHERE name = ?', (department_name,))
        cursor.execute('UPDATE users SET department = NULL WHERE department = ?', (department_name,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Department deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@management_bp.route('/department/<department_name>')
def department_details(department_name):
    """Detailed department view with students"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    dept_info = conn.execute('SELECT * FROM departments WHERE name = ?', (department_name,)).fetchone()
    
    if not dept_info:
        return "Department Not Found", 404
    
    students = get_users_by_department(department_name)
    stats = get_department_stats(department_name)
    conn.close()
    
    return render_template('department_details.html', 
                         department=dict(dept_info),
                         students=students,
                         stats=stats,
                         role=session['role'])


# ============================================
# USER & BATCH MANAGEMENT
# ============================================


@management_bp.route('/batch-management')
def batch_management():
    """Batch year management dashboard"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    batch_stats = get_batch_stats()
    return render_template('batch_management.html', batch_stats=batch_stats, role=session['role'])


@management_bp.route('/batch/<batch_year>')
def batch_details(batch_year):
    """Detailed batch view with students"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    students = get_users_by_batch(batch_year)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) as total_students,
               COUNT(CASE WHEN finger_id IS NOT NULL THEN 1 END) as enrolled_students,
               COUNT(CASE WHEN mac_address IS NOT NULL THEN 1 END) as mac_assigned
        FROM users 
        WHERE batch_year = ? AND role = 'student'
    ''', (batch_year,))
    batch_info = cursor.fetchone()
    
    cursor.execute('''
        SELECT department, COUNT(*) as count
        FROM users 
        WHERE batch_year = ? AND role = 'student'
        GROUP BY department
        ORDER BY count DESC
    ''', (batch_year,))
    dept_distribution = cursor.fetchall()
    conn.close()
    
    return render_template('batch_details.html', 
                         batch_year=batch_year,
                         students=students,
                         batch_info=dict(batch_info),
                         dept_distribution=dept_distribution,
                         role=session['role'])


@management_bp.route('/user/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit user details and photo"""
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('dashboard.dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Import here to avoid potential circular dependencies
    from .dashboard import allowed_file
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app

    if request.method == 'POST':
        name = request.form.get('name')
        reg_no = request.form.get('reg_no')
        role = request.form.get('role')
        department = request.form.get('department')
        batch_year = request.form.get('batch_year')
        
        if not all([name, reg_no, role]):
            flash('Required fields missing', 'error')
            return redirect(url_for('management.edit_user', user_id=user_id))
        
        try:
            # Check for duplicate Reg No if it's being changed
            cursor.execute('SELECT id FROM users WHERE reg_no = ? AND id != ?', (reg_no, user_id))
            if cursor.fetchone():
                flash('Error: Register Number already belongs to another user.', 'error')
                return redirect(url_for('management.edit_user', user_id=user_id))

            # Handle Photo Upload
            photo_path = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(f"{reg_no}_{file.filename}")
                    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(save_path)
                    photo_path = f"uploads/profile_photos/{filename}"

            query = '''
                UPDATE users 
                SET name = ?, reg_no = ?, role = ?, department = ?, batch_year = ?, updated_at = CURRENT_TIMESTAMP
            '''
            params = [name, reg_no, role, department, batch_year]
            
            if photo_path:
                query += ", photo_path = ?"
                params.append(photo_path)
            
            query += " WHERE id = ?"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            conn.commit()
            flash(f'User {name} updated!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    departments = get_all_departments()
    conn.close()
    
    if not user:
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('edit_user.html', user=user, departments=departments, role=session['role'])


# ============================================
# API ENDPOINTS
# ============================================

@management_bp.route('/api/users-by-department/<department>')
def api_get_users_by_department(department):
    if 'username' not in session: return jsonify({'error': 'Unauthorized'}), 401
    return jsonify([dict(u) for u in get_users_by_department(department)])


@management_bp.route('/api/department-stats/<department_name>')
def api_department_stats(department_name):
    if 'username' not in session: return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_department_stats(department_name))

