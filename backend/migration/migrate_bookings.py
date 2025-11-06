"""
Booking and payment migration scripts.

Requirements: 10.1, 10.2
"""
import csv
import uuid
import json
from typing import Dict, List, Tuple
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.booking import Booking, BookingStatus, Payment, PaymentStatus
from migration.field_mapper import FieldMapper
from migration.config import config

logger = logging.getLogger(__name__)


class BookingMigrator:
    """Migrate bookings and payments from Phase 1 to Phase 2"""
    
    def __init__(self, user_id_mapping: Dict[str, str] = None, db: Session = None):
        """
        Initialize booking migrator.
        
        Args:
            user_id_mapping: Mapping of Phase 1 user IDs to Phase 2 UUIDs
            db: Database session (optional)
        """
        self.db = db or SessionLocal()
        self.mapper = FieldMapper()
        self.user_id_mapping = user_id_mapping or {}
        self.booking_id_mapping: Dict[str, str] = {}  # Phase 1 -> Phase 2
        self.stats = {
            "bookings": {"total": 0, "success": 0, "failed": 0, "errors": []},
            "payments": {"total": 0, "success": 0, "failed": 0, "errors": []}
        }
    
    def load_user_id_mapping(self, filepath: str):
        """
        Load user ID mapping from file.
        
        Args:
            filepath: Path to mapping file
        """
        with open(filepath, 'r') as f:
            self.user_id_mapping = json.load(f)
        logger.info(f"Loaded {len(self.user_id_mapping)} user ID mappings")
    
    def migrate_bookings(self, csv_path: str) -> Tuple[int, int, List[Dict]]:
        """
        Migrate bookings from CSV file.
        
        Args:
            csv_path: Path to bookings CSV file
            
        Returns:
            Tuple of (success_count, failed_count, error_list)
        """
        logger.info(f"Starting booking migration from {csv_path}")
        start_time = datetime.now()
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    self.stats["bookings"]["total"] += 1
                    
                    try:
                        self._migrate_booking(row)
                        self.stats["bookings"]["success"] += 1
                        
                        if self.stats["bookings"]["success"] % 100 == 0:
                            logger.info(f"Migrated {self.stats['bookings']['success']} bookings...")
                    
                    except Exception as e:
                        self.stats["bookings"]["failed"] += 1
                        error_info = {
                            "booking_id": row.get("_id", "unknown"),
                            "error": str(e)
                        }
                        self.stats["bookings"]["errors"].append(error_info)
                        logger.error(f"Failed to migrate booking: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error during booking migration: {str(e)}")
            self.db.rollback()
            raise
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Booking migration completed in {duration:.2f} seconds")
        
        return (
            self.stats["bookings"]["success"],
            self.stats["bookings"]["failed"],
            self.stats["bookings"]["errors"]
        )
    
    def _migrate_booking(self, phase1_data: Dict) -> Booking:
        """
        Migrate a single booking record.
        
        Args:
            phase1_data: Booking data from Phase 1
            
        Returns:
            Created Booking object
        """
        # Map fields from Phase 1 to Phase 2
        mapped_data = self.mapper.map_booking_fields(phase1_data)
        
        # Get Phase 2 user IDs
        phase1_client_id = phase1_data.get("client_user_id") or phase1_data.get("client_id")
        phase1_coach_id = phase1_data.get("coach_user_id") or phase1_data.get("coach_id")
        
        if not phase1_client_id or not phase1_coach_id:
            raise ValueError("Missing client_id or coach_id in booking data")
        
        phase2_client_id = self.user_id_mapping.get(str(phase1_client_id))
        phase2_coach_id = self.user_id_mapping.get(str(phase1_coach_id))
        
        if not phase2_client_id:
            raise ValueError(f"Client ID mapping not found for {phase1_client_id}")
        if not phase2_coach_id:
            raise ValueError(f"Coach ID mapping not found for {phase1_coach_id}")
        
        # Generate new UUID for Phase 2
        new_booking_id = uuid.uuid4()
        
        # Create booking object
        booking = Booking(
            id=new_booking_id,
            client_id=uuid.UUID(phase2_client_id),
            coach_id=uuid.UUID(phase2_coach_id),
            session_datetime=mapped_data.get("session_datetime"),
            duration_minutes=mapped_data.get("duration_minutes", 60),
            status=BookingStatus(mapped_data.get("status", "pending")),
            meeting_link=mapped_data.get("meeting_link"),
            notes=mapped_data.get("notes"),
            created_at=mapped_data.get("created_at") or datetime.utcnow(),
            updated_at=mapped_data.get("updated_at") or datetime.utcnow()
        )
        
        # Validate
        if not booking.validate_duration():
            raise ValueError(f"Invalid duration: {booking.duration_minutes}")
        
        # Add to database
        try:
            self.db.add(booking)
            self.db.flush()
            
            # Store ID mapping for payment migration
            phase1_id = phase1_data.get("_id") or phase1_data.get("id")
            if phase1_id:
                self.booking_id_mapping[str(phase1_id)] = str(new_booking_id)
            
            logger.debug(f"Migrated booking {new_booking_id}")
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        
        return booking
    
    def migrate_payments(self, csv_path: str) -> Tuple[int, int, List[Dict]]:
        """
        Migrate payments from CSV file.
        
        Args:
            csv_path: Path to payments CSV file
            
        Returns:
            Tuple of (success_count, failed_count, error_list)
        """
        logger.info(f"Starting payment migration from {csv_path}")
        start_time = datetime.now()
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    self.stats["payments"]["total"] += 1
                    
                    try:
                        self._migrate_payment(row)
                        self.stats["payments"]["success"] += 1
                        
                        if self.stats["payments"]["success"] % 100 == 0:
                            logger.info(f"Migrated {self.stats['payments']['success']} payments...")
                    
                    except Exception as e:
                        self.stats["payments"]["failed"] += 1
                        error_info = {
                            "payment_id": row.get("_id", "unknown"),
                            "error": str(e)
                        }
                        self.stats["payments"]["errors"].append(error_info)
                        logger.error(f"Failed to migrate payment: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error during payment migration: {str(e)}")
            self.db.rollback()
            raise
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Payment migration completed in {duration:.2f} seconds")
        
        return (
            self.stats["payments"]["success"],
            self.stats["payments"]["failed"],
            self.stats["payments"]["errors"]
        )
    
    def _migrate_payment(self, phase1_data: Dict) -> Payment:
        """
        Migrate a single payment record.
        
        Args:
            phase1_data: Payment data from Phase 1
            
        Returns:
            Created Payment object
        """
        # Map fields from Phase 1 to Phase 2
        mapped_data = self.mapper.map_payment_fields(phase1_data)
        
        # Get Phase 2 booking ID
        phase1_booking_id = phase1_data.get("booking_ref") or phase1_data.get("booking_id")
        if not phase1_booking_id:
            raise ValueError("Missing booking_id in payment data")
        
        phase2_booking_id = self.booking_id_mapping.get(str(phase1_booking_id))
        if not phase2_booking_id:
            raise ValueError(f"Booking ID mapping not found for {phase1_booking_id}")
        
        # Create payment object
        payment = Payment(
            id=uuid.uuid4(),
            booking_id=uuid.UUID(phase2_booking_id),
            amount=mapped_data.get("amount"),
            currency=mapped_data.get("currency", "USD"),
            status=PaymentStatus(mapped_data.get("status", "pending")),
            stripe_session_id=mapped_data.get("stripe_session_id"),
            stripe_payment_intent_id=mapped_data.get("stripe_payment_intent_id"),
            created_at=mapped_data.get("created_at") or datetime.utcnow(),
            updated_at=mapped_data.get("updated_at") or datetime.utcnow()
        )
        
        # Validate
        if not payment.validate_amount():
            raise ValueError(f"Invalid payment amount: {payment.amount}")
        
        # Add to database
        try:
            self.db.add(payment)
            self.db.flush()
            
            # Update booking with payment_id
            booking = self.db.query(Booking).filter(Booking.id == payment.booking_id).first()
            if booking:
                booking.payment_id = payment.id
                self.db.flush()
            
            logger.debug(f"Migrated payment {payment.id}")
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        
        return payment
    
    def save_booking_id_mapping(self, filepath: str):
        """
        Save booking ID mapping to file.
        
        Args:
            filepath: Path to save mapping file
        """
        with open(filepath, 'w') as f:
            json.dump(self.booking_id_mapping, f, indent=2)
        logger.info(f"Saved booking ID mapping to {filepath}")
    
    def get_stats(self) -> Dict:
        """Get migration statistics"""
        return self.stats
    
    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()


