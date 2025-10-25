# Performance Tests

## Overview

Performance tests validate response times, throughput, and system behavior under load. These tests ensure the application meets performance requirements under expected concurrent usage.

## Framework

- **Locust** - Modern load testing framework with Python
- **pytest-benchmark** - Performance benchmarking for Python code

## Test Organization

```
performance/
├── locustfile.py           # Main load test scenarios
├── scenarios/
│   ├── user_login.py       # Login flow load test
│   ├── api_endpoints.py    # API endpoint load test
│   ├── form_submission.py  # Form submission load test
│   └── page_load.py        # Page load performance test
├── benchmarks/
│   ├── test_db_queries.py  # Database query benchmarks
│   └── test_api_perf.py    # API performance benchmarks
├── reports/
│   └── (generated reports)
└── README.md
```

## Running Performance Tests

**Load tests (Locust):**
```bash
./testing/run-tests.sh --suite performance
```

**Custom load test parameters:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    locust -f performance/locustfile.py \
    --users 50 \
    --spawn-rate 5 \
    --run-time 120s \
    --html=testing/reports/html/performance-report.html
```

**Interactive load testing (web UI):**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm -p 8089:8089 test-runner \
    locust -f performance/locustfile.py --host=http://proxy:80
# Open http://localhost:8089 in browser
```

**Benchmark tests:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    pytest performance/benchmarks/ --benchmark-only
```

## Writing Load Tests (Locust)

### Basic Load Test

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts."""
        # Login before performing tasks
        response = self.client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["token"]

    @task(3)  # Weight: 3x more likely than other tasks
    def view_dashboard(self):
        """Simulate user viewing dashboard."""
        self.client.get("/dashboard", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task(1)
    def submit_assessment(self):
        """Simulate assessment submission."""
        self.client.post("/api/v1/assessment/", {
            "age": 25,
            "sport": "running",
            "level": "intermediate",
            "training_days": 4
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task(2)
    def view_profile(self):
        """Simulate user viewing profile."""
        self.client.get("/api/v1/user/profile/", headers={
            "Authorization": f"Bearer {self.token}"
        })
```

### Load Test with Custom Scenarios

```python
from locust import HttpUser, task, between, SequentialTaskSet

class UserJourneyTasks(SequentialTaskSet):
    """Sequential user journey: login -> dashboard -> form -> submit."""

    @task
    def login(self):
        self.client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "password123"
        })

    @task
    def view_dashboard(self):
        self.client.get("/dashboard")

    @task
    def fill_assessment_form(self):
        self.client.get("/assessment")

    @task
    def submit_assessment(self):
        self.client.post("/api/v1/assessment/", {
            "age": 25,
            "sport": "running",
            "level": "intermediate",
            "training_days": 4
        })

class UserJourneyUser(HttpUser):
    tasks = [UserJourneyTasks]
    wait_time = between(1, 2)
```

### Performance Assertions

```python
from locust import events

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Assert performance requirements."""
    if exception is None:
        # API requests should be < 500ms
        if name.startswith("/api/") and response_time > 500:
            print(f"WARNING: {name} took {response_time}ms (threshold: 500ms)")

        # Page loads should be < 2000ms
        if not name.startswith("/api/") and response_time > 2000:
            print(f"WARNING: {name} took {response_time}ms (threshold: 2000ms)")
```

## Writing Benchmarks (pytest-benchmark)

### Database Query Benchmark

```python
import pytest
from apps.users.models import User

@pytest.mark.benchmark
def test_user_query_performance(benchmark, django_db_reset_sequences):
    """Benchmark user query performance."""

    # Setup: Create 1000 users
    users = [
        User(email=f"user{i}@example.com", password="password")
        for i in range(1000)
    ]
    User.objects.bulk_create(users)

    # Benchmark the query
    result = benchmark(User.objects.filter, email__startswith="user")

    assert result.count() == 1000
```

### API Endpoint Benchmark

```python
from rest_framework.test import APIClient

@pytest.mark.benchmark
def test_api_endpoint_performance(benchmark, api_client, test_user):
    """Benchmark API endpoint performance."""

    api_client.force_authenticate(user=test_user)

    def call_endpoint():
        response = api_client.get('/api/v1/user/profile/')
        return response

    result = benchmark(call_endpoint)

    assert result.status_code == 200
```

## Performance Requirements

### Response Time Thresholds

