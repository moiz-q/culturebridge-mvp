"""
Calendar service for Google Calendar and Outlook integration.

Requirements: 5.5
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import json

from app.models.booking import Booking


class CalendarError(Exception):
    """Custom exception for calendar errors"""
    pass


class CalendarService:
    """
    Service class for calendar integration operations.
    
    This is a foundational implementation that provides the structure for
    Google Calendar and Outlook integration. Full OAuth implementation and
    API calls would be added in production.
    
    Requirements: 5.5
    """
    
    def __init__(self):
        """Initialize calendar service"""
        pass
    
    def create_google_calendar_event(
        self,
        booking: Booking,
        access_token: str,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Create a Google Calendar event for a booking.
        
        Args:
            booking: Booking object
            access_token: Google OAuth access token
            timezone: Timezone for the event (default UTC)
            
        Returns:
            Dictionary with event details including event_id and html_link
            
        Raises:
            CalendarError: If event creation fails
            
        Requirements: 5.5
        
        Note: This is a placeholder implementation. In production, this would:
        1. Use the Google Calendar API client library
        2. Make authenticated API calls to create events
        3. Handle OAuth token refresh
        4. Add attendees (client and coach emails)
        5. Set up meeting reminders
        """
        try:
            # Calculate end time
            end_time = booking.session_datetime + timedelta(minutes=booking.duration_minutes)
            
            # Build event data structure (Google Calendar API format)
            event_data = {
                "summary": f"Coaching Session - CultureBridge",
                "description": self._build_event_description(booking),
                "start": {
                    "dateTime": booking.session_datetime.isoformat(),
                    "timeZone": timezone
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": timezone
                },
                "attendees": [
                    {"email": booking.client.email},
                    {"email": booking.coach.email}
                ],
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},  # 1 day before
                        {"method": "popup", "minutes": 30}  # 30 minutes before
                    ]
                },
                "conferenceData": {
                    "createRequest": {
                        "requestId": str(booking.id),
                        "conferenceSolutionKey": {"type": "hangoutsMeet"}
                    }
                }
            }
            
            # In production, make API call here:
            # from googleapiclient.discovery import build
            # service = build('calendar', 'v3', credentials=credentials)
            # event = service.events().insert(
            #     calendarId='primary',
            #     body=event_data,
            #     conferenceDataVersion=1
            # ).execute()
            
            # For now, return mock response
            return {
                "event_id": f"google_event_{booking.id}",
                "html_link": f"https://calendar.google.com/event?eid={booking.id}",
                "meeting_link": f"https://meet.google.com/{booking.id}",
                "status": "confirmed"
            }
            
        except Exception as e:
            raise CalendarError(f"Failed to create Google Calendar event: {str(e)}")
    
    def create_outlook_calendar_event(
        self,
        booking: Booking,
        access_token: str,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Create an Outlook Calendar event for a booking.
        
        Args:
            booking: Booking object
            access_token: Microsoft OAuth access token
            timezone: Timezone for the event (default UTC)
            
        Returns:
            Dictionary with event details including event_id and web_link
            
        Raises:
            CalendarError: If event creation fails
            
        Requirements: 5.5
        
        Note: This is a placeholder implementation. In production, this would:
        1. Use the Microsoft Graph API
        2. Make authenticated API calls to create events
        3. Handle OAuth token refresh
        4. Add attendees (client and coach emails)
        5. Set up Teams meeting link
        """
        try:
            # Calculate end time
            end_time = booking.session_datetime + timedelta(minutes=booking.duration_minutes)
            
            # Build event data structure (Microsoft Graph API format)
            event_data = {
                "subject": "Coaching Session - CultureBridge",
                "body": {
                    "contentType": "HTML",
                    "content": self._build_event_description(booking)
                },
                "start": {
                    "dateTime": booking.session_datetime.isoformat(),
                    "timeZone": timezone
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": timezone
                },
                "attendees": [
                    {
                        "emailAddress": {"address": booking.client.email},
                        "type": "required"
                    },
                    {
                        "emailAddress": {"address": booking.coach.email},
                        "type": "required"
                    }
                ],
                "isOnlineMeeting": True,
                "onlineMeetingProvider": "teamsForBusiness"
            }
            
            # In production, make API call here:
            # import requests
            # headers = {
            #     'Authorization': f'Bearer {access_token}',
            #     'Content-Type': 'application/json'
            # }
            # response = requests.post(
            #     'https://graph.microsoft.com/v1.0/me/events',
            #     headers=headers,
            #     json=event_data
            # )
            # event = response.json()
            
            # For now, return mock response
            return {
                "event_id": f"outlook_event_{booking.id}",
                "web_link": f"https://outlook.office.com/calendar/item/{booking.id}",
                "meeting_link": f"https://teams.microsoft.com/l/meetup-join/{booking.id}",
                "status": "confirmed"
            }
            
        except Exception as e:
            raise CalendarError(f"Failed to create Outlook Calendar event: {str(e)}")
    
    def update_google_calendar_event(
        self,
        event_id: str,
        booking: Booking,
        access_token: str,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Update a Google Calendar event.
        
        Args:
            event_id: Google Calendar event ID
            booking: Updated booking object
            access_token: Google OAuth access token
            timezone: Timezone for the event
            
        Returns:
            Dictionary with updated event details
            
        Raises:
            CalendarError: If event update fails
        """
        try:
            # In production, implement event update logic
            # This would use the Google Calendar API to update the event
            
            return {
                "event_id": event_id,
                "status": "updated"
            }
            
        except Exception as e:
            raise CalendarError(f"Failed to update Google Calendar event: {str(e)}")
    
    def update_outlook_calendar_event(
        self,
        event_id: str,
        booking: Booking,
        access_token: str,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Update an Outlook Calendar event.
        
        Args:
            event_id: Outlook Calendar event ID
            booking: Updated booking object
            access_token: Microsoft OAuth access token
            timezone: Timezone for the event
            
        Returns:
            Dictionary with updated event details
            
        Raises:
            CalendarError: If event update fails
        """
        try:
            # In production, implement event update logic
            # This would use the Microsoft Graph API to update the event
            
            return {
                "event_id": event_id,
                "status": "updated"
            }
            
        except Exception as e:
            raise CalendarError(f"Failed to update Outlook Calendar event: {str(e)}")
    
    def delete_google_calendar_event(
        self,
        event_id: str,
        access_token: str
    ) -> bool:
        """
        Delete a Google Calendar event.
        
        Args:
            event_id: Google Calendar event ID
            access_token: Google OAuth access token
            
        Returns:
            True if deletion was successful
            
        Raises:
            CalendarError: If event deletion fails
        """
        try:
            # In production, implement event deletion logic
            # This would use the Google Calendar API to delete the event
            
            return True
            
        except Exception as e:
            raise CalendarError(f"Failed to delete Google Calendar event: {str(e)}")
    
    def delete_outlook_calendar_event(
        self,
        event_id: str,
        access_token: str
    ) -> bool:
        """
        Delete an Outlook Calendar event.
        
        Args:
            event_id: Outlook Calendar event ID
            access_token: Microsoft OAuth access token
            
        Returns:
            True if deletion was successful
            
        Raises:
            CalendarError: If event deletion fails
        """
        try:
            # In production, implement event deletion logic
            # This would use the Microsoft Graph API to delete the event
            
            return True
            
        except Exception as e:
            raise CalendarError(f"Failed to delete Outlook Calendar event: {str(e)}")
    
    def sync_booking_to_calendar(
        self,
        booking: Booking,
        calendar_type: str,
        access_token: str,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Sync a booking to the specified calendar service.
        
        Args:
            booking: Booking object to sync
            calendar_type: Type of calendar ('google' or 'outlook')
            access_token: OAuth access token for the calendar service
            timezone: Timezone for the event
            
        Returns:
            Dictionary with event details including meeting link
            
        Raises:
            CalendarError: If sync fails or calendar type is invalid
            
        Requirements: 5.5
        """
        if calendar_type.lower() == "google":
            return self.create_google_calendar_event(booking, access_token, timezone)
        elif calendar_type.lower() == "outlook":
            return self.create_outlook_calendar_event(booking, access_token, timezone)
        else:
            raise CalendarError(f"Unsupported calendar type: {calendar_type}")
    
    def _build_event_description(self, booking: Booking) -> str:
        """
        Build event description with booking details.
        
        Args:
            booking: Booking object
            
        Returns:
            Formatted event description
        """
        client_name = "Unknown"
        coach_name = "Unknown"
        
        if booking.client and booking.client.client_profile:
            client_name = booking.client.client_profile.get_full_name()
        
        if booking.coach and booking.coach.coach_profile:
            coach_name = booking.coach.coach_profile.get_full_name()
        
        description = f"""
CultureBridge Coaching Session

Client: {client_name}
Coach: {coach_name}
Duration: {booking.duration_minutes} minutes
Booking ID: {booking.id}

"""
        
        if booking.notes:
            description += f"\nNotes:\n{booking.notes}\n"
        
        description += "\nThis is an automated calendar event created by CultureBridge."
        
        return description.strip()


class OAuthService:
    """
    Service for handling OAuth flows for calendar integrations.
    
    This is a foundational implementation. In production, this would handle:
    - OAuth authorization URL generation
    - Token exchange from authorization codes
    - Token refresh
    - Token storage and retrieval
    
    Requirements: 5.5
    """
    
    def __init__(self):
        """Initialize OAuth service"""
        pass
    
    def get_google_auth_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str
    ) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            client_id: Google OAuth client ID
            redirect_uri: Redirect URI after authorization
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL
            
        Requirements: 5.5
        """
        # In production, use google-auth library
        scopes = [
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/calendar"
        ]
        
        # Build authorization URL
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # In production, properly encode parameters
        return f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={'+'.join(scopes)}&state={state}"
    
    def get_outlook_auth_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str
    ) -> str:
        """
        Generate Microsoft OAuth authorization URL.
        
        Args:
            client_id: Microsoft OAuth client ID
            redirect_uri: Redirect URI after authorization
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL
            
        Requirements: 5.5
        """
        # In production, use msal library
        scopes = [
            "Calendars.ReadWrite",
            "OnlineMeetings.ReadWrite"
        ]
        
        # Build authorization URL
        base_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "response_mode": "query"
        }
        
        # In production, properly encode parameters
        return f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={'+'.join(scopes)}&state={state}"
    
    def exchange_google_code_for_token(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange Google authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Dictionary with access_token, refresh_token, and expiry
            
        Requirements: 5.5
        """
        # In production, make token exchange request
        # This would use the Google OAuth token endpoint
        
        return {
            "access_token": "mock_google_access_token",
            "refresh_token": "mock_google_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
    
    def exchange_outlook_code_for_token(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange Microsoft authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            client_id: Microsoft OAuth client ID
            client_secret: Microsoft OAuth client secret
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Dictionary with access_token, refresh_token, and expiry
            
        Requirements: 5.5
        """
        # In production, make token exchange request
        # This would use the Microsoft OAuth token endpoint
        
        return {
            "access_token": "mock_outlook_access_token",
            "refresh_token": "mock_outlook_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
    
    def refresh_google_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str
    ) -> Dict[str, Any]:
        """
        Refresh Google access token.
        
        Args:
            refresh_token: Google refresh token
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            
        Returns:
            Dictionary with new access_token and expiry
        """
        # In production, make token refresh request
        return {
            "access_token": "new_mock_google_access_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
    
    def refresh_outlook_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str
    ) -> Dict[str, Any]:
        """
        Refresh Microsoft access token.
        
        Args:
            refresh_token: Microsoft refresh token
            client_id: Microsoft OAuth client ID
            client_secret: Microsoft OAuth client secret
            
        Returns:
            Dictionary with new access_token and expiry
        """
        # In production, make token refresh request
        return {
            "access_token": "new_mock_outlook_access_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
