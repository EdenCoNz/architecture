#!/usr/bin/env python3
"""
Trend Analyzer

Analyzes historical test execution data to identify trends such as:
- Pass rate over time
- Flaky tests (tests that intermittently fail)
- Performance trends (response times, throughput)
- Test duration trends

Story 13.15: Test Execution Reporting
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TrendAnalyzer:
    """
    Analyzes historical test execution data to identify trends.

    Stores test results in SQLite database for efficient querying and trend analysis.
    """

    def __init__(self, database_path: Path):
        """
        Initialize the trend analyzer.

        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the SQLite database schema."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Test runs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                git_commit TEXT,
                git_branch TEXT,
                ci_run_id TEXT,
                total_tests INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                skipped INTEGER NOT NULL,
                duration_seconds REAL NOT NULL,
                pass_rate REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """
        )

        # Individual test results table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                test_name TEXT NOT NULL,
                suite TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_seconds REAL,
                error_message TEXT,
                file TEXT,
                line INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES test_runs(id)
            )
        """
        )

        # Performance metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                total_requests INTEGER,
                failure_rate REAL,
                requests_per_second REAL,
                response_time_50th REAL,
                response_time_95th REAL,
                response_time_99th REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES test_runs(id)
            )
        """
        )

        # Create indexes for efficient querying
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_runs_timestamp
            ON test_runs(timestamp)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_run_id
            ON test_results(run_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_test_name
            ON test_results(test_name)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_status
            ON test_results(status)
        """
        )

        conn.commit()
        conn.close()

    def store_test_run(self, aggregated_data: Dict[str, Any]) -> int:
        """
        Store test run results in database.

        Args:
            aggregated_data: Aggregated test results from report generator

        Returns:
            run_id: ID of the stored test run
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Store test run summary
        summary = aggregated_data["summary"]
        metadata = aggregated_data["metadata"]

        cursor.execute(
            """
            INSERT INTO test_runs (
                timestamp, git_commit, git_branch, ci_run_id,
                total_tests, passed, failed, skipped,
                duration_seconds, pass_rate, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                aggregated_data["timestamp"],
                metadata.get("git_commit"),
                metadata.get("git_branch"),
                metadata.get("ci_run_id"),
                summary["total_tests"],
                summary["passed"],
                summary["failed"],
                summary["skipped"],
                summary["duration_seconds"],
                summary["pass_rate"],
                datetime.utcnow().isoformat(),
            ),
        )

        run_id = cursor.lastrowid
        if run_id is None:
            raise RuntimeError("Failed to get lastrowid after inserting test run")

        # Store individual test results
        for suite_name, suite_data in aggregated_data.get("test_suites", {}).items():
            if suite_name == "performance":
                # Store performance metrics separately
                cursor.execute(
                    """
                    INSERT INTO performance_metrics (
                        run_id, total_requests, failure_rate,
                        requests_per_second, response_time_50th,
                        response_time_95th, response_time_99th, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        run_id,
                        suite_data.get("total_requests", 0),
                        suite_data.get("failure_rate", 0.0),
                        suite_data.get("requests_per_second", 0.0),
                        suite_data.get("response_time_50th", 0),
                        suite_data.get("response_time_95th", 0),
                        suite_data.get("response_time_99th", 0),
                        datetime.utcnow().isoformat(),
                    ),
                )
            else:
                # Store test results
                for failure in suite_data.get("failures", []):
                    cursor.execute(
                        """
                        INSERT INTO test_results (
                            run_id, test_name, suite, status,
                            duration_seconds, error_message, file, line, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            run_id,
                            failure["test_name"],
                            suite_name,
                            "failed",
                            None,  # Duration not tracked per test in failures
                            failure.get("error_message"),
                            failure.get("file"),
                            failure.get("line"),
                            datetime.utcnow().isoformat(),
                        ),
                    )

        conn.commit()
        conn.close()

        print(f"✅ Test run stored in database (run_id: {run_id})")
        return run_id

    def get_pass_rate_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get pass rate trend over time.

        Args:
            days: Number of days to look back

        Returns:
            List of {timestamp, pass_rate, total_tests} dictionaries
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        cursor.execute(
            """
            SELECT timestamp, pass_rate, total_tests, passed, failed
            FROM test_runs
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """,
            (cutoff_date,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "timestamp": row[0],
                "pass_rate": row[1],
                "total_tests": row[2],
                "passed": row[3],
                "failed": row[4],
            }
            for row in rows
        ]

    def get_flaky_tests(
        self, days: int = 30, min_runs: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identify flaky tests (tests that pass sometimes and fail sometimes).

        Args:
            days: Number of days to look back
            min_runs: Minimum number of runs required to consider a test flaky

        Returns:
            List of flaky test information dictionaries
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Find tests that have both passed and failed in the time period
        cursor.execute(
            """
            SELECT
                tr.test_name,
                tr.suite,
                COUNT(*) as total_runs,
                SUM(CASE WHEN tr.status = 'failed' THEN 1 ELSE 0 END) as failures,
                SUM(CASE WHEN tr.status = 'passed' THEN 1 ELSE 0 END) as passes,
                tr.file
            FROM test_results tr
            JOIN test_runs truns ON tr.run_id = truns.id
            WHERE truns.timestamp >= ?
            GROUP BY tr.test_name, tr.suite
            HAVING total_runs >= ?
                AND failures > 0
                AND passes > 0
            ORDER BY failures DESC, total_runs DESC
        """,
            (cutoff_date, min_runs),
        )

        rows = cursor.fetchall()
        conn.close()

        flaky_tests = []
        for row in rows:
            test_name, suite, total_runs, failures, passes, file = row
            flaky_tests.append(
                {
                    "test_name": test_name,
                    "suite": suite,
                    "total_runs": total_runs,
                    "failures": failures,
                    "passes": passes,
                    "failure_rate": (failures / total_runs * 100),
                    "file": file,
                }
            )

        return flaky_tests

    def get_performance_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get performance trends over time.

        Args:
            days: Number of days to look back

        Returns:
            List of performance metric dictionaries
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        cursor.execute(
            """
            SELECT
                truns.timestamp,
                pm.total_requests,
                pm.failure_rate,
                pm.requests_per_second,
                pm.response_time_50th,
                pm.response_time_95th,
                pm.response_time_99th
            FROM performance_metrics pm
            JOIN test_runs truns ON pm.run_id = truns.id
            WHERE truns.timestamp >= ?
            ORDER BY truns.timestamp ASC
        """,
            (cutoff_date,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "timestamp": row[0],
                "total_requests": row[1],
                "failure_rate": row[2],
                "requests_per_second": row[3],
                "response_time_50th": row[4],
                "response_time_95th": row[5],
                "response_time_99th": row[6],
            }
            for row in rows
        ]

    def get_duration_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get test execution duration trends over time.

        Args:
            days: Number of days to look back

        Returns:
            List of {timestamp, duration_seconds} dictionaries
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        cursor.execute(
            """
            SELECT timestamp, duration_seconds
            FROM test_runs
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """,
            (cutoff_date,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "timestamp": row[0],
                "duration_seconds": row[1],
            }
            for row in rows
        ]

    def get_trends_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive trends summary.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with all trend data
        """
        return {
            "period_days": days,
            "pass_rate_trend": self.get_pass_rate_trend(days),
            "flaky_tests": self.get_flaky_tests(days),
            "performance_trends": self.get_performance_trends(days),
            "duration_trends": self.get_duration_trends(days),
        }

    def export_trends_to_json(self, output_file: Path, days: int = 30) -> None:
        """
        Export trends summary to JSON file.

        Args:
            output_file: Path to output JSON file
            days: Number of days to look back
        """
        trends = self.get_trends_summary(days)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(trends, f, indent=2)

        print(f"✅ Trends exported to: {output_file}")
