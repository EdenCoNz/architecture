# Test Execution Reporting - Usage Examples

Complete examples demonstrating all features of the test execution reporting system.

**Story 13.15: Test Execution Reporting**

## Table of Contents

1. [Basic Report Generation](#basic-report-generation)
2. [Report with Historical Trends](#report-with-historical-trends)
3. [Flaky Test Detection](#flaky-test-detection)
4. [Complete CI/CD Integration](#complete-cicd-integration)
5. [Python API Usage](#python-api-usage)
6. [Manual PDF Generation](#manual-pdf-generation)

## Basic Report Generation

### Generate HTML and JSON Reports from E2E Tests

```bash
cd testing/reporting

python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json
```

**Output:**
- `testing/reports/test-report.html` - Interactive HTML report
- `testing/reports/test-report.json` - Machine-readable JSON

### Generate Reports from All Test Types

```bash
python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json \
  --integration-report ../integration/test-results.json \
  --visual-report ../visual/test-results.json \
  --performance-report ../performance/test-results.json
```

## Report with Historical Trends

### Enable Trend Tracking (30-day window)

```bash
python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json \
  --with-trends \
  --trends-days 30
```

**Output:**
- `testing/reports/test-report.html`
- `testing/reports/test-report.json`
- `testing/reports/test-trends.json` - Historical trend data

### Custom Trend Analysis Period

```bash
# Analyze last 90 days
python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json \
  --with-trends \
  --trends-days 90
```

### View Trend Data

```bash
# Export trends to JSON
python -c "
from reporting import TrendAnalyzer
analyzer = TrendAnalyzer('../reports/trends.db')
trends = analyzer.get_trends_summary(days=30)

print('Pass Rate Trend:', len(trends['pass_rate_trend']), 'runs')
print('Flaky Tests:', len(trends['flaky_tests']))
print('Performance Trends:', len(trends['performance_trends']), 'runs')
"
```

## Flaky Test Detection

### Detect Flaky Tests (Standalone)

```bash
python generate_report.py \
  --output-dir ../reports \
  --detect-flaky \
  --flaky-min-runs 5 \
  --trends-days 30
```

**Output:**
- `testing/reports/flaky-tests-report.json`

### Flaky Detection with Custom Thresholds

```bash
# Require minimum 10 runs to identify flaky tests
python generate_report.py \
  --output-dir ../reports \
  --detect-flaky \
  --flaky-min-runs 10 \
  --trends-days 60
```

### Combined Report and Flaky Detection

```bash
python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json \
  --with-trends \
  --detect-flaky \
  --flaky-min-runs 5 \
  --trends-days 30
```

**Output:**
- Test report (HTML + JSON)
- Trend data
- Flaky test analysis

## Complete CI/CD Integration

### GitHub Actions Workflow Step

```yaml
- name: Generate comprehensive test report
  if: always()
  run: |
    cd testing/reporting

    # Install dependencies
    pip install -r ../requirements.txt

    # Generate reports with metadata
    python generate_report.py \
      --output-dir ../reports \
      --e2e-report ../e2e/test-results.json \
      --integration-report ../integration/test-results.json \
      --performance-report ../performance/test-results.json \
      --with-trends \
      --detect-flaky \
      --git-commit ${{ github.sha }} \
      --git-branch ${{ github.ref_name }} \
      --ci-run-id ${{ github.run_id }} \
      --no-pdf  # Skip PDF in CI/CD

- name: Upload comprehensive reports
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-reports-${{ github.sha }}
    path: |
      testing/reports/test-report.html
      testing/reports/test-report.json
      testing/reports/test-trends.json
      testing/reports/flaky-tests-report.json
    retention-days: 30
```

### With Docker Compose (Test Runner Container)

```bash
# In CI/CD workflow
docker compose -f docker-compose.yml -f compose.test.yml \
  run --rm test-runner \
  bash -c "cd /app/testing/reporting && \
    pip install -r ../requirements.txt && \
    python generate_report.py \
      --output-dir ../reports \
      --e2e-report ../e2e/test-results.json \
      --with-trends \
      --detect-flaky \
      --git-commit ${GITHUB_SHA} \
      --git-branch ${GITHUB_REF_NAME} \
      --ci-run-id ${GITHUB_RUN_ID} \
      --no-pdf"
```

## Python API Usage

### Basic Report Generation

```python
from pathlib import Path
from reporting import TestReportGenerator

# Initialize generator
generator = TestReportGenerator(output_dir=Path('reports'))

# Aggregate test results
aggregated_data = generator.aggregate_test_results(
    e2e_report=Path('e2e/test-results.json'),
    integration_report=Path('integration/test-results.json'),
)

# Generate HTML report
generator.generate_html_report(
    aggregated_data,
    Path('reports/test-report.html')
)

# Generate JSON report
generator.generate_json_report(
    aggregated_data,
    Path('reports/test-report.json')
)

print(f"Total tests: {aggregated_data['summary']['total_tests']}")
print(f"Pass rate: {aggregated_data['summary']['pass_rate']:.1f}%")
```

### Historical Trend Analysis

```python
from pathlib import Path
from reporting import TrendAnalyzer

# Initialize analyzer
analyzer = TrendAnalyzer(database_path=Path('reports/trends.db'))

# Store test run
run_id = analyzer.store_test_run(aggregated_data)
print(f"Stored test run: {run_id}")

# Get pass rate trend (last 30 days)
pass_rate_trend = analyzer.get_pass_rate_trend(days=30)
for entry in pass_rate_trend:
    print(f"{entry['timestamp']}: {entry['pass_rate']:.1f}% ({entry['passed']}/{entry['total_tests']})")

# Get performance trends
perf_trends = analyzer.get_performance_trends(days=30)
for entry in perf_trends:
    print(f"{entry['timestamp']}: {entry['response_time_95th']}ms (P95)")

# Export trends to JSON
analyzer.export_trends_to_json(
    Path('reports/test-trends.json'),
    days=30
)
```

### Flaky Test Detection

```python
from pathlib import Path
from reporting import TrendAnalyzer, FlakyTestDetector

# Initialize
analyzer = TrendAnalyzer(Path('reports/trends.db'))
detector = FlakyTestDetector(analyzer)

# Detect flaky tests
flaky_tests = detector.detect_flaky_tests(
    days=30,
    min_runs=5,
    flakiness_threshold=10.0  # 10% minimum failure rate
)

# Print results by severity
for test in flaky_tests:
    print(f"\n{test['severity'].upper()}: {test['test_name']}")
    print(f"  Suite: {test['suite']}")
    print(f"  Runs: {test['total_runs']} (Failures: {test['failures']}, Passes: {test['passes']})")
    print(f"  Failure Rate: {test['failure_rate']:.1f}%")
    print(f"  Impact Score: {test['impact_score']}")
    print(f"  Recommendations:")
    for rec in test['recommendations'][:3]:
        print(f"    - {rec}")

# Generate flaky test report
detector.generate_flaky_test_report(
    Path('reports/flaky-tests-report.json'),
    days=30,
    min_runs=5
)
```

### Complete Workflow

```python
from pathlib import Path
from reporting import TestReportGenerator, TrendAnalyzer, FlakyTestDetector

# Step 1: Generate test report
print("Generating test reports...")
generator = TestReportGenerator(Path('reports'))

aggregated_data = generator.aggregate_test_results(
    e2e_report=Path('e2e/test-results.json'),
    integration_report=Path('integration/test-results.json'),
    visual_report=Path('visual/test-results.json'),
    performance_report=Path('performance/test-results.json'),
)

# Add metadata
aggregated_data['metadata']['git_commit'] = 'abc123'
aggregated_data['metadata']['git_branch'] = 'main'

generator.generate_html_report(aggregated_data, Path('reports/test-report.html'))
generator.generate_json_report(aggregated_data, Path('reports/test-report.json'))

# Step 2: Store for trend analysis
print("Storing test results for trend analysis...")
analyzer = TrendAnalyzer(Path('reports/trends.db'))
run_id = analyzer.store_test_run(aggregated_data)

# Step 3: Export trends
print("Exporting trend data...")
analyzer.export_trends_to_json(Path('reports/test-trends.json'), days=30)

# Step 4: Detect flaky tests
print("Detecting flaky tests...")
detector = FlakyTestDetector(analyzer)
detector.generate_flaky_test_report(Path('reports/flaky-tests-report.json'), days=30)

print("\n✅ All reports generated successfully!")
```

## Manual PDF Generation

### Generate PDF from HTML Report

```python
from pathlib import Path
from reporting import TestReportGenerator

generator = TestReportGenerator(Path('reports'))

# Generate PDF from existing HTML report
generator.generate_pdf_report(
    html_report=Path('reports/test-report.html'),
    output_file=Path('reports/test-report.pdf')
)
```

### Using WeasyPrint Directly

```python
from weasyprint import HTML

# Convert HTML to PDF
HTML('reports/test-report.html').write_pdf('reports/test-report.pdf')
```

### System Dependencies for PDF Generation

**Ubuntu/Debian:**
```bash
sudo apt-get install -y \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info

pip install weasyprint
```

**macOS:**
```bash
brew install pango gdk-pixbuf libffi
pip install weasyprint
```

## Advanced Usage

### Query Trend Database Directly

```python
import sqlite3
from pathlib import Path

conn = sqlite3.connect('reports/trends.db')
cursor = conn.cursor()

# Get recent test runs
cursor.execute("""
    SELECT timestamp, pass_rate, total_tests, failed
    FROM test_runs
    ORDER BY timestamp DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    timestamp, pass_rate, total, failed = row
    print(f"{timestamp}: {pass_rate:.1f}% ({failed} failures)")

conn.close()
```

### Custom Flaky Test Filtering

```python
from reporting import TrendAnalyzer, FlakyTestDetector

analyzer = TrendAnalyzer('reports/trends.db')
detector = FlakyTestDetector(analyzer)

# Get all flaky tests
flaky_tests = detector.detect_flaky_tests(days=30, min_runs=5)

# Filter critical only
critical_flaky = [t for t in flaky_tests if t['severity'] == 'critical']

# Filter by suite
e2e_flaky = [t for t in flaky_tests if t['suite'] == 'e2e']

# Sort by impact score
flaky_tests.sort(key=lambda x: x['impact_score'], reverse=True)
top_10_flaky = flaky_tests[:10]
```

### Export Specific Trend Metrics

```python
from reporting import TrendAnalyzer

analyzer = TrendAnalyzer('reports/trends.db')

# Get only pass rate trend
pass_rate = analyzer.get_pass_rate_trend(days=30)

# Get only performance trends
perf = analyzer.get_performance_trends(days=30)

# Get only duration trends
duration = analyzer.get_duration_trends(days=30)

# Export to separate files
import json

with open('reports/pass-rate-trend.json', 'w') as f:
    json.dump(pass_rate, f, indent=2)

with open('reports/performance-trend.json', 'w') as f:
    json.dump(perf, f, indent=2)

with open('reports/duration-trend.json', 'w') as f:
    json.dump(duration, f, indent=2)
```

## Troubleshooting Examples

### Handle Missing Test Results

```python
from pathlib import Path
from reporting import TestReportGenerator

generator = TestReportGenerator(Path('reports'))

# Check if test results exist before aggregating
e2e_report = Path('e2e/test-results.json')
if e2e_report.exists():
    aggregated_data = generator.aggregate_test_results(
        e2e_report=e2e_report
    )
else:
    print("Warning: E2E test results not found")
```

### Graceful PDF Generation Failure

```python
from reporting import TestReportGenerator

generator = TestReportGenerator(Path('reports'))

# Generate HTML report
html_file = Path('reports/test-report.html')
generator.generate_html_report(aggregated_data, html_file)

# Try PDF generation with error handling
pdf_file = Path('reports/test-report.pdf')
try:
    generator.generate_pdf_report(html_file, pdf_file)
    print("✅ PDF report generated")
except Exception as e:
    print(f"⚠️  PDF generation failed: {e}")
    print("   HTML and JSON reports are still available")
```

### Verify Trend Database

```python
import sqlite3
from pathlib import Path

db_path = Path('reports/trends.db')

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count test runs
    cursor.execute("SELECT COUNT(*) FROM test_runs")
    count = cursor.fetchone()[0]
    print(f"Test runs in database: {count}")

    # Get date range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM test_runs")
    min_date, max_date = cursor.fetchone()
    print(f"Date range: {min_date} to {max_date}")

    conn.close()
else:
    print("Trend database not found - run with --with-trends to create")
```

## Real-World Scenarios

### Scenario 1: Daily CI/CD Report

```bash
#!/bin/bash
# daily-test-report.sh

cd testing/reporting

# Run all tests and generate comprehensive report
python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json \
  --integration-report ../integration/test-results.json \
  --with-trends \
  --detect-flaky \
  --git-commit $(git rev-parse HEAD) \
  --git-branch $(git branch --show-current) \
  --trends-days 30

# Upload to artifact storage or S3
# aws s3 cp ../reports/test-report.html s3://test-reports/$(date +%Y-%m-%d)/
```

### Scenario 2: Weekly Flaky Test Review

```python
#!/usr/bin/env python3
# weekly-flaky-review.py

from pathlib import Path
from reporting import TrendAnalyzer, FlakyTestDetector

# Detect flaky tests over last 7 days
analyzer = TrendAnalyzer(Path('reports/trends.db'))
detector = FlakyTestDetector(analyzer)

flaky_tests = detector.detect_flaky_tests(days=7, min_runs=3)

# Send email/Slack notification for critical flaky tests
critical = [t for t in flaky_tests if t['severity'] == 'critical']

if critical:
    print(f"⚠️  {len(critical)} CRITICAL flaky tests detected!")
    for test in critical:
        print(f"  - {test['test_name']}: {test['failure_rate']:.1f}% failure rate")

    # TODO: Send notification
```

### Scenario 3: Performance Regression Detection

```python
from reporting import TrendAnalyzer

analyzer = TrendAnalyzer('reports/trends.db')
perf_trends = analyzer.get_performance_trends(days=30)

# Check for response time regression
if len(perf_trends) >= 2:
    latest = perf_trends[-1]
    previous = perf_trends[-2]

    p95_increase = latest['response_time_95th'] - previous['response_time_95th']

    if p95_increase > 100:  # More than 100ms increase
        print(f"⚠️  Performance regression detected!")
        print(f"   P95 increased by {p95_increase}ms")
        print(f"   Previous: {previous['response_time_95th']}ms")
        print(f"   Current: {latest['response_time_95th']}ms")
```

## Best Practices

### 1. Always Enable Trends in CI/CD

```bash
# Good - tracks trends over time
python generate_report.py \
  --e2e-report e2e/test-results.json \
  --with-trends

# Bad - no historical tracking
python generate_report.py \
  --e2e-report e2e/test-results.json
```

### 2. Run Flaky Detection Weekly

```bash
# Automated weekly cron job
0 0 * * 0 cd /app/testing/reporting && \
  python generate_report.py \
    --detect-flaky \
    --flaky-min-runs 5 \
    --trends-days 7
```

### 3. Include All Metadata in CI/CD

```bash
# Complete metadata tracking
python generate_report.py \
  --e2e-report e2e/test-results.json \
  --git-commit $GITHUB_SHA \
  --git-branch $GITHUB_REF_NAME \
  --ci-run-id $GITHUB_RUN_ID
```

### 4. Skip PDF in CI/CD, Generate Manually

```bash
# CI/CD - fast, no system dependencies
python generate_report.py \
  --e2e-report e2e/test-results.json \
  --no-pdf

# Local - generate PDF for stakeholder report
python generate_report.py \
  --e2e-report e2e/test-results.json
```

## Summary

This reporting system provides:

✅ **Comprehensive test reporting** from multiple frameworks
✅ **Historical trend tracking** for quality metrics
✅ **Flaky test detection** with actionable recommendations
✅ **Multiple output formats** (HTML, JSON, PDF)
✅ **CI/CD integration** with GitHub Actions
✅ **Python API** for custom workflows

For more details, see [README.md](README.md).
