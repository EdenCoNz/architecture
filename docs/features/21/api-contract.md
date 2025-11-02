# API Contract: Sports Terminology and Database Storage

**Feature ID:** 21
**Created:** 2025-11-02
**Related Stories:** 21.1, 21.3, 21.6

## Overview

This API contract documents the sport field implementation in the Assessment API endpoints. It clarifies the distinction between internal database values and user-facing display labels, specifically addressing the "soccer" vs "Football" terminology mapping.

**Key Concept:** The system uses "soccer" as the internal database identifier while displaying "Football" to users. This maintains internationally recognized terminology internally while preserving user-friendly labels in the interface.

## Design Decisions

### Internal Value vs Display Label Pattern

**Decision:** Use Django's `TextChoices` pattern to separate internal database values from user-facing labels.

**Rationale:**
- **Consistency:** Aligns with international terminology standards (soccer is universally recognized)
- **User Experience:** Maintains familiar terminology for users (Football in UI)
- **Data Integrity:** Internal values are stable and not subject to localization changes
- **API Clarity:** Clear separation between what's stored (value) and what's displayed (label)

**Implementation:**
```python
class Sport(models.TextChoices):
    SOCCER = "soccer", _("Football")  # Internal: "soccer", Display: "Football"
    CRICKET = "cricket", _("Cricket")  # Internal: "cricket", Display: "Cricket"
```

### API Response Strategy

**Decision:** Include both internal value and display label in API responses.

**Approach:**
1. `sport` field: Returns the internal database value (e.g., "soccer")
2. `sport_display` field: Returns the user-facing label (e.g., "Football")
3. Dedicated endpoint (`/sport-choices/`) provides complete mapping for dropdowns

**Benefits:**
- Frontend can display user-friendly labels without maintaining mapping logic
- Backend is source of truth for value-to-label mapping
- Easy to add localization support in the future
- Reduces frontend complexity and potential inconsistencies

---

## Common Types

### Sport Field Types

```typescript
/**
 * Sport internal values (database identifiers)
 * These are the values that should be sent in API requests
 */
export type SportValue = 'soccer' | 'cricket';

/**
 * Sport display labels (user-facing text)
 * These are shown to users in the UI
 */
export type SportDisplayName = 'Football' | 'Cricket';

/**
 * Sport choice with both internal value and display label
 * Used by the sport-choices endpoint
 */
export interface SportChoice {
  /** Internal database value (e.g., "soccer") */
  value: SportValue;
  /** User-facing display label (e.g., "Football") */
  display_name: SportDisplayName;
}

/**
 * Sport choices response
 */
export interface SportChoicesResponse {
  /** Array of available sport choices */
  choices: SportChoice[];
}
```

### Assessment Types

```typescript
/**
 * Assessment response with sport information
 * Includes both internal value and display label
 */
export interface AssessmentResponse {
  id: number;
  sport: SportValue;                    // Internal value: "soccer"
  sport_display: SportDisplayName;      // Display label: "Football"
  age: number;
  experience_level: string;
  training_days: string;
  injuries: string;
  equipment: string;
  equipment_items: string[];
  created_at: string;
  updated_at: string;
}

/**
 * Assessment create/update request
 * Only requires internal sport value
 */
export interface AssessmentRequest {
  sport: SportValue;                    // Send internal value: "soccer"
  age: number;
  experience_level: string;
  training_days: string;
  injuries?: string;
  equipment: string;
  equipment_items?: string[];
}
```

---

## Endpoints

### 1. Get Sport Choices

**Method:** GET
**Path:** `/api/v1/assessments/sport-choices/`
**Description:** Retrieve the list of available sports with both internal database values and user-friendly display labels. Use this endpoint to populate sport selection dropdowns in the UI.

**Authentication:** Required (JWT Bearer token)

#### Request

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** None (GET request)

#### Response

**Success (200 OK):**
```typescript
interface SportChoicesResponse {
  choices: Array<{
    value: string;        // Internal database value
    display_name: string; // User-facing display label
  }>;
}
```

**Example Response:**
```json
{
  "choices": [
    {
      "value": "soccer",
      "display_name": "Football"
    },
    {
      "value": "cricket",
      "display_name": "Cricket"
    }
  ]
}
```

**Usage Notes:**
- **Frontend Implementation:** Display `display_name` to users but submit `value` in requests
- **Caching:** This endpoint returns static data; consider caching the response
- **Form Initialization:** Call this endpoint once when loading the assessment form

