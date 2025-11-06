# CultureBridge Phase 1 to Phase 2 Migration

This package contains scripts and utilities for migrating data from Phase 1 (Bubble) to Phase 2 (PostgreSQL).

## Overview

The migration process consists of the following steps:

1. **Export**: Export data from Bubble API to CSV files
2. **User Migration**: Migrate users with password re-hashing (bcrypt, 12 rounds)
3. **Profile Migration**: Migrate client and coach profiles
4. **Booking Migration**: Migrate bookings and payments
5. **Validation**: Validate data integrity and referential relationships
6. **Reporting**: Generate comprehensive migration reports

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Access to Bubble API (API key required)
- All backend dependencies installed (`pip install -r requirements.txt`)

## Configuration

Set the following environment variables:

```bash
# Bubble API Configuration
export BUBBLE_API_URL="https://culturebridge-phase1.bubbleapps.io/api/1.1"
export BUBBLE_API_KEY="your_bubble_api_key_here"

# Database Configuration (from main app config)
export DATABASE_URL="postgresql://user:password@localhost:5432/culturebridge"

# Migration Configuration (optional)
export MIGRATION_BATCH_SIZE="100"
export MIGRATION_EXPORT_DIR="./migration_data"
export MIGRATION_REPORT_DIR="./migration_reports"
```

## Usage

### Full Migration (Recommended)

Run the complete migration process:

```bash
cd backend
python -m migration.run_migration
```

This will:
- Export all data from Bubble API
- Migrate users, profiles, bookings, and payments
- Validate data integrity
- Generate comprehensive reports

### Skip Export (Use Existing Data)

If you already have exported CSV files:

```bash
python -m migration.run_migration --skip-export
```

### Individual Migration Steps

You can also run individual migration steps:

#### 1. Export Data from Bubble

```bash
python -m migration.bubble_export
```

This creates CSV files in `./migration_data/`:
- `users.csv`
- `client_profiles.csv`
- `coach_profiles.csv`
- `bookings.csv`
- `payments.csv`

#### 2. Migrate Users

```bash
python -m migration.migrate_users
```

This:
- Migrates users from `users.csv`
- Re-hashes passwords with bcrypt (12 rounds)
- Maps Phase 1 roles to Phase 2 roles
- Generates `user_id_mapping.json` for profile migration

#### 3. Migrate Profiles

```bash
python -m migration.migrate_profiles
```

This:
- Migrates client profiles from `client_profiles.csv`
- Migrates coach profiles from `coach_profiles.csv`
- Uses `user_id_mapping.json` to link profiles to users

#### 4. Migrate Bookings and Payments

```bash
python -m migration.migrate_bookings
```

This:
- Migrates bookings from `bookings.csv`
- Migrates payments from `payments.csv`
- Links payments to bookings
- Generates `booking_id_mapping.json`

#### 5. Validate Data

```bash
python -m migration.validation
```

This validates:
- Row counts (Phase 1 vs Phase 2)
- Referential integrity (foreign key relationships)
- Data quality (business rules, constraints)
- Sample data (random sampling for spot checks)

## Field Mappings

### User Fields

| Phase 1 (Bubble) | Phase 2 (PostgreSQL) | Transformation |
|------------------|----------------------|----------------|
| email | email | Direct copy |
| password | password_hash | Re-hash with bcrypt (12 rounds) |
| type | role | Map: "seeker" → "client" |
| active | is_active | Direct copy |
| verified | email_verified | Direct copy |
| created_date | created_at | Parse datetime |
| modified_date | updated_at | Parse datetime |

### Client Profile Fields

| Phase 1 | Phase 2 | Transformation |
|---------|---------|----------------|
| first_name | first_name | Direct copy |
| last_name | last_name | Direct copy |
| photo | photo_url | Direct copy |
| phone_number | phone | Direct copy |
| time_zone | timezone | Direct copy |
| quiz_responses | quiz_data | Parse to JSONB |
| user_preferences | preferences | Parse to JSONB |

### Coach Profile Fields

| Phase 1 | Phase 2 | Transformation |
|---------|---------|----------------|
| first_name | first_name | Direct copy |
| last_name | last_name | Direct copy |
| biography | bio | Direct copy |
| expertise_areas | expertise | Parse to array |
| languages_spoken | languages | Parse to array |
| countries_experience | countries | Parse to array |
| rate | hourly_rate | Convert to decimal |
| availability_data | availability | Parse to JSONB |
| average_rating | rating | Convert to decimal |
| session_count | total_sessions | Convert to integer |

### Booking Fields

