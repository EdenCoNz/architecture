# API Documentation System - Verification Checklist

This checklist verifies that the API documentation system meets all acceptance criteria from User Story #8.

## Prerequisites

Before testing, ensure:
- [ ] Backend server is running: `python manage.py runserver`
- [ ] Database is migrated: `python manage.py migrate`
- [ ] All dependencies are installed: `pip install -r requirements/base.txt`

## Acceptance Criteria Verification

### AC1: When I access the documentation, I should see a list of all available endpoints with descriptions

**Test Steps:**
1. Navigate to `http://localhost:8000/api/v1/docs/` (Swagger UI)
2. Verify you can see all endpoints organized by tags:
   - Health (4 endpoints)
   - Authentication (4 endpoints)
   - Users (2 endpoints)
3. Expand any endpoint and verify it has a summary and description

**Expected Result:**
- ✅ Swagger UI loads successfully
- ✅ All endpoints are visible and grouped by category
- ✅ Each endpoint has a descriptive summary
- ✅ Endpoints can be expanded to see more details

**Alternative Test:**
1. Navigate to `http://localhost:8000/api/v1/redoc/`
2. Verify ReDoc interface shows all endpoints with descriptions

---

### AC2: When I view an endpoint, I should see required parameters, optional parameters, and expected responses

**Test Steps:**
1. In Swagger UI, expand the `POST /api/v1/auth/register/` endpoint
2. Verify the "Request body" section shows:
   - Required fields: `email`, `password`, `password_confirm`
   - Optional fields: `first_name`, `last_name`
   - Field types and constraints
3. Verify the "Responses" section shows:
   - 201: Success response with user data
   - 400: Validation errors

**Expected Result:**
- ✅ Request parameters are clearly listed
- ✅ Required vs optional parameters are indicated
- ✅ Field types are specified (string, email, etc.)
- ✅ All response codes are documented
- ✅ Response schemas are provided

**Test with another endpoint:**
1. Expand `POST /api/v1/auth/login/`
2. Verify request shows required `email` and `password` fields
3. Verify response shows success (200) with tokens and error (400) cases

---

### AC3: When I view an endpoint, I should see example requests and responses

**Test Steps:**
1. In Swagger UI, expand `POST /api/v1/auth/register/`
2. Click "Try it out"
3. Verify the request body is pre-filled with example values:
   ```json
   {
     "email": "user@example.com",
     "password": "SecurePass123!",
     "password_confirm": "SecurePass123!",
     "first_name": "John",
     "last_name": "Doe"
   }
   ```
4. Look at the "Responses" section
5. Verify example responses are shown for different status codes

**Expected Result:**
- ✅ Example request body is provided
- ✅ Example values are realistic and helpful
- ✅ Example success response is shown
- ✅ Example error responses are shown
- ✅ Examples match the actual API behavior

**Test with Login:**
1. Expand `POST /api/v1/auth/login/`
2. Verify example shows email and password
3. Verify success response example shows tokens and user data

---

### AC4: When the API changes, I should see documentation update automatically or have clear instructions to update it

**Test Steps:**
1. Download the OpenAPI schema: `http://localhost:8000/api/v1/schema/`
2. Make a note of the endpoints count
3. Restart the server
4. Download the schema again
5. Verify the schema is current

**Expected Result:**
- ✅ Schema is generated dynamically from code
- ✅ No manual schema files to maintain
- ✅ Documentation reflects current code state
- ✅ Schema can be downloaded for external tools

**Automatic Update Test:**
1. Check that views use `@extend_schema` decorators
2. Verify `DEFAULT_SCHEMA_CLASS` is set to `drf_spectacular.openapi.AutoSchema`
3. Confirm no static schema files exist
4. Review documentation guide for update instructions

---

## Additional Verification

### Documentation Accessibility

**Test Steps:**
1. Access documentation WITHOUT authentication
2. Verify all three endpoints work:
   - `http://localhost:8000/api/v1/schema/` - JSON schema
   - `http://localhost:8000/api/v1/docs/` - Swagger UI
   - `http://localhost:8000/api/v1/redoc/` - ReDoc UI

