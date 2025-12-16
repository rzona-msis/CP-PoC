"""
Google Calendar Integration Service

This module handles all Google Calendar API interactions including:
- OAuth2 authentication flow
- Creating calendar events for bookings
- Updating and deleting calendar events
- Token management and refresh
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# OAuth2 scopes required for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Google OAuth2 client configuration
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/google/callback")],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}


class GoogleCalendarService:
    """Service for managing Google Calendar integration."""
    
    def __init__(self):
        """Initialize the Google Calendar service."""
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/google/callback")
        self.is_configured = bool(self.client_id and self.client_secret)
    
    def is_enabled(self) -> bool:
        """Check if Google Calendar integration is properly configured."""
        return self.is_configured
    
    def get_authorization_url(self, state: str) -> Optional[str]:
        """
        Generate the OAuth2 authorization URL for user to grant calendar access.
        
        Args:
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL or None if not configured
        """
        if not self.is_configured:
            return None
        
        try:
            flow = Flow.from_client_config(
                CLIENT_CONFIG,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            return authorization_url
        except Exception as e:
            print(f"Error generating authorization URL: {e}")
            return None
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Dictionary with token, refresh_token, and expiry or None
        """
        if not self.is_configured:
            return None
        
        try:
            flow = Flow.from_client_config(
                CLIENT_CONFIG,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            return {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    def get_credentials(self, token: str, refresh_token: str, token_expiry: str) -> Optional[Credentials]:
        """
        Create credentials object from stored tokens.
        
        Args:
            token: Access token
            refresh_token: Refresh token
            token_expiry: Token expiry datetime as ISO string
            
        Returns:
            Credentials object or None
        """
        try:
            expiry = datetime.fromisoformat(token_expiry) if token_expiry else None
            
            credentials = Credentials(
                token=token,
                refresh_token=refresh_token,
                token_uri=CLIENT_CONFIG['web']['token_uri'],
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=SCOPES,
                expiry=expiry
            )
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            return credentials
        except Exception as e:
            print(f"Error creating credentials: {e}")
            return None
    
    def create_booking_event(
        self,
        credentials: Credentials,
        booking_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a calendar event for a booking.
        
        Args:
            credentials: User's Google Calendar credentials
            booking_data: Dictionary containing booking details
            
        Returns:
            Calendar event ID or None if failed
        """
        try:
            service = build('calendar', 'v3', credentials=credentials)
            
            # Parse datetime strings
            start_dt = datetime.fromisoformat(booking_data['start_datetime'].replace(' ', 'T'))
            end_dt = datetime.fromisoformat(booking_data['end_datetime'].replace(' ', 'T'))
            
            # Create event
            event = {
                'summary': f"🎓 {booking_data['resource_title']}",
                'location': booking_data.get('location', ''),
                'description': self._create_event_description(booking_data),
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'America/Indiana/Indianapolis',  # IU timezone
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'America/Indiana/Indianapolis',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
                'colorId': '10',  # Green color for resource bookings
            }
            
            # Add notes if present
            if booking_data.get('notes'):
                event['description'] += f"\n\nNotes: {booking_data['notes']}"
            
            # Insert event
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            
            return created_event.get('id')
            
        except HttpError as e:
            print(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None
    
    def update_booking_event(
        self,
        credentials: Credentials,
        event_id: str,
        booking_data: Dict[str, Any]
    ) -> bool:
        """
        Update an existing calendar event.
        
        Args:
            credentials: User's Google Calendar credentials
            event_id: Calendar event ID to update
            booking_data: Updated booking details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Parse datetime strings
            start_dt = datetime.fromisoformat(booking_data['start_datetime'].replace(' ', 'T'))
            end_dt = datetime.fromisoformat(booking_data['end_datetime'].replace(' ', 'T'))
            
            # Update event fields
            event['summary'] = f"🎓 {booking_data['resource_title']}"
            event['location'] = booking_data.get('location', '')
            event['description'] = self._create_event_description(booking_data)
            event['start'] = {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'America/Indiana/Indianapolis',
            }
            event['end'] = {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'America/Indiana/Indianapolis',
            }
            
            if booking_data.get('notes'):
                event['description'] += f"\n\nNotes: {booking_data['notes']}"
            
            # Update event
            service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            
            return True
            
        except HttpError as e:
            print(f"Google Calendar API error: {e}")
            return False
        except Exception as e:
            print(f"Error updating calendar event: {e}")
            return False
    
    def delete_booking_event(self, credentials: Credentials, event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            credentials: User's Google Calendar credentials
            event_id: Calendar event ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            service = build('calendar', 'v3', credentials=credentials)
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
            
        except HttpError as e:
            print(f"Google Calendar API error: {e}")
            return False
        except Exception as e:
            print(f"Error deleting calendar event: {e}")
            return False
    
    def _create_event_description(self, booking_data: Dict[str, Any]) -> str:
        """
        Create a formatted event description from booking data.
        
        Args:
            booking_data: Booking details
            
        Returns:
            Formatted description string
        """
        description = f"Campus Resource Booking\n"
        description += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        description += f"Resource: {booking_data['resource_title']}\n"
        
        if booking_data.get('category'):
            description += f"Category: {booking_data['category']}\n"
        
        if booking_data.get('location'):
            description += f"Location: {booking_data['location']}\n"
        
        if booking_data.get('capacity'):
            description += f"Capacity: {booking_data['capacity']} people\n"
        
        description += f"\nBooking ID: #{booking_data['booking_id']}\n"
        description += f"Status: {booking_data['status'].title()}\n"
        
        description += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
        description += "Managed by Campus Resource Hub"
        
        return description


# Global service instance
calendar_service = GoogleCalendarService()

