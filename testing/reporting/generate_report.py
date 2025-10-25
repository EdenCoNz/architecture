#!/usr/bin/env python3
"""
Test Report Generation CLI

Command-line tool for generating comprehensive test execution reports.

Usage:
    python generate_report.py --output-dir reports/ --e2e-report e2e/test-results.json

Story 13.15: Test Execution Reporting
"""

import argparse
import os
import sys
from pathlib import Path

from .flaky_detector import FlakyTestDetector
from .report_generator import TestReportGenerator
from .trend_analyzer import TrendAnalyzer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test execution reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate complete test report from all test types
  python generate_report.py --output-dir reports/ \\
    --e2e-report e2e/test-results.json \\
    --integration-report integration/test-results.json \\
    --visual-report visual/test-results.json \\
    --performance-report performance/test-results.json

  # Generate report with historical trends
  python generate_report.py --output-dir reports/ \\
    --e2e-report e2e/test-results.json \\
    --with-trends --trends-days 30

  # Generate flaky test report
  python generate_report.py --output-dir reports/ \\
    --detect-flaky --flaky-min-runs 5
        """,
    )

    # Input report paths
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

    # Output configuration
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Directory where reports will be saved (default: reports/)",
    )
    parser.add_argument(
        "--no-pdf", action="store_true", help="Skip PDF report generation"
    )

    # Historical trends
    parser.add_argument(
        "--with-trends", action="store_true", help="Include historical trend analysis"
    )
    parser.add_argument(
        "--trends-db",
        type=Path,
        default=Path("reports/trends.db"),
        help="Path to trends database (default: reports/trends.db)",
    )
    parser.add_argument(
        "--trends-days",
        type=int,
        default=30,
        help="Number of days to analyze for trends (default: 30)",
    )

    # Flaky test detection
    parser.add_argument(
        "--detect-flaky",
        action="store_true",
        help="Generate flaky test detection report",
    )
    parser.add_argument(
        "--flaky-min-runs",
        type=int,
        default=5,
        help="Minimum number of runs to consider for flaky detection (default: 5)",
    )

    # Metadata
    parser.add_argument("--git-commit", type=str, help="Git commit SHA")
    parser.add_argument("--git-branch", type=str, help="Git branch name")
    parser.add_argument("--ci-run-id", type=str, help="CI run ID")

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
        if not args.detect_flaky:
            parser.error(
                "At least one test report must be provided (or use --detect-flaky)"
            )

    print("=" * 80)
    print("Test Execution Report Generator")
    print("=" * 80)
    print()

    # Step 1: Generate main test report
    if any(
        [
            args.e2e_report,
            args.integration_report,
            args.visual_report,
            args.performance_report,
        ]
    ):
        print("Step 1: Generating test execution report...")
        print("-" * 80)

        generator = TestReportGenerator(args.output_dir)

        # Aggregate test results
        aggregated_data = generator.aggregate_test_results(
            e2e_report=args.e2e_report,
            integration_report=args.integration_report,
            visual_report=args.visual_report,
            performance_report=args.performance_report,
        )

        # Add metadata
        aggregated_data["metadata"]["git_commit"] = args.git_commit or os.getenv(
            "GITHUB_SHA"
        )
        aggregated_data["metadata"]["git_branch"] = args.git_branch or os.getenv(
            "GITHUB_REF_NAME"
        )
        aggregated_data["metadata"]["ci_run_id"] = args.ci_run_id or os.getenv(
            "GITHUB_RUN_ID"
        )

        # Generate HTML report
        html_file = args.output_dir / "test-report.html"
        generator.generate_html_report(aggregated_data, html_file)

        # Generate JSON report
        json_file = args.output_dir / "test-report.json"
        generator.generate_json_report(aggregated_data, json_file)

        # Generate PDF report (unless disabled)
        if not args.no_pdf:
            pdf_file = args.output_dir / "test-report.pdf"
            try:
                generator.generate_pdf_report(html_file, pdf_file)
            except Exception as e:
                print(f"⚠️  PDF generation failed: {e}")
                print("   HTML and JSON reports are still available")

        print()
        print("Summary:")
        print(f"  Total Tests: {aggregated_data['summary']['total_tests']}")
        print(f"  Passed: {aggregated_data['summary']['passed']}")
        print(f"  Failed: {aggregated_data['summary']['failed']}")
        print(f"  Skipped: {aggregated_data['summary']['skipped']}")
        print(f"  Pass Rate: {aggregated_data['summary']['pass_rate']:.1f}%")
        print(f"  Duration: {aggregated_data['summary']['duration_seconds']:.2f}s")
        print()

        # Step 2: Store results for trend analysis (if enabled)
        if args.with_trends:
            print("Step 2: Storing results for trend analysis...")
            print("-" * 80)

            trend_analyzer = TrendAnalyzer(args.trends_db)
            run_id = trend_analyzer.store_test_run(aggregated_data)

            # Export trends
            trends_file = args.output_dir / "test-trends.json"
            trend_analyzer.export_trends_to_json(trends_file, days=args.trends_days)

            print()

    # Step 3: Detect flaky tests (if enabled)
    if args.detect_flaky:
        print("Step 3: Detecting flaky tests...")
        print("-" * 80)

        trend_analyzer = TrendAnalyzer(args.trends_db)
        flaky_detector = FlakyTestDetector(trend_analyzer)

        flaky_report_file = args.output_dir / "flaky-tests-report.json"
        flaky_detector.generate_flaky_test_report(
            flaky_report_file, days=args.trends_days, min_runs=args.flaky_min_runs
        )

        print()

    print("=" * 80)
    print("Report generation complete!")
    print("=" * 80)
    print()
    print(f"Reports saved to: {args.output_dir.absolute()}")
    print()

    # Exit with non-zero code if tests failed
    if any(
        [
            args.e2e_report,
            args.integration_report,
            args.visual_report,
            args.performance_report,
        ]
    ):
        if aggregated_data["summary"]["failed"] > 0:
            print("⚠️  WARNING: Some tests failed")
            sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
