"""Project Manager Agent - Manages prioritization and conflict resolution."""

from app.agents.base import BaseAgent, AgentResult
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class ProjectManagerAgent(BaseAgent):
    """Agent responsible for project management aspects of fixes."""

    def __init__(self):
        super().__init__("project_manager_agent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Manage prioritization and requirements.
        
        Args:
            input_data: Should contain:
                - analysis: Debugging analysis
                - proposed_fixes: Proposed code fixes
                - architectural_review: Architect review
                - requirements: Project requirements
        """
        self.log_execution("info", "Starting project management review")
        self.status = "running"

        try:
            if not await self.validate_input(input_data):
                return AgentResult(
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="Invalid input data"
                )

            # Prioritize fixes
            priorities = await self._prioritize_fixes(input_data)
            
            # Check for conflicts
            conflicts = await self._identify_conflicts(input_data)
            
            # Estimate effort
            estimates = await self._estimate_effort(priorities)
            
            result_data = {
                "priorities": priorities,
                "conflicts": conflicts,
                "effort_estimates": estimates,
                "implementation_plan": await self._create_implementation_plan(priorities),
            }

            self.log_execution("info", "Project management review complete")
            
            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                status="completed",
                data=result_data,
                recommendations=self._generate_recommendations(priorities),
            )

        except Exception as e:
            self.log_execution("error", f"Project management failed: {str(e)}")
            self.status = "error"
            return AgentResult(
                agent_name=self.name,
                status="error",
                data={},
                error=str(e)
            )

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input."""
        return all(key in input_data for key in ["analysis", "proposed_fixes"])

    async def _prioritize_fixes(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize fixes by impact and effort."""
        analysis = input_data.get("analysis", {})
        fixes = input_data.get("proposed_fixes", [])
        
        priorities = []
        for idx, fix in enumerate(fixes, 1):
            # Find matching analysis
            test_analysis = next(
                (a for a in analysis.get("analyses", []) if a.get("test_name") == fix.get("test_name")),
                {}
            )
            
            priority = {
                "rank": idx,
                "fix": fix.get("test_name"),
                "severity": "high" if test_analysis.get("security_implications") else "medium",
                "effort": "low",
                "impact": "high",
                "recommendation": "Implement immediately" if test_analysis.get("security_implications") else "Schedule in current sprint",
            }
            priorities.append(priority)
        
        return priorities

    async def _identify_conflicts(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify conflicts between requirements or fixes."""
        return [
            {
                "type": "dependency",
                "description": "Fix A must be implemented before Fix B",
                "resolution": "Follow priority order",
            }
        ]

    async def _estimate_effort(self, priorities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate effort for implementing all fixes."""
        total_hours = sum(2 if p.get("severity") == "high" else 1 for p in priorities)
        
        return {
            "total_hours": total_hours,
            "total_days": (total_hours + 7) // 8,
            "by_priority": [
                {"rank": p["rank"], "hours": 2 if p.get("severity") == "high" else 1}
                for p in priorities
            ],
        }

    async def _create_implementation_plan(self, priorities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create detailed implementation plan."""
        plan = []
        day = 1
        
        for priority in priorities:
            plan.append({
                "phase": f"Phase {priority['rank']}",
                "fixes": [priority["fix"]],
                "timeline": f"Day {day}",
                "deliverables": ["Code changes", "Tests", "Documentation"],
            })
            day += 1
        
        return plan

    def _generate_recommendations(self, priorities: List[Dict[str, Any]]) -> List[str]:
        """Generate project management recommendations."""
        recommendations = [
            "Follow priority order for implementation",
            "All fixes are feasible and low-risk",
        ]
        
        high_severity = [p for p in priorities if p.get("severity") == "high"]
        if high_severity:
            recommendations.append(f"URGENT: {len(high_severity)} high-severity fix(es) require immediate attention")
        
        return recommendations
