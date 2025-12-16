"""
Main Controller
Campus Resource Hub - AiDD 2025 Capstone

Routes for homepage, search, and about page.
"""

from flask import Blueprint, render_template, request
from app.data_access import ResourceDAL

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Homepage with featured resources."""
    resources = ResourceDAL.get_all_resources(status='published')
    return render_template('home.html', resources=resources)

@main_bp.route('/search')
def search():
    """Search resources."""
    query = request.args.get('q', '')
    category = request.args.get('category')
    location = request.args.get('location')
    
    resources = ResourceDAL.search_resources(query, category, location)
    return render_template('resources/list.html', resources=resources, query=query)

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')
