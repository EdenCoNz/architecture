# Feature 20 - Issue #342: Login Component Test Router Context Failures

**Issue**: CI/CD Pipeline Failed: Build and Test - Run #132
**Branch**: feature/20-basic-login
**Type**: Bug Fix
**Created**: 2025-11-02

## Issue Summary

All 22 tests in the Login component test suite are failing because the component uses React Router's `useNavigate()` hook, which requires the component to be rendered within a Router context. The tests render the Login component in isolation without providing the required Router provider, causing a runtime error: "useNavigate() may be used only in the context of a Router component."

## Root Cause Analysis

The Login component test file (`src/pages/Login/Login.test.tsx`) has two conflicting approaches:
1. It mocks `react-router-dom` to provide a mock `useNavigate` function
2. It wraps components in `<BrowserRouter>` using the `renderWithRouter` helper

However, the mock is applied at the module level before the component is rendered, which prevents the actual Router context from being established. When the Login component tries to call `useNavigate()`, it executes before the Router wrapper can provide the context.

## Impact

- All Login functionality tests are blocked (22 test failures)
- CI/CD pipeline is failing
- Cannot verify that the login feature works correctly
- Prevents confidence in Feature 20 deployment

---

## User Stories

### Story 342.1: Fix Router Context in Login Component Tests

**As a** developer
**I want** Login component tests to properly provide Router context
**So that** all test assertions can execute and verify login functionality

**Agent**: frontend-developer

**Acceptance Criteria**:

1. **Given** the Login component test suite is executed, **when** any test renders the Login component, **then** the component should have access to Router context and not throw "useNavigate() may be used only in the context of a Router component" errors

2. **Given** the test file uses mocked navigation, **when** a test triggers navigation (e.g., successful login), **then** the mock navigate function should be called with the expected route

3. **Given** all 22 tests are executed, **when** the test suite completes, **then** all tests should pass without Router context errors

4. **Given** the tests verify navigation behavior, **when** reviewing the test implementation, **then** the approach should be clear and maintainable (either using real Router with mocked navigate, or using a different testing approach that doesn't require Router)

**Technical Context**:
- Error occurs in: `frontend/src/pages/Login/Login.test.tsx`
- Affected tests: All 22 tests (Story 20.3 tests, form rendering, form validation, email field validation)
- Root cause: Mock setup conflicts with Router context requirements
- Current approach: Mocks `useNavigate` but component still requires Router context

**Notes**:
- The fix should maintain the existing test coverage
- Tests should continue to verify navigation behavior
- Consider using MemoryRouter instead of BrowserRouter for tests
- Ensure mock setup happens after Router context is established
- All 22 failing tests should pass after the fix

---

## Execution Plan

### Phase 1: Fix Test Setup (Sequential)
1. **Story 342.1**: Fix Router context in Login component tests

---

## Test Validation

After implementing Story 342.1, verify:
- [ ] All 22 Login component tests pass
- [ ] CI/CD pipeline "Build and Test" job succeeds
- [ ] Navigation mocking still works as expected
- [ ] Test output is clear and maintainable

---

## Definition of Done

- All Login component tests pass locally and in CI/CD
- No Router context errors in test output
- CI/CD pipeline "Build and Test Complete Stack" job succeeds
- Code changes are reviewed and follow testing best practices
