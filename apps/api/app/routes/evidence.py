import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
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

SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "hidden_context",
    "internal",
    "key",
    "memory",
    "oracle",
    "password",
    "path",
    "private",
    "private_prompt",
    "provider",
    "raw_response",
    "secret",
    "self_state",
    "source_path",
    "thought",
    "token",
)

LLM_KEY_PARTS = ("api_key", "apikey", "authorization", "credential", "key", "password", "secret", "token")
SENSITIVE_VALUE_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "hidden_context",
    "private_prompt",
    "provider_secret",
    "raw_response",
    "self_state",
    "source_path",
    "password",
    "secret",
    "token",
)


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
        replay_index=count(CommitPoint),
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


def _load_json(raw_value: str | None) -> Any:
    if not raw_value:
        return {}
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return {}


def _sanitize_payload(value: Any) -> tuple[Any, bool, bool]:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        found_sensitive = False
        found_llm_key = False
        for key, item in value.items():
            lowered_key = str(key).lower()
            key_is_sensitive = any(part in lowered_key for part in SENSITIVE_KEY_PARTS)
            if key_is_sensitive:
                found_sensitive = True
                found_llm_key = any(part in lowered_key for part in LLM_KEY_PARTS)
                continue
            sanitized_item, item_sensitive, item_llm_key = _sanitize_payload(item)
            found_sensitive = found_sensitive or item_sensitive
            found_llm_key = found_llm_key or item_llm_key
            sanitized[key] = sanitized_item
        return sanitized, found_sensitive, found_llm_key
    if isinstance(value, list):
        items = []
        found_sensitive = False
        found_llm_key = False
        for item in value:
            sanitized_item, item_sensitive, item_llm_key = _sanitize_payload(item)
            found_sensitive = found_sensitive or item_sensitive
            found_llm_key = found_llm_key or item_llm_key
            items.append(sanitized_item)
        return items, found_sensitive, found_llm_key
    if isinstance(value, str):
        lowered_value = value.lower()
        value_is_sensitive = any(marker in lowered_value for marker in SENSITIVE_VALUE_MARKERS)
        if value_is_sensitive:
            return "[redacted]", True, any(marker in lowered_value for marker in LLM_KEY_PARTS)
    return value, False, False


def _append_warning(warnings: list[str], warning: str) -> None:
    if warning not in warnings:
        warnings.append(warning)


