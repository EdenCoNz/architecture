# Equipment Data Migration Guide

## Story 19.10: Migrate Existing Equipment Data

This guide provides instructions for operators to safely migrate existing equipment assessment data from any legacy multiple-selection format to the new single-selection format.

---

## Overview

The migration command converts equipment data in existing user assessments to ensure compatibility with the new single-selection equipment assessment (implemented in Stories 19.4-19.9).

### What It Does

1. **Converts multiple selections to single selection** using hierarchy:
   - `full_gym` (most advanced) > `basic_equipment` > `no_equipment`
   - Retains the most specific/advanced option when multiple exist

2. **Flags assessments needing re-assessment**:
   - `basic_equipment` without specific equipment items
   - Users will need to specify their equipment when they next access the system

3. **Preserves valid data**:
   - Assessments already in single-selection format are skipped
   - All other assessment fields (sport, age, experience, etc.) remain unchanged

4. **Provides detailed reporting**:
   - Summary statistics (migrated, flagged, skipped, errors)
   - Per-user details for audit trails

---

## Prerequisites

- Backend application deployed with Story 19.10 code
- Database backup completed (recommended)
- Django environment configured
- Access to backend server or container

---

## Migration Workflow

### Step 1: Preview Migration (Dry Run)

**Always run a dry-run first to preview the impact:**

```bash
# Activate virtual environment
cd /home/ed/Dev/architecture/backend
source venv/bin/activate

# Run dry-run migration
python manage.py migrate_equipment_data --dry-run
```

**Expected Output:**
```
Starting equipment data migration...
DRY RUN MODE - No changes will be saved
Found 150 assessments to process
Rolling back changes (dry run mode)

--- Migration Report ---
Total Processed: 150
Migrated: 25
Flagged for Re-assessment: 10
Skipped (Already Valid): 115
Errors: 0

Migration completed successfully!
```

### Step 2: Review Dry Run Results

Check the dry-run output for:

- **Migrated count**: Assessments with multiple selections that will be converted
- **Flagged count**: Users needing to re-complete equipment assessment
- **Errors count**: Any problematic data that needs investigation

If errors > 0, investigate before proceeding to production migration.

### Step 3: Run Production Migration

**Once satisfied with dry-run results:**

```bash
# Run production migration with detailed report
python manage.py migrate_equipment_data --save-report /tmp/equipment_migration_$(date +%Y%m%d_%H%M%S).json
```

**Expected Output:**
```
Starting equipment data migration...
Found 150 assessments to process

--- Migration Report ---
Total Processed: 150
Migrated: 25
Flagged for Re-assessment: 10
Skipped (Already Valid): 115
Errors: 0

Report saved to: /tmp/equipment_migration_20251031_203000.json
Migration completed successfully!
```

### Step 4: Review Migration Report

The JSON report contains detailed information for each user:

```json
{
  "summary": {
    "total_processed": 150,
    "migrated": 25,
    "flagged": 10,
    "skipped": 115,
    "errors": 0
  },
  "details": [
    {
      "user_id": 42,
      "user_email": "user@example.com",
      "status": "migrated",
      "original_equipment": ["no_equipment", "full_gym"],
      "new_equipment": "full_gym",
      "items_cleared": true
    },
    {
      "user_id": 123,
      "user_email": "another@example.com",
      "status": "flagged",
      "reason": "Basic equipment without specific items - user needs to re-assess",
      "original_equipment": "basic_equipment",
      "original_items": []
    }
  ]
}
```

### Step 5: Communicate with Flagged Users (Optional)

For users flagged for re-assessment:

1. Extract flagged user emails from report:
   ```bash
   cat /tmp/equipment_migration_*.json | jq '.details[] | select(.status=="flagged") | .user_email'
   ```

2. Consider sending notification:
   - "We've updated our equipment assessment"
   - "Please re-complete your equipment details for better program recommendations"

---

## Command Reference

### Syntax

```bash
python manage.py migrate_equipment_data [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview migration without saving changes |
| `--save-report <file>` | Save detailed JSON report to specified file |

### Examples

```bash
# Preview only
python manage.py migrate_equipment_data --dry-run

# Production migration
python manage.py migrate_equipment_data

# Production with report
python manage.py migrate_equipment_data --save-report /var/log/migration_report.json

# Dry run with report (useful for planning)
python manage.py migrate_equipment_data --dry-run --save-report /tmp/dry_run_report.json
```

---

## Migration Categories

### Migrated
- **What**: Assessments with multiple equipment selections
- **Action**: Converted to single selection using hierarchy
- **User Impact**: Equipment updated to most advanced option
- **Example**: `["no_equipment", "full_gym"]` → `"full_gym"`

### Flagged
- **What**: Assessments with `basic_equipment` but no specific items
- **Action**: Flagged for re-assessment
- **User Impact**: Will see prompt to specify equipment items on next login
- **Example**: `equipment="basic_equipment", items=[]`

### Skipped
- **What**: Assessments already in valid single-selection format
- **Action**: No changes made
- **User Impact**: None - assessment already compliant
- **Example**: `equipment="full_gym"` (already valid)

### Errors
- **What**: Assessments with invalid or unexpected data
- **Action**: Logged but not migrated
- **User Impact**: May need manual investigation
- **Example**: `equipment="invalid_value"`

---

## Rollback Strategy

If migration causes issues:

1. **Restore from database backup**:
   ```bash
   # Example with PostgreSQL
   pg_restore -d backend_db /path/to/backup.dump
   ```

2. **Re-run deployment** of previous application version

3. **Investigate migration report** to identify problematic assessments

---

## Troubleshooting

### Issue: "No assessments found to migrate"

**Cause**: Database has no assessment records

**Solution**: Verify you're connected to correct database

### Issue: High error count in dry-run

**Cause**: Assessments with invalid equipment data

**Solution**:
1. Review error details in output
2. Check for data corruption or legacy format issues
3. Consider manual data cleanup before migration

### Issue: Migration takes too long

**Cause**: Large number of assessments

**Solution**: Migration processes all assessments in single transaction, which is correct behavior. For very large databases (>10,000 assessments), monitor progress and consider running during maintenance window.

---

## Post-Migration Verification

After migration, verify:

1. **Check assessment data**:
   ```bash
   python manage.py shell
   >>> from apps.assessments.models import Assessment
   >>> Assessment.objects.filter(equipment__in=['basic_equipment', 'full_gym', 'no_equipment']).count()
   # Should equal total assessments
   ```

2. **Test user login**:
   - Log in as user from "migrated" category
   - Verify equipment selection displays correctly
   - Confirm program generation works

3. **Test flagged user workflow**:
   - Log in as user from "flagged" category
   - Verify re-assessment prompt appears (if implemented in frontend)

---

## Command Implementation Details

**Location**: `/home/ed/Dev/architecture/backend/apps/assessments/management/commands/migrate_equipment_data.py`

**Test Suite**: `/home/ed/Dev/architecture/backend/tests/integration/test_migrate_equipment_data.py`

**Coverage**: 28 tests with 83% code coverage

**Key Features**:
- Atomic transaction (all-or-nothing)
- Dry-run mode with rollback
- Detailed per-user tracking
- Error handling without failure cascade
- JSON report export

---

## Support

For issues or questions:
1. Review migration report details
2. Check application logs for errors
3. Consult implementation log at `/home/ed/Dev/architecture/docs/features/19/implementation-log.json`
4. Contact backend development team

---

**Last Updated**: 2025-10-31
**Story**: 19.10 - Migrate Existing Equipment Data
**Status**: Production Ready
