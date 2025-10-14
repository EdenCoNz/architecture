# Django REST Framework with MySQL: Best Practices Guide
**Date**: 2025-10-13
**Purpose**: Inform development decisions for Django REST Framework applications using MySQL with latest standards

## Summary

Django 5.2 and DRF 3.15 (released March 2024) provide robust support for MySQL 8.0+, with significant improvements including utf8mb4 as the default charset, enhanced geospatial support, and improved security. Critical areas requiring attention include connection pooling (MySQL lacks native Django 5.x support unlike PostgreSQL), query optimization through select_related/prefetch_related, and addressing recent SQL injection vulnerabilities (CVE-2024-42005, CVE-2024-53908). Performance optimization focuses on serializer design choices, cursor-based pagination for large datasets, and strict SQL mode configuration.

## 1. Database Configuration and Optimization

### MySQL Version and Driver Requirements
- **Minimum supported version**: MySQL 8.0.11+
- **Recommended drivers**: mysqlclient (native, preferred) or MySQL Connector/Python (pure Python)
- **Default charset**: utf8mb4 (as of Django 5.2) for full Unicode support including emojis

### Optimal Database Configuration

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "your_database",
        "USER": "your_user",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            # Enable strict SQL mode to prevent data loss
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
            "sql_mode": "STRICT_TRANS_TABLES",
            "isolation_level": "read committed",
        },
        # Persistent connections
        "CONN_MAX_AGE": 600,  # 10 minutes
    }
}
```

### Critical MySQL Limitations
- **VARCHAR fields with unique=True**: 255 character limit
- **TextField**: Cannot be indexed directly
- **No transaction support for DDL**: Schema changes cannot be rolled back
- **Case-insensitive collation**: Default behavior affects string comparisons
- **Index size limits**: Smaller combined column size limit compared to PostgreSQL

### Storage Engine
- **Use InnoDB exclusively**: Provides ACID compliance, foreign keys, and transaction support
- **Create database command**: `CREATE DATABASE <dbname> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

## 2. Connection Pooling and Performance Tuning

### Current State (as of Django 5.1/5.2)
- **Native connection pooling**: Only available for PostgreSQL in Django 5.1+
- **MySQL limitation**: No native Django connection pooling support

### Connection Pooling Solutions

#### Option 1: Persistent Connections (Built-in, Recommended)
```python
DATABASES = {
    "default": {
        # ... other settings
        "CONN_MAX_AGE": 600,  # 10 minutes, or None for unlimited
    }
}
```
- **Performance impact**: Reduces latency by 50-70ms per request
- **Caution**: Disable for ASGI applications (set to 0)
- **Not suitable for**: Long-running processes with infrequent queries

#### Option 2: Third-Party Connection Pooling
**django-db-connection-pool** (SQLAlchemy-based):
```python
DATABASES = {
    "default": {
        "ENGINE": "dj_db_conn_pool.backends.mysql",
        # ... other settings
        "POOL_OPTIONS": {
            "POOL_SIZE": 10,
            "MAX_OVERFLOW": 20,
            "RECYCLE": 3600,  # Recycle connections after 1 hour
            "PRE_PING": True,  # Verify connection health
        }
    }
}
```

**Warning**: Third-party pooling packages often break during Django upgrades and may lack maintenance.

### Performance Tuning Recommendations
- **For sync/WSGI apps**: Use CONN_MAX_AGE=600
- **For async/ASGI apps**: Disable persistent connections, use database-level pooling
- **Monitor connection counts**: Ensure pool size matches concurrent worker capacity
- **Connection recycling**: Set RECYCLE parameter to prevent stale connections

## 3. Models, Serializers, and ViewSets Best Practices

### Model Design for MySQL

