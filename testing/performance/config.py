"""
Performance Test Configuration

Centralized configuration for performance testing including:
- Performance thresholds
- Load test parameters
- Test data configuration
- Reporting settings
"""

from typing import Optional

# =============================================================================
# Performance Thresholds (in milliseconds)
# =============================================================================

# API Response Time Thresholds
API_THRESHOLDS = {
    "health_check": 100,  # Health endpoint must be very fast
    "read_operation": 500,  # GET requests (95th percentile)
    "write_operation": 1000,  # POST/PUT/PATCH requests (95th percentile)
    "complex_query": 1500,  # Complex database queries (95th percentile)
}

# Page Load Time Thresholds
PAGE_THRESHOLDS = {
    "initial_load": 2000,  # First page load (95th percentile)
    "subsequent_load": 1500,  # Cached page loads (95th percentile)
    "static_asset": 500,  # JS/CSS/Images (95th percentile)
}

# Form Submission Thresholds
FORM_THRESHOLDS = {
    "login": 500,  # Login form (critical)
    "registration": 1000,  # Registration with validation
    "assessment": 1000,  # Assessment form with complex validation
    "profile_update": 800,  # Profile updates
}

# Database Operation Thresholds
DATABASE_THRESHOLDS = {
    "simple_query": 50,  # Single table queries
    "join_query": 100,  # Queries with joins
    "aggregate_query": 200,  # Aggregation queries
}

# =============================================================================
# Load Test Parameters
# =============================================================================

# Normal Load (typical usage)
NORMAL_LOAD = {
    "users": 10,
    "spawn_rate": 2,
    "duration": 300,  # 5 minutes
    "description": "Typical daily usage pattern",
}

# Peak Load (rush hours, high activity periods)
PEAK_LOAD = {
    "users": 50,
    "spawn_rate": 5,
    "duration": 600,  # 10 minutes
    "description": "Peak usage hours",
}

# Stress Test (system limits)
STRESS_TEST = {
    "users": 100,
    "spawn_rate": 10,
    "duration": 300,  # 5 minutes
    "description": "System stress testing",
}

# Spike Test (sudden traffic increase)
SPIKE_TEST = {
    "users": 100,
    "spawn_rate": 50,  # Rapid spike
    "duration": 120,  # 2 minutes
    "description": "Sudden traffic spike simulation",
}

# Endurance Test (sustained load over time)
ENDURANCE_TEST = {
    "users": 25,
    "spawn_rate": 3,
    "duration": 3600,  # 1 hour
    "description": "Sustained load endurance testing",
}

# =============================================================================
# Throughput Requirements
# =============================================================================

THROUGHPUT_REQUIREMENTS = {
    "normal": {
        "concurrent_users": 10,
        "requests_per_second": 50,
        "description": "Normal operating conditions",
    },
    "peak": {
        "concurrent_users": 50,
        "requests_per_second": 200,
        "description": "Peak hours",
    },
    "stress": {
        "concurrent_users": 100,
        "requests_per_second": 300,
        "description": "Stress testing limits",
    },
}

# =============================================================================
# Test Data Configuration
# =============================================================================

TEST_DATA = {
    "user_pool_size": 1000,  # Number of test users to create
    "assessment_variations": 50,  # Different assessment data combinations
    "concurrent_sessions": 100,  # Maximum concurrent user sessions
}

# =============================================================================
# Reporting Configuration
# =============================================================================

REPORTING = {
    "percentiles": [50, 75, 90, 95, 99],  # Percentiles to track
    "failure_threshold": 5,  # Max % of failed requests allowed
    "html_report": True,  # Generate HTML reports
    "json_report": True,  # Generate JSON reports
    "csv_export": True,  # Export CSV data
    "charts": True,  # Generate performance charts
}

# Report output paths (relative to testing/reports/)
REPORT_PATHS = {
    "html": "html/performance-report.html",
    "json": "json/performance-report.json",
    "csv": "csv/performance-data.csv",
    "charts": "charts/",
}

# =============================================================================
# Acceptance Criteria (for automated pass/fail)
# =============================================================================

ACCEPTANCE_CRITERIA = {
    # Response time requirements
    "api_response_time_95th": 500,  # 95th percentile < 500ms
    "page_load_time_95th": 2000,  # 95th percentile < 2s
    "form_submission_95th": 1000,  # 95th percentile < 1s
    # Throughput requirements
    "min_requests_per_second": 50,  # Minimum RPS for normal load
    "peak_requests_per_second": 200,  # Minimum RPS for peak load
    # Reliability requirements
    "max_failure_rate": 1.0,  # Maximum 1% failure rate
    "max_timeout_rate": 0.5,  # Maximum 0.5% timeout rate
    # Resource utilization (tracked separately)
    "max_cpu_usage": 80,  # Maximum 80% CPU usage
    "max_memory_usage": 85,  # Maximum 85% memory usage
}

