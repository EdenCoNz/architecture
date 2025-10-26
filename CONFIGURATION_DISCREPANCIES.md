# Configuration Discrepancies Analysis

**Date:** 2025-10-26
**Status:** Critical issues found requiring immediate attention

---

## Executive Summary

A comprehensive analysis of all configuration files across the application has identified **7 critical discrepancies** and **3 minor inconsistencies** that could lead to runtime errors, failed deployments, or unexpected behavior.

**Priority Issues:**
1. ❌ **CRITICAL:** Wrong Django settings module path in test environment (will cause ImportError)
2. ⚠️  **HIGH:** Inconsistent frontend API URLs across environments
3. ⚠️  **MEDIUM:** CORS configuration mismatch in test environment
4. 🔧 **LOW:** Inconsistent health check implementations

---

## Critical Issues

### 1. Django Settings Module Path - Test Environment ❌ CRITICAL

**Impact:** Test environment will fail to start with `ImportError: No module named 'backend.settings'`

**Affected Files:**
- `compose.test.yml:89` - `DJANGO_SETTINGS_MODULE: backend.settings.test`
- `.env.test:59` - `DJANGO_SETTINGS_MODULE=backend.settings.test`
- `testing/pytest.ini:5` - `DJANGO_SETTINGS_MODULE = backend.settings.test`
- `testing/integration/conftest.py:15` - `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.test")`
- `testing/integration/test_assessment_submission.py:23` - `backend.settings.test`
- `testing/integration/test_profile_creation.py:24` - `backend.settings.test`
- `.github/workflows/performance-tests.yml:80` - `DJANGO_SETTINGS_MODULE=backend.settings.test`

**Correct Value:**
```bash
DJANGO_SETTINGS_MODULE=config.settings.testing
```

**Evidence:**
- Actual settings file location: `backend/config/settings/testing.py`
- Backend pytest.ini (line 2): `DJANGO_SETTINGS_MODULE = config.settings.testing` ✓
- Backend test scripts use: `config.settings.testing` ✓
- All other environments use: `config.settings.{environment}` ✓

**Required Changes:**
1. Update `compose.test.yml` line 89
2. Update `.env.test` line 59
3. Update `testing/pytest.ini` line 5
4. Update `testing/integration/conftest.py` line 15
5. Update all test files in `testing/integration/test_*.py`
6. Update `.github/workflows/performance-tests.yml` line 80

---

### 2. Frontend API URL Inconsistencies ⚠️ HIGH

**Impact:** Frontend may attempt to connect to wrong backend URL, causing CORS errors or connection failures

