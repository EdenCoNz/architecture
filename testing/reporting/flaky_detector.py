#!/usr/bin/env python3
"""
Flaky Test Detector

Advanced flaky test detection with statistical analysis and recommendations.

Story 13.15: Test Execution Reporting
"""

import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

from .trend_analyzer import TrendAnalyzer


class FlakyTestDetector:
    """
    Detects and analyzes flaky tests with statistical rigor.

    Uses multiple metrics to identify flaky tests:
    - Inconsistent pass/fail patterns
    - High variance in execution time
    - Error message patterns
    - Environmental dependencies
    """

    def __init__(self, trend_analyzer: TrendAnalyzer):
        """
        Initialize flaky test detector.

        Args:
            trend_analyzer: TrendAnalyzer instance for accessing historical data
        """
        self.trend_analyzer = trend_analyzer

    def detect_flaky_tests(
        self, days: int = 30, min_runs: int = 5, flakiness_threshold: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Detect flaky tests with detailed analysis.

        Args:
            days: Number of days to look back
            min_runs: Minimum number of runs required
            flakiness_threshold: Minimum failure rate % to consider flaky (default 10%)

        Returns:
            List of flaky test analysis dictionaries
        """
        flaky_tests = self.trend_analyzer.get_flaky_tests(days=days, min_runs=min_runs)

        # Enrich with additional analysis
        enriched_flaky_tests = []
        for test in flaky_tests:
            if test["failure_rate"] >= flakiness_threshold:
                severity = self._calculate_severity(test)
                recommendations = self._generate_recommendations(test, severity)

                enriched_flaky_tests.append(
                    {
                        **test,
                        "severity": severity,
                        "recommendations": recommendations,
                        "impact_score": self._calculate_impact_score(test),
                    }
                )

        # Sort by impact score (highest first)
        enriched_flaky_tests.sort(key=lambda x: x["impact_score"], reverse=True)

        return enriched_flaky_tests

    def _calculate_severity(self, test: Dict[str, Any]) -> str:
        """
        Calculate severity level based on failure rate and frequency.

        Args:
            test: Test information dictionary

        Returns:
            Severity level: 'critical', 'high', 'medium', or 'low'
        """
        failure_rate = test["failure_rate"]
        total_runs = test["total_runs"]

        if failure_rate >= 50 and total_runs >= 10:
            return "critical"
        elif failure_rate >= 30 or total_runs >= 20:
            return "high"
        elif failure_rate >= 20:
            return "medium"
        else:
            return "low"

    def _calculate_impact_score(self, test: Dict[str, Any]) -> float:
        """
        Calculate impact score for prioritization.

        Score considers:
        - Failure rate (weight: 40%)
        - Total runs (weight: 30%)
        - Absolute failures (weight: 30%)

        Args:
            test: Test information dictionary

        Returns:
            Impact score (0-100)
        """
        failure_rate = test["failure_rate"]
        total_runs = min(test["total_runs"], 100)  # Cap at 100 for scoring
        failures = test["failures"]

        # Normalize and weight
        score = (
            (failure_rate / 100.0) * 40
            + (total_runs / 100.0) * 30  # 40% weight on failure rate
            + (min(failures, 50) / 50.0)  # 30% weight on frequency
            * 30  # 30% weight on absolute failures
        )

        return round(score, 2)

    def _generate_recommendations(
        self, test: Dict[str, Any], severity: str
    ) -> List[str]:
        """
        Generate actionable recommendations for fixing flaky test.

        Args:
            test: Test information dictionary
            severity: Severity level

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Priority recommendation based on severity
        if severity == "critical":
            recommendations.append(
                "⚠️ CRITICAL: This test is highly flaky and should be disabled or fixed immediately"
            )
        elif severity == "high":
            recommendations.append(
                "⚠️ HIGH PRIORITY: This test requires urgent attention to improve reliability"
            )

        # Generic recommendations
        recommendations.extend(
            [
                "Review test for race conditions and timing issues",
                "Check for dependencies on external services or test data",
                "Add explicit waits for async operations",
                "Verify test isolation - ensure test doesn't depend on other tests",
                "Consider adding retry logic or more robust assertions",
            ]
        )

        # Suite-specific recommendations
        suite = test.get("suite", "")
        if suite == "e2e":
            recommendations.extend(
                [
                    "E2E: Increase timeout values for page loads and element waits",
                    "E2E: Use Playwright's auto-waiting features instead of fixed delays",
                    "E2E: Check for dynamic content that may not be fully loaded",
                ]
            )
        elif suite == "integration":
            recommendations.extend(
                [
                    "Integration: Verify database state is properly reset between tests",
                    "Integration: Check for shared resources or fixtures causing conflicts",
                ]
            )
        elif suite == "visual":
            recommendations.extend(
                [
                    "Visual: Review baseline images for inconsistencies",
                    "Visual: Increase diff tolerance for minor rendering variations",
                ]
            )

        return recommendations

    def generate_flaky_test_report(
        self, output_file: Path, days: int = 30, min_runs: int = 5
    ) -> None:
        """
        Generate comprehensive flaky test report.

        Args:
            output_file: Path to output JSON file
            days: Number of days to look back
            min_runs: Minimum number of runs required
        """
        flaky_tests = self.detect_flaky_tests(days=days, min_runs=min_runs)

        report: Dict[str, Any] = {
            "generated_at": str(Path(__file__).parent),
            "analysis_period_days": days,
            "min_runs_threshold": min_runs,
            "total_flaky_tests": len(flaky_tests),
            "flaky_tests_by_severity": {
                "critical": len(
                    [t for t in flaky_tests if t["severity"] == "critical"]
                ),
                "high": len([t for t in flaky_tests if t["severity"] == "high"]),
                "medium": len([t for t in flaky_tests if t["severity"] == "medium"]),
                "low": len([t for t in flaky_tests if t["severity"] == "low"]),
            },
            "flaky_tests": flaky_tests,
        }

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Flaky test report generated: {output_file}")
        print(f"   Total flaky tests: {len(flaky_tests)}")
        print(f"   - Critical: {report['flaky_tests_by_severity']['critical']}")
        print(f"   - High: {report['flaky_tests_by_severity']['high']}")
        print(f"   - Medium: {report['flaky_tests_by_severity']['medium']}")
        print(f"   - Low: {report['flaky_tests_by_severity']['low']}")
