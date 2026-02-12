"""
Thiagarajar Polytechnic AI & ML Lab Management System
Smart Biometric Attendance & Lab Automation System

Entry point for running the application
"""
from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