def _bundle_records(session_id: str, db: Session) -> tuple[EvidenceBundleRecords, EvidenceBundleRedactionFlags, list[str]]:
    warnings: list[str] = ["public evaluator outputs unavailable"]
    found_sensitive_payload = False
    found_llm_key_payload = False

    branches = db.execute(
        select(TimelineBranch)
        .where(TimelineBranch.session_id == session_id)
        .order_by(TimelineBranch.tick, TimelineBranch.branch_name, TimelineBranch.created_at, TimelineBranch.id)
    ).scalars()
    branch_records = [
        {
            "id": branch.id,
            "branch_name": branch.branch_name,
            "commit_point_id": branch.commit_point_id,
            "tick": branch.tick,
            "snapshot_reference": branch.snapshot_reference,
            "is_main": branch.is_main,
            "created_at": branch.created_at.isoformat(),
        }
        for branch in branches
    ]

    branch_names_by_commit: dict[str, list[str]] = {}
    branch_ids_by_commit: dict[str, list[str]] = {}
    for branch in branch_records:
        commit_point_id = branch["commit_point_id"]
        branch_ids_by_commit.setdefault(commit_point_id, []).append(branch["id"])
        branch_names_by_commit.setdefault(commit_point_id, []).append(branch["branch_name"])

    commit_points = db.execute(
        select(CommitPoint)
        .where(CommitPoint.session_id == session_id)
        .order_by(CommitPoint.tick, CommitPoint.created_at, CommitPoint.id)
    ).scalars()
    commit_point_records = [
        {
            "id": commit_point.id,
            "tick": commit_point.tick,
            "event_id": commit_point.event_id,
            "snapshot_id": commit_point.snapshot_id,
            "created_at": commit_point.created_at.isoformat(),
        }
        for commit_point in commit_points
    ]
    replay_index = [
        {
            "commit_point_id": commit_point["id"],
            "tick": commit_point["tick"],
            "event_id": commit_point["event_id"],
            "snapshot_id": commit_point["snapshot_id"],
            "branch_ids": branch_ids_by_commit.get(commit_point["id"], []),
            "branch_names": branch_names_by_commit.get(commit_point["id"], []),
        }
        for commit_point in commit_point_records
    ]

    event_records = []
    for event in db.execute(
        select(Event).where(Event.session_id == session_id).order_by(Event.tick, Event.created_at, Event.id)
    ).scalars():
        payload, has_sensitive, has_llm_key = _sanitize_payload(_load_json(event.payload_json))
        found_sensitive_payload = found_sensitive_payload or has_sensitive
        found_llm_key_payload = found_llm_key_payload or has_llm_key
        event_records.append(
            {
                "id": event.id,
                "branch_id": event.branch_id,
                "tick": event.tick,
                "event_kind": event.event_kind,
                "payload": payload,
                "created_at": event.created_at.isoformat(),
            }
        )

    state_diff_records = []
    for state_diff in db.execute(
        select(StateDiff).where(StateDiff.session_id == session_id).order_by(StateDiff.tick, StateDiff.created_at, StateDiff.id)
    ).scalars():
        diff, has_sensitive, has_llm_key = _sanitize_payload(_load_json(state_diff.diff_json))
        found_sensitive_payload = found_sensitive_payload or has_sensitive
        found_llm_key_payload = found_llm_key_payload or has_llm_key
        state_diff_records.append(
            {
                "id": state_diff.id,
                "branch_id": state_diff.branch_id,
                "tick": state_diff.tick,
                "diff": diff,
                "created_at": state_diff.created_at.isoformat(),
            }
        )

    snapshot_records = []
    for snapshot in db.execute(
        select(Snapshot).where(Snapshot.session_id == session_id).order_by(Snapshot.tick, Snapshot.created_at, Snapshot.id)
    ).scalars():
        payload, has_sensitive, has_llm_key = _sanitize_payload(_load_json(snapshot.snapshot_json))
        found_sensitive_payload = found_sensitive_payload or has_sensitive
        found_llm_key_payload = found_llm_key_payload or has_llm_key
        snapshot_records.append(
            {
                "id": snapshot.id,
                "branch_id": snapshot.branch_id,
                "tick": snapshot.tick,
                "snapshot": payload,
                "created_at": snapshot.created_at.isoformat(),
            }
        )

    director_intent_records = []
    for intent in db.execute(
        select(DirectorIntent)
        .where(DirectorIntent.session_id == session_id)
        .order_by(DirectorIntent.tick, DirectorIntent.created_at, DirectorIntent.id)
    ).scalars():
        instruction_text, instruction_sensitive, instruction_llm_key = _sanitize_payload(intent.instruction_text)
        public_explanation, explanation_sensitive, explanation_llm_key = _sanitize_payload(intent.public_explanation)
        error_message, error_sensitive, error_llm_key = _sanitize_payload(intent.error_message)
        found_sensitive_payload = (
            found_sensitive_payload or instruction_sensitive or explanation_sensitive or error_sensitive
        )
        found_llm_key_payload = found_llm_key_payload or instruction_llm_key or explanation_llm_key or error_llm_key
        director_intent_records.append(
            {
                "id": intent.id,
                "branch_id": intent.branch_id,
                "tick": intent.tick,
                "instruction_text": instruction_text,
                "status": intent.status,
                "public_explanation": public_explanation,
                "applied_event_id": intent.applied_event_id,
                "error_message": error_message,
                "created_at": intent.created_at.isoformat(),
            }
        )

    api_trace_records = []
    for trace in db.execute(
        select(ApiTrace).where(ApiTrace.session_id == session_id).order_by(ApiTrace.created_at, ApiTrace.id)
    ).scalars():
        request_summary, request_sensitive, request_llm_key = _sanitize_payload(_load_json(trace.request_summary_json))
        response_summary, response_sensitive, response_llm_key = _sanitize_payload(_load_json(trace.response_summary_json))
        found_sensitive_payload = found_sensitive_payload or request_sensitive or response_sensitive
        found_llm_key_payload = found_llm_key_payload or request_llm_key or response_llm_key
        api_trace_records.append(
            {
                "method": trace.method,
                "url_path": trace.url_path,
                "status_code": trace.status_code,
                "request_summary": request_summary,
                "response_summary": response_summary,
                "error_message": trace.error_message,
                "llm_keys_included": trace.llm_keys_included,
                "private_worldengine_internals_included": trace.private_worldengine_internals_included,
            }
        )

    if found_sensitive_payload:
        _append_warning(warnings, "sensitive content redacted from evidence records")

    payload_flags = EvidenceBundleRedactionFlags(
        llm_keys_included=found_llm_key_payload,
        private_worldengine_internals_included=found_sensitive_payload,
    )
    records = EvidenceBundleRecords(
        branches=branch_records,
        commit_points=commit_point_records,
        events=event_records,
        state_diffs=state_diff_records,
        snapshots=snapshot_records,
        director_intents=director_intent_records,
        api_traces=api_trace_records,
        evaluator_outputs=[],
        replay_index=replay_index,
    )
    return records, payload_flags, warnings


@router.get("/bundle", response_model=EvidenceBundleMetadata)
def get_bundle(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    counts = _bundle_counts(session_id, db)
    redaction_flags = _redaction_flags(session_id, db)

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
        llm_keys_included=redaction_flags.llm_keys_included,
        private_worldengine_internals_included=redaction_flags.private_worldengine_internals_included,
    )


@router.get("/bundle/manifest", response_model=EvidenceBundleResponse)
def get_bundle_manifest(session_id: str, db: Session = Depends(get_db)):
    return _build_bundle_response(session_id, db)


def _build_bundle_response(session_id: str, db: Session) -> EvidenceBundleResponse:
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    trace_flags = _redaction_flags(session_id, db)
    records, payload_flags, warnings = _bundle_records(session_id, db)
    redaction_flags = EvidenceBundleRedactionFlags(
        llm_keys_included=trace_flags.llm_keys_included or payload_flags.llm_keys_included,
        private_worldengine_internals_included=(
            trace_flags.private_worldengine_internals_included or payload_flags.private_worldengine_internals_included
        ),
    )
    if trace_flags.llm_keys_included or trace_flags.private_worldengine_internals_included:
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

    return EvidenceBundleResponse(manifest=manifest, records=records)


@router.get("/bundle/download")
def download_bundle(session_id: str, db: Session = Depends(get_db)):
    bundle = _build_bundle_response(session_id, db)
    generated_date = bundle.manifest.generated_at.date().isoformat()
    filename = f"evidence-bundle-{session_id}-{generated_date}.json"
    return JSONResponse(
        content=bundle.model_dump(mode="json"),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
