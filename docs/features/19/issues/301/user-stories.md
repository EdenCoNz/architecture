# Issue #301: CI/CD Pipeline Failed - Build and Test Run #95

**Feature**: 19 - Equipment Assessment Single Selection with Conditional Follow-up
**Branch**: feature/19-equipment-assessment-single-selection-with-item-input
**Issue Type**: Fix
**Created**: 2025-11-01

## Issue Summary

CI/CD pipeline Build and Test job failed with 15 test failures:
- 14 tests: Acceptance tests for docker-dev.sh script failing (file not accessible in test container)
- 1 test: Equipment migration details tracking not recording migration information

## Root Cause Analysis

### Issue 1: Docker Development Script Tests (14 failures)
**Root Cause**: Acceptance tests for Story #13 startup scripts were updated in this branch to verify Docker Compose workflow, but tests run inside the backend container where project root files are not mounted. The backend container only mounts `./backend:/app`, so `docker-dev.sh` at project root is not accessible to tests.

**Test Environment**: Tests execute inside backend Docker container via `docker compose exec backend pytest`
**File Location**: `/home/ed/Dev/architecture/docker-dev.sh` (project root)
**Container Mount**: `./backend:/app` (only backend directory mounted)
**Test Path Resolution**: `Path(__file__).parent.parent.parent.parent` -> `/app/../docker-dev.sh` (does not exist)

### Issue 2: Equipment Migration Details Tracking (1 failure)
**Root Cause**: The EquipmentMigrator class is not appending migration detail records to the `migration_details` list when processing assessments.

**Test**: `test_migration_details_tracking` in `backend/tests/integration/test_migrate_equipment_data.py`
**Expected Behavior**: When migrating equipment data, migrator should track user ID, email, status, original equipment, and new equipment in `migration_details` list

---

## User Stories

### Story 301.1: Mount Project Root Files for Acceptance Tests

**Title**: Mount Project Root Files for Acceptance Tests

**Description**: As a developer running acceptance tests, I need project root files to be accessible inside the test container so that tests verifying deployment scripts and configuration can validate their existence and content.

**Assigned Agent**: devops-engineer

**Acceptance Criteria**:
- Given I run acceptance tests via `docker compose exec backend pytest`, when tests reference project root files like `docker-dev.sh`, then those files should be accessible at the expected paths
- Given the backend container is running, when I check the container filesystem, then I should see project root files mounted at a location accessible to tests
- Given acceptance tests verify script existence, when they run inside the container, then they should pass without "file does not exist" errors
- Given I update project root scripts, when tests run in the container, then they should see the latest changes via volume mounts

**Technical Context**:
- Tests currently run: `docker compose exec backend pytest`
- Backend mount: `./backend:/app` in docker-compose.yml
- Test file: `backend/tests/acceptance/test_story13_startup_scripts.py`
- Path resolution: `Path(__file__).parent.parent.parent.parent` assumes project root at `/app/..`
- Required files: docker-dev.sh, docker-compose.yml, compose.*.yml at project root

**Implementation Notes**:
- DO NOT modify test files - they are correctly checking for required infrastructure
- Mount project root to container OR adjust volume mounts to make root files accessible
- Consider mounting specific files if full root mount creates conflicts
- Ensure test environment matches developer local environment expectations

---

### Story 301.2: Record Equipment Migration Details

**Title**: Record Equipment Migration Details

**Description**: As a system administrator reviewing equipment data migrations, I need detailed records of each assessment migration so that I can audit what changes were made and verify migration correctness.

**Assigned Agent**: backend-developer

**Acceptance Criteria**:
- Given I migrate an assessment with equipment data, when the migration completes, then the migrator should append a detail record to the `migration_details` list
- Given an assessment is migrated from multiple selections to single selection, when I check migration details, then I should see the user ID, user email, migration status, original equipment value, and new equipment value
- Given I generate a migration report, when I check the details section, then it should contain individual records for each processed assessment
- Given multiple assessments are migrated, when migration completes, then the `migration_details` list should have one entry per processed assessment

**Technical Context**:
- File: `backend/apps/assessments/management/commands/migrate_equipment_data.py`
- Class: `EquipmentMigrator`
- Method: `migrate_equipment_field(assessment)`
- Test: `test_migration_details_tracking` in `backend/tests/integration/test_migrate_equipment_data.py`
- Expected detail structure: `{"user_id": int, "user_email": str, "status": str, "original_equipment": Any, "new_equipment": str}`

**Implementation Notes**:
- Append detail record after successful migration
- Include both successful and failed migrations in details
- Ensure detail status matches migration outcome: "migrated", "skipped", "flagged", "error"
- Use existing migrator state tracking (migrated_count, flagged_count, etc.)

---

## Execution Order

### Phase 1: Parallel Resolution (No Dependencies)
- Story 301.1 (devops-engineer) - Fix container volume mounts
- Story 301.2 (backend-developer) - Fix migration details tracking

Both issues are independent and can be fixed in parallel.

---

## Story Assignment Summary

| Story ID | Title | Agent | Type |
|----------|-------|-------|------|
| 301.1 | Mount Project Root Files for Acceptance Tests | devops-engineer | Infrastructure |
| 301.2 | Record Equipment Migration Details | backend-developer | Backend Logic |

---

## Quality Validation

### Generic & Implementation-Agnostic
- ✅ No frameworks, libraries, or technologies prescribed
- ✅ No architecture patterns or code structure specified
- ✅ Stories work regardless of implementation approach

### User-Focused
- ✅ Story 301.1: Developer perspective - running acceptance tests
- ✅ Story 301.2: System administrator perspective - reviewing migrations
- ✅ Uses domain language: "acceptance tests", "migration details", "audit"

### Acceptance Criteria
- ✅ All criteria describe observable outcomes
- ✅ Uses "Given... When... Then..." patterns
- ✅ No technical validation implementation details

### Atomic
- ✅ Story 301.1: ONE capability - make project files accessible to tests
- ✅ Story 301.2: ONE capability - record migration details
- ✅ Each has 4 acceptance criteria
- ✅ Each deliverable in 1-3 days

### Red Flag Check
- ✅ No specific framework mentions
- ✅ No code structure descriptions
- ✅ Could be implemented with different technology stacks
- ✅ Focus on WHAT needs to work, not HOW to implement

---

## Notes

**Test Failure Pattern**: All 14 docker-dev.sh tests follow same pattern - file existence check fails because project root is not mounted in test container.

**Migration Details**: Test creates assessment with `equipment=["no_equipment", "full_gym"]`, expects migrator to track this in `migration_details` list with user info and before/after equipment values.

**Design Philosophy**: Tests are correct - they verify required infrastructure exists and works. Fix should adjust infrastructure to match test expectations, not modify tests.
