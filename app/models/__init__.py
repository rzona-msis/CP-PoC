"""
Models Package
Campus Resource Hub - AiDD 2025 Capstone

Import all models for easy access.
"""

from app.models.user import User
from app.models.resource import Resource
from app.models.booking import Booking
from app.models.message import Message
from app.models.review import Review

__all__ = ['User', 'Resource', 'Booking', 'Message', 'Review']
