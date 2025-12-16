"""
Booking Data Access Layer
Campus Resource Hub - AiDD 2025 Capstone

CRUD operations for Booking model with conflict detection.
"""

from datetime import datetime
from app import db
from app.models import Booking, Resource

class BookingDAL:
    """Data Access Layer for Booking operations."""
    
    @staticmethod
    def create_booking(resource_id, requester_id, start_datetime, end_datetime, message=None):
        """Create a new booking request."""
        booking = Booking(
            resource_id=resource_id,
            requester_id=requester_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            message=message,
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()
        return booking
    
    @staticmethod
    def get_booking_by_id(booking_id):
        """Get booking by ID."""
        return Booking.query.get(booking_id)
    
    @staticmethod
    def get_bookings_by_user(user_id):
        """Get all bookings for a user."""
        return Booking.query.filter_by(requester_id=user_id).all()
    
    @staticmethod
    def get_bookings_by_resource(resource_id):
        """Get all bookings for a resource."""
        return Booking.query.filter_by(resource_id=resource_id).all()
    
    @staticmethod
    def get_pending_bookings_for_owner(owner_id):
        """Get all pending bookings for resources owned by a user."""
        return Booking.query.join(Resource).filter(
            Resource.owner_id == owner_id,
            Booking.status == 'pending'
        ).all()
    
    @staticmethod
    def get_active_bookings(user_id=None):
        """Get all active (approved) bookings, optionally filtered by user."""
        query = Booking.query.filter_by(status='approved')
        if user_id:
            query = query.filter_by(requester_id=user_id)
        return query.all()
    
    @staticmethod
    def check_conflicts(resource_id, start_datetime, end_datetime, exclude_booking_id=None):
        """Check for booking conflicts."""
        query = Booking.query.filter(
            Booking.resource_id == resource_id,
            Booking.status.in_(['pending', 'approved']),
            db.or_(
                db.and_(Booking.start_datetime <= start_datetime, Booking.end_datetime > start_datetime),
                db.and_(Booking.start_datetime < end_datetime, Booking.end_datetime >= end_datetime),
                db.and_(Booking.start_datetime >= start_datetime, Booking.end_datetime <= end_datetime)
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.booking_id != exclude_booking_id)
        
        return query.first() is not None
    
    @staticmethod
    def approve_booking(booking_id):
        """Approve a booking."""
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
        
        booking.approve()
        db.session.commit()
        return booking
    
    @staticmethod
    def reject_booking(booking_id):
        """Reject a booking."""
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
        
        booking.reject()
        db.session.commit()
        return booking
    
    @staticmethod
    def cancel_booking(booking_id):
        """Cancel a booking."""
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
        
        booking.cancel()
        db.session.commit()
        return booking
    
    @staticmethod
    def update_booking(booking_id, **kwargs):
        """Update booking fields."""
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
        
        for key, value in kwargs.items():
            if hasattr(booking, key):
                setattr(booking, key, value)
        
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        return booking
    
    @staticmethod
    def delete_booking(booking_id):
        """Delete a booking."""
        booking = Booking.query.get(booking_id)
        if not booking:
            return False
        
        db.session.delete(booking)
        db.session.commit()
        return True
