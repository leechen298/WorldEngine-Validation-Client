from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommitPoint, TimelineBranch, Session as DbSession
from ..schemas import BranchListResponse, BranchResponse, CommitPointResponse

router = APIRouter(prefix="/sessions/{session_id}/branches", tags=["timelines"])


@router.get("", response_model=BranchListResponse)
def list_branches(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    branch_rows = (
        db.execute(select(TimelineBranch).where(TimelineBranch.session_id == session_id).order_by(TimelineBranch.created_at.asc()))
        .scalars()
        .all()
    )

    branches = [
        BranchResponse(
            id=item.id,
            branch_name=item.branch_name,
            commit_point_id=item.commit_point_id,
            tick=item.tick,
            snapshot_reference=item.snapshot_reference,
            created_at=item.created_at,
        )
        for item in branch_rows
    ]

    return BranchListResponse(session_id=session_id, branches=branches)


@router.get("/commit-points", response_model=list[CommitPointResponse])
def list_commit_points(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    rows = db.execute(
        select(CommitPoint).where(CommitPoint.session_id == session_id).order_by(CommitPoint.created_at.asc())
    ).scalars().all()
    return [
        CommitPointResponse(
            id=item.id,
            session_id=item.session_id,
            tick=item.tick,
            event_id=item.event_id,
            snapshot_id=item.snapshot_id,
            payload_json=item.payload_json,
            created_at=item.created_at,
        )
        for item in rows
    ]