# =============================================================================
# Test Scenarios
# =============================================================================

SCENARIOS = {
    "user_journey": {
        "description": "Complete user journey from login to assessment",
        "file": "locustfile.py",
        "user_class": "WebsiteUser",
        "weight": 3,
    },
    "api_only": {
        "description": "API-heavy usage (mobile apps, SPAs)",
        "file": "locustfile.py",
        "user_class": "QuickApiUser",
        "weight": 1,
    },
    "login_flow": {
        "description": "Login/logout performance testing",
        "file": "scenarios/user_login.py",
        "user_class": "LoginUser",
        "weight": 1,
    },
    "api_endpoints": {
        "description": "Comprehensive API endpoint testing",
        "file": "scenarios/api_endpoints.py",
        "user_class": "ApiUser",
        "weight": 1,
    },
    "page_loads": {
        "description": "Page loading performance",
        "file": "scenarios/page_load.py",
        "user_class": "PageLoadUser",
        "weight": 1,
    },
    "form_submissions": {
        "description": "Form submission performance",
        "file": "scenarios/form_submission.py",
        "user_class": "FormUser",
        "weight": 1,
    },
}

# =============================================================================
# Utility Functions
# =============================================================================


def get_load_params(load_type: str) -> dict:
    """
    Get load testing parameters for a specific load type.

    Args:
        load_type: One of "normal", "peak", "stress", "spike", "endurance"

    Returns:
        Dictionary with users, spawn_rate, duration, and description
    """
    load_configs = {
        "normal": NORMAL_LOAD,
        "peak": PEAK_LOAD,
        "stress": STRESS_TEST,
        "spike": SPIKE_TEST,
        "endurance": ENDURANCE_TEST,
    }
    return load_configs.get(load_type, NORMAL_LOAD)


def get_threshold(category: str, operation: Optional[str] = None) -> int:
    """
    Get performance threshold for a specific operation.

    Args:
        category: "api", "page", "form", or "database"
        operation: Specific operation within category (optional)

    Returns:
        Threshold in milliseconds
    """
    thresholds = {
        "api": API_THRESHOLDS,
        "page": PAGE_THRESHOLDS,
        "form": FORM_THRESHOLDS,
        "database": DATABASE_THRESHOLDS,
    }

    category_thresholds = thresholds.get(category, {})

    if operation and operation in category_thresholds:
        return category_thresholds[operation]

    # Return default threshold for category
    defaults = {
        "api": 500,
        "page": 2000,
        "form": 1000,
        "database": 100,
    }
    return defaults.get(category, 1000)


def meets_acceptance_criteria(stats: dict) -> tuple[bool, list]:
    """
    Check if performance test results meet acceptance criteria.

    Args:
        stats: Dictionary with performance statistics

    Returns:
        Tuple of (passed: bool, failures: list)
    """
    failures = []

    # Check response times
    if (
        stats.get("api_response_time_95th", 0)
        > ACCEPTANCE_CRITERIA["api_response_time_95th"]
    ):
        failures.append(
            f"API response time (95th): {stats['api_response_time_95th']}ms > "
            f"{ACCEPTANCE_CRITERIA['api_response_time_95th']}ms"
        )

    if stats.get("page_load_time_95th", 0) > ACCEPTANCE_CRITERIA["page_load_time_95th"]:
        failures.append(
            f"Page load time (95th): {stats['page_load_time_95th']}ms > "
            f"{ACCEPTANCE_CRITERIA['page_load_time_95th']}ms"
        )

    # Check failure rate
    if stats.get("failure_rate", 0) > ACCEPTANCE_CRITERIA["max_failure_rate"]:
        failures.append(
            f"Failure rate: {stats['failure_rate']}% > "
            f"{ACCEPTANCE_CRITERIA['max_failure_rate']}%"
        )

    # Check throughput (if available)
    if "requests_per_second" in stats:
        min_rps = ACCEPTANCE_CRITERIA["min_requests_per_second"]
        if stats["requests_per_second"] < min_rps:
            failures.append(
                f"Throughput: {stats['requests_per_second']} RPS < {min_rps} RPS"
            )

    return len(failures) == 0, failures
