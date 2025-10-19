# Error Code Mapping for Pre-Flight Validation

## Purpose

This document maps existing pre-flight validation error messages to the standardized error codes from the command error handling system. Use this as a quick reference when displaying validation errors.

## Error Code Mapping Table

### Git Repository Validation

| Existing Error Message | Error Code | Category | Severity |
|------------------------|------------|----------|----------|
| "Not a git repository" | ENV-001 | Environment | Critical |
| "Detached HEAD state" | ENV-003 | Environment | Blocking |
| "No changes to commit" | GIT-001 | Git Operations | Informational |
| "Uncommitted changes blocking operation" | GIT-007 | Git Operations | Warning |
| "Branch is behind remote" | GIT-006 | Git Operations | Warning |
| "Push rejected by remote" | GIT-005 | Git Operations | Blocking |

### File System Validation

| Existing Error Message | Error Code | Category | Severity |
|------------------------|------------|----------|----------|
| "Feature log not found" | FS-001 | File System | Blocking |
| "User stories file not found" | FS-001 | File System | Blocking |
| "Implementation log not found" | FS-001 | File System | Blocking |
| "Agents directory not found" | FS-002 | File System | Blocking |
| "Feature log contains invalid JSON" | FS-005 | File System | Blocking |
| "Implementation log contains invalid JSON" | FS-005 | File System | Blocking |
| "Cannot write metrics cache" | FS-004 | File System | Warning |

### GitHub/External Service Validation

| Existing Error Message | Error Code | Category | Severity |
|------------------------|------------|----------|----------|
| "GitHub CLI not installed" | ENV-004 | Environment | Critical |
| "GitHub CLI not authenticated" | ENV-005 | Environment | Blocking |
| "Cannot connect to GitHub repository" | ENV-006 | Environment | Blocking |
| "GitHub API rate limit exceeded" | EXT-001 | External Services | Blocking |
| "No open GitHub issues found" | EXT-003 | External Services | Informational |
| "GitHub network error" | EXT-004 | External Services | Blocking |

### Data Validation

| Existing Error Message | Error Code | Category | Severity |
|------------------------|------------|----------|----------|
| "Feature not found in feature log" | DEP-002 | Dependencies | Blocking |
| "User stories not created" | DEP-003 | Dependencies | Blocking |
| "Missing required field" | DATA-001 | Data Validation | Blocking |
| "Invalid JSON syntax" | FS-005 | File System | Blocking |
| "Invalid bug ID format" | INPUT-002 | User Input | Blocking |
| "Commit message is required" | INPUT-001 | User Input | Blocking |

### State Validation

| Existing Error Message | Error Code | Category | Severity |
|------------------------|------------|----------|----------|
| "Feature already fully implemented" | STATE-002 | State Consistency | Warning |
| "Feature already summarized" | STATE-003 | State Consistency | Warning |
| "Invalid state transition" | STATE-004 | State Consistency | Blocking |
| "Feature already exists" | STATE-001 | State Consistency | Warning |

### Dependency Validation

| Existing Error Message | Error Code | Category | Severity |
|------------------------|------------|----------|----------|
| "No agents available" | DEP-006 | Dependencies | Warning |
| "Missing agent definitions" | DEP-006 | Dependencies | Warning |
| "No unsummarised features" | DEP-004 | Dependencies | Informational |

## How to Use This Mapping

When displaying validation errors in commands:

1. **Identify the error scenario** from pre-flight validation
2. **Look up the error code** in this mapping table
3. **Display the error** using the standardized format from command-error-handling.md
4. **Include the error code** in the error message header

### Example: Converting Existing Error

**Before (without error code)**:
```
Error: Feature log not found

File: docs/features/feature-log.json
Purpose: Tracks all features
Command: /implement

Remediation:
1. Run /feature command
```

**After (with error code)**:
```
ERROR: Feature log not found

Code: FS-001
Category: File System Errors
Command: /implement

Details:
Required file does not exist at expected location.

Context:
- Attempted operation: Read feature log
- Target: docs/features/feature-log.json
- Purpose: Tracks all features and implementation status

Impact:
Cannot proceed with implementation without feature metadata.

Recovery Steps:
1. Run /feature command to initialize feature log:
   /feature "Your first feature"

2. Verify file was created:
   ls -la docs/features/feature-log.json

For more information, see: .claude/helpers/command-error-handling.md (FS-001)
```

## Command-Specific Error Code Usage

### /commit Command

Common error codes:
- ENV-001: Git repository not found
- ENV-003: Detached HEAD state
- GIT-001: No changes to commit
- INPUT-001: Missing commit message
- GIT-005: Push rejected
- GIT-007: Uncommitted changes (warning)

### /feature Command

Common error codes:
- ENV-001: Git repository not found
- FS-002: Agents directory not found
- FS-005: Invalid JSON in feature-log
- DEP-006: No agents available (warning)
- GIT-007: Uncommitted changes (warning)
- STATE-001: Feature already exists (warning)

### /implement Command

Common error codes:
- ENV-001: Git repository not found
- FS-001: User stories not found
- FS-005: Invalid JSON in feature-log or implementation-log
- DEP-002: Feature not found
- DEP-003: User stories not created
- INPUT-002: Invalid bug ID format
- STATE-004: Invalid state transition
- STATE-002: Feature already implemented (warning)

### /fix Command

Common error codes:
- ENV-001: Git repository not found
- ENV-004: GitHub CLI not installed
- ENV-005: GitHub CLI not authenticated
- ENV-006: GitHub repository not connected
- FS-001: Feature log not found
- FS-005: Invalid JSON in feature-log
- EXT-001: GitHub API rate limit
- EXT-003: No open issues (informational)
- EXT-004: GitHub network error

### /summarise Command

Common error codes:
- ENV-001: Git repository not found
- FS-001: Feature log not found
- FS-005: Invalid JSON in feature-log or implementation-logs
- STATE-003: Feature already summarized (informational)
- STATE-004: Invalid state transition
- DATA-005: Feature references don't exist
- DEP-004: No unsummarised features (informational)

### /dashboard Command

Common error codes:
- ENV-001: Git repository not found
- FS-001: Feature log not found
- FS-005: Invalid JSON in feature-log
- INPUT-002: Invalid state filter value
- DATA-001: Missing state fields (use defaults)

### /metrics Command

Common error codes:
- ENV-001: Git repository not found
- FS-001: Feature log or implementation logs not found
- FS-005: Invalid JSON in logs
- DATA-001: Missing required fields (skip story)
- DATA-004: Invalid timestamp format (skip story)
- FS-004: Cannot write metrics cache (warning)
- INPUT-002: Invalid agent name
- INPUT-006: Unknown flag

## Quick Reference: Error Code Prefixes

- **ENV-XXX**: Environment and setup issues
- **FS-XXX**: File system operations
- **GIT-XXX**: Git operations
- **DATA-XXX**: Data validation
- **DEP-XXX**: Dependencies
- **EXT-XXX**: External services
- **INPUT-XXX**: User input validation
- **STATE-XXX**: State consistency

## Integration Notes

1. **Error codes are required** in all new error messages
2. **Use standard format** from command-error-handling.md
3. **Map existing messages** using this document
4. **Include recovery steps** specific to the error
5. **Reference documentation** with error code

## Version History

- v1.0.0 (2025-10-19): Initial error code mapping
  - Mapped all existing validation errors to error codes
  - Documented command-specific error usage
  - Provided conversion examples
