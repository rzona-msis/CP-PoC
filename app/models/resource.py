"""
Resource Model
Campus Resource Hub - AiDD 2025 Capstone

Represents campus resources that can be booked.
"""

from datetime import datetime
from app import db

class Resource(db.Model):
    """Resource model for bookable items."""
    
    __tablename__ = 'resources'
    
    resource_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # study_room, equipment, lab, event_space, tutoring
    location = db.Column(db.String(200))
    capacity = db.Column(db.Integer)
    images = db.Column(db.Text)  # Comma-separated paths or JSON
    availability_rules = db.Column(db.Text)  # JSON blob for recurring availability
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    requires_approval = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='resource', lazy='dynamic')
    reviews = db.relationship('Review', backref='resource', lazy='dynamic')
    
    def average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)
    
    def is_available(self, start_time, end_time):
        """Check if resource is available for given time slot."""
        # Check for conflicting bookings
        conflicting = Booking.query.filter(
            Booking.resource_id == self.resource_id,
            Booking.status.in_(['pending', 'approved']),
            db.or_(
                db.and_(Booking.start_datetime <= start_time, Booking.end_datetime > start_time),
                db.and_(Booking.start_datetime < end_time, Booking.end_datetime >= end_time),
                db.and_(Booking.start_datetime >= start_time, Booking.end_datetime <= end_time)
            )
        ).first()
        return conflicting is None
    
    def __repr__(self):
        return f'<Resource {self.title}>'
