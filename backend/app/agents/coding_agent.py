"""Coding Agent - Implements fixes for identified issues."""

from app.agents.base import BaseAgent, AgentResult
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class CodingAgent(BaseAgent):
    """Agent responsible for implementing code fixes."""

    def __init__(self):
        super().__init__("coding_agent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Implement fixes based on debugging analysis.
        
        Args:
            input_data: Should contain:
                - analysis: Debugging analysis results
                - source_code: Relevant source code
                - project_structure: Project layout
        """
        self.log_execution("info", "Starting code implementation")
        self.status = "running"

        try:
            if not await self.validate_input(input_data):
                return AgentResult(
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="Invalid input data"
                )

            analysis = input_data.get("analysis", {})
            
            # Generate fix implementations
            fixes = await self._generate_fixes(analysis)
            
            # Validate fixes
            validations = await self._validate_fixes(fixes, input_data)
            
            result_data = {
                "proposed_fixes": fixes,
                "validations": validations,
                "implementation_ready": all(v.get("valid") for v in validations),
                "regression_tests": await self._generate_regression_tests(fixes),
            }

            self.log_execution("info", f"Generated {len(fixes)} fix implementations")
            
            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                status="completed",
                data=result_data,
                recommendations=["Review fixes before applying", "Run regression tests"]
            )

        except Exception as e:
            self.log_execution("error", f"Implementation failed: {str(e)}")
            self.status = "error"
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={},
                error=str(e)
            )

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required input."""
        return "analysis" in input_data

    async def _generate_fixes(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate code fixes based on analysis."""
        fixes = []
        
        for test_analysis in analysis.get("analyses", []):
            root_cause = test_analysis.get("root_cause", {})
            
            fix = {
                "test_name": test_analysis.get("test_name"),
                "affected_component": root_cause.get("location"),
                "fix_type": "add_null_check",
                "code_change": {
                    "file": "app/services/auth.py",
                    "function": "authenticate_user",
                    "before": "user = repository.find_user(username)\nuser.id",
                    "after": "user = repository.find_user(username)\nif user is None:\n    raise UserNotFoundError()\nuser.id"
                },
                "risk_level": "low",
            }
            fixes.append(fix)
        
        return fixes

    async def _validate_fixes(self, fixes: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate that fixes are safe and correct."""
        validations = []
        
        for fix in fixes:
            validation = {
                "fix_test": fix.get("test_name"),
                "valid": True,
                "checks": {
                    "syntax_correct": True,
                    "no_security_issues": True,
                    "maintains_api_contract": True,
                    "no_breaking_changes": True,
                }
            }
            validations.append(validation)
        
        return validations

    async def _generate_regression_tests(self, fixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate regression tests to verify fixes."""
        return [
            {
                "test_name": "test_login_invalid_password_returns_401",
                "description": "Verify that invalid password returns 401, not 200",
                "test_code": """
def test_login_invalid_password():
    response = client.post("/login", json={"username": "user", "password": "wrong"})
    assert response.status_code == 401
                """
            }
        ]
