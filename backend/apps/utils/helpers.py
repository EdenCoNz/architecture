"""
Helper functions and utilities.
"""

import hashlib
import uuid
from typing import Any, Dict, Optional

from django.http import HttpRequest


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


def generate_hash(data: str) -> str:
    """Generate a SHA256 hash of the given data."""
    return hashlib.sha256(data.encode()).hexdigest()


def normalize_email(email: str) -> str:
    """Normalize email address to lowercase."""
    return email.strip().lower()


def get_client_ip(request: HttpRequest) -> str:
    """
    Extract the client's IP address from the request.
    Handles proxies and load balancers.
    """
    x_forwarded_for: Optional[str] = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip: str = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip
