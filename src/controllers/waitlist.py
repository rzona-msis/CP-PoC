"""
Waitlist controller - handles waitlist operations for resources.

Blueprint: waitlist_bp
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from src.data_access.waitlist_dal import WaitlistDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from datetime import datetime

waitlist_bp = Blueprint('waitlist', __name__)


@waitlist_bp.route('/join', methods=['POST'])
@login_required
def join_waitlist():
    """
    Add current user to waitlist for a resource.
    """
    resource_id = request.form.get('resource_id', type=int)
    requested_datetime = request.form.get('requested_datetime')
    
    if not resource_id or not requested_datetime:
        flash('Missing required information.', 'danger')
        return redirect(url_for('resources.list_resources'))
    
    try:
        # Verify resource exists
        resource = ResourceDAL.get_resource_by_id(resource_id)
        if not resource:
            flash('Resource not found.', 'danger')
            return redirect(url_for('resources.list_resources'))
        
        # Check if already on waitlist
        if WaitlistDAL.is_user_on_waitlist(current_user.user_id, resource_id, requested_datetime):
            flash('You are already on the waitlist for this time slot.', 'info')
        else:
            # Add to waitlist
            waitlist_id = WaitlistDAL.join_waitlist(resource_id, current_user.user_id, requested_datetime)
            position = WaitlistDAL.get_waitlist_position(waitlist_id)
            
            flash(f'✓ You\'ve been added to the waitlist! You are #{position} in line. We\'ll notify you when a spot opens up.', 'success')
        
        return redirect(url_for('resources.view_resource', resource_id=resource_id))
        
    except ValueError as e:
        flash(str(e), 'warning')
        return redirect(url_for('resources.view_resource', resource_id=resource_id))
    except Exception as e:
        flash(f'Error joining waitlist: {str(e)}', 'danger')
        return redirect(url_for('resources.view_resource', resource_id=resource_id))


@waitlist_bp.route('/leave/<int:waitlist_id>', methods=['POST'])
@login_required
def leave_waitlist(waitlist_id):
    """
    Remove current user from waitlist.
    """
    try:
        success = WaitlistDAL.leave_waitlist(waitlist_id, current_user.user_id)
        
        if success:
            flash('You have been removed from the waitlist.', 'info')
        else:
            flash('Could not remove you from the waitlist.', 'warning')
            
    except Exception as e:
        flash(f'Error leaving waitlist: {str(e)}', 'danger')
    
    # Redirect back to dashboard
    return redirect(url_for('dashboard.my_bookings'))


@waitlist_bp.route('/my-waitlists')
@login_required
def my_waitlists():
    """
    View all waitlist entries for current user.
    """
    try:
        waitlists = WaitlistDAL.get_user_waitlists(current_user.user_id)
        
        # Add position info to each waitlist entry
        for waitlist in waitlists:
            waitlist['position'] = WaitlistDAL.get_waitlist_position(waitlist['waitlist_id'])
        
        return render_template('waitlist/my_waitlists.html', waitlists=waitlists)
        
    except Exception as e:
        flash(f'Error loading waitlists: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@waitlist_bp.route('/resource/<int:resource_id>')
@login_required
def view_resource_waitlist(resource_id):
    """
    View waitlist for a specific resource (owner/admin only).
    """
    resource = ResourceDAL.get_resource_by_id(resource_id)
    
    if not resource:
        abort(404)
    
    # Check permissions
    if current_user.user_id != resource['owner_id'] and not current_user.is_admin():
        abort(403)
    
    try:
        waitlists = WaitlistDAL.get_waitlist_for_resource(resource_id)
        
        # Add position info
        for i, waitlist in enumerate(waitlists, 1):
            waitlist['position'] = i
        
        return render_template('waitlist/resource_waitlist.html', 
                             resource=resource, 
                             waitlists=waitlists)
        
    except Exception as e:
        flash(f'Error loading waitlist: {str(e)}', 'danger')
        return redirect(url_for('resources.view_resource', resource_id=resource_id))


@waitlist_bp.route('/api/count')
@login_required
def get_waitlist_count():
    """
    API endpoint to get waitlist count for a resource/time.
    """
    resource_id = request.args.get('resource_id', type=int)
    requested_datetime = request.args.get('requested_datetime')
    
    if not resource_id:
        return jsonify({'error': 'Missing resource_id'}), 400
    
    try:
        count = WaitlistDAL.get_waitlist_count_for_resource(resource_id, requested_datetime)
        return jsonify({'count': count, 'resource_id': resource_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

