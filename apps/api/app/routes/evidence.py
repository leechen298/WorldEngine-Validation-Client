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
    OperationLogEntry,
    Session as DbSession,
    Snapshot,
    StateDiff,
    TimelineBranch,
    ValidationRun,
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
    "goal",
    "helper",
    "hidden_context",
    "identity",
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
    "relationship",
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
    "helper",
    "internal",
    "/internal",
    "/private",
    "/helper",
    "/helpers",
    "private_path",
    "private_prompt",
    "provider_secret",
    "raw_response",
    "self_state",
    "source_path",
    "password",
    "secret",
    "token",
)

STATUS_VALUES = ["pass", "fail", "blocked", "not_run"]

ARTIFACT_SPECS: dict[str, dict[str, Any]] = {
    "manifest.json": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "result.json": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "operation-log.jsonl": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "api-log.jsonl": {
        "producer": "validation_client",
        "displayable": False,
        "exportable": True,
    },
    "api-summary.json": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "provider-live-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "world-creation-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "world-rule-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "rule-parameter-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "event-legality-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "agent-autonomy-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "diff-replay-summary.json": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "world-lifecycle-summary.json": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "narrative-projection-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "diagnostic-conversation-summary.json": {
        "producer": "worldengine",
        "displayable": True,
        "exportable": True,
    },
    "redaction-scan.json": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "scorecard-summary.json": {
        "producer": "worldengine_checker",
        "displayable": True,
        "exportable": True,
    },
    "second-agent-review.md": {
        "producer": "second_agent_review",
        "displayable": True,
        "exportable": True,
    },
    "transcript.md": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
    "console.log": {
        "producer": "validation_client",
        "displayable": False,
        "exportable": True,
    },
    "screenshots/": {
        "producer": "validation_client",
        "displayable": True,
        "exportable": True,
    },
}

SCENARIO_REQUIRED_ARTIFACTS: dict[str, set[str]] = {
    "provider-live-smoke-deepseek": {
        "manifest.json",
        "result.json",
        "operation-log.jsonl",
        "api-summary.json",
        "provider-live-summary.json",
        "redaction-scan.json",
    },
    "llm-backed-full-lifecycle-autonomous": set(ARTIFACT_SPECS),
    "worldengine-full-lifecycle-autonomous": {
        "manifest.json",
        "result.json",
        "operation-log.jsonl",
        "api-summary.json",
        "world-lifecycle-summary.json",
        "diff-replay-summary.json",
        "redaction-scan.json",
        "scorecard-summary.json",
        "screenshots/",
        "transcript.md",
    },
}


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
        validation_runs=count(ValidationRun),
        operation_log_entries=count(OperationLogEntry),
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
                found_llm_key = found_llm_key or any(part in lowered_key for part in LLM_KEY_PARTS)
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


def _artifact_generated(name: str, counts: EvidenceBundleCounts) -> bool:
    if name == "manifest.json":
        return True
    if name == "api-summary.json":
        return counts.api_traces > 0
    if name == "operation-log.jsonl":
        return counts.operation_log_entries > 0
    if name == "diff-replay-summary.json":
        return counts.commit_points > 0 or counts.state_diffs > 0 or counts.snapshots > 0
    if name == "world-lifecycle-summary.json":
        return counts.events > 0 or counts.snapshots > 0 or counts.api_traces > 0
    if name == "redaction-scan.json":
        return True
    return False


