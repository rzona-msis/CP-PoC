"""
Unit tests for Booking Data Access Layer.

Tests booking CRUD operations and conflict detection logic.
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_access.booking_dal import BookingDAL
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.models.database import init_database, get_db_connection


@pytest.fixture
def test_db_with_data():
    """Create test database with sample user and resource."""
    init_database()
    
    # Create test user
    user_id = UserDAL.create_user("Test User", "test@example.com", "password", "student")
    
    # Create test resource
    resource_id = ResourceDAL.create_resource(
        owner_id=user_id,
        title="Test Resource",
        status="published"
    )
    
    yield {'user_id': user_id, 'resource_id': resource_id}
    
    # Cleanup
    conn = get_db_connection()
    conn.execute("DELETE FROM bookings")
    conn.execute("DELETE FROM resources")
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()


def test_create_booking(test_db_with_data):
    """Test booking creation."""
    data = test_db_with_data
    
    booking_id = BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-15 10:00:00",
        end_datetime="2025-11-15 12:00:00",
        status="pending",
        notes="Test booking"
    )
    
    assert booking_id is not None
    assert booking_id > 0
    
    # Verify booking was created
    booking = BookingDAL.get_booking_by_id(booking_id)
    assert booking is not None
    assert booking['resource_id'] == data['resource_id']
    assert booking['status'] == "pending"


def test_conflict_detection(test_db_with_data):
    """Test booking conflict detection."""
    data = test_db_with_data
    
    # Create first booking (10:00 - 12:00)
    BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-15 10:00:00",
        end_datetime="2025-11-15 12:00:00",
        status="approved"
    )
    
    # Test overlapping booking (11:00 - 13:00) - should conflict
    has_conflict = BookingDAL.has_conflict(
        resource_id=data['resource_id'],
        start_datetime="2025-11-15 11:00:00",
        end_datetime="2025-11-15 13:00:00"
    )
    assert has_conflict is True
    
    # Test non-overlapping booking (13:00 - 15:00) - should not conflict
    has_conflict = BookingDAL.has_conflict(
        resource_id=data['resource_id'],
        start_datetime="2025-11-15 13:00:00",
        end_datetime="2025-11-15 15:00:00"
    )
    assert has_conflict is False
    
    # Test exact match (10:00 - 12:00) - should conflict
    has_conflict = BookingDAL.has_conflict(
        resource_id=data['resource_id'],
        start_datetime="2025-11-15 10:00:00",
        end_datetime="2025-11-15 12:00:00"
    )
    assert has_conflict is True


def test_conflict_prevention(test_db_with_data):
    """Test that creating conflicting booking raises error."""
    data = test_db_with_data
    
    # Create first booking
    BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-15 10:00:00",
        end_datetime="2025-11-15 12:00:00",
        status="approved"
    )
    
    # Attempt to create conflicting booking
    with pytest.raises(ValueError, match="conflict"):
        BookingDAL.create_booking(
            resource_id=data['resource_id'],
            requester_id=data['user_id'],
            start_datetime="2025-11-15 11:00:00",
            end_datetime="2025-11-15 13:00:00",
            status="pending"
        )


def test_update_booking_status(test_db_with_data):
    """Test updating booking status."""
    data = test_db_with_data
    
    booking_id = BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-15 10:00:00",
        end_datetime="2025-11-15 12:00:00",
        status="pending"
    )
    
    # Update status
    success = BookingDAL.update_booking_status(booking_id, "approved")
    assert success is True
    
    # Verify status changed
    booking = BookingDAL.get_booking_by_id(booking_id)
    assert booking['status'] == "approved"
    
    # Test invalid status
    with pytest.raises(ValueError, match="Invalid status"):
        BookingDAL.update_booking_status(booking_id, "invalid_status")


def test_get_bookings_for_user(test_db_with_data):
    """Test retrieving bookings for a specific user."""
    data = test_db_with_data
    
    # Create multiple bookings
    BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-15 10:00:00",
        end_datetime="2025-11-15 12:00:00",
        status="approved"
    )
    BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-16 14:00:00",
        end_datetime="2025-11-16 16:00:00",
        status="pending"
    )
    
    # Get all bookings
    bookings = BookingDAL.get_bookings_for_user(data['user_id'])
    assert len(bookings) == 2
    
    # Get only pending bookings
    pending = BookingDAL.get_bookings_for_user(data['user_id'], status="pending")
    assert len(pending) == 1
    assert pending[0]['status'] == "pending"


def test_get_booking_statistics(test_db_with_data):
    """Test booking statistics aggregation."""
    data = test_db_with_data
    
    # Create bookings with different statuses
    BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-15 10:00:00",
        end_datetime="2025-11-15 12:00:00",
        status="approved"
    )
    BookingDAL.create_booking(
        resource_id=data['resource_id'],
        requester_id=data['user_id'],
        start_datetime="2025-11-16 10:00:00",
        end_datetime="2025-11-16 12:00:00",
        status="pending"
    )
    
    stats = BookingDAL.get_booking_statistics()
    assert stats['total_bookings'] == 2
    assert stats['approved'] == 1
    assert stats['pending'] == 1