**Expected Result:**
- ✅ Documentation is publicly accessible
- ✅ No authentication required to view docs
- ✅ All three formats work correctly

---

### Authentication Documentation

**Test Steps:**
1. In Swagger UI, look for the "Authorize" button at the top
2. Click it and verify JWT Bearer authentication is configured
3. Read the description explaining how to use tokens
4. Expand any authenticated endpoint (e.g., `/api/v1/auth/me/`)
5. Verify it shows a lock icon indicating authentication required

**Expected Result:**
- ✅ Security scheme is documented (JWT Bearer)
- ✅ Instructions for authentication are clear
- ✅ Authenticated endpoints are marked
- ✅ Token format is explained

---

### Try It Out Functionality

**Test Steps:**
1. In Swagger UI, expand `GET /api/v1/health/`
2. Click "Try it out"
3. Click "Execute"
4. Verify you get a real response from the API

**Expected Result:**
- ✅ "Try it out" button works
- ✅ Request can be executed
- ✅ Real response is shown
- ✅ Response time is displayed

---

### Schema Export

**Test Steps:**
1. Visit `http://localhost:8000/api/v1/schema/`
2. Save the JSON response
3. Import it into Postman (or similar API client)
4. Verify all endpoints are imported correctly

**Expected Result:**
- ✅ Schema can be downloaded as JSON
- ✅ Schema is valid OpenAPI 3.0 format
- ✅ Can be imported into API clients
- ✅ Includes all endpoints and definitions

---

## Automated Test Verification

**Run Tests:**
```bash
cd /home/ed/Dev/architecture/backend
pytest tests/integration/test_api_documentation.py -v
```

**Expected Result:**
- ✅ All tests pass
- ✅ Schema endpoints are accessible
- ✅ Schema contains all expected endpoints
- ✅ Endpoints have proper documentation
- ✅ Examples are present
- ✅ Authentication is documented

---

## Health Endpoints Documentation

**Test Steps:**
1. Verify these endpoints are documented:
   - `GET /api/v1/health/` - Basic health check
   - `GET /api/v1/status/` - Detailed status
   - `GET /api/v1/health/ready/` - Readiness probe
   - `GET /api/v1/health/live/` - Liveness probe

**Expected Result:**
- ✅ All health endpoints are listed
- ✅ Each has a description
- ✅ Response formats are documented
- ✅ Examples are provided

---

## Authentication Endpoints Documentation

**Test Steps:**
1. Verify these endpoints are documented:
   - `POST /api/v1/auth/register/` - User registration
   - `POST /api/v1/auth/login/` - User login
   - `POST /api/v1/auth/logout/` - User logout
   - `POST /api/v1/auth/token/refresh/` - Token refresh

**Expected Result:**
- ✅ All auth endpoints are listed
- ✅ Request/response formats are clear
- ✅ Error cases are documented
- ✅ Examples show token structure

---

## User Profile Endpoints Documentation

**Test Steps:**
1. Verify these endpoints are documented:
   - `GET /api/v1/auth/me/` - Get current user
   - `POST /api/v1/auth/change-password/` - Change password

**Expected Result:**
- ✅ User endpoints are listed
- ✅ Authentication requirements are clear
- ✅ Request/response formats are documented
- ✅ Examples are helpful

---

## Documentation Quality

**Review:**
1. Check that all endpoints have:
   - Clear, concise summaries
   - Detailed descriptions
   - Proper tags for grouping
   - Request body schemas (for POST/PUT)
   - Response schemas for all status codes
   - Realistic examples

**Expected Result:**
- ✅ Documentation is comprehensive
- ✅ Descriptions are clear and helpful
- ✅ Examples are realistic
- ✅ No endpoints are missing documentation

---

## Sign Off

Once all checklist items are verified:

- [ ] All acceptance criteria met
- [ ] Documentation is accessible
- [ ] All endpoints are documented
- [ ] Examples are present and helpful
- [ ] Tests pass
- [ ] Documentation guide is available
- [ ] Ready for production use

**Verified By:** _________________

**Date:** _________________

**Notes:**
