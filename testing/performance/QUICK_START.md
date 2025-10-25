# Performance Testing Quick Start Guide

## Run Tests Locally

### Basic Performance Test
```bash
./testing/run-tests.sh --suite performance
```

### Specific Scenarios

**Login Flow Only:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    locust -f performance/scenarios/user_login.py \
    --host=http://proxy:80 \
    --headless \
    --users 20 \
    --spawn-rate 5 \
    --run-time 60s \
    --html=reports/html/login-performance.html
```

**API Endpoints Only:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    locust -f performance/scenarios/api_endpoints.py \
    --host=http://proxy:80 \
    --headless \
    --users 30 \
    --spawn-rate 10 \
    --run-time 120s \
    --html=reports/html/api-performance.html
```

**Page Load Only:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    locust -f performance/scenarios/page_load.py \
    --host=http://proxy:80 \
    --headless \
    --users 25 \
    --spawn-rate 5 \
    --run-time 90s \
    --html=reports/html/pageload-performance.html
```

**Form Submission Only:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    locust -f performance/scenarios/form_submission.py \
    --host=http://proxy:80 \
    --headless \
    --users 15 \
    --spawn-rate 3 \
    --run-time 120s \
    --html=reports/html/forms-performance.html
```

### Load Test Profiles

**Normal Load (10 users):**
```bash
locust -f performance/locustfile.py \
    --host=http://proxy:80 \
    --headless \
    --users 10 \
    --spawn-rate 2 \
    --run-time 300s
```

**Peak Load (50 users):**
```bash
locust -f performance/locustfile.py \
    --host=http://proxy:80 \
    --headless \
    --users 50 \
    --spawn-rate 5 \
    --run-time 600s
```

**Stress Test (100 users):**
```bash
locust -f performance/locustfile.py \
    --host=http://proxy:80 \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 300s
```

**Spike Test (rapid increase):**
```bash
locust -f performance/locustfile.py \
    --host=http://proxy:80 \
    --headless \
    --users 100 \
    --spawn-rate 50 \
    --run-time 120s
```

## Interactive Testing (Web UI)

Start Locust with web interface:
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm -p 8089:8089 test-runner \
    locust -f performance/locustfile.py --host=http://proxy:80
```

Then open: http://localhost:8089

## View Reports

**HTML Reports:**
```bash
open testing/reports/html/performance-report.html
```

**JSON Reports (for automation):**
```bash
cat testing/reports/json/performance-report.json | jq '.'
```

**CSV Data:**
```bash
cat testing/reports/csv/performance-data_stats.csv
```

## GitHub Actions

### Manual Trigger
1. Go to GitHub → Actions → "Performance Tests"
2. Click "Run workflow"
3. Select load type: normal / peak / stress / spike
4. Set duration and user count (optional)
5. Click "Run workflow"

### View Results
- Check workflow summary for pass/fail status
- Download artifacts for detailed reports
- PR comments show performance metrics automatically

## Performance Thresholds

| Operation | Threshold | Status |
|-----------|-----------|--------|
| API Requests | < 500ms | ✅ Enforced |
| Page Loads | < 2000ms | ✅ Enforced |
| Form Submissions | < 1000ms | ✅ Enforced |
| Health Checks | < 100ms | ✅ Enforced |
| Failure Rate | < 1% | ✅ Enforced |
| Throughput | > 50 RPS | ✅ Enforced |

## Common Issues

### "Test Failed" - Threshold Violations
**Check:** HTML report shows which endpoints are slow
**Fix:** Optimize backend code, add database indexes, implement caching

### "Low Throughput"
**Check:** System resources (CPU, memory)
**Fix:** Increase container resources, optimize queries, reduce logging

### "Service Timeout"
**Check:** Service health before test
**Fix:** Wait for services to be healthy before running tests

## Need Help?

- Documentation: `testing/performance/README.md`
- Implementation Details: `testing/performance/STORY_13_11_IMPLEMENTATION.md`
- Configuration: `testing/performance/config.py`
- Main Test Suite: `testing/README.md`
