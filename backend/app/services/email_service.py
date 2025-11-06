"""
Email service for sending booking confirmation and notification emails.

Requirements: 5.4
"""
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.config import settings
from app.models.booking import Booking
from app.models.user import User


logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Custom exception for email errors"""
    pass


class EmailService:
    """Service class for email operations with retry logic"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.max_retries = 5
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email with retry logic.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
            
        Returns:
            True if email sent successfully, False otherwise
            
        Requirements: 5.4
        """
        message = MIMEMultipart('alternative')
        message['From'] = self.from_email
        message['To'] = to_email
        message['Subject'] = subject
        
        # Add plain text version if provided
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            message.attach(text_part)
        
        # Add HTML version
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                await self._send_smtp(to_email, message)
                logger.info(f"Email sent successfully to {to_email}")
                return True
                
            except Exception as e:
                logger.warning(
                    f"Email send attempt {attempt + 1}/{self.max_retries} failed: {str(e)}"
                )
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to send email to {to_email} after {self.max_retries} attempts")
                    return False
        
        return False
    
    async def _send_smtp(self, to_email: str, message: MIMEMultipart):
        """
        Send email via SMTP.
        
        Args:
            to_email: Recipient email address
            message: Email message object
            
        Raises:
            Exception: If SMTP send fails
        """
        async with aiosmtplib.SMTP(
            hostname=self.smtp_host,
            port=self.smtp_port,
            use_tls=False,
            start_tls=True
        ) as smtp:
            if self.smtp_user and self.smtp_password:
                await smtp.login(self.smtp_user, self.smtp_password)
            
            await smtp.send_message(message)
    
    async def send_booking_confirmation_to_client(
        self,
        booking: Booking,
        client: User,
        coach: User
    ) -> bool:
        """
        Send booking confirmation email to client.
        
        Args:
            booking: Booking object
            client: Client user object
            coach: Coach user object
            
        Returns:
            True if email sent successfully, False otherwise
            
        Requirements: 5.4
        """
        coach_profile = coach.coach_profile
        client_profile = client.client_profile
        
        if not client_profile or not coach_profile:
            logger.error("Missing profile data for email")
            return False
        
        # Format session datetime
        session_date = booking.session_datetime.strftime("%B %d, %Y")
        session_time = booking.session_datetime.strftime("%I:%M %p")
        
        subject = f"Booking Confirmed: Session with {coach_profile.first_name} {coach_profile.last_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4F46E5; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Hi {client_profile.first_name},</p>
                    <p>Your coaching session has been confirmed. We're excited for your upcoming session!</p>
                    
                    <div class="details">
                        <h3>Session Details</h3>
                        <p><strong>Coach:</strong> {coach_profile.first_name} {coach_profile.last_name}</p>
                        <p><strong>Date:</strong> {session_date}</p>
                        <p><strong>Time:</strong> {session_time}</p>
                        <p><strong>Duration:</strong> {booking.duration_minutes} minutes</p>
                        <p><strong>Booking ID:</strong> {booking.id}</p>
                    </div>
                    
                    <p>You will receive a meeting link closer to your session time.</p>
                    
                    <p>If you need to reschedule or have any questions, please contact us.</p>
                    
                    <p>Best regards,<br>The CultureBridge Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 CultureBridge. All rights reserved.</p>
                    <p>This is an automated message, please do not reply directly to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Booking Confirmed!
        
        Hi {client_profile.first_name},
        
        Your coaching session has been confirmed. We're excited for your upcoming session!
        
        Session Details:
        - Coach: {coach_profile.first_name} {coach_profile.last_name}
        - Date: {session_date}
        - Time: {session_time}
        - Duration: {booking.duration_minutes} minutes
        - Booking ID: {booking.id}
        
        You will receive a meeting link closer to your session time.
        
        If you need to reschedule or have any questions, please contact us.
        
        Best regards,
        The CultureBridge Team
        
        © 2025 CultureBridge. All rights reserved.
        """
        
        return await self.send_email(
            to_email=client.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_booking_confirmation_to_coach(
        self,
        booking: Booking,
        client: User,
        coach: User
    ) -> bool:
        """
        Send booking confirmation email to coach.
        
        Args:
            booking: Booking object
            client: Client user object
            coach: Coach user object
            
        Returns:
            True if email sent successfully, False otherwise
            
        Requirements: 5.4
        """
        coach_profile = coach.coach_profile
        client_profile = client.client_profile
        
        if not client_profile or not coach_profile:
            logger.error("Missing profile data for email")
            return False
        
        # Format session datetime
        session_date = booking.session_datetime.strftime("%B %d, %Y")
        session_time = booking.session_datetime.strftime("%I:%M %p")
        
        # Calculate payment amount
        duration_hours = booking.duration_minutes / 60
        amount = float(coach_profile.hourly_rate) * duration_hours
        
        subject = f"New Booking: Session with {client_profile.first_name} {client_profile.last_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #10B981; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Booking Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Hi {coach_profile.first_name},</p>
                    <p>You have a new confirmed booking!</p>
                    
                    <div class="details">
                        <h3>Session Details</h3>
                        <p><strong>Client:</strong> {client_profile.first_name} {client_profile.last_name}</p>
                        <p><strong>Date:</strong> {session_date}</p>
                        <p><strong>Time:</strong> {session_time}</p>
                        <p><strong>Duration:</strong> {booking.duration_minutes} minutes</p>
                        <p><strong>Payment:</strong> {coach_profile.currency} {amount:.2f}</p>
                        <p><strong>Booking ID:</strong> {booking.id}</p>
                    </div>
                    
                    <p>Please prepare for your session and ensure you're available at the scheduled time.</p>
                    
                    <p>You can create and share a meeting link with your client through the platform.</p>
                    
                    <p>Best regards,<br>The CultureBridge Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 CultureBridge. All rights reserved.</p>
                    <p>This is an automated message, please do not reply directly to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Booking Confirmed!
        
        Hi {coach_profile.first_name},
        
        You have a new confirmed booking!
        
        Session Details:
        - Client: {client_profile.first_name} {client_profile.last_name}
        - Date: {session_date}
        - Time: {session_time}
        - Duration: {booking.duration_minutes} minutes
        - Payment: {coach_profile.currency} {amount:.2f}
        - Booking ID: {booking.id}
        
        Please prepare for your session and ensure you're available at the scheduled time.
        
        You can create and share a meeting link with your client through the platform.
        
        Best regards,
        The CultureBridge Team
        
        © 2025 CultureBridge. All rights reserved.
        """
        
        return await self.send_email(
            to_email=coach.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_booking_confirmations(
        self,
        booking: Booking,
        client: User,
        coach: User
    ) -> Dict[str, bool]:
        """
        Send booking confirmation emails to both client and coach.
        
        This method sends emails concurrently to both parties within 2 minutes
        of booking confirmation as required.
        
        Args:
            booking: Booking object
            client: Client user object
            coach: Coach user object
            
        Returns:
            Dictionary with success status for client and coach emails
            
        Requirements: 5.4
        """
        # Send both emails concurrently
        client_task = self.send_booking_confirmation_to_client(booking, client, coach)
        coach_task = self.send_booking_confirmation_to_coach(booking, client, coach)
        
        client_result, coach_result = await asyncio.gather(
            client_task,
            coach_task,
            return_exceptions=True
        )
        
        return {
            'client_email_sent': client_result if isinstance(client_result, bool) else False,
            'coach_email_sent': coach_result if isinstance(coach_result, bool) else False
        }


# Global email service instance
email_service = EmailService()
