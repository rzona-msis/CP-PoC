"""
Messages controller - handles messaging between users.

Blueprint: messages_bp
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from src.forms import MessageForm
from src.data_access.message_dal import MessageDAL
from src.data_access.user_dal import UserDAL

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/')
@login_required
def list_threads():
    """
    List all message threads for current user.
    
    Shows conversations with unread counts.
    """
    threads = MessageDAL.get_user_threads(current_user.user_id)
    
    # Get all users for compose dropdown (excluding current user)
    all_users = UserDAL.get_all_users()
    available_users = [user for user in all_users if user['user_id'] != current_user.user_id]
    
    # Create form for composing new message
    form = MessageForm()
    
    return render_template('messages/list.html', 
                         threads=threads, 
                         available_users=available_users,
                         form=form)


@messages_bp.route('/thread/<thread_id>')
@login_required
def view_thread(thread_id):
    """
    View a specific message thread.
    
    Displays all messages in conversation.
    """
    messages = MessageDAL.get_thread_messages(thread_id)
    
    if not messages:
        flash('Conversation not found.', 'warning')
        return redirect(url_for('messages.list_threads'))
    
    # Check if current user is part of this conversation
    first_message = messages[0]
    if current_user.user_id not in [first_message['sender_id'], first_message['receiver_id']]:
        abort(403)
    
    # Mark messages as read
    MessageDAL.mark_as_read(thread_id, current_user.user_id)
    
    # Determine other user
    other_user_id = first_message['receiver_id'] if current_user.user_id == first_message['sender_id'] else first_message['sender_id']
    other_user = UserDAL.get_user_by_id(other_user_id)
    
    # Create form for reply
    form = MessageForm()
    form.receiver_id.data = other_user_id
    
    return render_template('messages/thread.html', 
                         messages=messages,
                         thread_id=thread_id,
                         other_user=other_user,
                         form=form)


@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Send a new message.
    
    Can be sent from thread view or initiate new conversation.
    """
    # Debug: Print ALL form data
    print("=" * 80)
    print("SEND MESSAGE ROUTE CALLED")
    print("All form data received:")
    for key, value in request.form.items():
        print(f"  {key}: {value}")
    print("=" * 80)
    
    # Get data directly from request
    receiver_id = request.form.get('receiver_id')
    content = request.form.get('content')
    booking_id = request.form.get('booking_id')
    
    print(f"Extracted - receiver_id: '{receiver_id}', content: '{content}', booking_id: '{booking_id}'")
    
    # Validate receiver_id
    if not receiver_id or receiver_id.strip() == '':
        print(f"VALIDATION FAILED: receiver_id is empty or None")
        flash('Please select a recipient.', 'danger')
        return redirect(request.referrer or url_for('messages.list_threads'))
    
    # Validate content
    if not content or not content.strip():
        flash('Message content is required.', 'danger')
        return redirect(request.referrer or url_for('messages.list_threads'))
    
    if len(content) > 1000:
        flash('Message must be less than 1000 characters.', 'danger')
        return redirect(request.referrer or url_for('messages.list_threads'))
    
    try:
        receiver_id = int(receiver_id)
        
        # Verify receiver exists
        receiver = UserDAL.get_user_by_id(receiver_id)
        if not receiver:
            flash('Recipient not found.', 'danger')
            return redirect(url_for('messages.list_threads'))
        
        # Don't allow messaging yourself
        if receiver_id == current_user.user_id:
            flash('You cannot send messages to yourself.', 'warning')
            return redirect(url_for('messages.list_threads'))
        
        booking_id = int(booking_id) if booking_id else None
        
        # Send message
        MessageDAL.send_message(
            sender_id=current_user.user_id,
            receiver_id=receiver_id,
            content=content.strip(),
            booking_id=booking_id
        )
        
        # Generate thread_id for redirect
        thread_id = f"{min(current_user.user_id, receiver_id)}_{max(current_user.user_id, receiver_id)}"
        if booking_id:
            thread_id += f"_b{booking_id}"
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages.view_thread', thread_id=thread_id))
        
    except ValueError:
        flash('Invalid recipient ID.', 'danger')
    except Exception as e:
        flash(f'Error sending message: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('messages.list_threads'))


@messages_bp.route('/compose/<int:receiver_id>')
@login_required
def compose_message(receiver_id):
    """
    Start a new conversation with a user.
    
    Displays compose form for new message.
    """
    receiver = UserDAL.get_user_by_id(receiver_id)
    
    if not receiver:
        flash('Recipient not found.', 'danger')
        return redirect(url_for('messages.list_threads'))
    
    if receiver_id == current_user.user_id:
        flash('You cannot send messages to yourself.', 'warning')
        return redirect(url_for('messages.list_threads'))
    
    form = MessageForm()
    form.receiver_id.data = receiver_id
    
    return render_template('messages/compose.html', receiver=receiver, form=form)

