"""
Admin service for analytics, reporting, and administrative operations.

Requirements: 7.1, 7.2, 7.5
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import csv
import io

from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus, Payment, PaymentStatus
from app.models.profile import ClientProfile, CoachProfile
from app.models.community import Post, Comment
from app.repositories.user_repository import UserRepository
from app.repositories.booking_repository import BookingRepository


class AdminError(Exception):
    """Custom exception for admin operations"""
    pass


class AuditLog:
    """Simple audit log entry"""
    def __init__(self, admin_id: UUID, action: str, target_type: str, target_id: UUID, details: Optional[Dict] = None):
        self.admin_id = admin_id
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def __repr__(self):
        return f"<AuditLog(admin={self.admin_id}, action={self.action}, target={self.target_type}:{self.target_id})>"


class AdminService:
    """Service class for admin operations and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.booking_repo = BookingRepository(db)
        self.audit_logs: List[AuditLog] = []
    
    def get_platform_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get platform analytics for the specified number of days.
        
        Args:
            days: Number of days to look back (default 30)
            
        Returns:
            Dictionary containing platform metrics:
            - total_users: Total number of users
            - total_clients: Total number of clients
            - total_coaches: Total number of coaches
            - active_sessions: Number of confirmed/completed sessions in period
            - session_volume: Total number of bookings in period
            - total_revenue: Total revenue in period
            - revenue_by_currency: Revenue breakdown by currency
            - new_users: Number of new users in period
            - avg_session_duration: Average session duration in minutes
            
        Requirements: 7.1, 7.2
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total users by role
        total_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        total_clients = self.db.query(func.count(User.id)).filter(
            User.role == UserRole.CLIENT,
            User.is_active == True
        ).scalar() or 0
        total_coaches = self.db.query(func.count(User.id)).filter(
            User.role == UserRole.COACH,
            User.is_active == True
        ).scalar() or 0
        
        # New users in period
        new_users = self.db.query(func.count(User.id)).filter(
            User.created_at >= start_date
        ).scalar() or 0
        
        # Active sessions (confirmed or completed) in period
        active_sessions = self.db.query(func.count(Booking.id)).filter(
            Booking.session_datetime >= start_date,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
        ).scalar() or 0
        
        # Total session volume (all bookings) in period
        session_volume = self.db.query(func.count(Booking.id)).filter(
            Booking.created_at >= start_date
        ).scalar() or 0
        
        # Revenue calculations
        revenue_query = self.db.query(
            func.sum(Payment.amount).label('total'),
            Payment.currency
        ).join(Booking).filter(
            Payment.status == PaymentStatus.SUCCEEDED,
            Booking.session_datetime >= start_date
        ).group_by(Payment.currency).all()
        
        total_revenue = Decimal('0.00')
        revenue_by_currency = {}
        
        for row in revenue_query:
            amount = row.total or Decimal('0.00')
            currency = row.currency
            revenue_by_currency[currency] = float(amount)
            if currency == 'USD':
                total_revenue += amount
        
        # Average session duration
        avg_duration = self.db.query(func.avg(Booking.duration_minutes)).filter(
            Booking.created_at >= start_date,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
        ).scalar() or 0
        
        # Booking status breakdown
        status_breakdown = {}
        for status in BookingStatus:
            count = self.db.query(func.count(Booking.id)).filter(
                Booking.created_at >= start_date,
                Booking.status == status
            ).scalar() or 0
            status_breakdown[status.value] = count
        
        return {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'total_users': total_users,
            'total_clients': total_clients,
            'total_coaches': total_coaches,
            'new_users': new_users,
            'active_sessions': active_sessions,
            'session_volume': session_volume,
            'total_revenue_usd': float(total_revenue),
            'revenue_by_currency': revenue_by_currency,
            'avg_session_duration_minutes': float(avg_duration) if avg_duration else 0,
            'booking_status_breakdown': status_breakdown
        }
    
    def get_revenue_report(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = 'day'
    ) -> List[Dict[str, Any]]:
        """
        Generate revenue report for a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            group_by: Grouping period ('day', 'week', 'month')
            
        Returns:
            List of revenue data points grouped by period
            
        Requirements: 7.5
        """
        # Query successful payments in date range
        payments = self.db.query(
            Payment.amount,
            Payment.currency,
            Payment.created_at,
            Booking.session_datetime
        ).join(Booking).filter(
            Payment.status == PaymentStatus.SUCCEEDED,
            Booking.session_datetime >= start_date,
            Booking.session_datetime <= end_date
        ).all()
        
        # Group by period
        revenue_data = {}
        
        for payment in payments:
            # Determine period key
            if group_by == 'day':
                period_key = payment.session_datetime.strftime('%Y-%m-%d')
            elif group_by == 'week':
                period_key = payment.session_datetime.strftime('%Y-W%U')
            elif group_by == 'month':
                period_key = payment.session_datetime.strftime('%Y-%m')
            else:
                period_key = payment.session_datetime.strftime('%Y-%m-%d')
            
            if period_key not in revenue_data:
                revenue_data[period_key] = {
                    'period': period_key,
                    'total_usd': Decimal('0.00'),
                    'by_currency': {},
                    'transaction_count': 0
                }
            
            # Add to totals
            revenue_data[period_key]['transaction_count'] += 1
            
            currency = payment.currency
            if currency not in revenue_data[period_key]['by_currency']:
                revenue_data[period_key]['by_currency'][currency] = Decimal('0.00')
            
            revenue_data[period_key]['by_currency'][currency] += payment.amount
            
            if currency == 'USD':
                revenue_data[period_key]['total_usd'] += payment.amount
        
        # Convert to list and format
        result = []
        for period_key in sorted(revenue_data.keys()):
            data = revenue_data[period_key]
            result.append({
                'period': data['period'],
                'total_usd': float(data['total_usd']),
                'by_currency': {k: float(v) for k, v in data['by_currency'].items()},
                'transaction_count': data['transaction_count']
            })
        
        return result
    
    def export_users_csv(self, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Export users data to CSV format.
        
        Args:
            filters: Optional filters (role, is_active, etc.)
            
        Returns:
            CSV string containing user data
            
        Requirements: 7.5
        """
        query = self.db.query(User)
        
        # Apply filters
        if filters:
            if 'role' in filters:
                query = query.filter(User.role == filters['role'])
            if 'is_active' in filters:
                query = query.filter(User.is_active == filters['is_active'])
            if 'created_after' in filters:
                query = query.filter(User.created_at >= filters['created_after'])
        
        users = query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Email', 'Role', 'Is Active', 'Email Verified',
            'Created At', 'Updated At'
        ])
        
        # Data rows
        for user in users:
            writer.writerow([
                str(user.id),
                user.email,
                user.role.value,
                user.is_active,
                user.email_verified,
                user.created_at.isoformat(),
                user.updated_at.isoformat()
            ])
        
        return output.getvalue()
    
    def export_bookings_csv(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """
        Export bookings data to CSV format.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            CSV string containing booking data
            
        Requirements: 7.5
        """
        query = self.db.query(Booking)
        
        if start_date:
            query = query.filter(Booking.session_datetime >= start_date)
        if end_date:
            query = query.filter(Booking.session_datetime <= end_date)
        
        bookings = query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Booking ID', 'Client ID', 'Client Email', 'Coach ID', 'Coach Email',
            'Session DateTime', 'Duration (min)', 'Status', 'Payment ID',
            'Created At', 'Updated At'
        ])
        
        # Data rows
        for booking in bookings:
            writer.writerow([
                str(booking.id),
                str(booking.client_id),
                booking.client.email,
                str(booking.coach_id),
                booking.coach.email,
                booking.session_datetime.isoformat(),
                booking.duration_minutes,
                booking.status.value,
                str(booking.payment_id) if booking.payment_id else '',
                booking.created_at.isoformat(),
                booking.updated_at.isoformat()
            ])
        
        return output.getvalue()
    
    def export_revenue_csv(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """
        Export revenue data to CSV format.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CSV string containing revenue data
            
        Requirements: 7.5
        """
        payments = self.db.query(
            Payment.id,
            Payment.amount,
            Payment.currency,
            Payment.status,
            Payment.created_at,
            Booking.id.label('booking_id'),
            Booking.client_id,
            Booking.coach_id,
            Booking.session_datetime
        ).join(Booking).filter(
            Booking.session_datetime >= start_date,
            Booking.session_datetime <= end_date
        ).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Payment ID', 'Booking ID', 'Client ID', 'Coach ID',
            'Amount', 'Currency', 'Status', 'Session DateTime', 'Payment Created At'
        ])
        
        # Data rows
        for payment in payments:
            writer.writerow([
                str(payment.id),
                str(payment.booking_id),
                str(payment.client_id),
                str(payment.coach_id),
                float(payment.amount),
                payment.currency,
                payment.status.value,
                payment.session_datetime.isoformat(),
                payment.created_at.isoformat()
            ])
        
        return output.getvalue()
    
    def log_admin_action(
        self,
        admin_id: UUID,
        action: str,
        target_type: str,
        target_id: UUID,
        details: Optional[Dict] = None
    ):
        """
        Log an admin action for audit purposes.
        
        Args:
            admin_id: ID of admin performing action
            action: Action performed (e.g., 'delete_user', 'update_user', 'delete_post')
            target_type: Type of target (e.g., 'user', 'post', 'booking')
            target_id: ID of target entity
            details: Optional additional details
            
        Requirements: 7.2
        """
        log_entry = AuditLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details
        )
        
        self.audit_logs.append(log_entry)
        
        # In production, this would write to a database table or logging service
        # For now, we'll just keep it in memory
        print(f"[AUDIT] {log_entry}")
    
    def get_user_activity_history(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get activity history for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing user activity data
            
        Requirements: 7.4
        """
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            raise AdminError("User not found")
        
        # Get bookings
        if user.is_client():
            bookings = self.db.query(Booking).filter(Booking.client_id == user_id).all()
        elif user.is_coach():
            bookings = self.db.query(Booking).filter(Booking.coach_id == user_id).all()
        else:
            bookings = []
        
        # Get payments
        payment_ids = [b.payment_id for b in bookings if b.payment_id]
        payments = self.db.query(Payment).filter(Payment.id.in_(payment_ids)).all() if payment_ids else []
        
        # Get community activity
        posts = self.db.query(Post).filter(Post.author_id == user_id).all()
        comments = self.db.query(Comment).filter(Comment.author_id == user_id).all()
        
        return {
            'user_id': str(user_id),
            'email': user.email,
            'role': user.role.value,
            'created_at': user.created_at.isoformat(),
            'bookings': {
                'total': len(bookings),
                'by_status': {
                    status.value: len([b for b in bookings if b.status == status])
                    for status in BookingStatus
                }
            },
            'payments': {
                'total': len(payments),
                'total_amount_usd': float(sum(p.amount for p in payments if p.currency == 'USD' and p.status == PaymentStatus.SUCCEEDED))
            },
            'community': {
                'posts_created': len(posts),
                'comments_made': len(comments),
                'total_post_upvotes': sum(p.upvotes for p in posts)
            }
        }