```python
from django.db import models

class Article(models.Model):
    # Use db_index for frequently queried fields
    title = models.CharField(max_length=200, db_index=True)

    # Avoid TextField for indexed columns (MySQL limitation)
    slug = models.SlugField(max_length=200, unique=True)

    # Use appropriate field types for performance
    status = models.IntegerField(
        choices=[(1, 'Draft'), (2, 'Published')],
        db_index=True  # Integer indexes are faster than string comparisons
    )

    # Timestamps for cursor pagination
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Explicit table name
        db_table = 'articles'
        # Index for common query patterns
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
        # Ordering for consistent pagination
        ordering = ['-created_at']
```

### Serializer Performance Optimization

**Performance Hierarchy** (benchmarked on 10k objects):
1. **Simple function**: 0.034 seconds (fastest)
2. **Regular Serializer**: 2.101 seconds
3. **ModelSerializer (read-only)**: 7.407 seconds
4. **ModelSerializer (writable)**: 12.818 seconds (slowest)

**Optimization Strategy**:
```python
from rest_framework import serializers

# BAD: Writable ModelSerializer for read-only endpoint
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'author', 'created_at']

# GOOD: Explicit read-only fields
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'author', 'created_at']
        read_only_fields = ['id', 'title', 'author', 'created_at']

# BETTER: Regular serializer for read-only (3.5x faster)
class ArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    author = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

# BEST: Direct serialization for critical performance
from django.http import JsonResponse

def article_list(request):
    articles = Article.objects.values('id', 'title', 'author', 'created_at')
    return JsonResponse(list(articles), safe=False)
```

### ViewSet Query Optimization

**Critical: Prevent N+1 Queries**
```python
from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        # BAD: N+1 queries (1 query + N queries for each author)
        # return Article.objects.all()

        # GOOD: One-to-one/Foreign key (single JOIN query)
        queryset = Article.objects.select_related('author', 'category')

        # GOOD: Many-to-many/Reverse FK (2 queries total)
        queryset = queryset.prefetch_related('tags', 'comments')

        # GOOD: Add ordering for pagination
        queryset = queryset.order_by('-created_at')

        return queryset
```

**Performance Impact**: select_related and prefetch_related can reduce queries from N+1 to 1-2 total queries, improving response time by 99% on large datasets.

## 4. Common Pitfalls and Avoidance Strategies

### Pitfall 1: Missing Query Optimization
**Problem**: Serializers automatically trigger database queries for related objects.
**Solution**: Always use select_related/prefetch_related in ViewSet.get_queryset()

### Pitfall 2: Writable Serializers for Read-Only Endpoints
**Problem**: 6x slower performance due to validation overhead.
**Solution**: Mark fields as read_only or use regular Serializer class.

### Pitfall 3: Case-Insensitive String Lookups on MySQL
**Problem**: `lookup_expr="iexact"` uses LIKE, causing full table scans.
```python
# BAD: Uses LIKE (slow)
class ArticleFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')

# GOOD: Uses = comparison (fast)
class ArticleFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='exact')

# BEST: Use integer choices instead of strings
class ArticleFilter(filters.FilterSet):
    status = filters.NumberFilter(field_name='status')
```

### Pitfall 4: No Transaction Support for DDL
**Problem**: Failed migrations cannot be rolled back on MySQL.
**Solution**:
- Test migrations on staging database first
- Keep migrations small and atomic
- Use `--fake` flag cautiously
- Backup database before running migrations

### Pitfall 5: Slow Pagination COUNT Queries
**Problem**: COUNT(*) on millions of rows takes hundreds of milliseconds.
**Solution**: Override paginator to select only 'id' for counting:
```python
from rest_framework.pagination import PageNumberPagination

class OptimizedPagination(PageNumberPagination):
    def get_count(self, queryset):
        # Only count IDs, not entire row data
        return queryset.values('id').count()
```

### Pitfall 6: Using MyISAM Storage Engine
**Problem**: No foreign key support, table-level locking, no transactions.
**Solution**: Always use InnoDB. Convert existing tables:
```sql
ALTER TABLE table_name ENGINE=InnoDB;
```

## 5. Security Considerations

### SQL Injection Prevention

**Built-in Protection**: Django querysets use parameterized queries, preventing SQL injection.

