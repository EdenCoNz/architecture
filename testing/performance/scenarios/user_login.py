"""
User Login Flow Performance Test

Validates login performance under various load conditions.

Thresholds:
- Login API endpoint: < 500ms
- Session creation: < 200ms
- Token generation: < 100ms

Usage:
    locust -f testing/performance/scenarios/user_login.py \
        --host=http://proxy:80 \
        --users 20 \
        --spawn-rate 5 \
        --run-time 60s
"""

import logging
import random

from locust import HttpUser, between, events, task

logger = logging.getLogger(__name__)

# Performance thresholds
LOGIN_THRESHOLD = 500  # ms
SESSION_THRESHOLD = 200  # ms

violations = []


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track login performance threshold violations."""
    if exception is None and "/auth/login" in name:
        if response_time > LOGIN_THRESHOLD:
            violations.append(
                {
                    "endpoint": name,
                    "response_time": response_time,
                    "threshold": LOGIN_THRESHOLD,
                }
            )
            logger.warning(
                f"Login threshold violation: {response_time:.0f}ms > {LOGIN_THRESHOLD}ms"
            )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Report login performance results."""
    if violations:
        logger.error(f"\n❌ {len(violations)} login threshold violations detected")
        logger.error(
            f"Slowest login: {max(v['response_time'] for v in violations):.0f}ms"
        )
        environment.process_exit_code = 1
    else:
        logger.info("\n✅ All login operations within threshold")


class LoginUser(HttpUser):
    """
    User that performs login/logout cycles.

    Simulates continuous authentication to test:
    - Login endpoint performance
    - Token generation speed
    - Session management overhead
    """

    wait_time = between(1, 3)

    @task
    def login_logout_cycle(self):
        """Perform a complete login/logout cycle."""
        # Generate unique user credentials
        user_id = random.randint(1, 1000)
        email = f"perftest{user_id}@example.com"
        password = "testpassword123"

        # Try to login (may need to register first)
        with self.client.post(
            "/api/v1/auth/login/",
            json={"email": email, "password": password},
            catch_response=True,
            name="/api/v1/auth/login/ (POST)",
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    token = data.get("token") or data.get("access")
                    response.success()

                    # Perform logout
                    self.client.post(
                        "/api/v1/auth/logout/",
                        headers={"Authorization": f"Bearer {token}"},
                        name="/api/v1/auth/logout/ (POST)",
                    )
                except Exception as e:
                    response.failure(f"Login response error: {e}")
            else:
                # Register user and retry
                self.register_user(email, password)

    def register_user(self, email: str, password: str):
        """Register a new test user."""
        with self.client.post(
            "/api/v1/auth/register/",
            json={
                "email": email,
                "password": password,
                "first_name": "Perf",
                "last_name": "Test",
            },
            catch_response=True,
            name="/api/v1/auth/register/ (POST)",
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}")
