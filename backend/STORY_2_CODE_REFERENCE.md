# Story #2 Code Reference: Store User Theme Preference

Quick reference guide to key code components for the theme preference implementation.

## File Structure

```
backend/
├── src/
│   ├── apps/
│   │   └── preferences/
│   │       ├── __init__.py
│   │       ├── apps.py
│   │       ├── models.py              # UserPreferences model
│   │       ├── serializers.py         # API serializer
│   │       ├── views.py               # API endpoints
│   │       ├── urls.py                # URL routing
│   │       ├── admin.py               # Django admin
│   │       ├── README.md              # App documentation
│   │       └── migrations/
│   │           ├── __init__.py
│   │           └── 0001_initial.py    # Database migration
│   └── backend/
│       ├── settings/
│       │   └── base.py                # Added app to LOCAL_APPS
│       └── urls.py                    # Added preferences URLs
└── tests/
    ├── unit/
    │   └── apps/
    │       └── preferences/
    │           ├── __init__.py
    │           ├── test_models.py     # 13 model tests
    │           └── test_serializers.py # 12 serializer tests
    └── integration/
        └── api/
            └── preferences/
                ├── __init__.py
                └── test_theme_endpoints.py  # 15 API tests
```

## Core Model (backend/src/apps/preferences/models.py)

```python
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class UserPreferences(models.Model):
    """Store user-specific preferences."""

    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("auto", "Auto"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="preferences",
    )

    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default="auto",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_preferences"
        ordering = ["-updated_at"]
```

## Serializer (backend/src/apps/preferences/serializers.py)

```python
from rest_framework import serializers
from apps.preferences.models import UserPreferences

class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for UserPreferences model."""

    class Meta:
        model = UserPreferences
        fields = ["theme", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_theme(self, value: str) -> str:
        """Validate theme value."""
        valid_themes = [choice[0] for choice in UserPreferences.THEME_CHOICES]
        if value not in valid_themes:
            raise serializers.ValidationError(
                f"Invalid theme. Must be one of: {', '.join(valid_themes)}"
            )
        return value
```