```python
# SAFE: Parameterized query
Article.objects.filter(title=user_input)

# SAFE: Parameterized raw SQL
Article.objects.raw('SELECT * FROM articles WHERE title = %s', [user_input])

# UNSAFE: String formatting
Article.objects.raw(f'SELECT * FROM articles WHERE title = "{user_input}"')
```

### Recent Critical Vulnerabilities (2024)

**CVE-2024-42005 (CVSS 9.8)**: SQL injection in QuerySet.values()/values_list() with JSONField
- **Affected versions**: Django < 5.0.8, < 4.2.15
- **Mitigation**: Upgrade to Django 5.0.8+, 4.2.15+, or 3.2.26+

**CVE-2024-53908**: SQL injection in HasKey lookup on Oracle with untrusted lhs value
- **Affected versions**: Django versions using Oracle backend
- **Mitigation**: Upgrade to latest patch release

### Authentication and Authorization Best Practices

```python
# settings.py
REST_FRAMEWORK = {
    # Use JWT for stateless authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    # Require authentication by default
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    # Throttling to prevent brute-force
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
}
```

### Additional Security Measures
- **HTTPS only**: Set SECURE_SSL_REDIRECT=True in production
- **CSRF tokens**: Enabled by default for session auth
- **Secret key**: Never commit SECRET_KEY to version control
- **Input validation**: Validate all serializer fields with appropriate validators
- **SQL mode**: Use STRICT_TRANS_TABLES to prevent data truncation attacks

## 6. Pagination, Filtering, and Query Optimization

### Pagination Strategy Selection

**PageNumberPagination** (default):
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}
```
- **Use case**: Small to medium datasets (<100k records)
- **Performance**: Degrades with page number (OFFSET becomes expensive)
- **Pros**: Intuitive, supports page numbers
- **Cons**: Slow for deep pagination

**LimitOffsetPagination**:
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_LIMIT': 100,
}
```
- **Use case**: Database-style querying, flexible client control
- **Performance**: Similar degradation to PageNumberPagination
- **Pros**: Flexible limit/offset control
- **Cons**: Slow for large offsets

**CursorPagination** (recommended for large datasets):
```python
from rest_framework.pagination import CursorPagination

class ArticleCursorPagination(CursorPagination):
    page_size = 100
    ordering = '-created_at'  # Must be unique, unchanging field
    cursor_query_param = 'cursor'

class ArticleViewSet(viewsets.ModelViewSet):
    pagination_class = ArticleCursorPagination
```
- **Use case**: Large datasets (>100k records), time-series data
- **Performance**: Constant time, does not degrade with dataset size
- **Pros**: No duplicate items, consistent performance, prevents pagination anomalies
- **Cons**: No page numbers, cannot jump to arbitrary pages, requires unique ordering field

### Performance Comparison
- **PageNumberPagination**: O(n) where n = offset (slows linearly)
- **CursorPagination**: O(1) constant time (always fast)

### Filtering Best Practices

```python
from django_filters import rest_framework as filters

class ArticleFilter(filters.FilterSet):
    # Use exact match for indexed fields
    status = filters.NumberFilter(field_name='status', lookup_expr='exact')

    # Avoid iexact on MySQL (uses LIKE)
    # title = filters.CharFilter(field_name='title', lookup_expr='iexact')  # SLOW
    title = filters.CharFilter(field_name='title', lookup_expr='exact')    # FAST

    # Date range filtering (ensure created_at is indexed)
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Article
        fields = ['status', 'title', 'created_after', 'created_before']

class ArticleViewSet(viewsets.ModelViewSet):
    filterset_class = ArticleFilter
```

### Query Optimization Checklist
- Index all filtered fields in database
- Use integer comparisons over string comparisons
- Avoid `iexact`, `icontains`, `istartswith` on MySQL (case-insensitive, uses LIKE)
- Add `order_by()` to ViewSet querysets for consistent pagination
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many and reverse foreign keys
- Override count() method in custom paginators for large tables
- Use `.values()` or `.values_list()` when full objects not needed

