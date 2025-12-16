"""
Data Access Layer for Analytics operations.

Provides SQL queries and calculations for daily booking analytics,
resource usage tracking, and operational metrics.
"""

from src.models.database import get_db_connection
from datetime import datetime, timedelta


class AnalyticsDAL:
    """Data Access Layer for Analytics."""
    
    @staticmethod
    def get_daily_booking_metrics(days=30):
        """
        Get daily booking counts and trends.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            dict: Daily booking metrics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Total bookings in period
        cursor.execute("""
            SELECT COUNT(*) as total_bookings
            FROM bookings
            WHERE DATE(created_at) >= DATE(?)
        """, (start_date.strftime('%Y-%m-%d'),))
        total_bookings = cursor.fetchone()['total_bookings']
        
        # Today's bookings
        cursor.execute("""
            SELECT COUNT(*) as today_bookings
            FROM bookings
            WHERE DATE(created_at) = DATE('now')
        """)
        today_bookings = cursor.fetchone()['today_bookings']
        
        # This week's bookings
        cursor.execute("""
            SELECT COUNT(*) as week_bookings
            FROM bookings
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        """)
        week_bookings = cursor.fetchone()['week_bookings']
        
        # Bookings by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM bookings
            WHERE DATE(created_at) >= DATE(?)
            GROUP BY status
        """, (start_date.strftime('%Y-%m-%d'),))
        bookings_by_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Average bookings per day
        cursor.execute("""
            SELECT AVG(daily_count) as avg_per_day
            FROM (
                SELECT DATE(created_at) as booking_date, COUNT(*) as daily_count
                FROM bookings
                WHERE DATE(created_at) >= DATE(?)
                GROUP BY DATE(created_at)
            )
        """, (start_date.strftime('%Y-%m-%d'),))
        avg_per_day = cursor.fetchone()['avg_per_day'] or 0
        
        conn.close()
        
        return {
            'total_bookings': total_bookings,
            'today_bookings': today_bookings,
            'week_bookings': week_bookings,
            'bookings_by_status': bookings_by_status,
            'avg_per_day': round(avg_per_day, 1),
            'period_days': days
        }
    
    @staticmethod
    def get_booking_timeline(days=30):
        """
        Get booking counts per day for timeline visualization.
        
        Args:
            days (int): Number of days to include
            
        Returns:
            list: Daily booking counts with dates
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM bookings
            WHERE DATE(created_at) >= DATE(?)
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (start_date.strftime('%Y-%m-%d'),))
        
        timeline = [{'date': row['date'], 'count': row['count']} for row in cursor.fetchall()]
        conn.close()
        
        return timeline
    
    @staticmethod
    def get_resource_usage_stats():
        """
        Get resource usage statistics.
        
        Returns:
            list: Resource usage metrics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                r.resource_id,
                r.title,
                r.category,
                COUNT(b.booking_id) as booking_count,
                SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count,
                AVG(CAST((julianday(b.end_datetime) - julianday(b.start_datetime)) * 24 AS REAL)) as avg_duration_hours
            FROM resources r
            LEFT JOIN bookings b ON r.resource_id = b.resource_id
            WHERE r.status = 'published'
            GROUP BY r.resource_id, r.title, r.category
            ORDER BY booking_count DESC
        """)
        
        stats = []
        for row in cursor.fetchall():
            stats.append({
                'resource_id': row['resource_id'],
                'title': row['title'],
                'category': row['category'],
                'booking_count': row['booking_count'],
                'completed_count': row['completed_count'],
                'cancelled_count': row['cancelled_count'],
                'avg_duration_hours': round(row['avg_duration_hours'], 1) if row['avg_duration_hours'] else 0,
                'cancellation_rate': round((row['cancelled_count'] / row['booking_count'] * 100), 1) if row['booking_count'] > 0 else 0
            })
        
        conn.close()
        return stats
    
    @staticmethod
    def get_peak_hours_data():
        """
        Get booking distribution by hour of day.
        
        Returns:
            dict: Booking counts by hour
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CAST(strftime('%H', start_datetime) AS INTEGER) as hour,
                COUNT(*) as count
            FROM bookings
            WHERE DATE(created_at) >= DATE('now', '-30 days')
            GROUP BY hour
            ORDER BY hour
        """)
        
        hours_data = {row['hour']: row['count'] for row in cursor.fetchall()}
        conn.close()
        
        # Fill in missing hours with 0
        return {hour: hours_data.get(hour, 0) for hour in range(24)}
    
    @staticmethod
    def get_day_of_week_distribution():
        """
        Get booking distribution by day of week.
        
        Returns:
            dict: Booking counts by day of week
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE CAST(strftime('%w', start_datetime) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_name,
                COUNT(*) as count
            FROM bookings
            WHERE DATE(created_at) >= DATE('now', '-30 days')
            GROUP BY day_name
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return {row['day_name']: row['count'] for row in results}
    
    @staticmethod
    def get_user_activity_stats():
        """
        Get user activity statistics.
        
        Returns:
            dict: User activity metrics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Active users today
        cursor.execute("""
            SELECT COUNT(DISTINCT requester_id) as active_today
            FROM bookings
            WHERE DATE(created_at) = DATE('now')
        """)
        active_today = cursor.fetchone()['active_today']
        
        # Active users this week
        cursor.execute("""
            SELECT COUNT(DISTINCT requester_id) as active_week
            FROM bookings
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        """)
        active_week = cursor.fetchone()['active_week']
        
        # New registrations this week
        cursor.execute("""
            SELECT COUNT(*) as new_users
            FROM users
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        """)
        new_users = cursor.fetchone()['new_users']
        
        # Department breakdown
        cursor.execute("""
            SELECT 
                u.department,
                COUNT(DISTINCT b.booking_id) as booking_count
            FROM users u
            LEFT JOIN bookings b ON u.user_id = b.requester_id
            WHERE u.department IS NOT NULL
                AND DATE(b.created_at) >= DATE('now', '-30 days')
            GROUP BY u.department
            ORDER BY booking_count DESC
            LIMIT 5
        """)
        dept_breakdown = [{'department': row['department'], 'count': row['booking_count']} 
                         for row in cursor.fetchall()]
        
        # Role distribution
        cursor.execute("""
            SELECT 
                u.role,
                COUNT(DISTINCT b.booking_id) as booking_count
            FROM users u
            LEFT JOIN bookings b ON u.user_id = b.requester_id
            WHERE DATE(b.created_at) >= DATE('now', '-30 days')
            GROUP BY u.role
        """)
        role_breakdown = {row['role']: row['booking_count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'active_today': active_today,
            'active_week': active_week,
            'new_users': new_users,
            'dept_breakdown': dept_breakdown,
            'role_breakdown': role_breakdown
        }
    
    @staticmethod
    def get_operational_insights():
        """
        Get operational insights and KPIs.
        
        Returns:
            dict: Operational metrics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Average approval time (for resources that require approval)
        cursor.execute("""
            SELECT AVG(CAST((julianday(b.updated_at) - julianday(b.created_at)) * 24 AS REAL)) as avg_approval_hours
            FROM bookings b
            JOIN resources r ON b.resource_id = r.resource_id
            WHERE b.status IN ('approved', 'rejected')
                AND r.requires_approval = 1
                AND DATE(b.created_at) >= DATE('now', '-30 days')
        """)
        result = cursor.fetchone()
        avg_approval_hours = result['avg_approval_hours'] if result['avg_approval_hours'] else 0
        
        # Cancellation rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM bookings
            WHERE DATE(created_at) >= DATE('now', '-30 days')
        """)
        result = cursor.fetchone()
        cancellation_rate = (result['cancelled'] / result['total'] * 100) if result['total'] > 0 else 0
        
        # Waitlist metrics
        cursor.execute("""
            SELECT COUNT(*) as waiting_count
            FROM waitlist
            WHERE status = 'waiting'
        """)
        waiting_count = cursor.fetchone()['waiting_count']
        
        # Messages sent
        cursor.execute("""
            SELECT COUNT(*) as message_count
            FROM messages
            WHERE DATE(timestamp) >= DATE('now', '-30 days')
        """)
        message_count = cursor.fetchone()['message_count']
        
        # Reviews submitted
        cursor.execute("""
            SELECT COUNT(*) as review_count
            FROM reviews
            WHERE DATE(timestamp) >= DATE('now', '-30 days')
        """)
        review_count = cursor.fetchone()['review_count']
        
        conn.close()
        
        return {
            'avg_approval_hours': round(avg_approval_hours, 1),
            'cancellation_rate': round(cancellation_rate, 1),
            'waiting_count': waiting_count,
            'message_count': message_count,
            'review_count': review_count
        }
    
    @staticmethod
    def get_booking_lead_time_stats():
        """
        Get statistics on how far in advance users book.
        
        Returns:
            dict: Lead time statistics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                AVG(CAST((julianday(start_datetime) - julianday(created_at)) AS REAL)) as avg_lead_days,
                MIN(CAST((julianday(start_datetime) - julianday(created_at)) AS REAL)) as min_lead_days,
                MAX(CAST((julianday(start_datetime) - julianday(created_at)) AS REAL)) as max_lead_days
            FROM bookings
            WHERE DATE(created_at) >= DATE('now', '-30 days')
                AND start_datetime > created_at
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'avg_lead_days': round(result['avg_lead_days'], 1) if result['avg_lead_days'] else 0,
            'min_lead_days': round(result['min_lead_days'], 1) if result['min_lead_days'] else 0,
            'max_lead_days': round(result['max_lead_days'], 1) if result['max_lead_days'] else 0
        }

