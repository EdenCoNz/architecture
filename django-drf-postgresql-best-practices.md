# Django REST Framework with PostgreSQL: Comprehensive Best Practices Guide

**Date**: 2025-10-19
**Purpose**: Establish comprehensive guidelines for developing Django REST Framework applications with PostgreSQL backend, ensuring optimal performance, security, and maintainability.

---

## Executive Summary

This guide synthesizes current best practices (2024-2025) for building Django REST Framework (DRF) applications with PostgreSQL. Key findings include Django 5.1's native connection pooling support, the critical importance of select_related/prefetch_related for query optimization, cursor-based pagination for large datasets, and zero-downtime migration strategies. All recommendations are based on official documentation, peer-reviewed sources, and established community practices.

---

## 1. Database Configuration and Connection Pooling

### Django 5.1 Native Connection Pooling (New in 2024)

Django 5.1 introduces built-in connection pool support for PostgreSQL, reducing the need for external tools.

**Configuration Example:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # 10 minutes
        'CONN_HEALTH_CHECKS': True,  # Enable connection health checks
        'OPTIONS': {
            'pool': {
                'min_size': 2,
                'max_size': 10,
                'timeout': 30,
            }
            # Or use: 'pool': True  # for defaults
        }
    }
}
```

### CONN_MAX_AGE Best Practices

- **Value**: Set to 0 for request-scoped connections (Django's historical behavior), or None for unlimited persistent connections
- **Production Recommendation**: 300-600 seconds (5-10 minutes)
- **Warning**: If your database terminates idle connections, set CONN_MAX_AGE lower than the database timeout
- **Threading Consideration**: Each thread maintains its own connection; ensure your database supports connections >= worker threads

### PgBouncer for Large-Scale Applications

For applications requiring advanced connection pooling, PgBouncer remains a robust solution.

**Django Configuration for PgBouncer:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'pgbouncer',  # PgBouncer host
        'PORT': '6432',       # PgBouncer port
        'DISABLE_SERVER_SIDE_CURSORS': True,  # Required for transaction mode
    }
}
```

**PgBouncer Pool Modes:**
- **Session Mode**: Assigns connection for entire session duration (safest for Django)
- **Transaction Mode**: Default mode; requires `DISABLE_SERVER_SIDE_CURSORS = True`
- **Statement Mode**: Not recommended for Django

**Key PgBouncer Settings:**
- `default_pool_size`: 20-25 (lower than max_client_conn)
- `max_client_conn`: 100-200 (based on application needs)
- `pool_mode`: transaction or session

---

## 2. Model Design and PostgreSQL-Specific Field Types

### PostgreSQL-Specific Fields (django.contrib.postgres.fields)

```python
from django.contrib.postgres.fields import (
    ArrayField, JSONField, HStoreField, DateTimeRangeField
)
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)

    # ArrayField - use callable for default
    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,  # NOT default=[] (mutable default issue)
        blank=True
    )

    # JSONField - for structured data
    metadata = models.JSONField(default=dict, blank=True)

    # HStoreField - key-value pairs
    attributes = HStoreField(default=dict, blank=True)

    # Range fields
    availability = DateTimeRangeField(null=True, blank=True)
```

### ArrayField Best Practices

- **Always use callable defaults**: `default=list` NOT `default=[]`
- **Benefits**: Flexibility, efficiency (reduces multiple rows), simpler queries
- **Limitations**: Less normalized, limited complex querying

### JSONField Best Practices

- **Use Case**: Structured, semi-structured data that doesn't require frequent querying
- **Indexing**: Use GIN indexes for better query performance (see Section 4)
- **Querying**: PostgreSQL 10+ supports full-text search on JSONB
- **Caveat**: JSON path lookups conflict with Django's double-underscore syntax; use annotations to work around this

---

## 3. Query Optimization and ORM Best Practices

### The N+1 Query Problem

**Problem**: Accessing related objects in a loop generates N additional queries.

**Solution**: Use `select_related()` and `prefetch_related()`

### select_related() - For ForeignKey and OneToOne

Uses SQL JOIN to retrieve related objects in a single query.

```python
# BAD: N+1 queries
articles = Article.objects.all()
for article in articles:
    print(article.author.name)  # Triggers query per article

# GOOD: 1 query with JOIN
articles = Article.objects.select_related('author')
for article in articles:
    print(article.author.name)  # No additional queries
```

### prefetch_related() - For ManyToMany and Reverse ForeignKey

Performs separate lookup for each relationship, joins in Python.

```python
# BAD: N+1 queries
authors = Author.objects.all()
for author in authors:
    for book in author.books.all():  # Query per author
        print(book.title)

# GOOD: 2 queries total
authors = Author.objects.prefetch_related('books')
for author in authors:
    for book in author.books.all():  # No additional queries
        print(book.title)
```

### Combining Both Methods

```python
# Fetch authors with their books and each book's publisher
authors = Author.objects.select_related('hometown').prefetch_related(
    'books__publisher'
)
```

### Using Prefetch Object for Advanced Control