| Phase 1 | Phase 2 | Transformation |
|---------|---------|----------------|
| client_user_id | client_id | Map via user_id_mapping |
| coach_user_id | coach_id | Map via user_id_mapping |
| session_date | session_datetime | Parse datetime |
| duration | duration_minutes | Convert to integer |
| booking_status | status | Map: "complete" → "completed" |

### Payment Fields

| Phase 1 | Phase 2 | Transformation |
|---------|---------|----------------|
| booking_ref | booking_id | Map via booking_id_mapping |
| payment_amount | amount | Convert to decimal |
| currency_code | currency | Direct copy |
| payment_status | status | Map: "success" → "succeeded" |
| stripe_session | stripe_session_id | Direct copy |
| stripe_intent | stripe_payment_intent_id | Direct copy |

## Validation Checks

The migration includes comprehensive validation:

### Row Count Validation
- Compares record counts between Phase 1 CSV and Phase 2 database
- Ensures no data loss during migration

### Referential Integrity
- Validates all foreign key relationships
- Checks for orphaned records
- Ensures data consistency

### Data Quality
- Validates email formats
- Checks hourly rate ranges ($25-$500)
- Validates booking durations (> 0)
- Validates payment amounts (> 0)
- Ensures confirmed bookings have payments

### Sample Data Validation
- Random sampling of migrated records
- Spot checks for data accuracy
- Validates business rules

## Reports

The migration generates several reports in `./migration_reports/`:

### 1. Summary Report (`migration_summary_YYYYMMDD_HHMMSS.txt`)
- Overall migration statistics
- Success/failure counts by entity type
- Validation results
- Overall status

### 2. Error Log (`migration_errors_YYYYMMDD_HHMMSS.csv`)
- Detailed list of all migration errors
- Record IDs and error messages
- Useful for troubleshooting

### 3. JSON Report (`migration_report_YYYYMMDD_HHMMSS.json`)
- Machine-readable complete report
- All statistics and validation results
- Useful for automated processing

### 4. Rollback Script (`rollback_migration_YYYYMMDD_HHMMSS.sql`)
- SQL script to rollback migration
- Deletes all migrated data
- Use with caution!

### 5. Migration Log (`migration_YYYYMMDD_HHMMSS.log`)
- Detailed execution log
- All INFO, WARNING, and ERROR messages
- Useful for debugging

## Rollback

If you need to rollback the migration:

1. Review the generated rollback script in `./migration_reports/`
2. Execute the SQL script:

```bash
psql -U username -d culturebridge -f migration_reports/rollback_migration_YYYYMMDD_HHMMSS.sql
```

**WARNING**: This will delete all migrated data. Use with caution!

## Troubleshooting

### Common Issues

#### 1. Bubble API Connection Failed
- Check `BUBBLE_API_KEY` environment variable
- Verify API URL is correct
- Ensure network connectivity

#### 2. Database Connection Failed
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL is running
- Ensure database exists

#### 3. User ID Mapping Not Found
- Ensure user migration completed successfully
- Check `user_id_mapping.json` exists in export directory
- Run user migration before profile migration

#### 4. Validation Errors
- Review validation report for specific issues
- Check error log for failed records
- Fix data issues and re-run migration

#### 5. High Failure Rate
- Check migration log for error patterns
- Verify field mappings are correct
- Ensure Phase 1 data quality

### Getting Help

For issues or questions:
1. Check the migration log file
2. Review the error log CSV
3. Examine the validation report
4. Contact the development team

## Best Practices

1. **Test First**: Run migration on a test database before production
2. **Backup**: Always backup Phase 1 data before migration
3. **Validate**: Review validation reports carefully
4. **Monitor**: Watch logs during migration
5. **Verify**: Spot-check migrated data manually
6. **Document**: Keep migration reports for audit trail

## Architecture

```
migration/
├── __init__.py              # Package initialization
├── config.py                # Configuration and field mappings
├── bubble_export.py         # Bubble API export
├── field_mapper.py          # Field transformation utilities
├── migrate_users.py         # User migration with password re-hashing
├── migrate_profiles.py      # Profile migration (client & coach)
├── migrate_bookings.py      # Booking and payment migration
├── validation.py            # Data validation checks
├── reporting.py             # Report generation
├── run_migration.py         # Main orchestrator
└── README.md                # This file
```

## Requirements Mapping

This migration implementation satisfies the following requirements:

- **10.1**: Export data from Phase 1 system via API
- **10.2**: Map Phase 1 data fields to PostgreSQL schema
- **10.3**: Validate data integrity (row counts, referential integrity)
- **10.4**: Generate migration reports with error logging
- **10.5**: Implement rollback capability

## License

Copyright © 2025 CultureBridge. All rights reserved.
