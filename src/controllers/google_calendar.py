"""
Google Calendar OAuth2 Controller

Handles OAuth2 authentication flow for Google Calendar integration.
"""

from flask import Blueprint, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from src.services.google_calendar_service import calendar_service
from src.data_access.user_dal import update_user_calendar_tokens, disconnect_user_calendar
import secrets

google_calendar_bp = Blueprint('google_calendar', __name__)


@google_calendar_bp.route('/connect')
@login_required
def connect_calendar():
    """Initiate Google Calendar OAuth2 flow."""
    
    if not calendar_service.is_enabled():
        flash('Google Calendar integration is not configured. Please contact your administrator.', 'warning')
        return redirect(url_for('dashboard.profile'))
    
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    session['google_calendar_state'] = state
    
    # Get authorization URL
    auth_url = calendar_service.get_authorization_url(state)
    
    if not auth_url:
        flash('Failed to initiate Google Calendar connection.', 'danger')
        return redirect(url_for('dashboard.profile'))
    
    return redirect(auth_url)


@google_calendar_bp.route('/callback')
@login_required
def calendar_callback():
    """Handle OAuth2 callback from Google."""
    
    # Verify state token
    state = request.args.get('state')
    stored_state = session.pop('google_calendar_state', None)
    
    if not state or state != stored_state:
        flash('Invalid state parameter. Please try again.', 'danger')
        return redirect(url_for('dashboard.profile'))
    
    # Check for errors
    error = request.args.get('error')
    if error:
        flash(f'Google Calendar authorization failed: {error}', 'danger')
        return redirect(url_for('dashboard.profile'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        flash('No authorization code received.', 'danger')
        return redirect(url_for('dashboard.profile'))
    
    # Exchange code for tokens
    token_data = calendar_service.exchange_code_for_token(code)
    
    if not token_data:
        flash('Failed to obtain Google Calendar access token.', 'danger')
        return redirect(url_for('dashboard.profile'))
    
    # Store tokens in database
    success = update_user_calendar_tokens(
        current_user.user_id,
        token_data['token'],
        token_data['refresh_token'],
        token_data['token_expiry']
    )
    
    if success:
        flash('Google Calendar connected successfully! Your bookings will now sync to your calendar.', 'success')
    else:
        flash('Failed to save calendar tokens. Please try again.', 'danger')
    
    return redirect(url_for('dashboard.profile'))


@google_calendar_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect_calendar():
    """Disconnect user's Google Calendar."""
    
    success = disconnect_user_calendar(current_user.user_id)
    
    if success:
        flash('Google Calendar disconnected successfully.', 'success')
    else:
        flash('Failed to disconnect Google Calendar.', 'danger')
    
    return redirect(url_for('dashboard.profile'))

