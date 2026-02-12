"""
Routes package - contains all Flask blueprints
"""
from .auth import auth_bp
from .dashboard import dashboard_bp
from .hardware import hardware_bp
from .reports import reports_bp
from .analytics import analytics_bp
from .profile import profile_bp
from .search import search_bp
from .management import management_bp

__all__ = ['auth_bp', 'dashboard_bp', 'hardware_bp', 'reports_bp', 'analytics_bp', 'profile_bp', 'search_bp', 'management_bp']
