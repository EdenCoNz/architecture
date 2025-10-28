# Django REST Framework Testing Best Practices Guide
**Date**: 2025-10-13
**Purpose**: Comprehensive testing guide for Django REST Framework backend development
**Versions Covered**: Django 4.x/5.x, DRF 3.14/3.15, pytest-django 4.9.0+, Python 3.12+

## Summary

This guide provides actionable testing strategies for Django REST Framework based on 2024-2025 best practices. Modern DRF testing emphasizes pytest over unittest for reduced boilerplate, Factory Boy for test data generation, and comprehensive coverage tools. Key findings: DRF 3.15 (released March 2024) supports Django 5.0+ and Python 3.12; pytest-django 4.10.0+ (February 2025) provides robust database fixtures and transaction support; coverage.py 7.10.7 (September 2025) offers the latest test coverage analysis. The testing ecosystem has matured around automation, CI/CD integration, and TDD workflows.

---

## 1. Core Testing Tools (2025)

### 1.1 pytest-django vs Django TestCase

**Current Versions:**
- pytest-django: 4.10.0+ (released February 2025)
- Django 5.0+: Active updates through August 2024, security updates through April 2025
- Django 5.2: Latest release with PostgreSQL 14+ support, utf8mb4 default for MySQL

**Key Differences:**

| Feature | pytest-django | Django TestCase |
|---------|--------------|-----------------|
| Boilerplate | Minimal - plain functions | High - requires class inheritance |
| Syntax | Pythonic `assert` statements | `self.assertEqual()` methods |
| Fixtures | Advanced - scope control, reusable | Limited - class-level only |
| Parameterization | Built-in `@pytest.mark.parametrize` | Manual implementation required |
| Plugin Ecosystem | Extensive (pytest-cov, pytest-xdist) | Standard library only |
| Django Integration | Via pytest-django adapter | Native Django support |

**When to Use Which:**

**Use pytest-django when:**
- Starting new projects (less boilerplate, modern approach)
- Need advanced fixture management with different scopes
- Want parameterized tests for multiple input scenarios
- Require extensive plugin ecosystem (coverage, parallel execution)
- Team prefers functional programming style

**Use Django TestCase when:**
- Working on legacy codebases using unittest
- Team has strong unittest expertise
- Need Django's native TransactionTestCase features
- Minimal external dependencies required

**Recommendation:** pytest-django is the 2025 standard for new DRF projects due to reduced boilerplate, better fixture management, and superior integration with modern tooling.

**Installation:**

```bash
pip install pytest-django pytest-cov factory-boy faker
```

**Basic Configuration (pytest.ini):**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings.test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=.
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-fail-under=80
    --reuse-db
    --nomigrations
```

**Example: pytest-django Test:**

```python
# tests/test_api.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
```

**Example: Django TestCase Equivalent:**

```python
# tests/test_api.py
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
```

---

### 1.2 Factory Boy + Faker for Test Data

**Current Versions:**
- Factory Boy: 3.3.0+ (actively maintained as of 2024)
- Faker: 20.0.0+ (2024 releases)

**Why Use Factory Boy + Faker:**
- Eliminates verbose test data setup
- Creates realistic test data with Faker integration
- Reduces fixture JSON file maintenance
- Supports complex object relationships
- Provides lazy attribute evaluation

**Installation:**

```bash
pip install factory-boy faker
```

**Basic Factory Setup:**

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from django.contrib.auth import get_user_model
from myapp.models import Article, Category

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())
    description = factory.Faker('paragraph')

class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker('sentence', nb_words=6)
    slug = factory.LazyAttribute(lambda obj: obj.title.lower().replace(' ', '-'))
    content = factory.Faker('paragraphs', nb=3)
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    status = FuzzyChoice(['draft', 'published', 'archived'])
    published_at = factory.Faker('date_time_this_year')
```

**Using Factories in Tests:**

```python
# tests/test_articles.py
import pytest
from tests.factories import ArticleFactory, UserFactory

@pytest.mark.django_db
class TestArticleModel:
    def test_article_creation(self):
        article = ArticleFactory()
        assert article.title is not None
        assert article.author is not None
        assert article.category is not None

    def test_article_with_custom_author(self):
        author = UserFactory(username='custom_author')
        article = ArticleFactory(author=author)
        assert article.author.username == 'custom_author'

    def test_create_multiple_articles(self):
        articles = ArticleFactory.create_batch(5)
        assert len(articles) == 5
```

**Advanced Factory Patterns:**

```python
# tests/factories.py
class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker('sentence')
    content = factory.Faker('paragraphs', nb=3)
    author = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def word_count(self):
        """Calculate word count from content."""
        return len(' '.join(self.content).split())

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags after article creation."""
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)

# Usage
@pytest.mark.django_db
def test_article_with_tags():
    tag1 = TagFactory(name='python')
    tag2 = TagFactory(name='django')
    article = ArticleFactory(tags=[tag1, tag2])
    assert article.tags.count() == 2
```

**Best Practices:**
- Store factories in `tests/factories.py` or app-specific `myapp/tests/factories.py`
- Use `Sequence` for unique fields (username, email)
- Use `LazyAttribute` for derived fields (slug from title)
- Use `SubFactory` for foreign key relationships
- Use `post_generation` for many-to-many relationships
- Combine with pytest fixtures for reusable test data

```python
# conftest.py
import pytest
from tests.factories import UserFactory, ArticleFactory

@pytest.fixture
def user(db):
    """Create a standard user."""
    return UserFactory()

@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return UserFactory(is_staff=True, is_superuser=True)

@pytest.fixture
def published_article(db):
    """Create a published article."""
    return ArticleFactory(status='published')
```

---

### 1.3 DRF's APIClient and APITestCase

**Current Versions:**
- Django REST Framework 3.15.0 (released March 15, 2024)
- Supports Django 5.0+ and Python 3.12+

**APIClient vs APITestCase:**

| Feature | APIClient | APITestCase |
|---------|-----------|-------------|
| Usage | Standalone client | TestCase subclass |
| Framework | Works with pytest | Django TestCase style |
| CSRF | Disabled by default | Disabled by default |
| Authentication | Manual via `force_authenticate()` | Manual via `force_authenticate()` |
| Flexibility | Use as fixture/standalone | Class-based inheritance |

**APIClient with pytest (Recommended for 2025):**

```python
# conftest.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """Provide an API client for tests."""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    """Provide an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client

# tests/test_api_views.py
import pytest
from rest_framework import status
from django.urls import reverse
from tests.factories import ArticleFactory

@pytest.mark.django_db
class TestArticleAPI:
    def test_list_articles(self, api_client):
        ArticleFactory.create_batch(3, status='published')
        url = reverse('article-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_article_unauthenticated(self, api_client):
        url = reverse('article-list')
        data = {'title': 'Test Article', 'content': 'Test content'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_article_authenticated(self, authenticated_client):
        url = reverse('article-list')
        data = {
            'title': 'New Article',
            'content': 'Article content',
            'status': 'draft'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Article'
```

**APITestCase (Django TestCase Style):**