**Example Frontend Code:**
```typescript
// Fetch sport choices for dropdown
const response = await fetch('/api/v1/assessments/sport-choices/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
const data: SportChoicesResponse = await response.json();

// Display in dropdown
data.choices.forEach(choice => {
  console.log(`Show: "${choice.display_name}", Submit: "${choice.value}"`);
  // Show: "Football", Submit: "soccer"
  // Show: "Cricket", Submit: "cricket"
});
```

#### Error Responses

**401 Unauthorized** - Missing or invalid authentication token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 2. Create Assessment

**Method:** POST
**Path:** `/api/v1/assessments/`
**Description:** Create a new assessment for the authenticated user. The sport field must use the internal value (e.g., "soccer"), not the display label.

**Authentication:** Required (JWT Bearer token)

#### Request

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```typescript
interface CreateAssessmentRequest {
  sport: string;              // Internal value: "soccer" or "cricket" (REQUIRED)
  age: number;                // User age: 13-100 (REQUIRED)
  experience_level: string;   // "beginner", "intermediate", or "advanced" (REQUIRED)
  training_days: string;      // "2-3", "4-5", or "6-7" (REQUIRED)
  injuries?: string;          // "yes" or "no" (OPTIONAL, default: "no")
  equipment: string;          // "no_equipment", "basic_equipment", or "full_gym" (REQUIRED)
  equipment_items?: string[]; // Required if equipment is "basic_equipment"
}
```

**Validation Rules - Sport Field:**
- **Required:** Must be provided
- **Valid Values:** "soccer", "cricket"
- **Case Sensitive:** Must be lowercase
- **Error Message:** "Please select a valid sport (soccer or cricket)"

**Example Request (Soccer/Football):**
```json
POST /api/v1/assessments/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "sport": "soccer",
  "age": 25,
  "experience_level": "intermediate",
  "training_days": "4-5",
  "injuries": "no",
  "equipment": "basic_equipment",
  "equipment_items": ["dumbbells", "resistance_bands"]
}
```

**Example Request (Cricket):**
```json
{
  "sport": "cricket",
  "age": 30,
  "experience_level": "advanced",
  "training_days": "6-7",
  "injuries": "yes",
  "equipment": "full_gym",
  "equipment_items": []
}
```

#### Response

**Success (201 Created):**
```typescript
interface AssessmentResponse {
  id: number;
  sport: string;              // Internal value: "soccer"
  sport_display: string;      // Display label: "Football"
  age: number;
  experience_level: string;
  training_days: string;
  injuries: string;
  equipment: string;
  equipment_items: string[];
  created_at: string;         // ISO 8601 datetime
  updated_at: string;         // ISO 8601 datetime
}
```

**Example Response:**
```json
{
  "id": 42,
  "sport": "soccer",
  "sport_display": "Football",
  "age": 25,
  "experience_level": "intermediate",
  "training_days": "4-5",
  "injuries": "no",
  "equipment": "basic_equipment",
  "equipment_items": ["dumbbells", "resistance_bands"],
  "created_at": "2025-11-02T14:30:00Z",
  "updated_at": "2025-11-02T14:30:00Z"
}
```

**Important Notes:**
- Response includes BOTH `sport` (internal value) and `sport_display` (user-facing label)
- Frontend should use `sport_display` when showing the sport to users
- Frontend should use `sport` value when submitting updates

#### Error Responses

**400 Bad Request - Invalid Sport Value:**
```json
{
  "sport": ["Please select a valid sport (soccer or cricket)"]
}
```

**400 Bad Request - Missing Sport:**
```json
{
  "sport": ["Sport selection is required"]
}
```

**400 Bad Request - Using Display Label Instead of Value:**
```json
// WRONG: Submitting "Football" instead of "soccer"
{
  "sport": "Football",  // ❌ This will fail
  ...
}

// Response:
{
  "sport": ["Please select a valid sport (soccer or cricket)"]
}

// CORRECT: Submit internal value
{
  "sport": "soccer",    // ✅ Correct internal value
  ...
}
```

---

### 3. Get Assessment (Detail)

**Method:** GET
**Path:** `/api/v1/assessments/{id}/`
**Description:** Retrieve a specific assessment by ID. Only returns assessments owned by the authenticated user.

**Authentication:** Required (JWT Bearer token)

#### Request

**Path Parameters:**
- `id` (integer, required): Assessment ID

