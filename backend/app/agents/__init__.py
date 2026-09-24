"""Agents module - Multi-agent orchestration system."""

from app.agents.base import BaseAgent, AgentOrchestrator
from app.agents.testing_agent import TestingAgent
from app.agents.debugging_agent import DebuggingAgent
from app.agents.coding_agent import CodingAgent
from app.agents.architect_agent import ArchitectAgent
from app.agents.project_manager_agent import ProjectManagerAgent

__all__ = [
    "BaseAgent",
    "AgentOrchestrator",
    "TestingAgent",
    "DebuggingAgent",
    "CodingAgent",
    "ArchitectAgent",
    "ProjectManagerAgent",
]


def create_orchestrator() -> AgentOrchestrator:
    """Create and configure the agent orchestrator."""
    orchestrator = AgentOrchestrator()
    
    # Register all agents
    orchestrator.register_agent(TestingAgent())
    orchestrator.register_agent(DebuggingAgent())
    orchestrator.register_agent(CodingAgent())
    orchestrator.register_agent(ArchitectAgent())
    orchestrator.register_agent(ProjectManagerAgent())
    
    return orchestrator