**Issue:** After implementing unified reverse proxy architecture (Feature #12), frontend should access backend through proxy at `http://localhost`, not directly at `http://localhost:8000`. However, multiple files still use the old direct URL.

**Current State:**

| File | Line | Value | Correct? |
|------|------|-------|----------|
| `frontend/.env.docker` | 18 | `http://localhost` | ✓ Correct (through proxy) |
| `frontend/.env.test` | 24 | `http://localhost:8000` | ❌ Direct backend |
| `docker-compose.yml` | 315 | `http://localhost:8000` | ❌ Direct backend |
| `compose.test.yml` | 151 | `http://localhost/api` | ⚠️  Has `/api` prefix |
| `compose.override.yml` | 101 | `http://localhost` | ✓ Correct (through proxy) |

**Analysis:**

With the reverse proxy architecture:
- Browser → `http://localhost/` → nginx → frontend
- Browser → `http://localhost/api/` → nginx → backend
- Frontend JavaScript makes requests to `/api/` (same origin, no CORS)

**Recommended Values:**

**Development (with proxy):**
```bash
VITE_API_URL=http://localhost  # Proxy handles routing to /api/
```

**Development (direct access for debugging):**
```bash
VITE_API_URL=http://localhost:8000  # Direct backend, CORS must allow
```

**Test Environment:**
```bash
VITE_API_URL=http://localhost/api  # Through test proxy
```

**Required Changes:**
1. Decide on canonical approach: always through proxy OR allow direct access in dev
2. Update `docker-compose.yml` line 315 to match chosen approach
3. Update `frontend/.env.test` line 24 to `http://localhost/api`
4. Document the decision in configuration guide

**Current Behavior:**
- `docker-compose.yml` sets `VITE_API_URL=http://localhost:8000` (direct)
- But reverse proxy expects traffic through `http://localhost/api/`
- This creates confusion about which URL to use

---

### 3. Test Environment CORS Configuration Mismatch ⚠️ MEDIUM

**Impact:** Frontend-to-backend requests in test environment may fail with CORS errors

**Issue:** Inconsistent CORS allowed origins between environment file and compose file

**.env.test (line 65) - More Complete:**
```bash
CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:80,http://localhost:5173,http://localhost:5174,http://frontend:5173
```

**compose.test.yml (line 107) - Missing Origins:**
```bash
CORS_ALLOWED_ORIGINS: "http://localhost,http://localhost:5174"
```

**Missing in compose.test.yml:**
- `http://localhost:80` - Explicit port 80
- `http://localhost:5173` - Direct frontend access
- `http://frontend:5173` - Internal container-to-container communication

**Impact:**
- If test runner container tries to access backend via `http://frontend:5173`, it will be blocked
- Direct access to frontend dev server may be blocked

**Required Changes:**
1. Update `compose.test.yml` line 107 to match `.env.test` line 65
2. Or remove from compose.test.yml and let `.env.test` take precedence

---

## Medium Priority Issues

### 4. Frontend Health Check Invalid Endpoint 🔧 MEDIUM

**Impact:** Health check will always fail in test environment

**Issue:** Frontend health check tries to access `/health` endpoint which doesn't exist

**compose.test.yml (line 168):**
```yaml
test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5173/health"]
```

**Problem:** Frontend is a static React SPA served by Vite dev server. It doesn't have a `/health` endpoint.

**Correct Implementation:**
```yaml
test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1:5173"]
```

**Evidence:**
- Main `docker-compose.yml` line 349 correctly uses root path: `http://127.0.0.1:5173`
- Only test environment has this error

---

### 5. Health Check URL Inconsistency (localhost vs 127.0.0.1) 🔧 LOW

**Impact:** Potential IPv6 resolution issues, slower health checks

**Issue:** Main compose uses `127.0.0.1` (IPv4 explicit), test compose uses `localhost` (could resolve to IPv6 ::1)

**Main docker-compose.yml - Correct:**
```yaml
# Backend (line 265)
test: ["CMD", "curl", "-f", "http://127.0.0.1:8000/api/v1/health/"]

# Frontend (line 349)
test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1:5173"]

# Proxy (line 427)
test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1/health"]
```

**compose.test.yml - Inconsistent:**
```yaml
# Backend (line 131) - uses localhost
test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]

# Frontend (line 168) - uses localhost
test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5173/health"]

# Proxy (line 193) - uses localhost
test: ["CMD", "curl", "-f", "http://localhost/health"]
```

**Reason for 127.0.0.1:**
- Forces IPv4 resolution
- Avoids IPv6 lookup delays
- Django and Vite bind to 0.0.0.0 (IPv4)

**Required Changes:**
- Update all health checks in `compose.test.yml` to use `127.0.0.1` instead of `localhost`

---

### 6. Proxy Health Check Tool Inconsistency 🔧 LOW

**Impact:** Potential missing dependencies in test container

**Issue:** Different tools used for same purpose

**Main docker-compose.yml (line 427):**
```yaml
test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1/health"]
```

**compose.test.yml (line 193):**
```yaml
test: ["CMD", "curl", "-f", "http://localhost/health"]
```

**Recommendation:** Use `wget` consistently (nginx:alpine has wget by default)

---

## Minor Issues

### 7. Documentation Port Discrepancy 📝 LOW

**Impact:** Confusion for developers

**Issue:** Generated documentation (`docs/configuration.md`) states test proxy runs on port 5175, but actual configuration uses port 80.

**Actual (compose.test.yml line 185):**
```yaml
ports:
  - "80:80"
```

**Documentation says:**
```
Proxy: 5175
```

**Required Changes:**
- Update `docs/configuration.md` to reflect actual port (80)
- Consider if test environment should use different port to avoid conflicts

---

## Summary of Required Changes

### High Priority (Fix Immediately)

1. **Fix Django Settings Module Path** (7 files)
   - Change `backend.settings.test` → `config.settings.testing`
   - Files: compose.test.yml, .env.test, testing/pytest.ini, testing/integration/conftest.py, test files, GitHub workflow

2. **Standardize Frontend API URLs** (3 files)
   - Decide: Always through proxy OR allow direct access
   - Update docker-compose.yml, frontend/.env.test, compose.test.yml
   - Document decision

3. **Fix Test CORS Configuration** (1 file)
   - Update compose.test.yml line 107 with complete origins list

### Medium Priority (Fix Before Next Release)

4. **Fix Frontend Health Check** (1 file)
   - Remove `/health` from path in compose.test.yml

5. **Standardize Health Check URLs** (1 file)
   - Use `127.0.0.1` instead of `localhost` in compose.test.yml

6. **Standardize Health Check Tools** (1 file)
   - Use `wget` instead of `curl` for proxy in compose.test.yml

### Low Priority (Technical Debt)

7. **Update Documentation** (1 file)
   - Fix port number in docs/configuration.md

---

## Validation Checklist

After making changes, validate:

- [ ] Test environment starts successfully: `docker compose -f compose.test.yml up`
- [ ] Backend health check passes: `curl http://localhost/api/v1/health/`
- [ ] Frontend loads without errors: `curl http://localhost/`
- [ ] CORS requests work from frontend to backend
- [ ] All container health checks turn healthy
- [ ] Integration tests run successfully
- [ ] E2E tests connect to correct URLs

---

## Root Cause Analysis

**Why did these discrepancies occur?**

1. **Feature #13 (Testing)** was implemented after **Feature #12 (Unified Proxy)**
   - Test configuration copied old patterns before proxy implementation
   - Not updated to match new architecture

2. **Multiple pytest.ini files** (backend/pytest.ini vs testing/pytest.ini)
   - Different teams/contexts using different paths
   - No single source of truth

3. **Gradual migration to proxy architecture**
   - Some files updated, others missed
   - No comprehensive audit performed

4. **Copy-paste propagation**
   - Wrong value in one file copied to others
   - Integration test files all copied same wrong pattern

---

## Prevention Recommendations

1. **Configuration Validation Script**
   - Add pre-commit hook to validate DJANGO_SETTINGS_MODULE format
   - Validate VITE_API_URL matches deployment architecture
   - Check CORS origins include necessary URLs

2. **Single Source of Truth**
   - Consider consolidating environment files
   - Use template generation for repeated values

3. **Architecture Decision Records (ADRs)**
   - Document decision: "Frontend accesses backend through proxy"
   - Reference in all configuration files

4. **Automated Testing**
   - Add test that validates settings module imports
   - Add test that validates API URL connectivity
   - Add test that validates CORS configuration

5. **Documentation**
   - Update configuration.md with architectural decisions
   - Add troubleshooting section for common misconfigurations

---

## Next Steps

1. Create GitHub issue for each high-priority discrepancy
2. Assign to appropriate team member
3. Implement fixes
4. Add validation tests
5. Update documentation
6. Add pre-commit hooks

**Estimated Effort:** 2-4 hours for all fixes
**Risk Level:** High (blocking test environment from functioning correctly)
