"""
Data Access Layer for Message operations.

Handles all database operations related to messaging between users.
"""

from src.models.database import get_db_connection
from datetime import datetime


class MessageDAL:
    """Data Access Layer for Message entity."""
    
    @staticmethod
    def send_message(sender_id, receiver_id, content, booking_id=None, thread_id=None):
        """
        Send a message from one user to another.
        
        Args:
            sender_id (int): ID of user sending message
            receiver_id (int): ID of user receiving message
            content (str): Message content
            booking_id (int, optional): Related booking ID
            thread_id (str, optional): Conversation thread ID
            
        Returns:
            int: ID of newly created message
        """
        # Generate thread_id if not provided
        if not thread_id:
            thread_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
            if booking_id:
                thread_id += f"_b{booking_id}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (thread_id, sender_id, receiver_id, booking_id, content)
            VALUES (?, ?, ?, ?, ?)
        """, (thread_id, sender_id, receiver_id, booking_id, content))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return message_id
    
    @staticmethod
    def get_message_by_id(message_id):
        """
        Retrieve a message by ID.
        
        Args:
            message_id (int): Message ID
            
        Returns:
            sqlite3.Row: Message record
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*,
                   s.name as sender_name,
                   r.name as receiver_name
            FROM messages m
            JOIN users s ON m.sender_id = s.user_id
            JOIN users r ON m.receiver_id = r.user_id
            WHERE m.message_id = ?
        """, (message_id,))
        
        message = cursor.fetchone()
        conn.close()
        
        return message
    
    @staticmethod
    def get_thread_messages(thread_id):
        """
        Get all messages in a conversation thread.
        
        Args:
            thread_id (str): Thread identifier
            
        Returns:
            list: List of messages in chronological order
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*,
                   s.name as sender_name,
                   r.name as receiver_name
            FROM messages m
            JOIN users s ON m.sender_id = s.user_id
            JOIN users r ON m.receiver_id = r.user_id
            WHERE m.thread_id = ?
            ORDER BY m.timestamp
        """, (thread_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return messages
    
    @staticmethod
    def get_user_threads(user_id):
        """
        Get all conversation threads for a user with latest message.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of threads with latest message and unread count
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                m.thread_id,
                MAX(m.timestamp) as last_message_time,
                (SELECT content FROM messages WHERE thread_id = m.thread_id ORDER BY timestamp DESC LIMIT 1) as last_message,
                (SELECT name FROM users WHERE user_id = 
                    CASE WHEN m.sender_id = ? THEN m.receiver_id ELSE m.sender_id END) as other_user_name,
                (SELECT user_id FROM users WHERE user_id = 
                    CASE WHEN m.sender_id = ? THEN m.receiver_id ELSE m.sender_id END) as other_user_id,
                SUM(CASE WHEN m.receiver_id = ? AND m.is_read = 0 THEN 1 ELSE 0 END) as unread_count
            FROM messages m
            WHERE m.sender_id = ? OR m.receiver_id = ?
            GROUP BY m.thread_id
            ORDER BY last_message_time DESC
        """, (user_id, user_id, user_id, user_id, user_id))
        
        threads = cursor.fetchall()
        conn.close()
        
        return threads
    
    @staticmethod
    def mark_as_read(thread_id, user_id):
        """
        Mark all messages in a thread as read for a specific user.
        
        Args:
            thread_id (str): Thread identifier
            user_id (int): User ID (receiver)
            
        Returns:
            int: Number of messages marked as read
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages
            SET is_read = 1
            WHERE thread_id = ? AND receiver_id = ? AND is_read = 0
        """, (thread_id, user_id))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    @staticmethod
    def get_unread_count(user_id):
        """
        Get count of unread messages for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            int: Number of unread messages
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as unread_count
            FROM messages
            WHERE receiver_id = ? AND is_read = 0
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['unread_count']
    
    @staticmethod
    def delete_message(message_id):
        """
        Delete a message.
        
        Args:
            message_id (int): Message ID
            
        Returns:
            bool: True if deletion successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

