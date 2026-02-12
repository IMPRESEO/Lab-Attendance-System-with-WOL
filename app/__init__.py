"""
Flask Application Factory
"""
import os
from flask import Flask
from .config import Config
from .models import init_db


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = Config.ALLOWED_EXTENSIONS
    
    # Initialize database
    # Ensure upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    init_db()
    
    # Register blueprints
    from .routes import auth_bp, dashboard_bp, hardware_bp, reports_bp, analytics_bp, profile_bp, search_bp, management_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(hardware_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(management_bp)
    
    return app
