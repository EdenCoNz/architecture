# Django PostgreSQL Production Optimization Guide

## Database Configuration

### Basic Production Settings

```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection persistence (seconds)
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 second query timeout
        },
    }
}
```

### Django 5.1+ Native Connection Pooling (NEW - August 2024)

**Benefits**: Reduces latency by 50-70ms, improves response times 10-30%

```python
# Requires Django 5.1+ and psycopg (not psycopg2)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... other settings ...
        'OPTIONS': {
            'pool': {
                'min_size': 2,
                'max_size': 10,
                'timeout': 30,
            }
        }
    }
}
```

**Note**: Django docs recommend against native pooling with ASGI. Use PgBouncer instead for ASGI apps.

## Connection Pooling with PgBouncer

### Why PgBouncer?
- Lightweight connection pooler sits between Django and PostgreSQL
- Essential for scaling with multiple workers/containers
- Reduces connection overhead significantly

### PgBouncer Configuration

```ini
# pgbouncer.ini
[databases]
mydb = host=postgres_host port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction  # Most common for Django
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3
```

### Django Settings for PgBouncer

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'pgbouncer',  # Point to PgBouncer, not Postgres
        'PORT': '6432',
        'CONN_MAX_AGE': 0,  # Important: Disable Django's pooling
        'DISABLE_SERVER_SIDE_CURSORS': True,  # Required for transaction mode
    }
}
```

### Pool Modes
- **Session mode**: Most conservative, no Django changes needed
- **Transaction mode**: Default, requires `DISABLE_SERVER_SIDE_CURSORS = True`
- **Statement mode**: Most aggressive, rarely used

## Query Optimization

### 1. Use select_related() for Foreign Keys

```python
# Bad - N+1 queries (1 + 100 queries)
articles = Article.objects.all()  # 1 query
for article in articles:
    print(article.author.name)  # 100 additional queries

# Good - Single JOIN query
articles = Article.objects.select_related('author').all()  # 1 query
for article in articles:
    print(article.author.name)  # No additional queries
```

**Result**: Up to 80% reduction in query time for FK relationships

### 2. Use prefetch_related() for Reverse FKs and M2M

```python
# Bad - N+1 queries
authors = Author.objects.all()
for author in authors:
    print(author.articles.count())  # Query per author

# Good - 2 queries total
authors = Author.objects.prefetch_related('articles').all()
for author in authors:
    print(author.articles.count())  # No additional queries
```

### 3. Combine Both Methods

```python
# Fetch articles with authors and tags
articles = Article.objects.select_related(
    'author'
).prefetch_related(
    'tags',
    'comments__user'
).all()

# Advanced: Custom Prefetch with filtering
from django.db.models import Prefetch

articles = Article.objects.prefetch_related(
    Prefetch(
        'comments',
        queryset=Comment.objects.select_related('user').filter(approved=True)
    )
)
```

### 4. Field Selection Optimization

```python
# Only fetch needed fields - 50%+ faster
Article.objects.only('id', 'title', 'created_at')

# Exclude heavy fields
Article.objects.defer('content', 'metadata')

# Get dicts instead of model instances - fastest
Article.objects.values('id', 'title')
Article.objects.values_list('id', 'title', named=True)
```

## Database Indexing

### Index Strategy

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)  # Auto-indexed
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Auto-indexed
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        # Composite index for common query patterns
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['-created_at']),  # Descending
        ]
```

### Index Guidelines
- **Always index**: Primary keys (auto), Foreign keys (auto), fields in WHERE/ORDER BY/GROUP BY
- **Composite indexes**: For frequent multi-field queries
- **Partial indexes**: For filtered queries
- **Trade-off**: Indexes speed reads but slow writes and increase storage

### PostgreSQL-Specific Indexes

```python
from django.contrib.postgres.indexes import BrinIndex, GinIndex, HashIndex

class Article(models.Model):
    content = models.TextField()
    tags = ArrayField(models.CharField(max_length=50))

    class Meta:
        indexes = [
            # GIN index for full-text search
            GinIndex(fields=['content'], opclasses=['gin_trgm_ops']),
            # GIN for array fields
            GinIndex(fields=['tags']),
            # BRIN for large timestamp columns
            BrinIndex(fields=['created_at']),
        ]
```

## PostgreSQL-Specific Features

### 1. JSONField

```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    metadata = models.JSONField(default=dict)

# Query JSON fields
Product.objects.filter(metadata__color='red')
Product.objects.filter(metadata__specs__weight__gt=100)
```

### 2. ArrayField

```python
from django.contrib.postgres.fields import ArrayField

class Article(models.Model):
    tags = ArrayField(models.CharField(max_length=50), default=list)

# Query arrays
Article.objects.filter(tags__contains=['django'])
Article.objects.filter(tags__overlap=['python', 'postgres'])
```

### 3. Full-Text Search

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

# Basic search
Article.objects.filter(content__search='django')

