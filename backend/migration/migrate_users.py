"""
User migration script with password re-hashing.

Requirements: 10.1, 10.2
"""
import csv
import uuid
from typing import Dict, List, Tuple
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.user import User, UserRole
from migration.field_mapper import FieldMapper
from migration.config import config

logger = logging.getLogger(__name__)


class UserMigrator:
    """Migrate users from Phase 1 to Phase 2 with password re-hashing"""
    
    def __init__(self, db: Session = None):
        """
        Initialize user migrator.
        
        Args:
            db: Database session (optional, will create if not provided)
        """
        self.db = db or SessionLocal()
        self.mapper = FieldMapper()
        self.user_id_mapping: Dict[str, str] = {}  # Phase 1 ID -> Phase 2 UUID
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
    
    def migrate_from_csv(self, csv_path: str) -> Tuple[int, int, List[Dict]]:
        """
        Migrate users from CSV file.
        
        Args:
            csv_path: Path to users CSV file
            
        Returns:
            Tuple of (success_count, failed_count, error_list)
        """
        logger.info(f"Starting user migration from {csv_path}")
        start_time = datetime.now()
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    self.stats["total"] += 1
                    
                    try:
                        self._migrate_user(row)
                        self.stats["success"] += 1
                        
                        if self.stats["success"] % 100 == 0:
                            logger.info(f"Migrated {self.stats['success']} users...")
                    
                    except Exception as e:
                        self.stats["failed"] += 1
                        error_info = {
                            "email": row.get("email", "unknown"),
                            "phase1_id": row.get("_id", "unknown"),
                            "error": str(e)
                        }
                        self.stats["errors"].append(error_info)
                        logger.error(f"Failed to migrate user {row.get('email')}: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error during user migration: {str(e)}")
            self.db.rollback()
            raise
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"User migration completed in {duration:.2f} seconds")
        logger.info(f"Success: {self.stats['success']}, Failed: {self.stats['failed']}")
        
        return self.stats["success"], self.stats["failed"], self.stats["errors"]
    
    def _migrate_user(self, phase1_data: Dict) -> User:
        """
        Migrate a single user record.
        
        Args:
            phase1_data: User data from Phase 1
            
        Returns:
            Created User object
        """
        # Map fields from Phase 1 to Phase 2
        mapped_data = self.mapper.map_user_fields(phase1_data)
        
        # Generate new UUID for Phase 2
        new_user_id = uuid.uuid4()
        
        # Create user object
        user = User(
            id=new_user_id,
            email=mapped_data.get("email"),
            password_hash=mapped_data.get("password_hash"),
            role=UserRole(mapped_data.get("role", "client")),
            is_active=mapped_data.get("is_active", True),
            email_verified=mapped_data.get("email_verified", False),
            created_at=mapped_data.get("created_at") or datetime.utcnow(),
            updated_at=mapped_data.get("updated_at") or datetime.utcnow()
        )
        
        # Validate email
        if not user.validate_email():
            raise ValueError(f"Invalid email format: {user.email}")
        
        # Add to database
        try:
            self.db.add(user)
            self.db.flush()  # Flush to catch integrity errors
            
            # Store ID mapping for profile migration
            phase1_id = phase1_data.get("_id") or phase1_data.get("id")
            if phase1_id:
                self.user_id_mapping[str(phase1_id)] = str(new_user_id)
            
            logger.debug(f"Migrated user: {user.email} (role: {user.role})")
            
        except IntegrityError as e:
            self.db.rollback()
            if "duplicate key" in str(e).lower():
                raise ValueError(f"User with email {user.email} already exists")
            raise
        
        return user
    
    def get_user_id_mapping(self) -> Dict[str, str]:
        """
        Get mapping of Phase 1 user IDs to Phase 2 UUIDs.
        
        Returns:
            Dictionary mapping old IDs to new UUIDs
        """
        return self.user_id_mapping
    
    def save_id_mapping(self, filepath: str):
        """
        Save user ID mapping to file for use in profile migration.
        
        Args:
            filepath: Path to save mapping file
        """
        import json
        with open(filepath, 'w') as f:
            json.dump(self.user_id_mapping, f, indent=2)
        logger.info(f"Saved user ID mapping to {filepath}")
    
    def load_id_mapping(self, filepath: str):
        """
        Load user ID mapping from file.
        
        Args:
            filepath: Path to mapping file
        """
        import json
        with open(filepath, 'r') as f:
            self.user_id_mapping = json.load(f)
        logger.info(f"Loaded {len(self.user_id_mapping)} user ID mappings")
    
    def get_stats(self) -> Dict:
        """Get migration statistics"""
        return self.stats
    
    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()


def main():
    """Main function to run user migration"""
    import os
    
    csv_path = os.path.join(config.EXPORT_DIR, "users.csv")
    mapping_path = os.path.join(config.EXPORT_DIR, "user_id_mapping.json")
    
    if not os.path.exists(csv_path):
        logger.error(f"Users CSV file not found: {csv_path}")
        return 1
    
    try:
        migrator = UserMigrator()
        success, failed, errors = migrator.migrate_from_csv(csv_path)
        
        # Save ID mapping for profile migration
        migrator.save_id_mapping(mapping_path)
        
        print(f"\n=== User Migration Summary ===")
        print(f"Total: {success + failed}")
        print(f"Success: {success}")
        print(f"Failed: {failed}")
        
        if errors:
            print(f"\nErrors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error['email']}: {error['error']}")
        
        migrator.close()
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"User migration failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
