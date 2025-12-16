"""
Admin panel controller - administrative functions and moderation.

Blueprint: admin_bp
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from src.data_access.admin_dal import AdminDAL
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from src.data_access.review_dal import ReviewDAL

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """
    Decorator to require admin role for route access.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard with system statistics and recent activity.
    
    Only accessible to administrators.
    """
    # Get comprehensive system statistics
    stats = AdminDAL.get_system_statistics()
    
    # Get recent admin logs
    recent_logs = AdminDAL.get_recent_logs(limit=20)
    
    # Get flagged content
    flagged_content = AdminDAL.get_flagged_content()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_logs=recent_logs,
                         flagged_content=flagged_content)


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """
    User management page.
    
    View and manage all users.
    """
    role_filter = request.args.get('role', None)
    
    users = UserDAL.get_all_users(role=role_filter)
    user_stats = UserDAL.get_user_statistics()
    
    return render_template('admin/users.html', 
                         users=users,
                         stats=user_stats,
                         current_filter=role_filter)


@admin_bp.route('/users/<int:user_id>/update-role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """
    Update a user's role.
    
    Admin can promote/demote users.
    """
    new_role = request.form.get('role')
    
    if new_role not in ['student', 'staff', 'admin']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        UserDAL.update_user(user_id, role=new_role)
        
        # Log action
        AdminDAL.log_action(
            current_user.user_id,
            f'Changed user role to {new_role}',
            'users',
            user_id
        )
        
        flash('User role updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating user role: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete a user account.
    
    Cascades to user's resources and bookings.
    """
    if user_id == current_user.user_id:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user = UserDAL.get_user_by_id(user_id)
        UserDAL.delete_user(user_id)
        
        # Log action
        AdminDAL.log_action(
            current_user.user_id,
            f'Deleted user account',
            'users',
            user_id,
            f'Email: {user["email"]}'
        )
        
        flash('User deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/resources')
@login_required
@admin_required
def manage_resources():
    """
    Resource management page.
    
    View and moderate all resources.
    """
    status_filter = request.args.get('status', 'published')
    
    resources = ResourceDAL.search_resources(status=status_filter, sort_by='recent')
    stats = ResourceDAL.get_resource_statistics()
    
    return render_template('admin/resources.html',
                         resources=resources,
                         stats=stats,
                         current_filter=status_filter)


@admin_bp.route('/bookings')
@login_required
@admin_required
def manage_bookings():
    """
    Booking management page.
    
    View all bookings with filtering.
    """
    status_filter = request.args.get('status', None)
    
    # Get bookings (simplified - in production would add pagination)
    from src.models.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT b.*, 
               r.title as resource_title,
               u.name as requester_name
        FROM bookings b
        JOIN resources r ON b.resource_id = r.resource_id
        JOIN users u ON b.requester_id = u.user_id
        WHERE 1=1
    """
    params = []
    
    if status_filter:
        query += " AND b.status = ?"
        params.append(status_filter)
    
    query += " ORDER BY b.created_at DESC LIMIT 100"
    
    cursor.execute(query, params)
    bookings = cursor.fetchall()
    conn.close()
    
    stats = BookingDAL.get_booking_statistics()
    
    return render_template('admin/bookings.html',
                         bookings=bookings,
                         stats=stats,
                         current_filter=status_filter)


@admin_bp.route('/reviews')
@login_required
@admin_required
def manage_reviews():
    """
    Review moderation page.
    
    View and moderate all reviews.
    """
    # Get all reviews (simplified)
    from src.models.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.*, 
               res.title as resource_title,
               u.name as reviewer_name
        FROM reviews r
        JOIN resources res ON r.resource_id = res.resource_id
        JOIN users u ON r.reviewer_id = u.user_id
        ORDER BY r.timestamp DESC
        LIMIT 100
    """)
    reviews = cursor.fetchall()
    conn.close()
    
    return render_template('admin/reviews.html', reviews=reviews)


@admin_bp.route('/reviews/<int:review_id>/hide', methods=['POST'])
@login_required
@admin_required
def hide_review(review_id):
    """
    Hide an inappropriate review.
    """
    try:
        ReviewDAL.hide_review(review_id, hide=True)
        
        # Log action
        AdminDAL.log_action(
            current_user.user_id,
            'Hid review',
            'reviews',
            review_id
        )
        
        flash('Review hidden successfully.', 'success')
    except Exception as e:
        flash(f'Error hiding review: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('admin.manage_reviews'))


@admin_bp.route('/reviews/<int:review_id>/unhide', methods=['POST'])
@login_required
@admin_required
def unhide_review(review_id):
    """
    Unhide a previously hidden review.
    """
    try:
        ReviewDAL.hide_review(review_id, hide=False)
        
        # Log action
        AdminDAL.log_action(
            current_user.user_id,
            'Unhid review',
            'reviews',
            review_id
        )
        
        flash('Review restored successfully.', 'success')
    except Exception as e:
        flash(f'Error unhiding review: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('admin.manage_reviews'))


@admin_bp.route('/reports')
@login_required
@admin_required
def usage_reports():
    """
    Generate usage reports and analytics.
    """
    # Get usage report for last 30 days
    report = AdminDAL.get_usage_report()
    
    return render_template('admin/reports.html', report=report)


@admin_bp.route('/logs')
@login_required
@admin_required
def view_logs():
    """
    View admin action logs.
    """
    limit = request.args.get('limit', 100, type=int)
    
    logs = AdminDAL.get_recent_logs(limit=limit)
    
    return render_template('admin/logs.html', logs=logs)

