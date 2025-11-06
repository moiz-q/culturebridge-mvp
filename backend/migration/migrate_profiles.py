"""
Profile migration scripts for clients and coaches.

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
from app.models.profile import ClientProfile, CoachProfile
from migration.field_mapper import FieldMapper
from migration.config import config

logger = logging.getLogger(__name__)


class ProfileMigrator:
    """Migrate client and coach profiles from Phase 1 to Phase 2"""
    
    def __init__(self, user_id_mapping: Dict[str, str] = None, db: Session = None):
        """
        Initialize profile migrator.
        
        Args:
            user_id_mapping: Mapping of Phase 1 user IDs to Phase 2 UUIDs
            db: Database session (optional)
        """
        self.db = db or SessionLocal()
        self.mapper = FieldMapper()
        self.user_id_mapping = user_id_mapping or {}
        self.stats = {
            "client_profiles": {"total": 0, "success": 0, "failed": 0, "errors": []},
            "coach_profiles": {"total": 0, "success": 0, "failed": 0, "errors": []}
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
    
    def migrate_client_profiles(self, csv_path: str) -> Tuple[int, int, List[Dict]]:
        """
        Migrate client profiles from CSV file.
        
        Args:
            csv_path: Path to client profiles CSV file
            
        Returns:
            Tuple of (success_count, failed_count, error_list)
        """
        logger.info(f"Starting client profile migration from {csv_path}")
        start_time = datetime.now()
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    self.stats["client_profiles"]["total"] += 1
                    
                    try:
                        self._migrate_client_profile(row)
                        self.stats["client_profiles"]["success"] += 1
                        
                        if self.stats["client_profiles"]["success"] % 100 == 0:
                            logger.info(f"Migrated {self.stats['client_profiles']['success']} client profiles...")
                    
                    except Exception as e:
                        self.stats["client_profiles"]["failed"] += 1
                        error_info = {
                            "user_id": row.get("user_id", "unknown"),
                            "error": str(e)
                        }
                        self.stats["client_profiles"]["errors"].append(error_info)
                        logger.error(f"Failed to migrate client profile: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error during client profile migration: {str(e)}")
            self.db.rollback()
            raise
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Client profile migration completed in {duration:.2f} seconds")
        
        return (
            self.stats["client_profiles"]["success"],
            self.stats["client_profiles"]["failed"],
            self.stats["client_profiles"]["errors"]
        )
    
    def _migrate_client_profile(self, phase1_data: Dict) -> ClientProfile:
        """
        Migrate a single client profile record.
        
        Args:
            phase1_data: Client profile data from Phase 1
            
        Returns:
            Created ClientProfile object
        """
        # Map fields from Phase 1 to Phase 2
        mapped_data = self.mapper.map_client_profile_fields(phase1_data)
        
        # Get Phase 2 user ID
        phase1_user_id = phase1_data.get("user_id") or phase1_data.get("user_ref")
        if not phase1_user_id:
            raise ValueError("Missing user_id in client profile data")
        
        phase2_user_id = self.user_id_mapping.get(str(phase1_user_id))
        if not phase2_user_id:
            raise ValueError(f"User ID mapping not found for {phase1_user_id}")
        
        # Create client profile object
        profile = ClientProfile(
            id=uuid.uuid4(),
            user_id=uuid.UUID(phase2_user_id),
            first_name=mapped_data.get("first_name"),
            last_name=mapped_data.get("last_name"),
            photo_url=mapped_data.get("photo_url"),
            phone=mapped_data.get("phone"),
            timezone=mapped_data.get("timezone"),
            quiz_data=mapped_data.get("quiz_data", {}),
            preferences=mapped_data.get("preferences"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        try:
            self.db.add(profile)
            self.db.flush()
            logger.debug(f"Migrated client profile for user {phase2_user_id}")
            
        except IntegrityError as e:
            self.db.rollback()
            if "duplicate key" in str(e).lower():
                raise ValueError(f"Client profile already exists for user {phase2_user_id}")
            raise
        
        return profile
    
    def migrate_coach_profiles(self, csv_path: str) -> Tuple[int, int, List[Dict]]:
        """
        Migrate coach profiles from CSV file.
        
        Args:
            csv_path: Path to coach profiles CSV file
            
        Returns:
            Tuple of (success_count, failed_count, error_list)
        """
        logger.info(f"Starting coach profile migration from {csv_path}")
        start_time = datetime.now()
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    self.stats["coach_profiles"]["total"] += 1
                    
                    try:
                        self._migrate_coach_profile(row)
                        self.stats["coach_profiles"]["success"] += 1
                        
                        if self.stats["coach_profiles"]["success"] % 100 == 0:
                            logger.info(f"Migrated {self.stats['coach_profiles']['success']} coach profiles...")
                    
                    except Exception as e:
                        self.stats["coach_profiles"]["failed"] += 1
                        error_info = {
                            "user_id": row.get("user_id", "unknown"),
                            "error": str(e)
                        }
                        self.stats["coach_profiles"]["errors"].append(error_info)
                        logger.error(f"Failed to migrate coach profile: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error during coach profile migration: {str(e)}")
            self.db.rollback()
            raise
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Coach profile migration completed in {duration:.2f} seconds")
        
        return (
            self.stats["coach_profiles"]["success"],
            self.stats["coach_profiles"]["failed"],
            self.stats["coach_profiles"]["errors"]
        )
    
    def _migrate_coach_profile(self, phase1_data: Dict) -> CoachProfile:
        """
        Migrate a single coach profile record.
        
        Args:
            phase1_data: Coach profile data from Phase 1
            
        Returns:
            Created CoachProfile object
        """
        # Map fields from Phase 1 to Phase 2
        mapped_data = self.mapper.map_coach_profile_fields(phase1_data)
        
        # Get Phase 2 user ID
        phase1_user_id = phase1_data.get("user_id") or phase1_data.get("user_ref")
        if not phase1_user_id:
            raise ValueError("Missing user_id in coach profile data")
        
        phase2_user_id = self.user_id_mapping.get(str(phase1_user_id))
        if not phase2_user_id:
            raise ValueError(f"User ID mapping not found for {phase1_user_id}")
        
        # Create coach profile object
        profile = CoachProfile(
            id=uuid.uuid4(),
            user_id=uuid.UUID(phase2_user_id),
            first_name=mapped_data.get("first_name"),
            last_name=mapped_data.get("last_name"),
            photo_url=mapped_data.get("photo_url"),
            bio=mapped_data.get("bio"),
            intro_video_url=mapped_data.get("intro_video_url"),
            expertise=mapped_data.get("expertise", []),
            languages=mapped_data.get("languages", []),
            countries=mapped_data.get("countries", []),
            hourly_rate=mapped_data.get("hourly_rate"),
            currency=mapped_data.get("currency", "USD"),
            availability=mapped_data.get("availability"),
            rating=mapped_data.get("rating", 0.0),
            total_sessions=mapped_data.get("total_sessions", 0),
            is_verified=mapped_data.get("is_verified", False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Validate hourly rate
        if profile.hourly_rate and not profile.validate_hourly_rate():
            logger.warning(f"Invalid hourly rate for coach {phase2_user_id}: {profile.hourly_rate}")
            profile.hourly_rate = 100.0  # Set default
        
        # Add to database
        try:
            self.db.add(profile)
            self.db.flush()
            logger.debug(f"Migrated coach profile for user {phase2_user_id}")
            
        except IntegrityError as e:
            self.db.rollback()
            if "duplicate key" in str(e).lower():
                raise ValueError(f"Coach profile already exists for user {phase2_user_id}")
            raise
        
        return profile
    
    def get_stats(self) -> Dict:
        """Get migration statistics"""
        return self.stats
    
    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()


def main():
    """Main function to run profile migration"""
    import os
    
    user_mapping_path = os.path.join(config.EXPORT_DIR, "user_id_mapping.json")
    client_csv_path = os.path.join(config.EXPORT_DIR, "client_profiles.csv")
    coach_csv_path = os.path.join(config.EXPORT_DIR, "coach_profiles.csv")
    
    if not os.path.exists(user_mapping_path):
        logger.error(f"User ID mapping file not found: {user_mapping_path}")
        return 1
    
    try:
        migrator = ProfileMigrator()
        migrator.load_user_id_mapping(user_mapping_path)
        
        # Migrate client profiles
        if os.path.exists(client_csv_path):
            client_success, client_failed, client_errors = migrator.migrate_client_profiles(client_csv_path)
            print(f"\n=== Client Profile Migration Summary ===")
            print(f"Success: {client_success}, Failed: {client_failed}")
        
        # Migrate coach profiles
        if os.path.exists(coach_csv_path):
            coach_success, coach_failed, coach_errors = migrator.migrate_coach_profiles(coach_csv_path)
            print(f"\n=== Coach Profile Migration Summary ===")
            print(f"Success: {coach_success}, Failed: {coach_failed}")
        
        migrator.close()
        return 0
        
    except Exception as e:
        logger.error(f"Profile migration failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
