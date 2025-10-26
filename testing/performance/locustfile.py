"""
Locust Load Testing Suite for Performance Threshold Validation

This file implements comprehensive load testing scenarios for:
- Login flow performance
- Page load performance
- API endpoint performance
- Form submission performance

Validates performance thresholds:
- API responses < 500ms (95th percentile)
- Page loads < 2s (95th percentile)
- Form submissions < 1s (95th percentile)

Usage:
    locust -f testing/performance/locustfile.py --host=http://proxy:80

    # Headless with specific parameters
    locust -f testing/performance/locustfile.py \
        --host=http://proxy:80 \
        --users 50 \
        --spawn-rate 5 \
        --run-time 120s \
        --html=testing/reports/html/performance-report.html
"""

import json
import logging
import random
import time
from typing import Any, Dict, List, Optional

from locust import HttpUser, TaskSet, between, events, task
from locust.exception import StopUser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Performance thresholds (in milliseconds)
THRESHOLDS = {
    "api_endpoint": 500,  # API responses must be < 500ms
    "page_load": 2000,  # Page loads must be < 2s
    "form_submission": 1000,  # Form submissions must be < 1s
    "database_query": 100,  # Database operations must be < 100ms
}

# Track threshold violations
threshold_violations: Dict[str, List[Dict[str, Any]]] = {
    "api_endpoint": [],
    "page_load": [],
    "form_submission": [],
}


