"""
Main migration orchestrator script.

This script coordinates the entire migration process from Phase 1 to Phase 2:
1. Export data from Bubble API
2. Migrate users with password re-hashing
3. Migrate client and coach profiles
4. Migrate bookings and payments
5. Validate data integrity
6. Generate comprehensive reports

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

from migration.config import config
from migration.bubble_export import BubbleExporter
from migration.migrate_users import UserMigrator
from migration.migrate_profiles import ProfileMigrator
from migration.migrate_bookings import BookingMigrator
from migration.validation import MigrationValidator
from migration.reporting import MigrationReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.REPORT_DIR, f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MigrationOrchestrator:
    """Orchestrate the complete migration process"""
    
    def __init__(self, skip_export: bool = False):
        """
        Initialize migration orchestrator.
        
        Args:
            skip_export: Skip Bubble export if data already exists
        """
        self.skip_export = skip_export
        self.migration_data: Dict[str, Any] = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "user_stats": {},
            "profile_stats": {},
            "booking_stats": {},
            "validation_results": {},
            "report_paths": {}
        }
        
        # Create necessary directories
        os.makedirs(config.EXPORT_DIR, exist_ok=True)
        os.makedirs(config.REPORT_DIR, exist_ok=True)
    
    def run(self) -> int:
        """
        Run the complete migration process.
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        logger.info("=" * 80)
        logger.info("STARTING CULTUREBRIDGE PHASE 1 TO PHASE 2 MIGRATION")
        logger.info("=" * 80)
        
        self.migration_data["start_time"] = datetime.now()
        
        try:
            # Step 1: Export data from Bubble
            if not self.skip_export:
                logger.info("\n[STEP 1/6] Exporting data from Bubble API...")
                self._export_bubble_data()
            else:
                logger.info("\n[STEP 1/6] Skipping Bubble export (using existing data)")
            
            # Step 2: Migrate users
            logger.info("\n[STEP 2/6] Migrating users...")
            self._migrate_users()
            
            # Step 3: Migrate profiles
            logger.info("\n[STEP 3/6] Migrating profiles...")
            self._migrate_profiles()
            
            # Step 4: Migrate bookings and payments
            logger.info("\n[STEP 4/6] Migrating bookings and payments...")
            self._migrate_bookings()
            
            # Step 5: Validate data
            logger.info("\n[STEP 5/6] Validating migrated data...")
            self._validate_data()
            
            # Step 6: Generate reports
            logger.info("\n[STEP 6/6] Generating migration reports...")
            self._generate_reports()
            
            # Calculate duration
            self.migration_data["end_time"] = datetime.now()
            duration = self.migration_data["end_time"] - self.migration_data["start_time"]
            self.migration_data["duration_seconds"] = duration.total_seconds()
            
            # Final summary
            self._print_summary()
            
            # Check for errors
            if self._has_critical_errors():
                logger.error("Migration completed with CRITICAL ERRORS")
                return 1
            else:
                logger.info("Migration completed SUCCESSFULLY")
                return 0
        
        except Exception as e:
            logger.error(f"Migration failed with exception: {str(e)}", exc_info=True)
            return 1
    
    def _export_bubble_data(self):
        """Export data from Bubble API"""
        try:
            exporter = BubbleExporter()
            exported_files = exporter.export_all()
            
            if not exported_files:
                raise Exception("No data exported from Bubble API")
            
            logger.info(f"Successfully exported {len(exported_files)} data files")
            
        except Exception as e:
            logger.error(f"Bubble export failed: {str(e)}")
            raise
    
    def _migrate_users(self):
        """Migrate users with password re-hashing"""
        try:
            csv_path = os.path.join(config.EXPORT_DIR, "users.csv")
            mapping_path = os.path.join(config.EXPORT_DIR, "user_id_mapping.json")
            
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Users CSV not found: {csv_path}")
            
            migrator = UserMigrator()
            success, failed, errors = migrator.migrate_from_csv(csv_path)
            
            # Save ID mapping
            migrator.save_id_mapping(mapping_path)
            
            # Store stats
            self.migration_data["user_stats"] = migrator.get_stats()
            
            migrator.close()
            
            logger.info(f"User migration: {success} success, {failed} failed")
            
        except Exception as e:
            logger.error(f"User migration failed: {str(e)}")
            raise
    
    def _migrate_profiles(self):
        """Migrate client and coach profiles"""
        try:
            user_mapping_path = os.path.join(config.EXPORT_DIR, "user_id_mapping.json")
            client_csv_path = os.path.join(config.EXPORT_DIR, "client_profiles.csv")
            coach_csv_path = os.path.join(config.EXPORT_DIR, "coach_profiles.csv")
            
            migrator = ProfileMigrator()
            migrator.load_user_id_mapping(user_mapping_path)
            
            # Migrate client profiles
            if os.path.exists(client_csv_path):
                client_success, client_failed, client_errors = migrator.migrate_client_profiles(client_csv_path)
                logger.info(f"Client profile migration: {client_success} success, {client_failed} failed")
            
            # Migrate coach profiles
            if os.path.exists(coach_csv_path):
                coach_success, coach_failed, coach_errors = migrator.migrate_coach_profiles(coach_csv_path)
                logger.info(f"Coach profile migration: {coach_success} success, {coach_failed} failed")
            
            # Store stats
            self.migration_data["profile_stats"] = migrator.get_stats()
            
            migrator.close()
            
        except Exception as e:
            logger.error(f"Profile migration failed: {str(e)}")
            raise
    
    def _migrate_bookings(self):
        """Migrate bookings and payments"""
        try:
            user_mapping_path = os.path.join(config.EXPORT_DIR, "user_id_mapping.json")
            bookings_csv_path = os.path.join(config.EXPORT_DIR, "bookings.csv")
            payments_csv_path = os.path.join(config.EXPORT_DIR, "payments.csv")
            booking_mapping_path = os.path.join(config.EXPORT_DIR, "booking_id_mapping.json")
            
            migrator = BookingMigrator()
            migrator.load_user_id_mapping(user_mapping_path)
            
            # Migrate bookings
            if os.path.exists(bookings_csv_path):
                booking_success, booking_failed, booking_errors = migrator.migrate_bookings(bookings_csv_path)
                logger.info(f"Booking migration: {booking_success} success, {booking_failed} failed")
                
                # Save booking ID mapping
                migrator.save_booking_id_mapping(booking_mapping_path)
            
            # Migrate payments
            if os.path.exists(payments_csv_path):
                payment_success, payment_failed, payment_errors = migrator.migrate_payments(payments_csv_path)
                logger.info(f"Payment migration: {payment_success} success, {payment_failed} failed")
            
            # Store stats
            self.migration_data["booking_stats"] = migrator.get_stats()
            
            migrator.close()
            
        except Exception as e:
            logger.error(f"Booking/Payment migration failed: {str(e)}")
            raise
    
    def _validate_data(self):
        """Validate migrated data integrity"""
        try:
            validator = MigrationValidator()
            
            # Run all validations
            validator.validate_row_counts()
            validator.validate_referential_integrity()
            validator.validate_data_quality()
            validator.validate_sample_data(sample_size=10)
            
            # Store results
            self.migration_data["validation_results"] = validator.get_validation_results()
            
            if validator.has_errors():
                logger.warning(f"Validation found {len(validator.validation_results['errors'])} issues")
            else:
                logger.info("All validation checks passed")
            
            validator.close()
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise
    
    def _generate_reports(self):
        """Generate migration reports"""
        try:
            reporter = MigrationReporter()
            
            # Generate summary report
            summary_path = reporter.generate_summary_report(
                self.migration_data["user_stats"],
                self.migration_data["profile_stats"],
                self.migration_data["booking_stats"],
                self.migration_data["validation_results"]
            )
            self.migration_data["report_paths"]["summary"] = summary_path
            
            # Generate error log if there are errors
            all_errors = {
                "users": self.migration_data["user_stats"].get("errors", []),
                "client_profiles": self.migration_data["profile_stats"].get("client_profiles", {}).get("errors", []),
                "coach_profiles": self.migration_data["profile_stats"].get("coach_profiles", {}).get("errors", []),
                "bookings": self.migration_data["booking_stats"].get("bookings", {}).get("errors", []),
                "payments": self.migration_data["booking_stats"].get("payments", {}).get("errors", [])
            }
            
            if any(errors for errors in all_errors.values()):
                error_log_path = reporter.generate_error_log(all_errors)
                self.migration_data["report_paths"]["error_log"] = error_log_path
            
            # Generate JSON report
            json_path = reporter.generate_json_report(self.migration_data)
            self.migration_data["report_paths"]["json"] = json_path
            
            # Generate rollback script
            user_mapping_path = os.path.join(config.EXPORT_DIR, "user_id_mapping.json")
            if os.path.exists(user_mapping_path):
                import json
                with open(user_mapping_path, 'r') as f:
                    user_id_mapping = json.load(f)
                rollback_path = reporter.generate_rollback_script(user_id_mapping)
                self.migration_data["report_paths"]["rollback"] = rollback_path
            
            logger.info("All reports generated successfully")
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise
    
    def _has_critical_errors(self) -> bool:
        """Check if there are critical errors that should fail the migration"""
        # Check for referential integrity errors
        ref_integrity = self.migration_data["validation_results"].get("referential_integrity", {})
        for check, result in ref_integrity.items():
            if not result.get("valid", True):
                return True
        
        # Check for high failure rate (>10%)
        user_stats = self.migration_data["user_stats"]
        if user_stats.get("total", 0) > 0:
            failure_rate = user_stats.get("failed", 0) / user_stats.get("total", 1)
            if failure_rate > 0.1:
                return True
        
        return False
    
    def _print_summary(self):
        """Print migration summary"""
        logger.info("\n" + "=" * 80)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 80)
        
        logger.info(f"Duration: {self.migration_data['duration_seconds']:.2f} seconds")
        
        user_stats = self.migration_data["user_stats"]
        logger.info(f"\nUsers: {user_stats.get('success', 0)}/{user_stats.get('total', 0)} migrated")
        
        profile_stats = self.migration_data["profile_stats"]
        client_stats = profile_stats.get("client_profiles", {})
        coach_stats = profile_stats.get("coach_profiles", {})
        logger.info(f"Client Profiles: {client_stats.get('success', 0)}/{client_stats.get('total', 0)} migrated")
        logger.info(f"Coach Profiles: {coach_stats.get('success', 0)}/{coach_stats.get('total', 0)} migrated")
        
        booking_stats = self.migration_data["booking_stats"]
        booking_data = booking_stats.get("bookings", {})
        payment_data = booking_stats.get("payments", {})
        logger.info(f"Bookings: {booking_data.get('success', 0)}/{booking_data.get('total', 0)} migrated")
        logger.info(f"Payments: {payment_data.get('success', 0)}/{payment_data.get('total', 0)} migrated")
        
        logger.info("\nReports generated:")
        for report_type, path in self.migration_data["report_paths"].items():
            logger.info(f"  - {report_type}: {path}")
        
        logger.info("=" * 80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CultureBridge Phase 1 to Phase 2 Migration")
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Skip Bubble export and use existing CSV files"
    )
    
    args = parser.parse_args()
    
    orchestrator = MigrationOrchestrator(skip_export=args.skip_export)
    exit_code = orchestrator.run()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
