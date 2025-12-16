"""
Integration Tests for Campus Resource Hub
Tests core functionality and Google Calendar integration
"""

import pytest
import sqlite3
from src.app import create_app
from src.models.database import get_db_connection, init_database, seed_sample_data
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL
from src.services.google_calendar_service import calendar_service
import os


@pytest.fixture
def app():
    """Create and configure test app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestDatabaseIntegration:
    """Test database setup and integrity."""
    
    def test_database_exists(self):
        """Verify database file exists."""
        db_path = 'src/campus_hub.db'
        assert os.path.exists(db_path), "Database file should exist"
    
    def test_database_schema(self):
        """Verify all required tables exist with correct columns."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        assert 'user_id' in user_columns
        assert 'google_calendar_token' in user_columns
        assert 'google_calendar_refresh_token' in user_columns
        assert 'google_calendar_token_expiry' in user_columns
        
        # Check bookings table
        cursor.execute("PRAGMA table_info(bookings)")
        booking_columns = [row[1] for row in cursor.fetchall()]
        assert 'booking_id' in booking_columns
        assert 'calendar_event_id' in booking_columns
        
        # Check resources table
        cursor.execute("PRAGMA table_info(resources)")
        resource_columns = [row[1] for row in cursor.fetchall()]
        assert 'resource_id' in resource_columns
        assert 'owner_id' in resource_columns
        
        conn.close()
    
    def test_sample_data_exists(self):
        """Verify sample data was seeded."""
        # Check users
        users = UserDAL.get_all_users()
        assert len(users) > 0, "Should have sample users"
        
        # Check resources
        resources = ResourceDAL.search_resources()
        assert len(resources) > 0, "Should have sample resources"
        
        # Check bookings
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bookings")
        booking_count = cursor.fetchone()[0]
        conn.close()
        assert booking_count > 0, "Should have sample bookings"


class TestAuthenticationIntegration:
    """Test authentication flows."""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_page_loads(self, client):
        """Test registration page is accessible."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_valid_login(self, client):
        """Test login with valid credentials."""
        response = client.post('/auth/login', data={
            'email': 'admin@university.edu',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestResourceIntegration:
    """Test resource management."""
    
    def test_resource_list_page(self, client):
        """Test resource listing is accessible."""
        response = client.get('/resources/')
        assert response.status_code == 200
    
    def test_resource_search(self):
        """Test resource search functionality."""
        results = ResourceDAL.search_resources(keyword="room")
        assert isinstance(results, list)
    
    def test_resource_categories(self):
        """Test category filtering."""
        categories = ['Study Room', 'Meeting Room', 'Equipment', 'Lab Space']
        for category in categories:
            results = ResourceDAL.search_resources(category=category)
            assert isinstance(results, list)


class TestBookingIntegration:
    """Test booking functionality."""
    
    def test_booking_dal_methods(self):
        """Test booking data access methods."""
        # Get existing bookings
        bookings = BookingDAL.get_bookings_for_user(3)  # Alex Smith
        assert isinstance(bookings, list)
        
        # Get booking statistics
        stats = BookingDAL.get_booking_statistics()
        assert 'total_bookings' in stats
        assert stats['total_bookings'] > 0
    
    def test_booking_conflict_detection(self):
        """Test conflict detection works."""
        # This should work with existing sample data
        has_conflict = BookingDAL.has_conflict(
            resource_id=1,
            start_datetime='2025-11-11 10:00:00',
            end_datetime='2025-11-11 12:00:00'
        )
        # Should detect conflict with existing booking
        assert has_conflict == True


class TestDashboardIntegration:
    """Test dashboard functionality."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects to login when not authenticated."""
        response = client.get('/dashboard/')
        assert response.status_code == 302  # Redirect
    
    def test_profile_requires_login(self, client):
        """Test profile page requires authentication."""
        response = client.get('/dashboard/profile')
        assert response.status_code == 302  # Redirect


