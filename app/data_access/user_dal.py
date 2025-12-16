"""
User Data Access Layer
Campus Resource Hub - AiDD 2025 Capstone

CRUD operations for User model.
"""

from app import db
from app.models import User

class UserDAL:
    """Data Access Layer for User operations."""
    
    @staticmethod
    def create_user(name, email, password, role='student', department=None):
        """Create a new user."""
        user = User(name=name, email=email, role=role, department=department)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_users():
        """Get all users."""
        return User.query.all()
    
    @staticmethod
    def get_users_by_role(role):
        """Get all users with a specific role."""
        return User.query.filter_by(role=role).all()
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user fields."""
        user = User.query.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and key != 'password':
                setattr(user, key, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password."""
        user = User.query.get(user_id)
        if not user:
            return None
        
        user.set_password(new_password)
        db.session.commit()
        return user
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user."""
        user = User.query.get(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password."""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
