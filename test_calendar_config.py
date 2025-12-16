"""
Quick test to verify Google Calendar configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Google Calendar Configuration Test")
print("=" * 60)

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

print(f"\nGOOGLE_CLIENT_ID: {'✅ SET' if client_id else '❌ NOT SET'}")
if client_id:
    print(f"  Value: {client_id[:20]}...")

print(f"\nGOOGLE_CLIENT_SECRET: {'✅ SET' if client_secret else '❌ NOT SET'}")
if client_secret:
    print(f"  Value: {client_secret[:10]}...")

print(f"\nGOOGLE_REDIRECT_URI: {'✅ SET' if redirect_uri else '❌ NOT SET'}")
if redirect_uri:
    print(f"  Value: {redirect_uri}")

print("\n" + "=" * 60)

# Test the service
try:
    from src.services.google_calendar_service import calendar_service
    
    is_enabled = calendar_service.is_enabled()
    print(f"Calendar Service Enabled: {'✅ YES' if is_enabled else '❌ NO'}")
    
    if is_enabled:
        print("\n✅ Google Calendar is properly configured!")
        print("Students should be able to connect their calendars.")
    else:
        print("\n❌ Google Calendar service reports as NOT configured")
        print("Checking service internals...")
        print(f"  - Service client_id: {'SET' if calendar_service.client_id else 'NOT SET'}")
        print(f"  - Service client_secret: {'SET' if calendar_service.client_secret else 'NOT SET'}")
        print(f"  - Service is_configured: {calendar_service.is_configured}")
        
except Exception as e:
    print(f"\n❌ Error testing service: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)