# Performance threshold validation listener
@events.request.add_listener
def on_request(
    request_type: str,
    name: str,
    response_time: float,
    response_length: int,
    exception: Optional[Exception],
    **kwargs: Any,
) -> None:
    """
    Monitor every request and track performance threshold violations.

    This listener is called after each request completes and validates
    response times against defined thresholds. Violations are logged and
    tracked for reporting.
    """
    if exception is None:
        # Determine threshold based on request type
        threshold = None
        category = None

        # API endpoint thresholds
        if name.startswith("/api/"):
            threshold = THRESHOLDS["api_endpoint"]
            category = "api_endpoint"

        # Form submission thresholds (POST/PUT/PATCH to API)
        elif request_type in ["POST", "PUT", "PATCH"] and name.startswith("/api/"):
            threshold = THRESHOLDS["form_submission"]
            category = "form_submission"

        # Page load thresholds (GET requests for HTML pages)
        elif request_type == "GET" and not name.startswith("/api/"):
            threshold = THRESHOLDS["page_load"]
            category = "page_load"

        # Check threshold violation
        if threshold and category and response_time > threshold:
            violation = {
                "name": name,
                "response_time": response_time,
                "threshold": threshold,
                "exceeded_by": response_time - threshold,
                "request_type": request_type,
            }
            threshold_violations[category].append(violation)

            logger.warning(
                f"⚠️  THRESHOLD VIOLATION: {name} took {response_time:.0f}ms "
                f"(threshold: {threshold}ms, exceeded by {response_time - threshold:.0f}ms)"
            )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Report performance threshold violations at the end of the test.

    This generates a summary of all threshold violations and fails the test
    if any critical operations exceeded thresholds.
    """
    logger.info("\n" + "=" * 80)
    logger.info("PERFORMANCE THRESHOLD VALIDATION REPORT")
    logger.info("=" * 80)

    total_violations = 0

    for category, violations in threshold_violations.items():
        if violations:
            logger.error(
                f"\n{category.upper()} THRESHOLD VIOLATIONS: {len(violations)}"
            )
            logger.error(f"Threshold: {THRESHOLDS[category]}ms")

            # Group by endpoint and show worst violations
            violations_by_endpoint = {}
            for v in violations:
                endpoint = v["name"]
                if endpoint not in violations_by_endpoint:
                    violations_by_endpoint[endpoint] = []
                violations_by_endpoint[endpoint].append(v)

            for endpoint, endpoint_violations in violations_by_endpoint.items():
                worst = max(endpoint_violations, key=lambda x: x["response_time"])
                avg = sum(v["response_time"] for v in endpoint_violations) / len(
                    endpoint_violations
                )

                logger.error(
                    f"  {endpoint}: {len(endpoint_violations)} violations, "
                    f"worst: {worst['response_time']:.0f}ms, "
                    f"avg: {avg:.0f}ms"
                )

            total_violations += len(violations)

    if total_violations > 0:
        logger.error(
            f"\n❌ TEST FAILED: {total_violations} threshold violations detected"
        )
        logger.error("Review the violations above to identify slow operations")

        # Exit with error code if running in headless mode
        if environment.parsed_options and hasattr(
            environment.parsed_options, "headless"
        ):
            environment.process_exit_code = 1
    else:
        logger.info("\n✅ TEST PASSED: All operations within performance thresholds")

    logger.info("=" * 80 + "\n")


class AuthenticatedUser(TaskSet):
    """
    Base task set for authenticated user workflows.

    Handles login and provides authenticated session for all tasks.
    """

    def on_start(self):
        """Login before performing tasks."""
        self.login()

    def login(self):
        """
        Perform user login and store authentication token.

        This simulates a real user login flow, measuring the performance
        of the authentication endpoint.
        """
        # Get CSRF token first (if needed)
        with self.client.get(
            "/api/v1/config/frontend/", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get config: {response.status_code}")

        # Perform login
        login_data = {
            "email": f"testuser{random.randint(1, 100)}@example.com",
            "password": "testpassword123",
        }

        with self.client.post(
            "/api/v1/auth/login/",
            json=login_data,
            catch_response=True,
            name="/api/v1/auth/login/ (POST)",
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.token = data.get("token") or data.get("access")
                    response.success()
                except json.JSONDecodeError:
                    # If login fails, create user and retry
                    self.register_and_login(login_data)
            else:
                # User doesn't exist, create and retry
                self.register_and_login(login_data)

    def register_and_login(self, login_data: Dict[str, str]):
        """Create a test user and login."""
        # Register new user
        register_data = {
            **login_data,
            "first_name": "Test",
            "last_name": "User",
        }

        with self.client.post(
            "/api/v1/auth/register/",
            json=register_data,
            catch_response=True,
            name="/api/v1/auth/register/ (POST)",
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.token = data.get("token") or data.get("access")
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response from register")
            else:
                response.failure(f"Registration failed: {response.status_code}")

    def get_auth_headers(self) -> Dict[str, str]:
        """Return authorization headers for authenticated requests."""
        if hasattr(self, "token") and self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}


class UserWorkflowTasks(AuthenticatedUser):
    """
    Complete user workflow simulation.

    Simulates realistic user behavior with weighted task distribution:
    - Viewing pages (most common)
    - API calls (common)
    - Form submissions (less common but critical)
    """

    @task(5)
    def view_dashboard(self):
        """
        View dashboard page (most common user action).

        Weight: 5 (5x more likely than other tasks)
        Expected: < 2s page load time
        """
        with self.client.get(
            "/dashboard",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="/dashboard (GET)",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Dashboard failed: {response.status_code}")

    @task(3)
    def view_profile(self):
        """
        View user profile via API.

        Weight: 3
        Expected: < 500ms API response
        """
        with self.client.get(
            "/api/v1/user/profile/",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="/api/v1/user/profile/ (GET)",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Profile API failed: {response.status_code}")

    @task(2)
    def view_assessment_page(self):
        """
        View assessment form page.

        Weight: 2
        Expected: < 2s page load time
        """
        with self.client.get(
            "/assessment",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="/assessment (GET)",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Assessment page failed: {response.status_code}")

    @task(1)
    def submit_assessment(self):
        """
        Submit assessment form (critical operation).

        Weight: 1 (less frequent but must be fast)
        Expected: < 1s form submission time
        """
        assessment_data = {
            "age": random.randint(18, 65),
            "sport": random.choice(["running", "cycling", "swimming", "weightlifting"]),
            "level": random.choice(["beginner", "intermediate", "advanced"]),
            "training_days": random.randint(1, 7),
            "equipment": random.choice(["none", "basic", "full"]),
        }

        with self.client.post(
            "/api/v1/assessment/",
            json=assessment_data,
            headers=self.get_auth_headers(),
            catch_response=True,
            name="/api/v1/assessment/ (POST)",
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(
                    f"Assessment submission failed: {response.status_code}"
                )

    @task(2)
    def check_health(self):
        """
        Health check endpoint (monitoring simulation).

        Weight: 2
        Expected: < 500ms (should be very fast)
        """
        with self.client.get(
            "/api/v1/health/", catch_response=True, name="/api/v1/health/ (GET)"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


class LoginFlowUser(HttpUser):
    """
    User focused on login/logout flow.

    This simulates users who login, perform a few actions, and logout.
    Tests session management and authentication performance.
    """

    wait_time = between(1, 3)
    tasks = [UserWorkflowTasks]

    def on_start(self):
        """Called when user starts."""
        logger.debug("LoginFlowUser started")

    def on_stop(self):
        """Called when user stops - perform logout."""
        if hasattr(self, "token"):
            self.logout()

    def logout(self):
        """Perform logout."""
        with self.client.post(
            "/api/v1/auth/logout/",
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="/api/v1/auth/logout/ (POST)",
        ) as response:
            if response.status_code in [200, 204]:
                response.success()
            else:
                response.failure(f"Logout failed: {response.status_code}")


class QuickApiUser(HttpUser):
    """
    User focused on rapid API calls.

    Simulates API-heavy usage patterns (mobile apps, SPAs with frequent polling).
    Tests API performance under sustained load.
    """

    wait_time = between(0.5, 2)  # Faster cadence

    @task(5)
    def get_profile(self):
        """Rapid profile checks."""
        with self.client.get(
            "/api/v1/user/profile/",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="/api/v1/user/profile/ (GET - Quick)",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Quick profile failed: {response.status_code}")

    @task(3)
    def get_config(self):
        """Rapid config checks."""
        with self.client.get(
            "/api/v1/config/frontend/",
            catch_response=True,
            name="/api/v1/config/frontend/ (GET - Quick)",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Quick config failed: {response.status_code}")

    def get_auth_headers(self):
        """Simplified auth headers."""
        return {}  # Use session-based auth for quick user


# Default user class
class WebsiteUser(HttpUser):
    """
    Default user class with mixed workflow.

    Represents typical user behavior with balanced task distribution.
    """

    wait_time = between(1, 5)  # Realistic user think time
    tasks = [UserWorkflowTasks]

    # User weight distribution (for multiple user classes)
    weight = 3  # 3x more common than QuickApiUser
