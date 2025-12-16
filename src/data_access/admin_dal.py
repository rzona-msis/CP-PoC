"""
Data Access Layer for Admin operations.

Handles administrative functions including audit logging and system statistics.
"""

from src.models.database import get_db_connection
from datetime import datetime, timedelta


class AdminDAL:
    """Data Access Layer for Admin operations."""
    
    @staticmethod
    def log_action(admin_id, action, target_table=None, target_id=None, details=None):
        """
        Log an administrative action.
        
        Args:
            admin_id (int): ID of admin performing action
            action (str): Description of action taken
            target_table (str, optional): Table affected
            target_id (int, optional): ID of record affected
            details (str, optional): Additional details
            
        Returns:
            int: ID of log entry
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, target_table, target_id, details)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_id, action, target_table, target_id, details))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    @staticmethod
    def get_recent_logs(limit=50, admin_id=None):
        """
        Retrieve recent admin logs.
        
        Args:
            limit (int): Maximum number of logs to return
            admin_id (int, optional): Filter by specific admin
            
        Returns:
            list: List of log entries with admin info
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT l.*, u.name as admin_name
            FROM admin_logs l
            JOIN users u ON l.admin_id = u.user_id
        """
        params = []
        
        if admin_id:
            query += " WHERE l.admin_id = ?"
            params.append(admin_id)
        
        query += " ORDER BY l.timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()
        
        return logs
    
    @staticmethod
    def get_system_statistics():
        """
        Get comprehensive system statistics for admin dashboard.
        
        Returns:
            dict: System-wide statistics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # User statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as students,
                SUM(CASE WHEN role = 'staff' THEN 1 ELSE 0 END) as staff,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admins
            FROM users
        """)
        stats['users'] = dict(cursor.fetchone())
        
        # Resource statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_resources,
                SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published,
                SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as draft,
                SUM(CASE WHEN status = 'archived' THEN 1 ELSE 0 END) as archived
            FROM resources
        """)
        stats['resources'] = dict(cursor.fetchone())
        
        # Booking statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM bookings
        """)
        stats['bookings'] = dict(cursor.fetchone())
        
        # Review statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as average_rating,
                SUM(CASE WHEN is_hidden = 1 THEN 1 ELSE 0 END) as hidden_reviews
            FROM reviews
        """)
        review_stats = dict(cursor.fetchone())
        if review_stats['average_rating']:
            review_stats['average_rating'] = round(review_stats['average_rating'], 2)
        stats['reviews'] = review_stats
        
        # Message statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_messages,
                SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_messages
            FROM messages
        """)
        stats['messages'] = dict(cursor.fetchone())
        
        # Activity in last 7 days
        cursor.execute("""
            SELECT 
                COUNT(*) as new_users
            FROM users
            WHERE created_at >= datetime('now', '-7 days')
        """)
        stats['recent_users'] = cursor.fetchone()['new_users']
        
        cursor.execute("""
            SELECT 
                COUNT(*) as new_bookings
            FROM bookings
            WHERE created_at >= datetime('now', '-7 days')
        """)
        stats['recent_bookings'] = cursor.fetchone()['new_bookings']
        
        conn.close()
        return stats
    
    @staticmethod
    def get_flagged_content():
        """
        Get content that may need moderation.
        
        Returns:
            dict: Lists of potentially problematic content
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        content = {}
        
        # Get reviews with low ratings (1-2 stars) - may indicate problems
        cursor.execute("""
            SELECT r.*, 
                   res.title as resource_title,
                   u.name as reviewer_name
            FROM reviews r
            JOIN resources res ON r.resource_id = res.resource_id
            JOIN users u ON r.reviewer_id = u.user_id
            WHERE r.rating <= 2 AND r.is_hidden = 0
            ORDER BY r.timestamp DESC
            LIMIT 20
        """)
        content['low_rated_reviews'] = cursor.fetchall()
        
        # Get resources with no bookings (may need attention)
        cursor.execute("""
            SELECT r.*
            FROM resources r
            LEFT JOIN bookings b ON r.resource_id = b.resource_id
            WHERE r.status = 'published'
            GROUP BY r.resource_id
            HAVING COUNT(b.booking_id) = 0
            ORDER BY r.created_at DESC
            LIMIT 10
        """)
        content['unused_resources'] = cursor.fetchall()
        
        # Get users with many rejected bookings
        cursor.execute("""
            SELECT u.*, COUNT(b.booking_id) as rejected_count
            FROM users u
            JOIN bookings b ON u.user_id = b.requester_id
            WHERE b.status = 'rejected'
            GROUP BY u.user_id
            HAVING rejected_count >= 3
            ORDER BY rejected_count DESC
            LIMIT 10
        """)
        content['users_with_rejections'] = cursor.fetchall()
        
        conn.close()
        return content
    
    @staticmethod
    def get_usage_report(start_date=None, end_date=None):
        """
        Generate usage report for a date range.
        
        Args:
            start_date (str, optional): Start date (ISO format)
            end_date (str, optional): End date (ISO format)
            
        Returns:
            dict: Usage metrics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Default to last 30 days if not specified
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        if not end_date:
            end_date = datetime.now().isoformat()
        
        report = {}
        
        # Bookings by status in date range
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM bookings
            WHERE created_at BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))
        report['bookings_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Most booked resources
        cursor.execute("""
            SELECT r.resource_id, r.title, COUNT(b.booking_id) as booking_count
            FROM resources r
            JOIN bookings b ON r.resource_id = b.resource_id
            WHERE b.created_at BETWEEN ? AND ?
            GROUP BY r.resource_id
            ORDER BY booking_count DESC
            LIMIT 10
        """, (start_date, end_date))
        report['most_booked_resources'] = cursor.fetchall()
        
        # Most active users (by bookings)
        cursor.execute("""
            SELECT u.user_id, u.name, u.role, COUNT(b.booking_id) as booking_count
            FROM users u
            JOIN bookings b ON u.user_id = b.requester_id
            WHERE b.created_at BETWEEN ? AND ?
            GROUP BY u.user_id
            ORDER BY booking_count DESC
            LIMIT 10
        """, (start_date, end_date))
        report['most_active_users'] = cursor.fetchall()
        
        # Bookings by category
        cursor.execute("""
            SELECT r.category, COUNT(b.booking_id) as booking_count
            FROM resources r
            JOIN bookings b ON r.resource_id = b.resource_id
            WHERE b.created_at BETWEEN ? AND ?
            GROUP BY r.category
            ORDER BY booking_count DESC
        """, (start_date, end_date))
        report['bookings_by_category'] = cursor.fetchall()
        
        conn.close()
        return report