**Request Headers:**
```
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**
Returns the same `AssessmentResponse` structure as the create endpoint, including both `sport` and `sport_display` fields.

**Example Response:**
```json
{
  "id": 42,
  "sport": "soccer",
  "sport_display": "Football",
  "age": 25,
  "experience_level": "intermediate",
  "training_days": "4-5",
  "injuries": "no",
  "equipment": "basic_equipment",
  "equipment_items": ["dumbbells", "resistance_bands"],
  "created_at": "2025-11-02T14:30:00Z",
  "updated_at": "2025-11-02T14:30:00Z"
}
```

---

### 4. Get Current User's Assessment

**Method:** GET
**Path:** `/api/v1/assessments/me/`
**Description:** Retrieve the authenticated user's assessment without needing to know the assessment ID. Convenient endpoint for fetching the current user's data.

**Authentication:** Required (JWT Bearer token)

#### Request

**Request Headers:**
```
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**
Returns the same `AssessmentResponse` structure, including both `sport` and `sport_display` fields.

**Example Response:**
```json
{
  "id": 42,
  "sport": "soccer",
  "sport_display": "Football",
  "age": 25,
  "experience_level": "intermediate",
  "training_days": "4-5",
  "injuries": "no",
  "equipment": "basic_equipment",
  "equipment_items": ["dumbbells", "resistance_bands"],
  "created_at": "2025-11-02T14:30:00Z",
  "updated_at": "2025-11-02T14:30:00Z"
}
```

**404 Not Found - No Assessment:**
```json
{
  "detail": "No assessment found for this user."
}
```

---

### 5. Update Assessment

**Method:** PUT / PATCH
**Path:** `/api/v1/assessments/{id}/`
**Description:** Update an existing assessment. Use PUT for full updates (all fields required) or PATCH for partial updates.

**Authentication:** Required (JWT Bearer token)

#### Request

**Path Parameters:**
- `id` (integer, required): Assessment ID

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (PUT):**
Same as create request - all fields required.

**Request Body (PATCH):**
Any subset of fields can be updated.

**Example PATCH Request (Update Sport Only):**
```json
PATCH /api/v1/assessments/42/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "sport": "cricket"
}
```

#### Response

**Success (200 OK):**
Returns the updated `AssessmentResponse` with both `sport` and `sport_display` fields.

**Example Response:**
```json
{
  "id": 42,
  "sport": "cricket",
  "sport_display": "Cricket",
  "age": 25,
  "experience_level": "intermediate",
  "training_days": "4-5",
  "injuries": "no",
  "equipment": "basic_equipment",
  "equipment_items": ["dumbbells", "resistance_bands"],
  "created_at": "2025-11-02T14:30:00Z",
  "updated_at": "2025-11-02T15:45:00Z"
}
```

---

### 6. List Assessments

**Method:** GET
**Path:** `/api/v1/assessments/`
**Description:** List all assessments for the authenticated user. In practice, users have only one assessment, so this typically returns a single item.

**Authentication:** Required (JWT Bearer token)

#### Response

**Success (200 OK):**
```typescript
interface AssessmentListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AssessmentResponse[];
}
```

**Example Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "sport": "soccer",
      "sport_display": "Football",
      "age": 25,
      "experience_level": "intermediate",
      "training_days": "4-5",
      "injuries": "no",
      "equipment": "basic_equipment",
      "equipment_items": ["dumbbells", "resistance_bands"],
      "created_at": "2025-11-02T14:30:00Z",
      "updated_at": "2025-11-02T14:30:00Z"
    }
  ]
}
```

---

## Sport Field Constraints and Validation

### Valid Sport Values

The sport field accepts the following internal values:

| Internal Value | Display Label | Description |
|---------------|---------------|-------------|
| `soccer` | Football | Association football / soccer |
| `cricket` | Cricket | Cricket |

### Validation Rules

1. **Required Field**: Sport must be provided in create/update requests
2. **Valid Values**: Only "soccer" or "cricket" are accepted
3. **Case Sensitive**: Values must be lowercase
4. **No Display Labels**: Submitting "Football" instead of "soccer" will fail validation

### Common Validation Errors

**Error 1: Missing Sport Field**
```json
// Request (missing sport)
{
  "age": 25,
  "experience_level": "intermediate"
}

// Response (400 Bad Request)
{
  "sport": ["Sport selection is required"]
}
```

**Error 2: Invalid Sport Value**
```json
// Request (invalid value)
{
  "sport": "football",  // ❌ Wrong - should be "soccer"
  ...
}

// Response (400 Bad Request)
{
  "sport": ["Please select a valid sport (soccer or cricket)"]
}
```

**Error 3: Using Display Label**
```json
// Request (using display label)
{
  "sport": "Football",  // ❌ Wrong - this is the display label
  ...
}

// Response (400 Bad Request)
{
  "sport": ["Please select a valid sport (soccer or cricket)"]
}
```

**Error 4: Empty Sport Field**
```json
// Request (empty value)
{
  "sport": "",
  ...
}

