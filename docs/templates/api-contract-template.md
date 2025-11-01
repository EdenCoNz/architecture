# API Contract: {Feature Name}

**Feature ID:** {feature_id}
**Created:** {YYYY-MM-DD}
**Related Stories:** {Story IDs that require API interactions}

## Overview

Brief description of the API endpoints in this feature and their purpose. Explain what functionality these endpoints enable and how they fit into the overall application architecture.

## Design Decisions

Document key API design decisions:
- Why these endpoints were chosen
- Authentication/authorization approach
- Pagination strategy (if applicable)
- Rate limiting considerations
- Caching strategy

## Common Types

Define shared TypeScript types used across multiple endpoints:

```typescript
// Common request/response types
export interface ErrorResponse {
  error: string;
  details?: Record<string, string[]>;
}

// Enums for fixed value sets
export type ResourceStatus = 'active' | 'inactive' | 'pending';

// Pagination types (if applicable)
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

## Endpoints

### 1. {Endpoint Name}

**Method:** GET | POST | PUT | PATCH | DELETE
**Path:** `/api/v1/resource/{id}/`
**Description:** Clear description of what this endpoint does and when it should be used.

**Authentication:** Required | Optional | Not Required

#### Request

**Path Parameters:**
- `id` (integer, required): Description of the ID parameter

**Query Parameters:**
- `param_name` (string, optional): Description of the parameter
  - Default: `default_value`
  - Valid values: `option1`, `option2`, `option3`

**Request Headers:**
- `Authorization` (required): Bearer token for authentication
- `Content-Type` (required): `application/json`

**Request Body:**
```typescript
interface CreateResourceRequest {
  field1: string;              // Description (required, max 255 chars)
  field2?: number;             // Description (optional, must be positive)
  field3: 'option1' | 'option2';  // Description (required, enum)
  nested: {
    subfield1: string;         // Description
    subfield2: boolean;        // Description
  };
}
```

**Example Request:**
```json
POST /api/v1/resource/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "field1": "Example value",
  "field2": 42,
  "field3": "option1",
  "nested": {
    "subfield1": "Nested value",
    "subfield2": true
  }
}
```

#### Response

**Success (201 Created):**
```typescript
interface ResourceResponse {
  id: string;                  // UUID of created resource
  field1: string;
  field2: number | null;
  field3: 'option1' | 'option2';
  nested: {
    subfield1: string;
    subfield2: boolean;
  };
  created_at: string;          // ISO 8601 datetime
  updated_at: string;          // ISO 8601 datetime
}
```

**Example Response:**
```json
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "field1": "Example value",
  "field2": 42,
  "field3": "option1",
  "nested": {
    "subfield1": "Nested value",
    "subfield2": true
  },
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### Validation Rules

**field1:**
- Required
- Type: string
- Max length: 255 characters
- Pattern: `^[a-zA-Z0-9\s-]+$` (alphanumeric, spaces, hyphens only)

**field2:**
- Optional
- Type: integer
- Must be positive (> 0)
- Range: 1 to 1000000

**field3:**
- Required
- Type: enum
- Allowed values: `'option1'`, `'option2'`

**nested.subfield1:**
- Required when `nested` is provided
- Type: string
- Min length: 1 character
- Max length: 100 characters

**Business Logic Validation:**
- If `field3` is `'option2'`, then `field2` must be provided
- The combination of `field1` and `nested.subfield1` must be unique

#### Error Responses

**400 Bad Request** - Validation Error
```json
{
  "error": "Validation failed",
  "details": {
    "field1": ["This field is required"],
    "field2": ["Must be a positive integer"],
    "nested": {
      "subfield1": ["This field cannot be blank"]
    }
  }
}
```

**401 Unauthorized** - Authentication Failed
```json
{
  "error": "Authentication credentials were not provided"
}
```

**403 Forbidden** - Insufficient Permissions
```json
{
  "error": "You do not have permission to perform this action"
}
```

**404 Not Found** - Resource Not Found (for endpoints with path parameters)
```json
{
  "error": "Resource not found"
}
```

