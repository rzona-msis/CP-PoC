"""
Bookings Controller
Campus Resource Hub - AiDD 2025 Capstone

Routes for booking requests, approvals, and management.
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data_access import BookingDAL, ResourceDAL

bookings_bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bookings_bp.route('/')
@login_required
def my_bookings():
    """Show user's bookings."""
    bookings = BookingDAL.get_bookings_by_user(current_user.user_id)
    return render_template('bookings/my_bookings.html', bookings=bookings)

@bookings_bp.route('/pending')
@login_required
def pending_requests():
    """Show pending booking requests for staff/owners."""
    if not current_user.is_staff():
        abort(403)
    
    bookings = BookingDAL.get_pending_bookings_for_owner(current_user.user_id)
    return render_template('bookings/pending.html', bookings=bookings)

@bookings_bp.route('/create/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def create_booking(resource_id):
    """Create a booking request."""
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        abort(404)
    
    if request.method == 'POST':
        start_str = request.form.get('start_datetime')
        end_str = request.form.get('end_datetime')
        message = request.form.get('message')
        
        try:
            start_datetime = datetime.fromisoformat(start_str)
            end_datetime = datetime.fromisoformat(end_str)
        except ValueError:
            flash('Invalid date/time format.', 'danger')
            return render_template('bookings/create.html', resource=resource)
        
        # Check for conflicts
        if BookingDAL.check_conflicts(resource_id, start_datetime, end_datetime):
            flash('This time slot is already booked.', 'danger')
            return render_template('bookings/create.html', resource=resource)
        
        # Create booking
        booking = BookingDAL.create_booking(
            resource_id=resource_id,
            requester_id=current_user.user_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            message=message
        )
        
        flash('Booking request submitted!', 'success')
        return redirect(url_for('bookings.my_bookings'))
    
    return render_template('bookings/create.html', resource=resource)

@bookings_bp.route('/<int:booking_id>/approve', methods=['POST'])
@login_required
def approve_booking(booking_id):
    """Approve a booking request."""
    booking = BookingDAL.get_booking_by_id(booking_id)
    if not booking:
        abort(404)
    
    # Authorization: resource owner or admin
    if booking.resource.owner_id != current_user.user_id and not current_user.is_admin():
        abort(403)
    
    BookingDAL.approve_booking(booking_id)
    flash('Booking approved!', 'success')
    return redirect(url_for('bookings.pending_requests'))

@bookings_bp.route('/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject_booking(booking_id):
    """Reject a booking request."""
    booking = BookingDAL.get_booking_by_id(booking_id)
    if not booking:
        abort(404)
    
    # Authorization: resource owner or admin
    if booking.resource.owner_id != current_user.user_id and not current_user.is_admin():
        abort(403)
    
    BookingDAL.reject_booking(booking_id)
    flash('Booking rejected.', 'info')
    return redirect(url_for('bookings.pending_requests'))

@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking."""
    booking = BookingDAL.get_booking_by_id(booking_id)
    if not booking:
        abort(404)
    
    # Authorization: requester, owner, or admin
    authorized = (
        booking.requester_id == current_user.user_id or
        booking.resource.owner_id == current_user.user_id or
        current_user.is_admin()
    )
    if not authorized:
        abort(403)
    
    BookingDAL.cancel_booking(booking_id)
    flash('Booking cancelled.', 'info')
    return redirect(url_for('bookings.my_bookings'))
