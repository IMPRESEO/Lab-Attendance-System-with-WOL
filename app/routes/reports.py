"""
Reports routes - attendance reports, exports
"""
from flask import Blueprint, render_template, redirect, url_for, session, send_file
from datetime import datetime
import csv
import io
from ..models import get_all_attendance, delete_attendance

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/attendance_report')
def attendance_report():
    """View all attendance logs"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    logs = get_all_attendance()
    return render_template('attendance_report.html', logs=logs, role=session['role'])


@reports_bp.route('/download_excel')
def download_excel():
    """Download attendance logs as CSV"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    logs = get_all_attendance()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Register No', 'Timestamp', 'Status'])
    
    # Write data
    for log in logs:
        writer.writerow([log['name'], log['reg_no'], log['timestamp'], log['status']])
    
    # Convert to bytes
    output.seek(0)
    bytes_output = io.BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)
    
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'attendance_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@reports_bp.route('/delete_attendance/<int:log_id>')
def delete_attendance_route(log_id):
    """Delete attendance log (Admin, Staff, HOD only)"""
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    if session['role'] not in ['admin', 'staff', 'hod']:
        return redirect(url_for('reports.attendance_report'))
    
    delete_attendance(log_id)
    return redirect(url_for('reports.attendance_report'))
