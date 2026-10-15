"""Tests for execution state history and simulation APIs."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api import simulation
from app.database import Base, get_db
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


@pytest.fixture
async def simulation_client():
    """Provide an API client backed by an isolated SQLite database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        project = Project(name="simulation-api-project")
        session.add(project)
        await session.flush()
        execution = Execution(project_id=project.id)
        other_execution = Execution(project_id=project.id)
        session.add_all([execution, other_execution])
        await session.commit()
        execution_id = execution.id
        other_execution_id = other_execution.id

    async def override_get_db():
        async with session_factory() as session:
            yield session

    test_app = FastAPI()
    test_app.include_router(simulation.router, prefix="/api")
    test_app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client, execution_id, other_execution_id
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


@pytest.mark.asyncio
async def test_snapshot_timeline_and_state_diff(simulation_client):
    client, execution_id, _ = simulation_client
    before_response = await client.post(
        f"/api/executions/{execution_id}/snapshots",
        json={
            "label": "before request",
            "state": {"request": {"status": "pending"}, "items": [1, 2]},
        },
    )
    after_response = await client.post(
        f"/api/executions/{execution_id}/snapshots",
        json={
            "label": "after request",
            "state": {"request": {"status": "failed"}, "items": [1, 3], "retry": True},
        },
    )

    assert before_response.status_code == 201
    assert after_response.status_code == 201
    before_id = before_response.json()["id"]
    after_id = after_response.json()["id"]

    timeline_response = await client.get(
        f"/api/executions/{execution_id}/snapshots"
    )
    diff_response = await client.get(
        f"/api/executions/{execution_id}/snapshots/diff",
        params={"before_id": before_id, "after_id": after_id},
    )

    assert timeline_response.status_code == 200
    assert [item["id"] for item in timeline_response.json()] == [before_id, after_id]
    assert diff_response.status_code == 200
    assert diff_response.json()["changes"] == [
        {"path": "/items/1", "change": "changed", "before": 2, "after": 3},
        {"path": "/request/status", "change": "changed", "before": "pending", "after": "failed"},
        {"path": "/retry", "change": "added", "before": None, "after": True},
    ]


@pytest.mark.asyncio
async def test_snapshot_diff_rejects_snapshot_from_another_execution(simulation_client):
    client, execution_id, other_execution_id = simulation_client
    first = await client.post(
        f"/api/executions/{execution_id}/snapshots",
        json={"state": {"step": 1}},
    )
    second = await client.post(
        f"/api/executions/{other_execution_id}/snapshots",
        json={"state": {"step": 2}},
    )

    response = await client.get(
        f"/api/executions/{execution_id}/snapshots/diff",
        params={
            "before_id": first.json()["id"],
            "after_id": second.json()["id"],
        },
    )

    assert response.status_code == 404
