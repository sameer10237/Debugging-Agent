"""Improved Debugging Agent with LLM integration."""

from app.agents.base import BaseAgent, AgentResult
from app.services.llm_service import get_llm_service, RootCauseAnalysis
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ImprovedDebuggingAgent(BaseAgent):
    """
    Enhanced debugging agent using LLM for intelligent analysis.
    
    Implements the full debugging methodology with AI assistance.
    """

    def __init__(self):
        super().__init__("debugging_agent")
        self.llm_service = get_llm_service()

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Perform intelligent debugging analysis.
        
        Args:
            input_data: Failures and context
            
        Returns:
            AgentResult with comprehensive analysis
        """
        self.log_execution("info", "Starting intelligent debugging analysis")
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

            # Perform LLM-enhanced analysis
            analyses = []
            for failure in failures:
                analysis = await self._perform_llm_analysis(failure, input_data)
                analyses.append(analysis)

            # Group and prioritize
            grouped = await self._group_by_root_cause(analyses)
            priorities = await self._prioritize_by_impact(analyses)

            # Security analysis
            security_findings = await self._analyze_security_implications(analyses, input_data)

            result_data = {
                "total_failures": len(failures),
                "analyses": analyses,
                "grouped_by_root_cause": grouped,
                "priorities": priorities,
                "security_findings": security_findings,
                "overall_risk_level": self._calculate_overall_risk(security_findings),
            }

            self.log_execution(
                "info",
                f"Intelligent analysis complete: {len(analyses)} failures, risk={result_data['overall_risk_level']}"
            )

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                status="completed",
                data=result_data,
                recommendations=self._generate_recommendations(analyses, security_findings)
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

    async def _perform_llm_analysis(self, failure: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform LLM-enhanced analysis on a single failure."""
        self.log_execution("info", f"Analyzing with LLM: {failure.get('test_name')}")

        try:
            # Use LLM for root cause analysis
            llm_analysis = await self.llm_service.analyze_failure(failure)

            return {
                "test_name": failure.get("test_name"),
                "failure_type": llm_analysis.category,
                "root_cause": llm_analysis.root_cause,
                "affected_components": llm_analysis.affected_components,
                "causal_chain": llm_analysis.causal_chain,
                "confidence": llm_analysis.confidence,
                "security_implications": llm_analysis.security_implications,
                "evidence": {
                    "error": failure.get("error"),
                    "traceback_lines": len(failure.get("traceback", "").split("\n")),
                    "llm_used": True,
                }
            }

        except Exception as e:
            self.log_execution("warning", f"LLM analysis failed, using fallback: {str(e)}")
            # Fallback to heuristic analysis
            return await self._heuristic_analysis(failure)

    async def _heuristic_analysis(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback heuristic analysis when LLM is unavailable."""
        error = failure.get("error", "").lower()

        # Classification heuristics
        if "nonetype" in error or "attributeerror" in error:
            return {
                "test_name": failure.get("test_name"),
                "failure_type": "TYPE_ERROR",
                "root_cause": "Null pointer or type mismatch - accessing attribute on None",
                "affected_components": ["Service Layer"],
                "causal_chain": [
                    "Function returns None",
                    "Caller assumes non-None value",
                    "AttributeError raised"
                ],
                "confidence": 80,
                "security_implications": None,
                "evidence": {"error": error}
            }

        elif "expected" in error and "got" in error:
            return {
                "test_name": failure.get("test_name"),
                "failure_type": "LOGIC_ERROR",
                "root_cause": "Logic error - function returns incorrect value or status",
                "affected_components": ["Business Logic"],
                "causal_chain": ["Incorrect condition", "Wrong return value"],
                "confidence": 75,
                "security_implications": None,
                "evidence": {"error": error}
            }

        elif "401" in error or "403" in error or "auth" in error:
            return {
                "test_name": failure.get("test_name"),
                "failure_type": "AUTHENTICATION_ERROR",
                "root_cause": "Authentication or authorization failure",
                "affected_components": ["Authentication Service"],
                "causal_chain": ["Auth check failed", "Incorrect status returned"],
                "confidence": 85,
                "security_implications": "MEDIUM: Potential authentication bypass",
                "evidence": {"error": error}
            }

        else:
            return {
                "test_name": failure.get("test_name"),
                "failure_type": "RUNTIME_ERROR",
                "root_cause": "Runtime error requiring investigation",
                "affected_components": ["Unknown"],
                "causal_chain": ["Error occurred at runtime"],
                "confidence": 50,
                "security_implications": None,
                "evidence": {"error": error}
            }

    async def _analyze_security_implications(
        self,
        analyses: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze security implications of failures."""
        security_findings = []

        for analysis in analyses:
            if analysis.get("security_implications"):
                security_findings.append({
                    "test": analysis.get("test_name"),
                    "issue": analysis.get("security_implications"),
                    "component": analysis.get("affected_components", ["Unknown"])[0],
                })

        return security_findings

    async def _group_by_root_cause(self, analyses: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Group failures by root cause."""
        grouped = {}

        for analysis in analyses:
            root_cause = analysis.get("root_cause", "unknown")
            if root_cause not in grouped:
                grouped[root_cause] = []
            grouped[root_cause].append(analysis.get("test_name"))

        return grouped

    async def _prioritize_by_impact(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize failures by impact (security, confidence, etc.)."""
        def impact_score(analysis):
            score = analysis.get("confidence", 0)
            if analysis.get("security_implications"):
                score += 50
            return score

        prioritized = sorted(analyses, key=impact_score, reverse=True)

        return [
            {
                "rank": idx + 1,
                "test": p.get("test_name"),
                "confidence": p.get("confidence"),
                "impact": "HIGH" if p.get("security_implications") else "MEDIUM",
            }
            for idx, p in enumerate(prioritized[:10])
        ]

    def _calculate_overall_risk(self, security_findings: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level."""
        if any("CRITICAL" in str(f.get("issue", "")) for f in security_findings):
            return "CRITICAL"
        elif len(security_findings) > 2:
            return "HIGH"
        elif security_findings:
            return "MEDIUM"
        return "LOW"

    def _generate_recommendations(
        self,
        analyses: List[Dict[str, Any]],
        security_findings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations."""
        recommendations = []

        if security_findings:
            recommendations.append(f"🔒 SECURITY: Address {len(security_findings)} security findings immediately")

        high_confidence = [a for a in analyses if a.get("confidence", 0) >= 80]
        if high_confidence:
            recommendations.append(f"✓ Implement fixes for {len(high_confidence)} high-confidence analyses")

        return recommendations or ["Review detailed analysis"]
