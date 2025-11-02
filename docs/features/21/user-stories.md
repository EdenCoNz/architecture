# Feature #21: Sports Terminology and Database Storage

## Overview
Update sport terminology to use "soccer" as the internal identifier while displaying "Football" to users, and verify that sport selections are properly persisted to the database with correct data integrity.

**Feature Branch**: feature/21-sports-terminology-and-storage

## User Stories

### Story 21.1: Update Sport Internal Identifier to Soccer
**Agent**: backend-developer
**Priority**: High
**Story Points**: 2

**Description**:
As a system administrator, I want the sport previously identified as "football" to use "soccer" as its internal database identifier, so that the system uses internationally recognized terminology while maintaining user-facing display preferences.

**Acceptance Criteria**:
- Given the system has existing assessment data with sport="football", when I view the database directly, then the sport field should store "soccer" as the value
- Given a user selects "Football" in the assessment form, when the data is saved, then the database should store "soccer" as the sport value
- Given assessment data exists with sport="soccer", when the system processes this data, then all functionality should work correctly
- Given the API returns sport data, when I inspect the response, then it should return "soccer" as the internal value

---

### Story 21.2: Migrate Existing Football Data to Soccer
**Agent**: backend-developer
**Priority**: High
**Story Points**: 2

**Description**:
As a system administrator, I need all existing assessment records with sport="football" to be migrated to sport="soccer", so that the database maintains consistent terminology across all records.

**Acceptance Criteria**:
- Given there are existing assessments with sport="football", when the migration runs, then all records should be updated to sport="soccer"
- Given the migration completes, when I query for assessments with sport="football", then no records should be returned
- Given the migration completes, when I query for assessments with sport="soccer", then I should see all previously "football" records
- Given the migration runs multiple times, when I check the database, then it should be idempotent and not cause errors or data corruption

---

### Story 21.3: Maintain Football Display Label for Users
**Agent**: backend-developer
**Priority**: High
**Story Points**: 1

**Description**:
As a user, I want to continue seeing "Football" as the sport option in the user interface, so that the terminology remains familiar and user-friendly regardless of internal system changes.

**Acceptance Criteria**:
- Given I view the sport selection options, when I see the available sports, then "Football" should be displayed as a choice
- Given the system stores "soccer" internally, when the API returns sport choices, then it should include a display label "Football" for the "soccer" value
- Given I view my saved assessment, when the sport is displayed, then it should show "Football" not "soccer"
- Given the API documentation is generated, when I view sport field options, then it should clearly indicate the internal value is "soccer" with display label "Football"

---

### Story 21.4: Update Frontend to Handle Soccer Value
**Agent**: frontend-developer
**Priority**: High
**Story Points**: 2

**Description**:
As a frontend developer, I need the application to correctly send "soccer" to the backend when users select "Football", so that data is stored with the correct internal identifier.

**Acceptance Criteria**:
- Given a user selects "Football" in the assessment form, when the form is submitted, then the request should send sport: "soccer" to the backend
- Given the user's saved assessment has sport="soccer", when the form loads existing data, then the "Football" option should be pre-selected
- Given the API returns sport="soccer", when displaying the user's sport selection, then it should render as "Football" in the UI
- Given form validation occurs, when checking sport values, then both "soccer" and "Football" display should be handled correctly

---

### Story 21.5: Verify Sport Data Persistence
**Agent**: backend-developer
**Priority**: High
**Story Points**: 2

**Description**:
As a quality assurance tester, I need to verify that sport selections are correctly saved to the database and retrieved without data loss, so that users' sport preferences are reliably persisted across sessions.

**Acceptance Criteria**:
- Given a user submits an assessment with a sport selection, when I query the database, then the sport field should contain the expected value
- Given an assessment is saved with sport="soccer", when I retrieve the assessment via API, then the sport field should return "soccer"
- Given multiple users create assessments, when I verify the database, then each user's sport selection should be stored correctly in their assessment record
- Given the database schema, when I inspect the sport field definition, then it should have proper constraints, indexes, and validation rules

---

### Story 21.6: Update API Contract Documentation
**Agent**: backend-developer
**Priority**: Medium
**Story Points**: 1

**Description**:
As an API consumer, I need clear documentation about sport field values and display labels, so that I understand the difference between internal values and user-facing labels.

**Acceptance Criteria**:
- Given I view the API documentation, when I look at the sport field specification, then it should clearly document that "soccer" is the internal value with display label "Football"
- Given I view the assessment endpoints, when I check the request/response examples, then they should show "soccer" as the value being sent and received
- Given I read the API contract, when I look at sport field constraints, then it should list all valid sport values including "soccer"
- Given the API schema is generated, when I inspect sport field enumerations, then "soccer" should be listed as a valid choice

---

### Story 21.7: Update Sport-Related Tests
**Agent**: backend-developer
**Priority**: High
**Story Points**: 2

**Description**:
As a developer, I need all existing tests that reference "football" to be updated to use "soccer", so that the test suite validates the correct behavior with the new terminology.

**Acceptance Criteria**:
- Given there are tests that create assessments with sport="football", when the tests run, then they should be updated to use sport="soccer"
- Given tests verify sport field values, when they check database records, then they should expect "soccer" not "football"
- Given integration tests submit assessment data, when they validate responses, then they should verify "soccer" is stored correctly
- Given all tests pass, when I run the full test suite, then no tests should fail due to the terminology change

---

### Story 21.8: Verify Database Indexes and Constraints
**Agent**: backend-developer
**Priority**: Medium
**Story Points**: 1

**Description**:
As a database administrator, I need to verify that the sport field has appropriate database indexes and constraints, so that queries are performant and data integrity is maintained.

**Acceptance Criteria**:
- Given the sport field is queried frequently, when I check database indexes, then there should be an appropriate index on the sport column
- Given the sport field has valid values, when I inspect database constraints, then it should enforce valid sport choices at the database level
- Given invalid sport values are submitted, when the database processes them, then they should be rejected with clear error messages
- Given the assessment table schema, when I review field definitions, then the sport field should have proper data type, length, and null constraints

---

## Execution Order

### Phase 1: Backend Model and Migration (Sequential)
- **Story 21.1**: Update Sport Internal Identifier to Soccer
- **Story 21.2**: Migrate Existing Football Data to Soccer
- **Story 21.3**: Maintain Football Display Label for Users

### Phase 2: Backend Testing and Documentation (Parallel)
- **Story 21.7**: Update Sport-Related Tests
- **Story 21.6**: Update API Contract Documentation
- **Story 21.8**: Verify Database Indexes and Constraints

### Phase 3: Frontend Updates (Sequential)
- **Story 21.4**: Update Frontend to Handle Soccer Value

### Phase 4: Integration Verification (Sequential)
- **Story 21.5**: Verify Sport Data Persistence

## Notes

### Implementation Considerations
- This feature involves both data migration and code changes
- Backward compatibility must be maintained during migration
- All tests must be updated to reflect the new terminology
- API documentation must clearly distinguish internal values from display labels

### Testing Requirements
- Verify data migration completes successfully
- Test that new assessments save with "soccer" value
- Verify frontend displays "Football" but sends "soccer"
- Ensure existing assessments load correctly after migration
- Validate database constraints and indexes function properly

### Definition of Done
- All assessment records use "soccer" as internal value
- Users continue to see "Football" in the UI
- API documentation reflects the terminology change
- All tests pass with updated terminology
- Database indexes and constraints are verified
- Frontend correctly handles the soccer value
- No data loss or corruption during migration