```python
from django.db.models import Prefetch

# Prefetch with custom queryset
authors = Author.objects.prefetch_related(
    Prefetch(
        'books',
        queryset=Book.objects.select_related('publisher').filter(published=True)
    )
)
```

### Django 4.1+ Iterator Support

Since Django 4.1, prefetch_related() works with iterator() when chunk_size is provided:

```python
queryset = Author.objects.prefetch_related('books').iterator(chunk_size=100)
```

### only() and defer() for Field Selection

```python
# Load only specific fields
articles = Article.objects.only('title', 'published_date')

# Defer loading large fields
articles = Article.objects.defer('content', 'raw_data')
```

### values() and values_list() for Performance-Critical Views

For maximum performance, bypass serializers entirely:

```python
# Instead of serializing queryset
data = Article.objects.values('id', 'title', 'author__name')
# Returns: [{'id': 1, 'title': 'Article 1', 'author__name': 'John'}, ...]
```

**Performance Gain**: 50-70% faster than ModelSerializer for read-only data.

---

## 4. Database Indexing Strategies

### Standard B-Tree Indexes

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)  # Automatically indexed

    class Meta:
        indexes = [
            models.Index(fields=['published_date', 'status']),
            models.Index(fields=['-created_at']),  # Descending
        ]
```

### PostgreSQL-Specific Indexes

```python
from django.contrib.postgres.indexes import GinIndex, GistIndex, BrinIndex
from django.contrib.postgres.fields import ArrayField, JSONField

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    tags = ArrayField(models.CharField(max_length=50))
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # GIN index for full-text search
            GinIndex(
                fields=['description'],
                name='product_description_gin_idx',
                opclasses=['gin_trgm_ops']
            ),
            # GIN index for ArrayField
            GinIndex(fields=['tags'], name='product_tags_idx'),
            # GIN index for JSONField with specific operator class
            GinIndex(
                fields=['metadata'],
                name='product_metadata_idx',
                opclasses=['jsonb_path_ops']
            ),
            # BRIN index for time-series data
            BrinIndex(fields=['created_at'], name='product_created_brin_idx'),
        ]
```

### Index Type Selection Guide

| Index Type | Best For | Performance Characteristics |
|-----------|----------|----------------------------|
| **B-Tree** | Exact matches, ranges, sorting | Default; good all-around performance |
| **GIN** | Full-text search, ArrayField, JSONField | 3x faster lookups than GiST; 3x slower build; 2-3x larger |
| **GiST** | Spatial data, full-text search (alternative) | Faster builds; smaller size |
| **BRIN** | Time-series, append-only data | Extremely small; best for sorted data |
| **Hash** | Simple equality | Limited use; only equality comparisons |

### GIN Index Configuration

```python
GinIndex(
    fields=['field_name'],
    fastupdate=True,  # Enable fast updates (default)
    gin_pending_list_limit=4096  # KB for pending list
)
```

### Full-Text Search Index with Trigram

Requires `pg_trgm` extension:

```sql
-- Enable extension (run as migration)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

```python
from django.contrib.postgres.indexes import GinIndex

class Article(models.Model):
    content = models.TextField()

    class Meta:
        indexes = [
            GinIndex(
                fields=['content'],
                name='article_content_trgm_idx',
                opclasses=['gin_trgm_ops']
            )
        ]
```

---

## 5. Transaction Management and Database Isolation Levels

### Default Isolation Level

Django and PostgreSQL both default to **READ COMMITTED** isolation level.

### ATOMIC_REQUESTS Configuration

Enable database-level transactions for all views:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... other settings
        'ATOMIC_REQUESTS': True,
    }
}
```

**Behavior**:
- Starts transaction before calling view function
- Commits if response produced successfully
- Rolls back if view raises exception

**Performance Impact**: Adds overhead; use judiciously based on traffic patterns.

### Manual Transaction Control

```python
from django.db import transaction

# Decorator
@transaction.atomic
def create_order(request):
    order = Order.objects.create(user=request.user)
    OrderItem.objects.create(order=order, product=product)
    return order

# Context manager
def process_payment(order_id):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order_id)
        order.status = 'paid'
        order.save()
        send_confirmation_email(order)
```

### Custom Isolation Levels with django-pgtransaction

Install: `pip install django-pgtransaction`

```python
import pgtransaction

# Serializable isolation
@pgtransaction.atomic(isolation_level=pgtransaction.SERIALIZABLE)
def transfer_funds(from_account, to_account, amount):
    from_account.balance -= amount
    from_account.save()
    to_account.balance += amount
    to_account.save()

# Available levels:
# - pgtransaction.READ_COMMITTED
# - pgtransaction.REPEATABLE_READ
# - pgtransaction.SERIALIZABLE
```

### Database Configuration for Isolation Levels

Django 5.0+ supports configuring default isolation level:

```python
from django.db.backends.postgresql.psycopg_any import IsolationLevel

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... other settings
        'OPTIONS': {
            'isolation_level': IsolationLevel.SERIALIZABLE,
        }
    }
}
```

### Best Practices

1. **Use READ COMMITTED** for most general-purpose queries
2. **Use REPEATABLE READ** when you need consistent reads within a transaction
3. **Use SERIALIZABLE** for critical financial transactions (higher overhead)
4. **Always use select_for_update()** for row-level locking when updating contested data
5. **Keep transactions short** to minimize lock contention

---

## 6. PostgreSQL-Specific Features with Django

### Full-Text Search

```python
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank
)

