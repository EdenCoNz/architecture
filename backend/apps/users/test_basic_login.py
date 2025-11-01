"""
Tests for basic login functionality (Story 20.6).

Tests the BasicLoginView and BasicLoginSerializer to ensure:
- Users can log in with just name and email
- New users are created automatically
- Existing users' names are updated
- JWT tokens are generated correctly
- Validation errors are returned properly
- Rate limiting is enforced
- Inactive accounts are rejected
"""

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class BasicLoginViewTests(APITestCase):
    """Test cases for the basic login endpoint."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("auth:basic_login")
        self.valid_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
        }

    def test_basic_login_new_user(self):
        """Test basic login creates new user and returns tokens."""
        response = self.client.post(self.url, data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Account created successfully.")
        self.assertEqual(response.data["user"]["email"], "john.doe@example.com")
        self.assertEqual(response.data["user"]["first_name"], "John")
        self.assertEqual(response.data["user"]["last_name"], "Doe")
        self.assertTrue(response.data["is_new_user"])
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Verify user was created in database
        user = User.objects.get(email="john.doe@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertTrue(user.is_active)

    def test_basic_login_existing_user(self):
        """Test basic login with existing user updates name and returns tokens."""
        # Create existing user
        user = User.objects.create(
            email="john.doe@example.com",
            first_name="Jane",
            last_name="Smith",
            is_active=True,
        )

        # Login with updated name
        response = self.client.post(self.url, data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Login successful.")
        self.assertEqual(response.data["user"]["email"], "john.doe@example.com")
        self.assertEqual(response.data["user"]["first_name"], "John")
        self.assertEqual(response.data["user"]["last_name"], "Doe")
        self.assertFalse(response.data["is_new_user"])
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Verify name was updated
        user.refresh_from_db()
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

    def test_basic_login_missing_name(self):
        """Test basic login rejects request with missing name."""
        data = {"email": "john.doe@example.com"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "This field is required.")

    def test_basic_login_missing_email(self):
        """Test basic login rejects request with missing email."""
        data = {"name": "John Doe"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "This field is required.")

    def test_basic_login_empty_name(self):
        """Test basic login rejects request with empty name."""
        data = {"name": "   ", "email": "john.doe@example.com"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "This field may not be blank.")

    def test_basic_login_invalid_email_format(self):
        """Test basic login rejects request with invalid email format."""
        data = {"name": "John Doe", "email": "invalid-email"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Enter a valid email address.")

    def test_basic_login_email_case_insensitive(self):
        """Test email is normalized to lowercase."""
        data = {"name": "John Doe", "email": "JOHN.DOE@EXAMPLE.COM"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["email"], "john.doe@example.com")

        # Verify user email is lowercase
        user = User.objects.get(email="john.doe@example.com")
        self.assertEqual(user.email, "john.doe@example.com")

    def test_basic_login_name_with_html_tags(self):
        """Test name sanitization removes HTML tags."""
        data = {"name": "<script>alert('xss')</script>John Doe", "email": "john@example.com"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # HTML tags should be stripped
        user = User.objects.get(email="john@example.com")
        self.assertNotIn("<script>", user.first_name)
        self.assertNotIn("</script>", user.first_name)

    def test_basic_login_single_word_name(self):
        """Test single word name (no space) sets only first_name."""
        data = {"name": "Madonna", "email": "madonna@example.com"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["first_name"], "Madonna")
        self.assertEqual(response.data["user"]["last_name"], "")

    def test_basic_login_multiple_word_name(self):
        """Test multiple word name splits on first space."""
        data = {"name": "Mary Jane Watson", "email": "mary@example.com"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["first_name"], "Mary")
        self.assertEqual(response.data["user"]["last_name"], "Jane Watson")

    def test_basic_login_inactive_account(self):
        """Test basic login rejects inactive accounts."""
        # Create inactive user
        User.objects.create(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            is_active=False,
        )

        response = self.client.post(self.url, data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "This account has been deactivated. Please contact support.",
        )

    def test_basic_login_jwt_tokens_valid(self):
        """Test JWT tokens returned are valid and can be used."""
        response = self.client.post(self.url, data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get tokens
        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        # Verify access token can be used to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_response = self.client.get(reverse("auth:me"))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "john.doe@example.com")

        # Verify refresh token can be used to get new access token
        refresh_response = self.client.post(
            reverse("auth:token_refresh"),
            data={"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_basic_login_name_max_length(self):
        """Test name validation enforces max length."""
        # Name longer than 255 characters
        long_name = "A" * 256
        data = {"name": long_name, "email": "test@example.com"}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_basic_login_email_max_length(self):
        """Test email validation enforces max length."""
        # Email longer than 254 characters
        long_email = "a" * 240 + "@example.com"
        data = {"name": "John Doe", "email": long_email}
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    @override_settings(RATELIMIT_ENABLE=True)
    def test_basic_login_rate_limiting(self):
        """Test rate limiting is enforced (10 requests per minute per IP)."""
        # This test verifies the rate limit decorator is in place
        # Actual rate limiting behavior depends on django-ratelimit configuration
        # We can verify the decorator is applied by checking the view's attributes
        from apps.users.views import BasicLoginView

        # Check that rate limit decorator was applied
        # The decorator adds attributes to the dispatch method
        self.assertTrue(hasattr(BasicLoginView.dispatch, "_django_ratelimit_decorated"))

    def test_basic_login_response_structure(self):
        """Test response contains all required fields per API contract."""
        response = self.client.post(self.url, data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify response structure matches contract
        self.assertIn("message", response.data)
        self.assertIn("user", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("is_new_user", response.data)

        # Verify user object structure
        user_data = response.data["user"]
        self.assertIn("id", user_data)
        self.assertIn("email", user_data)
        self.assertIn("first_name", user_data)
        self.assertIn("last_name", user_data)
        self.assertIn("is_active", user_data)
        self.assertIn("date_joined", user_data)


class BasicLoginSerializerTests(APITestCase):
    """Test cases for the BasicLoginSerializer."""

    def test_parse_name_single_word(self):
        """Test parse_name with single word."""
        from apps.users.serializers import BasicLoginSerializer

        serializer = BasicLoginSerializer()
        first_name, last_name = serializer.parse_name("Madonna")

        self.assertEqual(first_name, "Madonna")
        self.assertEqual(last_name, "")

    def test_parse_name_two_words(self):
        """Test parse_name with two words."""
        from apps.users.serializers import BasicLoginSerializer

        serializer = BasicLoginSerializer()
        first_name, last_name = serializer.parse_name("John Doe")

        self.assertEqual(first_name, "John")
        self.assertEqual(last_name, "Doe")

    def test_parse_name_multiple_words(self):
        """Test parse_name with multiple words."""
        from apps.users.serializers import BasicLoginSerializer

        serializer = BasicLoginSerializer()
        first_name, last_name = serializer.parse_name("Mary Jane Watson")

        self.assertEqual(first_name, "Mary")
        self.assertEqual(last_name, "Jane Watson")

    def test_parse_name_with_extra_spaces(self):
        """Test parse_name handles extra spaces."""
        from apps.users.serializers import BasicLoginSerializer

        serializer = BasicLoginSerializer()
        first_name, last_name = serializer.parse_name("  John   Doe  ")

        self.assertEqual(first_name, "John")
        self.assertEqual(last_name, "Doe")

    def test_validate_name_strips_html(self):
        """Test name validation strips HTML tags."""
        from apps.users.serializers import BasicLoginSerializer

        serializer = BasicLoginSerializer(
            data={"name": "<b>John</b> Doe", "email": "test@example.com"}
        )
        self.assertTrue(serializer.is_valid())
        # HTML tags should be removed
        self.assertNotIn("<b>", serializer.validated_data["name"])
        self.assertNotIn("</b>", serializer.validated_data["name"])

    def test_validate_email_lowercase(self):
        """Test email is converted to lowercase."""
        from apps.users.serializers import BasicLoginSerializer

        serializer = BasicLoginSerializer(
            data={"name": "John Doe", "email": "JOHN.DOE@EXAMPLE.COM"}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "john.doe@example.com")
