"""
Advanced search and filtering routes
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
from ..models import get_db_connection

search_bp = Blueprint('search', __name__)


@search_bp.route('/advanced-search')
def advanced_search():
    """Advanced search page with filters"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    if session['role'] not in ['admin', 'hod', 'staff']:
        return redirect(url_for('auth.index'))
    
    return render_template('advanced_search.html', role=session['role'])


@search_bp.route('/api/search-attendance')
def api_search_attendance():
    """API endpoint for advanced attendance search"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get search parameters
        name_query = request.args.get('name', '')
        reg_no = request.args.get('reg_no', '')
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = '''
            SELECT a.log_id, a.name, a.reg_no, a.timestamp, a.status, u.role
            FROM attendance a
            JOIN users u ON a.reg_no = u.reg_no
            WHERE 1=1
        '''
        params = []
        
        if name_query:
            query += ' AND a.name LIKE ?'
            params.append(f'%{name_query}%')
        
        if reg_no:
            query += ' AND a.reg_no LIKE ?'
            params.append(f'%{reg_no}%')
        
        if role_filter:
            query += ' AND u.role = ?'
            params.append(role_filter)
        
        if status_filter:
            query += ' AND a.status = ?'
            params.append(status_filter)
        
        if date_from:
            query += ' AND DATE(a.timestamp) >= ?'
            params.append(date_from)
        
        if date_to:
            query += ' AND DATE(a.timestamp) <= ?'
            params.append(date_to)
        
        # Count total results
        count_query = query.replace('SELECT a.log_id, a.name, a.reg_no, a.timestamp, a.status, u.role', 'SELECT COUNT(*)')
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Add pagination
        query += ' ORDER BY a.timestamp DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'results': results,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@search_bp.route('/api/export-search')
def api_export_search():
    """Export search results to Excel"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        import pandas as pd
        from io import BytesIO
        import flask
        
        # Get same search parameters
        name_query = request.args.get('name', '')
        reg_no = request.args.get('reg_no', '')
        role_filter = request.args.get('role', '')
        status_filter = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query (same as search but without pagination)
        query = '''
            SELECT a.name as "Name", a.reg_no as "Register Number", 
                   u.role as "Role", a.timestamp as "Timestamp", a.status as "Status"
            FROM attendance a
            JOIN users u ON a.reg_no = u.reg_no
            WHERE 1=1
        '''
        params = []
        
        if name_query:
            query += ' AND a.name LIKE ?'
            params.append(f'%{name_query}%')
        
        if reg_no:
            query += ' AND a.reg_no LIKE ?'
            params.append(f'%{reg_no}%')
        
        if role_filter:
            query += ' AND u.role = ?'
            params.append(role_filter)
        
        if status_filter:
            query += ' AND a.status = ?'
            params.append(status_filter)
        
        if date_from:
            query += ' AND DATE(a.timestamp) >= ?'
            params.append(date_from)
        
        if date_to:
            query += ' AND DATE(a.timestamp) <= ?'
            params.append(date_to)
        
        query += ' ORDER BY a.timestamp DESC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # Create DataFrame
        df = pd.DataFrame([dict(row) for row in results])
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Attendance Search Results', index=False)
        
        output.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'attendance_search_{timestamp}.xlsx'
        
        return flask.send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
