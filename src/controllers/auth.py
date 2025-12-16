"""
Authentication controller - handles user registration, login, and logout.

Blueprint: auth_bp
"""
# AI Contribution: Authentication flow scaffolded by Cursor AI; team enhanced security

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from src.forms import RegistrationForm, LoginForm
from src.data_access.user_dal import UserDAL
from src.models.user import User
import sqlite3

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration endpoint.
    
    GET: Display registration form
    POST: Process registration and create new user
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user_id = UserDAL.create_user(
                name=form.name.data,
                email=form.email.data.lower().strip(),
                password=form.password.data,
                role=form.role.data,
                department=form.department.data
            )
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except sqlite3.IntegrityError:
            flash('Email address already registered. Please use a different email.', 'danger')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login endpoint.
    
    GET: Display login form
    POST: Authenticate user and create session
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data
        
        # Verify credentials
        user_data = UserDAL.verify_password(email, password)
        
        if user_data:
            user = User(user_data)
            login_user(user)
            
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """
    User logout endpoint.
    Clears user session and redirects to homepage.
    """
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