class TestGoogleCalendarIntegration:
    """Test Google Calendar integration."""
    
    def test_calendar_service_exists(self):
        """Test Google Calendar service is importable."""
        assert calendar_service is not None
    
    def test_calendar_service_configuration(self):
        """Test calendar service configuration check."""
        # Should work even without credentials
        is_enabled = calendar_service.is_enabled()
        assert isinstance(is_enabled, bool)
    
    def test_calendar_token_storage_methods(self):
        """Test calendar token DAL methods exist."""
        # Test has_calendar_connected method
        result = UserDAL.has_calendar_connected(1)
        assert isinstance(result, bool)
    
    def test_calendar_event_id_field(self):
        """Test booking can store calendar event ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get a booking
        cursor.execute("SELECT booking_id, calendar_event_id FROM bookings LIMIT 1")
        booking = cursor.fetchone()
        assert booking is not None
        
        # calendar_event_id field should exist (can be NULL)
        assert len(booking) >= 2
        
        conn.close()
    
    def test_update_calendar_event_id(self):
        """Test updating calendar event ID on booking."""
        # Get first booking
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT booking_id FROM bookings LIMIT 1")
        booking = cursor.fetchone()
        conn.close()
        
        if booking:
            booking_id = booking[0]
            # Test update method
            result = BookingDAL.update_calendar_event_id(
                booking_id,
                'test_event_id_12345'
            )
            assert result == True
            
            # Verify it was updated
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT calendar_event_id FROM bookings WHERE booking_id = ?",
                (booking_id,)
            )
            updated_booking = cursor.fetchone()
            conn.close()
            
            assert updated_booking['calendar_event_id'] == 'test_event_id_12345'


class TestAIChatbotIntegration:
    """Test AI Chatbot functionality."""
    
    def test_ai_chat_page_loads(self, client):
        """Test AI chat interface is accessible."""
        # Login first
        client.post('/auth/login', data={
            'email': 'admin@university.edu',
            'password': 'admin123'
        })
        
        response = client.get('/ai/chat')
        assert response.status_code == 200
    
    def test_ai_service_exists(self):
        """Test AI concierge service is importable."""
        from src.services.ai_concierge import ResourceConcierge
        concierge = ResourceConcierge()
        assert concierge is not None


class TestRoutesIntegration:
    """Test all major routes are accessible."""
    
    def test_homepage(self, client):
        """Test homepage loads."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_resources_routes(self, client):
        """Test resource routes are accessible."""
        # List page
        response = client.get('/resources/')
        assert response.status_code == 200
        
        # View specific resource
        response = client.get('/resources/1')
        assert response.status_code in [200, 302]  # 302 if needs login
    
    def test_calendar_routes(self, client):
        """Test calendar routes require authentication."""
        response = client.get('/calendar/connect')
        assert response.status_code == 302  # Redirect to login
    
    def test_error_pages_exist(self, client):
        """Test error pages can be rendered."""
        # 404 page
        response = client.get('/nonexistent-page')
        assert response.status_code == 404


class TestSecurityIntegration:
    """Test security features."""
    
    def test_password_hashing(self):
        """Test passwords are hashed, not stored in plain text."""
        user = UserDAL.get_user_by_email('admin@university.edu')
        assert user is not None
        # Password hash should not be the plain password
        assert user['password_hash'] != 'admin123'
        # Should look like a bcrypt hash
        assert user['password_hash'].startswith('$2')
    
    def test_protected_routes(self, client):
        """Test protected routes redirect unauthenticated users."""
        protected_routes = [
            '/dashboard/',
            '/dashboard/profile',
            '/dashboard/my-resources',
            '/dashboard/my-bookings',
            '/bookings/create',
            '/calendar/connect',
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302, f"{route} should redirect"


class TestDataIntegrity:
    """Test data integrity and relationships."""
    
    def test_foreign_keys_enforced(self):
        """Test foreign key constraints are working."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try to create booking with non-existent resource
        try:
            cursor.execute("""
                INSERT INTO bookings 
                (resource_id, requester_id, start_datetime, end_datetime, status)
                VALUES (99999, 1, '2025-12-01 10:00:00', '2025-12-01 12:00:00', 'pending')
            """)
            conn.commit()
            assert False, "Should have raised foreign key error"
        except sqlite3.IntegrityError:
            # Expected - foreign key constraint should fail
            conn.rollback()
        
        conn.close()
    
    def test_cascade_deletes(self):
        """Test cascade delete behavior."""
        # This test verifies the schema supports cascading
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check foreign key pragma
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        assert fk_enabled == 1, "Foreign keys should be enabled"
        
        conn.close()


def run_integration_tests():
    """Run all integration tests and print results."""
    print("=" * 70)
    print("CAMPUS RESOURCE HUB - INTEGRATION TEST SUITE")
    print("=" * 70)
    print()
    
    # Run pytest programmatically
    import sys
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ])
    
    return exit_code


if __name__ == '__main__':
    run_integration_tests()