// Response (400 Bad Request)
{
  "sport": ["Sport cannot be empty"]
}
```

---

## OpenAPI Schema Documentation

The API uses `drf-spectacular` to generate OpenAPI/Swagger documentation. The sport field is documented with the following schema:

### Sport Field Schema

```yaml
sport:
  type: string
  enum:
    - soccer
    - cricket
  description: |
    Sport selection for training program.

    Valid internal values:
    - "soccer": Football/Association Football (displayed as "Football" to users)
    - "cricket": Cricket

    Important: Submit the internal value ("soccer"), not the display label ("Football").
  example: soccer
```

### Sport Display Field Schema

```yaml
sport_display:
  type: string
  readOnly: true
  description: |
    User-friendly display label for the sport field.
    This field is read-only and automatically populated based on the sport value.

    Examples:
    - When sport="soccer", sport_display="Football"
    - When sport="cricket", sport_display="Cricket"
  example: Football
```

### Accessing OpenAPI Schema

The complete API schema can be accessed at:
- **Schema JSON:** `GET /api/schema/`
- **Swagger UI:** `GET /api/schema/swagger-ui/`
- **ReDoc UI:** `GET /api/schema/redoc/`

---

## Frontend Integration Guide

### Best Practices

#### 1. Fetching Sport Options

**DO:** Fetch sport choices from the API
```typescript
const fetchSportChoices = async () => {
  const response = await fetch('/api/v1/assessments/sport-choices/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  const data = await response.json();
  return data.choices;
};
```

**DON'T:** Hardcode sport options in frontend
```typescript
// ❌ Avoid hardcoding - source of truth is backend
const sports = [
  { value: 'soccer', label: 'Football' },
  { value: 'cricket', label: 'Cricket' }
];
```

#### 2. Displaying Sport in Dropdown

**DO:** Show display_name, submit value
```typescript
// Populate dropdown
sportChoices.forEach(choice => {
  const option = document.createElement('option');
  option.value = choice.value;           // Internal value: "soccer"
  option.textContent = choice.display_name; // Display label: "Football"
  selectElement.appendChild(option);
});

// On submit
const formData = {
  sport: selectElement.value,  // ✅ Submits "soccer"
  ...
};
```

**DON'T:** Submit display label
```typescript
// ❌ Wrong - submitting display label
const formData = {
  sport: selectElement.options[selectElement.selectedIndex].text, // "Football"
  ...
};
```

#### 3. Displaying Saved Assessment

**DO:** Use sport_display for user-facing text
```typescript
// Show user-friendly label
const assessmentResponse = await getAssessment();
console.log(`Your sport: ${assessmentResponse.sport_display}`);
// Output: "Your sport: Football"
```

**DON'T:** Try to convert internal value yourself
```typescript
// ❌ Don't maintain your own mapping
const sportLabels = { soccer: 'Football', cricket: 'Cricket' };
console.log(`Your sport: ${sportLabels[assessmentResponse.sport]}`);
```

#### 4. Pre-selecting Sport in Edit Form

**DO:** Match internal value
```typescript
// When loading assessment for editing
const assessment = await getAssessment();
const sportSelect = document.querySelector('select[name="sport"]');
sportSelect.value = assessment.sport;  // ✅ Set to "soccer"
// The dropdown will show "Football" because that's the option's textContent
```

### Complete Example

```typescript
interface SportChoice {
  value: string;
  display_name: string;
}

interface Assessment {
  id: number;
  sport: string;
  sport_display: string;
  age: number;
  // ... other fields
}

class AssessmentForm {
  private sportChoices: SportChoice[] = [];

  async initialize() {
    // 1. Fetch sport choices for dropdown
    this.sportChoices = await this.fetchSportChoices();

    // 2. Populate dropdown
    this.populateSportDropdown();

    // 3. If editing, load existing assessment
    const existingAssessment = await this.loadAssessment();
    if (existingAssessment) {
      this.populateForm(existingAssessment);
    }
  }

  async fetchSportChoices(): Promise<SportChoice[]> {
    const response = await fetch('/api/v1/assessments/sport-choices/', {
      headers: {
        'Authorization': `Bearer ${this.getAccessToken()}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    return data.choices;
  }

  populateSportDropdown() {
    const select = document.querySelector('select[name="sport"]') as HTMLSelectElement;

    this.sportChoices.forEach(choice => {
      const option = document.createElement('option');
      option.value = choice.value;              // "soccer"
      option.textContent = choice.display_name;  // "Football"
      select.appendChild(option);
    });
  }

  async loadAssessment(): Promise<Assessment | null> {
    try {
      const response = await fetch('/api/v1/assessments/me/', {
        headers: {
          'Authorization': `Bearer ${this.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      return null;
    }
  }

  populateForm(assessment: Assessment) {
    // Set sport dropdown to internal value
    const sportSelect = document.querySelector('select[name="sport"]') as HTMLSelectElement;
    sportSelect.value = assessment.sport;  // "soccer" - dropdown shows "Football"

    // Display sport to user
    console.log(`Current sport: ${assessment.sport_display}`);  // "Football"

    // ... populate other fields
  }

  async submitForm() {
    const form = document.querySelector('form') as HTMLFormElement;
    const formData = new FormData(form);

    const data = {
      sport: formData.get('sport') as string,  // Submits "soccer", not "Football"
      age: parseInt(formData.get('age') as string),
      // ... other fields
    };

    const response = await fetch('/api/v1/assessments/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.getAccessToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      const result: Assessment = await response.json();
      console.log(`Assessment created with sport: ${result.sport_display}`);
      // Output: "Assessment created with sport: Football"
    }
  }

  private getAccessToken(): string {
    return localStorage.getItem('access_token') || '';
  }
}
```

---

## Testing Considerations

### Backend Tests

Test cases should verify:

1. **Sport field accepts valid internal values**
   - "soccer" should be accepted
   - "cricket" should be accepted

2. **Sport field rejects invalid values**
   - "football" should be rejected (wrong internal value)
   - "Football" should be rejected (display label, not value)
   - Empty string should be rejected
   - Null should be rejected

3. **Response includes both sport and sport_display**
   - Create response has both fields
   - Retrieve response has both fields
   - List response has both fields for each item
   - Update response has both fields

4. **sport_display shows correct labels**
   - When sport="soccer", sport_display="Football"
   - When sport="cricket", sport_display="Cricket"

5. **Sport-choices endpoint returns correct data**
   - Returns array of choices
   - Each choice has value and display_name
   - Soccer maps to Football
   - Cricket maps to Cricket

### Frontend Tests

Test cases should verify:

1. **Sport choices fetched from API**
   - Dropdown populated from API response
   - Display labels shown to user

2. **Form submission uses internal values**
   - Submitting "Football" selection sends "soccer" value
   - Validation errors handled correctly

3. **Existing assessments display correctly**
   - sport_display shown in UI
   - Internal sport value used for form pre-selection

4. **Error handling**
   - Invalid sport values rejected
   - Validation error messages displayed

---

## Migration Notes

### From Previous Implementation

Prior to Feature 21, the system used "football" as the internal value. This has been changed to "soccer" with the following impacts:

1. **Database Migration**: All existing records with sport="football" were migrated to sport="soccer"
2. **API Behavior**: The API now only accepts "soccer", not "football"
3. **Display Labels**: Users continue to see "Football" in the UI (no change from user perspective)

### Backward Compatibility

**Breaking Changes:**
- API requests with sport="football" will now fail validation
- Frontend must update to use sport="soccer" when submitting forms

**Non-Breaking Changes:**
- Display labels unchanged (still show "Football" to users)
- Response structure unchanged (added sport_display field, but additive change)

---

## Summary

### Key Points

1. **Internal Value:** Always use "soccer" (not "football" or "Football") when sending requests
2. **Display Label:** The API returns "Football" in the `sport_display` field for user-facing text
3. **Source of Truth:** Fetch sport choices from `/api/v1/assessments/sport-choices/` endpoint
4. **Response Structure:** All assessment responses include both `sport` and `sport_display` fields
5. **Validation:** Only "soccer" and "cricket" are valid sport values

### Valid Sport Values Reference

| ✅ Valid Internal Value | ❌ Invalid Values | ✅ Correct Display Label |
|------------------------|-------------------|------------------------|
| `soccer` | `football`, `Football`, `Soccer` | `Football` |
| `cricket` | `Cricket` (API expects lowercase) | `Cricket` |

### Quick Reference for Developers

**When creating/updating an assessment:**
```json
{
  "sport": "soccer"  // ✅ Use this internal value
}
```

**When displaying to users:**
```typescript
// ✅ Use the sport_display field from API response
<div>Your sport: {assessment.sport_display}</div>
// Output: "Your sport: Football"
```

**When populating dropdowns:**
```typescript
// ✅ Fetch from API, show display_name, submit value
sportChoices.forEach(choice => {
  // value: "soccer", display_name: "Football"
});
```

---

**Contract Status:** ✅ Complete
**Last Updated:** 2025-11-02
**Version:** 1.0