def _build_artifact_index(
    *,
    scenario: str,
    counts: EvidenceBundleCounts,
    redaction_status: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    required_artifacts = SCENARIO_REQUIRED_ARTIFACTS.get(
        scenario,
        SCENARIO_REQUIRED_ARTIFACTS["worldengine-full-lifecycle-autonomous"],
    )
    unsupported_items: list[str] = []
    artifact_index: list[dict[str, Any]] = []
    for name, spec in ARTIFACT_SPECS.items():
        required = name in required_artifacts
        generated = _artifact_generated(name, counts)
        status_value = "pass" if generated else "not_run"
        if required and not generated:
            status_value = "blocked"
            unsupported_items.append(f"required artifact {name} is not generated")
        artifact_index.append(
            {
                "name": name,
                "path": name,
                "required": required,
                "displayable": bool(spec["displayable"]),
                "exportable": bool(spec["exportable"]),
                "producer": str(spec["producer"]),
                "schema_version": "0.8.0",
                "status": status_value,
                "redaction_status": redaction_status["status"],
            }
        )
    return artifact_index, unsupported_items


def _redaction_status(redaction_flags: EvidenceBundleRedactionFlags) -> dict[str, Any]:
    blocking_flags = [
        field
        for field, enabled in redaction_flags.model_dump().items()
        if enabled
    ]
    return {
        "status": "fail" if blocking_flags else "pass",
        "blocking_flags": blocking_flags,
    }


def _result_status(*, redaction_status: dict[str, Any], unsupported_items: list[str]) -> str:
    if redaction_status["status"] == "fail":
        return "fail"
    if unsupported_items:
        return "blocked"
    return "pass"


def _unsupported_for_artifact(name: str, unsupported_items: list[str]) -> list[str]:
    return [item for item in unsupported_items if f" {name} " in f" {item} "]


def _summary_artifact(
    *,
    name: str,
    scenario: str,
    source: str,
    status_value: str,
    redaction_status: dict[str, Any],
    unsupported_items: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failures = _unsupported_for_artifact(name, unsupported_items)
    payload = {
        "schema_version": "0.8.0",
        "scenario": scenario,
        "status": status_value,
        "source": source,
        "redaction": redaction_status,
        "evidence_refs": [],
        "failures": failures,
    }
    if extra:
        payload.update(extra)
    return payload


def _build_named_artifacts(bundle: EvidenceBundleResponse) -> dict[str, Any]:
    manifest = bundle.manifest
    artifact_status = {item["name"]: item["status"] for item in manifest.artifact_index}
    unsupported_items = manifest.unsupported_items
    redaction_status = manifest.redaction_status
    scenario = manifest.scenario
    counts = manifest.counts

    artifacts: dict[str, Any] = {
        "manifest.json": manifest.model_dump(mode="json"),
        "result.json": {
            "schema_version": "0.8.0",
            "scenario": scenario,
            "status": manifest.result_status,
            "client_role": manifest.client_role,
            "provider_owner": manifest.provider_owner,
            "evaluator_role": manifest.evaluator_role,
            "unsupported_items": unsupported_items,
            "checker_contract": manifest.checker_contract,
            "redaction": redaction_status,
        },
        "operation-log.jsonl": bundle.records.operation_log_entries,
        "api-log.jsonl": bundle.records.api_traces,
        "api-summary.json": {
            "schema_version": "0.8.0",
            "scenario": scenario,
            "status": artifact_status.get("api-summary.json", "not_run"),
            "api_trace_count": counts.api_traces,
            "redaction": redaction_status,
        },
        "provider-live-summary.json": _summary_artifact(
            name="provider-live-summary.json",
            scenario=scenario,
            source="worldengine_public_endpoint",
            status_value=artifact_status.get("provider-live-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
            extra={
                "worldengine_owned_call": True,
                "call_attempted": False,
                "public_failure_category": (
                    _unsupported_for_artifact("provider-live-summary.json", unsupported_items) or [None]
                )[0],
            },
        ),
        "world-creation-summary.json": _summary_artifact(
            name="world-creation-summary.json",
            scenario=scenario,
            source="worldengine_public_evidence",
            status_value=artifact_status.get("world-creation-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
        ),
        "world-rule-summary.json": _summary_artifact(
            name="world-rule-summary.json",
            scenario=scenario,
            source="worldengine_public_evidence",
            status_value=artifact_status.get("world-rule-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
        ),
        "rule-parameter-summary.json": _summary_artifact(
            name="rule-parameter-summary.json",
            scenario=scenario,
            source="worldengine_public_evidence",
            status_value=artifact_status.get("rule-parameter-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
        ),
        "event-legality-summary.json": _summary_artifact(
            name="event-legality-summary.json",
            scenario=scenario,
            source="worldengine_public_evidence",
            status_value=artifact_status.get("event-legality-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
        ),
        "agent-autonomy-summary.json": _summary_artifact(
            name="agent-autonomy-summary.json",
            scenario=scenario,
            source="worldengine_public_evidence",
            status_value=artifact_status.get("agent-autonomy-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
        ),
        "diff-replay-summary.json": {
            "schema_version": "0.8.0",
            "scenario": scenario,
            "status": artifact_status.get("diff-replay-summary.json", "not_run"),
            "source": "validation_client",
            "events_ref": "records.events",
            "snapshots_ref": "records.snapshots",
            "diffs_ref": "records.state_diffs",
            "replay_supported": counts.commit_points > 0,
            "state_jump_targets": [item["commit_point_id"] for item in bundle.records.replay_index],
            "missing_replay_links": [],
            "redaction": redaction_status,
        },
        "world-lifecycle-summary.json": {
            "schema_version": "0.8.0",
            "scenario": scenario,
            "status": artifact_status.get("world-lifecycle-summary.json", "not_run"),
            "source": "validation_client",
            "session_id": manifest.session_id,
            "worldengine_world_id": manifest.worldengine_world_id,
            "world_status": manifest.world_status,
            "counts": counts.model_dump(mode="json"),
            "redaction": redaction_status,
        },
        "narrative-projection-summary.json": _summary_artifact(
            name="narrative-projection-summary.json",
            scenario=scenario,
            source="worldengine_public_projection",
            status_value=artifact_status.get("narrative-projection-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
        ),
        "diagnostic-conversation-summary.json": _summary_artifact(
            name="diagnostic-conversation-summary.json",
            scenario=scenario,
            source="worldengine_public_projection",
            status_value=artifact_status.get("diagnostic-conversation-summary.json", "not_run"),
            redaction_status=redaction_status,
            unsupported_items=unsupported_items,
        ),
        "redaction-scan.json": {
            "schema_version": "0.8.0",
            "scenario": scenario,
            "status": redaction_status["status"],
            "blocking_flags": redaction_status["blocking_flags"],
        },
        "scorecard-summary.json": {
            "schema_version": "0.8.0",
            "scenario": scenario,
            "status": artifact_status.get("scorecard-summary.json", "not_run"),
            "verdict_source": "worldengine_checker",
            "score_items": [],
            "critical_failures": unsupported_items if manifest.result_status != "pass" else [],
            "unverified_items": unsupported_items,
            "final_status": manifest.result_status,
        },
        "second-agent-review.md": {
            "status": artifact_status.get("second-agent-review.md", "not_run"),
            "summary": "Second-Agent review has not run in this bundle.",
        },
        "transcript.md": {
            "status": artifact_status.get("transcript.md", "not_run"),
            "summary": "Transcript has not been generated.",
        },
        "console.log": {
            "status": artifact_status.get("console.log", "not_run"),
            "summary": "Console log has not been generated.",
        },
        "screenshots/": {
            "status": artifact_status.get("screenshots/", "not_run"),
            "summary": "Screenshots have not been generated.",
        },
    }
    return artifacts


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
        url_path, url_sensitive, url_llm_key = _sanitize_payload(trace.url_path)
        error_message, error_sensitive, error_llm_key = _sanitize_payload(trace.error_message)
        found_sensitive_payload = (
            found_sensitive_payload or request_sensitive or response_sensitive or url_sensitive or error_sensitive
        )
        found_llm_key_payload = (
            found_llm_key_payload or request_llm_key or response_llm_key or url_llm_key or error_llm_key
        )
        api_trace_records.append(
            {
                "method": trace.method,
                "url_path": url_path,
                "status_code": trace.status_code,
                "request_summary": request_summary,
                "response_summary": response_summary,
                "error_message": error_message,
                "llm_keys_included": trace.llm_keys_included or request_llm_key or response_llm_key or url_llm_key or error_llm_key,
                "private_worldengine_internals_included": (
                    trace.private_worldengine_internals_included
                    or request_sensitive
                    or response_sensitive
                    or url_sensitive
                    or error_sensitive
                ),
            }
        )

    validation_run_records = []
    for run in db.execute(
        select(ValidationRun).where(ValidationRun.session_id == session_id).order_by(ValidationRun.created_at, ValidationRun.id)
    ).scalars():
        validation_run_records.append(
            {
                "id": run.id,
                "actor": run.actor,
                "status": run.status,
                "web_url": run.web_url,
                "api_base_url": run.api_base_url,
                "worldengine_api_base": run.worldengine_api_base,
                "evidence_bundle_path": run.evidence_bundle_path,
                "notes": run.notes,
                "created_at": run.created_at.isoformat(),
                "updated_at": run.updated_at.isoformat(),
            }
        )

    operation_log_records = []
    for entry in db.execute(
        select(OperationLogEntry)
        .where(OperationLogEntry.session_id == session_id)
        .order_by(OperationLogEntry.created_at, OperationLogEntry.id)
    ).scalars():
        operation_log_records.append(
            {
                "id": entry.id,
                "run_id": entry.run_id,
                "timestamp": entry.created_at.isoformat(),
                "actor": entry.actor,
                "phase": entry.phase,
                "url": entry.url,
                "action_type": entry.action_type,
                "target_label": entry.target_label,
                "input_text": entry.input_text,
                "request_method": entry.request_method,
                "request_path": entry.request_path,
                "response_status": entry.response_status,
                "response_summary": entry.response_summary,
                "visible_result": entry.visible_result,
                "screenshot_path": entry.screenshot_path,
                "downloaded_file": entry.downloaded_file,
                "notes": entry.notes,
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
        validation_runs=validation_run_records,
        operation_log_entries=operation_log_records,
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
def get_bundle_manifest(
    session_id: str,
    scenario: str = "worldengine-full-lifecycle-autonomous",
    db: Session = Depends(get_db),
):
    return _build_bundle_response(session_id, db, scenario=scenario)


@router.get("/bundle/artifacts")
def get_bundle_artifacts(
    session_id: str,
    scenario: str = "worldengine-full-lifecycle-autonomous",
    db: Session = Depends(get_db),
):
    bundle = _build_bundle_response(session_id, db, scenario=scenario)
    return JSONResponse(content=_build_named_artifacts(bundle), media_type="application/json")


def _build_bundle_response(
    session_id: str,
    db: Session,
    *,
    scenario: str = "worldengine-full-lifecycle-autonomous",
) -> EvidenceBundleResponse:
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
    latest_run = (
        db.execute(
            select(ValidationRun)
            .where(ValidationRun.session_id == session_id)
            .order_by(ValidationRun.created_at.desc(), ValidationRun.id.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )

    counts = _bundle_counts(session_id, db)
    redaction_status = _redaction_status(redaction_flags)
    artifact_index, unsupported_items = _build_artifact_index(
        scenario=scenario,
        counts=counts,
        redaction_status=redaction_status,
    )

    manifest = EvidenceBundleManifest(
        bundle_schema_version="0.7.0",
        schema_version="0.8.0",
        bundle_id=f"v0.8-{session.id}",
        scenario=scenario,
        result_status=_result_status(redaction_status=redaction_status, unsupported_items=unsupported_items),
        client_role="display_export_only",
        provider_owner="worldengine",
        evaluator_role="worldengine_checker_or_second_agent_review",
        generated_at=datetime.now(UTC),
        session_id=session.id,
        session_name=session.session_name,
        worldengine_world_id=session.worldengine_world_id,
        world_status=session.public_world_status or session.status,
        latest_validation_run_id=latest_run.id if latest_run else None,
        evidence_bundle_filename=f"evidence-bundle-{session_id}.json",
        counts=counts,
        redaction_flags=redaction_flags,
        redaction_status=redaction_status,
        artifact_index=artifact_index,
        checker_contract={
            "scenario": scenario,
            "status_values": STATUS_VALUES,
            "pass_source": "worldengine_checker_or_second_agent_review",
        },
        unsupported_items=unsupported_items,
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
