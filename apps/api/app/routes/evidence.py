from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    CommitPoint,
    DirectorIntent,
    Event,
    Session as DbSession,
    Snapshot,
    StateDiff,
    TimelineBranch,
)
from ..schemas import EvidenceBundleMetadata

router = APIRouter(prefix="/sessions/{session_id}/evidence")


@router.get("/bundle", response_model=EvidenceBundleMetadata)
def get_bundle(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    def count(model) -> int:
        return int(db.execute(select(func.count(model.id)).where(model.session_id == session_id)).scalar() or 0)

    return EvidenceBundleMetadata(
        session_id=session.id,
        session_name=session.session_name,
        branches=count(TimelineBranch),
        events=count(Event),
        state_diffs=count(StateDiff),
        snapshots=count(Snapshot),
        commit_points=count(CommitPoint),
        director_intents=count(DirectorIntent),
        llm_keys_included=False,
        private_worldengine_internals_included=False,
    )
