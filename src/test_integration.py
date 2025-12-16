"""
Integration tests for Google Calendar feature.
"""
import sqlite3
import time

def test_database_schema():
    """Test that the database has the correct schema with Google Calendar fields."""
    print("=" * 60)
    print("Testing Database Schema")
    print("=" * 60)
    
    # Wait a moment for database to be created
    time.sleep(2)
    
    try:
        conn = sqlite3.connect('src/campus_hub.db')
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute('PRAGMA table_info(users)')
        user_columns = {row[1] for row in cursor.fetchall()}
        
        print("\nUSERS TABLE:")
        for col in sorted(user_columns):
            print(f"  - {col}")
        
        # Check for Google Calendar fields in users
        required_user_fields = {
            'google_calendar_token',
            'google_calendar_refresh_token',
            'google_calendar_token_expiry'
        }
        
        missing_user_fields = required_user_fields - user_columns
        if missing_user_fields:
            print(f"\n[FAIL] Missing user fields: {missing_user_fields}")
            return False
        else:
            print("\n[PASS] All Google Calendar fields present in users table")
        
        # Check bookings table
        cursor.execute('PRAGMA table_info(bookings)')
        booking_columns = {row[1] for row in cursor.fetchall()}
        
        print("\nBOOKINGS TABLE:")
        for col in sorted(booking_columns):
            print(f"  - {col}")
        
        # Check for calendar_event_id in bookings
        if 'calendar_event_id' not in booking_columns:
            print("\n[FAIL] Missing calendar_event_id field in bookings")
            return False
        else:
            print("\n[PASS] calendar_event_id field present in bookings table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def test_imports():
    """Test that all Google Calendar modules can be imported."""
    print("\n" + "=" * 60)
    print("Testing Module Imports")
    print("=" * 60)
    
    try:
        print("\nTesting imports...")
        from src.services.google_calendar_service import GoogleCalendarService, calendar_service
        print("  [OK] google_calendar_service imported")
        
        from src.controllers.google_calendar import google_calendar_bp
        print("  [OK] google_calendar controller imported")
        
        from src.data_access.user_dal import update_user_calendar_tokens, disconnect_user_calendar
        print("  [OK] user_dal calendar functions imported")
        
        from src.data_access.booking_dal import BookingDAL
        print("  [OK] booking_dal imported")
        
        # Test service instantiation
        service = GoogleCalendarService()
        print(f"\n  Calendar service configured: {service.is_configured}")
        print(f"  Calendar service enabled: {service.is_enabled()}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] IMPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_blueprint_registration():
    """Test that the Google Calendar blueprint is registered."""
    print("\n" + "=" * 60)
    print("Testing Blueprint Registration")
    print("=" * 60)
    
    try:
        from src.app import create_app
        app = create_app()
        
        # Check if calendar routes exist
        calendar_routes = [rule.rule for rule in app.url_map.iter_rules() if '/calendar' in rule.rule]
        
        print("\nRegistered calendar routes:")
        for route in calendar_routes:
            print(f"  - {route}")
        
        required_routes = {
            '/calendar/connect',
            '/calendar/callback',
            '/calendar/disconnect'
        }
        
        found_routes = {route for route in calendar_routes}
        missing_routes = required_routes - found_routes
        
        if missing_routes:
            print(f"\n[FAIL] Missing routes: {missing_routes}")
            return False
        else:
            print("\n[PASS] All required calendar routes registered")
            return True
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_data():
    """Test that sample data was created."""
    print("\n" + "=" * 60)
    print("Testing Sample Data")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('src/campus_hub.db')
        cursor = conn.cursor()
        
        # Check users
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"\n  Users in database: {user_count}")
        
        # Check resources
        cursor.execute('SELECT COUNT(*) FROM resources')
        resource_count = cursor.fetchone()[0]
        print(f"  Resources in database: {resource_count}")
        
        # Check bookings
        cursor.execute('SELECT COUNT(*) FROM bookings')
        booking_count = cursor.fetchone()[0]
        print(f"  Bookings in database: {booking_count}")
        
        conn.close()
        
        if user_count > 0 and resource_count > 0:
            print("\n[PASS] Sample data exists")
            return True
        else:
            print("\n[FAIL] No sample data found")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("GOOGLE CALENDAR INTEGRATION TESTS")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Database Schema", test_database_schema()))
    results.append(("Module Imports", test_imports()))
    results.append(("Blueprint Registration", test_blueprint_registration()))
    results.append(("Sample Data", test_sample_data()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n*** All integration tests passed! ***")
        print("\nNext steps:")
        print("1. Set up Google Cloud credentials (see GOOGLE_CALENDAR_SETUP.md)")
        print("2. Add credentials to .env file")
        print("3. Test OAuth flow by connecting a calendar")
    else:
        print("\n*** Some tests failed. Please review the errors above. ***")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

