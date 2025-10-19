# User Preferences App

Django app for managing user-specific preferences and settings.

## Overview

The preferences app provides a flexible system for storing and managing user preferences. Currently supports theme preferences (light, dark, auto) with the ability to easily extend for additional preference types.

## Features

- **Theme Preference Management**: Store and retrieve user theme preference (light/dark/auto)
- **Automatic Defaults**: Creates default preferences automatically if none exist
- **Per-User Settings**: Each user has independent preferences
- **RESTful API**: Clean API endpoints for getting and updating preferences
- **Type Safety**: Full type hints and validation
- **Comprehensive Tests**: Unit and integration tests with high coverage

## Models

### UserPreferences

Stores user-specific preferences with a one-to-one relationship to the User model.

**Fields:**
- `user` (OneToOneField): Related user account
- `theme` (CharField): Theme preference - choices: 'light', 'dark', 'auto' (default: 'auto')
- `created_at` (DateTimeField): Timestamp when preferences were created
- `updated_at` (DateTimeField): Timestamp when preferences were last updated

**Model Properties:**
- One-to-one relationship with User model
- Cascading delete when user is deleted
- Automatic timestamp management
- Validation for theme choices

## API Endpoints

### Get Theme Preference

**Endpoint:** `GET /api/preferences/theme/`

**Authentication:** Required

**Description:** Retrieves the authenticated user's theme preference. Creates default preferences (auto theme) if none exist.

**Response:**
```json
{
  "theme": "dark",
  "created_at": "2025-10-19T12:00:00Z",
  "updated_at": "2025-10-19T14:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: User not authenticated

### Update Theme Preference

**Endpoint:** `PATCH /api/preferences/theme/`

**Authentication:** Required

**Description:** Updates the authenticated user's theme preference. Creates preferences if none exist.

**Request Body:**
```json
{
  "theme": "dark"
}
```

**Valid theme values:** `light`, `dark`, `auto`

**Response:**
```json
{
  "theme": "dark",
  "created_at": "2025-10-19T12:00:00Z",
  "updated_at": "2025-10-19T14:35:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid theme value
- `401 Unauthorized`: User not authenticated

## Usage Examples

### Frontend Integration

#### Get current theme preference

```javascript
// Using fetch API
const response = await fetch('/api/preferences/theme/', {
  headers: {
    'Authorization': 'Bearer <token>',
    'Content-Type': 'application/json',
  },
});
const data = await response.json();
console.log('Current theme:', data.theme);
```

#### Update theme preference

```javascript
// Using fetch API
const response = await fetch('/api/preferences/theme/', {
  method: 'PATCH',
  headers: {
    'Authorization': 'Bearer <token>',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ theme: 'dark' }),
});
const data = await response.json();
console.log('Updated theme:', data.theme);
```

### Python/Django Usage

```python
from apps.preferences.models import UserPreferences

# Get or create user preferences
preferences, created = UserPreferences.objects.get_or_create(
    user=user,
    defaults={'theme': 'auto'}
)

# Update theme
preferences.theme = 'dark'
preferences.save()

# Access through user relationship
user.preferences.theme  # Returns 'dark'
```

## Testing

The app includes comprehensive test coverage:

### Unit Tests

Located in `tests/unit/apps/preferences/`

**test_models.py:**
- Model creation and validation
- Default values and choices
- One-to-one relationship constraints
- Cascade deletion behavior
- String representation

**test_serializers.py:**
- Serialization and deserialization
- Field validation
- Read-only field enforcement
- Partial updates

### Integration Tests

Located in `tests/integration/api/preferences/`

**test_theme_endpoints.py:**
- GET endpoint for authenticated users
- PATCH endpoint for updating preferences
- Authentication requirements
- Automatic default creation
- Invalid value handling
- Multi-user independence

### Running Tests

```bash
# Run all preferences tests
PYTHONPATH=src pytest tests/unit/apps/preferences/ tests/integration/api/preferences/

# Run with coverage
PYTHONPATH=src pytest --cov=apps.preferences tests/unit/apps/preferences/ tests/integration/api/preferences/

# Run specific test file
PYTHONPATH=src pytest tests/unit/apps/preferences/test_models.py
```

## Database Migration

The app includes a migration for creating the `user_preferences` table:

```bash
# Apply migrations
PYTHONPATH=src python manage.py migrate preferences

# Create new migrations (if model changes)
PYTHONPATH=src python manage.py makemigrations preferences
```

## Admin Interface

The UserPreferences model is registered in the Django admin with:
- List display: user, theme, timestamps
- Filtering by theme and dates
- Search by username and email
- Autocomplete for user selection

Access at: `/admin/preferences/userpreferences/`

## Security Considerations

- **Authentication Required**: All endpoints require user authentication
- **User Isolation**: Users can only access/modify their own preferences
- **Input Validation**: Theme values are validated against allowed choices
- **No PII Exposure**: Preference data contains no personally identifiable information beyond user association

## Future Extensions

The preferences model is designed to be easily extended for additional preference types:

```python
# Example: Adding notification preferences
class UserPreferences(models.Model):
    # Existing fields...
    theme = models.CharField(...)

    # New preference fields
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[('instant', 'Instant'), ('daily', 'Daily'), ('weekly', 'Weekly')],
        default='instant'
    )
```

## Architecture

The app follows Django best practices:

- **Models**: Define data structure and validation (backend/src/apps/preferences/models.py)
- **Serializers**: Handle API serialization/deserialization (backend/src/apps/preferences/serializers.py)
- **Views**: Implement API endpoints (backend/src/apps/preferences/views.py)
- **URLs**: Define routing (backend/src/apps/preferences/urls.py)
- **Admin**: Provide admin interface (backend/src/apps/preferences/admin.py)
- **Tests**: Comprehensive test coverage (tests/unit/apps/preferences/, tests/integration/api/preferences/)

## Dependencies

- Django 5.1+
- Django REST Framework
- PostgreSQL (production) / SQLite (development)
- drf-spectacular (API documentation)

## Related Documentation

- [Django Models Documentation](https://docs.djangoproject.com/en/5.1/topics/db/models/)
- [Django REST Framework Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
- [drf-spectacular Schema Generation](https://drf-spectacular.readthedocs.io/)
