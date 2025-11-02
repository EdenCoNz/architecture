# Issue #355 - Fix Stories

**Issue**: CI/CD Pipeline Failed: Build and Test - Run #145
**Feature**: 21 - Sports Terminology and Database Storage
**Branch**: feature/21-sports-terminology-and-storage

## Issue Summary

The CI/CD pipeline is failing due to a database migration reversibility issue. The reverse migration function attempts to change "soccer" back to "football", but this violates the database check constraint because "football" is no longer a valid choice after the forward migration (0002_update_sport_to_soccer.py) has been applied.

**Root Cause**: Migration 0002 changes the model's valid choices from ["football", "cricket"] to ["soccer", "cricket"], and Migration 0003's reverse function tries to update records back to "football", which violates the constraint.

**Impact**: Teams cannot safely roll back Feature 21 if issues are discovered in production. This creates deployment risk and violates database migration best practices.

---

## Story 355.1: Fix Reverse Migration Constraint Violation

**Assigned Agent**: backend-developer

**Description**:
As a developer, I need the reverse migration to execute successfully without constraint violations, so that the sports terminology migration can be safely rolled back if needed in production environments.

**Acceptance Criteria**:

1. **Given** I run the reverse migration on a database with "soccer" records, **when** the migration executes, **then** it should complete successfully without IntegrityError or constraint violations

2. **Given** the reverse migration completes, **when** I query the database, **then** records should be reverted from "soccer" to "football" and should pass all validation

3. **Given** I run the test suite, **when** the reverse migration tests execute, **then** all tests in `test_story_21_2_migration.py::TestStory21_2ReverseMigration` should pass

4. **Given** the migration is reversed, **when** I run the forward migration again, **then** it should execute successfully and restore the "soccer" terminology

**Technical Context**:
- The issue occurs in `apps/assessments/migrations/0003_migrate_football_to_soccer.py`
- Test failure: `tests/test_story_21_2_migration.py::TestStory21_2ReverseMigration::test_reverse_migration_function`
- Error: `django.db.utils.IntegrityError: new row for relation "assessments" violates check constraint "assessments_sport_valid_choice"`
- The reverse migration must temporarily restore "football" as a valid choice before updating data

---

## Execution Order

**Sequential Execution**:
1. Story 355.1 - Fix Reverse Migration Constraint Violation (backend-developer)

---

## Validation

**Definition of Done**:
- All CI/CD pipeline tests pass
- Reverse migration executes without errors
- Migration can be applied and reversed repeatedly without data corruption
- No database constraint violations occur during forward or reverse migration

**Test Commands**:
```bash
# Backend tests
cd backend
pytest tests/test_story_21_2_migration.py::TestStory21_2ReverseMigration -v

# Full CI/CD validation
# Run the complete Build and Test workflow to verify all tests pass
```
