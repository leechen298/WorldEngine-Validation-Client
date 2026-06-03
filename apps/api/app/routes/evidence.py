from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import (
    ApiTrace,
    CommitPoint,
    DirectorIntent,
    Event,
    Session as DbSession,
    Snapshot,
    StateDiff,
    TimelineBranch,
)
from ..schemas import (
    EvidenceBundleCounts,
    EvidenceBundleManifest,
    EvidenceBundleMetadata,
    EvidenceBundleRecords,
    EvidenceBundleRedactionFlags,
    EvidenceBundleResponse,
)

router = APIRouter(prefix="/sessions/{session_id}/evidence")


def _bundle_counts(session_id: str, db: Session) -> EvidenceBundleCounts:
    def count(model) -> int:
        return int(db.execute(select(func.count(model.id)).where(model.session_id == session_id)).scalar() or 0)

    return EvidenceBundleCounts(
        branches=count(TimelineBranch),
        events=count(Event),
        state_diffs=count(StateDiff),
        snapshots=count(Snapshot),
        commit_points=count(CommitPoint),
        director_intents=count(DirectorIntent),
        api_traces=count(ApiTrace),
    )


def _redaction_flags(session_id: str, db: Session) -> EvidenceBundleRedactionFlags:
    llm_keys_count = int(
        db.execute(
            select(func.count(ApiTrace.id)).where(ApiTrace.session_id == session_id, ApiTrace.llm_keys_included.is_(True))
        ).scalar()
        or 0
    )
    private_internals_count = int(
        db.execute(
            select(func.count(ApiTrace.id)).where(
                ApiTrace.session_id == session_id,
                ApiTrace.private_worldengine_internals_included.is_(True),
            )
        ).scalar()
        or 0
    )
    return EvidenceBundleRedactionFlags(
        llm_keys_included=llm_keys_count > 0,
        private_worldengine_internals_included=private_internals_count > 0,
    )


@router.get("/bundle", response_model=EvidenceBundleMetadata)
def get_bundle(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    counts = _bundle_counts(session_id, db)

    return EvidenceBundleMetadata(
        session_id=session.id,
        session_name=session.session_name,
        branches=counts.branches,
        events=counts.events,
        state_diffs=counts.state_diffs,
        snapshots=counts.snapshots,
        commit_points=counts.commit_points,
        director_intents=counts.director_intents,
        api_traces=counts.api_traces,
        llm_keys_included=False,
        private_worldengine_internals_included=False,
    )


@router.get("/bundle/manifest", response_model=EvidenceBundleResponse)
def get_bundle_manifest(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    redaction_flags = _redaction_flags(session_id, db)
    warnings = ["records reserved for Task 3 content export"]
    if redaction_flags.llm_keys_included or redaction_flags.private_worldengine_internals_included:
        warnings.append("api traces include flagged sensitive content")

    manifest = EvidenceBundleManifest(
        bundle_schema_version="0.6.0",
        generated_at=datetime.now(UTC),
        session_id=session.id,
        session_name=session.session_name,
        worldengine_world_id=session.worldengine_world_id,
        world_status=session.public_world_status or session.status,
        counts=_bundle_counts(session_id, db),
        redaction_flags=redaction_flags,
        warnings=warnings,
    )

    return EvidenceBundleResponse(manifest=manifest, records=EvidenceBundleRecords())