## 7. Migration Management and Schema Best Practices

### MySQL-Specific Migration Considerations

**No DDL Transactions**: MySQL cannot roll back failed migrations.
```python
# migrations/0001_initial.py
from django.db import migrations

class Migration(migrations.Migration):
    # MySQL ignores atomic parameter for DDL
    atomic = False  # Document this limitation

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('title', models.CharField(max_length=200)),
            ],
        ),
    ]
```

**RunPython with MySQL**:
```python
from django.db import migrations

def forward(apps, schema_editor):
    if schema_editor.connection.vendor != 'mysql':
        return
    # MySQL-specific data migration

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(forward, atomic=False),
    ]
```

### Best Practices

**1. Keep Migrations Small and Focused**
- One logical change per migration
- Easier to debug and rollback manually if needed

**2. Test Migrations on Staging**
```bash
# Create migration
python manage.py makemigrations

# Review SQL before applying
python manage.py sqlmigrate app_name 0001

# Test on staging database
python manage.py migrate --database=staging

# Apply to production
python manage.py migrate
```

**3. Handle Index Size Limitations**
```python
class Article(models.Model):
    # BAD: Combined index too large for MySQL
    # long_field_1 = models.CharField(max_length=255)
    # long_field_2 = models.CharField(max_length=255)
    # class Meta:
    #     indexes = [models.Index(fields=['long_field_1', 'long_field_2'])]

    # GOOD: Individual indexes or shorter fields
    long_field_1 = models.CharField(max_length=255, db_index=True)
    long_field_2 = models.CharField(max_length=100, db_index=True)
```

**4. Zero-Downtime Migrations**
```python
# Step 1: Add new nullable field
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='article',
            name='new_field',
            field=models.CharField(max_length=200, null=True),
        ),
    ]

# Step 2: Populate data (separate deployment)
# Step 3: Make field non-nullable (separate deployment)
```

**5. Avoid Renaming Tables/Columns in Production**
- Use db_table and db_column to decouple model names from database schema
- Renaming requires table locks and can cause downtime

### MySQL 8.0 Performance Improvements
- Instant DDL operations for many schema changes (no table rebuild)
- Reduced locking for ADD COLUMN, DROP COLUMN operations
- Still cannot guarantee zero interruption

## 8. Testing Strategies for DRF with MySQL

### Test Database Configuration

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # ... production settings
        'TEST': {
            'NAME': 'test_database',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    },
}
```

### Testing Stack Recommendations

**pytest-django + Factory Boy + Faker**

**Installation**:
```bash
pip install pytest pytest-django factory-boy faker
```

**pytest.ini**:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings
python_files = tests.py test_*.py *_tests.py
addopts = --nomigrations --reuse-db
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py
├── factories.py
├── test_models.py
├── test_serializers.py
├── test_views.py
└── test_integration.py
```

### Factory Pattern

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()

class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = 'myapp.Article'

    title = factory.Faker('sentence', nb_words=6)
    slug = factory.Faker('slug')
    status = 1
    created_at = factory.Faker('date_time_this_year')

class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'auth.User'

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Faker('email')
```

### Test Examples

**Model Tests**:
```python
# tests/test_models.py
import pytest
from tests.factories import ArticleFactory

@pytest.mark.django_db
class TestArticleModel:
    def test_article_creation(self):
        article = ArticleFactory()
        assert article.id is not None
        assert article.title is not None

    def test_article_slug_unique(self):
        article1 = ArticleFactory(slug='test-slug')
        with pytest.raises(Exception):
            ArticleFactory(slug='test-slug')
```

**Serializer Tests**:
```python
# tests/test_serializers.py
import pytest
from myapp.serializers import ArticleSerializer
from tests.factories import ArticleFactory

@pytest.mark.django_db
class TestArticleSerializer:
    def test_serializer_with_valid_data(self):
        article = ArticleFactory()
        serializer = ArticleSerializer(article)
        assert 'title' in serializer.data
        assert serializer.data['title'] == article.title

    def test_serializer_validation(self):
        data = {'title': '', 'slug': 'test'}
        serializer = ArticleSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
