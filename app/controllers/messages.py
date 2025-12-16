"""
Messages Controller
Campus Resource Hub - AiDD 2025 Capstone

Routes for messaging between users.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data_access import MessageDAL, UserDAL

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.route('/')
@login_required
def inbox():
    """Show user's message inbox."""
    messages = MessageDAL.get_user_inbox(current_user.user_id)
    unread_count = MessageDAL.get_unread_count(current_user.user_id)
    return render_template('messages/inbox.html', messages=messages, unread_count=unread_count)

@messages_bp.route('/thread/<thread_id>')
@login_required
def view_thread(thread_id):
    """View a message thread."""
    messages = MessageDAL.get_thread_messages(thread_id)
    
    # Verify user is part of this thread
    if messages and not any(
        m.sender_id == current_user.user_id or m.receiver_id == current_user.user_id 
        for m in messages
    ):
        abort(403)
    
    # Mark as read
    MessageDAL.mark_thread_as_read(thread_id, current_user.user_id)
    
    return render_template('messages/thread.html', messages=messages, thread_id=thread_id)

@messages_bp.route('/send/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    """Send a message to a user."""
    receiver = UserDAL.get_user_by_id(receiver_id)
    if not receiver:
        abort(404)
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content:
            flash('Message cannot be empty.', 'danger')
            return render_template('messages/send.html', receiver=receiver)
        
        message = MessageDAL.send_message(
            sender_id=current_user.user_id,
            receiver_id=receiver_id,
            content=content
        )
        
        flash('Message sent!', 'success')
        return redirect(url_for('messages.view_thread', thread_id=message.thread_id))
    
    return render_template('messages/send.html', receiver=receiver)

@messages_bp.route('/reply/<thread_id>', methods=['POST'])
@login_required
def reply(thread_id):
    """Reply in a thread."""
    content = request.form.get('content')
    
    if not content:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('messages.view_thread', thread_id=thread_id))
    
    # Get thread messages to determine receiver
    messages = MessageDAL.get_thread_messages(thread_id)
    if not messages:
        abort(404)
    
    # Determine receiver (the other person in the thread)
    last_message = messages[-1]
    receiver_id = last_message.sender_id if last_message.sender_id != current_user.user_id else last_message.receiver_id
    
    MessageDAL.send_message(
        sender_id=current_user.user_id,
        receiver_id=receiver_id,
        content=content,
        thread_id=thread_id
    )
    
    return redirect(url_for('messages.view_thread', thread_id=thread_id))