# Basic full-text search
articles = Article.objects.annotate(
    search=SearchVector('title', 'content')
).filter(search='django')

# Weighted search (title more important than content)
articles = Article.objects.annotate(
    search=SearchVector('title', weight='A') + SearchVector('content', weight='B')
).filter(search=SearchQuery('django'))

# Ranked search results
articles = Article.objects.annotate(
    search=SearchVector('title', 'content'),
    rank=SearchRank(SearchVector('title', 'content'), SearchQuery('django'))
).filter(search='django').order_by('-rank')
```

### Full-Text Search on JSONField

**Challenge**: SearchVector with JSONField may generate incorrect stem words.

**Solution**: Use annotations before applying SearchVector:

```python
from django.db.models import F
from django.contrib.postgres.search import SearchVector

# Annotate JSON path first
products = Product.objects.annotate(
    description_text=F('metadata__description')
).annotate(
    search=SearchVector('description_text')
).filter(search='keyword')
```

### Stored Procedures and Triggers

Django doesn't natively support stored procedures/triggers, but you can use:

**Option 1: django-pgtrigger** (Recommended)

```python
import pgtrigger

class Comment(models.Model):
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        triggers = [
            pgtrigger.Protect(
                name='protect_deletes',
                operation=pgtrigger.Delete
            )
        ]
```

**Option 2: Raw SQL in Migrations**

```python
from django.db import migrations

def create_trigger(apps, schema_editor):
    schema_editor.execute("""
        CREATE OR REPLACE FUNCTION update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER update_article_timestamp
        BEFORE UPDATE ON myapp_article
        FOR EACH ROW EXECUTE FUNCTION update_timestamp();
    """)

def drop_trigger(apps, schema_editor):
    schema_editor.execute("""
        DROP TRIGGER IF EXISTS update_article_timestamp ON myapp_article;
        DROP FUNCTION IF EXISTS update_timestamp();
    """)

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(create_trigger, drop_trigger),
    ]
```

**Option 3: django-plpy** (for PL/Python)

For Python stored procedures within PostgreSQL.

---

## 7. Performance Optimization Techniques

### Query Analysis with EXPLAIN

```python
# Django ORM EXPLAIN support
queryset = Article.objects.filter(status='published').select_related('author')
print(queryset.explain())

# With ANALYZE (actually runs query)
print(queryset.explain(analyze=True))

# With additional options
print(queryset.explain(analyze=True, verbose=True, buffers=True))
```

### pg_stat_statements Extension

Enable in PostgreSQL for query performance tracking:

```sql
-- postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
```

**Usage**:
```sql
-- View most time-consuming queries
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

**Django Integration**: Use `django-pg-stat-statements` package

```bash
pip install django-pg-stat-statements
```

Add to INSTALLED_APPS and view statistics in Django admin under "PostgreSQL Stat Statements".

### pg_stat_monitor (Advanced Alternative)

Provides enhanced insights over pg_stat_statements:
- Captures actual parameters in queries (not just placeholders)
- Includes actual execution plans
- Detailed grouping by client address, application name
- Better for debugging and performance analysis

### auto_explain Module

Automatically run EXPLAIN on slow queries:

```sql
-- postgresql.conf
session_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = 1000  # Log queries > 1 second
auto_explain.log_analyze = true
auto_explain.log_buffers = true
```

### pgMustard Integration

Tool for visualizing EXPLAIN output with optimization recommendations:

1. Run `queryset.explain(analyze=True, buffers=True)`
2. Copy output to https://www.pgmustard.com/
3. Review ranked optimization opportunities (rated out of 5 stars)

---

## 8. Serializer Optimization for Database Queries

### Use select_related() and prefetch_related() in Viewsets

```python
from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'comments__user'
        )
```

### Read-Only Serializers

Make non-writable fields read-only to improve performance:

```python
class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author_name']
        read_only_fields = ['author_name', 'created_at']
```

**Performance Gain**: Serialization time reduced by 30-50% for read-only ModelSerializer.

### SerializerMethodField Optimization

```python
class ArticleSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        # BAD: Triggers query per object
        return obj.comments.count()

    class Meta:
        model = Article
        fields = ['id', 'title', 'comment_count']

# SOLUTION 1: Annotate in viewset
class ArticleViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article.objects.annotate(
            comment_count=Count('comments')
        )

class ArticleSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)

# SOLUTION 2: Use prefetch_related
class ArticleViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article.objects.prefetch_related('comments')

class ArticleSerializer(serializers.ModelSerializer):
    def get_comment_count(self, obj):
        return len(obj.comments.all())  # No query; uses prefetched data
```

### Performance-Critical Endpoints: Skip Serializers

For maximum performance, use `.values()` directly:

