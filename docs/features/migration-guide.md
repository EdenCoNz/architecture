# Feature Log Migration Guide

## Overview

This guide provides step-by-step instructions for migrating existing `feature-log.json` entries to the new extended state tracking schema. The migration adds `state` and `stateHistory` fields while preserving all existing data.

## Prerequisites

Before starting the migration:

1. Backup your current `feature-log.json` file
2. Ensure you have Python 3 installed (for validation)
3. Ensure your current `feature-log.json` has valid JSON syntax

## Backup Current Feature Log

```bash
cp docs/features/feature-log.json docs/features/feature-log.json.backup
```

## Migration Options

You have two options for migration:

1. **Automatic Migration** (Recommended): Use the migration script provided
2. **Manual Migration**: Manually edit each feature entry

## Option 1: Automatic Migration (Recommended)

### Step 1: Create Migration Script

Create a file at `scripts/migrate-feature-log.py`:

```python
#!/usr/bin/env python3
"""
Feature Log Migration Script
Migrates feature-log.json to the new state tracking schema.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def infer_state(feature):
    """Infer current state based on existing timestamp fields."""
    if feature.get('summarisedAt'):
        return 'summarised'
    elif feature.get('userStoriesImplemented'):
        return 'deployed'
    elif feature.get('userStoriesCreated'):
        return 'in_progress'
    else:
        return 'planned'


def construct_state_history(feature):
    """Construct state history from existing timestamp fields."""
    history = []

    # Always start with planned state
    if feature.get('createdAt'):
        history.append({
            'state': 'planned',
            'timestamp': feature['createdAt'],
            'triggeredBy': 'command',
            'notes': 'Migrated from legacy feature log'
        })

    # Add in_progress if user stories were created (and not same as createdAt)
    if (feature.get('userStoriesCreated') and
        feature.get('userStoriesCreated') != feature.get('createdAt')):
        history.append({
            'state': 'in_progress',
            'timestamp': feature['userStoriesCreated'],
            'triggeredBy': 'command',
            'notes': 'Migrated from legacy feature log'
        })

    # Add deployed if implementation completed
    if feature.get('userStoriesImplemented'):
        history.append({
            'state': 'deployed',
            'timestamp': feature['userStoriesImplemented'],
            'triggeredBy': 'command',
            'notes': 'Migrated from legacy feature log'
        })

    # Add summarised if feature was summarised
    if feature.get('summarisedAt'):
        history.append({
            'state': 'summarised',
            'timestamp': feature['summarisedAt'],
            'triggeredBy': 'command',
            'notes': 'Migrated from legacy feature log'
        })

    return history


def migrate_feature(feature):
    """Migrate a single feature to the new schema."""
    # Check if already migrated
    if 'state' in feature and 'stateHistory' in feature:
        return feature, False

    # Infer state and construct history
    migrated_feature = feature.copy()
    migrated_feature['state'] = infer_state(feature)
    migrated_feature['stateHistory'] = construct_state_history(feature)

    return migrated_feature, True


def validate_migration(feature):
    """Validate a migrated feature."""
    errors = []

    # Check required fields exist
    if 'state' not in feature:
        errors.append(f"Feature {feature.get('featureID', 'unknown')} missing 'state' field")
    if 'stateHistory' not in feature:
        errors.append(f"Feature {feature.get('featureID', 'unknown')} missing 'stateHistory' field")

    # Validate state is valid
    valid_states = ['planned', 'in_progress', 'testing', 'review', 'deployed', 'summarised', 'archived']
    if feature.get('state') not in valid_states:
        errors.append(f"Feature {feature.get('featureID', 'unknown')} has invalid state: {feature.get('state')}")

    # Validate state history is not empty
    if not feature.get('stateHistory'):
        errors.append(f"Feature {feature.get('featureID', 'unknown')} has empty state history")

    # Validate last state in history matches current state
    if feature.get('stateHistory'):
        last_state = feature['stateHistory'][-1]['state']
        if last_state != feature['state']:
            errors.append(
                f"Feature {feature.get('featureID', 'unknown')} state mismatch: "
                f"current='{feature['state']}' vs last history='{last_state}'"
            )

    # Validate state history is chronological
    if feature.get('stateHistory') and len(feature['stateHistory']) > 1:
        timestamps = [entry['timestamp'] for entry in feature['stateHistory']]
        sorted_timestamps = sorted(timestamps)
        if timestamps != sorted_timestamps:
            errors.append(f"Feature {feature.get('featureID', 'unknown')} state history is not chronological")

    return errors


def migrate_feature_log(input_path, output_path, dry_run=False):
    """Migrate entire feature log."""
    # Read current feature log
    try:
        with open(input_path, 'r') as f:
            feature_log = json.load(f)
    except FileNotFoundError:
        print(f"Error: Feature log not found at {input_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in feature log: {e}")
        return False

    # Migrate each feature
    migrated_count = 0
    skipped_count = 0
    errors = []

    migrated_features = []
    for feature in feature_log.get('features', []):
        migrated_feature, was_migrated = migrate_feature(feature)

        if was_migrated:
            migrated_count += 1
        else:
            skipped_count += 1

        # Validate migration
        validation_errors = validate_migration(migrated_feature)
        if validation_errors:
            errors.extend(validation_errors)

        migrated_features.append(migrated_feature)

    # Update feature log with migrated features
    migrated_log = feature_log.copy()
    migrated_log['features'] = migrated_features

    # Report results
    print(f"\nMigration Summary:")
    print(f"  Total features: {len(migrated_features)}")
    print(f"  Migrated: {migrated_count}")
    print(f"  Already migrated (skipped): {skipped_count}")

    if errors:
        print(f"\n⚠️  Validation Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"\n✓ All features validated successfully")

    # Write migrated feature log
    if not dry_run:
        try:
            with open(output_path, 'w') as f:
                json.dump(migrated_log, f, indent=2)
            print(f"\n✓ Migrated feature log written to: {output_path}")
            return True
        except Exception as e:
            print(f"\nError writing migrated feature log: {e}")
            return False
    else:
        print(f"\n[DRY RUN] Would write to: {output_path}")
        print("\nPreview of first migrated feature:")
        if migrated_features:
            print(json.dumps(migrated_features[0], indent=2))
        return True


def main():
    """Main migration function."""
    # Parse arguments
    dry_run = '--dry-run' in sys.argv

    # Define paths
    input_path = Path('docs/features/feature-log.json')
    output_path = Path('docs/features/feature-log.json')

    if dry_run:
        print("Running in DRY RUN mode - no files will be modified\n")

    # Run migration
    success = migrate_feature_log(input_path, output_path, dry_run)

    if success:
        print("\n✓ Migration completed successfully!")
        if not dry_run:
            print("\nNext steps:")
            print("  1. Validate the migrated feature log:")
            print("     python3 -m json.tool docs/features/feature-log.json")
            print("  2. Review the changes:")
            print("     git diff docs/features/feature-log.json")
            print("  3. If everything looks good, commit the changes")
            print("\nBackup location: docs/features/feature-log.json.backup")
        sys.exit(0)
    else:
        print("\n✗ Migration failed - feature log not modified")
        print("\nPlease fix the errors and try again")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Step 2: Run Migration (Dry Run First)

First, test the migration without modifying any files:

```bash
python3 scripts/migrate-feature-log.py --dry-run
```

Review the output to ensure the migration looks correct.

### Step 3: Run Actual Migration

If the dry run looks good, run the actual migration:

```bash
python3 scripts/migrate-feature-log.py
```

### Step 4: Validate Migration

Validate the JSON syntax:

```bash
python3 -m json.tool docs/features/feature-log.json > /dev/null && echo "✓ Valid JSON"
```

Review the changes:

```bash
git diff docs/features/feature-log.json
```

### Step 5: Commit Changes

If everything looks good, commit the migrated feature log:

```bash
git add docs/features/feature-log.json
git commit -m "Migrate feature log to extended state tracking schema

