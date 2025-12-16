"""
Authentication Controller
Campus Resource Hub - AiDD 2025 Capstone

Routes for user registration, login, and logout.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.data_access import UserDAL

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        role = request.form.get('role', 'student')
        
        # Validate inputs
        if not all([name, email, password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        # Check if user exists
        if UserDAL.get_user_by_email(email):
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        # Create user
        user = UserDAL.create_user(name, email, password, role, department)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Validate inputs
        if not all([email, password]):
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = UserDAL.authenticate_user(email, password)
        if not user:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')
        
        # Log in user
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))
