"""Tests for execution state history and simulation APIs."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import Execution, ExecutionSnapshot, Project


@pytest.fixture
async def simulation_session():
    """Provide an isolated SQLite database for simulation tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_execution_snapshot_persists_state(simulation_session):
    project = Project(name="snapshot-project")
    simulation_session.add(project)
    await simulation_session.flush()

    execution = Execution(project_id=project.id)
    simulation_session.add(execution)
    await simulation_session.flush()

    snapshot = ExecutionSnapshot(
        execution_id=execution.id,
        label="before failure",
        state={"step": 1, "user": {"authenticated": False}},
    )
    simulation_session.add(snapshot)
    await simulation_session.commit()

    result = await simulation_session.execute(
        select(ExecutionSnapshot).where(ExecutionSnapshot.execution_id == execution.id)
    )
    stored_snapshot = result.scalar_one()

    assert stored_snapshot.label == "before failure"
    assert stored_snapshot.state == {"step": 1, "user": {"authenticated": False}}
    assert stored_snapshot.execution_id == execution.id
