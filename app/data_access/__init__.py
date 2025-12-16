"""
Data Access Layer Package
Campus Resource Hub - AiDD 2025 Capstone

Import all DAL classes for easy access.
"""

from app.data_access.user_dal import UserDAL
from app.data_access.resource_dal import ResourceDAL
from app.data_access.booking_dal import BookingDAL
from app.data_access.message_dal import MessageDAL
from app.data_access.review_dal import ReviewDAL

__all__ = ['UserDAL', 'ResourceDAL', 'BookingDAL', 'MessageDAL', 'ReviewDAL']
