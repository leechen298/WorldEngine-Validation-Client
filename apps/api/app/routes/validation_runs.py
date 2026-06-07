import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ApiTrace, OperationLogEntry, Session as DbSession, ValidationRun
from ..schemas import (
    ApiSummaryItem,
    OperationLogCreatePayload,
    OperationLogListResponse,
    OperationLogResponse,
    ValidationRunApiSummaryResponse,
    ValidationRunCreatePayload,
    ValidationRunResponse,
)
from .evidence import _sanitize_payload

router = APIRouter(prefix="/validation-runs", tags=["validation-runs"])

FORBIDDEN_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "hidden_context",
    "private prompt",
    "private_prompt",
    "private filesystem",
    "private memory",
    "private goal",
    "provider raw trace",
    "provider secret",
    "raw_response",
    "self_state",
    "source_path",
    "password",
    "secret",
    "token",
)


def _json_or_empty(raw_value: str | None) -> dict[str, Any]:
    if not raw_value:
        return {}
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _sanitize_summary(value: Any) -> Any:
    sanitized, _found_sensitive, _found_llm_key = _sanitize_payload(value)
    return sanitized


def _contains_forbidden(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, dict):
        return any(_contains_forbidden(key) or _contains_forbidden(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    lowered = str(value).lower()
    return any(marker in lowered for marker in FORBIDDEN_MARKERS)


def _reject_forbidden_log_payload(payload: OperationLogCreatePayload) -> None:
    values = payload.model_dump()
    if _contains_forbidden(values):
        raise HTTPException(
            status_code=422,
            detail="Operation log contains forbidden private or secret content",
        )


def _run_response(run: ValidationRun) -> ValidationRunResponse:
    return ValidationRunResponse(
        id=run.id,
        session_id=run.session_id,
        actor=run.actor,
        status=run.status,
        web_url=run.web_url,
        api_base_url=run.api_base_url,
        worldengine_api_base=run.worldengine_api_base,
        evidence_bundle_path=run.evidence_bundle_path,
        notes=run.notes,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


def _entry_response(entry: OperationLogEntry) -> OperationLogResponse:
    return OperationLogResponse(
        id=entry.id,
        run_id=entry.run_id,
        session_id=entry.session_id,
        timestamp=entry.created_at,
        actor=entry.actor,
        phase=entry.phase,
        url=entry.url,
        action_type=entry.action_type,
        target_label=entry.target_label,
        input_text=entry.input_text,
        request_method=entry.request_method,
        request_path=entry.request_path,
        response_status=entry.response_status,
        response_summary=entry.response_summary,
        visible_result=entry.visible_result,
        screenshot_path=entry.screenshot_path,
        downloaded_file=entry.downloaded_file,
        notes=entry.notes,
    )


def _load_run(run_id: str, db: Session) -> ValidationRun:
    run = db.get(ValidationRun, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation run not found")
    return run


@router.post("", response_model=ValidationRunResponse, status_code=status.HTTP_201_CREATED)
def create_validation_run(payload: ValidationRunCreatePayload, db: Session = Depends(get_db)):
    session = db.get(DbSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if _contains_forbidden(payload.model_dump()):
        raise HTTPException(
            status_code=422,
            detail="Validation run contains forbidden private or secret content",
        )

    run = ValidationRun(
        session_id=session.id,
        actor=payload.actor,
        status="running",
        web_url=payload.web_url,
        api_base_url=payload.api_base_url,
        worldengine_api_base=payload.worldengine_api_base,
        notes=payload.notes,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return _run_response(run)


@router.post("/{run_id}/operation-log", response_model=OperationLogResponse, status_code=status.HTTP_201_CREATED)
def append_operation_log(run_id: str, payload: OperationLogCreatePayload, db: Session = Depends(get_db)):
    run = _load_run(run_id, db)
    _reject_forbidden_log_payload(payload)
    entry = OperationLogEntry(
        run_id=run.id,
        session_id=run.session_id,
        actor=payload.actor,
        phase=payload.phase,
        url=payload.url,
        action_type=payload.action_type,
        target_label=payload.target_label,
        input_text=payload.input_text,
        request_method=payload.request_method.upper() if payload.request_method else None,
        request_path=payload.request_path,
        response_status=payload.response_status,
        response_summary=payload.response_summary,
        visible_result=payload.visible_result,
        screenshot_path=payload.screenshot_path,
        downloaded_file=payload.downloaded_file,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _entry_response(entry)


@router.get("/{run_id}/operation-log", response_model=OperationLogListResponse)
def list_operation_log(run_id: str, db: Session = Depends(get_db)):
    run = _load_run(run_id, db)
    entries = (
        db.execute(
            select(OperationLogEntry)
            .where(OperationLogEntry.run_id == run.id)
            .order_by(OperationLogEntry.created_at, OperationLogEntry.id)
        )
        .scalars()
        .all()
    )
    return OperationLogListResponse(
        run_id=run.id,
        session_id=run.session_id,
        entries=[_entry_response(entry) for entry in entries],
    )


@router.get("/{run_id}/operation-log.jsonl")
def download_operation_log_jsonl(run_id: str, db: Session = Depends(get_db)):
    run = _load_run(run_id, db)
    entries = list_operation_log(run_id, db).entries
    lines = [
        json.dumps(entry.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
        for entry in entries
    ]
    filename = f"agent-run-{run.id}.jsonl"
    return Response(
        content=("\n".join(lines) + ("\n" if lines else "")),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{run_id}/api-summary", response_model=ValidationRunApiSummaryResponse)
def get_api_summary(run_id: str, db: Session = Depends(get_db)):
    run = _load_run(run_id, db)
    traces = (
        db.execute(select(ApiTrace).where(ApiTrace.session_id == run.session_id).order_by(ApiTrace.created_at, ApiTrace.id))
        .scalars()
        .all()
    )
    api_calls = [
        ApiSummaryItem(
            method=trace.method,
            path=_sanitize_summary(trace.url_path),
            status=trace.status_code,
            public_summary=_sanitize_summary(_json_or_empty(trace.response_summary_json)),
            error_class=trace.error_message.split(":", 1)[0] if trace.error_message else None,
        )
        for trace in traces
    ]
    return ValidationRunApiSummaryResponse(run_id=run.id, session_id=run.session_id, api_calls=api_calls)


@router.get("/{run_id}/api-summary/download")
def download_api_summary(run_id: str, db: Session = Depends(get_db)):
    summary = get_api_summary(run_id, db)
    filename = f"api-summary-{run_id}.json"
    return JSONResponse(
        content=summary.model_dump(mode="json"),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
