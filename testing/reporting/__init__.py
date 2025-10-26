"""
Test Execution Reporting

Comprehensive test reporting system that aggregates results from all test types
(E2E, integration, visual, performance) and generates HTML, JSON, and PDF reports
with historical trends and flaky test detection.

Story 13.15: Test Execution Reporting
"""

from .flaky_detector import FlakyTestDetector
from .report_generator import TestReportGenerator
from .trend_analyzer import TrendAnalyzer

__all__ = [
    "TestReportGenerator",
    "TrendAnalyzer",
    "FlakyTestDetector",
]
