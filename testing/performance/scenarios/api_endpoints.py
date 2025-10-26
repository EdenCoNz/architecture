"""
API Endpoint Performance Test

Validates all critical API endpoints meet performance thresholds.

Thresholds:
- Read operations (GET): < 500ms
- Write operations (POST/PUT): < 1000ms
- Health checks: < 100ms

Usage:
    locust -f testing/performance/scenarios/api_endpoints.py \
        --host=http://proxy:80 \
        --users 30 \
        --spawn-rate 10 \
        --run-time 120s
"""

import logging
import random

from locust import HttpUser, between, events, task

logger = logging.getLogger(__name__)

# API-specific thresholds
THRESHOLDS = {
    "health": 100,  # Health checks must be very fast
    "read": 500,  # GET requests
    "write": 1000,  # POST/PUT/PATCH requests
}

violations = {}


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track API performance threshold violations."""
    if exception is None and name.startswith("/api/"):
        # Determine threshold
        if "/health" in name:
            threshold = THRESHOLDS["health"]
        elif request_type == "GET":
            threshold = THRESHOLDS["read"]
        else:
            threshold = THRESHOLDS["write"]

        # Check violation
        if response_time > threshold:
            if name not in violations:
                violations[name] = []
            violations[name].append(
                {
                    "response_time": response_time,
                    "threshold": threshold,
                    "method": request_type,
                }
            )
            logger.warning(
                f"API threshold violation: {request_type} {name} "
                f"{response_time:.0f}ms > {threshold}ms"
            )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Report API performance results."""
    if violations:
        logger.error(f"\n❌ API Performance Issues Detected")
        logger.error(f"Endpoints with violations: {len(violations)}")

        for endpoint, endpoint_violations in violations.items():
            worst = max(v["response_time"] for v in endpoint_violations)
            avg = sum(v["response_time"] for v in endpoint_violations) / len(
                endpoint_violations
            )

            logger.error(
                f"  {endpoint}: {len(endpoint_violations)} violations, "
                f"worst: {worst:.0f}ms, avg: {avg:.0f}ms"
            )

        environment.process_exit_code = 1
    else:
        logger.info("\n✅ All API endpoints within performance thresholds")


class ApiUser(HttpUser):
    """
    User that exercises all critical API endpoints.

    Tests comprehensive API performance including:
    - Health checks
    - Configuration endpoints
    - User profile operations
    - Assessment operations
    """

    wait_time = between(0.5, 2)

    token = None

    def on_start(self):
        """Login to get authentication token."""
        self.login()

    def login(self):
        """Authenticate and store token."""
        email = f"apitest{random.randint(1, 100)}@example.com"
        password = "testpassword123"

        # Try login
        response = self.client.post(
            "/api/v1/auth/login/",
            json={"email": email, "password": password},
            name="/api/v1/auth/login/",
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("access")
        else:
            # Register and login
            self.client.post(
                "/api/v1/auth/register/",
                json={
                    "email": email,
                    "password": password,
                    "first_name": "API",
                    "last_name": "Test",
                },
                name="/api/v1/auth/register/",
            )
            response = self.client.post(
                "/api/v1/auth/login/",
                json={"email": email, "password": password},
                name="/api/v1/auth/login/",
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token") or data.get("access")

    def get_headers(self):
        """Get authorization headers."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(5)
    def health_check(self):
        """
        Health check endpoint (critical for monitoring).

        Weight: 5 (very frequent)
        Threshold: < 100ms
        """
        self.client.get("/api/v1/health/", name="/api/v1/health/ (GET)")

    @task(3)
    def get_frontend_config(self):
        """
        Frontend configuration endpoint (frequent).

        Weight: 3
        Threshold: < 500ms
        """
        self.client.get(
            "/api/v1/config/frontend/", name="/api/v1/config/frontend/ (GET)"
        )

    @task(4)
    def get_user_profile(self):
        """
        User profile retrieval (common operation).

        Weight: 4
        Threshold: < 500ms
        """
        self.client.get(
            "/api/v1/user/profile/",
            headers=self.get_headers(),
            name="/api/v1/user/profile/ (GET)",
        )

    @task(2)
    def update_user_profile(self):
        """
        User profile update (less frequent write operation).

        Weight: 2
        Threshold: < 1000ms
        """
        self.client.patch(
            "/api/v1/user/profile/",
            json={
                "first_name": f"Test{random.randint(1, 100)}",
            },
            headers=self.get_headers(),
            name="/api/v1/user/profile/ (PATCH)",
        )

    @task(1)
    def create_assessment(self):
        """
        Assessment creation (critical write operation).

        Weight: 1
        Threshold: < 1000ms
        """
        self.client.post(
            "/api/v1/assessment/",
            json={
                "age": random.randint(18, 65),
                "sport": random.choice(["running", "cycling", "swimming"]),
                "level": random.choice(["beginner", "intermediate", "advanced"]),
                "training_days": random.randint(1, 7),
            },
            headers=self.get_headers(),
            name="/api/v1/assessment/ (POST)",
        )

    @task(2)
    def get_assessment_list(self):
        """
        Assessment list retrieval.

        Weight: 2
        Threshold: < 500ms
        """
        self.client.get(
            "/api/v1/assessment/",
            headers=self.get_headers(),
            name="/api/v1/assessment/ (GET)",
        )
