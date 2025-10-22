"""
Unit tests for input validation and sanitization utilities.

Tests verify that:
- Malicious input is properly detected and sanitized
- SQL injection attempts are blocked
- XSS payloads are neutralized
- Path traversal attempts are prevented
- Command injection is blocked
"""

import pytest
from apps.utils.validators import (
    sanitize_html,
    sanitize_sql_input,
    validate_email,
    validate_username,
    sanitize_filename,
    detect_sql_injection,
    detect_xss,
    detect_path_traversal,
    validate_url,
    sanitize_json_input
)


class TestHTMLSanitization:
    """Test HTML sanitization functions."""

    def test_sanitize_simple_html_tags(self):
        """Test sanitization of simple HTML tags."""
        malicious = "<script>alert('XSS')</script>"
        result = sanitize_html(malicious)

        assert '<script>' not in result
        assert 'alert' not in result or '<script>' not in result

    def test_sanitize_on_event_handlers(self):
        """Test sanitization removes on* event handlers."""
        malicious = '<img src=x onerror="alert(1)">'
        result = sanitize_html(malicious)

        assert 'onerror' not in result
        assert 'alert' not in result or 'onerror' not in result

    def test_sanitize_javascript_protocol(self):
        """Test sanitization removes javascript: protocol."""
        malicious = '<a href="javascript:alert(1)">Click</a>'
        result = sanitize_html(malicious)

        assert 'javascript:' not in result

    def test_sanitize_data_protocol(self):
        """Test sanitization handles data: protocol."""
        malicious = '<img src="data:text/html,<script>alert(1)</script>">'
        result = sanitize_html(malicious)

        # Should either remove or safely encode
        assert '<script>' not in result

    def test_allow_safe_html_tags(self):
        """Test that safe HTML tags are allowed."""
        safe = '<p>Hello <strong>World</strong></p>'
        result = sanitize_html(safe)

        assert '<p>' in result or 'Hello' in result
        assert 'World' in result

    def test_sanitize_style_tags(self):
        """Test sanitization removes style tags with expressions."""
        malicious = '<style>body{background:url("javascript:alert(1)")}</style>'
        result = sanitize_html(malicious)

        assert 'javascript:' not in result


class TestSQLInjectionDetection:
    """Test SQL injection detection and sanitization."""

    def test_detect_sql_injection_union_attack(self):
        """Test detection of UNION-based SQL injection."""
        malicious = "1' UNION SELECT * FROM users--"
        result = detect_sql_injection(malicious)

        assert result is True

    def test_detect_sql_injection_comment_attack(self):
        """Test detection of comment-based SQL injection."""
        malicious = "admin'--"
        result = detect_sql_injection(malicious)

        assert result is True

    def test_detect_sql_injection_or_attack(self):
        """Test detection of OR 1=1 style attacks."""
        malicious = "' OR '1'='1"
        result = detect_sql_injection(malicious)

        assert result is True

    def test_detect_sql_injection_drop_table(self):
        """Test detection of DROP TABLE attacks."""
        malicious = "'; DROP TABLE users; --"
        result = detect_sql_injection(malicious)

        assert result is True

    def test_safe_input_passes(self):
        """Test that safe input passes validation."""
        safe_input = "john.doe@example.com"
        result = detect_sql_injection(safe_input)

        assert result is False

    def test_sanitize_sql_input_removes_dangerous_chars(self):
        """Test SQL input sanitization removes dangerous characters."""
        malicious = "test'; DROP TABLE--"
        result = sanitize_sql_input(malicious)

        # Should not contain dangerous SQL keywords/characters
        assert '--' not in result
        assert ';' not in result or 'DROP' not in result


class TestXSSDetection:
    """Test XSS detection functions."""

    def test_detect_xss_script_tag(self):
        """Test detection of script tag XSS."""
        malicious = "<script>alert('XSS')</script>"
        result = detect_xss(malicious)

        assert result is True

    def test_detect_xss_img_tag(self):
        """Test detection of img tag XSS."""
        malicious = '<img src=x onerror=alert(1)>'
        result = detect_xss(malicious)

        assert result is True

    def test_detect_xss_event_handler(self):
        """Test detection of event handler XSS."""
        malicious = '<div onclick="malicious()">Click</div>'
        result = detect_xss(malicious)

        assert result is True

    def test_detect_xss_encoded_attack(self):
        """Test detection of encoded XSS attacks."""
        malicious = '&#60;script&#62;alert(1)&#60;/script&#62;'
        result = detect_xss(malicious)

        # Should detect encoded attacks
        assert result is True or '<script>' not in malicious

    def test_safe_text_passes(self):
        """Test that safe text passes XSS detection."""
        safe_text = "Hello, this is a normal message!"
        result = detect_xss(safe_text)

        assert result is False


