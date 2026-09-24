"""Comprehensive test suite for backend."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import Base
from app.main import app
from app.models import Project, Execution, ExecutionStatusEnum
from app.agents.base import BaseAgent, AgentResult
from app.services.llm_service import LLMService
from uuid import uuid4
import asyncio


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create in-memory test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_db):
    """Create test database session."""
    async_session = async_sessionmaker(test_db, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_project(client, test_session):
    """Test project creation."""
    response = await client.post(
        "/api/projects",
        json={
            "name": "test-project",
            "description": "Test project",
            "repository_url": "https://github.com/test/repo"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test-project"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_projects(client, test_session):
    """Test project listing."""
    # Create test project
    await client.post(
        "/api/projects",
        json={"name": "project1", "description": "Test"}
    )
    
    response = await client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_nonexistent_project(client):
    """Test getting non-existent project."""
    from uuid import uuid4
    fake_id = uuid4()
    
    response = await client.get(f"/api/projects/{fake_id}")
    assert response.status_code == 404


# ============================================================================
# Agent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_testing_agent_execution():
    """Test Testing Agent execution."""
    from app.agents.testing_agent import TestingAgent
    
    agent = TestingAgent()
    result = await agent.execute({
        "project_path": "/tmp/test",
        "test_framework": "pytest",
        "test_paths": []
    })
    
    assert result.status == "completed"
    assert "test_results" in result.data
    assert result.data["passed_count"] == 12
    assert result.data["failed_count"] == 2


@pytest.mark.asyncio
async def test_debugging_agent_with_failures():
    """Test Debugging Agent with failures."""
    from app.agents.debugging_agent import DebuggingAgent
    
    agent = DebuggingAgent()
    
    failures = [
        {
            "test_name": "test_login",
            "error": "AttributeError: 'NoneType' object has no attribute 'id'",
            "traceback": "File test_auth.py, line 42, in test_login\n  user.id"
        }
    ]
    
    result = await agent.execute({"failures": failures})
    
    assert result.status == "completed"
    assert "analyses" in result.data
    assert len(result.data["analyses"]) == 1
    assert result.data["analyses"][0]["confidence"] > 0


@pytest.mark.asyncio
async def test_improved_debugging_agent():
    """Test Improved Debugging Agent with LLM simulation."""
    from app.agents.improved_debugging_agent import ImprovedDebuggingAgent
    
    agent = ImprovedDebuggingAgent()
    
    failures = [
        {
            "test_name": "test_invalid_password",
            "error": "AssertionError: Expected 401, got 200",
            "traceback": "test_auth.py:42"
        }
    ]
    
    result = await agent.execute({"failures": failures})
    
    assert result.status == "completed"
    assert "analyses" in result.data
    assert "security_findings" in result.data
    analysis = result.data["analyses"][0]
    assert "confidence" in analysis


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling."""
    from app.agents.debugging_agent import DebuggingAgent
    
    agent = DebuggingAgent()
    result = await agent.execute({})  # Empty input
    
    assert result.status == "error" or result.data.get("analysis_result") is not None


# ============================================================================
# LLM Service Tests
# ============================================================================

@pytest.mark.asyncio
async def test_llm_service_mock_analysis():
    """Test LLM service with mock (when no API key)."""
    llm_service = LLMService()
    
    failure = {
        "test_name": "test_example",
        "error": "Some error",
        "traceback": "trace"
    }
    
    # This will return mock if no API key
    analysis = await llm_service.analyze_failure(failure)
    
    assert analysis is not None
    assert "category" in analysis.model_dump()


# ============================================================================
# Exception Tests
# ============================================================================

def test_validation_exception():
    """Test ValidationException."""
    from app.exceptions import ValidationException
    
    exc = ValidationException("Invalid field", field="email")
    assert exc.status_code == 422
    assert exc.error_code == "VALIDATION_ERROR"


def test_not_found_exception():
    """Test NotFoundException."""
    from app.exceptions import NotFoundException
    
    exc = NotFoundException("Project", "uuid-123")
    assert exc.status_code == 404
    assert "uuid-123" in exc.message


def test_unauthorized_exception():
    """Test UnauthorizedException."""
    from app.exceptions import UnauthorizedException
    
    exc = UnauthorizedException()
    assert exc.status_code == 401
    assert exc.error_code == "UNAUTHORIZED"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_workflow_execution():
    """Test a full debugging workflow (integration test)."""
    from app.agents import create_orchestrator
    
    orchestrator = create_orchestrator()
    
    workflow_config = {
        "initial_state": {
            "project_id": str(uuid4()),
            "test_framework": "pytest",
            "test_paths": []
        },
        "steps": [
            {"agent": "testing_agent", "update_state": True},
            {"agent": "debugging_agent", "update_state": True},
        ]
    }
    
    results = await orchestrator.execute_workflow(workflow_config)
    
    assert results["workflow_complete"]
    assert "testing_agent" in results["results"]
    assert "debugging_agent" in results["results"]


# ============================================================================
# Fixture Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after tests."""
    yield
    # Add cleanup code here if needed


# Run tests: pytest backend/tests/test_comprehensive.py
