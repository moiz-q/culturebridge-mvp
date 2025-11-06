"""
Tests for migration functionality.

This test suite validates the migration scripts without requiring actual Bubble API access.
"""
import pytest
import os
import json
import csv
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import tempfile

from migration.config import config, MigrationConfig
from migration.field_mapper import FieldMapper
from migration.bubble_export import BubbleExporter


class TestMigrationConfig:
    """Test migration configuration"""
    
    def test_config_has_required_attributes(self):
        """Test that config has all required attributes"""
        assert hasattr(config, 'BUBBLE_API_URL')
        assert hasattr(config, 'BUBBLE_ENDPOINTS')
        assert hasattr(config, 'USER_FIELD_MAPPING')
        assert hasattr(config, 'ROLE_MAPPING')
        assert hasattr(config, 'BOOKING_STATUS_MAPPING')
        assert hasattr(config, 'PAYMENT_STATUS_MAPPING')
    
    def test_role_mapping(self):
        """Test role mapping from Phase 1 to Phase 2"""
        assert config.ROLE_MAPPING['seeker'] == 'client'
        assert config.ROLE_MAPPING['coach'] == 'coach'
        assert config.ROLE_MAPPING['admin'] == 'admin'
    
    def test_status_mappings(self):
        """Test status mappings"""
        assert config.BOOKING_STATUS_MAPPING['pending'] == 'pending'
        assert config.BOOKING_STATUS_MAPPING['complete'] == 'completed'
        assert config.BOOKING_STATUS_MAPPING['canceled'] == 'cancelled'
        
        assert config.PAYMENT_STATUS_MAPPING['success'] == 'succeeded'
        assert config.PAYMENT_STATUS_MAPPING['failed'] == 'failed'


class TestFieldMapper:
    """Test field mapping utilities"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = FieldMapper.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith('$2b$')  # bcrypt format
    
    def test_parse_datetime_iso_format(self):
        """Test datetime parsing with ISO format"""
        dt_str = "2025-11-05T10:30:00Z"
        parsed = FieldMapper.parse_datetime(dt_str)
        
        assert parsed is not None
        assert isinstance(parsed, datetime)
        assert parsed.year == 2025
        assert parsed.month == 11
        assert parsed.day == 5
    
    def test_parse_datetime_standard_format(self):
        """Test datetime parsing with standard format"""
        dt_str = "2025-11-05 10:30:00"
        parsed = FieldMapper.parse_datetime(dt_str)
        
        assert parsed is not None
        assert isinstance(parsed, datetime)
    
    def test_parse_datetime_invalid(self):
        """Test datetime parsing with invalid input"""
        parsed = FieldMapper.parse_datetime("invalid_date")
        assert parsed is None
    
    def test_parse_json_field_dict(self):
        """Test JSON field parsing with dict input"""
        data = {"key": "value", "nested": {"inner": "data"}}
        parsed = FieldMapper.parse_json_field(data)
        
        assert parsed == data
    
    def test_parse_json_field_string(self):
        """Test JSON field parsing with string input"""
        json_str = '{"key": "value", "number": 123}'
        parsed = FieldMapper.parse_json_field(json_str)
        
        assert parsed == {"key": "value", "number": 123}
    
    def test_parse_json_field_invalid(self):
        """Test JSON field parsing with invalid input"""
        parsed = FieldMapper.parse_json_field("not valid json")
        assert parsed == {}
    
    def test_parse_array_field_list(self):
        """Test array field parsing with list input"""
        data = ["item1", "item2", "item3"]
        parsed = FieldMapper.parse_array_field(data)
        
        assert parsed == ["item1", "item2", "item3"]
    
    def test_parse_array_field_json_string(self):
        """Test array field parsing with JSON string"""
        json_str = '["item1", "item2", "item3"]'
        parsed = FieldMapper.parse_array_field(json_str)
        
        assert parsed == ["item1", "item2", "item3"]
    
    def test_parse_array_field_comma_separated(self):
        """Test array field parsing with comma-separated string"""
        csv_str = "item1, item2, item3"
        parsed = FieldMapper.parse_array_field(csv_str)
        
        assert parsed == ["item1", "item2", "item3"]
    
    def test_parse_decimal(self):
        """Test decimal parsing"""
        assert FieldMapper.parse_decimal("123.45") == 123.45
        assert FieldMapper.parse_decimal(100) == 100.0
        assert FieldMapper.parse_decimal("invalid", default=0.0) == 0.0
    
    def test_parse_int(self):
        """Test integer parsing"""
        assert FieldMapper.parse_int("123") == 123
        assert FieldMapper.parse_int(456) == 456
        assert FieldMapper.parse_int("invalid", default=0) == 0
    
    def test_map_user_fields(self):
        """Test user field mapping"""
        phase1_data = {
            "email": "test@example.com",
            "password": "plain_password",
            "type": "seeker",
            "active": True,
            "verified": False,
            "created_date": "2025-11-05T10:00:00Z"
        }
        
        mapped = FieldMapper.map_user_fields(phase1_data)
        
        assert mapped["email"] == "test@example.com"
        assert mapped["password_hash"] != "plain_password"  # Should be hashed
        assert mapped["role"] == "client"  # seeker -> client
        assert mapped["is_active"] == True
        assert mapped["email_verified"] == False
        assert mapped["created_at"] is not None
    
    def test_map_coach_profile_fields(self):
        """Test coach profile field mapping"""
        phase1_data = {
            "first_name": "John",
            "last_name": "Doe",
            "biography": "Experienced coach",
            "expertise_areas": '["career", "leadership"]',
            "languages_spoken": '["English", "Spanish"]',
            "countries_experience": '["USA", "Spain"]',
            "rate": "150.00",
            "average_rating": "4.5",
            "session_count": "25"
        }
        
        mapped = FieldMapper.map_coach_profile_fields(phase1_data)
        
        assert mapped["first_name"] == "John"
        assert mapped["last_name"] == "Doe"
        assert mapped["bio"] == "Experienced coach"
        assert mapped["expertise"] == ["career", "leadership"]
        assert mapped["languages"] == ["English", "Spanish"]
        assert mapped["countries"] == ["USA", "Spain"]
        assert mapped["hourly_rate"] == 150.0
        assert mapped["rating"] == 4.5
        assert mapped["total_sessions"] == 25
        assert mapped["currency"] == "USD"  # Default


class TestBubbleExporter:
    """Test Bubble API export functionality"""
    
    @patch('migration.bubble_export.requests.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "results": [{"id": "1", "email": "test@example.com"}],
                "remaining": 0
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Mock the API key to avoid ValueError
        with patch.object(config, 'BUBBLE_API_KEY', 'test_key'):
            exporter = BubbleExporter(api_key='test_key')
            result = exporter._make_request('/test')
        
        assert result is not None
        assert "response" in result
        assert "results" in result["response"]
    
    def test_write_csv(self):
        """Test CSV writing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = BubbleExporter(api_key='test_key')
            exporter.export_dir = tmpdir
            
            records = [
                {"id": "1", "name": "Test 1", "value": 100},
                {"id": "2", "name": "Test 2", "value": 200}
            ]
            
            filepath = os.path.join(tmpdir, "test.csv")
            exporter._write_csv(filepath, records)
            
            # Verify file was created
            assert os.path.exists(filepath)
            
            # Verify content
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]["name"] == "Test 1"
                assert rows[1]["value"] == "200"


