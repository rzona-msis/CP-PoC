"""
Waitlist Data Access Layer
Handles all database operations related to resource waitlists
"""

from src.models.database import get_db_connection
from datetime import datetime


class WaitlistDAL:
    """Data access layer for waitlist operations"""
    
    @staticmethod
    def join_waitlist(resource_id, user_id, requested_datetime):
        """
        Add a user to the waitlist for a resource.
        
        Args:
            resource_id: ID of the resource
            user_id: ID of the user joining waitlist
            requested_datetime: Datetime they want to book
            
        Returns:
            waitlist_id: ID of the created waitlist entry
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user is already on waitlist for this resource/time
        cursor.execute("""
            SELECT waitlist_id FROM waitlist
            WHERE resource_id = ? AND user_id = ? AND requested_datetime = ? AND status = 'waiting'
        """, (resource_id, user_id, requested_datetime))
        
        if cursor.fetchone():
            conn.close()
            raise ValueError("You're already on the waitlist for this time slot")
        
        # Add to waitlist
        cursor.execute("""
            INSERT INTO waitlist (resource_id, user_id, requested_datetime, status, priority)
            VALUES (?, ?, ?, 'waiting', 0)
        """, (resource_id, user_id, requested_datetime))
        
        waitlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return waitlist_id
    
    @staticmethod
    def leave_waitlist(waitlist_id, user_id):
        """
        Remove a user from the waitlist.
        
        Args:
            waitlist_id: ID of the waitlist entry
            user_id: ID of the user (for verification)
            
        Returns:
            bool: True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM waitlist
            WHERE waitlist_id = ? AND user_id = ?
        """, (waitlist_id, user_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    @staticmethod
    def get_waitlist_for_resource(resource_id, requested_datetime=None):
        """
        Get all users on waitlist for a resource.
        
        Args:
            resource_id: ID of the resource
            requested_datetime: Optional - filter by specific datetime
            
        Returns:
            list: List of waitlist entries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if requested_datetime:
            cursor.execute("""
                SELECT w.*, u.name, u.email
                FROM waitlist w
                JOIN users u ON w.user_id = u.user_id
                WHERE w.resource_id = ? AND w.requested_datetime = ? AND w.status = 'waiting'
                ORDER BY w.priority DESC, w.created_at ASC
            """, (resource_id, requested_datetime))
        else:
            cursor.execute("""
                SELECT w.*, u.name, u.email
                FROM waitlist w
                JOIN users u ON w.user_id = u.user_id
                WHERE w.resource_id = ? AND w.status = 'waiting'
                ORDER BY w.requested_datetime ASC, w.priority DESC, w.created_at ASC
            """, (resource_id,))
        
        waitlist = cursor.fetchall()
        conn.close()
        
        return [dict(entry) for entry in waitlist]
    
    @staticmethod
    def get_user_waitlists(user_id):
        """
        Get all waitlist entries for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            list: List of waitlist entries with resource details
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT w.*, r.title, r.location, r.category
            FROM waitlist w
            JOIN resources r ON w.resource_id = r.resource_id
            WHERE w.user_id = ? AND w.status = 'waiting'
            ORDER BY w.requested_datetime ASC
        """, (user_id,))
        
        waitlist = cursor.fetchall()
        conn.close()
        
        return [dict(entry) for entry in waitlist]
    
    @staticmethod
    def get_waitlist_position(waitlist_id):
        """
        Get position of a user in the waitlist queue.
        
        Args:
            waitlist_id: ID of the waitlist entry
            
        Returns:
            int: Position in queue (1-indexed)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the waitlist entry
        cursor.execute("""
            SELECT resource_id, requested_datetime, priority, created_at
            FROM waitlist
            WHERE waitlist_id = ?
        """, (waitlist_id,))
        
        entry = cursor.fetchone()
        if not entry:
            conn.close()
            return 0
        
        resource_id, requested_datetime, priority, created_at = entry
        
        # Count how many are ahead in queue
        cursor.execute("""
            SELECT COUNT(*) FROM waitlist
            WHERE resource_id = ? 
            AND requested_datetime = ?
            AND status = 'waiting'
            AND (priority > ? OR (priority = ? AND created_at < ?))
        """, (resource_id, requested_datetime, priority, priority, created_at))
        
        position = cursor.fetchone()[0] + 1
        conn.close()
        
        return position
    
    @staticmethod
    def notify_next_in_waitlist(resource_id, requested_datetime):
        """
        Notify the next person in waitlist that a spot is available.
        
        Args:
            resource_id: ID of the resource
            requested_datetime: Datetime that became available
            
        Returns:
            dict: Next waitlist entry, or None if waitlist is empty
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the next person in line
        cursor.execute("""
            SELECT w.*, u.name, u.email
            FROM waitlist w
            JOIN users u ON w.user_id = u.user_id
            WHERE w.resource_id = ? AND w.requested_datetime = ? AND w.status = 'waiting'
            ORDER BY w.priority DESC, w.created_at ASC
            LIMIT 1
        """, (resource_id, requested_datetime))
        
        next_person = cursor.fetchone()
        
        if next_person:
            # Mark as notified
            cursor.execute("""
                UPDATE waitlist
                SET status = 'notified', notified_at = ?
                WHERE waitlist_id = ?
            """, (datetime.now().isoformat(), next_person['waitlist_id']))
            
            conn.commit()
            conn.close()
            
            return dict(next_person)
        
        conn.close()
        return None
    
    @staticmethod
    def mark_as_converted(waitlist_id):
        """
        Mark a waitlist entry as converted to a booking.
        
        Args:
            waitlist_id: ID of the waitlist entry
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE waitlist
            SET status = 'converted'
            WHERE waitlist_id = ?
        """, (waitlist_id,))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def expire_old_waitlist_entries(days=30):
        """
        Mark old waitlist entries as expired.
        
        Args:
            days: Number of days after which to expire entries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE waitlist
            SET status = 'expired'
            WHERE status = 'waiting' 
            AND datetime(created_at, '+' || ? || ' days') < datetime('now')
        """, (days,))
        
        expired_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return expired_count
    
    @staticmethod
    def get_waitlist_count_for_resource(resource_id, requested_datetime=None):
        """
        Get count of waiting users for a resource.
        
        Args:
            resource_id: ID of the resource
            requested_datetime: Optional - filter by specific datetime
            
        Returns:
            int: Number of people waiting
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if requested_datetime:
            cursor.execute("""
                SELECT COUNT(*) FROM waitlist
                WHERE resource_id = ? AND requested_datetime = ? AND status = 'waiting'
            """, (resource_id, requested_datetime))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM waitlist
                WHERE resource_id = ? AND status = 'waiting'
            """, (resource_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    @staticmethod
    def is_user_on_waitlist(user_id, resource_id, requested_datetime):
        """
        Check if user is already on waitlist for a specific resource/time.
        
        Args:
            user_id: ID of the user
            resource_id: ID of the resource
            requested_datetime: Datetime they want
            
        Returns:
            bool: True if already on waitlist
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT waitlist_id FROM waitlist
            WHERE user_id = ? AND resource_id = ? AND requested_datetime = ? AND status = 'waiting'
        """, (user_id, resource_id, requested_datetime))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None

