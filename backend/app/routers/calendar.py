"""
Calendar API endpoints for Google Calendar and Outlook integration.

Requirements: 5.5
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.services.calendar_service import CalendarService, OAuthService, CalendarError
from app.services.booking_service import BookingService

router = APIRouter(prefix="/calendar", tags=["calendar"])


class CalendarAuthUrlResponse(BaseModel):
    """Schema for calendar authorization URL response"""
    auth_url: str = Field(..., description="OAuth authorization URL")
    state: str = Field(..., description="State parameter for CSRF protection")
    
    class Config:
        schema_extra = {
            "example": {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
                "state": "random_state_string"
            }
        }


class CalendarTokenExchangeRequest(BaseModel):
    """Schema for token exchange request"""
    code: str = Field(..., description="Authorization code from OAuth callback")
    state: str = Field(..., description="State parameter for verification")
    
    class Config:
        schema_extra = {
            "example": {
                "code": "4/0AY0e-g7...",
                "state": "random_state_string"
            }
        }


class CalendarTokenResponse(BaseModel):
    """Schema for calendar token response"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "ya29.a0AfH6...",
                "refresh_token": "1//0gHZ...",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
        }


class BookingSyncRequest(BaseModel):
    """Schema for booking sync request"""
    booking_id: UUID = Field(..., description="Booking ID to sync")
    calendar_type: str = Field(..., description="Calendar type (google or outlook)")
    access_token: str = Field(..., description="OAuth access token")
    timezone: str = Field("UTC", description="Timezone for the event")
    
    class Config:
        schema_extra = {
            "example": {
                "booking_id": "123e4567-e89b-12d3-a456-426614174000",
                "calendar_type": "google",
                "access_token": "ya29.a0AfH6...",
                "timezone": "America/New_York"
            }
        }


class BookingSyncResponse(BaseModel):
    """Schema for booking sync response"""
    event_id: str
    meeting_link: Optional[str]
    status: str
    
    class Config:
        schema_extra = {
            "example": {
                "event_id": "google_event_123",
                "meeting_link": "https://meet.google.com/abc-defg-hij",
                "status": "confirmed"
            }
        }


@router.get(
    "/google/auth-url",
    response_model=CalendarAuthUrlResponse,
    summary="Get Google Calendar authorization URL",
    description="Generate OAuth authorization URL for Google Calendar integration"
)
def get_google_auth_url(
    redirect_uri: str = Query(..., description="Redirect URI after authorization"),
    current_user: User = Depends(get_current_user)
):
    """
    Get Google Calendar OAuth authorization URL.
    
    This endpoint generates the URL that users should visit to authorize
    the application to access their Google Calendar.
    
    Requirements: 5.5
    """
    oauth_service = OAuthService()
    
    # Generate state parameter for CSRF protection
    # In production, store this in session or database
    import secrets
    state = secrets.token_urlsafe(32)
    
    # Get client ID from environment (in production)
    # For now, use placeholder
    client_id = "YOUR_GOOGLE_CLIENT_ID"
    
    auth_url = oauth_service.get_google_auth_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state
    )
    
    return CalendarAuthUrlResponse(
        auth_url=auth_url,
        state=state
    )


@router.get(
    "/outlook/auth-url",
    response_model=CalendarAuthUrlResponse,
    summary="Get Outlook Calendar authorization URL",
    description="Generate OAuth authorization URL for Outlook Calendar integration"
)
def get_outlook_auth_url(
    redirect_uri: str = Query(..., description="Redirect URI after authorization"),
    current_user: User = Depends(get_current_user)
):
    """
    Get Outlook Calendar OAuth authorization URL.
    
    This endpoint generates the URL that users should visit to authorize
    the application to access their Outlook Calendar.
    
    Requirements: 5.5
    """
    oauth_service = OAuthService()
    
    # Generate state parameter for CSRF protection
    import secrets
    state = secrets.token_urlsafe(32)
    
    # Get client ID from environment (in production)
    client_id = "YOUR_MICROSOFT_CLIENT_ID"
    
    auth_url = oauth_service.get_outlook_auth_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state
    )
    
    return CalendarAuthUrlResponse(
        auth_url=auth_url,
        state=state
    )


