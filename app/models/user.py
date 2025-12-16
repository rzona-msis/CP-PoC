"""
User Model
Campus Resource Hub - AiDD 2025 Capstone

Represents users in the system with role-based access.
Roles: student, staff, admin
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """User model with authentication and role-based access."""
    
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student, staff, admin
    profile_image = db.Column(db.String(200))
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_resources = db.relationship('Resource', backref='owner', lazy='dynamic', 
                                     foreign_keys='Resource.owner_id')
    bookings = db.relationship('Booking', backref='requester', lazy='dynamic',
                              foreign_keys='Booking.requester_id')
    sent_messages = db.relationship('Message', backref='sender', lazy='dynamic',
                                   foreign_keys='Message.sender_id')
    received_messages = db.relationship('Message', backref='receiver', lazy='dynamic',
                                       foreign_keys='Message.receiver_id')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID for Flask-Login."""
        return str(self.user_id)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def is_staff(self):
        """Check if user is staff or admin."""
        return self.role in ['staff', 'admin']
    
    def __repr__(self):
        return f'<User {self.email}>'
