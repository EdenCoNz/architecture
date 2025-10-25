#!/usr/bin/env python3
"""
Test Report Generator

Aggregates test results from multiple sources (Playwright, pytest, Locust)
and generates comprehensive HTML, JSON, and PDF reports.

Story 13.15: Test Execution Reporting
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML


class TestReportGenerator:
    """
    Generates comprehensive test execution reports from multiple test types.

    Supports:
    - Aggregation of E2E (Playwright), integration (pytest), visual,
      and performance (Locust) test results
    - HTML report generation with charts and visualizations
    - JSON report for machine-readable output
    - PDF report generation for sharing
    - Historical trend analysis
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory where reports will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def aggregate_test_results(
        self,
        e2e_report: Optional[Path] = None,
        integration_report: Optional[Path] = None,
        visual_report: Optional[Path] = None,
        performance_report: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Aggregate test results from all test types.

        Args:
            e2e_report: Path to Playwright JSON report
            integration_report: Path to pytest JSON report
            visual_report: Path to visual regression JSON report
            performance_report: Path to Locust JSON report

        Returns:
            Aggregated test results dictionary
        """
        aggregated: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration_seconds": 0.0,
            },
            "test_suites": {},
            "failures": [],
            "metadata": {
                "git_commit": None,
                "git_branch": None,
                "ci_run_id": None,
            },
        }
        # Explicitly type the failures list to avoid Collection[str] inference
        failures_list: List[Dict[str, Any]] = []
        aggregated["failures"] = failures_list

        # Process E2E test results (Playwright)
        if e2e_report and e2e_report.exists():
            e2e_data = self._process_playwright_report(e2e_report)
            aggregated["test_suites"]["e2e"] = e2e_data
            self._update_summary(aggregated["summary"], e2e_data)
            aggregated["failures"].extend(e2e_data.get("failures", []))

        # Process integration test results (pytest)
        if integration_report and integration_report.exists():
            integration_data = self._process_pytest_report(integration_report)
            aggregated["test_suites"]["integration"] = integration_data
            self._update_summary(aggregated["summary"], integration_data)
            aggregated["failures"].extend(integration_data.get("failures", []))

        # Process visual regression test results
        if visual_report and visual_report.exists():
            visual_data = self._process_visual_report(visual_report)
            aggregated["test_suites"]["visual"] = visual_data
            self._update_summary(aggregated["summary"], visual_data)
            aggregated["failures"].extend(visual_data.get("failures", []))

        # Process performance test results (Locust)
        if performance_report and performance_report.exists():
            performance_data = self._process_locust_report(performance_report)
            aggregated["test_suites"]["performance"] = performance_data

        # Calculate pass rate
        total = aggregated["summary"]["total_tests"]
        passed = aggregated["summary"]["passed"]
        aggregated["summary"]["pass_rate"] = (
            (passed / total * 100) if total > 0 else 0.0
        )

        return aggregated

    def _process_playwright_report(self, report_path: Path) -> Dict[str, Any]:
        """Process Playwright JSON report."""
        with open(report_path, "r") as f:
            data = json.load(f)

        total = 0
        passed = 0
        failed = 0
        skipped = 0
        duration = 0.0
        failures = []

        for suite in data.get("suites", []):
            for spec in suite.get("specs", []):
                for test in spec.get("tests", []):
                    total += 1
                    status = test.get("status", "unknown")

                    if status == "passed":
                        passed += 1
                    elif status == "failed":
                        failed += 1
                        # Extract failure information
                        for result in test.get("results", []):
                            if result.get("status") == "failed":
                                error = result.get("error", {})
                                failures.append(
                                    {
                                        "test_name": test.get("title", "Unknown"),
                                        "file": spec.get("file", "Unknown"),
                                        "line": spec.get("line"),
                                        "error_message": error.get(
                                            "message", "No error message"
                                        ),
                                        "stack_trace": error.get("stack", ""),
                                        "screenshot": (
                                            result.get("attachments", [{}])[0].get(
                                                "path"
                                            )
                                            if result.get("attachments")
                                            else None
                                        ),
                                        "suite": "e2e",
                                    }
                                )
                    elif status == "skipped":
                        skipped += 1

                    # Sum up duration
                    for result in test.get("results", []):
                        duration += (
                            result.get("duration", 0) / 1000.0
                        )  # Convert to seconds

        return {
            "name": "End-to-End Tests (Playwright)",
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration_seconds": duration,
            "pass_rate": (passed / total * 100) if total > 0 else 0.0,
            "failures": failures,
        }

    def _process_pytest_report(self, report_path: Path) -> Dict[str, Any]:
        """Process pytest JSON report."""
        with open(report_path, "r") as f:
            data = json.load(f)

        summary = data.get("summary", {})
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        duration = data.get("duration", 0.0)

        failures = []
        for test in data.get("tests", []):
            if test.get("outcome") == "failed":
                failures.append(
                    {
                        "test_name": test.get("nodeid", "Unknown"),
                        "file": test.get("location", ["Unknown"])[0],
                        "line": test.get("location", [None, None])[1],
                        "error_message": test.get("call", {}).get(
                            "longrepr", "No error message"
                        ),
                        "stack_trace": test.get("call", {}).get("traceback", ""),
                        "screenshot": None,
                        "suite": "integration",
                    }
                )

        return {
            "name": "Integration Tests (pytest)",
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration_seconds": duration,
            "pass_rate": (passed / total * 100) if total > 0 else 0.0,
            "failures": failures,
        }

    def _process_visual_report(self, report_path: Path) -> Dict[str, Any]:
        """Process visual regression test report."""
        with open(report_path, "r") as f:
            data = json.load(f)

        total = data.get("total", 0)
        passed = data.get("passed", 0)
        failed = data.get("failed", 0)

        failures = []
        for test in data.get("failures", []):
            failures.append(
                {
                    "test_name": test.get("name", "Unknown"),
                    "file": test.get("file", "Unknown"),
                    "line": None,
                    "error_message": (
                        f"Visual diff detected: "
                        f"{test.get('diff_percentage', 0)}% difference"
                    ),
                    "stack_trace": "",
                    "screenshot": test.get("diff_image", None),
                    "suite": "visual",
                }
            )

        return {
            "name": "Visual Regression Tests",
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": 0,
            "duration_seconds": data.get("duration", 0.0),
            "pass_rate": (passed / total * 100) if total > 0 else 0.0,
            "failures": failures,
        }

    def _process_locust_report(self, report_path: Path) -> Dict[str, Any]:
        """Process Locust performance test report."""
        with open(report_path, "r") as f:
            data = json.load(f)

        return {
            "name": "Performance Tests (Locust)",
            "total_requests": data.get("summary", {}).get("total_requests", 0),
            "failure_rate": data.get("summary", {}).get("failure_rate_percent", 0.0),
            "requests_per_second": data.get("summary", {}).get(
                "requests_per_second", 0.0
            ),
            "response_time_50th": data.get("response_times_ms", {}).get("50th", 0),
            "response_time_95th": data.get("response_times_ms", {}).get("95th", 0),
            "response_time_99th": data.get("response_times_ms", {}).get("99th", 0),
            "passed": data.get("result", {}).get("passed", False),
        }

    def _update_summary(
        self, summary: Dict[str, Any], suite_data: Dict[str, Any]
    ) -> None:
        """Update overall summary with suite data."""
        summary["total_tests"] += suite_data.get("total", 0)
        summary["passed"] += suite_data.get("passed", 0)
        summary["failed"] += suite_data.get("failed", 0)
        summary["skipped"] += suite_data.get("skipped", 0)
        summary["duration_seconds"] += suite_data.get("duration_seconds", 0.0)

    def generate_html_report(
        self, aggregated_data: Dict[str, Any], output_file: Path
    ) -> None:
        """
        Generate HTML report with charts and visualizations.

        Args:
            aggregated_data: Aggregated test results
            output_file: Path to output HTML file
        """
        template = self.jinja_env.get_template("test_report.html")

        html_content = template.render(
            data=aggregated_data,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        )

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(html_content)

        print(f"✅ HTML report generated: {output_file}")

    def generate_json_report(
        self, aggregated_data: Dict[str, Any], output_file: Path
    ) -> None:
        """
        Generate JSON report for machine-readable output.

        Args:
            aggregated_data: Aggregated test results
            output_file: Path to output JSON file
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(aggregated_data, f, indent=2)

        print(f"✅ JSON report generated: {output_file}")

    def generate_pdf_report(self, html_report: Path, output_file: Path) -> None:
        """
        Generate PDF report from HTML report.

        Args:
            html_report: Path to HTML report
            output_file: Path to output PDF file
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        HTML(filename=str(html_report)).write_pdf(str(output_file))

        print(f"✅ PDF report generated: {output_file}")

    def generate_all_reports(
        self,
        e2e_report: Optional[Path] = None,
        integration_report: Optional[Path] = None,
        visual_report: Optional[Path] = None,
        performance_report: Optional[Path] = None,
    ) -> None:
        """
        Generate all report formats (HTML, JSON, PDF).

        Args:
            e2e_report: Path to Playwright JSON report
            integration_report: Path to pytest JSON report
            visual_report: Path to visual regression JSON report
            performance_report: Path to Locust JSON report
        """
        print("📊 Aggregating test results...")
        aggregated_data = self.aggregate_test_results(
            e2e_report=e2e_report,
            integration_report=integration_report,
            visual_report=visual_report,
            performance_report=performance_report,
        )

        print("\n📈 Test Summary:")
        print(f"  Total Tests: {aggregated_data['summary']['total_tests']}")
        print(f"  Passed: {aggregated_data['summary']['passed']}")
        print(f"  Failed: {aggregated_data['summary']['failed']}")
        print(f"  Skipped: {aggregated_data['summary']['skipped']}")
        print(f"  Pass Rate: {aggregated_data['summary']['pass_rate']:.1f}%")
        print(f"  Duration: {aggregated_data['summary']['duration_seconds']:.2f}s")

        print("\n📄 Generating reports...")

        # Generate HTML report
        html_file = self.output_dir / "test-report.html"
        self.generate_html_report(aggregated_data, html_file)

        # Generate JSON report
        json_file = self.output_dir / "test-report.json"
        self.generate_json_report(aggregated_data, json_file)

        # Generate PDF report
        pdf_file = self.output_dir / "test-report.pdf"
        try:
            self.generate_pdf_report(html_file, pdf_file)
        except Exception as e:
            print(f"⚠️  PDF generation failed: {e}")
            print("   (This is optional - HTML and JSON reports are still available)")

        print("\n✅ All reports generated successfully!")


def main():
    """CLI entry point for report generator."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test execution reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate reports from all test types
  python report_generator.py --output-dir reports/ \\
    --e2e-report e2e/test-results.json \\
    --integration-report integration/test-results.json \\
    --visual-report visual/test-results.json \\
    --performance-report performance/test-results.json

  # Generate reports from E2E tests only
  python report_generator.py --output-dir reports/ \\
    --e2e-report e2e/test-results.json
        """,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where reports will be saved",
    )
    parser.add_argument(
        "--e2e-report", type=Path, help="Path to Playwright E2E test JSON report"
    )
    parser.add_argument(
        "--integration-report",
        type=Path,
        help="Path to pytest integration test JSON report",
    )
    parser.add_argument(
        "--visual-report", type=Path, help="Path to visual regression test JSON report"
    )
    parser.add_argument(
        "--performance-report",
        type=Path,
        help="Path to Locust performance test JSON report",
    )

    args = parser.parse_args()

    # Validate that at least one report is provided
    if not any(
        [
            args.e2e_report,
            args.integration_report,
            args.visual_report,
            args.performance_report,
        ]
    ):
        parser.error("At least one test report must be provided")

    # Generate reports
    generator = TestReportGenerator(args.output_dir)
    generator.generate_all_reports(
        e2e_report=args.e2e_report,
        integration_report=args.integration_report,
        visual_report=args.visual_report,
        performance_report=args.performance_report,
    )


if __name__ == "__main__":
    main()
