"""
Data validation checks for migration integrity.

Requirements: 10.3, 10.4
"""
import csv
import os
from typing import Dict, List, Tuple
from datetime import datetime
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.profile import ClientProfile, CoachProfile
from app.models.booking import Booking, Payment
from migration.config import config

logger = logging.getLogger(__name__)


class MigrationValidator:
    """Validate data integrity after migration"""
    
    def __init__(self, db: Session = None):
        """
        Initialize migration validator.
        
        Args:
            db: Database session (optional)
        """
        self.db = db or SessionLocal()
        self.validation_results = {
            "row_counts": {},
            "referential_integrity": {},
            "data_quality": {},
            "errors": []
        }
    
    def validate_row_counts(self) -> Dict[str, Dict]:
        """
        Validate row counts between Phase 1 CSV and Phase 2 database.
        
        Requirements: 10.3
        
        Returns:
            Dictionary with row count comparisons
        """
        logger.info("Validating row counts...")
        
        results = {}
        
        # Users
        phase1_users = self._count_csv_rows(os.path.join(config.EXPORT_DIR, "users.csv"))
        phase2_users = self.db.query(func.count(User.id)).scalar()
        results["users"] = {
            "phase1": phase1_users,
            "phase2": phase2_users,
            "match": phase1_users == phase2_users,
            "difference": phase2_users - phase1_users
        }
        
        # Client profiles
        phase1_clients = self._count_csv_rows(os.path.join(config.EXPORT_DIR, "client_profiles.csv"))
        phase2_clients = self.db.query(func.count(ClientProfile.id)).scalar()
        results["client_profiles"] = {
            "phase1": phase1_clients,
            "phase2": phase2_clients,
            "match": phase1_clients == phase2_clients,
            "difference": phase2_clients - phase1_clients
        }
        
        # Coach profiles
        phase1_coaches = self._count_csv_rows(os.path.join(config.EXPORT_DIR, "coach_profiles.csv"))
        phase2_coaches = self.db.query(func.count(CoachProfile.id)).scalar()
        results["coach_profiles"] = {
            "phase1": phase1_coaches,
            "phase2": phase2_coaches,
            "match": phase1_coaches == phase2_coaches,
            "difference": phase2_coaches - phase1_coaches
        }
        
        # Bookings
        phase1_bookings = self._count_csv_rows(os.path.join(config.EXPORT_DIR, "bookings.csv"))
        phase2_bookings = self.db.query(func.count(Booking.id)).scalar()
        results["bookings"] = {
            "phase1": phase1_bookings,
            "phase2": phase2_bookings,
            "match": phase1_bookings == phase2_bookings,
            "difference": phase2_bookings - phase1_bookings
        }
        
        # Payments
        phase1_payments = self._count_csv_rows(os.path.join(config.EXPORT_DIR, "payments.csv"))
        phase2_payments = self.db.query(func.count(Payment.id)).scalar()
        results["payments"] = {
            "phase1": phase1_payments,
            "phase2": phase2_payments,
            "match": phase1_payments == phase2_payments,
            "difference": phase2_payments - phase1_payments
        }
        
        self.validation_results["row_counts"] = results
        
        # Log results
        for entity, counts in results.items():
            if counts["match"]:
                logger.info(f"✓ {entity}: {counts['phase2']} records (match)")
            else:
                logger.warning(f"✗ {entity}: Phase1={counts['phase1']}, Phase2={counts['phase2']} (diff={counts['difference']})")
        
        return results
    
    def validate_referential_integrity(self) -> Dict[str, Dict]:
        """
        Validate referential integrity between tables.
        
        Requirements: 10.3
        
        Returns:
            Dictionary with referential integrity checks
        """
        logger.info("Validating referential integrity...")
        
        results = {}
        
        # Check client profiles have valid user references
        orphaned_client_profiles = self.db.query(ClientProfile).filter(
            ~ClientProfile.user_id.in_(self.db.query(User.id))
        ).count()
        results["client_profiles_user_ref"] = {
            "orphaned": orphaned_client_profiles,
            "valid": orphaned_client_profiles == 0
        }
        
        # Check coach profiles have valid user references
        orphaned_coach_profiles = self.db.query(CoachProfile).filter(
            ~CoachProfile.user_id.in_(self.db.query(User.id))
        ).count()
        results["coach_profiles_user_ref"] = {
            "orphaned": orphaned_coach_profiles,
            "valid": orphaned_coach_profiles == 0
        }
        
        # Check bookings have valid client references
        orphaned_booking_clients = self.db.query(Booking).filter(
            ~Booking.client_id.in_(self.db.query(User.id))
        ).count()
        results["bookings_client_ref"] = {
            "orphaned": orphaned_booking_clients,
            "valid": orphaned_booking_clients == 0
        }
        
        # Check bookings have valid coach references
        orphaned_booking_coaches = self.db.query(Booking).filter(
            ~Booking.coach_id.in_(self.db.query(User.id))
        ).count()
        results["bookings_coach_ref"] = {
            "orphaned": orphaned_booking_coaches,
            "valid": orphaned_booking_coaches == 0
        }
        
        # Check payments have valid booking references
        orphaned_payments = self.db.query(Payment).filter(
            ~Payment.booking_id.in_(self.db.query(Booking.id))
        ).count()
        results["payments_booking_ref"] = {
            "orphaned": orphaned_payments,
            "valid": orphaned_payments == 0
        }
        
        self.validation_results["referential_integrity"] = results
        
        # Log results
        for check, result in results.items():
            if result["valid"]:
                logger.info(f"✓ {check}: No orphaned records")
            else:
                logger.error(f"✗ {check}: {result['orphaned']} orphaned records")
                self.validation_results["errors"].append({
                    "check": check,
                    "error": f"{result['orphaned']} orphaned records"
                })
        
        return results
    
    def validate_data_quality(self) -> Dict[str, Dict]:
        """
        Validate data quality and business rules.
        
        Requirements: 10.4
        
        Returns:
            Dictionary with data quality checks
        """
        logger.info("Validating data quality...")
        
        results = {}
        
        # Check for users with invalid emails
        invalid_emails = self.db.query(User).filter(
            ~User.email.contains('@')
        ).count()
        results["user_emails"] = {
            "invalid": invalid_emails,
            "valid": invalid_emails == 0
        }
        
        # Check for users without profiles
        users_without_profiles = self.db.query(User).filter(
            User.role.in_(['client', 'coach']),
            ~User.id.in_(
                self.db.query(ClientProfile.user_id).union(
                    self.db.query(CoachProfile.user_id)
                )
            )
        ).count()
        results["users_with_profiles"] = {
            "missing": users_without_profiles,
            "valid": users_without_profiles == 0
        }
        
        # Check for coach profiles with invalid hourly rates
        invalid_rates = self.db.query(CoachProfile).filter(
            (CoachProfile.hourly_rate < 25) | (CoachProfile.hourly_rate > 500)
        ).count()
        results["coach_hourly_rates"] = {
            "invalid": invalid_rates,
            "valid": invalid_rates == 0
        }
        
        # Check for bookings with invalid durations
        invalid_durations = self.db.query(Booking).filter(
            Booking.duration_minutes <= 0
        ).count()
        results["booking_durations"] = {
            "invalid": invalid_durations,
            "valid": invalid_durations == 0
        }
        
        # Check for payments with invalid amounts
        invalid_amounts = self.db.query(Payment).filter(
            Payment.amount <= 0
        ).count()
        results["payment_amounts"] = {
            "invalid": invalid_amounts,
            "valid": invalid_amounts == 0
        }
        
        # Check for bookings without payments (for confirmed/completed bookings)
        bookings_without_payments = self.db.query(Booking).filter(
            Booking.status.in_(['confirmed', 'completed']),
            Booking.payment_id.is_(None)
        ).count()
        results["confirmed_bookings_with_payments"] = {
            "missing": bookings_without_payments,
            "valid": bookings_without_payments == 0
        }
        
        self.validation_results["data_quality"] = results
        
        # Log results
        for check, result in results.items():
            if result["valid"]:
                logger.info(f"✓ {check}: All records valid")
            else:
                logger.warning(f"⚠ {check}: {result.get('invalid', result.get('missing', 0))} invalid records")
                self.validation_results["errors"].append({
                    "check": check,
                    "error": f"{result.get('invalid', result.get('missing', 0))} invalid records"
                })
        
        return results
    
    def validate_sample_data(self, sample_size: int = 10) -> Dict[str, List]:
        """
        Validate a random sample of migrated data.
        
        Requirements: 10.4
        
        Args:
            sample_size: Number of records to sample (default 10%)
            
        Returns:
            Dictionary with sample validation results
        """
        logger.info(f"Validating random sample of {sample_size} records...")
        
        results = {
            "users": [],
            "profiles": [],
            "bookings": []
        }
        
        # Sample users
        sample_users = self.db.query(User).limit(sample_size).all()
        for user in sample_users:
            validation = {
                "id": str(user.id),
                "email": user.email,
                "valid_email": user.validate_email(),
                "has_profile": (
                    user.client_profile is not None if user.is_client() 
                    else user.coach_profile is not None if user.is_coach()
                    else True
                )
            }
            results["users"].append(validation)
        
        # Sample coach profiles
        sample_coaches = self.db.query(CoachProfile).limit(sample_size).all()
        for coach in sample_coaches:
            validation = {
                "id": str(coach.id),
                "user_id": str(coach.user_id),
                "valid_rate": coach.validate_hourly_rate() if coach.hourly_rate else True,
                "has_languages": len(coach.languages or []) > 0,
                "has_expertise": len(coach.expertise or []) > 0
            }
            results["profiles"].append(validation)
        
        # Sample bookings
        sample_bookings = self.db.query(Booking).limit(sample_size).all()
        for booking in sample_bookings:
            validation = {
                "id": str(booking.id),
                "valid_duration": booking.validate_duration(),
                "has_payment": booking.payment is not None,
                "status": booking.status.value
            }
            results["bookings"].append(validation)
        
        return results
    
    def _count_csv_rows(self, filepath: str) -> int:
        """
        Count rows in CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Number of rows (excluding header)
        """
        if not os.path.exists(filepath):
            logger.warning(f"CSV file not found: {filepath}")
            return 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                return sum(1 for _ in reader)
        except Exception as e:
            logger.error(f"Error counting rows in {filepath}: {str(e)}")
            return 0
    
    def get_validation_results(self) -> Dict:
        """Get all validation results"""
        return self.validation_results
    
    def has_errors(self) -> bool:
        """Check if validation found any errors"""
        return len(self.validation_results["errors"]) > 0
    
    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()


def main():
    """Main function to run validation"""
    try:
        validator = MigrationValidator()
        
        print("\n=== Migration Validation ===\n")
        
        # Row count validation
        print("1. Row Count Validation")
        row_counts = validator.validate_row_counts()
        
        # Referential integrity validation
        print("\n2. Referential Integrity Validation")
        ref_integrity = validator.validate_referential_integrity()
        
        # Data quality validation
        print("\n3. Data Quality Validation")
        data_quality = validator.validate_data_quality()
        
        # Sample data validation
        print("\n4. Sample Data Validation")
        sample_data = validator.validate_sample_data(sample_size=10)
        
        # Summary
        print("\n=== Validation Summary ===")
        if validator.has_errors():
            print(f"❌ Validation FAILED with {len(validator.validation_results['errors'])} errors")
            for error in validator.validation_results["errors"][:5]:
                print(f"  - {error['check']}: {error['error']}")
            return 1
        else:
            print("✅ All validation checks PASSED")
            return 0
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return 1
    finally:
        validator.close()


if __name__ == "__main__":
    exit(main())