**409 Conflict** - Unique Constraint Violation
```json
{
  "error": "Resource with this field1 already exists"
}
```

**422 Unprocessable Entity** - Business Logic Error
```json
{
  "error": "When field3 is 'option2', field2 must be provided"
}
```

**500 Internal Server Error** - Server Error
```json
{
  "error": "An unexpected error occurred. Please try again later."
}
```

#### Notes
- Additional implementation notes
- Performance considerations
- Caching behavior
- Rate limiting specifics

---

### 2. {Another Endpoint Name}

[Repeat the structure above for each endpoint]

---

## Integration Examples

### Frontend Usage (React/TypeScript)

```typescript
import { useState } from 'react';
import { CreateResourceRequest, ResourceResponse, ErrorResponse } from './api-types';

const useCreateResource = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorResponse | null>(null);

  const createResource = async (data: CreateResourceRequest): Promise<ResourceResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/resource/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        setError(errorData);
        return null;
      }

      const result: ResourceResponse = await response.json();
      return result;
    } catch (err) {
      setError({ error: 'Network error occurred' });
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { createResource, loading, error };
};
```

### Backend Implementation (Django/DRF)

```python
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class NestedSerializer(serializers.Serializer):
    subfield1 = serializers.CharField(min_length=1, max_length=100)
    subfield2 = serializers.BooleanField()

class CreateResourceSerializer(serializers.Serializer):
    field1 = serializers.CharField(
        max_length=255,
        regex=r'^[a-zA-Z0-9\s-]+$'
    )
    field2 = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=1000000
    )
    field3 = serializers.ChoiceField(choices=['option1', 'option2'])
    nested = NestedSerializer()

    def validate(self, data):
        # Business logic validation
        if data.get('field3') == 'option2' and data.get('field2') is None:
            raise serializers.ValidationError(
                "When field3 is 'option2', field2 must be provided"
            )
        return data

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_resource(request):
    serializer = CreateResourceSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create resource using validated data
    resource = Resource.objects.create(**serializer.validated_data)

    # Return response matching contract
    return Response(
        ResourceSerializer(resource).data,
        status=status.HTTP_201_CREATED
    )
```

---

## Testing Checklist

Use this checklist to verify contract compliance:

### Frontend Testing
- [ ] Request types match contract TypeScript interfaces
- [ ] All required fields are sent in requests
- [ ] API calls use correct HTTP methods and paths
- [ ] Response handling covers all documented status codes
- [ ] Error responses are displayed appropriately
- [ ] Authentication headers are included when required

### Backend Testing
- [ ] Endpoints respond at documented paths with correct methods
- [ ] Request validation matches contract rules
- [ ] Success responses match contract schema exactly
- [ ] Error responses use documented formats
- [ ] HTTP status codes match contract specifications
- [ ] Example payloads from contract pass validation

### Integration Testing
- [ ] Frontend requests successfully reach backend endpoints
- [ ] Backend responses are correctly parsed by frontend
- [ ] Validation errors are properly communicated
- [ ] All documented error scenarios are handled
- [ ] Authentication/authorization works as specified

---

## Change Log

Track contract modifications to ensure both frontend and backend stay in sync:

### {YYYY-MM-DD} - Initial Version
- Created initial contract with endpoints 1-N
- Defined validation rules
- Established error response format

### {YYYY-MM-DD} - Updated Endpoint 1
- Added `field4` to request (optional)
- Updated validation rules for `field2`
- Added 409 Conflict error response
- **Breaking Change:** None
- **Migration Required:** No

---

## Appendix

### Authentication Details
Describe the authentication mechanism in detail:
- Token format (JWT, OAuth, etc.)
- Token expiration
- Refresh token strategy
- How to obtain tokens

### Rate Limiting
- Requests per minute/hour
- Rate limit headers
- Rate limit exceeded response format

### Pagination Details (if applicable)
- Default page size
- Maximum page size
- Query parameters for pagination
- Pagination response format

### Versioning Strategy
- How API versioning is handled
- Deprecation policy
- Migration path for breaking changes
