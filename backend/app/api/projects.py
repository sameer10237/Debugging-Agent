"""Project management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.database import get_db
from app.models import Project
from sqlalchemy import select

router = APIRouter()


class ProjectCreate(BaseModel):
    """Project creation request."""
    name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response."""
    id: UUID
    name: str
    description: Optional[str]
    repository_url: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project."""
    new_project = Project(
        name=project.name,
        description=project.description,
        repository_url=project.repository_url,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a project by ID."""
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """List all projects."""
    stmt = select(Project).offset(skip).limit(limit)
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return projects


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project."""
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.delete(project)
    await db.commit()
