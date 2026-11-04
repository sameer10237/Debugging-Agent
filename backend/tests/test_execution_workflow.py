"""Unit tests for execution background workflow session isolation."""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import Execution, ExecutionStatusEnum, Project
from app.api.executions import ExecutionRequest, _run_workflow


@pytest.fixture
async def workflow_test_env():
    """Create test database and mock async_session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    with patch("app.api.executions.async_session", session_factory):
        yield session_factory

    await engine.dispose()


@pytest.mark.asyncio
async def test_run_workflow_completes_with_isolated_session(workflow_test_env):
    """Ensure _run_workflow acquires its own session and transitions status to COMPLETED."""
    session_factory = workflow_test_env

    # Setup project and initial pending execution
    async with session_factory() as db:
        project = Project(name="workflow-session-test-project")
        db.add(project)
        await db.flush()

        execution = Execution(
            project_id=project.id,
            status=ExecutionStatusEnum.PENDING,
        )
        db.add(execution)
        await db.commit()
        execution_id = execution.id

    request = ExecutionRequest(
        project_id=project.id,
        test_framework="pytest",
    )

    # Mock orchestrator to return mock results
    mock_orchestrator = AsyncMock()
    mock_orchestrator.execute_workflow.return_value = {"status": "ok", "steps_completed": 5}

    with patch("app.api.executions.create_orchestrator", return_value=mock_orchestrator):
        await _run_workflow(str(execution_id), request)

    # Verify execution was updated to COMPLETED with workflow_results
    async with session_factory() as db:
        result = await db.execute(select(Execution).where(Execution.id == execution_id))
        updated = result.scalars().first()
        assert updated.status == ExecutionStatusEnum.COMPLETED
        assert updated.execution_metadata is not None
        assert updated.execution_metadata["workflow_results"] == {"status": "ok", "steps_completed": 5}
