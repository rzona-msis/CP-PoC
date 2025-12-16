"""
Controllers Package
Campus Resource Hub - AiDD 2025 Capstone

Import all blueprints for easy access.
"""

from app.controllers.auth import auth_bp
from app.controllers.main import main_bp
from app.controllers.resources import resources_bp
from app.controllers.bookings import bookings_bp
from app.controllers.messages import messages_bp
from app.controllers.reviews import reviews_bp
from app.controllers.admin import admin_bp

__all__ = ['auth_bp', 'main_bp', 'resources_bp', 'bookings_bp', 'messages_bp', 'reviews_bp', 'admin_bp']