class TestMigrationValidation:
    """Test migration validation logic"""
    
    def test_count_csv_rows(self):
        """Test CSV row counting"""
        from migration.validation import MigrationValidator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            
            # Create test CSV
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'name'])  # Header
                writer.writerow(['1', 'Test 1'])
                writer.writerow(['2', 'Test 2'])
                writer.writerow(['3', 'Test 3'])
            
            validator = MigrationValidator()
            count = validator._count_csv_rows(csv_path)
            
            assert count == 3  # Should not count header


class TestMigrationReporting:
    """Test migration reporting"""
    
    def test_generate_summary_report(self):
        """Test summary report generation"""
        from migration.reporting import MigrationReporter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = MigrationReporter()
            reporter.report_dir = tmpdir
            
            user_stats = {"total": 100, "success": 98, "failed": 2, "errors": []}
            profile_stats = {
                "client_profiles": {"total": 60, "success": 60, "failed": 0},
                "coach_profiles": {"total": 38, "success": 38, "failed": 0}
            }
            booking_stats = {
                "bookings": {"total": 150, "success": 148, "failed": 2},
                "payments": {"total": 120, "success": 120, "failed": 0}
            }
            validation_results = {
                "row_counts": {},
                "referential_integrity": {},
                "data_quality": {},
                "errors": []
            }
            
            report_path = reporter.generate_summary_report(
                user_stats, profile_stats, booking_stats, validation_results
            )
            
            assert os.path.exists(report_path)
            assert report_path.endswith('.txt')
            
            # Verify content
            with open(report_path, 'r') as f:
                content = f.read()
                assert "MIGRATION REPORT" in content
                assert "USER MIGRATION SUMMARY" in content
                assert "Success: 98" in content
    
    def test_generate_error_log(self):
        """Test error log generation"""
        from migration.reporting import MigrationReporter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = MigrationReporter()
            reporter.report_dir = tmpdir
            
            all_errors = {
                "users": [
                    {"email": "test1@example.com", "error": "Duplicate email"},
                    {"email": "test2@example.com", "error": "Invalid format"}
                ],
                "bookings": [
                    {"booking_id": "123", "error": "Missing client"}
                ]
            }
            
            error_log_path = reporter.generate_error_log(all_errors)
            
            assert os.path.exists(error_log_path)
            assert error_log_path.endswith('.csv')
            
            # Verify content
            with open(error_log_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 3
                assert rows[0]['entity_type'] == 'users'
                assert rows[0]['record_id'] == 'test1@example.com'
    
    def test_generate_json_report(self):
        """Test JSON report generation"""
        from migration.reporting import MigrationReporter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = MigrationReporter()
            reporter.report_dir = tmpdir
            
            report_data = {
                "user_stats": {"total": 100, "success": 98},
                "duration_seconds": 120.5
            }
            
            json_path = reporter.generate_json_report(report_data)
            
            assert os.path.exists(json_path)
            assert json_path.endswith('.json')
            
            # Verify content
            with open(json_path, 'r') as f:
                data = json.load(f)
                assert data["user_stats"]["total"] == 100
                assert data["duration_seconds"] == 120.5
                assert "generated_at" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
