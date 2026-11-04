"""Tests for model relationships and cascade deletion rules."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import Failure, FailureTypeEnum, Project, TestRun


@pytest.fixture
async def async_db_session():
    """Create an isolated SQLite database and yield session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_test_run_failures_relationship_and_cascade(async_db_session):
    """Verify bidirectional relationship and cascade deletion of Failures when TestRun is deleted."""
    project = Project(name="test-relationship-project")
    async_db_session.add(project)
    await async_db_session.flush()

    test_run = TestRun(
        project_id=project.id,
        test_file="tests/test_demo.py",
        test_name="test_addition",
    )
    async_db_session.add(test_run)
    await async_db_session.flush()

    failure = Failure(
        test_run_id=test_run.id,
        failure_type=FailureTypeEnum.ASSERTION_ERROR if hasattr(FailureTypeEnum, "ASSERTION_ERROR") else FailureTypeEnum.UNKNOWN,
        message="AssertionError: 1 != 2",
    )
    async_db_session.add(failure)
    await async_db_session.commit()

    # Verify relationship navigation from TestRun -> failures
    res = await async_db_session.execute(select(TestRun).where(TestRun.id == test_run.id))
    loaded_run = res.scalars().first()
    assert len(loaded_run.failures) == 1
    assert loaded_run.failures[0].message == "AssertionError: 1 != 2"
    assert loaded_run.failures[0].test_run.id == test_run.id

    # Verify cascade deletion
    await async_db_session.delete(loaded_run)
    await async_db_session.commit()

    res_fail = await async_db_session.execute(select(Failure).where(Failure.test_run_id == test_run.id))
    assert res_fail.scalars().first() is None
