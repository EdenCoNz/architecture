# User Stories for Issue #305: CI/CD Pipeline Failed - ESLint Violations

## Issue Context
- **Issue Number**: #305
- **Feature ID**: 19
- **Branch**: feature/19-equipment-assessment-single-selection-with-item-input
- **Type**: Bug Fix - CI/CD Pipeline Failure
- **Root Cause**: ESLint formatting violations (45 errors, 11 warnings)

## Error Summary
The CI/CD pipeline failed during the "Build and Test" stage due to ESLint violations:
- 45 prettier/prettier formatting errors (extra spaces/indentation)
- 11 no-console warnings (console.log usage in test files)
- All 437 tests pass functionally - failure is purely code style/formatting

## User Stories

### Story 1: Fix Prettier Formatting Violations in Frontend Code
**As a** developer
**I want** all frontend code to conform to Prettier formatting rules
**So that** the CI/CD pipeline passes and code maintains consistent style

**Acceptance Criteria:**
1. Run `npm run lint:fix` or `npx prettier --write` in frontend directory to auto-fix formatting
2. All 45 prettier/prettier errors in the following files are resolved:
   - `src/components/forms/AssessmentForm.test.tsx` (37 errors, lines 654-900)
   - Other affected files with formatting issues
3. ESLint reports 0 prettier/prettier errors when running `npm run lint`
4. All existing tests continue to pass (437 tests)
5. Changes are committed with proper formatting

**Technical Notes:**
- Errors are primarily "Delete `··`" indicating extra spaces/indentation
- Most errors are auto-fixable with `--fix` option
- Focus on `AssessmentForm.test.tsx` which has the majority of errors

**Assigned Agent:** frontend-developer

---

### Story 2: Remove Console.log Statements from Production Code
**As a** developer
**I want** to remove or replace inappropriate console.log statements
**So that** code quality standards are maintained and warnings are eliminated

**Acceptance Criteria:**
1. Review and fix console usage violations in:
   - `src/utils/version.test.ts` (5 console.log warnings)
   - `src/utils/version.ts` (5 console.log warnings)
2. Replace console.log with console.warn or console.error where appropriate
3. Remove console statements from test files or add proper eslint-disable comments if intentional
4. Remove unused eslint-disable directive at line 87 in `src/utils/version.ts`
5. ESLint reports 0 no-console warnings when running `npm run lint`
6. All tests continue to pass

**Technical Notes:**
- Only console.warn and console.error are allowed per project rules
- Test files may need console statements for debugging - consider using proper test logging or removing
- 1 unused eslint-disable directive needs cleanup

**Assigned Agent:** frontend-developer

---

## Execution Order
1. **Story 1** - Fix Prettier formatting violations (CRITICAL - blocks CI)
2. **Story 2** - Remove console.log statements (improves code quality)

## Dependencies
- None between stories - can be executed in parallel if needed
- Both stories target frontend codebase

## Definition of Done
- All ESLint errors (45) are resolved
- All ESLint warnings (11) are resolved or properly suppressed with justification
- `npm run lint` passes with 0 errors and 0 warnings
- `npm test` passes with all 437 tests passing
- CI/CD pipeline "Build and Test" stage completes successfully
- Changes are committed and pushed to feature branch
