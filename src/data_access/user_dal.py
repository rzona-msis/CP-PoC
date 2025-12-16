"""
Data Access Layer for User operations.

This module encapsulates all database operations related to users,
following the Data Access Layer (DAL) pattern to separate business logic
from database interactions.
"""
# AI Contribution: Cursor AI generated initial CRUD patterns; team reviewed for security

from src.models.database import get_db_connection
from datetime import datetime
import bcrypt


class UserDAL:
    """Data Access Layer for User entity."""
    
    @staticmethod
    def create_user(name, email, password, role='student', department=None, profile_image=None):
        """
        Create a new user with hashed password.
        
        Args:
            name (str): User's full name
            email (str): User's email address (must be unique)
            password (str): Plain text password (will be hashed)
            role (str): User role - 'student', 'staff', or 'admin'
            department (str, optional): User's department
            profile_image (str, optional): Path to profile image
            
        Returns:
            int: ID of newly created user
            
        Raises:
            sqlite3.IntegrityError: If email already exists
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash password with bcrypt (12 rounds)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, department, profile_image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, password_hash, role, department, profile_image))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a user by their ID.
        
        Args:
            user_id (int): User ID
            
        Returns:
            sqlite3.Row: User record or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    @staticmethod
    def get_user_by_email(email):
        """
        Retrieve a user by their email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            sqlite3.Row: User record or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    @staticmethod
    def verify_password(email, password):
        """
        Verify user credentials and return user record if valid.
        
        Args:
            email (str): User's email address
            password (str): Plain text password to verify
            
        Returns:
            sqlite3.Row: User record if credentials valid, None otherwise
        """
        user = UserDAL.get_user_by_email(email)
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user
        
        return None
    
    @staticmethod
    def get_all_users(role=None):
        """
        Retrieve all users, optionally filtered by role.
        
        Args:
            role (str, optional): Filter by role ('student', 'staff', 'admin')
            
        Returns:
            list: List of user records
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if role:
            cursor.execute("SELECT * FROM users WHERE role = ? ORDER BY created_at DESC", (role,))
        else:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        
        users = cursor.fetchall()
        conn.close()
        
        return users
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """
        Update user fields.
        
        Args:
            user_id (int): User ID
            **kwargs: Fields to update (name, email, department, profile_image, role)
            
        Returns:
            bool: True if update successful, False otherwise
        """
        allowed_fields = ['name', 'email', 'department', 'profile_image', 'role']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [user_id]
        
        cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def update_password(user_id, new_password):
        """
        Update user's password.
        
        Args:
            user_id (int): User ID
            new_password (str): New plain text password (will be hashed)
            
        Returns:
            bool: True if update successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (password_hash, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def delete_user(user_id):
        """
        Delete a user (soft delete recommended in production).
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if deletion successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def get_user_statistics():
        """
        Get user statistics for admin dashboard.
        
        Returns:
            dict: Statistics including counts by role
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as students,
                SUM(CASE WHEN role = 'staff' THEN 1 ELSE 0 END) as staff,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admins
            FROM users
        """)
        
        stats = dict(cursor.fetchone())
        conn.close()
        
        return stats
    
    @staticmethod
    def update_user_calendar_tokens(user_id, token, refresh_token, token_expiry):
        """
        Update user's Google Calendar tokens.
        
        Args:
            user_id (int): User ID
            token (str): Access token
            refresh_token (str): Refresh token
            token_expiry (str): Token expiry datetime (ISO format)
            
        Returns:
            bool: True if update successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET google_calendar_token = ?,
                google_calendar_refresh_token = ?,
                google_calendar_token_expiry = ?
            WHERE user_id = ?
        """, (token, refresh_token, token_expiry, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def disconnect_user_calendar(user_id):
        """
        Remove user's Google Calendar tokens.
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if update successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET google_calendar_token = NULL,
                google_calendar_refresh_token = NULL,
                google_calendar_token_expiry = NULL
            WHERE user_id = ?
        """, (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def has_calendar_connected(user_id):
        """
        Check if user has connected their Google Calendar.
        
        Args:
            user_id (int): User ID
            
        Returns:
            bool: True if calendar is connected
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT google_calendar_token 
            FROM users 
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result and result['google_calendar_token'] is not None


# Module-level convenience functions
create_user = UserDAL.create_user
get_user_by_id = UserDAL.get_user_by_id
get_user_by_email = UserDAL.get_user_by_email
verify_password = UserDAL.verify_password
get_all_users = UserDAL.get_all_users
update_user = UserDAL.update_user
update_password = UserDAL.update_password
delete_user = UserDAL.delete_user
get_user_statistics = UserDAL.get_user_statistics
update_user_calendar_tokens = UserDAL.update_user_calendar_tokens
disconnect_user_calendar = UserDAL.disconnect_user_calendar
has_calendar_connected = UserDAL.has_calendar_connected
