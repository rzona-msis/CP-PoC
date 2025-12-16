"""
Review Data Access Layer
Campus Resource Hub - AiDD 2025 Capstone

CRUD operations for Review model.
"""

from app import db
from app.models import Review

class ReviewDAL:
    """Data Access Layer for Review operations."""
    
    @staticmethod
    def create_review(resource_id, reviewer_id, rating, comment=None):
        """Create a new review."""
        # Check if user already reviewed this resource
        existing = Review.query.filter_by(
            resource_id=resource_id,
            reviewer_id=reviewer_id
        ).first()
        
        if existing:
            return None  # User already reviewed this resource
        
        review = Review(
            resource_id=resource_id,
            reviewer_id=reviewer_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        return review
    
    @staticmethod
    def get_review_by_id(review_id):
        """Get review by ID."""
        return Review.query.get(review_id)
    
    @staticmethod
    def get_reviews_by_resource(resource_id):
        """Get all reviews for a resource."""
        return Review.query.filter_by(resource_id=resource_id).order_by(Review.timestamp.desc()).all()
    
    @staticmethod
    def get_reviews_by_user(reviewer_id):
        """Get all reviews by a user."""
        return Review.query.filter_by(reviewer_id=reviewer_id).order_by(Review.timestamp.desc()).all()
    
    @staticmethod
    def get_average_rating(resource_id):
        """Get average rating for a resource."""
        reviews = Review.query.filter_by(resource_id=resource_id).all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)
    
    @staticmethod
    def get_rating_distribution(resource_id):
        """Get distribution of ratings (1-5 stars) for a resource."""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        reviews = Review.query.filter_by(resource_id=resource_id).all()
        for review in reviews:
            distribution[review.rating] += 1
        return distribution
    
    @staticmethod
    def update_review(review_id, rating=None, comment=None):
        """Update a review."""
        review = Review.query.get(review_id)
        if not review:
            return None
        
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        
        db.session.commit()
        return review
    
    @staticmethod
    def delete_review(review_id):
        """Delete a review."""
        review = Review.query.get(review_id)
        if not review:
            return False
        
        db.session.delete(review)
        db.session.commit()
        return True
    
    @staticmethod
    def user_can_review(user_id, resource_id):
        """Check if user can review a resource (hasn't reviewed yet)."""
        existing = Review.query.filter_by(
            resource_id=resource_id,
            reviewer_id=user_id
        ).first()
        return existing is None
