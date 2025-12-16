"""
Data Access Layer for Review operations.

Handles all database operations related to reviews and ratings.
"""

from src.models.database import get_db_connection
from datetime import datetime


class ReviewDAL:
    """Data Access Layer for Review entity."""
    
    @staticmethod
    def create_review(resource_id, reviewer_id, rating, comment=None, booking_id=None):
        """
        Create a new review for a resource.
        
        Args:
            resource_id (int): ID of resource being reviewed
            reviewer_id (int): ID of user creating review
            rating (int): Rating from 1 to 5
            comment (str, optional): Review text
            booking_id (int, optional): Associated booking ID
            
        Returns:
            int: ID of newly created review
            
        Raises:
            ValueError: If rating is not between 1 and 5
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reviews (resource_id, reviewer_id, rating, comment, booking_id)
            VALUES (?, ?, ?, ?, ?)
        """, (resource_id, reviewer_id, rating, comment, booking_id))
        
        review_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return review_id
    
    @staticmethod
    def get_review_by_id(review_id):
        """
        Retrieve a review by ID.
        
        Args:
            review_id (int): Review ID
            
        Returns:
            sqlite3.Row: Review record with reviewer info
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.*, u.name as reviewer_name
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.user_id
            WHERE r.review_id = ?
        """, (review_id,))
        
        review = cursor.fetchone()
        conn.close()
        
        return review
    
    @staticmethod
    def get_reviews_for_resource(resource_id, include_hidden=False):
        """
        Get all reviews for a specific resource.
        
        Args:
            resource_id (int): Resource ID
            include_hidden (bool): Whether to include hidden reviews
            
        Returns:
            list: List of reviews with reviewer information
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT r.*, u.name as reviewer_name, u.profile_image as reviewer_image
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.user_id
            WHERE r.resource_id = ?
        """
        
        if not include_hidden:
            query += " AND r.is_hidden = 0"
        
        query += " ORDER BY r.timestamp DESC"
        
        cursor.execute(query, (resource_id,))
        reviews = cursor.fetchall()
        conn.close()
        
        return reviews
    
    @staticmethod
    def get_reviews_by_user(reviewer_id):
        """
        Get all reviews written by a specific user.
        
        Args:
            reviewer_id (int): User ID
            
        Returns:
            list: List of reviews with resource information
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.*, res.title as resource_title
            FROM reviews r
            JOIN resources res ON r.resource_id = res.resource_id
            WHERE r.reviewer_id = ?
            ORDER BY r.timestamp DESC
        """, (reviewer_id,))
        
        reviews = cursor.fetchall()
        conn.close()
        
        return reviews
    
    @staticmethod
    def get_average_rating(resource_id):
        """
        Calculate average rating for a resource.
        
        Args:
            resource_id (int): Resource ID
            
        Returns:
            dict: Average rating and count
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                AVG(rating) as avg_rating,
                COUNT(*) as review_count
            FROM reviews
            WHERE resource_id = ? AND is_hidden = 0
        """, (resource_id,))
        
        result = dict(cursor.fetchone())
        conn.close()
        
        # Format average to 1 decimal place
        if result['avg_rating']:
            result['avg_rating'] = round(result['avg_rating'], 1)
        else:
            result['avg_rating'] = 0
        
        return result
    
    @staticmethod
    def can_user_review(reviewer_id, resource_id):
        """
        Check if a user can leave a review for a resource.
        User must have a completed booking and not already reviewed it.
        
        Args:
            reviewer_id (int): User ID
            resource_id (int): Resource ID
            
        Returns:
            bool: True if user can review
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for completed booking
        cursor.execute("""
            SELECT COUNT(*) as booking_count
            FROM bookings
            WHERE requester_id = ? 
              AND resource_id = ? 
              AND status = 'completed'
        """, (reviewer_id, resource_id))
        
        has_booking = cursor.fetchone()['booking_count'] > 0
        
        if not has_booking:
            conn.close()
            return False
        
        # Check if already reviewed
        cursor.execute("""
            SELECT COUNT(*) as review_count
            FROM reviews
            WHERE reviewer_id = ? AND resource_id = ?
        """, (reviewer_id, resource_id))
        
        already_reviewed = cursor.fetchone()['review_count'] > 0
        conn.close()
        
        return not already_reviewed
    
    @staticmethod
    def update_review(review_id, rating=None, comment=None):
        """
        Update a review.
        
        Args:
            review_id (int): Review ID
            rating (int, optional): New rating
            comment (str, optional): New comment
            
        Returns:
            bool: True if update successful
        """
        updates = {}
        if rating is not None:
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            updates['rating'] = rating
        if comment is not None:
            updates['comment'] = comment
        
        if not updates:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        values = list(updates.values()) + [review_id]
        
        cursor.execute(f"UPDATE reviews SET {set_clause} WHERE review_id = ?", values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def hide_review(review_id, hide=True):
        """
        Hide or unhide a review (admin moderation).
        
        Args:
            review_id (int): Review ID
            hide (bool): True to hide, False to unhide
            
        Returns:
            bool: True if update successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reviews SET is_hidden = ? WHERE review_id = ?
        """, (1 if hide else 0, review_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def delete_review(review_id):
        """
        Delete a review.
        
        Args:
            review_id (int): Review ID
            
        Returns:
            bool: True if deletion successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM reviews WHERE review_id = ?", (review_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def get_top_rated_resources(limit=10):
        """
        Get top-rated resources.
        
        Args:
            limit (int): Maximum number of resources to return
            
        Returns:
            list: List of resources with ratings
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                res.*,
                AVG(r.rating) as avg_rating,
                COUNT(r.review_id) as review_count
            FROM resources res
            JOIN reviews r ON res.resource_id = r.resource_id
            WHERE res.status = 'published' AND r.is_hidden = 0
            GROUP BY res.resource_id
            HAVING review_count >= 3
            ORDER BY avg_rating DESC, review_count DESC
            LIMIT ?
        """, (limit,))
        
        resources = cursor.fetchall()
        conn.close()
        
        return resources

