# Migration Quick Start Guide

This guide will help you quickly migrate data from CultureBridge Phase 1 (Bubble) to Phase 2 (PostgreSQL).

## Prerequisites

1. **Python Environment**: Python 3.11+ installed
2. **Database**: PostgreSQL 15+ running and accessible
3. **Dependencies**: All backend dependencies installed
4. **Bubble Access**: Valid Bubble API key

## Quick Start (5 Steps)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env` file or set environment variables:

```bash
# Required
export BUBBLE_API_URL="https://culturebridge-phase1.bubbleapps.io/api/1.1"
export BUBBLE_API_KEY="your_bubble_api_key_here"
export DATABASE_URL="postgresql://user:password@localhost:5432/culturebridge"

# Optional (defaults shown)
export MIGRATION_BATCH_SIZE="100"
export MIGRATION_EXPORT_DIR="./migration_data"
export MIGRATION_REPORT_DIR="./migration_reports"
```

### Step 3: Prepare Database

Ensure your database is ready:

```bash
# Run migrations to create tables
alembic upgrade head

# Verify database connection
python -c "from app.database import engine; print('Database connected:', engine.url)"
```

### Step 4: Run Migration

Execute the full migration:

```bash
python -m migration.run_migration
```

This will:
- ✓ Export data from Bubble API
- ✓ Migrate users (with password re-hashing)
- ✓ Migrate profiles (clients and coaches)
- ✓ Migrate bookings and payments
- ✓ Validate data integrity
- ✓ Generate reports

**Expected Duration**: 5-30 minutes depending on data volume

### Step 5: Review Results

Check the migration reports:

```bash
# View summary report
cat migration_reports/migration_summary_*.txt

# Check for errors
cat migration_reports/migration_errors_*.csv

# View detailed log
cat migration_reports/migration_*.log
```

## What Gets Migrated?

| Entity | Phase 1 Source | Phase 2 Destination |
|--------|----------------|---------------------|
| Users | Bubble User table | PostgreSQL `users` table |
| Client Profiles | Bubble ClientProfile | PostgreSQL `client_profiles` |
| Coach Profiles | Bubble CoachProfile | PostgreSQL `coach_profiles` |
| Bookings | Bubble Booking | PostgreSQL `bookings` |
| Payments | Bubble Payment | PostgreSQL `payments` |

## Key Features

### Password Security
- All passwords are **re-hashed** using bcrypt with 12 salt rounds
- Original Phase 1 passwords are not copied directly
- Users will need to use their existing passwords (they work with new hashes)

### Data Validation
- Row counts verified (Phase 1 vs Phase 2)
- Referential integrity checked (all foreign keys valid)
- Data quality validated (email formats, rate ranges, etc.)
- Sample data spot-checked

### Error Handling
- Failed records logged with details
- Migration continues even if some records fail
- Comprehensive error reporting
- Rollback capability included

## Validation Checklist

After migration, verify:

- [ ] User count matches Phase 1
- [ ] All users can log in with existing passwords
- [ ] Client profiles have quiz data
- [ ] Coach profiles have expertise and languages
- [ ] Bookings linked to correct clients and coaches
- [ ] Payments linked to bookings
- [ ] No orphaned records (referential integrity)

## Common Scenarios

### Scenario 1: First-Time Migration

```bash
# Full migration with export
python -m migration.run_migration
```

### Scenario 2: Re-run Migration (Data Already Exported)

```bash
# Skip export, use existing CSV files
python -m migration.run_migration --skip-export
```

### Scenario 3: Test Migration

```bash
# Use a test database
export DATABASE_URL="postgresql://user:password@localhost:5432/culturebridge_test"
python -m migration.run_migration
```

### Scenario 4: Incremental Migration

```bash
# Export only
python -m migration.bubble_export

# Migrate users only
python -m migration.migrate_users

# Migrate profiles only
python -m migration.migrate_profiles

# Migrate bookings only
python -m migration.migrate_bookings

# Validate only
python -m migration.validation
```

## Troubleshooting

### Issue: "BUBBLE_API_KEY not set"

**Solution**: Set the environment variable:
```bash
export BUBBLE_API_KEY="your_key_here"
```

### Issue: "Database connection failed"

**Solution**: Check DATABASE_URL and ensure PostgreSQL is running:
```bash
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: "User ID mapping not found"

**Solution**: Run user migration first:
```bash
python -m migration.migrate_users
```

### Issue: "Validation errors found"

**Solution**: Review the error log and fix data issues:
```bash
cat migration_reports/migration_errors_*.csv
```

## Rollback

If you need to undo the migration:

```bash
# Find the rollback script
ls migration_reports/rollback_migration_*.sql

# Review the script
cat migration_reports/rollback_migration_YYYYMMDD_HHMMSS.sql

# Execute rollback (CAUTION: This deletes all migrated data!)
psql $DATABASE_URL -f migration_reports/rollback_migration_YYYYMMDD_HHMMSS.sql
```

## Production Migration Checklist

Before running in production:

- [ ] Backup Phase 1 data
- [ ] Backup Phase 2 database
- [ ] Test migration on staging environment
- [ ] Review and approve test results
- [ ] Schedule maintenance window
- [ ] Notify users of downtime
- [ ] Set Phase 1 to read-only mode
- [ ] Run production migration
- [ ] Validate results
- [ ] Test critical user flows
- [ ] Update DNS if needed
- [ ] Monitor for issues
- [ ] Keep Phase 1 available for 30 days (read-only)

## Performance Tips

### For Large Datasets (>10,000 users)

1. **Increase Batch Size**:
   ```bash
   export MIGRATION_BATCH_SIZE="500"
   ```

2. **Disable Database Logging**:
   ```bash
   export ENVIRONMENT="production"  # Disables SQL echo
   ```

3. **Run During Off-Peak Hours**:
   - Less load on Bubble API
   - Faster database writes

4. **Monitor Resources**:
   ```bash
   # Watch database connections
   psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity"
   
   # Monitor disk space
   df -h
   ```

## Support

For issues or questions:
- Check the detailed README: `migration/README.md`
- Review migration logs: `migration_reports/migration_*.log`
- Contact development team

## Next Steps

After successful migration:

1. **Verify Data**: Spot-check migrated records
2. **Test Features**: Test key user flows (login, booking, payment)
3. **Update Documentation**: Document any migration-specific notes
4. **Archive Reports**: Save migration reports for audit trail
5. **Monitor Production**: Watch for any post-migration issues

## Quick Reference

```bash
# Full migration
python -m migration.run_migration

# Skip export
python -m migration.run_migration --skip-export

# Individual steps
python -m migration.bubble_export
python -m migration.migrate_users
python -m migration.migrate_profiles
python -m migration.migrate_bookings
python -m migration.validation

# View reports
ls migration_reports/
cat migration_reports/migration_summary_*.txt
```

---

**Ready to migrate?** Run `python -m migration.run_migration` and follow the prompts!
