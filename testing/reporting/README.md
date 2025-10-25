# Test Execution Reporting

Comprehensive test reporting system that aggregates results from all test types (E2E, integration, visual, performance) and generates HTML, JSON, and PDF reports with historical trends and flaky test detection.

**Story 13.15: Test Execution Reporting**

## Features

- **Multi-Format Reports**: Generate HTML, JSON, and PDF reports from test results
- **Test Result Aggregation**: Combine results from Playwright (E2E), pytest (integration), visual regression, and Locust (performance) tests
- **Historical Trends**: Track test metrics over time to identify trends and patterns
- **Flaky Test Detection**: Automatically identify tests with inconsistent pass/fail behavior
- **Rich Visualizations**: Charts, graphs, and metrics for easy analysis
- **CI/CD Integration**: Seamlessly integrate with GitHub Actions workflows

## Acceptance Criteria

- ✅ **AC1**: Pass/fail status for each test with execution time
- ✅ **AC2**: Error messages, stack traces, and screenshots for failures
- ✅ **AC3**: Historical trends (pass rate over time, flaky tests, performance trends)
- ✅ **AC4**: Standard formats (HTML, JSON, PDF) viewable without specialized tools

## Quick Start

### Generate Test Report

```bash
# From testing/reporting directory
python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json \
  --integration-report ../integration/test-results.json \
  --visual-report ../visual/test-results.json \
  --performance-report ../performance/test-results.json
```

### Generate Report with Trends

```bash
python generate_report.py \
  --output-dir ../reports \
  --e2e-report ../e2e/test-results.json \
  --with-trends \
  --trends-days 30
```

### Detect Flaky Tests

```bash
python generate_report.py \
  --output-dir ../reports \
  --detect-flaky \
  --flaky-min-runs 5 \
  --trends-days 30
```

## Usage

### Python API

```python
from reporting import TestReportGenerator, TrendAnalyzer, FlakyTestDetector

# Generate test report
generator = TestReportGenerator(output_dir='reports/')
aggregated_data = generator.aggregate_test_results(
    e2e_report='e2e/test-results.json',
    integration_report='integration/test-results.json',
)

# Generate HTML report
generator.generate_html_report(aggregated_data, 'reports/test-report.html')

# Generate JSON report
generator.generate_json_report(aggregated_data, 'reports/test-report.json')

# Generate PDF report
generator.generate_pdf_report('reports/test-report.html', 'reports/test-report.pdf')

# Trend analysis
trend_analyzer = TrendAnalyzer('reports/trends.db')
trend_analyzer.store_test_run(aggregated_data)
trends = trend_analyzer.get_trends_summary(days=30)

# Flaky test detection
flaky_detector = FlakyTestDetector(trend_analyzer)
flaky_tests = flaky_detector.detect_flaky_tests(days=30, min_runs=5)
```

### Command-Line Interface

```bash
# Full usage
python generate_report.py --help

# Generate all report types
python generate_report.py \
  --output-dir reports/ \
  --e2e-report e2e/test-results.json \
  --integration-report integration/test-results.json \
  --visual-report visual/test-results.json \
  --performance-report performance/test-results.json \
  --with-trends \
  --detect-flaky \
  --git-commit $GITHUB_SHA \
  --git-branch $GITHUB_REF_NAME \
  --ci-run-id $GITHUB_RUN_ID

# Skip PDF generation (faster)
python generate_report.py \
  --output-dir reports/ \
  --e2e-report e2e/test-results.json \
  --no-pdf
```

## Report Formats

### HTML Report

**File**: `test-report.html`

Rich, interactive HTML report with:
- Overall test summary with pass rate visualization
- Test suite breakdowns (E2E, integration, visual, performance)
- Detailed failure information with error messages and stack traces
- Screenshots captured at point of failure (for E2E tests)
- Performance metrics (RPS, response times, failure rate)

**Viewable in**: Any modern web browser (Chrome, Firefox, Safari, Edge)

### JSON Report

**File**: `test-report.json`

Machine-readable JSON format with:
- Complete test results structure
- Test suite statistics
- Individual failure details
- Metadata (git commit, branch, CI run ID)

**Use cases**:
- Programmatic analysis of test results
- Integration with custom dashboards
- Historical data storage
- API responses