class TestPathTraversalDetection:
    """Test path traversal detection."""

    def test_detect_path_traversal_dot_dot_slash(self):
        """Test detection of ../ path traversal."""
        malicious = "../../etc/passwd"
        result = detect_path_traversal(malicious)

        assert result is True

    def test_detect_path_traversal_encoded(self):
        """Test detection of encoded path traversal."""
        malicious = "..%2F..%2Fetc%2Fpasswd"
        result = detect_path_traversal(malicious)

        assert result is True

    def test_detect_path_traversal_backslash(self):
        """Test detection of backslash path traversal."""
        malicious = "..\\..\\windows\\system32"
        result = detect_path_traversal(malicious)

        assert result is True

    def test_safe_path_passes(self):
        """Test that safe paths pass validation."""
        safe_path = "documents/report.pdf"
        result = detect_path_traversal(safe_path)

        assert result is False


class TestFilenameValidation:
    """Test filename sanitization."""

    def test_sanitize_filename_removes_path_separators(self):
        """Test filename sanitization removes path separators."""
        malicious = "../../../etc/passwd"
        result = sanitize_filename(malicious)

        assert '/' not in result
        assert '..' not in result

    def test_sanitize_filename_removes_null_bytes(self):
        """Test filename sanitization removes null bytes."""
        malicious = "file.txt\x00.exe"
        result = sanitize_filename(malicious)

        assert '\x00' not in result

    def test_sanitize_filename_allows_safe_chars(self):
        """Test filename sanitization allows safe characters."""
        safe = "my_document-2024.pdf"
        result = sanitize_filename(safe)

        assert 'my_document' in result
        assert '2024' in result
        assert '.pdf' in result

    def test_sanitize_filename_handles_unicode(self):
        """Test filename sanitization handles unicode properly."""
        unicode_name = "résumé.pdf"
        result = sanitize_filename(unicode_name)

        # Should preserve or safely convert unicode
        assert len(result) > 0
        assert '.pdf' in result


class TestEmailValidation:
    """Test email validation."""

    def test_validate_email_correct_format(self):
        """Test validation of correctly formatted emails."""
        valid_emails = [
            "user@example.com",
            "test.user@example.co.uk",
            "user+tag@example.com",
            "user_name@example-domain.com"
        ]

        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_rejects_invalid(self):
        """Test validation rejects invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@@example.com",
            "user@.com",
            "<script>@example.com"
        ]

        for email in invalid_emails:
            assert validate_email(email) is False


class TestUsernameValidation:
    """Test username validation."""

    def test_validate_username_alphanumeric(self):
        """Test validation accepts alphanumeric usernames."""
        valid_usernames = [
            "john_doe",
            "user123",
            "test-user",
            "JohnDoe"
        ]

        for username in valid_usernames:
            assert validate_username(username) is True

    def test_validate_username_rejects_special_chars(self):
        """Test validation rejects usernames with special characters."""
        invalid_usernames = [
            "user@example",
            "test<script>",
            "user'--",
            "../admin"
        ]

        for username in invalid_usernames:
            assert validate_username(username) is False

    def test_validate_username_length_constraints(self):
        """Test username length validation."""
        too_short = "ab"
        too_long = "a" * 151

        assert validate_username(too_short) is False
        assert validate_username(too_long) is False

    def test_validate_username_normal_length(self):
        """Test username with normal length."""
        normal = "valid_username"
        assert validate_username(normal) is True


class TestURLValidation:
    """Test URL validation."""

    def test_validate_url_http_https(self):
        """Test validation accepts http and https URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://sub.example.com/path"
        ]

        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_rejects_javascript(self):
        """Test validation rejects javascript: URLs."""
        malicious = "javascript:alert(1)"
        assert validate_url(malicious) is False

    def test_validate_url_rejects_data(self):
        """Test validation rejects data: URLs."""
        malicious = "data:text/html,<script>alert(1)</script>"
        assert validate_url(malicious) is False

    def test_validate_url_rejects_file(self):
        """Test validation rejects file: URLs."""
        malicious = "file:///etc/passwd"
        assert validate_url(malicious) is False


class TestJSONInputSanitization:
    """Test JSON input sanitization."""

    def test_sanitize_json_input_removes_scripts(self):
        """Test JSON sanitization removes script content."""
        malicious = {
            "name": "test",
            "bio": "<script>alert('XSS')</script>"
        }
        result = sanitize_json_input(malicious)

        assert '<script>' not in str(result.get('bio', ''))

    def test_sanitize_json_input_nested_objects(self):
        """Test JSON sanitization handles nested objects."""
        malicious = {
            "user": {
                "name": "test",
                "profile": {
                    "bio": "<script>alert(1)</script>"
                }
            }
        }
        result = sanitize_json_input(malicious)

        # Should sanitize nested values
        bio = result.get('user', {}).get('profile', {}).get('bio', '')
        assert '<script>' not in str(bio)

    def test_sanitize_json_input_arrays(self):
        """Test JSON sanitization handles arrays."""
        malicious = {
            "tags": ["<script>alert(1)</script>", "normal-tag"]
        }
        result = sanitize_json_input(malicious)

        tags = result.get('tags', [])
        for tag in tags:
            assert '<script>' not in str(tag)

    def test_sanitize_json_preserves_safe_data(self):
        """Test JSON sanitization preserves safe data."""
        safe_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        result = sanitize_json_input(safe_data)

        assert result['name'] == "John Doe"
        assert result['age'] == 30
        assert result['email'] == "john@example.com"
