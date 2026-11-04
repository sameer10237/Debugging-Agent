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


@pytest.mark.asyncio
async def test_execution_analysis_proposed_fix_cascade(async_db_session):
    """Verify that deleting an Execution cascades down to Analysis and ProposedFix."""
    from app.models import Analysis, Execution, ProposedFix

    project = Project(name="cascade-analysis-project")
    async_db_session.add(project)
    await async_db_session.flush()

    execution = Execution(project_id=project.id)
    async_db_session.add(execution)
    await async_db_session.flush()

    analysis = Analysis(
        execution_id=execution.id,
        project_id=project.id,
        root_cause="IndexError in loop",
    )
    async_db_session.add(analysis)
    await async_db_session.flush()

    fix = ProposedFix(
        analysis_id=analysis.id,
        file_path="main.py",
        change_description="Fix loop boundary condition",
    )
    async_db_session.add(fix)
    await async_db_session.commit()

    # Verify relationships
    res_exec = await async_db_session.execute(select(Execution).where(Execution.id == execution.id))
    loaded_exec = res_exec.scalars().first()
    assert loaded_exec.analysis is not None
    assert len(loaded_exec.analysis.proposed_fixes) == 1
    assert loaded_exec.analysis.proposed_fixes[0].analysis.id == analysis.id

    # Delete Execution and verify Analysis + ProposedFix are cascaded
    await async_db_session.delete(loaded_exec)
    await async_db_session.commit()

    res_an = await async_db_session.execute(select(Analysis).where(Analysis.id == analysis.id))
    assert res_an.scalars().first() is None

    res_fix = await async_db_session.execute(select(ProposedFix).where(ProposedFix.id == fix.id))
    assert res_fix.scalars().first() is None


def test_foreign_keys_have_cascade_delete():
    """Verify that child table foreign keys are configured with ondelete='CASCADE'."""
    from app.models import AgentExecution, Analysis, Execution, ExecutionSnapshot, Failure, ProposedFix, TestRun

    tables_and_fks = [
        (Execution, "projects.id"),
        (AgentExecution, "executions.id"),
        (TestRun, "projects.id"),
        (Failure, "test_runs.id"),
        (Analysis, "executions.id"),
        (Analysis, "projects.id"),
        (ProposedFix, "analyses.id"),
        (ExecutionSnapshot, "executions.id"),
    ]

    for model, target_col in tables_and_fks:
        fk = next(f for f in model.__table__.foreign_keys if f.target_fullname == target_col)
        assert fk.ondelete == "CASCADE", f"FK on {model.__tablename__} -> {target_col} missing ondelete='CASCADE'"