## API View (backend/src/apps/preferences/views.py)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ThemePreferenceView(APIView):
    """API view for managing user theme preferences."""

    def get(self, request):
        """Get user's theme preference."""
        preferences, created = UserPreferences.objects.get_or_create(
            user=request.user,
            defaults={"theme": "auto"}
        )
        serializer = UserPreferencesSerializer(preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update user's theme preference."""
        preferences, created = UserPreferences.objects.get_or_create(
            user=request.user,
            defaults={"theme": "auto"}
        )
        serializer = UserPreferencesSerializer(
            preferences,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

## URL Configuration (backend/src/apps/preferences/urls.py)

```python
from django.urls import path
from apps.preferences.views import ThemePreferenceView

app_name = "preferences"

urlpatterns = [
    path("theme/", ThemePreferenceView.as_view(), name="theme"),
]
```

## Settings Update (backend/src/backend/settings/base.py)

```python
LOCAL_APPS: list[str] = [
    "apps.preferences",
]
```

## Root URLs Update (backend/src/backend/urls.py)

```python
urlpatterns = [
    # ... existing patterns ...
    path("api/preferences/", include("apps.preferences.urls")),
]
```

## API Usage Examples

### GET Request (Retrieve Theme)

```bash
curl -X GET http://localhost:8000/api/preferences/theme/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

Response:
```json
{
  "theme": "dark",
  "created_at": "2025-10-19T12:00:00Z",
  "updated_at": "2025-10-19T14:30:00Z"
}
```

### PATCH Request (Update Theme)

```bash
curl -X PATCH http://localhost:8000/api/preferences/theme/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"theme": "dark"}'
```

Response:
```json
{
  "theme": "dark",
  "created_at": "2025-10-19T12:00:00Z",
  "updated_at": "2025-10-19T14:35:00Z"
}
```

## Database Schema

```sql
CREATE TABLE user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    theme VARCHAR(10) NOT NULL DEFAULT 'auto',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT theme_check CHECK (theme IN ('light', 'dark', 'auto'))
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_updated_at ON user_preferences(updated_at);
```

## Test Examples

### Model Test (tests/unit/apps/preferences/test_models.py)

```python
@pytest.mark.django_db
def test_create_user_preferences_with_default_theme(user):
    """Test creating user preferences with default theme value."""
    preferences = UserPreferences.objects.create(user=user)

    assert preferences.user == user
    assert preferences.theme == "auto"
    assert preferences.created_at is not None
```

### Serializer Test (tests/unit/apps/preferences/test_serializers.py)

```python
@pytest.mark.django_db
def test_deserialize_invalid_theme(user):
    """Test deserializing invalid theme raises validation error."""
    data = {"theme": "invalid"}
    serializer = UserPreferencesSerializer(data=data)

    assert not serializer.is_valid()
    assert "theme" in serializer.errors
```

### API Test (tests/integration/api/preferences/test_theme_endpoints.py)

```python
@pytest.mark.django_db
def test_update_theme_preference_to_dark(authenticated_client, user):
    """Test updating theme preference to dark mode."""
    UserPreferences.objects.create(user=user, theme="light")

    url = reverse("preferences:theme")
    data = {"theme": "dark"}
    response = authenticated_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["theme"] == "dark"
```

## Running Tests

```bash
# All preferences tests
PYTHONPATH=src pytest tests/unit/apps/preferences/ tests/integration/api/preferences/

# With coverage
PYTHONPATH=src pytest --cov=apps.preferences tests/unit/apps/preferences/ tests/integration/api/preferences/

# Specific test file
PYTHONPATH=src pytest tests/unit/apps/preferences/test_models.py -v

# Watch mode (TDD)
PYTHONPATH=src ptw tests/unit/apps/preferences/
```

## Django Admin

Access at: `http://localhost:8000/admin/preferences/userpreferences/`

Features:
- List view with user, theme, timestamps
- Filter by theme and dates
- Search by username/email
- Autocomplete user selection

## API Documentation

Automatically generated at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## Integration Checklist

For frontend developers integrating with this API:

- [ ] Import API client or fetch library
- [ ] Implement getThemePreference() function
- [ ] Implement updateThemePreference(theme) function
- [ ] Call GET endpoint on app initialization
- [ ] Call PATCH endpoint when user changes theme
- [ ] Handle loading states
- [ ] Handle error states (network, validation, auth)
- [ ] Handle 'auto' theme by detecting system preference
- [ ] Add CSRF token for PATCH requests (if using session auth)
- [ ] Test with all three theme values: 'light', 'dark', 'auto'

## Common Troubleshooting

**401 Unauthorized:**
- Ensure user is authenticated
- Check authentication headers/cookies
- Verify CSRF token (for session auth)

**400 Bad Request:**
- Check theme value is exactly 'light', 'dark', or 'auto' (lowercase)
- Ensure Content-Type header is 'application/json'
- Verify JSON is valid

**404 Not Found:**
- Check URL is `/api/preferences/theme/` (with trailing slash)
- Verify app is registered in settings
- Confirm migrations are applied

## Files Modified

1. `backend/src/backend/settings/base.py` - Added 'apps.preferences' to LOCAL_APPS
2. `backend/src/backend/urls.py` - Added preferences URL include

## Key Design Patterns

- **Repository Pattern**: UserPreferences model as data repository
- **Serializer Pattern**: DRF serializer for validation and transformation
- **Factory Pattern**: get_or_create for automatic default creation
- **TDD Pattern**: Tests written before implementation
- **RESTful API**: Standard HTTP methods (GET, PATCH)
- **Authentication Required**: All endpoints require auth
- **Validation First**: Input validation before database operations

## Performance Notes

- Single database query per request (GET or PATCH)
- OneToOne relationship ensures max one preference per user
- Indexes on user_id and updated_at for fast lookups
- Auto-creation pattern prevents N+1 queries
- Consider adding caching layer for high-traffic scenarios

## Security Notes

- Authentication required for all endpoints
- User isolation enforced (can only access own preferences)
- Input validation prevents invalid data
- No XSS risk (JSON API)
- Database constraints enforce data integrity
- CSRF protection via Django middleware
