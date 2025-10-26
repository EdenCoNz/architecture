"""
Form Submission Performance Test

Validates form submission performance for all critical forms.

Thresholds:
- Login form: < 500ms
- Assessment form: < 1000ms
- Profile update form: < 1000ms
- Registration form: < 1000ms

Usage:
    locust -f testing/performance/scenarios/form_submission.py \
        --host=http://proxy:80 \
        --users 15 \
        --spawn-rate 3 \
        --run-time 120s
"""

import logging
import random

from locust import HttpUser, between, events, task

logger = logging.getLogger(__name__)

# Form-specific thresholds
FORM_THRESHOLDS = {
    "login": 500,  # Login must be fast
    "assessment": 1000,  # Assessment with validation
    "profile": 1000,  # Profile updates
    "registration": 1000,  # Registration with validation
}

violations = {}


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track form submission threshold violations."""
    if exception is None and request_type in ["POST", "PUT", "PATCH"]:
        # Determine form type and threshold
        threshold = None
        form_type = None

        if "/auth/login" in name:
            threshold = FORM_THRESHOLDS["login"]
            form_type = "login"
        elif "/auth/register" in name:
            threshold = FORM_THRESHOLDS["registration"]
            form_type = "registration"
        elif "/assessment" in name:
            threshold = FORM_THRESHOLDS["assessment"]
            form_type = "assessment"
        elif "/profile" in name:
            threshold = FORM_THRESHOLDS["profile"]
            form_type = "profile"

        # Check violation
        if threshold and response_time > threshold:
            if form_type not in violations:
                violations[form_type] = []
            violations[form_type].append(
                {
                    "name": name,
                    "response_time": response_time,
                    "threshold": threshold,
                    "method": request_type,
                }
            )
            logger.warning(
                f"Form submission violation: {form_type} form "
                f"{response_time:.0f}ms > {threshold}ms"
            )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Report form submission performance results."""
    if violations:
        logger.error(f"\n❌ Form Submission Performance Issues Detected")
        logger.error(f"Forms with violations: {len(violations)}")

        for form_type, form_violations in violations.items():
            worst = max(v["response_time"] for v in form_violations)
            avg = sum(v["response_time"] for v in form_violations) / len(
                form_violations
            )

            logger.error(
                f"  {form_type} form: {len(form_violations)} violations, "
                f"worst: {worst:.0f}ms, avg: {avg:.0f}ms, "
                f"threshold: {FORM_THRESHOLDS[form_type]}ms"
            )

        environment.process_exit_code = 1
    else:
        logger.info("\n✅ All form submissions within performance thresholds")


class FormUser(HttpUser):
    """
    User that focuses on form submissions.

    Tests performance of all critical form operations:
    - Login forms
    - Registration forms
    - Assessment forms
    - Profile update forms
    """

    wait_time = between(1, 3)

    token = None
    user_id = random.randint(1, 10000)

    @task(5)
    def submit_login_form(self):
        """
        Submit login form (most critical).

        Weight: 5
        Threshold: < 500ms
        """
        email = f"formtest{self.user_id}@example.com"
        password = "testpassword123"

        with self.client.post(
            "/api/v1/auth/login/",
            json={"email": email, "password": password},
            catch_response=True,
            name="/api/v1/auth/login/ (Form Submit)",
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token") or data.get("access")
                response.success()
            else:
                # Need to register first
                response.failure("User not found - will register")
                self.submit_registration_form()

    @task(1)
    def submit_registration_form(self):
        """
        Submit registration form.

        Weight: 1
        Threshold: < 1000ms
        """
        email = f"formtest{self.user_id}@example.com"
        password = "testpassword123"

        with self.client.post(
            "/api/v1/auth/register/",
            json={
                "email": email,
                "password": password,
                "first_name": "Form",
                "last_name": f"Test{self.user_id}",
            },
            catch_response=True,
            name="/api/v1/auth/register/ (Form Submit)",
        ) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                self.token = data.get("token") or data.get("access")
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}")

    @task(3)
    def submit_assessment_form(self):
        """
        Submit assessment form (critical user flow).

        Weight: 3
        Threshold: < 1000ms
        """
        if not self.token:
            return

        assessment_data = {
            "age": random.randint(18, 65),
            "sport": random.choice(
                [
                    "running",
                    "cycling",
                    "swimming",
                    "weightlifting",
                    "basketball",
                    "soccer",
                    "tennis",
                    "yoga",
                ]
            ),
            "level": random.choice(["beginner", "intermediate", "advanced", "expert"]),
            "training_days": random.randint(1, 7),
            "equipment": random.choice(["none", "basic", "intermediate", "full"]),
            "goals": random.choice(
                [
                    "weight_loss",
                    "muscle_gain",
                    "endurance",
                    "strength",
                    "flexibility",
                    "general_fitness",
                ]
            ),
        }

        self.client.post(
            "/api/v1/assessment/",
            json=assessment_data,
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/v1/assessment/ (Form Submit)",
        )

    @task(2)
    def submit_profile_update_form(self):
        """
        Submit profile update form.

        Weight: 2
        Threshold: < 1000ms
        """
        if not self.token:
            return

        profile_data = {
            "first_name": f"Updated{random.randint(1, 100)}",
            "last_name": f"User{random.randint(1, 100)}",
            "bio": f"Test bio updated at {random.randint(1000, 9999)}",
        }

        self.client.patch(
            "/api/v1/user/profile/",
            json=profile_data,
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/v1/user/profile/ (Form Submit)",
        )