- Added state field to all features
- Added stateHistory with transition tracking
- Maintained backward compatibility
- All existing fields preserved"
```

## Option 2: Manual Migration

If you prefer to manually migrate the feature log:

### Step 1: Open feature-log.json

Open `docs/features/feature-log.json` in your text editor.

### Step 2: Add Fields to Each Feature

For each feature in the `features` array, add the `state` and `stateHistory` fields.

**Example - Feature that is summarised:**

Before:
```json
{
  "featureID": "1",
  "title": "Initialize Frontend Web Application",
  "createdAt": "2025-10-15T00:00:00Z",
  "userStoriesCreated": "2025-10-15T00:00:00Z",
  "userStoriesImplemented": "2025-10-15T20:00:00Z",
  "isSummarised": true,
  "summarisedAt": "2025-10-15T20:15:00Z",
  "actions": []
}
```

After:
```json
{
  "featureID": "1",
  "title": "Initialize Frontend Web Application",
  "state": "summarised",
  "stateHistory": [
    {
      "state": "planned",
      "timestamp": "2025-10-15T00:00:00Z",
      "triggeredBy": "command",
      "notes": "Migrated from legacy feature log"
    },
    {
      "state": "deployed",
      "timestamp": "2025-10-15T20:00:00Z",
      "triggeredBy": "command",
      "notes": "Migrated from legacy feature log"
    },
    {
      "state": "summarised",
      "timestamp": "2025-10-15T20:15:00Z",
      "triggeredBy": "command",
      "notes": "Migrated from legacy feature log"
    }
  ],
  "createdAt": "2025-10-15T00:00:00Z",
  "userStoriesCreated": "2025-10-15T00:00:00Z",
  "userStoriesImplemented": "2025-10-15T20:00:00Z",
  "isSummarised": true,
  "summarisedAt": "2025-10-15T20:15:00Z",
  "actions": []
}
```

### Step 3: Determine State for Each Feature

Use this logic to determine the current state:

1. If `summarisedAt` is set → `"summarised"`
2. Else if `userStoriesImplemented` is set → `"deployed"`
3. Else if `userStoriesCreated` is set → `"in_progress"`
4. Else → `"planned"`

### Step 4: Construct State History

Build the state history array based on available timestamps:

1. Always include `"planned"` entry with `createdAt` timestamp
2. If `userStoriesCreated` exists and differs from `createdAt`, add `"in_progress"` entry
3. If `userStoriesImplemented` exists, add `"deployed"` entry
4. If `summarisedAt` exists, add `"summarised"` entry

### Step 5: Validate JSON Syntax

After editing, validate the JSON:

```bash
python3 -m json.tool docs/features/feature-log.json > /dev/null && echo "✓ Valid JSON"
```

### Step 6: Commit Changes

```bash
git add docs/features/feature-log.json
git commit -m "Migrate feature log to extended state tracking schema"
```

## Validation Checklist

After migration, verify:

- [ ] All features have a `state` field
- [ ] All features have a `stateHistory` array
- [ ] State history has at least one entry per feature
- [ ] Current `state` matches last entry in `stateHistory`
- [ ] State history is in chronological order
- [ ] All existing fields are preserved
- [ ] JSON syntax is valid
- [ ] No features are missing

## Rollback Procedure

If you need to rollback the migration:

```bash
# Restore from backup
cp docs/features/feature-log.json.backup docs/features/feature-log.json

