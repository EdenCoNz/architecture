"""
Tests for storing user information (Story 20.7).

Tests that focus specifically on data persistence:
- Given a new user logs in, when their information is submitted,
  then their name and email should be stored
- Given an existing user logs in, when their email matches a stored record,
  then their existing information should be retrieved
- Given a user logs in, when their name has changed,
  then the stored information should be updated
- Given user information is stored, when queried by email,
  then the system should return the user's details
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.serializers import BasicLoginSerializer

User = get_user_model()


class StoreUserInformationTests(APITestCase):
    """
    Test cases specifically for Story 20.7: Store user information.

    These tests verify that user data is correctly persisted to the database
    during basic login operations.
    """

    def setUp(self):
        """Set up test data."""
        self.url = reverse("auth:basic_login")

    def test_new_user_stores_name_and_email(self):
        """
        AC1: Given a new user logs in, when their information is submitted,
        then their name and email should be stored.
        """
        # Verify no user exists yet
        self.assertFalse(User.objects.filter(email="new.user@example.com").exists())

        # Submit login information for new user
        response = self.client.post(
            self.url,
            data={
                "name": "Alice Johnson",
                "email": "new.user@example.com",
            },
            format="json",
        )

        # Verify successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_new_user"])

        # Verify user information is stored in database
        user = User.objects.get(email="new.user@example.com")
        self.assertEqual(user.email, "new.user@example.com")
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Johnson")
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.date_joined)

    def test_existing_user_retrieves_stored_information(self):
        """
        AC2: Given an existing user logs in, when their email matches a stored record,
        then their existing information should be retrieved.
        """
        # Create existing user with stored information
        existing_user = User.objects.create(
            email="existing.user@example.com",
            first_name="Bob",
            last_name="Smith",
            is_active=True,
        )
        original_date_joined = existing_user.date_joined

        # Submit login with same email
        response = self.client.post(
            self.url,
            data={
                "name": "Bob Smith",  # Same name
                "email": "existing.user@example.com",
            },
            format="json",
        )

        # Verify successful login
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_new_user"])

        # Verify existing information is retrieved (not a new user created)
        self.assertEqual(User.objects.filter(email="existing.user@example.com").count(), 1)

        # Verify user information matches stored data
        self.assertEqual(response.data["user"]["id"], existing_user.id)
        self.assertEqual(response.data["user"]["email"], "existing.user@example.com")
        self.assertEqual(response.data["user"]["first_name"], "Bob")
        self.assertEqual(response.data["user"]["last_name"], "Smith")

        # Verify date_joined is preserved (proves it's the same user)
        user = User.objects.get(email="existing.user@example.com")
        self.assertEqual(user.date_joined, original_date_joined)

    def test_existing_user_updates_changed_name(self):
        """
        AC3: Given a user logs in, when their name has changed,
        then the stored information should be updated.
        """
        # Create existing user with original name
        existing_user = User.objects.create(
            email="update.user@example.com",
            first_name="Charlie",
            last_name="Brown",
            is_active=True,
        )
        original_id = existing_user.id
        original_date_joined = existing_user.date_joined

        # Submit login with updated name
        response = self.client.post(
            self.url,
            data={
                "name": "Charlotte Green",  # Changed name
                "email": "update.user@example.com",
            },
            format="json",
        )

        # Verify successful login
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_new_user"])

        # Verify only one user exists (not a duplicate)
        self.assertEqual(User.objects.filter(email="update.user@example.com").count(), 1)

        # Verify name is updated in database
        user = User.objects.get(email="update.user@example.com")
        self.assertEqual(user.id, original_id)  # Same user
        self.assertEqual(user.first_name, "Charlotte")  # Updated first name
        self.assertEqual(user.last_name, "Green")  # Updated last name
        self.assertEqual(user.date_joined, original_date_joined)  # Preserved

        # Verify response reflects updated information
        self.assertEqual(response.data["user"]["first_name"], "Charlotte")
        self.assertEqual(response.data["user"]["last_name"], "Green")

    def test_query_user_by_email_returns_details(self):
        """
        AC4: Given user information is stored, when queried by email,
        then the system should return the user's details.
        """
        # Store user information via basic login
        self.client.post(
            self.url,
            data={
                "name": "David Wilson",
                "email": "query.user@example.com",
            },
            format="json",
        )

        # Query user by email from database
        user = User.objects.get(email="query.user@example.com")

        # Verify all user details are returned
        self.assertEqual(user.email, "query.user@example.com")
        self.assertEqual(user.first_name, "David")
        self.assertEqual(user.last_name, "Wilson")
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.id)
        self.assertIsNotNone(user.date_joined)

    def test_email_normalized_for_storage(self):
        """
        Test that emails are normalized to lowercase before storage,
        ensuring case-insensitive lookups work correctly.
        """
        # Submit with uppercase email
        response = self.client.post(
            self.url,
            data={
                "name": "Emma Davis",
                "email": "EMMA.DAVIS@EXAMPLE.COM",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify email is stored in lowercase
        user = User.objects.get(email="emma.davis@example.com")
        self.assertEqual(user.email, "emma.davis@example.com")

        # Verify subsequent login with different case retrieves same user
        response2 = self.client.post(
            self.url,
            data={
                "name": "Emma Davis",
                "email": "emma.DAVIS@example.com",  # Mixed case
            },
            format="json",
        )

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertFalse(response2.data["is_new_user"])
        self.assertEqual(response2.data["user"]["id"], user.id)

    def test_multiple_users_stored_independently(self):
        """
        Test that multiple users can be stored and retrieved independently.
        """
        # Create first user
        response1 = self.client.post(
            self.url,
            data={
                "name": "User One",
                "email": "user1@example.com",
            },
            format="json",
        )

        # Create second user
        response2 = self.client.post(
            self.url,
            data={
                "name": "User Two",
                "email": "user2@example.com",
            },
            format="json",
        )

        # Verify both users created successfully
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Verify both users stored in database with correct information
        user1 = User.objects.get(email="user1@example.com")
        user2 = User.objects.get(email="user2@example.com")

        self.assertEqual(user1.first_name, "User")
        self.assertEqual(user1.last_name, "One")
        self.assertEqual(user2.first_name, "User")
        self.assertEqual(user2.last_name, "Two")
        self.assertNotEqual(user1.id, user2.id)

    def test_name_sanitization_on_storage(self):
        """
        Test that HTML tags are stripped from names before storage (security).
        """
        response = self.client.post(
            self.url,
            data={
                "name": "<script>alert('xss')</script>Frank <b>Miller</b>",
                "email": "frank@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify HTML tags are stripped before storage
        user = User.objects.get(email="frank@example.com")
        self.assertNotIn("<script>", user.first_name)
        self.assertNotIn("</script>", user.first_name)
        self.assertNotIn("<b>", user.last_name)
        self.assertNotIn("</b>", user.last_name)
        # Should contain the sanitized name
        self.assertIn("Frank", user.first_name)
        self.assertIn("Miller", user.last_name)

    def test_user_active_status_set_on_creation(self):
        """
        Test that new users are created with is_active=True.
        """
        response = self.client.post(
            self.url,
            data={
                "name": "Grace Hopper",
                "email": "grace@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify user is active by default
        user = User.objects.get(email="grace@example.com")
        self.assertTrue(user.is_active)


class BasicLoginSerializerPersistenceTests(TestCase):
    """
    Unit tests for the BasicLoginSerializer's data persistence methods.
    """

    def test_create_or_update_user_creates_new_user(self):
        """Test create_or_update_user creates a new user when email doesn't exist."""
        serializer = BasicLoginSerializer()
        validated_data = {
            "name": "Henry Adams",
            "email": "henry@example.com",
        }

        # Verify no user exists
        self.assertFalse(User.objects.filter(email="henry@example.com").exists())

        # Create user
        user, is_new_user = serializer.create_or_update_user(validated_data)

        # Verify user was created
        self.assertTrue(is_new_user)
        self.assertEqual(user.email, "henry@example.com")
        self.assertEqual(user.first_name, "Henry")
        self.assertEqual(user.last_name, "Adams")
        self.assertTrue(user.is_active)

        # Verify user is in database
        db_user = User.objects.get(email="henry@example.com")
        self.assertEqual(db_user.id, user.id)

    def test_create_or_update_user_updates_existing_user(self):
        """Test create_or_update_user updates existing user when email matches."""
        # Create existing user
        existing_user = User.objects.create(
            email="isabel@example.com",
            first_name="Isabel",
            last_name="Rodriguez",
            is_active=True,
        )
        original_id = existing_user.id

        # Update user with new name
        serializer = BasicLoginSerializer()
        validated_data = {
            "name": "Isabella Garcia",  # Changed name
            "email": "isabel@example.com",
        }

        user, is_new_user = serializer.create_or_update_user(validated_data)

        # Verify user was updated, not created
        self.assertFalse(is_new_user)
        self.assertEqual(user.id, original_id)
        self.assertEqual(user.email, "isabel@example.com")
        self.assertEqual(user.first_name, "Isabella")
        self.assertEqual(user.last_name, "Garcia")

        # Verify only one user exists
        self.assertEqual(User.objects.filter(email="isabel@example.com").count(), 1)

    def test_parse_name_splits_correctly(self):
        """Test parse_name correctly splits full names into first and last."""
        serializer = BasicLoginSerializer()

        # Single word
        first, last = serializer.parse_name("Madonna")
        self.assertEqual(first, "Madonna")
        self.assertEqual(last, "")

        # Two words
        first, last = serializer.parse_name("John Doe")
        self.assertEqual(first, "John")
        self.assertEqual(last, "Doe")

        # Multiple words (last name contains space)
        first, last = serializer.parse_name("Mary Jane Watson")
        self.assertEqual(first, "Mary")
        self.assertEqual(last, "Jane Watson")

    def test_user_password_not_set_on_basic_login(self):
        """
        Test that users created via basic login don't have a password set.
        This allows them to later set a password if needed.
        """
        serializer = BasicLoginSerializer()
        validated_data = {
            "name": "Jack Thompson",
            "email": "jack@example.com",
        }

        user, is_new_user = serializer.create_or_update_user(validated_data)

        # Verify user has no usable password
        self.assertFalse(user.has_usable_password())

    def test_existing_user_password_preserved_on_update(self):
        """
        Test that if an existing user has a password, it's preserved when
        updating their name via basic login.
        """
        # Create user with password
        existing_user = User.objects.create(
            email="kate@example.com",
            first_name="Kate",
            last_name="Williams",
            is_active=True,
        )
        existing_user.set_password("SecurePassword123!")
        existing_user.save()

        # Update via basic login
        serializer = BasicLoginSerializer()
        validated_data = {
            "name": "Katherine Wilson",  # Changed name
            "email": "kate@example.com",
        }

        user, is_new_user = serializer.create_or_update_user(validated_data)

        # Verify password is still valid
        self.assertTrue(user.check_password("SecurePassword123!"))
        self.assertTrue(user.has_usable_password())