```python
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def article_list_fast(request):
    data = Article.objects.values(
        'id', 'title', 'author__name', 'published_date'
    )
    return Response(list(data))
```

**Performance**: 50-70% faster than ModelSerializer.

**Trade-off**: Less flexibility, no validation/transformation.

---

## 9. API Pagination Strategies with Large Datasets

### Pagination Types Comparison

| Type | Best For | Performance | Use Case |
|------|----------|-------------|----------|
| **PageNumberPagination** | Small-medium datasets | Degrades with offset | User-facing lists |
| **LimitOffsetPagination** | API flexibility | Degrades with offset | Client-controlled paging |
| **CursorPagination** | Large datasets | Fixed-time (doesn't slow) | Infinite scroll, feeds |

### PageNumberPagination (Default)

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50
}
```

**URLs**: `?page=1`, `?page=2`

**Limitation**: Slow for large offsets (page 1000 requires scanning 50,000 rows).

### LimitOffsetPagination

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50
}
```

**URLs**: `?limit=50&offset=100`

**Limitation**: Same performance issue as PageNumberPagination.

### CursorPagination (Recommended for Large Datasets)

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 50
}
```

**Advantages**:
- Fixed-time performance regardless of dataset size
- No duplicate items when new records inserted during pagination
- Efficient for infinite scroll patterns

**Requirements**:
- Requires unique, unchanging ordering field (typically timestamp)
- Ordering field must have database index
- Ordering field should be set once on creation

**Limitations**:
- Only forward/reverse navigation (no arbitrary page jumping)
- Cannot navigate to arbitrary positions

**Custom Implementation**:
```python
from rest_framework.pagination import CursorPagination

class ArticleCursorPagination(CursorPagination):
    page_size = 50
    ordering = '-created_at'  # Must be unique and indexed
    cursor_query_param = 'cursor'

class ArticleViewSet(viewsets.ModelViewSet):
    pagination_class = ArticleCursorPagination

    def get_queryset(self):
        return Article.objects.select_related('author')
```

### Optimizing Count Queries

PageNumberPagination and LimitOffsetPagination perform COUNT(*) queries which are slow on large tables.

**Solution 1: Disable count**
```python
class FastPageNumberPagination(PageNumberPagination):
    django_paginator_class = DjangoPaginator

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
```

**Solution 2: Cache count**
```python
from django.core.cache import cache

def get_article_count():
    count = cache.get('article_count')
    if count is None:
        count = Article.objects.count()
        cache.set('article_count', count, 300)  # 5 minutes
    return count
```

---

## 10. Database Migration Best Practices

### Zero-Downtime Migration Principles

1. **Test migrations in staging** that mirrors production
2. **Use `sqlmigrate` to preview** SQL before running
3. **Break large migrations** into smaller steps
4. **Avoid long-running transactions**
5. **Use concurrent operations** when possible

### Tools for Zero-Downtime Migrations

**django-pg-zero-downtime-migrations**
```bash
pip install django-pg-zero-downtime-migrations
```

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django_pg_zero_downtime_migrations.backends.postgresql',
        # ... other settings
    }
}
```

**zero-downtime-migrations (Yandex)**
```bash
pip install zero-downtime-migrations
```

Provides helper functions to ensure PostgreSQL-compatible zero-downtime migrations.

### Common Zero-Downtime Patterns

#### Adding Non-Nullable Fields (Multi-Step)

**❌ DON'T: Single step causes table lock**
```python
class Article(models.Model):
    content = models.TextField()  # Adding this in one step = downtime
```

**✅ DO: Multi-step approach**

**Step 1: Add as nullable**
```python
# migration 0001
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='article',
            name='content',
            field=models.TextField(null=True, blank=True),
        ),
    ]
```

**Step 2: Backfill data**
```python
# migration 0002
def backfill_content(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    Article.objects.filter(content__isnull=True).update(
        content='Default content'
    )

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(backfill_content, migrations.RunPython.noop),
    ]
```

**Step 3: Make non-nullable**
```python
# migration 0003
class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(),
        ),
    ]
```

#### Creating Indexes Concurrently

**❌ DON'T: Standard index creation locks table**
```python
class Meta:
    indexes = [
        models.Index(fields=['email'])  # Locks table during creation
    ]
```

**✅ DO: Use concurrent index creation**
```python
from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models

class Migration(migrations.Migration):
    atomic = False  # Required for concurrent operations

    operations = [
        AddIndexConcurrently(
            model_name='user',
            index=models.Index(fields=['email'], name='user_email_idx'),
        ),
    ]
```

#### Removing Fields (Backward-Compatible)

**Step 1: Stop writing to field** (deploy code change)

**Step 2: Remove from model** (wait for old code to be fully replaced)

**Step 3: Remove from database** (use SeparateDatabaseAndState)
```python
from django.db import migrations

class Migration(migrations.Migration):
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='article',
                    name='old_field',
                ),
            ],
            database_operations=[
                # Actual column drop happens later
            ],
        ),
    ]
```

### Blue-Green Deployment Pattern

1. Deploy new code version (Blue) alongside old (Green)
2. Run migrations on Blue environment
3. Switch traffic to Blue
4. Retire Green after validation

