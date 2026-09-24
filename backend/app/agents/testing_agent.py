"""Testing Agent - Executes tests and captures failures."""

from app.agents.base import BaseAgent, AgentResult
from typing import Any, Dict, Optional
from datetime import datetime
import subprocess
import json
import logging

logger = logging.getLogger(__name__)


class TestingAgent(BaseAgent):
    """Agent responsible for executing test suites and capturing failures."""

    def __init__(self):
        super().__init__("testing_agent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute tests and collect results.
        
        Args:
            input_data: Should contain:
                - project_path: Path to the project
                - test_framework: pytest, unittest, jest, etc.
                - test_paths: Specific test files to run
                
        Returns:
            AgentResult with test results and failures
        """
        self.log_execution("info", "Starting test execution")
        self.status = "running"

        try:
            # Validate input
            if not await self.validate_input(input_data):
                return AgentResult(
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="Invalid input data"
                )

            project_path = input_data.get("project_path")
            test_framework = input_data.get("test_framework", "pytest")
            test_paths = input_data.get("test_paths", [])

            # Run tests
            test_results = await self._run_tests(
                project_path,
                test_framework,
                test_paths
            )

            # Analyze results for failures
            failures = await self._analyze_results(test_results)

            result_data = {
                "test_results": test_results,
                "failures": failures,
                "test_count": test_results.get("total_tests", 0),
                "passed_count": test_results.get("passed", 0),
                "failed_count": test_results.get("failed", 0),
                "skipped_count": test_results.get("skipped", 0),
                "execution_time": test_results.get("execution_time", 0),
            }

            self.log_execution(
                "info",
                f"Tests completed: {result_data['passed_count']}/{result_data['test_count']} passed"
            )

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                status="completed",
                data=result_data,
                recommendations=self._generate_recommendations(failures)
            )

        except Exception as e:
            self.log_execution("error", f"Test execution failed: {str(e)}")
            self.status = "error"
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={},
                error=str(e)
            )

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that required fields are present."""
        required_fields = ["project_path"]
        return all(field in input_data for field in required_fields)

    async def _run_tests(
        self,
        project_path: str,
        test_framework: str,
        test_paths: list
    ) -> Dict[str, Any]:
        """
        Execute test suite using specified framework.
        
        In production, this would actually run pytest or similar.
        For now, we provide a stub implementation.
        """
        self.log_execution("info", f"Running {test_framework} tests")

        # Stub implementation - in production would call subprocess
        # For demo purposes, return sample data
        return {
            "framework": test_framework,
            "total_tests": 15,
            "passed": 12,
            "failed": 2,
            "skipped": 1,
            "execution_time": 3.45,
            "test_details": [
                {
                    "name": "test_login_valid_credentials",
                    "status": "passed",
                    "duration": 0.23,
                },
                {
                    "name": "test_login_invalid_password",
                    "status": "failed",
                    "duration": 0.15,
                    "error": "AssertionError: Expected 401, got 200",
                    "traceback": "File test_auth.py, line 42, in test_login_invalid_password\n  assert response.status_code == 401"
                },
                {
                    "name": "test_refresh_token",
                    "status": "failed",
                    "duration": 0.18,
                    "error": "AttributeError: 'NoneType' object has no attribute 'id'",
                    "traceback": "File test_auth.py, line 78, in test_refresh_token\n  user_id = auth_result.id"
                },
            ]
        }

    async def _analyze_results(self, test_results: Dict[str, Any]) -> list:
        """Extract and analyze failures from test results."""
        failures = []

        for test_detail in test_results.get("test_details", []):
            if test_detail.get("status") == "failed":
                failures.append({
                    "test_name": test_detail.get("name"),
                    "error": test_detail.get("error"),
                    "traceback": test_detail.get("traceback"),
                    "timestamp": datetime.utcnow().isoformat()
                })

        return failures

    def _generate_recommendations(self, failures: list) -> list:
        """Generate recommendations based on test failures."""
        if not failures:
            return ["All tests passed! No issues detected."]

        recommendations = [
            f"Investigate {len(failures)} failing tests",
            "Review error messages and stack traces",
            "Check if failures are related or independent",
            "Verify test assumptions and mock data",
        ]

        return recommendations
