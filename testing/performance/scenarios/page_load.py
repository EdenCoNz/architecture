"""
Page Load Performance Test

Validates frontend page load performance.

Thresholds:
- Initial page load: < 2000ms
- Authenticated pages: < 2000ms
- Static assets: < 500ms

Usage:
    locust -f testing/performance/scenarios/page_load.py \
        --host=http://proxy:80 \
        --users 25 \
        --spawn-rate 5 \
        --run-time 90s
"""

import logging

from locust import HttpUser, between, events, task

logger = logging.getLogger(__name__)

# Page load thresholds
PAGE_THRESHOLD = 2000  # ms for HTML pages
ASSET_THRESHOLD = 500  # ms for static assets

violations = []


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track page load threshold violations."""
    if exception is None and request_type == "GET":
        # Determine threshold based on request type
        if any(ext in name for ext in [".js", ".css", ".svg", ".png", ".jpg", ".ico"]):
            threshold = ASSET_THRESHOLD
            category = "static asset"
        elif not name.startswith("/api/"):
            threshold = PAGE_THRESHOLD
            category = "page"
        else:
            return  # Skip API calls

        # Check violation
        if response_time > threshold:
            violations.append(
                {
                    "name": name,
                    "response_time": response_time,
                    "threshold": threshold,
                    "category": category,
                }
            )
            logger.warning(
                f"Page load violation: {category} {name} "
                f"{response_time:.0f}ms > {threshold}ms"
            )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Report page load performance results."""
    if violations:
        logger.error(f"\n❌ {len(violations)} page load violations detected")

        # Summarize by category
        by_category = {}
        for v in violations:
            cat = v["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(v)

        for category, cat_violations in by_category.items():
            worst = max(v["response_time"] for v in cat_violations)
            avg = sum(v["response_time"] for v in cat_violations) / len(cat_violations)

            logger.error(
                f"  {category}: {len(cat_violations)} violations, "
                f"worst: {worst:.0f}ms, avg: {avg:.0f}ms"
            )

        environment.process_exit_code = 1
    else:
        logger.info("\n✅ All pages load within performance thresholds")


class PageLoadUser(HttpUser):
    """
    User that focuses on page loading performance.

    Simulates browsing behavior with focus on measuring:
    - Initial page load times
    - Navigation between pages
    - Static asset loading
    """

    wait_time = between(2, 5)  # Realistic page viewing time

    @task(3)
    def load_home_page(self):
        """
        Load home/landing page.

        Weight: 3
        Threshold: < 2000ms
        """
        self.client.get("/", name="/ (Home Page)")

    @task(2)
    def load_login_page(self):
        """
        Load login page.

        Weight: 2
        Threshold: < 2000ms
        """
        self.client.get("/login", name="/login (Login Page)")

    @task(2)
    def load_dashboard(self):
        """
        Load dashboard (authenticated page).

        Weight: 2
        Threshold: < 2000ms
        """
        self.client.get("/dashboard", name="/dashboard (Dashboard Page)")

    @task(1)
    def load_assessment_page(self):
        """
        Load assessment form page.

        Weight: 1
        Threshold: < 2000ms
        """
        self.client.get("/assessment", name="/assessment (Assessment Page)")

    @task(1)
    def load_profile_page(self):
        """
        Load user profile page.

        Weight: 1
        Threshold: < 2000ms
        """
        self.client.get("/profile", name="/profile (Profile Page)")