### Migration Performance Tips

1. **Batch large updates**: Update rows in chunks to avoid long transactions
2. **Use `RunSQL` for complex operations**: Direct SQL can be more efficient
3. **Add indexes before constraints**: Speeds up constraint validation
4. **Disable triggers temporarily**: For bulk operations (re-enable after)
5. **Monitor active queries**: Use `pg_stat_activity` during migrations

---

## 11. Connection Pooling Solutions

### Comparison: Native Django 5.1 vs PgBouncer

| Feature | Django 5.1 Native | PgBouncer |
|---------|------------------|-----------|
| **Setup Complexity** | Low (built-in) | Medium (external service) |
| **Scalability** | Good (per-worker) | Excellent (centralized) |
| **Multi-App Support** | No | Yes |
| **Transaction Modes** | Session | Session, Transaction, Statement |
| **Resource Usage** | Higher (per-worker pools) | Lower (shared pool) |
| **Best For** | Single Django app | Multiple apps, microservices |

### Django 5.1 Native Connection Pooling

**Configuration**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypass',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'pool': {
                'min_size': 2,
                'max_size': 10,
                'timeout': 30,
                'max_lifetime': 3600,  # Close connections after 1 hour
                'max_idle': 600,       # Close idle connections after 10 min
            }
        }
    }
}
```

### PgBouncer Configuration

**Installation**:
```bash
sudo apt-get install pgbouncer
```

**pgbouncer.ini**:
```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 200
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3
server_lifetime = 3600
server_idle_timeout = 600
log_connections = 1
log_disconnections = 1
```

**Django Configuration**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypass',
        'HOST': '127.0.0.1',
        'PORT': '6432',  # PgBouncer port
        'DISABLE_SERVER_SIDE_CURSORS': True,  # Required for transaction mode
    }
}
```

### django-postgrespool2 (Alternative)

```bash
pip install django-postgrespool2
```

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_postgrespool',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Recommendation

- **Use Django 5.1 native pooling** for new single-application deployments
- **Use PgBouncer** for:
  - Multi-application environments
  - Legacy Django versions (< 5.1)
  - Need for transaction pooling mode
  - Microservices architecture

---

## 12. Security Best Practices

### SQL Injection Prevention

**Django ORM is Safe by Default**

Django's ORM automatically parameterizes queries, preventing SQL injection.

```python
# ✅ SAFE: ORM parameterizes automatically
articles = Article.objects.filter(author=user_input)

# ✅ SAFE: Raw queries with parameters
Article.objects.raw(
    'SELECT * FROM myapp_article WHERE author = %s',
    [user_input]
)

# ✅ SAFE: Using cursor with parameters
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(
        'SELECT * FROM myapp_article WHERE author = %s',
        [user_input]
    )
```

**Unsafe Patterns to Avoid**:
```python
# ❌ UNSAFE: String formatting
Article.objects.raw(
    f'SELECT * FROM myapp_article WHERE author = "{user_input}"'
)

# ❌ UNSAFE: String concatenation
query = 'SELECT * FROM myapp_article WHERE author = "' + user_input + '"'

# ❌ UNSAFE: extra() with user input
Article.objects.extra(
    where=[f"author = '{user_input}'"]
)
```

### Recent Security Vulnerabilities (2024)

Keep Django updated to address:
- **CVE-2024-27351**: Denial-of-Service vulnerability
- **CVE-2024-24680**: Denial-of-Service vulnerability
- **CVE-2023-46695**: Denial-of-Service vulnerability

**Action**: Run `pip install --upgrade django` regularly.

### Database User Permissions (Defense in Depth)

Create separate PostgreSQL roles with minimal privileges:

```sql
-- Migration role (for running migrations)
CREATE ROLE django_migrator WITH LOGIN PASSWORD 'secure_password';
GRANT CREATE ON DATABASE mydb TO django_migrator;
GRANT ALL PRIVILEGES ON SCHEMA public TO django_migrator;

-- Application role (for runtime queries)
CREATE ROLE django_app WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO django_app;
GRANT USAGE ON SCHEMA public TO django_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO django_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO django_app;

-- Set search path
ALTER ROLE django_app SET search_path TO public;
```

**Django Configuration**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'django_app',  # Restricted runtime user
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}
```

### Additional Security Measures

1. **Use environment variables** for sensitive credentials
2. **Enable SSL connections**:
   ```python
   DATABASES = {
       'default': {
           'OPTIONS': {
               'sslmode': 'require',
               'sslrootcert': '/path/to/ca-cert.pem',
           }
       }
   }
   ```
3. **Implement row-level security** (PostgreSQL 9.5+) for multi-tenant applications
4. **Use Django's built-in CSRF protection** (enabled by default)
5. **Validate and sanitize all user inputs** before processing
6. **Enable logging** for security audit trails

---

## 13. Testing Strategies for Django DRF with PostgreSQL

### Test Database Configuration

**settings_test.py**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',
        'USER': 'test_user',
        'PASSWORD': 'test_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_myapp',
            'CHARSET': 'UTF8',
        }
    }
}
```

