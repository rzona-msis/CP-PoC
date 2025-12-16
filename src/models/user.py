"""
User model for Flask-Login integration.

This class wraps database user records and provides
the required interface for Flask-Login authentication.
"""

from flask_login import UserMixin


class User(UserMixin):
    """
    User class for authentication and session management.
    
    Implements UserMixin interface for Flask-Login compatibility.
    """
    
    def __init__(self, user_data):
        """
        Initialize User from database row.
        
        Args:
            user_data (sqlite3.Row): User record from database
        """
        self.user_id = user_data['user_id']
        self.name = user_data['name']
        self.email = user_data['email']
        self.role = user_data['role']
        self.department = user_data['department']
        self.profile_image = user_data['profile_image']
        self.created_at = user_data['created_at']
    
    def get_id(self):
        """
        Return user ID as string (required by Flask-Login).
        
        Returns:
            str: User ID
        """
        return str(self.user_id)
    
    def is_admin(self):
        """
        Check if user has admin role.
        
        Returns:
            bool: True if user is admin
        """
        return self.role == 'admin'
    
    def is_staff(self):
        """
        Check if user has staff role or higher.
        
        Returns:
            bool: True if user is staff or admin
        """
        return self.role in ['staff', 'admin']
    
    def is_student(self):
        """
        Check if user has student role.
        
        Returns:
            bool: True if user is student
        """
        return self.role == 'student'
    
    def __repr__(self):
        return f'<User {self.email}>'

