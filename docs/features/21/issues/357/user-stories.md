# Issue #357: CI/CD Pipeline Failed - Database Constraint Not Enforcing Sports Terminology

**Feature:** 21 - Sports Terminology and Database Storage
**Issue Number:** 357
**Branch:** feature/21-sports-terminology-and-storage
**Workflow Run:** #146

## Issue Summary

A database test is failing because the database constraint that should reject old "football" terminology is not working properly. The test expects an IntegrityError when attempting to insert "football" values directly into the database, but the database is allowing these values through without raising an error.

## Root Cause

Migration 0004 (`0004_add_sport_check_constraint.py`) uses `migrations.AddConstraint()` to add the sport validation constraint. However, migration 0003's reverse function manually creates a constraint with the same name (`assessments_sport_valid_choice`) that allows "football", "soccer", and "cricket". When migration 0004 runs, it cannot add a constraint with a name that already exists, resulting in the old constraint remaining in place and continuing to allow "football" values.

The migration needs to be updated to first remove any existing constraint before adding the new one to ensure the correct constraint is always applied.

## User Stories

### Story 357.1: Replace Database Constraint Instead of Adding

**Agent:** backend-developer

**Description:**
As a system, I need to enforce that only current sport terminology ("soccer", "cricket") is stored in the database, so that data integrity is maintained and old terminology ("football") is properly rejected.

**Acceptance Criteria:**

1. Given migration 0004 is applied to a database, when the migration runs, then any existing `assessments_sport_valid_choice` constraint should be removed before adding the new constraint
2. Given migration 0004 has completed, when I attempt to insert a record with sport="football" directly via SQL, then the database should raise an IntegrityError
3. Given migration 0004 has completed, when I attempt to insert a record with sport="soccer" directly via SQL, then the insert should succeed
4. Given the test `test_old_football_value_rejected_by_database` is run, when the test attempts to insert "football" via cursor.execute(), then pytest.raises(IntegrityError) should successfully catch the error

**Dependencies:**
- None

**Notes:**
- The migration should use `migrations.RemoveConstraint()` followed by `migrations.AddConstraint()` instead of just `migrations.AddConstraint()`
- This ensures that any existing constraint with the same name (created by migration 0003's reverse function) is properly replaced
- The change is backward compatible - if the constraint doesn't exist, RemoveConstraint will handle it gracefully

---

## Execution Plan

### Phase 1: Sequential Execution
1. Story 357.1 (backend-developer)

---

## Validation

After implementation, verify:
- [ ] Migration 0004 successfully removes and re-adds the constraint
- [ ] Test `test_old_football_value_rejected_by_database` passes
- [ ] Direct database insertion of "football" values is rejected
- [ ] Direct database insertion of "soccer" values succeeds
- [ ] All other tests in `test_story_21_5_data_persistence.py` continue to pass
- [ ] CI/CD pipeline passes completely
