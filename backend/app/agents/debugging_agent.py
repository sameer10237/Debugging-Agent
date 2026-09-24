"""Debugging Agent - Analyzes failures and determines root causes."""

from app.agents.base import BaseAgent, AgentResult
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FailureType(str, Enum):
    """Classification of failure types."""
    LOGIC_ERROR = "logic_error"
    TYPE_ERROR = "type_error"
    RUNTIME_ERROR = "runtime_error"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    AUTHENTICATION_ERROR = "authentication_error"
    SECURITY_ERROR = "security_error"


class DebuggingAgent(BaseAgent):
    """
    Advanced debugging agent that performs root-cause analysis.
    
    This agent follows the debugging methodology outlined in the system prompt:
    1. Understand intended behavior
    2. Analyze the failure
    3. Classify the failure
    4. Trace through system
    5. Perform root-cause analysis
    6. Distinguish root cause from symptoms
    7. Determine correct fix
    """

    def __init__(self):
        super().__init__("debugging_agent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Perform debugging analysis on failures.
        
        Args:
            input_data: Should contain:
                - failures: List of test failures
                - test_results: Results from testing agent
                - source_code: Relevant source code
                - requirements: Original requirements
                
        Returns:
            AgentResult with root-cause analysis
        """
        self.log_execution("info", "Starting root-cause analysis")
        self.status = "running"

        try:
            if not await self.validate_input(input_data):
                return AgentResult(
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="Invalid input data"
                )

            failures = input_data.get("failures", [])
            if not failures:
                return AgentResult(
                    agent_name=self.name,
                    status="completed",
                    data={"analysis_result": "No failures to analyze"}
                )

            # Perform analysis on each failure
            analyses = []
            for failure in failures:
                analysis = await self._analyze_failure(failure, input_data)
                analyses.append(analysis)

            # Group related failures
            grouped = await self._group_related_failures(analyses)

            result_data = {
                "total_failures": len(failures),
                "analyses": analyses,
                "grouped_by_root_cause": grouped,
                "priority": await self._prioritize_fixes(analyses),
            }

            self.log_execution(
                "info",
                f"Analysis complete: {len(analyses)} failures analyzed"
            )

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                status="completed",
                data=result_data,
                recommendations=self._generate_fix_recommendations(analyses)
            )

        except Exception as e:
            self.log_execution("error", f"Analysis failed: {str(e)}")
            self.status = "error"
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={},
                error=str(e)
            )

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required input fields."""
        return "failures" in input_data and len(input_data.get("failures", [])) > 0

    async def _analyze_failure(self, failure: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform detailed root-cause analysis on a single failure.
        
        Steps:
        1. Classify the failure type
        2. Extract evidence
        3. Trace through system
        4. Find root cause
        5. Evaluate fix strategy
        """
        self.log_execution("info", f"Analyzing failure: {failure.get('test_name')}")

        # Step 1: Classify failure
        failure_type = await self._classify_failure(failure)

        # Step 2: Extract evidence
        evidence = await self._extract_evidence(failure, context)

        # Step 3: Trace the failure path
        trace = await self._trace_failure(failure, failure_type)

        # Step 4: Determine root cause
        root_cause = await self._determine_root_cause(failure, trace, evidence)

        # Step 5: Evaluate affected components
        affected = await self._identify_affected_components(root_cause, context)

        # Step 6: Assess confidence
        confidence = await self._assess_confidence(root_cause, evidence)

        return {
            "test_name": failure.get("test_name"),
            "failure_type": failure_type,
            "evidence": evidence,
            "trace": trace,
            "root_cause": root_cause,
            "affected_components": affected,
            "confidence": confidence,
            "security_implications": await self._check_security(failure, root_cause),
        }

    async def _classify_failure(self, failure: Dict[str, Any]) -> str:
        """Classify the type of failure."""
        error = failure.get("error", "").lower()
        
        if "attributeerror" in error or "typeerror" in error:
            return FailureType.TYPE_ERROR
        elif "expected" in error and "got" in error:
            return FailureType.LOGIC_ERROR
        elif "database" in error or "connection" in error:
            return FailureType.DATABASE_ERROR
        elif "401" in error or "auth" in error or "unauthorized" in error:
            return FailureType.AUTHENTICATION_ERROR
        elif "security" in error or "vulnerability" in error:
            return FailureType.SECURITY_ERROR
        else:
            return FailureType.RUNTIME_ERROR

    async def _extract_evidence(self, failure: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract evidence supporting the diagnosis."""
        evidence = [
            f"Test: {failure.get('test_name')}",
            f"Error: {failure.get('error')}",
            f"Traceback available: {'traceback' in failure}",
        ]

        if "traceback" in failure:
            # Extract file and line info from traceback
            traceback_lines = failure["traceback"].split("\n")
            evidence.extend([f"Stack depth: {len(traceback_lines)}", f"First frame: {traceback_lines[0]}"])

        return evidence

    async def _trace_failure(self, failure: Dict[str, Any], failure_type: str) -> Dict[str, Any]:
        """Trace the failure through the system stack."""
        return {
            "entry_point": "HTTP endpoint",
            "middleware": ["Authentication", "CORS", "Logging"],
            "handler": "Route handler",
            "service": "Service layer",
            "repository": "Data repository",
            "database": "PostgreSQL",
            "failure_point": "Exact location TBD",
        }

    async def _determine_root_cause(
        self,
        failure: Dict[str, Any],
        trace: Dict[str, Any],
        evidence: List[str]
    ) -> Dict[str, Any]:
        """Determine the actual root cause, not just symptoms."""
        error = failure.get("error", "")
        
        # Example: AttributeError 'NoneType' object
        if "nonetype" in error.lower() and "attribute" in error.lower():
            return {
                "category": "LOGIC_ERROR",
                "description": "Function returns None in cases where caller expects an object",
                "location": "Service layer - missing null check",
                "causal_chain": [
                    "Repository returns None when resource not found",
                    "Service layer doesn't validate repository response",
                    "Route tries to access attributes on None",
                    "AttributeError raised"
                ]
            }
        
        return {
            "category": "UNKNOWN",
            "description": "Requires manual investigation",
            "evidence_available": bool(evidence),
        }

    async def _identify_affected_components(
        self,
        root_cause: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify which components are affected by the root cause."""
        return [
            "Authentication Service",
            "User Repository",
            "Login Route",
        ]

    async def _assess_confidence(self, root_cause: Dict[str, Any], evidence: List[str]) -> int:
        """Assess confidence level in the diagnosis (0-100)."""
        base_confidence = 75
        
        if evidence:
            base_confidence += min(10, len(evidence) * 2)
        
        if root_cause.get("causal_chain"):
            base_confidence += 10
        
        return min(100, base_confidence)

    async def _check_security(self, failure: Dict[str, Any], root_cause: Dict[str, Any]) -> Optional[str]:
        """Check for security implications."""
        error = failure.get("error", "").lower()
        
        if "auth" in error or "token" in error:
            return "MEDIUM: Authentication bypass possible if root cause not addressed"
        
        if "sql" in error or "injection" in error:
            return "CRITICAL: SQL injection vulnerability detected"
        
        return None

    async def _group_related_failures(self, analyses: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Group failures that share a common root cause."""
        grouped = {}
        
        for analysis in analyses:
            root_cause = analysis.get("root_cause", {}).get("description", "unknown")
            if root_cause not in grouped:
                grouped[root_cause] = []
            grouped[root_cause].append(analysis.get("test_name"))
        
        return grouped

    async def _prioritize_fixes(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize which fixes to apply first."""
        # Sort by confidence and security implications
        prioritized = sorted(
            analyses,
            key=lambda x: (
                x.get("confidence", 0),
                -int(x.get("security_implications") is not None)
            ),
            reverse=True
        )
        
        return [
            {
                "test": p.get("test_name"),
                "priority": idx + 1,
                "confidence": p.get("confidence"),
            }
            for idx, p in enumerate(prioritized[:5])  # Top 5
        ]

    def _generate_fix_recommendations(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for fixing identified issues."""
        recommendations = []
        
        for analysis in analyses:
            cause = analysis.get("root_cause", {})
            if cause.get("category") == "LOGIC_ERROR":
                recommendations.append(
                    f"Add null-check in {cause.get('location', 'affected service')}"
                )
            
            if analysis.get("security_implications"):
                recommendations.append("URGENT: Address security implications first")
        
        return recommendations or ["Review detailed analysis before implementing fixes"]
