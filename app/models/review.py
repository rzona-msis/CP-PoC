"""
Review Model
Campus Resource Hub - AiDD 2025 Capstone

Represents user reviews for resources.
"""

from datetime import datetime
from app import db

class Review(db.Model):
    """Review model for resource ratings and comments."""
    
    __tablename__ = 'reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one review per user per resource
    __table_args__ = (db.UniqueConstraint('resource_id', 'reviewer_id', name='_resource_reviewer_uc'),)
    
    def __repr__(self):
        return f'<Review {self.review_id} for Resource {self.resource_id}>'
