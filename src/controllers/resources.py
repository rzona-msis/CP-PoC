"""
Resources controller - handles resource CRUD operations and search.

Blueprint: resources_bp
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from src.forms import ResourceForm, SearchForm
from src.data_access.resource_dal import ResourceDAL
from src.data_access.review_dal import ReviewDAL
from src.data_access.booking_dal import BookingDAL

resources_bp = Blueprint('resources', __name__)


@resources_bp.route('/')
def list_resources():
    """
    List and search resources.
    
    Supports filtering by keyword, category, location, and sorting.
    """
    form = SearchForm(request.args)
    
    # Get search parameters
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    location = request.args.get('location', '').strip()
    sort_by = request.args.get('sort_by', 'recent')
    
    # Search resources
    resources = ResourceDAL.search_resources(
        keyword=keyword if keyword else None,
        category=category if category else None,
        location=location if location else None,
        sort_by=sort_by
    )
    
    # Get all categories for filter
    categories = ResourceDAL.get_all_categories()
    
    return render_template('resources/list.html', 
                         resources=resources,
                         form=form,
                         categories=categories,
                         search_active=(keyword or category or location))


@resources_bp.route('/<int:resource_id>')
def view_resource(resource_id):
    """
    View detailed resource information.
    
    Shows resource details, reviews, availability, and booking option.
    """
    resource = ResourceDAL.get_resource_by_id(resource_id)
    
    if not resource:
        abort(404)
    
    # Only show published resources to non-owners
    if resource['status'] != 'published':
        if not current_user.is_authenticated or \
           (current_user.user_id != resource['owner_id'] and not current_user.is_admin()):
            abort(403)
    
    # Get reviews and rating
    reviews = ReviewDAL.get_reviews_for_resource(resource_id)
    rating_info = ReviewDAL.get_average_rating(resource_id)
    
    # Get recent bookings for calendar display
    bookings = BookingDAL.get_bookings_for_resource(resource_id, status='approved')
    
    # Check if current user can review
    can_review = False
    if current_user.is_authenticated:
        can_review = ReviewDAL.can_user_review(current_user.user_id, resource_id)
    
    return render_template('resources/view.html',
                         resource=resource,
                         reviews=reviews,
                         rating_info=rating_info,
                         bookings=bookings,
                         can_review=can_review)


@resources_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_resource():
    """
    Create a new resource listing.
    
    Requires authentication. Staff/admin can publish directly.
    """
    form = ResourceForm()
    
    if form.validate_on_submit():
        try:
            # Create resource
            resource_id = ResourceDAL.create_resource(
                owner_id=current_user.user_id,
                title=form.title.data,
                description=form.description.data,
                category=form.category.data,
                location=form.location.data,
                capacity=form.capacity.data,
                status=form.status.data,
                requires_approval=1 if form.requires_approval.data else 0
            )
            
            flash(f'Resource "{form.title.data}" created successfully!', 'success')
            return redirect(url_for('resources.view_resource', resource_id=resource_id))
            
        except Exception as e:
            flash(f'Error creating resource: {str(e)}', 'danger')
    
    return render_template('resources/create.html', form=form)


@resources_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resource(resource_id):
    """
    Edit an existing resource.
    
    Only resource owner or admin can edit.
    """
    resource = ResourceDAL.get_resource_by_id(resource_id)
    
    if not resource:
        abort(404)
    
    # Check permissions
    if current_user.user_id != resource['owner_id'] and not current_user.is_admin():
        abort(403)
    
    form = ResourceForm()
    
    if form.validate_on_submit():
        try:
            # Update resource
            ResourceDAL.update_resource(
                resource_id=resource_id,
                title=form.title.data,
                description=form.description.data,
                category=form.category.data,
                location=form.location.data,
                capacity=form.capacity.data,
                status=form.status.data,
                requires_approval=1 if form.requires_approval.data else 0
            )
            
            flash('Resource updated successfully!', 'success')
            return redirect(url_for('resources.view_resource', resource_id=resource_id))
            
        except Exception as e:
            flash(f'Error updating resource: {str(e)}', 'danger')
    
    # Pre-populate form
    elif request.method == 'GET':
        form.title.data = resource['title']
        form.description.data = resource['description']
        form.category.data = resource['category']
        form.location.data = resource['location']
        form.capacity.data = resource['capacity']
        form.status.data = resource['status']
        form.requires_approval.data = bool(resource['requires_approval'])
    
    return render_template('resources/edit.html', form=form, resource=resource)


@resources_bp.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete_resource(resource_id):
    """
    Delete a resource.
    
    Only resource owner or admin can delete.
    """
    resource = ResourceDAL.get_resource_by_id(resource_id)
    
    if not resource:
        abort(404)
    
    # Check permissions
    if current_user.user_id != resource['owner_id'] and not current_user.is_admin():
        abort(403)
    
    try:
        ResourceDAL.delete_resource(resource_id)
        flash('Resource deleted successfully.', 'success')
        return redirect(url_for('dashboard.my_resources'))
    except Exception as e:
        flash(f'Error deleting resource: {str(e)}', 'danger')
        return redirect(url_for('resources.view_resource', resource_id=resource_id))

