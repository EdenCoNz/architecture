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

    # Determine the inferred state to ensure history ends with current state
    inferred_state = infer_state(feature)

    # Always start with planned state
    if feature.get('createdAt'):
        history.append({
            'state': 'planned',
            'timestamp': feature['createdAt'],
            'triggeredBy': 'command',
            'notes': 'Migrated from legacy feature log'
        })

    # Add in_progress if user stories were created
    # Include it if userStoriesCreated exists AND we're in_progress or beyond
    if (feature.get('userStoriesCreated') and
        inferred_state in ['in_progress', 'testing', 'review', 'deployed', 'summarised']):
        # Only add a separate entry if timestamp differs from createdAt
        if feature.get('userStoriesCreated') != feature.get('createdAt'):
            history.append({
                'state': 'in_progress',
                'timestamp': feature['userStoriesCreated'],
                'triggeredBy': 'command',
                'notes': 'Migrated from legacy feature log'
            })
        # If timestamps are same but we're in_progress state, update the last entry
        elif inferred_state == 'in_progress':
            history[-1]['state'] = 'in_progress'

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
