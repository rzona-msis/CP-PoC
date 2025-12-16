"""
Message Data Access Layer
Campus Resource Hub - AiDD 2025 Capstone

CRUD operations for Message model with thread management.
"""

from app import db
from app.models import Message

class MessageDAL:
    """Data Access Layer for Message operations."""
    
    @staticmethod
    def send_message(sender_id, receiver_id, content, thread_id=None):
        """Send a message."""
        # Generate thread_id if not provided
        if not thread_id:
            thread_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            thread_id=thread_id
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    @staticmethod
    def get_message_by_id(message_id):
        """Get message by ID."""
        return Message.query.get(message_id)
    
    @staticmethod
    def get_thread_messages(thread_id):
        """Get all messages in a thread."""
        return Message.query.filter_by(thread_id=thread_id).order_by(Message.timestamp).all()
    
    @staticmethod
    def get_conversation(user1_id, user2_id):
        """Get all messages between two users."""
        thread_id = f"{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
        return MessageDAL.get_thread_messages(thread_id)
    
    @staticmethod
    def get_user_inbox(user_id):
        """Get all messages received by a user, grouped by thread."""
        return Message.query.filter_by(receiver_id=user_id).order_by(Message.timestamp.desc()).all()
    
    @staticmethod
    def get_user_sent_messages(user_id):
        """Get all messages sent by a user."""
        return Message.query.filter_by(sender_id=user_id).order_by(Message.timestamp.desc()).all()
    
    @staticmethod
    def get_unread_messages(user_id):
        """Get all unread messages for a user."""
        return Message.query.filter_by(receiver_id=user_id, is_read=False).all()
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread messages for a user."""
        return Message.query.filter_by(receiver_id=user_id, is_read=False).count()
    
    @staticmethod
    def mark_as_read(message_id):
        """Mark a message as read."""
        message = Message.query.get(message_id)
        if not message:
            return None
        
        message.mark_as_read()
        db.session.commit()
        return message
    
    @staticmethod
    def mark_thread_as_read(thread_id, user_id):
        """Mark all messages in a thread as read for a user."""
        messages = Message.query.filter_by(thread_id=thread_id, receiver_id=user_id, is_read=False).all()
        for message in messages:
            message.mark_as_read()
        db.session.commit()
        return len(messages)
    
    @staticmethod
    def delete_message(message_id):
        """Delete a message."""
        message = Message.query.get(message_id)
        if not message:
            return False
        
        db.session.delete(message)
        db.session.commit()
        return True
