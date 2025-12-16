"""
Admin Controller
Campus Resource Hub - AiDD 2025 Capstone

Routes for admin dashboard and moderation.
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.data_access import UserDAL, ResourceDAL, BookingDAL

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics."""
    total_users = len(UserDAL.get_all_users())
    total_resources = len(ResourceDAL.get_all_resources())
    pending_bookings = len(BookingDAL.get_active_bookings())
    
    stats = {
        'total_users': total_users,
        'total_resources': total_resources,
        'pending_bookings': pending_bookings
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users."""
    users = UserDAL.get_all_users()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/promote', methods=['POST'])
@login_required
@admin_required
def promote_user(user_id):
    """Promote user to staff."""
    UserDAL.update_user(user_id, role='staff')
    flash('User promoted to staff.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/demote', methods=['POST'])
@login_required
@admin_required
def demote_user(user_id):
    """Demote user to student."""
    UserDAL.update_user(user_id, role='student')
    flash('User demoted to student.', 'info')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user."""
    if user_id == current_user.user_id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    UserDAL.delete_user(user_id)
    flash('User deleted.', 'info')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/resources')
@login_required
@admin_required
def manage_resources():
    """View all resources for moderation."""
    resources = ResourceDAL.get_all_resources(status='published')
    return render_template('admin/resources.html', resources=resources)
