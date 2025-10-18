# Django Rest Framework Production Guide

## Core Architecture

DRF API is composed of 3 layers:
- **Serializer**: Converts database models to/from API formats (JSON, XML)
- **ViewSet**: Defines CRUD operations available via API
- **Router**: Maps URLs to viewsets

## Serializers Best Practices

### When to Use Which
- **ModelSerializer**: Default choice for simple model-to-JSON conversion
- **Custom Serializer**: When complex validation or business logic required
- **Different serializers per action**: Use separate read/write serializers for optimization

```python
class MyViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MyModelWriteSerializer
        return MyModelReadSerializer
```

### Nested Serializers
- Keep nesting shallow (max 2-3 levels)
- Use `select_related()` and `prefetch_related()` to avoid N+1 queries
- Consider read-only nested serializers to prevent performance issues

## ViewSets and Views

### ViewSet Types
- **ModelViewSet**: Full CRUD (.list, .retrieve, .create, .update, .partial_update, .destroy)
- **ReadOnlyModelViewSet**: List and retrieve only
- **GenericViewSet**: Custom action combinations

### When to Use Function-Based Views
- Simple, one-off endpoints
- Endpoints that don't fit REST patterns

## API Design Patterns

### Versioning Strategies
Configure in settings.py:
```python
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
}
```

**Versioning Options**:
- **URLPathVersioning**: `/api/v1/users/` (recommended for simplicity)
- **NamespaceVersioning**: Better for large projects
- **AcceptHeaderVersioning**: RESTful but less visible
- **QueryParameterVersioning**: `/api/users/?version=v1`

### Pagination
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}
```

**Pagination Types**:
- **PageNumberPagination**: Simple page numbers
- **LimitOffsetPagination**: Flexible offset-based
- **CursorPagination**: Best for large/changing datasets (recommended for production)

### Filtering and Search
```python
# settings.py
INSTALLED_APPS = [..., 'django_filters']

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ]
}

# views.py
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    filterset_fields = ['category', 'in_stock']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
```

## Authentication & Permissions

### Authentication Methods (Production)

**JWT (JSON Web Tokens)** - Recommended for SPAs/Mobile:
```python
# Use djangorestframework-simplejwt
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

**OAuth2** - For third-party integrations:
```python
# Use django-oauth-toolkit
INSTALLED_APPS = [..., 'oauth2_provider']
```

**Session Authentication** - For same-domain web apps with CSRF protection

### Permission Classes
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Custom per-view permissions
class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
```

## Throttling and Rate Limiting

**IMPORTANT**: Default local memory cache doesn't work with multiple workers/replicas. Use Redis for production.

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# With Redis cache backend
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Custom Throttling
```python
from rest_framework.throttling import SimpleRateThrottle

class BurstRateThrottle(SimpleRateThrottle):
    scope = 'burst'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}
```

## Exception Handling

```python
# Custom exception handler
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response

# settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'myapp.utils.custom_exception_handler'
}
```

## Testing Best Practices

### Use pytest with Factory Boy
```python
# conftest.py
import pytest
from pytest_factoryboy import register
from .factories import UserFactory, ArticleFactory

register(UserFactory)
register(ArticleFactory)

# tests.py
@pytest.mark.django_db
class TestArticleAPI:
    def test_list_articles(self, api_client, article_factory):
        article_factory.create_batch(5)
        response = api_client.get('/api/v1/articles/')
        assert response.status_code == 200
        assert len(response.json()['results']) == 5
```

### Testing Guidelines
- Test business logic, not Django's built-in functionality
- Use factory fixtures for test data
- Test permissions and authentication separately
- Test edge cases and validation errors

## Performance Optimization

### Query Optimization
```python
# Bad - N+1 queries
articles = Article.objects.all()
for article in articles:
    print(article.author.name)  # Query per iteration

# Good - Single query with join
articles = Article.objects.select_related('author').all()

# For reverse foreign keys and many-to-many
articles = Article.objects.prefetch_related('comments').all()

# Combine both
Article.objects.select_related('author').prefetch_related('tags')
```

### Response Optimization
```python
# Use .only() to fetch specific fields
Article.objects.only('id', 'title', 'created_at')

# Use .defer() to exclude heavy fields
Article.objects.defer('content', 'metadata')

# Use .values() for dictionaries (faster)
Article.objects.values('id', 'title')
```

## Project Structure

```
project/
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── filters.py
│   │   └── tests/
│   ├── articles/
│   └── ...
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   └── wsgi.py/asgi.py
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

## Key Production Settings

```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # Remove BrowsableAPI
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '10000/day'
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}
```

## Documentation

Use drf-spectacular for OpenAPI 3.0 schema:
```python
INSTALLED_APPS += ['drf_spectacular']

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'DESCRIPTION': 'API description',
    'VERSION': '1.0.0',
}
```

## Common Pitfalls.

1. **N+1 Queries**: Always use select_related/prefetch_related
2. **Missing Throttling**: Enable rate limiting from day one
3. **No Versioning**: Add versioning before first release
4. **Weak Permissions**: Set restrictive defaults, open up specific endpoints
5. **No Pagination**: Always paginate list endpoints
6. **Debug=True in Prod**: Never deploy with DEBUG enabled
7. **Hardcoded Secrets**: Use environment variables
8. **No HTTPS**: Always use HTTPS in production with JWT/tokens