**Example structure**:
```json
{
  "timestamp": "2025-10-26T12:00:00Z",
  "summary": {
    "total_tests": 150,
    "passed": 145,
    "failed": 5,
    "skipped": 0,
    "pass_rate": 96.67,
    "duration_seconds": 245.3
  },
  "test_suites": {
    "e2e": { ... },
    "integration": { ... }
  },
  "failures": [ ... ],
  "metadata": { ... }
}
```

### PDF Report

**File**: `test-report.pdf`

Print-ready PDF generated from HTML report with:
- Professional formatting for sharing
- All sections from HTML report
- Optimized for A4/Letter paper
- Embedded screenshots and charts

**Use cases**:
- Stakeholder reports
- Audit trail documentation
- Email attachments
- Archive storage

**Note**: PDF generation requires WeasyPrint and its dependencies. If PDF generation fails, HTML and JSON reports will still be generated.

## Historical Trends

### Database Schema

Test results are stored in SQLite database (`trends.db`) with three tables:

1. **test_runs**: Overall test run statistics
2. **test_results**: Individual test results
3. **performance_metrics**: Performance test metrics

### Trend Analysis

Available trend metrics:
- **Pass Rate Trend**: Track pass rate over time to identify quality degradation
- **Flaky Tests**: Tests with inconsistent pass/fail behavior
- **Performance Trends**: Response times, throughput, and error rates over time
- **Duration Trends**: Test execution time trends

### Export Trends

```bash
# Export trends to JSON
python -c "
from reporting import TrendAnalyzer
analyzer = TrendAnalyzer('reports/trends.db')
analyzer.export_trends_to_json('reports/test-trends.json', days=30)
"
```

## Flaky Test Detection

### Detection Algorithm

Flaky tests are identified using:
1. **Inconsistency Detection**: Tests that both pass and fail over time
2. **Minimum Runs Threshold**: Requires minimum number of runs (default: 5)
3. **Severity Classification**: Critical, high, medium, low based on failure rate
4. **Impact Scoring**: Prioritization based on failure rate, frequency, and failures

### Severity Levels

- **Critical**: ≥50% failure rate with ≥10 runs
- **High**: ≥30% failure rate or ≥20 runs
- **Medium**: ≥20% failure rate
- **Low**: <20% failure rate

### Recommendations

Flaky test reports include actionable recommendations:
- Generic best practices for test stability
- Suite-specific advice (E2E, integration, visual)
- Debugging steps and resources

### Example Flaky Test Report

```json
{
  "generated_at": "2025-10-26T12:00:00Z",
  "analysis_period_days": 30,
  "total_flaky_tests": 8,
  "flaky_tests_by_severity": {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 2
  },
  "flaky_tests": [
    {
      "test_name": "test_user_login_with_valid_credentials",
      "suite": "e2e",
      "total_runs": 15,
      "failures": 8,
      "passes": 7,
      "failure_rate": 53.33,
      "severity": "critical",
      "impact_score": 47.5,
      "recommendations": [...]
    }
  ]
}
```

## CI/CD Integration

### GitHub Actions

Example workflow integration:

```yaml
- name: Generate comprehensive test report
  if: always()
  run: |
    cd testing/reporting
    python generate_report.py \
      --output-dir ../reports \
      --e2e-report ../e2e/test-results.json \
      --integration-report ../integration/test-results.json \
      --with-trends \
      --detect-flaky \
      --git-commit ${{ github.sha }} \
      --git-branch ${{ github.ref_name }} \
      --ci-run-id ${{ github.run_id }}

- name: Upload test reports
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-reports-${{ github.sha }}
    path: testing/reports/
    retention-days: 30
```

### Artifact Publishing

Reports are published as GitHub Actions artifacts:
- **test-report.html**: Interactive HTML report
- **test-report.json**: Machine-readable JSON
- **test-report.pdf**: Print-ready PDF (optional)
- **test-trends.json**: Historical trends data
- **flaky-tests-report.json**: Flaky test analysis

## Dependencies

Required Python packages (included in `testing/requirements.txt`):

