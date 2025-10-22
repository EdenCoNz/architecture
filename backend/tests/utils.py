"""
Test utilities and helper functions.

This module provides common utilities and helper functions for writing tests.
Includes assertions, API helpers, authentication utilities, and test data helpers.
"""

import json
from typing import Dict, Any, Optional, List
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class APITestHelper:
    """
    Helper class for testing API endpoints.

    Provides utilities for making API requests, handling authentication,
    and asserting on responses.

    Examples:
        helper = APITestHelper(api_client)
        response = helper.get('/api/v1/users/')
        helper.assert_success(response)
    """

    def __init__(self, client: APIClient):
        """
        Initialize with an API client.

        Args:
            client: Django REST Framework APIClient instance
        """
        self.client = client

    def authenticate(self, user):
        """
        Authenticate the client with a user's JWT token.

        Args:
            user: User instance to authenticate as

        Returns:
            tuple: (access_token, refresh_token)

        Examples:
            helper = APITestHelper(api_client)
            access, refresh = helper.authenticate(user)
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        return access_token, refresh_token

    def clear_credentials(self):
        """
        Clear authentication credentials.

        Examples:
            helper = APITestHelper(api_client)
            helper.authenticate(user)
            helper.clear_credentials()  # Now unauthenticated
        """
        self.client.credentials()

    def get(self, url: str, **kwargs):
        """
        Make GET request.

        Args:
            url: URL to request
            **kwargs: Additional arguments for the request

        Returns:
            Response object

        Examples:
            response = helper.get('/api/v1/users/')
            response = helper.get('/api/v1/users/?page=2')
        """
        return self.client.get(url, **kwargs)

    def post(self, url: str, data: Optional[Dict] = None, **kwargs):
        """
        Make POST request.

        Args:
            url: URL to request
            data: Request payload
            **kwargs: Additional arguments for the request

        Returns:
            Response object

        Examples:
            data = {'email': 'test@example.com', 'password': 'pass123'}
            response = helper.post('/api/v1/auth/register/', data)
        """
        return self.client.post(url, data, format='json', **kwargs)

    def put(self, url: str, data: Optional[Dict] = None, **kwargs):
        """
        Make PUT request.

        Args:
            url: URL to request
            data: Request payload
            **kwargs: Additional arguments for the request

        Returns:
            Response object
        """
        return self.client.put(url, data, format='json', **kwargs)

    def patch(self, url: str, data: Optional[Dict] = None, **kwargs):
        """
        Make PATCH request.

        Args:
            url: URL to request
            data: Request payload
            **kwargs: Additional arguments for the request

        Returns:
            Response object
        """
        return self.client.patch(url, data, format='json', **kwargs)

    def delete(self, url: str, **kwargs):
        """
        Make DELETE request.

        Args:
            url: URL to request
            **kwargs: Additional arguments for the request

        Returns:
            Response object
        """
        return self.client.delete(url, **kwargs)

    @staticmethod
    def assert_success(response, status_code: int = 200):
        """
        Assert that response was successful.

        Args:
            response: Response object
            status_code: Expected status code (default: 200)

        Examples:
            response = helper.get('/api/v1/users/')
            helper.assert_success(response)
            helper.assert_success(response, 201)  # Created
        """
        assert response.status_code == status_code, \
            f"Expected {status_code}, got {response.status_code}: {response.data}"

    @staticmethod
    def assert_error(response, status_code: int = 400):
        """
        Assert that response was an error.

        Args:
            response: Response object
            status_code: Expected error status code (default: 400)

        Examples:
            response = helper.post('/api/v1/auth/login/', {})
            helper.assert_error(response)
            helper.assert_error(response, 401)  # Unauthorized
        """
        assert response.status_code == status_code, \
            f"Expected {status_code}, got {response.status_code}"

    @staticmethod
    def assert_has_keys(data: Dict, keys: List[str]):
        """
        Assert that data contains all specified keys.

        Args:
            data: Dictionary to check
            keys: List of required keys

        Examples:
            helper.assert_has_keys(response.data, ['id', 'email', 'first_name'])
        """
        for key in keys:
            assert key in data, f"Missing key '{key}' in response data"

    @staticmethod
    def assert_missing_keys(data: Dict, keys: List[str]):
        """
        Assert that data does NOT contain specified keys.

        Args:
            data: Dictionary to check
            keys: List of keys that should not be present

        Examples:
            helper.assert_missing_keys(response.data, ['password', 'secret_key'])
        """
        for key in keys:
            assert key not in data, f"Key '{key}' should not be in response data"

    @staticmethod
    def assert_paginated(response):
        """
        Assert that response is a paginated result.

        Args:
            response: Response object

        Examples:
            response = helper.get('/api/v1/users/')
            helper.assert_paginated(response)
        """
        assert 'count' in response.data, "Missing 'count' in paginated response"
        assert 'results' in response.data, "Missing 'results' in paginated response"


class AuthenticationTestHelper:
    """
    Helper class for testing authentication flows.

    Provides utilities for login, logout, token refresh, and permission testing.

    Examples:
        auth_helper = AuthenticationTestHelper(api_client)
        tokens = auth_helper.login(user)
    """

    def __init__(self, client: APIClient):
        """
        Initialize with an API client.

        Args:
            client: Django REST Framework APIClient instance
        """
        self.client = client
        self.api_helper = APITestHelper(client)

    def login(self, email: str, password: str):
        """
        Perform login and return tokens.

        Args:
            email: User email
            password: User password

        Returns:
            dict: Response data containing tokens

        Examples:
            tokens = auth_helper.login('user@example.com', 'pass123')
            access_token = tokens['access']
        """
        response = self.api_helper.post('/api/v1/auth/login/', {
            'email': email,
            'password': password
        })
        return response.data

    def logout(self, refresh_token: str):
        """
        Perform logout.

        Args:
            refresh_token: Refresh token to blacklist

        Returns:
            Response object

        Examples:
            auth_helper.logout(refresh_token)
        """
        return self.api_helper.post('/api/v1/auth/logout/', {
            'refresh': refresh_token
        })

    def refresh_token(self, refresh_token: str):
        """
        Refresh access token.

        Args:
            refresh_token: Refresh token

        Returns:
            dict: Response data with new tokens

        Examples:
            new_tokens = auth_helper.refresh_token(refresh_token)
            new_access = new_tokens['access']
        """
        response = self.api_helper.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        })
        return response.data

    def assert_authenticated(self, response):
        """
        Assert that the user is authenticated (has valid token).

        Args:
            response: Response from a protected endpoint

        Examples:
            response = api_client.get('/api/v1/auth/me/')
            auth_helper.assert_authenticated(response)
        """
        assert response.status_code != 401, "User should be authenticated"

    def assert_unauthenticated(self, response):
        """
        Assert that the user is not authenticated.

        Args:
            response: Response from a protected endpoint

        Examples:
            response = api_client.get('/api/v1/auth/me/')
            auth_helper.assert_unauthenticated(response)
        """
        assert response.status_code == 401, "User should not be authenticated"


class AssertionHelper:
    """
    Additional assertion helpers for common test scenarios.

    Examples:
        AssertionHelper.assert_email_sent(len(mail.outbox))
        AssertionHelper.assert_valid_uuid(user.id)
    """

    @staticmethod
    def assert_email_sent(count: int = 1):
        """
        Assert that emails were sent.

        Args:
            count: Expected number of emails

        Examples:
            from django.core import mail
            # ... trigger email sending ...
            AssertionHelper.assert_email_sent(1)
        """
        from django.core import mail
        assert len(mail.outbox) == count, \
            f"Expected {count} email(s), but {len(mail.outbox)} were sent"

    @staticmethod
    def assert_valid_uuid(value: str):
        """
        Assert that value is a valid UUID.

        Args:
            value: String to validate as UUID

        Examples:
            AssertionHelper.assert_valid_uuid(str(user.id))
        """
        from uuid import UUID
        try:
            UUID(str(value))
        except (ValueError, TypeError):
            raise AssertionError(f"'{value}' is not a valid UUID")

    @staticmethod
    def assert_valid_timestamp(value: str):
        """
        Assert that value is a valid ISO 8601 timestamp.

        Args:
            value: String to validate as timestamp

        Examples:
            AssertionHelper.assert_valid_timestamp(response.data['created_at'])
        """
        from datetime import datetime
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            raise AssertionError(f"'{value}' is not a valid ISO 8601 timestamp")

    @staticmethod
    def assert_dict_subset(subset: Dict, superset: Dict):
        """
        Assert that subset is contained in superset.

        Args:
            subset: Dictionary with expected key-value pairs
            superset: Dictionary to check against

        Examples:
            expected = {'email': 'test@example.com', 'is_active': True}
            AssertionHelper.assert_dict_subset(expected, response.data)
        """
        for key, value in subset.items():
            assert key in superset, f"Missing key '{key}' in superset"
            assert superset[key] == value, \
                f"Expected {key}={value}, got {key}={superset[key]}"


class DatabaseTestHelper:
    """
    Helper class for database-related test operations.

    Examples:
        DatabaseTestHelper.assert_object_exists(User, email='test@example.com')
        DatabaseTestHelper.assert_count(User, 5)
    """

    @staticmethod
    def assert_object_exists(model, **filters):
        """
        Assert that an object exists in the database.

        Args:
            model: Django model class
            **filters: Query filters

        Examples:
            DatabaseTestHelper.assert_object_exists(User, email='test@example.com')
        """
        exists = model.objects.filter(**filters).exists()
        assert exists, f"No {model.__name__} found with filters: {filters}"

    @staticmethod
    def assert_object_not_exists(model, **filters):
        """
        Assert that an object does NOT exist in the database.

        Args:
            model: Django model class
            **filters: Query filters

        Examples:
            DatabaseTestHelper.assert_object_not_exists(User, email='deleted@example.com')
        """
        exists = model.objects.filter(**filters).exists()
        assert not exists, f"{model.__name__} found with filters: {filters}, but should not exist"

    @staticmethod
    def assert_count(model, expected_count: int, **filters):
        """
        Assert the count of objects in the database.

        Args:
            model: Django model class
            expected_count: Expected number of objects
            **filters: Optional query filters

        Examples:
            DatabaseTestHelper.assert_count(User, 5)
            DatabaseTestHelper.assert_count(User, 2, is_active=True)
        """
        actual_count = model.objects.filter(**filters).count()
        assert actual_count == expected_count, \
            f"Expected {expected_count} {model.__name__} objects, found {actual_count}"

    @staticmethod
    def get_or_fail(model, **filters):
        """
        Get object from database or fail test.

        Args:
            model: Django model class
            **filters: Query filters

        Returns:
            Model instance

        Examples:
            user = DatabaseTestHelper.get_or_fail(User, email='test@example.com')
        """
        try:
            return model.objects.get(**filters)
        except model.DoesNotExist:
            raise AssertionError(f"No {model.__name__} found with filters: {filters}")
        except model.MultipleObjectsReturned:
            raise AssertionError(f"Multiple {model.__name__} found with filters: {filters}")


class MockHelper:
    """
    Helper class for working with mocks in tests.

    Examples:
        MockHelper.assert_called_with_subset(mock_func, {'key': 'value'})
    """

    @staticmethod
    def assert_called_with_subset(mock, expected_args: Dict):
        """
        Assert that mock was called with arguments containing expected subset.

        Args:
            mock: Mock object
            expected_args: Expected argument subset

        Examples:
            from unittest.mock import Mock
            mock_func = Mock()
            mock_func(name='John', age=30, city='NYC')
            MockHelper.assert_called_with_subset(mock_func, {'name': 'John', 'age': 30})
        """
        assert mock.called, "Mock was not called"
        call_args = mock.call_args
        if call_args is None:
            raise AssertionError("Mock was not called")

        # Check both args and kwargs
        for key, value in expected_args.items():
            if key in call_args.kwargs:
                assert call_args.kwargs[key] == value, \
                    f"Expected {key}={value}, got {key}={call_args.kwargs[key]}"
            else:
                raise AssertionError(f"Key '{key}' not found in mock call arguments")


# Convenient imports for test files
__all__ = [
    'APITestHelper',
    'AuthenticationTestHelper',
    'AssertionHelper',
    'DatabaseTestHelper',
    'MockHelper',
]