### Performance Optimization for Tests

#### 1. Use `--keepdb` Flag

Preserves test database between runs:
```bash
python manage.py test --keepdb
```

**Benefit**: Skips database creation/destruction, saving 30-60 seconds per run.

#### 2. Parallel Test Execution

```bash
# Django unittest
python manage.py test --parallel 4

# pytest-django
pytest -n 4
```

#### 3. RAM Drive for Test Database (Linux/Mac)

**Create RAM disk tablespace in PostgreSQL**:
```sql
CREATE TABLESPACE ramtest LOCATION '/mnt/ramdisk';
```

**Django configuration**:
```python
DATABASES = {
    'default': {
        'TEST': {
            'NAME': 'test_myapp',
            'OPTIONS': {
                'DEFAULT_TABLESPACE': 'ramtest',
            }
        }
    }
}
```

**Benefit**: 50-70% faster test execution.

#### 4. Optimize Test Settings

```python
# settings_test.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Remove unnecessary middleware for tests
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fastest
]

CELERY_TASK_ALWAYS_EAGER = True  # Execute tasks synchronously
CELERY_BROKER_URL = 'memory://'
```

#### 5. Specific Test Directory

```bash
pytest myapp/tests/  # Instead of pytest (searches entire project)
```

### Pytest-Django Configuration

**conftest.py**:
```python
import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',
        'USER': 'test_user',
        'PASSWORD': 'test_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()
```

**Example test**:
```python
import pytest
from myapp.models import Article

@pytest.mark.django_db
def test_create_article(api_client):
    response = api_client.post('/api/articles/', {
        'title': 'Test Article',
        'content': 'Test content'
    })
    assert response.status_code == 201
    assert Article.objects.count() == 1
```

### Testing PostgreSQL-Specific Features

```python
from django.contrib.postgres.search import SearchVector
from django.test import TestCase

class FullTextSearchTest(TestCase):
    def setUp(self):
        Article.objects.create(
            title='Django REST Framework',
            content='Building APIs with Django'
        )

    def test_full_text_search(self):
        results = Article.objects.annotate(
            search=SearchVector('title', 'content')
        ).filter(search='django')

        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Django REST Framework')
```

### Docker + PostgreSQL for Testing

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5432:5432"
    tmpfs:
      - /var/lib/postgresql/data  # RAM-backed storage
```

**Run tests**:
```bash
docker-compose up -d
pytest
docker-compose down
```

### Best Practices Summary

1. **Use `--keepdb`** for local development
2. **Run tests in parallel** for large test suites
3. **Use RAM disk** for maximum speed
4. **Optimize test settings** (minimal middleware, fast password hasher)
5. **Test PostgreSQL-specific features** (full-text search, JSONField, ArrayField)
6. **Use pytest-django** for better test organization
7. **Use Docker** for consistent test environments

---

## 14. Caching Strategies

### Django Cache Framework

Django supports multiple cache backends:
- **Redis** (recommended for production)
- **Memcached**
- **Database caching**
- **File system caching**
- **Local memory caching** (development only)

### Redis Cache Configuration

**Installation**:
```bash
pip install redis
```

**Django 4.0+ (Native Redis Support)**:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'myapp',
        'TIMEOUT': 300,  # 5 minutes default
    }
}
```

### Caching Strategies

#### 1. Per-View Caching

```python
from django.views.decorators.cache import cache_page

# Cache for 15 minutes
@cache_page(60 * 15)
def article_list(request):
    articles = Article.objects.all()
    return render(request, 'articles.html', {'articles': articles})
```

#### 2. Template Fragment Caching

```django
{% load cache %}
{% cache 500 sidebar request.user.username %}
    .. sidebar for logged in user ..
{% endcache %}
```

#### 3. Low-Level Cache API

```python
from django.core.cache import cache

def get_article(article_id):
    cache_key = f'article_{article_id}'
    article = cache.get(cache_key)

    if article is None:
        article = Article.objects.select_related('author').get(id=article_id)
        cache.set(cache_key, article, 300)  # Cache for 5 minutes

    return article
```

#### 4. Database Query Caching with django-cacheops

**Installation**:
```bash
pip install django-cacheops
```

**Configuration**:
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'cacheops',
]

CACHEOPS_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
    'socket_timeout': 3,
}

CACHEOPS = {
    # Automatically cache all queries for Article model for 60 minutes
    'myapp.article': {'ops': 'all', 'timeout': 60*60},

    # Cache only 'get' queries for User model for 15 minutes
    'auth.user': {'ops': ('get',), 'timeout': 60*15},

    # Cache all queries on Tag model for 1 hour
    'myapp.tag': {'ops': 'all', 'timeout': 60*60},

    # Cache specific querysets
    'myapp.*': {'ops': ('fetch', 'get'), 'timeout': 60*5},
}
```

**Features**:
- **Automatic invalidation**: Cache invalidated on model save/delete
- **Granular event-driven invalidation**: Smart cache invalidation based on query structure
- **ORM query caching**: Transparently caches ORM queries

**Manual cache control**:
```python
from cacheops import invalidate_model, invalidate_obj