def main():
    """Main function to run booking and payment migration"""
    import os
    
    user_mapping_path = os.path.join(config.EXPORT_DIR, "user_id_mapping.json")
    bookings_csv_path = os.path.join(config.EXPORT_DIR, "bookings.csv")
    payments_csv_path = os.path.join(config.EXPORT_DIR, "payments.csv")
    booking_mapping_path = os.path.join(config.EXPORT_DIR, "booking_id_mapping.json")
    
    if not os.path.exists(user_mapping_path):
        logger.error(f"User ID mapping file not found: {user_mapping_path}")
        return 1
    
    try:
        migrator = BookingMigrator()
        migrator.load_user_id_mapping(user_mapping_path)
        
        # Migrate bookings
        if os.path.exists(bookings_csv_path):
            booking_success, booking_failed, booking_errors = migrator.migrate_bookings(bookings_csv_path)
            print(f"\n=== Booking Migration Summary ===")
            print(f"Success: {booking_success}, Failed: {booking_failed}")
            
            # Save booking ID mapping for payment migration
            migrator.save_booking_id_mapping(booking_mapping_path)
        
        # Migrate payments
        if os.path.exists(payments_csv_path):
            payment_success, payment_failed, payment_errors = migrator.migrate_payments(payments_csv_path)
            print(f"\n=== Payment Migration Summary ===")
            print(f"Success: {payment_success}, Failed: {payment_failed}")
        
        migrator.close()
        return 0
        
    except Exception as e:
        logger.error(f"Booking/Payment migration failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
