import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CommitPoint, TimelineBranch, Session as DbSession
from ..schemas import BranchListResponse, BranchResponse, CommitPointResponse

router = APIRouter(prefix="/sessions/{session_id}/branches", tags=["timelines"])

PRIVATE_PAYLOAD_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "file_path",
    "goal",
    "helper",
    "internal",
    "key",
    "memory",
    "oracle",
    "password",
    "path",
    "private",
    "prompt",
    "provider",
    "secret",
    "source_path",
    "thought",
    "token",
)


def _load_json_object(raw_value: str | None) -> dict[str, Any]:
    if not raw_value:
        return {}
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _public_payload(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if any(part in str(key).lower() for part in PRIVATE_PAYLOAD_KEY_PARTS):
                continue
            result[key] = _public_payload(item)
        return result
    if isinstance(value, list):
        return [_public_payload(item) for item in value]
    return value


def _payload_summary(raw_value: str | None) -> str | None:
    payload = _public_payload(_load_json_object(raw_value))
    for key in ("summary", "text", "description", "event_kind"):
        value = payload.get(key)
        if value is not None:
            return str(value)
    return None


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
            current_tick=item.tick,
            snapshot_reference=item.snapshot_reference,
            is_main=item.is_main,
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
    result = []
    for item in rows:
        branches = (
            db.execute(
                select(TimelineBranch)
                .where(TimelineBranch.session_id == session_id, TimelineBranch.commit_point_id == item.id)
                .order_by(TimelineBranch.created_at.asc())
            )
            .scalars()
            .all()
        )
        result.append(
            CommitPointResponse(
                id=item.id,
                session_id=item.session_id,
                tick=item.tick,
                event_id=item.event_id,
                snapshot_id=item.snapshot_id,
                payload_summary=_payload_summary(item.payload_json),
                branch_ids=[branch.id for branch in branches],
                branch_names=[branch.branch_name for branch in branches],
                created_at=item.created_at,
            )
        )
    return result
