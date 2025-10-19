"""
Custom middleware components.

This module contains custom Django middleware for cross-cutting concerns
such as request/response processing, logging, authentication, etc.

Example middleware:
    - Request logging middleware
    - Custom authentication middleware
    - Rate limiting middleware
    - Response timing middleware
    - Error handling middleware
"""

from .error_handling import ErrorHandlingMiddleware
from .request_logging import RequestLoggingMiddleware

__all__ = ["ErrorHandlingMiddleware", "RequestLoggingMiddleware"]
