"""
Migration report generation.

Requirements: 10.4
"""
import json
import csv
from typing import Dict, Any
from datetime import datetime
import os
import logging

from migration.config import config

logger = logging.getLogger(__name__)


class MigrationReporter:
    """Generate comprehensive migration reports"""
    
    def __init__(self):
        """Initialize migration reporter"""
        self.report_dir = config.REPORT_DIR
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_summary_report(
        self,
        user_stats: Dict,
        profile_stats: Dict,
        booking_stats: Dict,
        validation_results: Dict
    ) -> str:
        """
        Generate comprehensive migration summary report.
        
        Requirements: 10.4
        
        Args:
            user_stats: User migration statistics
            profile_stats: Profile migration statistics
            booking_stats: Booking migration statistics
            validation_results: Validation results
            
        Returns:
            Path to generated report file
        """
        logger.info("Generating migration summary report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.report_dir, f"migration_summary_{timestamp}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CULTUREBRIDGE PHASE 1 TO PHASE 2 MIGRATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # User Migration Summary
            f.write("-" * 80 + "\n")
            f.write("USER MIGRATION SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Users Processed: {user_stats.get('total', 0)}\n")
            f.write(f"Successfully Migrated: {user_stats.get('success', 0)}\n")
            f.write(f"Failed: {user_stats.get('failed', 0)}\n")
            if user_stats.get('failed', 0) > 0:
                f.write(f"\nFirst 10 Errors:\n")
                for error in user_stats.get('errors', [])[:10]:
                    f.write(f"  - {error.get('email', 'unknown')}: {error.get('error', 'unknown')}\n")
            f.write("\n")
            
            # Profile Migration Summary
            f.write("-" * 80 + "\n")
            f.write("PROFILE MIGRATION SUMMARY\n")
            f.write("-" * 80 + "\n")
            
            client_stats = profile_stats.get('client_profiles', {})
            f.write(f"Client Profiles:\n")
            f.write(f"  Total: {client_stats.get('total', 0)}\n")
            f.write(f"  Success: {client_stats.get('success', 0)}\n")
            f.write(f"  Failed: {client_stats.get('failed', 0)}\n")
            
            coach_stats = profile_stats.get('coach_profiles', {})
            f.write(f"\nCoach Profiles:\n")
            f.write(f"  Total: {coach_stats.get('total', 0)}\n")
            f.write(f"  Success: {coach_stats.get('success', 0)}\n")
            f.write(f"  Failed: {coach_stats.get('failed', 0)}\n")
            f.write("\n")
            
            # Booking Migration Summary
            f.write("-" * 80 + "\n")
            f.write("BOOKING & PAYMENT MIGRATION SUMMARY\n")
            f.write("-" * 80 + "\n")
            
            booking_data = booking_stats.get('bookings', {})
            f.write(f"Bookings:\n")
            f.write(f"  Total: {booking_data.get('total', 0)}\n")
            f.write(f"  Success: {booking_data.get('success', 0)}\n")
            f.write(f"  Failed: {booking_data.get('failed', 0)}\n")
            
            payment_data = booking_stats.get('payments', {})
            f.write(f"\nPayments:\n")
            f.write(f"  Total: {payment_data.get('total', 0)}\n")
            f.write(f"  Success: {payment_data.get('success', 0)}\n")
            f.write(f"  Failed: {payment_data.get('failed', 0)}\n")
            f.write("\n")
            
            # Validation Results
            f.write("-" * 80 + "\n")
            f.write("VALIDATION RESULTS\n")
            f.write("-" * 80 + "\n")
            
            # Row counts
            f.write("Row Count Validation:\n")
            for entity, counts in validation_results.get('row_counts', {}).items():
                status = "✓" if counts.get('match', False) else "✗"
                f.write(f"  {status} {entity}: Phase1={counts.get('phase1', 0)}, Phase2={counts.get('phase2', 0)}\n")
            
            # Referential integrity
            f.write("\nReferential Integrity:\n")
            for check, result in validation_results.get('referential_integrity', {}).items():
                status = "✓" if result.get('valid', False) else "✗"
                orphaned = result.get('orphaned', 0)
                f.write(f"  {status} {check}: {orphaned} orphaned records\n")
            
            # Data quality
            f.write("\nData Quality:\n")
            for check, result in validation_results.get('data_quality', {}).items():
                status = "✓" if result.get('valid', False) else "⚠"
                invalid = result.get('invalid', result.get('missing', 0))
                f.write(f"  {status} {check}: {invalid} invalid records\n")
            
            # Overall status
            f.write("\n" + "=" * 80 + "\n")
            has_errors = len(validation_results.get('errors', [])) > 0
            if has_errors:
                f.write("OVERALL STATUS: MIGRATION COMPLETED WITH WARNINGS\n")
                f.write(f"Total Validation Errors: {len(validation_results.get('errors', []))}\n")
            else:
                f.write("OVERALL STATUS: MIGRATION COMPLETED SUCCESSFULLY\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"Summary report generated: {report_path}")
        return report_path
    
    def generate_error_log(self, all_errors: Dict[str, List[Dict]]) -> str:
        """
        Generate detailed error log.
        
        Requirements: 10.4
        
        Args:
            all_errors: Dictionary of errors by entity type
            
        Returns:
            Path to error log file
        """
        logger.info("Generating error log...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_log_path = os.path.join(self.report_dir, f"migration_errors_{timestamp}.csv")
        
        with open(error_log_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['entity_type', 'record_id', 'error_message', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for entity_type, errors in all_errors.items():
                for error in errors:
                    writer.writerow({
                        'entity_type': entity_type,
                        'record_id': error.get('email') or error.get('user_id') or error.get('booking_id') or 'unknown',
                        'error_message': error.get('error', 'Unknown error'),
                        'timestamp': datetime.now().isoformat()
                    })
        
        logger.info(f"Error log generated: {error_log_path}")
        return error_log_path
    
    def generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate machine-readable JSON report.
        
        Args:
            report_data: Complete report data
            
        Returns:
            Path to JSON report file
        """
        logger.info("Generating JSON report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(self.report_dir, f"migration_report_{timestamp}.json")
        
        report_data['generated_at'] = datetime.now().isoformat()
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"JSON report generated: {json_path}")
        return json_path
    
    def generate_rollback_script(self, user_id_mapping: Dict[str, str]) -> str:
        """
        Generate SQL script for rollback capability.
        
        Requirements: 10.5
        
        Args:
            user_id_mapping: Mapping of Phase 1 to Phase 2 user IDs
            
        Returns:
            Path to rollback script
        """
        logger.info("Generating rollback script...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = os.path.join(self.report_dir, f"rollback_migration_{timestamp}.sql")
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("-- CultureBridge Migration Rollback Script\n")
            f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- WARNING: This will delete all migrated data!\n\n")
            
            f.write("BEGIN;\n\n")
            
            # Delete in reverse order of dependencies
            f.write("-- Delete payments\n")
            f.write("DELETE FROM payments WHERE booking_id IN (\n")
            f.write("  SELECT id FROM bookings WHERE client_id IN (\n")
            f.write("    SELECT id FROM users WHERE created_at >= CURRENT_DATE\n")
            f.write("  )\n")
            f.write(");\n\n")
            
            f.write("-- Delete bookings\n")
            f.write("DELETE FROM bookings WHERE client_id IN (\n")
            f.write("  SELECT id FROM users WHERE created_at >= CURRENT_DATE\n")
            f.write(");\n\n")
            
            f.write("-- Delete comments\n")
            f.write("DELETE FROM comments WHERE author_id IN (\n")
            f.write("  SELECT id FROM users WHERE created_at >= CURRENT_DATE\n")
            f.write(");\n\n")
            
            f.write("-- Delete posts\n")
            f.write("DELETE FROM posts WHERE author_id IN (\n")
            f.write("  SELECT id FROM users WHERE created_at >= CURRENT_DATE\n")
            f.write(");\n\n")
            
            f.write("-- Delete bookmarks\n")
            f.write("DELETE FROM bookmarks WHERE user_id IN (\n")
            f.write("  SELECT id FROM users WHERE created_at >= CURRENT_DATE\n")
            f.write(");\n\n")
            
            f.write("-- Delete profiles\n")
            f.write("DELETE FROM client_profiles WHERE user_id IN (\n")
            f.write("  SELECT id FROM users WHERE created_at >= CURRENT_DATE\n")
            f.write(");\n\n")
            
            f.write("DELETE FROM coach_profiles WHERE user_id IN (\n")
            f.write("  SELECT id FROM users WHERE created_at >= CURRENT_DATE\n")
            f.write(");\n\n")
            
            f.write("-- Delete users\n")
            f.write("DELETE FROM users WHERE created_at >= CURRENT_DATE;\n\n")
            
            f.write("-- Alternatively, delete specific migrated user IDs:\n")
            f.write("-- DELETE FROM users WHERE id IN (\n")
            for i, user_id in enumerate(list(user_id_mapping.values())[:10]):
                f.write(f"--   '{user_id}'")
                if i < 9:
                    f.write(",")
                f.write("\n")
            f.write("--   -- ... (add all migrated user IDs)\n")
            f.write("-- );\n\n")
            
            f.write("COMMIT;\n")
            f.write("-- ROLLBACK; -- Uncomment to abort rollback\n")
        
        logger.info(f"Rollback script generated: {script_path}")
        return script_path


def main():
    """Main function to generate reports"""
    # This would typically be called from the main migration orchestrator
    # with actual migration statistics
    
    reporter = MigrationReporter()
    
    # Example usage
    sample_data = {
        "user_stats": {"total": 100, "success": 98, "failed": 2, "errors": []},
        "profile_stats": {
            "client_profiles": {"total": 60, "success": 60, "failed": 0},
            "coach_profiles": {"total": 38, "success": 38, "failed": 0}
        },
        "booking_stats": {
            "bookings": {"total": 150, "success": 148, "failed": 2},
            "payments": {"total": 120, "success": 120, "failed": 0}
        },
        "validation_results": {
            "row_counts": {},
            "referential_integrity": {},
            "data_quality": {},
            "errors": []
        }
    }
    
    summary_path = reporter.generate_summary_report(
        sample_data["user_stats"],
        sample_data["profile_stats"],
        sample_data["booking_stats"],
        sample_data["validation_results"]
    )
    
    print(f"Summary report: {summary_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