# Validate the restored file
python3 -m json.tool docs/features/feature-log.json > /dev/null && echo "✓ Rollback successful"
```

## Common Issues

### Issue: JSON Syntax Error After Migration

**Symptom**: `python3 -m json.tool` reports syntax error

**Solution**:
1. Check for missing commas between fields
2. Check for trailing commas in arrays or objects
3. Ensure all strings are properly quoted
4. Validate bracket/brace matching

### Issue: State History Not Chronological

**Symptom**: Timestamps in stateHistory are out of order

**Solution**:
1. Review the timestamps in your original feature log
2. Ensure state history is built in chronological order
3. Sort state history entries by timestamp if needed

### Issue: State Mismatch

**Symptom**: Current `state` doesn't match last entry in `stateHistory`

**Solution**:
1. Review the state inference logic
2. Ensure the last state history entry matches the current state
3. Update either the `state` field or the last `stateHistory` entry

## Testing the Migration

After migration, test that the system still works:

```bash
# Test that commands can read the new schema
# (These are just checks - don't actually run unless you want to)

# View the feature log
cat docs/features/feature-log.json | python3 -m json.tool

# Check that all features have required fields
python3 -c "
import json
with open('docs/features/feature-log.json') as f:
    data = json.load(f)
    for feature in data['features']:
        assert 'state' in feature, f\"Feature {feature['featureID']} missing state\"
        assert 'stateHistory' in feature, f\"Feature {feature['featureID']} missing stateHistory\"
print('✓ All features have required fields')
"
```

## Post-Migration Steps

After successful migration:

1. Delete the backup file (if you're confident):
   ```bash
   rm docs/features/feature-log.json.backup
   ```

2. Update any custom scripts or tools that read `feature-log.json` to handle the new fields

3. Consider updating slash commands to automatically manage state transitions

## Support

If you encounter issues during migration:

1. Check the validation errors from the migration script
2. Review the state system documentation at `docs/features/feature-state-system.md`
3. Ensure you have a backup before making changes
4. Test with the `--dry-run` flag first

## Migration Script Location

The migration script should be created at:
```
scripts/migrate-feature-log.py
```

Make it executable:
```bash
chmod +x scripts/migrate-feature-log.py
```