# Invalidate all Article caches
invalidate_model(Article)

# Invalidate specific object
article = Article.objects.get(id=1)
invalidate_obj(article)
```

#### 5. DRF Response Caching

```python
from rest_framework.decorators import api_view
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Function-based view
@api_view(['GET'])
@cache_page(60 * 15)
def article_list(request):
    articles = Article.objects.all()
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)

# Class-based view
class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

#### 6. Cache Invalidation Strategies

**Time-based expiration**:
```python
cache.set('key', value, 300)  # Expires in 5 minutes
```

**Event-based invalidation**:
```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Article)
def invalidate_article_cache(sender, instance, **kwargs):
    cache_key = f'article_{instance.id}'
    cache.delete(cache_key)
    cache.delete('article_list')  # Invalidate list cache

@receiver(post_delete, sender=Article)
def invalidate_article_list_on_delete(sender, instance, **kwargs):
    cache.delete('article_list')
```

**Cache versioning**:
```python
# Increment version to invalidate all related caches
CACHE_VERSION = 2

cache.set('key', value, 300, version=CACHE_VERSION)
cached_value = cache.get('key', version=CACHE_VERSION)
```

### Redis Cache Patterns

#### 1. Cache-Aside (Lazy Loading)

```python
def get_user_profile(user_id):
    cache_key = f'user_profile_{user_id}'
    profile = cache.get(cache_key)

    if profile is None:
        profile = UserProfile.objects.select_related('user').get(user_id=user_id)
        cache.set(cache_key, profile, 3600)  # 1 hour

    return profile
```

#### 2. Write-Through Cache

```python
def update_user_profile(user_id, data):
    profile = UserProfile.objects.get(user_id=user_id)
    for key, value in data.items():
        setattr(profile, key, value)
    profile.save()

    # Update cache immediately
    cache_key = f'user_profile_{user_id}'
    cache.set(cache_key, profile, 3600)

    return profile
```

#### 3. Cache with Fallback

```python
from django.core.cache import caches

# Use multiple cache layers
default_cache = caches['default']  # Redis
fallback_cache = caches['fallback']  # Memcached or local

def get_cached_value(key):
    value = default_cache.get(key)
    if value is None:
        value = fallback_cache.get(key)
        if value is None:
            value = expensive_computation()
            default_cache.set(key, value, 3600)
            fallback_cache.set(key, value, 3600)
    return value
```

### Performance Monitoring

```python
# Monitor cache hit/miss ratio
import logging

logger = logging.getLogger(__name__)

def get_with_logging(key):
    value = cache.get(key)
    if value is None:
        logger.info(f'Cache MISS: {key}')
    else:
        logger.info(f'Cache HIT: {key}')
    return value
```

### Best Practices

1. **Use Redis for production** (fast, persistent, feature-rich)
2. **Set appropriate TTLs** based on data update frequency
3. **Use django-cacheops** for automatic ORM query caching
4. **Invalidate caches on writes** (signals, post_save, post_delete)
5. **Monitor cache hit/miss ratios** to optimize caching strategy
6. **Use cache versioning** for coordinated cache invalidation
7. **Combine multiple caching layers** (view caching + query caching)
8. **Cache expensive computations and serializations**, not cheap queries

---

## Action Items

### Immediate Implementation (High Priority)

1. **Upgrade to Django 5.1+** to leverage native PostgreSQL connection pooling
   - Configure `CONN_MAX_AGE=600` and `CONN_HEALTH_CHECKS=True`
   - Set `OPTIONS['pool']` with appropriate min/max sizes based on worker count

2. **Audit all querysets for N+1 problems**
   - Add `select_related()` for ForeignKey/OneToOne relationships
   - Add `prefetch_related()` for ManyToMany/reverse ForeignKey relationships
   - Use Django Debug Toolbar or django-silk to identify problematic queries

3. **Implement cursor-based pagination** for large dataset endpoints
   - Switch from PageNumberPagination to CursorPagination
   - Ensure ordering fields are indexed and immutable

4. **Add PostgreSQL-specific indexes**
   - GIN indexes for full-text search, ArrayField, JSONField
   - BRIN indexes for time-series/append-only data
   - Verify indexes with EXPLAIN ANALYZE

5. **Enable query monitoring**
   - Install and configure pg_stat_statements
   - Set up django-pg-stat-statements for Django admin visibility
   - Establish baseline performance metrics

### Medium-Term Implementation (Weeks 2-4)

6. **Implement Redis caching**
   - Set up Redis cache backend
   - Install and configure django-cacheops for ORM query caching
   - Implement cache invalidation strategies (signals)

7. **Establish zero-downtime migration practices**
   - Install django-pg-zero-downtime-migrations
   - Document multi-step patterns for common operations
   - Test migrations in staging with production-sized data

8. **Optimize DRF serializers**
   - Make non-writable fields read_only=True
   - Replace SerializerMethodField with annotations where possible
   - Use .values() for performance-critical read-only endpoints

9. **Implement database security hardening**
   - Create separate PostgreSQL roles (migrator, application)
   - Configure minimal privileges for application role
   - Enable SSL connections
   - Audit and update to latest Django version

