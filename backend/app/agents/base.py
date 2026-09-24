"""Base agent class and shared utilities for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
from pydantic import BaseModel
import json
import logging

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class AgentMessage(BaseModel):
    """Message passed between agents."""
    sender: str
    recipient: str
    message_type: str  # request, response, notification
    content: Dict[str, Any]
    timestamp: Optional[str] = None


class AgentResult(BaseModel):
    """Result returned by an agent."""
    agent_name: str
    status: str
    data: Dict[str, Any]
    error: Optional[str] = None
    recommendations: Optional[list] = None


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str):
        self.name = name
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"agents.{name}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main function.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            AgentResult with status and output
        """
        pass

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data. Override in subclasses."""
        return True

    async def prepare_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare execution context. Override in subclasses."""
        return input_data

    def log_execution(self, level: str, message: str, **kwargs):
        """Log agent execution."""
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(f"[{self.name}] {message}", extra=kwargs)


class AgentOrchestrator:
    """Orchestrates communication between agents."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: list = []
        self.execution_state: Dict[str, Any] = {}
        self.logger = logging.getLogger("orchestrator")

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.name] = agent
        self.logger.info(f"Agent registered: {agent.name}")

    async def execute_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow of agents.
        
        Args:
            workflow_config: Configuration specifying which agents to run and in what order
            
        Returns:
            Complete workflow results
        """
        self.execution_state = workflow_config.get("initial_state", {})
        results = {}

        for step in workflow_config.get("steps", []):
            agent_name = step["agent"]
            
            if agent_name not in self.agents:
                self.logger.error(f"Agent not found: {agent_name}")
                continue

            self.logger.info(f"Executing agent: {agent_name}")
            
            try:
                agent = self.agents[agent_name]
                result = await agent.execute(self.execution_state)
                results[agent_name] = result.dict()
                
                # Update execution state with agent results
                if step.get("update_state", True):
                    self.execution_state.update(result.data)

            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed: {str(e)}")
                results[agent_name] = {
                    "agent_name": agent_name,
                    "status": "error",
                    "error": str(e),
                    "data": {}
                }
                
                if step.get("stop_on_error", False):
                    break

        return {
            "workflow_complete": True,
            "results": results,
            "final_state": self.execution_state
        }

    async def route_message(self, message: AgentMessage):
        """Route a message between agents."""
        if message.recipient in self.agents:
            self.agents[message.recipient].log_execution(
                "info",
                f"Message from {message.sender}: {message.message_type}"
            )
            self.message_queue.append(message)
        else:
            self.logger.warning(f"Unknown recipient: {message.recipient}")
