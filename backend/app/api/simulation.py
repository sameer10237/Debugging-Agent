"""Execution snapshot and state-diff endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Execution, ExecutionSnapshot
from app.services.pii_scrubber import scrub_diff_values, scrub_state, scrub_text

router = APIRouter()


class SnapshotCreate(BaseModel):
    """State to capture during an execution."""

    label: Optional[str] = None
    state: Dict[str, Any]


class SnapshotResponse(BaseModel):
    """Persisted execution state."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    execution_id: UUID
    label: Optional[str]
    state: Dict[str, Any]
    created_at: datetime


class StateChange(BaseModel):
    """One state mutation between two snapshots."""

    path: str
    change: str
    before: Any = None
    after: Any = None


class SnapshotDiffResponse(BaseModel):
    """State changes between two snapshots of one execution."""

    execution_id: UUID
    before_snapshot_id: UUID
    after_snapshot_id: UUID
    changes: List[StateChange]


@router.post(
    "/executions/{execution_id}/snapshots",
    response_model=SnapshotResponse,
    status_code=201,
)
async def create_snapshot(
    execution_id: UUID,
    request: SnapshotCreate,
    db: AsyncSession = Depends(get_db),
):
    """Capture a state snapshot for an existing execution."""
    execution = await db.get(Execution, execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    snapshot = ExecutionSnapshot(
        execution_id=execution_id,
        label=scrub_text(request.label) if request.label is not None else None,
        state=scrub_state(request.state),
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


@router.get(
    "/executions/{execution_id}/snapshots",
    response_model=List[SnapshotResponse],
)
async def list_snapshots(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List snapshots in recorded order."""
    if await db.get(Execution, execution_id) is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    result = await db.execute(
        select(ExecutionSnapshot)
        .where(ExecutionSnapshot.execution_id == execution_id)
        .order_by(ExecutionSnapshot.created_at, ExecutionSnapshot.id)
    )
    return [
        SnapshotResponse(
            id=snapshot.id,
            execution_id=snapshot.execution_id,
            label=scrub_text(snapshot.label) if snapshot.label is not None else None,
            state=scrub_state(snapshot.state),
            created_at=snapshot.created_at,
        )
        for snapshot in result.scalars().all()
    ]


@router.get(
    "/executions/{execution_id}/snapshots/diff",
    response_model=SnapshotDiffResponse,
)
async def compare_snapshots(
    execution_id: UUID,
    before_id: UUID = Query(...),
    after_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Return deterministic JSON-path changes between two snapshots."""
    snapshots = await db.execute(
        select(ExecutionSnapshot).where(
            ExecutionSnapshot.execution_id == execution_id,
            ExecutionSnapshot.id.in_([before_id, after_id]),
        )
    )
    by_id = {snapshot.id: snapshot for snapshot in snapshots.scalars().all()}
    before = by_id.get(before_id)
    after = by_id.get(after_id)
    if before is None or after is None:
        raise HTTPException(status_code=404, detail="Snapshot not found for execution")

    changes = []
    for change in _state_changes(before.state, after.state):
        safe_before, safe_after = scrub_diff_values(
            change.path,
            change.before,
            change.after,
        )
        changes.append(
            StateChange(
                path=scrub_text(change.path),
                change=change.change,
                before=safe_before,
                after=safe_after,
            )
        )

    return SnapshotDiffResponse(
        execution_id=execution_id,
        before_snapshot_id=before_id,
        after_snapshot_id=after_id,
        changes=changes,
    )


def _state_changes(before: Any, after: Any, path: str = "") -> List[StateChange]:
    if isinstance(before, dict) and isinstance(after, dict):
        changes = []
        for key in sorted(before.keys() | after.keys()):
            child_path = f"{path}/{key.replace('~', '~0').replace('/', '~1')}"
            if key not in before:
                changes.append(
                    StateChange(path=child_path, change="added", after=after[key])
                )
            elif key not in after:
                changes.append(
                    StateChange(path=child_path, change="removed", before=before[key])
                )
            else:
                changes.extend(_state_changes(before[key], after[key], child_path))
        return changes

    if isinstance(before, list) and isinstance(after, list):
        changes = []
        for index in range(max(len(before), len(after))):
            child_path = f"{path}/{index}"
            if index >= len(before):
                changes.append(
                    StateChange(path=child_path, change="added", after=after[index])
                )
            elif index >= len(after):
                changes.append(
                    StateChange(path=child_path, change="removed", before=before[index])
                )
            else:
                changes.extend(_state_changes(before[index], after[index], child_path))
        return changes

    if type(before) is not type(after) or before != after:
        return [StateChange(path=path, change="changed", before=before, after=after)]
    return []