```
jinja2>=3.1.2,<4.0.0              # HTML template engine
weasyprint>=60.0,<61.0            # PDF generation
matplotlib>=3.8.0,<4.0.0          # Charts and visualizations
```

### PDF Generation Requirements

WeasyPrint requires system dependencies:

**Ubuntu/Debian**:
```bash
sudo apt-get install -y \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info
```

**macOS**:
```bash
brew install pango gdk-pixbuf libffi
```

**Note**: If PDF generation fails, HTML and JSON reports are still generated.

## Troubleshooting

### PDF Generation Fails

**Symptom**: `weasyprint` import error or PDF generation exception

**Solutions**:
1. Install system dependencies (see above)
2. Use `--no-pdf` flag to skip PDF generation
3. Generate PDF manually from HTML report using external tools

### Trends Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Solution**: Ensure no other processes are accessing `trends.db`

### Missing Test Results

**Symptom**: Report shows 0 tests or missing suites

**Solution**: Verify test result JSON files exist and have correct format

### Template Not Found

**Symptom**: `jinja2.exceptions.TemplateNotFound: test_report.html`

**Solution**: Run from `testing/reporting/` directory or set correct template path

## Architecture

### Module Structure

```
testing/reporting/
├── __init__.py              # Package exports
├── report_generator.py      # Main report generation
├── trend_analyzer.py        # Historical trend analysis
├── flaky_detector.py        # Flaky test detection
├── generate_report.py       # CLI entry point
├── templates/
│   └── test_report.html     # HTML report template
└── README.md                # This file
```

### Data Flow

```
Test Results (JSON)
       ↓
  Aggregation
       ↓
  Report Generation
       ↓
  HTML / JSON / PDF
       ↓
  Trend Storage (SQLite)
       ↓
  Flaky Detection
```

## Best Practices

### Report Generation

1. **Always generate JSON reports** - Machine-readable format for automation
2. **Store trends in CI/CD** - Enable historical analysis across runs
3. **Act on flaky tests** - Fix or disable tests with high impact scores
4. **Share HTML reports** - Easy-to-read format for stakeholders
5. **Archive PDF reports** - Long-term documentation and audit trail

### Trend Analysis

1. **Run trends weekly** - Identify patterns before they become critical
2. **Monitor pass rate trends** - Catch quality degradation early
3. **Prioritize by impact score** - Fix high-impact flaky tests first
4. **Review performance trends** - Detect gradual performance regression

### Flaky Test Management

1. **Fix critical flaky tests immediately** - Block deployments if needed
2. **Investigate high-impact tests** - Most disruptive to CI/CD
3. **Disable severe flaky tests** - Better than unreliable CI/CD
4. **Track fixes over time** - Measure improvement in test stability

## Examples

### Complete CI/CD Report Generation

```yaml
# In GitHub Actions workflow
- name: Run all tests
  run: |
    # E2E tests
    cd testing/e2e
    npx playwright test --reporter=json > ../reports/e2e-results.json

    # Integration tests
    cd ../integration
    pytest --json-report --json-report-file=../reports/integration-results.json

    # Performance tests
    cd ../performance
    locust --headless --json > ../reports/performance-results.json

- name: Generate comprehensive report
  if: always()
  run: |
    cd testing/reporting
    python generate_report.py \
      --output-dir ../reports \
      --e2e-report ../reports/e2e-results.json \
      --integration-report ../reports/integration-results.json \
      --performance-report ../reports/performance-results.json \
      --with-trends \
      --detect-flaky \
      --git-commit ${{ github.sha }} \
      --git-branch ${{ github.ref_name }} \
      --ci-run-id ${{ github.run_id }}

- name: Publish reports
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-reports
    path: testing/reports/
```

## Future Enhancements

Potential improvements for future iterations:

- Interactive trend charts with Chart.js or D3.js
- Real-time reporting dashboard
- Slack/email notifications for flaky tests
- Custom report themes and branding
- Multi-project support
- Test coverage integration
- Performance baseline comparison
- Automatic flaky test quarantine

## Support

For issues or questions:
- Review test results JSON format compatibility
- Check system dependencies for PDF generation
- Verify database permissions for trend storage
- Ensure template files are accessible

## License

Part of Feature #13: End-to-End Testing Suite
Story 13.15: Test Execution Reporting
