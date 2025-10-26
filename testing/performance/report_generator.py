#!/usr/bin/env python3
"""
Performance Test Report Generator

Generates comprehensive performance reports from Locust test results.

Features:
- HTML report with charts and visualizations
- JSON report for CI/CD integration
- CSV data export for analysis
- Threshold validation and pass/fail determination

Usage:
    python report_generator.py --input stats.json --output-dir reports/
"""

import argparse
import csv
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .config import ACCEPTANCE_CRITERIA, THRESHOLDS, get_threshold, meets_acceptance_criteria


class PerformanceReportGenerator:
    """Generate comprehensive performance test reports."""

    def __init__(self, stats_file: Path, output_dir: Path):
        """
        Initialize report generator.

        Args:
            stats_file: Path to Locust stats JSON file
            output_dir: Directory for output reports
        """
        self.stats_file = stats_file
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.stats = self._load_stats()
        self.summary = self._calculate_summary()

    def _load_stats(self) -> Dict:
        """Load statistics from Locust JSON output."""
        if not self.stats_file.exists():
            return {"stats": [], "errors": []}

        with open(self.stats_file) as f:
            return json.load(f)

    def _calculate_summary(self) -> Dict:
        """Calculate summary statistics from test results."""
        stats = self.stats.get("stats", [])

        if not stats:
            return {}

        # Filter out aggregated stats (usually last entry)
        request_stats = [s for s in stats if s.get("name") != "Aggregated"]

        # Calculate overall metrics
        total_requests = sum(s.get("num_requests", 0) for s in request_stats)
        total_failures = sum(s.get("num_failures", 0) for s in request_stats)

        # Get response time percentiles (from aggregated stats if available)
        aggregated = next(
            (s for s in stats if s.get("name") == "Aggregated"),
            request_stats[0] if request_stats else {},
        )

        response_times = {
            "50th": aggregated.get("response_time_percentile_50", 0),
            "75th": aggregated.get("response_time_percentile_75", 0),
            "90th": aggregated.get("response_time_percentile_90", 0),
            "95th": aggregated.get("response_time_percentile_95", 0),
            "99th": aggregated.get("response_time_percentile_99", 0),
            "avg": aggregated.get("avg_response_time", 0),
            "min": aggregated.get("min_response_time", 0),
            "max": aggregated.get("max_response_time", 0),
        }

        # Calculate RPS
        test_duration = self.stats.get("test_duration", 1)
        rps = total_requests / test_duration if test_duration > 0 else 0

        # Calculate failure rate
        failure_rate = (
            (total_failures / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "total_requests": total_requests,
            "total_failures": total_failures,
            "failure_rate": failure_rate,
            "requests_per_second": rps,
            "response_times": response_times,
            "test_duration": test_duration,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_json_report(self) -> Path:
        """Generate JSON report for CI/CD integration."""
        report = {
            "test_run": {
                "timestamp": self.summary.get("timestamp"),
                "duration_seconds": self.summary.get("test_duration"),
            },
            "summary": {
                "total_requests": self.summary.get("total_requests"),
                "total_failures": self.summary.get("total_failures"),
                "failure_rate_percent": round(self.summary.get("failure_rate", 0), 2),
                "requests_per_second": round(
                    self.summary.get("requests_per_second", 0), 2
                ),
            },
            "response_times_ms": self.summary.get("response_times", {}),
            "acceptance_criteria": ACCEPTANCE_CRITERIA,
            "threshold_violations": self._get_threshold_violations(),
        }

        # Determine pass/fail
        passed, failures = meets_acceptance_criteria(
            {
                "api_response_time_95th": self.summary["response_times"]["95th"],
                "page_load_time_95th": self.summary["response_times"]["95th"],
                "failure_rate": self.summary["failure_rate"],
                "requests_per_second": self.summary["requests_per_second"],
            }
        )

        report["result"] = {
            "passed": passed,
            "failures": failures,
        }

        output_file = self.output_dir / "performance-report.json"
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✓ JSON report generated: {output_file}")
        return output_file

    def generate_html_report(self) -> Path:
        """Generate HTML report with visualizations."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2em;
        }}

        .timestamp {{
            color: #7f8c8d;
            margin-bottom: 30px;
        }}

        .status {{
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 30px;
            font-weight: 600;
        }}

        .status.pass {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}

        .status.fail {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}

        .metric-label {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: 700;
            color: #2c3e50;
        }}

        .metric-unit {{
            font-size: 0.5em;
            color: #7f8c8d;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .violations {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }}

        .violations h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}

        .violations ul {{
            list-style-position: inside;
            color: #856404;
        }}

        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Performance Test Report</h1>
        <div class="timestamp">Generated: {self.summary.get('timestamp', 'N/A')}</div>

        <div class="status {'pass' if self._check_passed() else 'fail'}">
            {(
                '✅ All tests passed - Performance within acceptable thresholds'
                if self._check_passed()
                else '❌ Tests failed - Performance issues detected'
            )}
        </div>

        <h2>📊 Summary Metrics</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{self.summary.get('total_requests', 0):,}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Failure Rate</div>
                <div class="metric-value">
                    {self.summary.get('failure_rate', 0):.2f}
                    <span class="metric-unit">%</span>
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Throughput</div>
                <div class="metric-value">
                    {self.summary.get('requests_per_second', 0):.1f}
                    <span class="metric-unit">RPS</span>
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Test Duration</div>
                <div class="metric-value">
                    {self.summary.get('test_duration', 0):.0f}
                    <span class="metric-unit">sec</span>
                </div>
            </div>
        </div>

        <h2>⏱️ Response Times (milliseconds)</h2>
        <table>
            <thead>
                <tr>
                    <th>Percentile</th>
                    <th>Response Time</th>
                    <th>Threshold</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_response_time_rows()}
            </tbody>
        </table>

        {self._generate_violations_section()}

        <div class="footer">
            Performance test report generated by automated testing suite
        </div>
    </div>
</body>
</html>"""

        output_file = self.output_dir / "performance-report.html"
        with open(output_file, "w") as f:
            f.write(html_content)

        print(f"✓ HTML report generated: {output_file}")
        return output_file

    def generate_csv_export(self) -> Path:
        """Generate CSV export of performance data."""
        output_file = self.output_dir / "performance-data.csv"

        stats = self.stats.get("stats", [])
        if not stats:
            return output_file

        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "name",
                    "method",
                    "num_requests",
                    "num_failures",
                    "avg_response_time",
                    "min_response_time",
                    "max_response_time",
                    "response_time_percentile_50",
                    "response_time_percentile_95",
                    "response_time_percentile_99",
                    "requests_per_second",
                ],
            )
            writer.writeheader()

            for stat in stats:
                writer.writerow(
                    {
                        "name": stat.get("name", ""),
                        "method": stat.get("method", ""),
                        "num_requests": stat.get("num_requests", 0),
                        "num_failures": stat.get("num_failures", 0),
                        "avg_response_time": stat.get("avg_response_time", 0),
                        "min_response_time": stat.get("min_response_time", 0),
                        "max_response_time": stat.get("max_response_time", 0),
                        "response_time_percentile_50": stat.get(
                            "response_time_percentile_50", 0
                        ),
                        "response_time_percentile_95": stat.get(
                            "response_time_percentile_95", 0
                        ),
                        "response_time_percentile_99": stat.get(
                            "response_time_percentile_99", 0
                        ),
                        "requests_per_second": stat.get("requests_per_second", 0),
                    }
                )

        print(f"✓ CSV data exported: {output_file}")
        return output_file

    def generate_all_reports(self):
        """Generate all report types."""
        self.generate_json_report()
        self.generate_html_report()
        self.generate_csv_export()

    def _check_passed(self) -> bool:
        """Check if tests passed acceptance criteria."""
        passed, _ = meets_acceptance_criteria(
            {
                "api_response_time_95th": self.summary["response_times"]["95th"],
                "page_load_time_95th": self.summary["response_times"]["95th"],
                "failure_rate": self.summary["failure_rate"],
                "requests_per_second": self.summary["requests_per_second"],
            }
        )
        return passed

    def _get_threshold_violations(self) -> List[Dict]:
        """Get list of threshold violations."""
        violations = []
        stats = self.stats.get("stats", [])

        for stat in stats:
            name = stat.get("name", "")
            if name == "Aggregated":
                continue

            response_time_95th = stat.get("response_time_percentile_95", 0)

            # Determine threshold
            threshold = 1000  # Default
            if "/api/" in name:
                threshold = 500
            elif name.startswith("/"):
                threshold = 2000

            if response_time_95th > threshold:
                violations.append(
                    {
                        "endpoint": name,
                        "response_time_95th": response_time_95th,
                        "threshold": threshold,
                        "exceeded_by": response_time_95th - threshold,
                    }
                )

        return violations

    def _generate_response_time_rows(self) -> str:
        """Generate HTML table rows for response times."""
        rows = []
        response_times = self.summary.get("response_times", {})

        for percentile in ["50th", "75th", "90th", "95th", "99th"]:
            value = response_times.get(percentile, 0)
            threshold = 2000 if percentile in ["95th", "99th"] else 1000
            passed = value <= threshold
            status = "✅" if passed else "❌"

            rows.append(
                f"""
                <tr>
                    <td>{percentile} percentile</td>
                    <td>{value:.0f} ms</td>
                    <td>{threshold} ms</td>
                    <td>{status}</td>
                </tr>
            """
            )

        return "".join(rows)

    def _generate_violations_section(self) -> str:
        """Generate HTML section for threshold violations."""
        violations = self._get_threshold_violations()

        if not violations:
            return ""

        violations_html = "<div class='violations'><h3>⚠️ Threshold Violations</h3><ul>"

        for v in violations:
            violations_html += f"""
                <li>{v['endpoint']}: {v['response_time_95th']:.0f}ms
                (threshold: {v['threshold']}ms, exceeded by {v['exceeded_by']:.0f}ms)</li>
            """

        violations_html += "</ul></div>"
        return violations_html


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate performance test reports")
    parser.add_argument(
        "--input", type=Path, required=True, help="Input Locust stats JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Output directory for reports",
    )

    args = parser.parse_args()

    generator = PerformanceReportGenerator(args.input, args.output_dir)
    generator.generate_all_reports()

    print("\n✅ All reports generated successfully")


if __name__ == "__main__":
    main()