### Long-Term Optimization (Month 2+)

10. **Set up comprehensive test suite optimization**
    - Configure pytest-django with --keepdb
    - Implement parallel test execution
    - Create RAM disk tablespace for test database

11. **Implement advanced PostgreSQL features**
    - Evaluate full-text search needs (SearchVector, SearchRank)
    - Consider stored procedures/triggers for complex business logic (django-pgtrigger)
    - Explore PostgreSQL-specific field types (ArrayField, JSONField, HStoreField)

12. **Establish performance monitoring and alerting**
    - Integrate pgMustard or similar EXPLAIN visualization tool
    - Set up auto_explain for slow query logging
    - Create dashboards for query performance metrics
    - Implement APM solution (e.g., New Relic, Datadog, Sentry Performance)

13. **Document and standardize**
    - Create team guidelines based on this research
    - Establish code review checklist for database-related changes
    - Document migration procedures and rollback strategies
    - Create runbook for common database performance issues

---

## Sources

1. [Django REST Framework Official Documentation](https://www.django-rest-framework.org/) - API design, serializers, pagination
2. [Django 5.1 Release Notes](https://docs.djangoproject.com/en/5.1/releases/5.1/) - Native PostgreSQL connection pooling
3. [Django PostgreSQL Database Documentation](https://docs.djangoproject.com/en/5.2/ref/databases/) - Database configuration, OPTIONS
4. [PostgreSQL Official Documentation](https://www.postgresql.org/docs/) - Index types, isolation levels, extensions
5. [10 Tips to Optimize PostgreSQL Queries in Django (GitGuardian Blog, 2024)](https://blog.gitguardian.com/10-tips-to-optimize-postgresql-queries-in-your-django-project/) - Query optimization techniques
6. [Django Performance Improvements - Database Optimizations (Sentry Blog, 2024)](https://blog.sentry.io/django-performance-improvements-part-1-database-optimizations/) - select_related, prefetch_related
7. [Optimizing Pagination in DRF for Large Datasets (Poespas Blog, May 2024)](https://blog.poespas.me/posts/2024/05/20/optimizing-django-rest-framework-pagination/) - CursorPagination best practices
8. [Django Zero Downtime Deployment Guide (Vinta Software, 2024)](https://www.vintasoftware.com/blog/django-zero-downtime-guide) - Migration strategies
9. [django-pg-zero-downtime-migrations (GitHub)](https://github.com/tbicr/django-pg-zero-downtime-migrations) - Zero-downtime migration library
10. [Django Cacheops (GitHub)](https://github.com/Suor/django-cacheops) - Automatic ORM query caching
11. [11 Tips for Lightning-Fast Tests in Django (Medium, 2024)](https://gauravvjn.medium.com/11-tips-for-lightning-fast-tests-in-django-effa87383040) - Test optimization
12. [Concurrency and Database Connections in Django (Heroku Dev Center)](https://devcenter.heroku.com/articles/python-concurrency-and-database-connections) - Connection pooling, CONN_MAX_AGE
13. [Django Security Documentation](https://docs.djangoproject.com/en/5.2/topics/security/) - SQL injection prevention
14. [PostgreSQL Better Security for Django (DEV Community)](https://dev.to/matthewhegarty/postgresql-better-security-for-django-applications-3c7m) - Database role separation
15. [pg_stat_statements Documentation](https://www.postgresql.org/docs/current/pgstatstatements.html) - Query performance monitoring

---

## Caveats

1. **Django Version Dependency**: Many recommendations (especially native connection pooling) require Django 5.1+. Teams on earlier versions should evaluate upgrade path vs. using external tools like PgBouncer.

2. **Performance Metrics are Context-Dependent**: Benchmarks cited (e.g., "50-70% faster with .values()") vary significantly based on data size, query complexity, and hardware. Always profile in your specific environment.

3. **Zero-Downtime Migration Complexity**: While multi-step migration patterns prevent downtime, they increase deployment complexity and require careful coordination between code and database changes.

4. **Caching Adds Complexity**: Automatic query caching (django-cacheops) introduces cache invalidation challenges. Ensure thorough testing of cache invalidation logic to prevent stale data issues.

5. **PostgreSQL Version Requirements**: Some features require specific PostgreSQL versions:
   - Full-text search on JSON: PostgreSQL 10+
   - Connection pooling optimizations: PostgreSQL 12+
   - Recommended minimum: PostgreSQL 13+ for production

6. **Further Research Needed**:
   - Horizontal scaling strategies (read replicas, sharding)
   - PostgreSQL tuning parameters (shared_buffers, work_mem, etc.)
   - Container orchestration considerations (Kubernetes, Docker Swarm)
   - Multi-region deployment patterns

7. **Testing Coverage**: Testing strategies outlined focus on unit/integration tests. Load testing and performance testing under production-like conditions require additional tooling (e.g., Locust, Artillery, k6).

8. **Monitoring and Observability**: While query monitoring tools are covered, comprehensive application performance monitoring (APM) integration is beyond scope but highly recommended for production systems.
