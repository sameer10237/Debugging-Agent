"""Execution and debugging workflow endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from app.database import get_db
from app.models import Execution, Project, ExecutionStatusEnum
from app.agents import create_orchestrator
from sqlalchemy import select
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ExecutionRequest(BaseModel):
    """Request to start a debugging workflow."""
    project_id: UUID
    test_paths: Optional[List[str]] = None
    test_framework: str = "pytest"


class ExecutionResponse(BaseModel):
    """Execution response."""
    id: UUID
    project_id: UUID
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/executions", response_model=ExecutionResponse, status_code=202)
async def start_execution(
    request: ExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start a debugging workflow execution."""
    
    # Verify project exists
    stmt = select(Project).where(Project.id == request.project_id)
    result = await db.execute(stmt)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create execution
    execution = Execution(
        project_id=request.project_id,
        status=ExecutionStatusEnum.PENDING,
        metadata={
            "test_framework": request.test_framework,
            "test_paths": request.test_paths or [],
        }
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # Schedule workflow (in production, use a task queue)
    import asyncio
    asyncio.create_task(_run_workflow(str(execution.id), request, db))
    
    return execution


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get execution status and results."""
    stmt = select(Execution).where(Execution.id == execution_id)
    result = await db.execute(stmt)
    execution = result.scalars().first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution


@router.get("/executions/{execution_id}/results")
async def get_execution_results(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed results from a completed execution."""
    stmt = select(Execution).where(Execution.id == execution_id)
    result = await db.execute(stmt)
    execution = result.scalars().first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Return execution metadata and related data
    return {
        "execution_id": str(execution.id),
        "status": execution.status,
        "created_at": execution.created_at.isoformat(),
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "metadata": execution.metadata or {},
        "error": execution.error_message,
    }


async def _run_workflow(execution_id: str, request: ExecutionRequest, db: AsyncSession):
    """Run the debugging workflow (background task)."""
    try:
        # Create orchestrator
        orchestrator = create_orchestrator()
        
        # Prepare workflow
        workflow_config = {
            "initial_state": {
                "project_id": str(request.project_id),
                "test_framework": request.test_framework,
                "test_paths": request.test_paths or [],
            },
            "steps": [
                {"agent": "testing_agent", "update_state": True},
                {"agent": "debugging_agent", "update_state": True},
                {"agent": "coding_agent", "update_state": True},
                {"agent": "architect_agent", "update_state": True},
                {"agent": "project_manager_agent", "update_state": True},
            ]
        }
        
        # Execute workflow
        logger.info(f"Starting workflow execution: {execution_id}")
        results = await orchestrator.execute_workflow(workflow_config)
        
        # Update execution status
        stmt = select(Execution).where(Execution.id == UUID(execution_id))
        result = await db.execute(stmt)
        execution = result.scalars().first()
        
        if execution:
            execution.status = ExecutionStatusEnum.COMPLETED
            execution.metadata = {
                **(execution.metadata or {}),
                "workflow_results": results,
            }
            await db.commit()
            logger.info(f"Workflow completed: {execution_id}")
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        
        stmt = select(Execution).where(Execution.id == UUID(execution_id))
        result = await db.execute(stmt)
        execution = result.scalars().first()
        
        if execution:
            execution.status = ExecutionStatusEnum.FAILED
            execution.error_message = str(e)
            await db.commit()
