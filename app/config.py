"""
Configuration settings for the application
"""
import os

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'thiagarajar_polytechnic_secret_key_2024')
    DATABASE = os.environ.get('DATABASE', 'attendance.db')
    DEBUG = os.environ.get('DEBUG', True)
    HOST = '0.0.0.0'
    # Use absolute path for upload folder to avoid confusion
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'profile_photos')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    PORT = 5000


# Global hardware state (shared across requests)
class HardwareState:
    """Manages hardware mode and enrollment status"""
    mode = {"action": "attendance", "id": None}
    enrollment = {"status": "idle", "finger_id": None, "message": ""}
    
    @classmethod
    def set_enroll_mode(cls, finger_id):
        """Set to enrollment mode"""
        cls.mode = {"action": "enroll", "id": finger_id}
        cls.enrollment = {"status": "pending", "finger_id": finger_id, "message": "Waiting for ESP32..."}
    
    @classmethod
    def set_attendance_mode(cls):
        """Reset to attendance mode"""
        cls.mode = {"action": "attendance", "id": None}
        cls.enrollment = {"status": "idle", "finger_id": None, "message": ""}
    
    @classmethod
    def update_enrollment(cls, status, finger_id, message):
        """Update enrollment status"""
        cls.enrollment = {"status": status, "finger_id": finger_id, "message": message}
