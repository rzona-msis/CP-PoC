"""
Reviews Controller
Campus Resource Hub - AiDD 2025 Capstone

Routes for resource reviews and ratings.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data_access import ReviewDAL, ResourceDAL

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/create/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def create_review(resource_id):
    """Create a review for a resource."""
    resource = ResourceDAL.get_resource_by_id(resource_id)
    if not resource:
        abort(404)
    
    # Check if user can review
    if not ReviewDAL.user_can_review(current_user.user_id, resource_id):
        flash('You have already reviewed this resource.', 'warning')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5.', 'danger')
            return render_template('reviews/create.html', resource=resource)
        
        review = ReviewDAL.create_review(
            resource_id=resource_id,
            reviewer_id=current_user.user_id,
            rating=rating,
            comment=comment
        )
        
        if review:
            flash('Review submitted!', 'success')
        else:
            flash('Could not submit review.', 'danger')
        
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    return render_template('reviews/create.html', resource=resource)

@reviews_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """Edit a review."""
    review = ReviewDAL.get_review_by_id(review_id)
    if not review:
        abort(404)
    
    # Authorization: reviewer only
    if review.reviewer_id != current_user.user_id:
        abort(403)
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5.', 'danger')
            return render_template('reviews/edit.html', review=review)
        
        ReviewDAL.update_review(review_id, rating=rating, comment=comment)
        flash('Review updated!', 'success')
        return redirect(url_for('resources.detail', resource_id=review.resource_id))
    
    return render_template('reviews/edit.html', review=review)

@reviews_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete a review."""
    review = ReviewDAL.get_review_by_id(review_id)
    if not review:
        abort(404)
    
    # Authorization: reviewer or admin
    if review.reviewer_id != current_user.user_id and not current_user.is_admin():
        abort(403)
    
    resource_id = review.resource_id
    ReviewDAL.delete_review(review_id)
    flash('Review deleted.', 'info')
    return redirect(url_for('resources.detail', resource_id=resource_id))
