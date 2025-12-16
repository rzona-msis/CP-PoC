"""
Message Model
Campus Resource Hub - AiDD 2025 Capstone

Represents messages between users.
"""

from datetime import datetime
from app import db

class Message(db.Model):
    """Message model for user-to-user communication."""
    
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(100))  # Group related messages
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_as_read(self):
        """Mark message as read."""
        self.is_read = True
    
    def __repr__(self):
        return f'<Message {self.message_id} from {self.sender_id} to {self.receiver_id}>'
