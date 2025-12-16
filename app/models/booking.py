"""
Booking Model
Campus Resource Hub - AiDD 2025 Capstone

Represents booking requests for resources.
"""

from datetime import datetime
from app import db

class Booking(db.Model):
    """Booking model for resource reservations."""
    
    __tablename__ = 'bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    message = db.Column(db.Text)  # Request message or cancellation reason
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def approve(self):
        """Approve the booking."""
        self.status = 'approved'
        self.updated_at = datetime.utcnow()
    
    def reject(self):
        """Reject the booking."""
        self.status = 'rejected'
        self.updated_at = datetime.utcnow()
    
    def cancel(self):
        """Cancel the booking."""
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()
    
    def is_active(self):
        """Check if booking is currently active."""
        return self.status in ['pending', 'approved']
    
    def is_past(self):
        """Check if booking is in the past."""
        return self.end_datetime < datetime.utcnow()
    
    def __repr__(self):
        return f'<Booking {self.booking_id} for Resource {self.resource_id}>'