# Advanced search with ranking
vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
query = SearchQuery('django postgres')
Article.objects.annotate(
    rank=SearchRank(vector, query)
).filter(rank__gte=0.3).order_by('-rank')
```

### 4. Database Functions

```python
from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg
from django.db.models import Q

# Aggregate into arrays
Author.objects.annotate(article_titles=ArrayAgg('articles__title'))

# Case-insensitive queries
Article.objects.filter(title__iexact='django')
Article.objects.filter(title__icontains='django')
```

## Query Performance Analysis

### 1. Use Django Debug Toolbar (Development)

```python
# settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### 2. Use django-silk (Production-safe profiling)

```python
# Profile slow queries in production
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

### 3. PostgreSQL EXPLAIN ANALYZE

```python
from django.db import connection

def analyze_query():
    with connection.cursor() as cursor:
        cursor.execute('EXPLAIN ANALYZE SELECT * FROM articles WHERE status = %s', ['published'])
        print(cursor.fetchall())

# Or use queryset.explain()
print(Article.objects.filter(status='published').explain(analyze=True))
```

### 4. Log Slow Queries

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Shows all queries (dev only)
        },
    },
}

# PostgreSQL config for slow query logging
# In postgresql.conf:
# log_min_duration_statement = 1000  # Log queries > 1 second
```

## Database Migrations Best Practices

### 1. Zero-Downtime Migrations

**Adding nullable fields (preferred)**:
```python
# migration 1: Add nullable field
class Migration(migrations.Migration):
    operations = [
        migrations.AddField('Article', 'new_field',
                          models.CharField(max_length=100, null=True)),
    ]

# migration 2: Populate data
# migration 3: Make field non-nullable (optional)
```

**Adding NOT NULL fields** (avoid for large tables):
```python
# For small tables only (<100k rows)
migrations.AddField('Article', 'new_field',
                   models.CharField(max_length=100, default=''))
```

### 2. Migration Testing

```python
# Test migrations before production
python manage.py migrate --plan
python manage.py sqlmigrate app_name 0001

# Time migrations in staging
\timing on  # PostgreSQL
python manage.py migrate
```

### 3. Index Creation (Large Tables)

```python
# Create indexes concurrently (doesn't lock table)
from django.contrib.postgres.operations import AddIndexConcurrently

class Migration(migrations.Migration):
    atomic = False  # Required for CONCURRENT

    operations = [
        AddIndexConcurrently(
            model_name='article',
            index=models.Index(fields=['status']),
        ),
    ]
```

## Transaction Management

### 1. Atomic Transactions

```python
from django.db import transaction

# Decorator
@transaction.atomic
def create_article(data):
    article = Article.objects.create(**data)
    notify_subscribers(article)  # Runs in transaction
    return article

# Context manager
def update_balance(account, amount):
    with transaction.atomic():
        account.balance += amount
        account.save()
        Transaction.objects.create(account=account, amount=amount)
```

### 2. Signals with Transactions

```python
from django.db import transaction
from django.db.models.signals import post_save

@receiver(post_save, sender=Article)
def article_saved(sender, instance, **kwargs):
    # Run AFTER transaction commits (prevents issues on rollback)
    transaction.on_commit(lambda: send_notification(instance))
```

### 3. Isolation Levels

```python
# For specific isolation requirements
from django.db import transaction

with transaction.atomic():
    # Default is READ COMMITTED in PostgreSQL
    cursor.execute('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
    # Your queries here
```

## Backup and Monitoring

### Backup Strategy

```bash
# Automated backups
pg_dump -U user -d dbname > backup_$(date +%Y%m%d_%H%M%S).sql

# With compression
pg_dump -U user -d dbname | gzip > backup.sql.gz

# Restore
psql -U user -d dbname < backup.sql
```

### Monitoring Queries

```python
# Install django-pgviews or query pg_stat_statements
from django.db import connection

def get_slow_queries():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT query, calls, mean_exec_time, total_exec_time
            FROM pg_stat_statements
            ORDER BY mean_exec_time DESC
            LIMIT 10;
        """)
        return cursor.fetchall()
```

## Performance Checklist

- [ ] Connection pooling configured (PgBouncer or Django 5.1+)
- [ ] `select_related()` used for all FK access
- [ ] `prefetch_related()` used for reverse FKs and M2M
- [ ] Database indexes on filtered/sorted fields
- [ ] Composite indexes for common multi-field queries
- [ ] Query analysis with EXPLAIN ANALYZE
- [ ] Slow query logging enabled
- [ ] `CONN_MAX_AGE` set appropriately
- [ ] `DISABLE_SERVER_SIDE_CURSORS` if using PgBouncer transaction mode
- [ ] Migrations tested in staging environment
- [ ] Automated backup system in place
- [ ] PostgreSQL-specific fields used where appropriate (JSONField, ArrayField)
- [ ] Full-text search with SearchVector instead of `__icontains`
