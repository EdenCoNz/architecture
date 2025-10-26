# User Stories - Fix Frontend Configuration API URL Port Issue

**Feature**: Phase 1: Consolidate Docker Compose Files
**Issue**: #230 - CI/CD Pipeline Failed: Build and Test - Run #23
**Branch**: feature/15-consolidate-docker-compose-files
**Created**: 2025-10-27

## Overview

The frontend configuration endpoint is returning an incomplete API URL (`http://localhost` without port number) instead of the expected `http://localhost:8000`. This mismatch occurs because:

1. The code defaults to `http://localhost` when no environment variable is set
2. The test expects `http://localhost:8000` as the default value
3. The Docker environment configuration sets `FRONTEND_API_URL=http://localhost`

This could cause frontend applications to fail when connecting to the backend API, as requests to `http://localhost` default to port 80 instead of the actual backend port 8000.

## Business Context

When users deploy the application in different environments, the frontend needs to know where to find the backend API. The configuration endpoint provides this information dynamically, allowing the same frontend image to work across environments. If the API URL is incomplete or incorrect, the frontend cannot communicate with the backend, breaking all functionality.

## User Stories

### Story 15.1: Fix Frontend Configuration Default API URL

**As a** frontend application
**I want** the configuration endpoint to return the complete backend API URL including port number
**So that** I can successfully connect to the backend API in all environments

**Agent**: backend-developer

**Acceptance Criteria**:
- Given no FRONTEND_API_URL environment variable is set, when I request the frontend configuration, then the API URL should be `http://localhost:8000`
- Given FRONTEND_API_URL environment variable is set to `http://localhost`, when I request the frontend configuration, then the API URL should include the port number `:8000`
- Given FRONTEND_API_URL environment variable is set to a complete URL with port (e.g., `http://localhost:8000`), when I request the frontend configuration, then the API URL should be returned exactly as configured
- Given FRONTEND_API_URL environment variable is set to a production URL (e.g., `https://api.example.com`), when I request the frontend configuration, then the API URL should be returned exactly as configured without modification

**Technical Context**:
The test failure occurs at:
- File: `backend/tests/integration/test_frontend_config.py`
- Line 101: `assert data["api"]["url"] == "http://localhost:8000"`
- Current behavior: Returns `http://localhost` (missing port)
- Expected behavior: Returns `http://localhost:8000` (with port)

The issue is in `backend/apps/api/config_views.py` line 92:
```python
frontend_api_url = os.getenv("FRONTEND_API_URL") or "http://localhost"
```

The default should be `http://localhost:8000` to match the backend's default port.

**Dependencies**: None

**Estimated Effort**: 1-2 hours

---

## Execution Plan

### Phase 1: Sequential
1. Story 15.1: Fix Frontend Configuration Default API URL

---

## Notes

### Root Cause Analysis
The Docker Compose consolidation (Feature #15) likely changed environment variable handling or defaults, exposing this inconsistency between:
- The code's default value (`http://localhost`)
- The test's expected value (`http://localhost:8000`)
- Production/Docker configuration needs (which vary by deployment)

### Solution Approach
Update the default API URL in the configuration endpoint to include the port number, ensuring consistency between development, testing, and Docker environments. The endpoint should:
1. Return `http://localhost:8000` when no environment variable is set (local development default)
2. Respect environment variables when they are set (Docker/production deployments)
3. Handle URLs with and without ports appropriately

### Validation
After implementation:
- All 617 tests should pass
- Frontend configuration endpoint should return complete URLs
- Docker environments should continue to work with their configured URLs
- Local development should work without environment variables
