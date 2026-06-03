import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommitPoint, Event, Session as DbSession, TimelineBranch
from ..schemas import (
    BranchResponse,
    BranchCreatePayload,
    EventResponse,
    SessionCreatePayload,
    SessionListResponse,
    SessionSummary,
)

router = APIRouter(prefix="/sessions")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SessionSummary)
def create_session(payload: SessionCreatePayload, db: Session = Depends(get_db)):
    db_session = DbSession(session_name=payload.session_name)
    db.add(db_session)
    db.flush()

    first_commit = CommitPoint(session_id=db_session.id, tick=0, payload_json="{}")
    db.add(first_commit)
    db.flush()

    main_branch = TimelineBranch(
        session_id=db_session.id,
        branch_name="main",
        commit_point_id=first_commit.id,
        tick=0,
        snapshot_reference=None,
        is_main=True,
    )
    db.add(main_branch)
    db.commit()
    db.refresh(db_session)
    db.refresh(main_branch)

    return SessionSummary(
        id=db_session.id,
        session_name=db_session.session_name,
        status=db_session.status,
        worldengine_world_id=db_session.worldengine_world_id,
        public_world_status=db_session.public_world_status,
        initial_state_summary=db_session.initial_state_summary,
        visualization_payload_summary=db_session.visualization_payload_summary,
        branch_count=1,
        main_branch_id=main_branch.id,
        main_commit_point_id=first_commit.id,
        created_at=db_session.created_at,
        updated_at=db_session.updated_at,
    )


@router.get("", response_model=SessionListResponse)
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.execute(select(DbSession).order_by(DbSession.created_at.desc())).scalars().all()
    result = []
    for item in sessions:
        main_branch = (
            db.execute(
                select(TimelineBranch)
                .where(TimelineBranch.session_id == item.id, TimelineBranch.is_main.is_(True))
                .order_by(TimelineBranch.created_at.asc())
                .limit(1)
            )
            .scalars()
            .first()
        )
        branch_count = (
            db.execute(select(func.count(TimelineBranch.id)).where(TimelineBranch.session_id == item.id)).scalar() or 0
        )

        result.append(
            SessionSummary(
                id=item.id,
                session_name=item.session_name,
                status=item.status,
                worldengine_world_id=item.worldengine_world_id,
                public_world_status=item.public_world_status,
                initial_state_summary=item.initial_state_summary,
                visualization_payload_summary=item.visualization_payload_summary,
                branch_count=int(branch_count),
                main_branch_id=main_branch.id if main_branch else None,
                main_commit_point_id=main_branch.commit_point_id if main_branch else None,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
        )

    return SessionListResponse(sessions=result)


@router.post("/{session_id}/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(session_id: str, payload: BranchCreatePayload, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    commit_point = db.get(CommitPoint, payload.commit_point_id)
    if not commit_point or commit_point.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commit point not found")

    existing_branch = (
        db.execute(
            select(TimelineBranch).where(
                TimelineBranch.session_id == session_id,
                TimelineBranch.branch_name == payload.branch_name,
            )
        )
        .scalars()
        .first()
    )
    if existing_branch:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Branch name already exists")

    branch = TimelineBranch(
        session_id=session_id,
        branch_name=payload.branch_name,
        commit_point_id=payload.commit_point_id,
        tick=commit_point.tick,
        snapshot_reference=commit_point.snapshot_id,
        is_main=False,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return BranchResponse(
        id=branch.id,
        branch_name=branch.branch_name,
        commit_point_id=branch.commit_point_id,
        tick=branch.tick,
        snapshot_reference=branch.snapshot_reference,
        created_at=branch.created_at,
    )


@router.get("/{session_id}/events", response_model=list[EventResponse])
def list_session_events(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    events = db.execute(
        select(Event).where(Event.session_id == session_id).order_by(Event.created_at.asc())
    ).scalars().all()
    return events