| Operation | Target | Maximum | Notes |
|-----------|--------|---------|-------|
| API Requests | < 200ms | < 500ms | 95th percentile |
| Page Load | < 1s | < 2s | First Contentful Paint |
| Database Queries | < 50ms | < 100ms | 95th percentile |
| Form Submission | < 300ms | < 1s | Including validation |

### Throughput Requirements

| Scenario | Concurrent Users | RPS (requests/sec) | Notes |
|----------|------------------|-------------------|-------|
| Normal Load | 10 | 50 | Typical usage |
| Peak Load | 50 | 200 | Rush hours |
| Stress Test | 100+ | 300+ | System limits |

## Load Test Scenarios

### Scenario 1: Normal Load
```bash
locust -f performance/locustfile.py \
    --users 10 \
    --spawn-rate 2 \
    --run-time 300s
```

### Scenario 2: Peak Load
```bash
locust -f performance/locustfile.py \
    --users 50 \
    --spawn-rate 5 \
    --run-time 600s
```

### Scenario 3: Stress Test
```bash
locust -f performance/locustfile.py \
    --users 100 \
    --spawn-rate 10 \
    --run-time 300s
```

### Scenario 4: Spike Test
```bash
# Start with low load, spike to high
locust -f performance/locustfile.py \
    --users 100 \
    --spawn-rate 50 \
    --run-time 120s
```

## Analyzing Results

### Locust Reports

Reports are generated in `testing/reports/html/performance-report.html`

**Key Metrics:**
- **RPS (Requests Per Second):** Total throughput
- **Response Time:** 50th, 95th, 99th percentiles
- **Failure Rate:** Percentage of failed requests
- **Concurrent Users:** Active users at time of measurement

### Interpreting Results

**Successful Test:**
- Response times within thresholds
- Failure rate < 1%
- System resources (CPU, memory) stable
- No error spikes

**Performance Issues:**
- Response times increasing with load
- High failure rate (> 5%)
- Memory leaks (increasing memory usage)
- CPU maxed out (> 80%)

## Best Practices

### Test Design

1. **Realistic scenarios:**
   - Model actual user behavior
   - Include think time (wait_time)
   - Mix of read/write operations

2. **Gradual ramp-up:**
   ```python
   --spawn-rate 5  # Add 5 users per second
   ```

3. **Sufficient duration:**
   ```python
   --run-time 300s  # Run for 5 minutes minimum
   ```

4. **Performance assertions:**
   - Assert response time thresholds
   - Monitor error rates
   - Check resource utilization

### Data Management

1. **Use test data:**
   - Create realistic test datasets
   - Clean up after tests
   - Don't use production data

2. **Database state:**
   - Reset database between runs
   - Use consistent baseline data
   - Monitor database performance

### Monitoring

1. **Application metrics:**
   - Response times
   - Error rates
   - Request throughput

2. **System metrics:**
   - CPU usage
   - Memory usage
   - Database connections
   - Network I/O

## Debugging Performance Issues

### Identify Bottlenecks

1. **Check slowest endpoints:**
   - Review Locust statistics
   - Sort by response time
   - Focus on 95th/99th percentile

2. **Profile database queries:**
   ```python
   from django.db import connection
   print(connection.queries)  # See all executed queries
   ```

3. **Monitor system resources:**
   ```bash
   docker stats  # Real-time resource usage
   ```

### Common Performance Issues

**Slow database queries:**
- Add database indexes
- Optimize query structure
- Use select_related/prefetch_related

**Memory leaks:**
- Check for unclosed connections
- Review object lifecycle
- Monitor memory growth over time

**High CPU usage:**
- Profile CPU-intensive code
- Optimize algorithms
- Consider caching

**Connection pool exhaustion:**
- Increase pool size
- Fix connection leaks
- Add connection timeout

## CI/CD Integration

Performance tests in CI/CD:

1. **Automated execution:**
   ```yaml
   - name: Run Performance Tests
     run: ./testing/run-tests.sh --suite performance
   ```

2. **Performance regression detection:**
   - Compare against baseline metrics
   - Fail if thresholds exceeded
   - Track performance trends

3. **Report artifacts:**
   ```yaml
   - name: Upload Performance Report
     uses: actions/upload-artifact@v4
     with:
       name: performance-report
       path: testing/reports/html/performance-report.html
   ```

## Future Implementation

See Story 13.11 for full performance test suite implementation including:
- Login flow performance tests
- Page load performance tests
- API endpoint performance tests
- Form submission performance tests
- Database query benchmarks
- Comprehensive performance reporting
- Performance regression detection