```python
# tests/test_api_views.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from tests.factories import UserFactory, ArticleFactory

class ArticleAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.article = ArticleFactory(author=self.user)

    def test_list_articles(self):
        url = reverse('article-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_article_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('article-list')
        data = {'title': 'New Article', 'content': 'Content'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

**Testing Different HTTP Methods:**

```python
@pytest.mark.django_db
class TestArticleAPICRUD:
    def test_retrieve_article(self, api_client):
        article = ArticleFactory()
        url = reverse('article-detail', kwargs={'pk': article.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == article.id

    def test_update_article(self, authenticated_client):
        article = ArticleFactory()
        url = reverse('article-detail', kwargs={'pk': article.pk})
        data = {'title': 'Updated Title'}
        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        article.refresh_from_db()
        assert article.title == 'Updated Title'

    def test_delete_article(self, authenticated_client):
        article = ArticleFactory()
        url = reverse('article-detail', kwargs={'pk': article.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Article.objects.filter(pk=article.pk).exists()
```

**Custom Headers and Authentication:**

```python
@pytest.mark.django_db
def test_api_with_custom_headers(api_client):
    url = reverse('article-list')
    response = api_client.get(
        url,
        HTTP_AUTHORIZATION='Bearer fake-token',
        HTTP_X_CUSTOM_HEADER='custom-value'
    )
    assert response.status_code in [200, 401]

@pytest.mark.django_db
def test_token_authentication(api_client, user):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user)

    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    url = reverse('article-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
```

---

## 2. Essential Testing Patterns

### 2.1 Testing DRF ViewSets

**Basic ViewSet Structure:**

```python
# myapp/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        if self.request.user.is_staff:
            return Article.objects.all()
        return Article.objects.filter(status='published')

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Custom action to publish an article."""
        article = self.get_object()
        article.status = 'published'
        article.save()
        serializer = self.get_serializer(article)
        return Response(serializer.data)
```

**Comprehensive ViewSet Tests:**

```python
# tests/test_viewsets.py
import pytest
from rest_framework import status
from django.urls import reverse
from tests.factories import ArticleFactory, UserFactory

@pytest.mark.django_db
class TestArticleViewSet:
    """Test suite for ArticleViewSet."""

    def test_list_articles_unauthenticated(self, api_client):
        """Unauthenticated users see only published articles."""
        ArticleFactory.create_batch(2, status='published')
        ArticleFactory.create_batch(2, status='draft')

        url = reverse('article-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_articles_staff_user(self, api_client):
        """Staff users see all articles."""
        staff_user = UserFactory(is_staff=True)
        api_client.force_authenticate(user=staff_user)

        ArticleFactory.create_batch(2, status='published')
        ArticleFactory.create_batch(2, status='draft')

        url = reverse('article-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4

    def test_retrieve_article(self, api_client):
        """Test retrieving a single article."""
        article = ArticleFactory(status='published')
        url = reverse('article-detail', kwargs={'pk': article.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == article.id
        assert response.data['title'] == article.title

    def test_create_article_authenticated(self, authenticated_client):
        """Authenticated users can create articles."""
        url = reverse('article-list')
        data = {
            'title': 'New Article',
            'content': 'Article content',
            'status': 'draft'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Article'
        assert Article.objects.filter(title='New Article').exists()

    def test_create_article_unauthenticated(self, api_client):
        """Unauthenticated users cannot create articles."""
        url = reverse('article-list')
        data = {'title': 'New Article', 'content': 'Content'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_article_owner(self, api_client):
        """Article owner can update their article."""
        user = UserFactory()
        article = ArticleFactory(author=user)
        api_client.force_authenticate(user=user)

        url = reverse('article-detail', kwargs={'pk': article.pk})
        data = {'title': 'Updated Title'}
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        article.refresh_from_db()
        assert article.title == 'Updated Title'

    def test_delete_article_owner(self, api_client):
        """Article owner can delete their article."""
        user = UserFactory()
        article = ArticleFactory(author=user)
        api_client.force_authenticate(user=user)

        url = reverse('article-detail', kwargs={'pk': article.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Article.objects.filter(pk=article.pk).exists()

    def test_custom_action_publish(self, api_client):
        """Test custom publish action."""
        user = UserFactory()
        article = ArticleFactory(author=user, status='draft')
        api_client.force_authenticate(user=user)

        url = reverse('article-publish', kwargs={'pk': article.pk})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        article.refresh_from_db()
        assert article.status == 'published'
```

**Testing Query Parameters and Filtering:**

```python
@pytest.mark.django_db
class TestArticleFiltering:
    def test_filter_by_status(self, api_client):
        ArticleFactory.create_batch(2, status='published')
        ArticleFactory.create_batch(3, status='draft')

        url = reverse('article-list')
        response = api_client.get(url, {'status': 'published'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_articles(self, api_client):
        ArticleFactory(title='Python Tutorial', status='published')
        ArticleFactory(title='Django Guide', status='published')

        url = reverse('article-list')
        response = api_client.get(url, {'search': 'Python'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'Python' in response.data[0]['title']
```

---

### 2.2 Testing Serializers

**Basic Serializer:**

```python
# myapp/serializers.py
from rest_framework import serializers
from .models import Article, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id', 'slug']

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    word_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'author', 'author_name',
            'category', 'category_id', 'status', 'word_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'author', 'created_at', 'updated_at']

    def get_word_count(self, obj):
        return len(obj.content.split())

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters.")
        return value

    def validate(self, attrs):
        if attrs.get('status') == 'published' and not attrs.get('category'):
            raise serializers.ValidationError(
                "Published articles must have a category."
            )
        return attrs
```

**Comprehensive Serializer Tests:**

```python
# tests/test_serializers.py
import pytest
from myapp.serializers import ArticleSerializer, CategorySerializer
from tests.factories import ArticleFactory, CategoryFactory, UserFactory

@pytest.mark.django_db
class TestArticleSerializer:
    """Test suite for ArticleSerializer."""

    def test_serialization(self):
        """Test serializing an article instance."""
        article = ArticleFactory()
        serializer = ArticleSerializer(article)
        data = serializer.data

        assert data['id'] == article.id
        assert data['title'] == article.title
        assert data['author_name'] == article.author.username
        assert 'category' in data
        assert 'word_count' in data

    def test_deserialization_valid_data(self):
        """Test creating an article from valid data."""
        category = CategoryFactory()
        data = {
            'title': 'Test Article',
            'content': 'This is test content',
            'category_id': category.id,
            'status': 'draft'
        }
        serializer = ArticleSerializer(data=data)

        assert serializer.is_valid()
        article = serializer.save(author=UserFactory())
        assert article.title == 'Test Article'
        assert article.category == category

    def test_title_validation_too_short(self):
        """Test title validation fails for short titles."""
        data = {
            'title': 'Test',  # Too short
            'content': 'Content',
            'status': 'draft'
        }
        serializer = ArticleSerializer(data=data)

        assert not serializer.is_valid()
        assert 'title' in serializer.errors
        assert 'at least 5 characters' in str(serializer.errors['title'])

    def test_published_article_requires_category(self):
        """Test that published articles must have a category."""
        data = {
            'title': 'Test Article',
            'content': 'Content',
            'status': 'published'
            # Missing category_id
        }
        serializer = ArticleSerializer(data=data)

        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_read_only_fields_ignored_on_create(self):
        """Test that read-only fields are ignored during creation."""
        category = CategoryFactory()
        data = {
            'title': 'Test Article',
            'content': 'Content',
            'category_id': category.id,
            'status': 'draft',
            'id': 999,  # Should be ignored
            'slug': 'custom-slug',  # Should be ignored
        }
        serializer = ArticleSerializer(data=data)

        assert serializer.is_valid()
        article = serializer.save(author=UserFactory())
        assert article.id != 999
        assert article.slug != 'custom-slug'

    def test_update_article(self):
        """Test updating an existing article."""
        article = ArticleFactory(status='draft')
        data = {'title': 'Updated Title', 'status': 'published'}
        serializer = ArticleSerializer(article, data=data, partial=True)

        assert serializer.is_valid()
        updated_article = serializer.save()
        assert updated_article.title == 'Updated Title'
        assert updated_article.status == 'published'

    def test_method_field_word_count(self):
        """Test SerializerMethodField for word count."""
        article = ArticleFactory(content='one two three four five')
        serializer = ArticleSerializer(article)

        assert serializer.data['word_count'] == 5

    def test_nested_serializer_read(self):
        """Test nested category serializer on read."""
        category = CategoryFactory(name='Technology')
        article = ArticleFactory(category=category)
        serializer = ArticleSerializer(article)

        assert serializer.data['category']['name'] == 'Technology'
        assert serializer.data['category']['id'] == category.id
```

**Testing Custom Serializer Methods:**

```python
@pytest.mark.django_db
class TestCategorySerializer:
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from name."""
        data = {
            'name': 'Test Category',
            'description': 'Description'
        }
        serializer = CategorySerializer(data=data)

        assert serializer.is_valid()
        category = serializer.save()
        assert category.slug == 'test-category'
```

---

### 2.3 Testing Permissions

**Custom Permission Classes:**

```python
# myapp/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for the owner
        return obj.author == request.user

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff users to edit.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
```

**Permission Tests:**

```python
# tests/test_permissions.py
import pytest
from rest_framework import status
from django.urls import reverse
from tests.factories import ArticleFactory, UserFactory

@pytest.mark.django_db
class TestArticlePermissions:
    """Test suite for article permissions."""

    def test_unauthenticated_can_read(self, api_client):
        """Unauthenticated users can read articles."""
        article = ArticleFactory(status='published')
        url = reverse('article-detail', kwargs={'pk': article.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_cannot_create(self, api_client):
        """Unauthenticated users cannot create articles."""
        url = reverse('article-list')
        data = {'title': 'Test', 'content': 'Content'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_owner_can_update(self, api_client):
        """Article owner can update their article."""
        user = UserFactory()
        article = ArticleFactory(author=user)
        api_client.force_authenticate(user=user)

        url = reverse('article-detail', kwargs={'pk': article.pk})
        data = {'title': 'Updated Title'}
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_non_owner_cannot_update(self, api_client):
        """Non-owner cannot update article."""
        owner = UserFactory()
        other_user = UserFactory()
        article = ArticleFactory(author=owner)
        api_client.force_authenticate(user=other_user)

        url = reverse('article-detail', kwargs={'pk': article.pk})
        data = {'title': 'Updated Title'}
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete(self, api_client):
        """Article owner can delete their article."""
        user = UserFactory()
        article = ArticleFactory(author=user)
        api_client.force_authenticate(user=user)

        url = reverse('article-detail', kwargs={'pk': article.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_staff_can_update_any_article(self, api_client):
        """Staff users can update any article."""
        staff_user = UserFactory(is_staff=True)
        regular_user = UserFactory()
        article = ArticleFactory(author=regular_user)
        api_client.force_authenticate(user=staff_user)

        url = reverse('article-detail', kwargs={'pk': article.pk})
        data = {'title': 'Staff Updated'}
        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
```

**Testing Permission Classes Directly:**

```python
# tests/test_permission_classes.py
import pytest
from rest_framework.test import APIRequestFactory
from myapp.permissions import IsOwnerOrReadOnly
from myapp.views import ArticleViewSet
from tests.factories import ArticleFactory, UserFactory

@pytest.mark.django_db
class TestIsOwnerOrReadOnlyPermission:
    """Test the IsOwnerOrReadOnly permission class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.permission = IsOwnerOrReadOnly()

    def test_safe_methods_allowed_for_anyone(self):
        """GET, HEAD, OPTIONS allowed for any user."""
        article = ArticleFactory()
        request = self.factory.get('/')
        request.user = UserFactory()

        assert self.permission.has_object_permission(request, None, article)

    def test_owner_can_modify(self):
        """Owner can perform unsafe methods."""
        user = UserFactory()
        article = ArticleFactory(author=user)
        request = self.factory.put('/')
        request.user = user

        assert self.permission.has_object_permission(request, None, article)

    def test_non_owner_cannot_modify(self):
        """Non-owner cannot perform unsafe methods."""
        owner = UserFactory()
        other_user = UserFactory()
        article = ArticleFactory(author=owner)
        request = self.factory.put('/')
        request.user = other_user

        assert not self.permission.has_object_permission(request, None, article)
```

---

### 2.4 Authentication and Authorization Testing

**Token Authentication Tests:**

```python
# tests/test_authentication.py
import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from tests.factories import UserFactory

@pytest.mark.django_db
class TestTokenAuthentication:
    """Test token-based authentication."""

    def test_obtain_auth_token(self, api_client):
        """Test obtaining authentication token."""
        user = UserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()

        url = reverse('api-token-auth')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data

    def test_invalid_credentials(self, api_client):
        """Test authentication with invalid credentials."""
        url = reverse('api-token-auth')
        data = {'username': 'invalid', 'password': 'wrong'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authenticated_request_with_token(self, api_client):
        """Test making authenticated request with token."""
        user = UserFactory()
        token = Token.objects.create(user=user)

        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        url = reverse('article-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_invalid_token(self, api_client):
        """Test request with invalid token."""
        api_client.credentials(HTTP_AUTHORIZATION='Token invalid-token-key')
        url = reverse('article-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

**JWT Authentication Tests:**

```python
@pytest.mark.django_db
class TestJWTAuthentication:
    """Test JWT authentication (using djangorestframework-simplejwt)."""

    def test_obtain_jwt_token_pair(self, api_client):
        """Test obtaining access and refresh tokens."""
        user = UserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()

        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_refresh_token(self, api_client):
        """Test refreshing access token."""
        user = UserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()

        # Obtain tokens
        token_url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        token_response = api_client.post(token_url, data, format='json')
        refresh_token = token_response.data['refresh']

        # Refresh token
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = api_client.post(refresh_url, refresh_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_authenticated_request_with_jwt(self, api_client):
        """Test making authenticated request with JWT."""
        user = UserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()

        # Obtain token
        token_url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        token_response = api_client.post(token_url, data, format='json')
        access_token = token_response.data['access']

        # Make authenticated request
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('article-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
```

**Session Authentication Tests:**

```python
@pytest.mark.django_db
class TestSessionAuthentication:
    """Test session-based authentication."""

    def test_login_view(self, api_client):
        """Test logging in via session authentication."""
        user = UserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()

        # Login
        login_success = api_client.login(username='testuser', password='testpass123')
        assert login_success

        # Make authenticated request
        url = reverse('article-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_logout_view(self, api_client):
        """Test logging out."""
        user = UserFactory(username='testuser')
        user.set_password('testpass123')
        user.save()

        # Login
        api_client.login(username='testuser', password='testpass123')

        # Logout
        api_client.logout()

        # Verify logged out
        url = reverse('article-list')
        response = api_client.get(url)
        # Behavior depends on permission_classes
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
```

---

### 2.5 Database Testing Strategies

**Database Fixtures and Transactions:**

Django's TestCase uses database transactions that are rolled back after each test. pytest-django provides multiple database access strategies:

| Fixture | Scope | Transaction Support | Use Case |
|---------|-------|---------------------|----------|
| `db` | Function | Rollback after test | Standard tests |
| `transactional_db` | Function | Commit/rollback testing | Testing transactions |
| `django_db_reset_sequences` | Function | Resets sequences | Testing with auto-increment |
| `django_db_serialized_rollback` | Function | Serialized rollback | Complex test isolation |

**Basic Database Testing:**

```python
# conftest.py
import pytest
from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Load initial data for the entire test session.
    Only for non-transactional tests.
    """
    with django_db_blocker.unblock():
        call_command('loaddata', 'initial_data.json')

# tests/test_database.py
@pytest.mark.django_db
def test_simple_database_access():
    """Standard database test with automatic rollback."""
    user = UserFactory()
    assert User.objects.count() == 1

@pytest.mark.django_db(transaction=True)
def test_with_transaction_support():
    """Test that requires actual transaction commit/rollback."""
    from django.db import transaction

    user = UserFactory()

    with transaction.atomic():
        user.username = 'updated'
        user.save()

    user.refresh_from_db()
    assert user.username == 'updated'

@pytest.mark.django_db(reset_sequences=True)
def test_with_sequence_reset():
    """Test that requires primary key sequences to be reset."""
    user1 = UserFactory()
    assert user1.pk == 1

    user2 = UserFactory()
    assert user2.pk == 2
```

**Fixture Loading Strategies:**

```python
# conftest.py
import pytest
from django.core.management import call_command

@pytest.fixture(scope='function')
def load_test_data(db):
    """Load test data from fixture file."""
    call_command('loaddata', 'test_data.json')

# tests/test_with_fixtures.py
@pytest.mark.django_db
def test_with_loaded_fixtures(load_test_data):
    """Test using pre-loaded fixture data."""
    assert Article.objects.count() > 0
    assert Category.objects.count() > 0
```

**Multi-Database Testing:**

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings.test

# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db_default',
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db_analytics',
    }
}

# tests/test_multi_database.py
@pytest.mark.django_db(databases=['default', 'analytics'])
def test_multi_database_access():
    """Test accessing multiple databases."""
    # Create in default database
    user = UserFactory()

    # Create in analytics database
    from myapp.models import AnalyticsEvent
    event = AnalyticsEvent.objects.using('analytics').create(
        user_id=user.id,
        event_type='login'
    )

    assert User.objects.count() == 1
    assert AnalyticsEvent.objects.using('analytics').count() == 1
```

**Performance Optimization for Tests:**

```ini
# pytest.ini - Use in-memory SQLite for faster tests
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings.test
addopts = --reuse-db --nomigrations

# settings/test.py - Use SQLite in memory
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

**Best Practices:**
- Use `@pytest.mark.django_db` for tests requiring database access
- Default `db` fixture provides automatic rollback (fastest)
- Use `transactional_db` only when testing actual transactions
- Load fixtures at session scope for read-only data
- Use Factory Boy instead of JSON fixtures for maintainability
- Consider in-memory SQLite for faster test execution
- Use `--reuse-db` flag to speed up test runs during development

---

### 2.6 Mocking External APIs and Services

**Why Mock External Services:**
- Faster test execution (no network latency)
- Test reliability (no dependency on external service availability)
- Test edge cases (simulate errors, timeouts, rate limits)
- Cost reduction (avoid API call charges during testing)

**Mocking with unittest.mock:**

```python
# myapp/services.py
import requests

class WeatherService:
    """Service for fetching weather data from external API."""

    BASE_URL = "https://api.weather.com/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city):
        """Fetch weather data for a city."""
        response = requests.get(
            f"{self.BASE_URL}/weather",
            params={'city': city, 'api_key': self.api_key}
        )
        response.raise_for_status()
        return response.json()

# tests/test_weather_service.py
import pytest
from unittest.mock import patch, Mock
from myapp.services import WeatherService

@pytest.mark.django_db
class TestWeatherService:
    """Test suite for WeatherService with mocked API."""

    @patch('myapp.services.requests.get')
    def test_get_weather_success(self, mock_get):
        """Test successful weather data retrieval."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'city': 'London',
            'temperature': 15,
            'condition': 'Cloudy'
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Test service
        service = WeatherService(api_key='test-key')
        weather = service.get_weather('London')

        # Assertions
        assert weather['city'] == 'London'
        assert weather['temperature'] == 15
        mock_get.assert_called_once_with(
            "https://api.weather.com/v1/weather",
            params={'city': 'London', 'api_key': 'test-key'}
        )

    @patch('myapp.services.requests.get')
    def test_get_weather_api_error(self, mock_get):
        """Test handling of API errors."""
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.HTTPError("API Error")

        service = WeatherService(api_key='test-key')

        with pytest.raises(requests.exceptions.HTTPError):
            service.get_weather('London')
```

**Mocking with responses Library:**

```python
# Install: pip install responses
import responses
import requests
from myapp.services import WeatherService

@pytest.mark.django_db
class TestWeatherServiceWithResponses:
    """Test WeatherService using responses library."""

    @responses.activate
    def test_get_weather_with_responses(self):
        """Test using responses library for more realistic mocking."""
        # Setup mock response
        responses.add(
            responses.GET,
            'https://api.weather.com/v1/weather',
            json={'city': 'London', 'temperature': 15, 'condition': 'Cloudy'},
            status=200
        )

        service = WeatherService(api_key='test-key')
        weather = service.get_weather('London')

        assert weather['city'] == 'London'
        assert len(responses.calls) == 1
        assert 'city=London' in responses.calls[0].request.url

    @responses.activate
    def test_get_weather_timeout(self):
        """Test handling of API timeout."""
        responses.add(
            responses.GET,
            'https://api.weather.com/v1/weather',
            body=requests.exceptions.Timeout("Connection timeout")
        )

        service = WeatherService(api_key='test-key')

        with pytest.raises(requests.exceptions.Timeout):
            service.get_weather('London')
```

**Mocking Django Signals:**

```python
# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from .tasks import process_article

@receiver(post_save, sender=Article)
def article_post_save(sender, instance, created, **kwargs):
    """Process article after save."""
    if created:
        process_article.delay(instance.id)

# tests/test_signals.py
import pytest
from unittest.mock import patch
from tests.factories import ArticleFactory

@pytest.mark.django_db
class TestArticleSignals:
    @patch('myapp.signals.process_article.delay')
    def test_article_creation_triggers_task(self, mock_task):
        """Test that creating article triggers processing task."""
        article = ArticleFactory()

        mock_task.assert_called_once_with(article.id)
```

**Mocking Celery Tasks:**

```python
# myapp/tasks.py
from celery import shared_task
from .models import Article

@shared_task
def process_article(article_id):
    """Background task to process article."""
    article = Article.objects.get(id=article_id)
    # Processing logic...
    article.processed = True
    article.save()
    return article_id

# tests/test_tasks.py
import pytest
from unittest.mock import patch
from myapp.tasks import process_article
from tests.factories import ArticleFactory

@pytest.mark.django_db
class TestCeleryTasks:
    def test_process_article_task(self):
        """Test article processing task (synchronous)."""
        article = ArticleFactory(processed=False)

        result = process_article(article.id)

        assert result == article.id
        article.refresh_from_db()
        assert article.processed is True

    @patch('myapp.tasks.process_article.delay')
    def test_article_processing_called_async(self, mock_task):
        """Test that task is called asynchronously."""
        article = ArticleFactory()

        # Trigger async task
        process_article.delay(article.id)

        mock_task.assert_called_once_with(article.id)
```

**Mocking External Email Services:**

```python
# tests/test_email.py
import pytest
from django.core import mail
from tests.factories import UserFactory

@pytest.mark.django_db
def test_welcome_email_sent():
    """Test that welcome email is sent on user registration."""
    from myapp.views import register_user

    # Django test email backend captures emails
    user = UserFactory()
    register_user(user)

    # Check email was sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'Welcome'
    assert user.email in mail.outbox[0].to

# settings/test.py
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

**Best Practices:**
- Mock at the boundary - mock `requests.get()` not internal functions
- Use `responses` library for HTTP mocking (more realistic than unittest.mock)
- Mock external services, not your own code
- Test both success and failure scenarios
- Verify mock calls with `assert_called_once_with()`
- Use Django's `locmem` email backend for email testing
- Mock Celery tasks with `@patch('app.tasks.task_name.delay')`

---

## 3. Testing Infrastructure

### 3.1 Coverage Tools and Configuration

**Current Versions (2025):**
- coverage.py 7.10.7 (released September 21, 2025)
- pytest-cov 7.0.0 (released September 9, 2025)

**Installation:**

```bash
pip install coverage pytest-cov
```

**pytest-cov Configuration (Recommended):**

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings.test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=myapp
    --cov=myproject
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
    --reuse-db
    --nomigrations
    -v
```

**pyproject.toml Configuration:**

```toml
# pyproject.toml
[tool.coverage.run]
source = ["myapp", "myproject"]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/test_*.py",
    "*/__init__.py",
    "*/conftest.py",
    "*/settings/*",
    "*/wsgi.py",
    "*/asgi.py",
    "manage.py",
]
branch = true
parallel = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "def __str__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

**Running Coverage:**

```bash
# Run tests with coverage
pytest --cov

# Generate HTML report
pytest --cov --cov-report=html

# Generate XML report (for CI/CD)
pytest --cov --cov-report=xml

# Show missing lines
pytest --cov --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov --cov-fail-under=80
```

**Coverage.py Direct Usage (Alternative):**

```bash
# Run coverage with Django's test runner
coverage run --source='.' manage.py test

# Generate report
coverage report

# Generate HTML report
coverage html

# Show missing lines
coverage report --show-missing
```

**Coverage Configuration (.coveragerc):**

```ini
# .coveragerc
[run]
source = .
omit =
    */migrations/*
    */tests/*
    */test_*.py
    */__init__.py
    */conftest.py
    */settings/*
    manage.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__:
    if TYPE_CHECKING:

[html]
directory = htmlcov
```

**Measuring Branch Coverage:**

```bash
# Enable branch coverage
pytest --cov --cov-branch

# Or in pytest.ini
[tool.coverage.run]
branch = true
```

**Best Practices:**
- **Target 80%+ coverage** for production code (90%+ ideal)
- **Exclude auto-generated files**: migrations, settings, `__init__.py`
- **Use HTML reports** for identifying uncovered lines
- **Track coverage in CI/CD** - fail builds below threshold
- **Focus on critical paths** - 100% coverage doesn't guarantee bug-free code
- **Review uncovered code** - intentionally exclude boilerplate with `# pragma: no cover`

**Viewing Coverage Reports:**

```bash
# Terminal report
pytest --cov --cov-report=term

# Open HTML report
pytest --cov --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**CI/CD Coverage Integration:**

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest --cov --cov-report=xml --cov-report=term

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

---

### 3.2 CI/CD Integration with GitHub Actions

**Complete GitHub Actions Workflow for Django:**

```yaml
# .github/workflows/django-tests.yml
name: Django Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  PYTHON_VERSION: "3.12"
  DJANGO_VERSION: "5.2"

jobs:
  test:
    name: Test on Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
        django-version: ["4.2", "5.0", "5.2"]

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install -r requirements/test.txt
          pip install Django==${{ matrix.django-version }}

      - name: Run linting (flake8)
        run: |
          flake8 myapp myproject --max-line-length=100 --exclude=migrations

      - name: Run linting (black)
        run: |
          black --check myapp myproject

      - name: Run type checking (mypy)
        run: |
          mypy myapp myproject
        continue-on-error: true

      - name: Run migrations check
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          python manage.py makemigrations --check --dry-run

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-for-ci
          DEBUG: False
        run: |
          pytest --cov --cov-report=xml --cov-report=term --cov-fail-under=80

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: true

      - name: Upload coverage to Code Climate
        uses: paambaati/codeclimate-action@v5
        env:
          CC_TEST_REPORTER_ID: ${{ secrets.CC_TEST_REPORTER_ID }}
        with:
          coverageLocations: ./coverage.xml:coverage.py

  lint:
    name: Linting & Code Quality
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install flake8 black isort pylint

      - name: Run flake8
        run: flake8 myapp myproject

      - name: Run black
        run: black --check .

      - name: Run isort
        run: isort --check-only .

      - name: Run pylint
        run: pylint myapp myproject
        continue-on-error: true

  security:
    name: Security Checks
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install bandit safety

      - name: Run bandit (security linter)
        run: bandit -r myapp myproject

      - name: Run safety check
        run: safety check
```

**Optimized Fast Workflow (Development):**

```yaml
# .github/workflows/fast-tests.yml
name: Fast Tests

on:
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements/test.txt

      - name: Run tests (SQLite, no migrations)
        run: |
          pytest --reuse-db --nomigrations --maxfail=5
        env:
          DJANGO_SETTINGS_MODULE: myproject.settings.test
```

**requirements/test.txt:**

```txt
# Django and DRF
Django>=5.2,<6.0
djangorestframework>=3.15,<4.0

# Testing
pytest>=8.0
pytest-django>=4.10
pytest-cov>=5.0
pytest-xdist>=3.5  # Parallel test execution
factory-boy>=3.3
faker>=20.0

# Code quality
flake8>=7.0
black>=24.0
isort>=5.13
mypy>=1.8
pylint>=3.0

# Security
bandit>=1.7
safety>=3.0

# Other
psycopg2-binary>=2.9  # PostgreSQL
redis>=5.0
celery>=5.3
```

**Best Practices for CI/CD:**
- **Test matrix**: Test multiple Python/Django versions
- **Use services**: Run PostgreSQL/Redis as GitHub Actions services
- **Cache dependencies**: Use `cache: 'pip'` for faster builds
- **Parallel execution**: Use `pytest-xdist` for faster test runs
- **Fail fast**: Set `--maxfail=5` to stop early on failures
- **Security checks**: Run bandit and safety in CI
- **Coverage enforcement**: Use `--cov-fail-under=80`
- **Branch protection**: Require CI passing before merge

---

### 3.3 Django 5.x and DRF 3.15 Testing Updates

**Django 5.x Testing Changes (2024-2025):**

**Django 5.0 (Released December 2023):**
- Full Python 3.12 support
- Active updates through August 2024
- Security updates through April 2025
- No breaking testing changes

**Django 5.2 (Released April 2025):**
- PostgreSQL 14+ minimum requirement
- MySQL connections default to utf8mb4 character set
- Enhanced async testing support
- Improved test database handling

**pytest-django Updates (2024-2025):**

**Version 4.10.0 (February 2025):**
- Multiple database support (no longer experimental)
- Improved async test support
- Better Django 5.x compatibility

**Version 4.9.0 (September 2024):**
- Enhanced fixture scoping
- Performance improvements
- Bug fixes for transactional tests

**DRF 3.15 Updates (March 2024):**

```python
# DRF 3.15 introduces improved APIClient with better authentication handling
from rest_framework.test import APIClient

# New in 3.15: Improved force_authenticate with better session handling
@pytest.fixture
def api_client():
    client = APIClient()
    # Enhanced authentication now properly handles session storage
    return client

# New in 3.15: Better RequestsClient for integration testing
from rest_framework.test import RequestsClient

@pytest.fixture
def requests_client():
    """Use RequestsClient for full integration tests."""
    return RequestsClient()

@pytest.mark.django_db
def test_with_requests_client(requests_client, live_server):
    """Test using RequestsClient against live server."""
    url = f'{live_server.url}/api/articles/'
    response = requests_client.get(url)
    assert response.status_code == 200
```

**Async Testing Support (Django 5.x):**

```python
# Django 5.x improved async testing support
import pytest
from channels.testing import WebsocketCommunicator
from myapp.consumers import ChatConsumer

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_websocket_consumer():
    """Test async WebSocket consumer."""
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({"message": "Hello"})
    response = await communicator.receive_json_from()
    assert response["message"] == "Hello"

    await communicator.disconnect()

# Async view testing
from asgiref.sync import sync_to_async

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_view(authenticated_client):
    """Test async DRF view."""
    url = reverse('async-article-list')

    # Use sync_to_async for client methods
    get = sync_to_async(authenticated_client.get)
    response = await get(url)

    assert response.status_code == 200
```

**Migration Testing (Django 5.x):**

```python
# Test migrations for data integrity
@pytest.mark.django_db
def test_migration_0005_article_status():
    """Test that migration properly adds status field."""
    # Use django_migrations fixture to test migrations
    pass

# Or use --nomigrations flag for faster tests
# pytest.ini
[pytest]
addopts = --nomigrations
```

**Best Practices for Django 5.x/DRF 3.15:**
- **Use Python 3.12+** for best performance and features
- **Test async views** with `@pytest.mark.asyncio`
- **Use RequestsClient** for integration tests
- **Test multiple databases** using pytest-django's non-experimental support
- **Skip migrations in tests** with `--nomigrations` for speed
- **Use PostgreSQL 15+** for modern JSON field support

---

## 4. Best Practices

### 4.1 TDD Workflow for Django/DRF

**The Red-Green-Refactor Cycle:**

```
RED: Write failing test → GREEN: Minimal code to pass → REFACTOR: Improve code
```

**Step-by-Step TDD Workflow:**

**1. Write User Story:**

```
As an API user
I want to create a new article
So that I can publish content
```

**2. Write Failing Test (RED):**

```python
# tests/test_article_creation.py
import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
def test_create_article(authenticated_client):
    """Test creating a new article via API."""
    url = reverse('article-list')
    data = {
        'title': 'Test Article',
        'content': 'Test content',
        'status': 'draft'
    }
    response = authenticated_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == 'Test Article'
    assert Article.objects.filter(title='Test Article').exists()
```

**Run test - it fails (RED):**

```bash
$ pytest tests/test_article_creation.py
FAILED - Article model doesn't exist
```

**3. Write Minimal Code (GREEN):**

```python
# myapp/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# myapp/serializers.py
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'status', 'created_at']

# myapp/views.py
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

**Run test - it passes (GREEN):**

```bash
$ pytest tests/test_article_creation.py
PASSED
```

**4. Refactor (REFACTOR):**

```python
# Refactor: Add validation, improve serializer
class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'status', 'author', 'author_name', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters.")
        return value
```

**Run tests again - still passes:**

```bash
$ pytest tests/test_article_creation.py
PASSED
```

**Complete TDD Example - Adding Feature:**

```python
# Step 1: Write test for new feature (publish article)
@pytest.mark.django_db
def test_publish_article(authenticated_client):
    """Test publishing a draft article."""
    article = ArticleFactory(status='draft', author=authenticated_client.handler._force_user)
    url = reverse('article-publish', kwargs={'pk': article.pk})

    response = authenticated_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    article.refresh_from_db()
    assert article.status == 'published'
    assert article.published_at is not None

# Test fails - feature doesn't exist yet

# Step 2: Implement minimal feature
class ArticleViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        serializer = self.get_serializer(article)
        return Response(serializer.data)

# Test passes

# Step 3: Refactor - add validation
@action(detail=True, methods=['post'])
def publish(self, request, pk=None):
    article = self.get_object()

    if article.status == 'published':
        return Response(
            {'error': 'Article already published'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not article.category:
        return Response(
            {'error': 'Cannot publish article without category'},
            status=status.HTTP_400_BAD_REQUEST
        )

    article.status = 'published'
    article.published_at = timezone.now()
    article.save()

    serializer = self.get_serializer(article)
    return Response(serializer.data)
```

**TDD Best Practices:**
- **Write test first** - resist temptation to code before testing
- **One test, one feature** - test single behavior at a time
- **Minimal implementation** - write simplest code to pass test
- **Refactor continuously** - improve code while maintaining passing tests
- **Fast feedback loop** - tests should run in seconds
- **Test behavior, not implementation** - focus on what, not how

---

### 4.2 Test Organization and Structure

**Recommended Directory Structure:**

```
myproject/
├── myapp/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── services.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py              # App-specific fixtures
│       ├── factories.py             # Factory Boy factories
│       ├── test_models.py           # Model tests
│       ├── test_serializers.py      # Serializer tests
│       ├── test_views.py            # View/ViewSet tests
│       ├── test_permissions.py      # Permission tests
│       ├── test_services.py         # Business logic tests
│       └── integration/
│           ├── __init__.py
│           └── test_article_workflow.py
├── conftest.py                      # Global fixtures
├── pytest.ini                       # Pytest configuration
└── requirements/
    └── test.txt                     # Test dependencies
```

**File Naming Conventions:**

```python
# All test files must start with test_
test_models.py          ✓ Correct
test_views.py           ✓ Correct
models_test.py          ✗ Wrong - won't be discovered

# All test functions must start with test_
def test_user_creation():       ✓ Correct
def user_creation_test():       ✗ Wrong - won't be discovered

# All test classes must start with Test
class TestArticleModel:         ✓ Correct
class ArticleModelTest:         ✗ Wrong - won't be discovered
```

**Organizing Tests by Type:**

```python
# tests/test_models.py - Model tests
@pytest.mark.django_db
class TestArticleModel:
    """Unit tests for Article model."""

    def test_string_representation(self):
        article = ArticleFactory(title='Test Article')
        assert str(article) == 'Test Article'

    def test_slug_generation(self):
        article = ArticleFactory(title='Test Article')
        assert article.slug == 'test-article'

# tests/test_serializers.py - Serializer tests
@pytest.mark.django_db
class TestArticleSerializer:
    """Unit tests for ArticleSerializer."""

    def test_valid_serialization(self):
        article = ArticleFactory()
        serializer = ArticleSerializer(article)
        assert serializer.data['title'] == article.title

# tests/test_views.py - View tests
@pytest.mark.django_db
class TestArticleViewSet:
    """Integration tests for ArticleViewSet."""

    def test_list_articles(self, api_client):
        ArticleFactory.create_batch(3)
        url = reverse('article-list')
        response = api_client.get(url)
        assert response.status_code == 200

# tests/integration/test_article_workflow.py - End-to-end tests
@pytest.mark.django_db
class TestArticlePublishingWorkflow:
    """End-to-end tests for article publishing workflow."""

    def test_complete_article_lifecycle(self, authenticated_client):
        # Create draft article
        # Review article
        # Publish article
        # Verify published state
        pass
```

**Using Fixtures Effectively:**

```python
# conftest.py - Global fixtures
import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory

@pytest.fixture
def api_client():
    """Provide APIClient for all tests."""
    return APIClient()

@pytest.fixture
def user(db):
    """Provide a standard user."""
    return UserFactory()

@pytest.fixture
def authenticated_client(api_client, user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client

# myapp/tests/conftest.py - App-specific fixtures
import pytest
from tests.factories import ArticleFactory, CategoryFactory

@pytest.fixture
def article(db):
    """Provide a standard article."""
    return ArticleFactory()

@pytest.fixture
def published_article(db):
    """Provide a published article."""
    return ArticleFactory(status='published')

@pytest.fixture
def category(db):
    """Provide a standard category."""
    return CategoryFactory()
```

**Grouping Tests with Markers:**

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    api: API endpoint tests
    models: Model tests

# Usage in tests
@pytest.mark.unit
@pytest.mark.django_db
def test_article_creation():
    pass

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.django_db
def test_article_workflow():
    pass

# Run specific markers
pytest -m unit              # Run only unit tests
pytest -m "not slow"        # Skip slow tests
pytest -m "api and not slow"  # Run API tests except slow ones
```

**Parametrized Tests for Multiple Scenarios:**

```python
@pytest.mark.django_db
@pytest.mark.parametrize('status,expected_visibility', [
    ('draft', False),
    ('published', True),
    ('archived', False),
])
def test_article_visibility(status, expected_visibility):
    """Test article visibility based on status."""
    article = ArticleFactory(status=status)
    assert article.is_visible() == expected_visibility
```

**Best Practices:**
- **Mirror application structure** - `tests/test_models.py` mirrors `models.py`
- **One test file per module** - separate concerns clearly
- **Use descriptive names** - `test_authenticated_user_can_create_article()`
- **Group related tests in classes** - `class TestArticlePermissions:`
- **Fixtures in conftest.py** - reusable test data
- **Use markers** - organize and selectively run tests
- **Keep integration tests separate** - `tests/integration/`

---

### 4.3 Performance Testing Basics

**Why Performance Testing:**
- Identify N+1 query problems
- Benchmark API response times
- Detect performance regressions
- Optimize database queries

**Detecting N+1 Queries:**

```python
# tests/test_performance.py
import pytest
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import CaptureQueriesContext
from tests.factories import ArticleFactory, CategoryFactory

@pytest.mark.django_db
def test_article_list_query_count(api_client):
    """Test that article list doesn't have N+1 queries."""
    # Create test data
    ArticleFactory.create_batch(10)

    url = reverse('article-list')

    # Measure query count
    with CaptureQueriesContext(connection) as context:
        response = api_client.get(url)

    # Assert reasonable query count (adjust based on your setup)
    assert len(context.captured_queries) <= 3, (
        f"Too many queries: {len(context.captured_queries)}. "
        f"Possible N+1 problem."
    )
    assert response.status_code == 200

# Fix N+1 with select_related and prefetch_related
class ArticleViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article.objects.select_related('author', 'category').prefetch_related('tags')
```

**Using django-assert-num-queries:**

```python
@pytest.mark.django_db
def test_article_detail_queries(api_client, django_assert_num_queries):
    """Test exact number of queries for article detail."""
    article = ArticleFactory()
    url = reverse('article-detail', kwargs={'pk': article.pk})

    # Assert exact query count
    with django_assert_num_queries(2):
        response = api_client.get(url)

    assert response.status_code == 200
```

**Benchmarking with pytest-benchmark:**

```bash
pip install pytest-benchmark
```

```python
# tests/test_benchmarks.py
import pytest
from tests.factories import ArticleFactory

@pytest.mark.django_db
def test_article_serialization_performance(benchmark):
    """Benchmark article serialization speed."""
    articles = ArticleFactory.create_batch(100)

    def serialize_articles():
        from myapp.serializers import ArticleSerializer
        serializer = ArticleSerializer(articles, many=True)
        return serializer.data

    result = benchmark(serialize_articles)
    assert len(result) == 100

# Run benchmarks
pytest tests/test_benchmarks.py --benchmark-only
```

**Load Testing with Locust:**

```bash
pip install locust
```

```python
# locustfile.py
from locust import HttpUser, task, between

class ArticleAPIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before starting tasks."""
        response = self.client.post("/api/token/", {
            "username": "testuser",
            "password": "testpass123"
        })
        self.token = response.json()['access']
        self.client.headers = {'Authorization': f'Bearer {self.token}'}

    @task(3)
    def list_articles(self):
        """List articles (weighted 3x)."""
        self.client.get("/api/articles/")

    @task(1)
    def get_article(self):
        """Get single article (weighted 1x)."""
        self.client.get("/api/articles/1/")

    @task(1)
    def create_article(self):
        """Create article (weighted 1x)."""
        self.client.post("/api/articles/", json={
            "title": "Load Test Article",
            "content": "Content",
            "status": "draft"
        })

# Run load test
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 in browser
```

**Response Time Assertions:**

```python
import time

@pytest.mark.django_db
def test_article_list_response_time(api_client):
    """Test that article list responds within acceptable time."""
    ArticleFactory.create_batch(100)
    url = reverse('article-list')

    start_time = time.time()
    response = api_client.get(url)
    end_time = time.time()

    response_time = end_time - start_time

    assert response.status_code == 200
    assert response_time < 0.5, f"Response too slow: {response_time}s"
```

**Best Practices:**
- **Test query counts** - detect N+1 problems early
- **Use select_related/prefetch_related** - optimize database queries
- **Benchmark critical paths** - serialization, complex queries
- **Load test before production** - use Locust for realistic traffic
- **Set performance budgets** - fail tests if response time exceeds threshold
- **Monitor in CI/CD** - track performance over time

---

### 4.4 Common Anti-Patterns to Avoid

**1. Testing Implementation Instead of Behavior**

```python
# ❌ BAD - Testing implementation details
def test_article_creation_implementation():
    article = Article()
    article.title = 'Test'
    article.content = 'Content'
    article.save()
    assert article.id is not None

# ✓ GOOD - Testing behavior
@pytest.mark.django_db
def test_article_creation_behavior(authenticated_client):
    url = reverse('article-list')
    data = {'title': 'Test', 'content': 'Content'}
    response = authenticated_client.post(url, data, format='json')

    assert response.status_code == 201
    assert Article.objects.filter(title='Test').exists()
```

**2. Dependent Tests (Test Order Matters)**

```python
# ❌ BAD - Tests depend on each other
class TestArticleSequence:
    article_id = None

    def test_01_create_article(self):
        article = ArticleFactory()
        self.article_id = article.id
        assert article.id is not None

    def test_02_update_article(self):
        article = Article.objects.get(id=self.article_id)  # Depends on test_01
        article.title = 'Updated'
        article.save()

# ✓ GOOD - Each test is independent
@pytest.mark.django_db
class TestArticle:
    def test_create_article(self):
        article = ArticleFactory()
        assert article.id is not None

    def test_update_article(self):
        article = ArticleFactory()  # Create fresh data
        article.title = 'Updated'
        article.save()
        assert article.title == 'Updated'
```

**3. Overusing Fixtures / Not Keeping Tests Independent**

```python
# ❌ BAD - Shared mutable fixture state
@pytest.fixture
def articles(db):
    return ArticleFactory.create_batch(5)

def test_delete_article(articles):
    articles[0].delete()
    assert Article.objects.count() == 4

def test_count_articles(articles):
    # This test fails if test_delete_article runs first
    assert Article.objects.count() == 5

# ✓ GOOD - Fresh fixtures per test
@pytest.fixture
def articles(db):
    """Create fresh articles for each test."""
    return ArticleFactory.create_batch(5)

@pytest.mark.django_db
def test_delete_article():
    articles = ArticleFactory.create_batch(5)
    articles[0].delete()
    assert Article.objects.count() == 4

@pytest.mark.django_db
def test_count_articles():
    ArticleFactory.create_batch(5)
    assert Article.objects.count() == 5
```

**4. Not Mocking External Services**

```python
# ❌ BAD - Calling real external API
def test_fetch_weather():
    weather = fetch_weather_from_api('London')  # Real API call
    assert weather['temperature'] > 0

# ✓ GOOD - Mocking external API
@patch('myapp.services.requests.get')
def test_fetch_weather(mock_get):
    mock_get.return_value.json.return_value = {
        'temperature': 15,
        'condition': 'Cloudy'
    }

    weather = fetch_weather_from_api('London')
    assert weather['temperature'] == 15
```

**5. Testing Django Framework / Third-Party Code**

```python
# ❌ BAD - Testing Django's ORM (already tested by Django)
def test_django_save():
    article = ArticleFactory()
    article.save()
    assert Article.objects.filter(pk=article.pk).exists()

# ✓ GOOD - Test your business logic
def test_article_auto_slug_generation():
    """Test custom slug generation logic."""
    article = ArticleFactory(title='Test Article')
    assert article.slug == 'test-article'
```

**6. Unclear Test Names**

```python
# ❌ BAD - Vague test names
def test_article():
    pass

def test_api():
    pass

def test_1():
    pass

# ✓ GOOD - Descriptive test names
def test_authenticated_user_can_create_article():
    pass

def test_unauthenticated_user_receives_401_on_create():
    pass

def test_article_requires_title_validation():
    pass
```

**7. Overly Complex Tests**

```python
# ❌ BAD - Testing too many things at once
@pytest.mark.django_db
def test_article_everything(authenticated_client):
    # Create article
    response = authenticated_client.post('/api/articles/', {...})
    assert response.status_code == 201

    # Update article
    article_id = response.data['id']
    response = authenticated_client.patch(f'/api/articles/{article_id}/', {...})
    assert response.status_code == 200

    # Delete article
    response = authenticated_client.delete(f'/api/articles/{article_id}/')
    assert response.status_code == 204

# ✓ GOOD - One test, one behavior
@pytest.mark.django_db
def test_create_article(authenticated_client):
    response = authenticated_client.post('/api/articles/', {...})
    assert response.status_code == 201

@pytest.mark.django_db
def test_update_article(authenticated_client):
    article = ArticleFactory()
    response = authenticated_client.patch(f'/api/articles/{article.id}/', {...})
    assert response.status_code == 200

@pytest.mark.django_db
def test_delete_article(authenticated_client):
    article = ArticleFactory()
    response = authenticated_client.delete(f'/api/articles/{article.id}/')
    assert response.status_code == 204
```

**8. Not Using Factory Boy (Relying on Fixtures)**

```python
# ❌ BAD - Using JSON fixtures (hard to maintain)
# fixtures/articles.json
[
    {
        "model": "myapp.article",
        "pk": 1,
        "fields": {
            "title": "Test Article",
            "author": 1,  # Hardcoded foreign key
            "category": 2
        }
    }
]

# ✓ GOOD - Using Factory Boy (flexible, maintainable)
class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker('sentence')
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
```

**9. Ignoring Test Coverage**

```python
# ❌ BAD - No coverage checking
pytest

# ✓ GOOD - Enforce minimum coverage
pytest --cov --cov-fail-under=80
```

**10. Not Testing Edge Cases**

```python
# ❌ BAD - Only testing happy path
def test_create_article(authenticated_client):
    data = {'title': 'Test', 'content': 'Content'}
    response = authenticated_client.post('/api/articles/', data)
    assert response.status_code == 201

# ✓ GOOD - Testing edge cases
@pytest.mark.django_db
class TestArticleCreation:
    def test_create_article_success(self, authenticated_client):
        """Happy path."""
        data = {'title': 'Valid Title', 'content': 'Content'}
        response = authenticated_client.post('/api/articles/', data)
        assert response.status_code == 201

    def test_create_article_missing_title(self, authenticated_client):
        """Edge case: missing required field."""
        data = {'content': 'Content'}
        response = authenticated_client.post('/api/articles/', data)
        assert response.status_code == 400

    def test_create_article_title_too_short(self, authenticated_client):
        """Edge case: validation error."""
        data = {'title': 'Bad', 'content': 'Content'}
        response = authenticated_client.post('/api/articles/', data)
        assert response.status_code == 400

    def test_create_article_unauthenticated(self, api_client):
        """Edge case: authentication required."""
        data = {'title': 'Test', 'content': 'Content'}
        response = api_client.post('/api/articles/', data)
        assert response.status_code == 401
```

---

## Summary: Key Takeaways

1. **Use pytest-django** (4.10.0+) for modern Django/DRF testing with minimal boilerplate
2. **Factory Boy + Faker** for maintainable test data generation
3. **APIClient with fixtures** for clean, reusable API testing
4. **Test all layers**: models, serializers, views, permissions
5. **Mock external services** to keep tests fast and reliable
6. **Coverage 80%+** with pytest-cov, track in CI/CD
7. **GitHub Actions** for automated testing on push/PR
8. **TDD workflow**: Red → Green → Refactor
9. **Organize tests** by type (models, views, integration)
10. **Avoid anti-patterns**: test behavior not implementation, keep tests independent

---

## Action Items

1. **Set up testing environment:**
   ```bash
   pip install pytest-django pytest-cov factory-boy faker
   ```

2. **Configure pytest.ini:**
   ```ini
   [pytest]
   DJANGO_SETTINGS_MODULE = myproject.settings.test
   addopts = --cov --cov-report=html --cov-fail-under=80 --reuse-db
   ```

3. **Create test structure:**
   ```
   myapp/tests/
   ├── conftest.py
   ├── factories.py
   ├── test_models.py
   ├── test_serializers.py
   └── test_views.py
   ```

4. **Set up GitHub Actions workflow** (see section 3.2)

5. **Adopt TDD workflow** for new features (Red-Green-Refactor)

6. **Measure and improve coverage:**
   ```bash
   pytest --cov --cov-report=html
   open htmlcov/index.html
   ```

---

## Sources

- [Django REST Framework 3.15 Official Documentation](https://www.django-rest-framework.org/api-guide/testing/) - Official DRF testing guide (March 2024)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/) - Official pytest-django docs with 4.10.0+ updates (February 2025)
- [Django 5.2 Release Notes](https://docs.djangoproject.com/en/5.2/releases/5.2/) - Django 5.2 testing changes (April 2025)
- [coverage.py 7.10.7 Documentation](https://coverage.readthedocs.io/) - Coverage.py official docs (September 2025)
- [Factory Boy Official Documentation](https://factoryboy.readthedocs.io/) - Factory Boy recipes and best practices (2024)
- [GitHub Actions Django CI/CD](https://medium.com/intelligentmachines/github-actions-end-to-end-ci-cd-pipeline-for-django-5d48d6f00abf) - End-to-end CI/CD pipeline guide (2024)
- [Django Testing Best Practices](https://codezup.com/django-testing-best-practices-unit-tests-integration-tests/) - Comprehensive testing guide (2024)
- [Mocking External APIs in Django](https://medium.com/@epatrickk0505/building-reliable-django-applications-with-software-testing-mocks-external-apis-and-quality-d45aa0c581fa) - Mocking strategies and best practices (May 2025)

---

## Caveats

- **Version compatibility**: This guide targets Django 4.2-5.2, DRF 3.14-3.15, and pytest-django 4.9.0+. Always check compatibility matrices for your specific versions.
- **Database differences**: Examples use PostgreSQL; adjust connection strings and features for MySQL/SQLite.
- **Performance trade-offs**: Using Factory Boy and pytest fixtures adds slight overhead compared to hardcoded test data, but maintainability gains outweigh performance costs.
- **Coverage isn't everything**: 100% coverage doesn't guarantee bug-free code; focus on testing critical paths and edge cases.
- **Async testing**: Django 5.x async testing support is still evolving; some features may require additional configuration.
- **Tool preferences**: pytest-django vs Django TestCase is partly subjective; choose based on team expertise and project needs.
