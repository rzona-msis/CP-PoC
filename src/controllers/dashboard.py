"""
Dashboard controller - user dashboard for managing resources and bookings.

Blueprint: dashboard_bp
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.forms import ProfileForm, ChangePasswordForm
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.message_dal import MessageDAL

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """
    User dashboard overview.
    
    Shows summary of user's resources, bookings, and messages.
    """
    # Get user statistics
    my_resources = ResourceDAL.search_resources(owner_id=current_user.user_id, status=None)
    my_bookings = BookingDAL.get_bookings_for_user(current_user.user_id, upcoming_only=True)
    unread_messages = MessageDAL.get_unread_count(current_user.user_id)
    
    # Get resource statistics (always get stats, even if empty)
    resource_stats = ResourceDAL.get_resource_statistics(owner_id=current_user.user_id)
    
    # Get booking statistics
    booking_stats = BookingDAL.get_booking_statistics(owner_id=current_user.user_id)
    
    # Get pending approvals if staff/admin
    pending_approvals = []
    if current_user.is_staff():
        pending_approvals = BookingDAL.get_pending_approvals(owner_id=current_user.user_id)
    
    return render_template('dashboard/index.html',
                         my_resources=my_resources[:5],  # Show latest 5
                         my_bookings=my_bookings[:5],    # Show next 5
                         resource_stats=resource_stats,
                         booking_stats=booking_stats,
                         unread_messages=unread_messages,
                         pending_approvals=pending_approvals[:5])


@dashboard_bp.route('/my-resources')
@login_required
def my_resources():
    """
    List all resources owned by current user.
    
    Shows all statuses (draft, published, archived).
    """
    resources = ResourceDAL.search_resources(owner_id=current_user.user_id, status=None)
    stats = ResourceDAL.get_resource_statistics(owner_id=current_user.user_id)
    
    return render_template('dashboard/my_resources.html', 
                         resources=resources,
                         stats=stats)


@dashboard_bp.route('/my-bookings')
@login_required
def my_bookings():
    """
    List all bookings made by current user.
    
    Shows all booking statuses with filters.
    """
    status_filter = request.args.get('status', None)
    
    bookings = BookingDAL.get_bookings_for_user(current_user.user_id, status=status_filter)
    stats = BookingDAL.get_booking_statistics()
    
    # Get booking counts by status
    booking_counts = {
        'all': len(BookingDAL.get_bookings_for_user(current_user.user_id)),
        'pending': len(BookingDAL.get_bookings_for_user(current_user.user_id, status='pending')),
        'approved': len(BookingDAL.get_bookings_for_user(current_user.user_id, status='approved')),
        'completed': len(BookingDAL.get_bookings_for_user(current_user.user_id, status='completed')),
    }
    
    return render_template('dashboard/my_bookings.html',
                         bookings=bookings,
                         stats=stats,
                         booking_counts=booking_counts,
                         current_filter=status_filter)


@dashboard_bp.route('/pending-approvals')
@login_required
def pending_approvals():
    """
    List bookings pending approval for user's resources.
    
    Only accessible to resource owners.
    """
    if not current_user.is_staff():
        flash('You do not have permission to access this page.', 'warning')
        return redirect(url_for('dashboard.index'))
    
    approvals = BookingDAL.get_pending_approvals(owner_id=current_user.user_id)
    
    return render_template('dashboard/pending_approvals.html', approvals=approvals)


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    View and edit user profile.
    
    Allows updating name and department.
    """
    form = ProfileForm()
    
    if form.validate_on_submit():
        try:
            UserDAL.update_user(
                current_user.user_id,
                name=form.name.data,
                department=form.department.data
            )
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard.profile'))
            
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    # Pre-populate form
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.department.data = current_user.department
    
    # Check if user has Google Calendar connected
    has_calendar = UserDAL.has_calendar_connected(current_user.user_id)
    
    # Check if Google Calendar integration is enabled on server
    from src.services.google_calendar_service import calendar_service
    calendar_enabled = calendar_service.is_enabled()
    
    return render_template('dashboard/profile.html', 
                         form=form, 
                         has_calendar=has_calendar,
                         calendar_enabled=calendar_enabled)


@dashboard_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change user password.
    
    Requires current password verification.
    """
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        user_data = UserDAL.verify_password(current_user.email, form.current_password.data)
        
        if not user_data:
            flash('Current password is incorrect.', 'danger')
        else:
            try:
                UserDAL.update_password(current_user.user_id, form.new_password.data)
                flash('Password changed successfully!', 'success')
                return redirect(url_for('dashboard.profile'))
            except Exception as e:
                flash(f'Error changing password: {str(e)}', 'danger')
    
    return render_template('dashboard/change_password.html', form=form)

