"""
Integration tests for authentication flow.

Tests complete user registration and login process.
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import create_app
from src.models.database import init_database, get_db_connection


@pytest.fixture
def client():
    """Create a test client for Flask app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    # Initialize database
    init_database()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    conn = get_db_connection()
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()


def test_registration_page_loads(client):
    """Test that registration page is accessible."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data


def test_user_registration(client):
    """Test complete user registration flow."""
    response = client.post('/auth/register', data={
        'name': 'New User',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'role': 'student',
        'department': 'Computer Science'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data or b'Login' in response.data


def test_user_login(client):
    """Test user login flow."""
    # First register a user
    client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'role': 'student'
    })
    
    # Now try to login
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome' in response.data or b'Dashboard' in response.data


def test_login_with_wrong_password(client):
    """Test login fails with incorrect password."""
    # Register user
    client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'correct_password',
        'confirm_password': 'correct_password',
        'role': 'student'
    })
    
    # Try to login with wrong password
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'wrong_password'
    }, follow_redirects=True)
    
    assert b'Invalid email or password' in response.data


def test_protected_route_requires_login(client):
    """Test that protected routes redirect to login."""
    response = client.get('/dashboard/', follow_redirects=False)
    
    # Should redirect to login
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_logout(client):
    """Test user logout."""
    # Register and login
    client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'logout@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'role': 'student'
    })
    
    client.post('/auth/login', data={
        'email': 'logout@example.com',
        'password': 'password123'
    })
    
    # Logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data or b'Login' in response.data

