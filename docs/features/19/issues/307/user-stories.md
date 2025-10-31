# Fix Stories for Issue #307: CI/CD Pipeline Failed - Test Timeout

**Issue**: #307 - CI/CD Pipeline Failed: Build and Test - Run #100
**Feature**: 19 - Equipment Assessment Single Selection with Item Input
**Branch**: feature/19-equipment-assessment-single-selection-with-item-input

## Problem Summary

A frontend test is timing out when verifying equipment selection deselection behavior. The test "should deselect previous equipment level when selecting a new one (Story 19.4 AC 1)" in `AssessmentForm.test.tsx:285` exceeds the 15-second timeout, preventing CI/CD pipeline completion.

## Fix Stories

### Story 307.1: Fix Equipment Selection Test Timeout

**As a** developer
**I want** the equipment selection deselection test to complete successfully
**So that** the CI/CD pipeline can pass and deploy changes

**Agent**: frontend-developer

**Description**:
The test at `frontend/src/components/forms/AssessmentForm.test.tsx:285` times out after 15 seconds when testing the scenario where a user selects "No Equipment", submits the form, then switches to "Basic Equipment" and submits again. The test expects the second submission to only include basic equipment data, but something is preventing the test from completing.

**Root Cause Investigation Needed**:
1. Check if the component has infinite render loops when switching equipment selections
2. Verify event handlers are properly debounced/throttled
3. Check if state updates are completing correctly after equipment selection changes
4. Ensure the form submission mock is being called correctly on the second submit
5. Verify waitFor conditions are achievable

**Acceptance Criteria**:
1. The test "should deselect previous equipment level when selecting a new one (Story 19.4 AC 1)" completes within the 15-second timeout
2. The test verifies that switching from "No Equipment" to "Basic Equipment" correctly updates the form data
3. No infinite render loops or stuck event handlers exist in the equipment selection logic
4. All other equipment selection tests continue to pass
5. CI/CD pipeline completes successfully

**Technical Context**:
- Test file: `frontend/src/components/forms/AssessmentForm.test.tsx:285-336`
- Component: `frontend/src/components/forms/AssessmentForm.tsx`
- Related story: Story 19.4 (Single Selection for Equipment Levels)
- Similar passing tests suggest the issue is specific to the toggle/deselection behavior

**Test Scenario**:
```typescript
1. Fill required form fields (sport, age, experience, frequency, injuries)
2. Select "No Equipment" button
3. Submit form → verify equipment: ['no-equipment']
4. Select "Basic Equipment" button
5. Select at least one equipment item (e.g., "Dumbbell")
6. Submit form → verify equipment: ['basic-equipment'] and equipmentItems includes 'dumbbell'
// This is where the test times out at step 6
```

## Execution Order

1. Story 307.1 - MUST be completed first (frontend-developer)

## Notes

- This is a fix story for a test timeout issue
- The component logic itself may be working correctly in the app, but the test is unable to verify the behavior
- Other similar tests pass, so the issue is likely specific to the interaction pattern in this test
- Consider if the test needs adjustment or if there's a legitimate bug in the component