```

**ViewSet/API Tests**:
```python
# tests/test_views.py
import pytest
from rest_framework.test import APIClient
from tests.factories import ArticleFactory, UserFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestArticleViewSet:
    def test_list_articles(self, authenticated_client):
        ArticleFactory.create_batch(5)
        response = authenticated_client.get('/api/articles/')
        assert response.status_code == 200
        assert len(response.data['results']) == 5

    def test_create_article(self, authenticated_client):
        data = {
            'title': 'Test Article',
            'slug': 'test-article',
            'status': 1,
        }
        response = authenticated_client.post('/api/articles/', data)
        assert response.status_code == 201
        assert response.data['title'] == 'Test Article'

    def test_unauthorized_access(self, api_client):
        response = api_client.get('/api/articles/')
        assert response.status_code == 401
```

### MySQL-Specific Testing Considerations

**MyISAM vs InnoDB**:
```python
# TransactionTestCase required for MyISAM (not recommended)
from django.test import TransactionTestCase

class MyISAMTest(TransactionTestCase):
    # Data deleted at end, not rolled back
    pass
```

**Test Performance Optimization**:
```python
# conftest.py
import pytest

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Reuse test database across sessions"""
    with django_db_blocker.unblock():
        # Setup code
        pass

# Use --reuse-db flag
# pytest --reuse-db --nomigrations
```

### Coverage and Quality
```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=myapp --cov-report=html

# Aim for >80% coverage on critical paths
```

## 9. Django 4.x/5.x and DRF 3.x Updates

### Django 5.2 (Latest, 2024)
**MySQL Improvements**:
- **utf8mb4 default charset**: Full Unicode support including emojis
- **Geospatial support**: coveredby and covers lookups now supported on MySQL
- **AlterConstraint operation**: Modify constraints without drop/recreate

**Other Features**:
- Async authentication backends
- reverse() and reverse_lazy() accept query and fragment arguments
- Enhanced form accessibility with aria-describedby

### Django 5.1 (August 2024)
**MySQL Improvements**:
- **Collect supported on MySQL 8.0.24+**: Geospatial aggregation

**Other Features**:
- **Native connection pooling for PostgreSQL only** (not MySQL)
- LoginRequiredMiddleware for app-wide authentication
- {% query_string %} template tag for URL parameter manipulation
- Enhanced password hashing with updated PBKDF2 and Scrypt parameters

### Django 5.0 (December 2023)
**Breaking Changes**:
- Dropped support for Python 3.8 and 3.9
- Dropped support for PostgreSQL < 12

**Features**:
- Facet filtering support
- Database-computed default values
- Simplified templates for form field rendering

### Django REST Framework 3.15 (March 2024)
**Features**:
- **Full Django 5.0 and Python 3.12 support**
- ModelSerializer generates validators for UniqueConstraint
- Dependency on pytz removed (uses ZoneInfo)
- Quoted phrase search support (phrases with spaces)
- Null-character validation in search

**Minimum Requirements** (DRF 3.15):
- Django 3.0+
- Python 3.6+

### Recommended Versions for New Projects (October 2025)
- **Django**: 5.2.x (latest stable)
- **DRF**: 3.15.x
- **MySQL**: 8.0.30+
- **Python**: 3.11 or 3.12
- **mysqlclient**: 2.2.0+

### Upgrade Path from Django 4.2 LTS
1. Review deprecation warnings in Django 4.2
2. Update third-party packages for Django 5.x compatibility
3. Test on Django 5.0 with warnings enabled
4. Address breaking changes (pytz → zoneinfo, etc.)
5. Upgrade to Django 5.1, then 5.2
6. Update DRF to 3.15

## 10. Production Deployment Considerations

### Recommended Production Stack

**Application Server**: Gunicorn (preferred) or uWSGI
**Reverse Proxy**: Nginx
**Containerization**: Docker
**Database**: MySQL 8.0.30+

### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"  # Use "uvicorn.workers.UvicornWorker" for ASGI
worker_connections = 1000
max_requests = 1000  # Restart workers after 1000 requests
max_requests_jitter = 100
timeout = 30
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

**Worker Calculation**:
```
workers = (2 * CPU_cores) + 1
```

**Database Connection Sizing**:
```
CONN_MAX_AGE should be less than MySQL wait_timeout (default 28800s)
Total connections = workers * threads_per_worker
Ensure MySQL max_connections > total_connections * 1.5
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "myproject.wsgi:application", "-c", "gunicorn.conf.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydatabase
      MYSQL_USER: myuser
      MYSQL_PASSWORD: mypassword
    volumes:
      - mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password
             --character-set-server=utf8mb4
             --collation-server=utf8mb4_unicode_ci
    ports:
      - "3306:3306"

  web:
    build: .
    command: gunicorn myproject.wsgi:application -c gunicorn.conf.py
    volumes:
      - .:/app
      - static_volume:/app/static
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=mysql://myuser:mypassword@db:3306/mydatabase

  nginx:
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/static
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  mysql_data:
  static_volume:
```

### Nginx Configuration

```nginx
# nginx.conf
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name example.com;

    client_max_body_size 20M;

    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Production Django Settings

```python
# settings/production.py
import os

DEBUG = False
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 600,
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
```

### Monitoring and Observability

**Database Connection Monitoring**:
```sql
-- Check active connections
SHOW PROCESSLIST;

-- Check max connections
SHOW VARIABLES LIKE 'max_connections';

-- Check current connection count
SHOW STATUS LIKE 'Threads_connected';
```

**Application Performance Monitoring**:
- **Django Silk**: Development profiling
- **Sentry**: Error tracking and performance monitoring
- **New Relic/DataDog**: APM and infrastructure monitoring
- **Prometheus + Grafana**: Metrics and dashboards

### Deployment Checklist

- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS and security headers
- [ ] Set SECRET_KEY from environment variable
- [ ] Configure production database with connection pooling
- [ ] Set up static file serving (Nginx/CDN)
- [ ] Configure logging to files/external service
- [ ] Set up database backups (automated, tested)
- [ ] Configure error monitoring (Sentry)
- [ ] Set up health check endpoints
- [ ] Load test application under expected traffic
- [ ] Plan and test migration rollback procedures
- [ ] Configure firewall rules (database access)
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure CORS if needed
- [ ] Test database connection limits under load
- [ ] Set up monitoring and alerting
- [ ] Document deployment process and runbooks

### Performance Benchmarks

**Target Metrics**:
- API response time (p95): <200ms
- Database query time (p95): <50ms
- Concurrent users: 1000+
- Requests per second: 100+

**Optimization Priority**:
1. Database query optimization (biggest impact)
2. Serializer performance (6x improvement possible)
3. Pagination strategy (constant vs linear time)
4. Connection pooling (50-70ms reduction)
5. Caching strategy (Redis/Memcached)

## Action Items

1. **Immediate Setup**:
   - Configure MySQL 8.0+ with utf8mb4 charset and InnoDB engine
   - Set CONN_MAX_AGE=600 for persistent connections
   - Enable STRICT_TRANS_TABLES in MySQL OPTIONS
   - Upgrade to Django 5.2 and DRF 3.15 for latest features

2. **Performance Optimization**:
   - Audit all ViewSets for select_related/prefetch_related usage
   - Mark all read-only serializer fields explicitly
   - Implement CursorPagination for large datasets (>100k records)
   - Replace iexact/icontains filters with exact comparisons
   - Index all frequently filtered/ordered fields

3. **Security Hardening**:
   - Upgrade Django to latest patch version (address CVE-2024-42005)
   - Implement JWT authentication with djangorestframework-simplejwt
   - Configure rate limiting/throttling on authentication endpoints
   - Enable all production security settings (SSL, HSTS, etc.)
   - Review raw SQL queries for injection vulnerabilities

4. **Testing Infrastructure**:
   - Set up pytest-django with Factory Boy
   - Create factories for all models
   - Implement test coverage for serializers, views, and models
   - Configure --reuse-db and --nomigrations for faster tests
   - Aim for >80% test coverage

5. **Production Deployment**:
   - Containerize with Docker using python:3.12-slim base
   - Configure Gunicorn with (2*CPU+1) workers
   - Set up Nginx reverse proxy with static file serving
   - Implement comprehensive logging and monitoring
   - Create database backup and restore procedures

6. **Migration Strategy**:
   - Test all migrations on staging environment first
   - Use sqlmigrate to review SQL before production application
   - Plan zero-downtime migrations for schema changes
   - Document rollback procedures for critical migrations
   - Monitor migration performance on large tables

## Sources

- [Django 5.2 Official Documentation - Databases](https://docs.djangoproject.com/en/5.2/ref/databases/) - MySQL configuration, limitations, and settings
- [Django 5.1 Release Notes](https://docs.djangoproject.com/en/5.1/releases/5.1/) - Connection pooling, new features (August 2024)
- [Django 5.2 Release Notes](https://docs.djangoproject.com/en/5.2/releases/5.2/) - utf8mb4 default, geospatial improvements (2024)
- [DRF 3.15 Announcement](https://www.django-rest-framework.org/community/3.15-announcement/) - Latest features and Django 5.0 support (March 2024)
- [Improve Serialization Performance in DRF - Haki Benita](https://hakibenita.com/django-rest-framework-slow) - Performance benchmarks and optimization techniques
- [DRF Pagination Documentation](https://www.django-rest-framework.org/api-guide/pagination/) - Pagination strategies and best practices
- [Django Security Documentation](https://docs.djangoproject.com/en/5.2/topics/security/) - SQL injection prevention, CSRF, XSS protection
- [Django REST Framework Performance Part 2](https://smhk.net/note/2023/09/django-rest-framework-performance-part-2/) - Advanced optimization techniques (2023)
- [Optimizing DRF Pagination for Large Datasets - Poespas Blog](https://blog.poespas.me/posts/2024/05/20/optimizing-django-rest-framework-pagination/) - Cursor pagination strategies (May 2024)
- [Cut Database Latency with Native Connection Pooling - Saurabh Kumar](https://saurabh-kumar.com/articles/2025/06/cut-django-database-latency-by-50-70ms-with-native-connection-pooling/) - Connection pooling performance impact (2025)
- [Django SQL Injection Guide - StackHawk](https://www.stackhawk.com/blog/sql-injection-prevention-django/) - SQL injection prevention and CVE-2024-42005 details
- [Django Migrations Documentation](https://docs.djangoproject.com/en/5.2/topics/migrations/) - Migration best practices and MySQL considerations
- [Streamlining Django Testing - Jonas Tischer](https://jonastischer.com/blog/streamlining-django-testing-with-pytest-factory-boy-and-fixtures) - pytest and Factory Boy setup (February 2024)
- [Dockerizing Django with Postgres, Gunicorn, and Nginx - TestDriven.io](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/) - Production deployment architecture
- [How to Dockerize Django App - Docker Official Blog](https://www.docker.com/blog/how-to-dockerize-django-app/) - Docker containerization guide (January 2025)

## Caveats

This research focuses on Django 5.x and DRF 3.15 as of October 2025. Connection pooling recommendations are limited to PostgreSQL for native Django support; MySQL requires third-party solutions or persistent connections. Performance benchmarks are environment-dependent and should be validated in your specific infrastructure. Security vulnerabilities are current as of the search date; always check for latest CVEs before deployment. Some optimization techniques (like removing serializers entirely) trade developer experience for performance and may not be suitable for all teams. Testing strategies assume MySQL with InnoDB; MyISAM has different transaction behavior. Production deployment recommendations are general; specific cloud platforms (AWS RDS, Google Cloud SQL) may have additional optimization opportunities not covered here.