@router.post(
    "/google/exchange-token",
    response_model=CalendarTokenResponse,
    summary="Exchange Google authorization code for token",
    description="Exchange authorization code for Google Calendar access token"
)
def exchange_google_token(
    token_request: CalendarTokenExchangeRequest,
    redirect_uri: str = Query(..., description="Redirect URI used in authorization"),
    current_user: User = Depends(get_current_user)
):
    """
    Exchange Google authorization code for access token.
    
    After user authorizes the application, they are redirected back with
    an authorization code. This endpoint exchanges that code for an
    access token and refresh token.
    
    Requirements: 5.5
    """
    oauth_service = OAuthService()
    
    # In production, verify state parameter matches stored value
    
    # Get credentials from environment
    client_id = "YOUR_GOOGLE_CLIENT_ID"
    client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
    
    try:
        tokens = oauth_service.exchange_google_code_for_token(
            code=token_request.code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        
        # In production, store tokens securely in database
        # associated with current_user.id
        
        return CalendarTokenResponse(**tokens)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange token: {str(e)}"
        )


@router.post(
    "/outlook/exchange-token",
    response_model=CalendarTokenResponse,
    summary="Exchange Outlook authorization code for token",
    description="Exchange authorization code for Outlook Calendar access token"
)
def exchange_outlook_token(
    token_request: CalendarTokenExchangeRequest,
    redirect_uri: str = Query(..., description="Redirect URI used in authorization"),
    current_user: User = Depends(get_current_user)
):
    """
    Exchange Outlook authorization code for access token.
    
    After user authorizes the application, they are redirected back with
    an authorization code. This endpoint exchanges that code for an
    access token and refresh token.
    
    Requirements: 5.5
    """
    oauth_service = OAuthService()
    
    # In production, verify state parameter matches stored value
    
    # Get credentials from environment
    client_id = "YOUR_MICROSOFT_CLIENT_ID"
    client_secret = "YOUR_MICROSOFT_CLIENT_SECRET"
    
    try:
        tokens = oauth_service.exchange_outlook_code_for_token(
            code=token_request.code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        
        # In production, store tokens securely in database
        # associated with current_user.id
        
        return CalendarTokenResponse(**tokens)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange token: {str(e)}"
        )


@router.post(
    "/sync-booking",
    response_model=BookingSyncResponse,
    summary="Sync booking to calendar",
    description="Create a calendar event for a booking"
)
def sync_booking_to_calendar(
    sync_request: BookingSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync a booking to Google Calendar or Outlook Calendar.
    
    This endpoint creates a calendar event for the specified booking
    and returns the event details including meeting link.
    
    Requirements: 5.5
    """
    booking_service = BookingService(db)
    calendar_service = CalendarService()
    
    # Get booking
    booking = booking_service.get_booking(sync_request.booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Authorization: Only client or coach can sync their bookings
    if not current_user.is_admin():
        if booking.client_id != current_user.id and booking.coach_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to sync this booking"
            )
    
    # Sync to calendar
    try:
        event_details = calendar_service.sync_booking_to_calendar(
            booking=booking,
            calendar_type=sync_request.calendar_type,
            access_token=sync_request.access_token,
            timezone=sync_request.timezone
        )
        
        # Update booking with meeting link
        if event_details.get("meeting_link"):
            booking.meeting_link = event_details["meeting_link"]
            booking_service.booking_repo.update(booking)
        
        return BookingSyncResponse(
            event_id=event_details["event_id"],
            meeting_link=event_details.get("meeting_link"),
            status=event_details["status"]
        )
        
    except CalendarError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
