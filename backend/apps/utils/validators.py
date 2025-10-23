"""
Input validation and sanitization utilities.

Provides functions to:
- Sanitize HTML input to prevent XSS
- Detect and prevent SQL injection
- Validate email addresses and usernames
- Sanitize filenames and URLs
- Detect path traversal attempts
- Sanitize JSON input
"""

import html
import re
from typing import Any, Dict, List, Union
from urllib.parse import urlparse

# Patterns for security threat detection
SQL_INJECTION_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bor\b\s*['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
    r"(--|\#|\/\*|\*\/)",
    r"(\bdrop\b.*\btable\b)",
    r"(\bexec\b|\bexecute\b)",
    r"(\binsert\b.*\binto\b)",
    r"(\bupdate\b.*\bset\b)",
    r"(\bdelete\b.*\bfrom\b)",
    r"(;.*(\bdrop\b|\bdelete\b|\binsert\b|\bupdate\b))",
]

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe",
    r"<embed",
    r"<object",
    r"eval\s*\(",
    r"expression\s*\(",
]

PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.",
    r"%2e%2e",
    r"\.\.\\",
    r"%252e",
]


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML input to prevent XSS attacks.

    Args:
        text: Input text that may contain HTML

    Returns:
        Sanitized text with HTML entities escaped
    """
    if not isinstance(text, str):
        return text

    # Escape HTML entities
    sanitized = html.escape(text)

    # Remove dangerous patterns
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r'on\w+\s*=\s*["\']?[^"\']*["\']?',
        r"<iframe[^>]*>.*?</iframe>",
        r"<embed[^>]*>",
        r"<object[^>]*>.*?</object>",
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

    return sanitized


def detect_sql_injection(text: str) -> bool:
    """
    Detect potential SQL injection attempts.

    Args:
        text: Input text to check

    Returns:
        True if SQL injection pattern detected, False otherwise
    """
    if not isinstance(text, str):
        return False

    text_lower = text.lower()

    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True

    return False


def sanitize_sql_input(text: str) -> str:
    """
    Sanitize input to prevent SQL injection.

    Note: This should be used in addition to parameterized queries,
    not as a replacement.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return text

    # Remove SQL comments
    sanitized = re.sub(r"(--|#|\/\*|\*\/)", "", text)

    # Remove dangerous SQL keywords when followed by suspicious patterns
    dangerous = [
        (r";.*\b(drop|delete|insert|update|exec|execute)\b", ""),
        (r"\bunion\b.*\bselect\b", ""),
    ]

    for pattern, replacement in dangerous:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def detect_xss(text: str) -> bool:
    """
    Detect potential XSS attacks.

    Args:
        text: Input text to check

    Returns:
        True if XSS pattern detected, False otherwise
    """
    if not isinstance(text, str):
        return False

    for pattern in XSS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return True

    # Check for HTML entity encoded scripts
    decoded = html.unescape(text)
    if decoded != text:
        # If text was decoded, check again
        for pattern in XSS_PATTERNS:
            if re.search(pattern, decoded, re.IGNORECASE | re.DOTALL):
                return True

    return False


def detect_path_traversal(path: str) -> bool:
    """
    Detect path traversal attempts.

    Args:
        path: File path to check

    Returns:
        True if path traversal detected, False otherwise
    """
    if not isinstance(path, str):
        return False

    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, path, re.IGNORECASE):
            return True

    return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    if not isinstance(filename, str):
        return ""

    # Remove path separators
    sanitized = filename.replace("/", "").replace("\\", "")

    # Remove parent directory references
    sanitized = sanitized.replace("..", "")

    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Keep only alphanumeric, dash, underscore, and dot
    sanitized = re.sub(r"[^\w\-.]", "_", sanitized)

    # Limit length
    if len(sanitized) > 255:
        # Preserve extension
        parts = sanitized.rsplit(".", 1)
        if len(parts) == 2:
            name, ext = parts
            sanitized = name[:250] + "." + ext
        else:
            sanitized = sanitized[:255]

    return sanitized


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    if not isinstance(email, str):
        return False

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return False

    # Additional checks for XSS attempts
    if detect_xss(email):
        return False

    # Check length
    if len(email) > 254:  # RFC 5321
        return False

    return True


def validate_username(username: str) -> bool:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        True if valid username, False otherwise
    """
    if not isinstance(username, str):
        return False

    # Length check
    if len(username) < 3 or len(username) > 150:
        return False

    # Allow alphanumeric, underscore, and hyphen
    pattern = r"^[a-zA-Z0-9_-]+$"

    if not re.match(pattern, username):
        return False

    # Check for XSS or SQL injection attempts
    if detect_xss(username) or detect_sql_injection(username):
        return False

    return True


def validate_url(url: str) -> bool:
    """
    Validate URL and check for dangerous protocols.

    Args:
        url: URL to validate

    Returns:
        True if safe URL, False otherwise
    """
    if not isinstance(url, str):
        return False

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Check for dangerous protocols
    dangerous_schemes = ["javascript", "data", "file", "vbscript"]

    if parsed.scheme.lower() in dangerous_schemes:
        return False

    # Only allow http and https
    if parsed.scheme.lower() not in ["http", "https", ""]:
        return False

    return True


def sanitize_json_input(data: Union[Dict, List, str, Any]) -> Union[Dict, List, str, Any]:
    """
    Recursively sanitize JSON input data.

    Args:
        data: JSON data to sanitize (dict, list, or primitive)

    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        return {key: sanitize_json_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_json_input(item) for item in data]
    elif isinstance(data, str):
        # Sanitize string values
        return sanitize_html(data)
    else:
        # Return primitives as-is (int, float, bool, None)
        return data
