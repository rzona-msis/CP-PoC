"""
Resources Controller
Campus Resource Hub - AiDD 2025 Capstone

Routes for resource CRUD operations.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data_access import ResourceDAL, ReviewDAL

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')

@resources_bp.route('/')
def list_resources():
    """List all published resources."""
    category = request.args.get('category')
    if category:
        resources = ResourceDAL.get_resources_by_category(category)
    else:
        resources = ResourceDAL.get_all_resources()
    return render_template('resources/list.html', resources=resources)

@resources_bp.route('/<int:resource_id>')
def detail(resource_id):
    """Show resource details."""
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        abort(404)
    
    reviews = ReviewDAL.get_reviews_by_resource(resource_id)
    avg_rating = ReviewDAL.get_average_rating(resource_id)
    
    return render_template('resources/detail.html', 
                         resource=resource, 
                         reviews=reviews, 
                         avg_rating=avg_rating)

@resources_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new resource."""
    if not current_user.is_staff():
        flash('Only staff can create resources.', 'danger')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        location = request.form.get('location')
        capacity = request.form.get('capacity', type=int)
        requires_approval = request.form.get('requires_approval') == 'on'
        
        if not all([title, category, location]):
            flash('Title, category, and location are required.', 'danger')
            return render_template('resources/create.html')
        
        resource = ResourceDAL.create_resource(
            owner_id=current_user.user_id,
            title=title,
            description=description,
            category=category,
            location=location,
            capacity=capacity,
            requires_approval=requires_approval
        )
        
        flash('Resource created successfully!', 'success')
        return redirect(url_for('resources.detail', resource_id=resource.resource_id))
    
    return render_template('resources/create.html')

@resources_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(resource_id):
    """Edit a resource."""
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        abort(404)
    
    # Authorization: owner or admin
    if resource.owner_id != current_user.user_id and not current_user.is_admin():
        abort(403)
    
    if request.method == 'POST':
        updates = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'location': request.form.get('location'),
            'capacity': request.form.get('capacity', type=int),
            'requires_approval': request.form.get('requires_approval') == 'on'
        }
        
        ResourceDAL.update_resource(resource_id, **updates)
        flash('Resource updated successfully!', 'success')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    return render_template('resources/edit.html', resource=resource)

@resources_bp.route('/<int:resource_id>/publish', methods=['POST'])
@login_required
def publish(resource_id):
    """Publish a draft resource."""
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        abort(404)
    
    # Authorization: owner or admin
    if resource.owner_id != current_user.user_id and not current_user.is_admin():
        abort(403)
    
    ResourceDAL.publish_resource(resource_id)
    flash('Resource published!', 'success')
    return redirect(url_for('resources.detail', resource_id=resource_id))

@resources_bp.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete(resource_id):
    """Delete a resource."""
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        abort(404)
    
    # Authorization: owner or admin
    if resource.owner_id != current_user.user_id and not current_user.is_admin():
        abort(403)
    
    ResourceDAL.delete_resource(resource_id)
    flash('Resource deleted.', 'info')
    return redirect(url_for('main.home'))
