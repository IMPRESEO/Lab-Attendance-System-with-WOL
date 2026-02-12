"""
Hardware API routes - ESP32 communication, fingerprint enrollment
"""
from flask import Blueprint, jsonify, request, redirect, url_for, session
from datetime import datetime
from wakeonlan import send_magic_packet
from ..models import get_user_by_finger_id, log_attendance
from ..config import HardwareState

hardware_bp = Blueprint('hardware', __name__)

# Status messages for enrollment process
ENROLLMENT_MESSAGES = {
    "started": "Enrollment started",
    "waiting_finger_1": "Place finger on sensor...",
    "got_finger_1": "First scan complete! Remove finger",
    "remove_finger": "Remove finger from sensor",
    "waiting_finger_2": "Place the SAME finger again...",
    "got_finger_2": "Second scan complete!",
    "processing": "Processing fingerprint...",
    "success": "✅ Enrollment successful!",
    "failed": "❌ Enrollment failed. Please try again."
}


@hardware_bp.route('/get_mode', methods=['GET'])
def get_mode():
    """ESP32 polls this to know what mode to operate in"""
    return jsonify(HardwareState.mode)


@hardware_bp.route('/activate_enroll/<int:finger_id>', methods=['GET'])
def activate_enroll(finger_id):
    """Activate enrollment mode for a specific finger ID"""
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    HardwareState.set_enroll_mode(finger_id)
    
    # Clear any previous enrollment notification
    session.pop('just_enrolled_id', None)
    
    return redirect(url_for('dashboard.dashboard'))


@hardware_bp.route('/cancel_enroll', methods=['GET'])
def cancel_enroll():
    """Cancel enrollment and return to attendance mode"""
    HardwareState.set_attendance_mode()
    return redirect(url_for('dashboard.dashboard'))


@hardware_bp.route('/enrollment_status', methods=['POST'])
def enrollment_status():
    """Receive enrollment status updates from ESP32"""
    data = request.get_json()
    finger_id = data.get('finger_id')
    status = data.get('status')
    
    if not finger_id or not status:
        return jsonify({"status": "error", "message": "Missing data"}), 400
    
    # Update global status
    message = ENROLLMENT_MESSAGES.get(status, status)
    HardwareState.update_enrollment(status, finger_id, message)
    
    # Auto-reset to attendance mode when enrollment completes
    if status in ["success", "failed"]:
        if status == "success":
            session['just_enrolled_id'] = finger_id
            # Log the successful fingerprint enrollment
            user = get_user_by_finger_id(finger_id)
            if user:
                print(f"[FINGERPRINT ENROLLED] User: {user['name']} (ID: {user['id']}), Finger ID: {finger_id}, Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"[FINGERPRINT ENROLLED] Finger ID: {finger_id} assigned to new user, Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        HardwareState.set_attendance_mode()
    
    return jsonify({"status": "ok"})


@hardware_bp.route('/get_enrollment_status', methods=['GET'])
def get_enrollment_status():
    """Get current enrollment status for website polling"""
    return jsonify(HardwareState.enrollment)


@hardware_bp.route('/verify', methods=['POST'])
def verify():
    """Receive fingerprint verification from ESP32"""
    data = request.get_json()
    finger_id = data.get('finger_id')
    
    if not finger_id:
        return jsonify({"status": "error", "message": "No finger ID provided"})
    
    # Find user by finger ID
    user = get_user_by_finger_id(finger_id)
    
    if not user:
        return jsonify({"status": "error", "message": "User not found"})
    
    # Log attendance
    log_attendance(user['name'], user['reg_no'])
    
    # Wake-on-LAN if MAC address exists
    wake_message = None
    if user['mac_address']:
        try:
            send_magic_packet(user['mac_address'])
            wake_message = f"🚀 Wake Signal Sent to {user['name']}'s PC ({user['mac_address']})"
            session['wake_msg'] = wake_message
        except Exception as e:
            wake_message = f"⚠️ Failed to send wake signal: {str(e)}"
            session['wake_msg'] = wake_message
    
    return jsonify({
        "status": "success", 
        "message": f"Welcome {user['name']}!",
        "wake_message": wake_message
    })
