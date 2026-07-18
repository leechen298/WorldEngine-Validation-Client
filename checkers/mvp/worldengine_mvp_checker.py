from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import shutil
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional
from urllib.parse import urlparse

from PIL import Image


CONTRACT_VERSION = "worldengine-godot-mvp-1"
PRODUCER = "worldengine-independent-checker"
EXECUTOR_PRODUCER = "godot-executor"
MAX_CHALLENGE_AGE_SECONDS = 900
FORBIDDEN_MARKERS = (
    "api_key",
    "authorization",
    "bearer ",
    "chain_of_thought",
    "chain-of-thought",
    "private_memory",
    "private_prompt",
    "provider_trace",
    "raw_prompt",
    "raw_provider",
    "sk-live-",
    "sk-test-",
)
REQUEST_SUFFIXES = {
    "package_create": "package",
    "package_repeat": "package-repeat",
    "session_create": "session",
    "direction_accept": "direction-accept",
    "direction_reject": "direction-reject",
    "step": "step",
    "action": "action",
    "feedback": "feedback",
    "step_after_feedback": "step-after-feedback",
}


class CheckFailure(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class VerificationResult:
    run_id: str
    session_id: str
    checks: Mapping[str, bool]
    input_seal_sha256: str


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CheckFailure("missing_file", f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CheckFailure("invalid_json", f"Invalid JSON in {path}: {exc}") from exc


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _safe_child(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise CheckFailure("unsafe_path", f"Path escapes run directory: {relative}")
    return candidate


def _validate_base_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise CheckFailure("invalid_base_url", "Challenge API base must be HTTP(S)")
    if parsed.username or parsed.password:
        raise CheckFailure("invalid_base_url", "Challenge API base cannot contain credentials")
    return value.rstrip("/")


def _default_scenario_path() -> Path:
    return Path(__file__).resolve().parents[2] / "contracts" / "mvp" / "scenario.json"


def prepare_run(
    output_root: Path,
    base_url: str,
    registry_path: Path,
    *,
    run_id: Optional[str] = None,
    now: Optional[int] = None,
) -> Path:
    timestamp = int(time.time() if now is None else now)
    actual_run_id = run_id or (
        time.strftime("run-%Y%m%dT%H%M%SZ", time.gmtime(timestamp))
        + "-"
        + secrets.token_hex(4)
    )
    if "/" in actual_run_id or "\\" in actual_run_id or actual_run_id in {".", ".."}:
        raise CheckFailure("invalid_run_id", "run_id must be one safe path segment")
    registry = _load_registry(registry_path)
    if (
        actual_run_id in registry["issued"]
        or actual_run_id in registry["consumed"]
    ):
        raise CheckFailure("reused_run_id", "Run id has already been issued or consumed")
    actual_base_url = _validate_base_url(base_url)
    run_dir = output_root / actual_run_id
    if run_dir.exists():
        raise CheckFailure("run_directory_exists", f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    nonce = secrets.token_hex(32)
    challenge = {
        "contract_version": CONTRACT_VERSION,
        "run_id": actual_run_id,
        "nonce": nonce,
        "created_at_epoch": timestamp,
        "expires_at_epoch": timestamp + MAX_CHALLENGE_AGE_SECONDS,
        "worldengine_api_base": actual_base_url,
    }
    _write_json(run_dir / "challenge.json", challenge)
    registry["issued"][actual_run_id] = {
        "nonce_sha256": _sha256_bytes(nonce.encode("utf-8")),
        "created_at_epoch": timestamp,
        "expires_at_epoch": timestamp + MAX_CHALLENGE_AGE_SECONDS,
        "worldengine_api_base": actual_base_url,
    }
    _save_registry(registry_path, registry)
    return run_dir


def _load_operations(run_dir: Path) -> List[Dict[str, Any]]:
    path = run_dir / "executor" / "raw" / "operations.jsonl"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise CheckFailure("missing_operations", "Missing executor operations.jsonl") from exc
    records: List[Dict[str, Any]] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CheckFailure(
                "invalid_operation_record",
                f"operations.jsonl line {index} is invalid JSON",
            ) from exc
        if not isinstance(value, dict):
            raise CheckFailure(
                "invalid_operation_record",
                f"operations.jsonl line {index} is not an object",
            )
        records.append(value)
    return records


def _response_payloads(
    run_dir: Path,
    records: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    payloads: Dict[str, Any] = {}
    for expected_sequence, record in enumerate(records, start=1):
        if record.get("sequence") != expected_sequence:
            raise CheckFailure("operation_sequence", "Operation sequence is not contiguous")
        if record.get("producer") != EXECUTOR_PRODUCER:
            raise CheckFailure("executor_producer", "Operation producer is not Godot")
        if record.get("status_code") != 200:
            raise CheckFailure(
                "http_status",
                f"{record.get('label')} returned HTTP {record.get('status_code')}",
            )
        response_path = _safe_child(run_dir, str(record.get("response_file", "")))
        if not response_path.is_file():
            raise CheckFailure("missing_response", f"Missing response: {response_path}")
        actual_hash = _sha256_file(response_path)
        if actual_hash != record.get("response_sha256"):
            raise CheckFailure(
                "response_hash_mismatch",
                f"Response hash mismatch for {record.get('label')}",
            )
        body = _read_json(response_path)
        if not isinstance(body, dict) or body.get("code") != 0 or "data" not in body:
            raise CheckFailure(
                "worldengine_response",
                f"{record.get('label')} is not a successful WorldEngine response",
            )
        label = str(record.get("label", ""))
        if label in payloads:
            raise CheckFailure("duplicate_operation_label", f"Duplicate label: {label}")
        payloads[label] = body["data"]
    return payloads


def _fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise CheckFailure("worldengine_fetch_failed", f"Cannot fetch {url}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("code") != 0 or "data" not in payload:
        raise CheckFailure("worldengine_fetch_invalid", f"Invalid response from {url}")
    return payload["data"]


def _operation_path(manifest: Mapping[str, Any], operation_id: str, session_id: str) -> str:
    operations = {
        item.get("operation_id"): item
        for item in manifest.get("operations", [])
        if isinstance(item, dict)
    }
    operation = operations.get(operation_id)
    if not operation:
        raise CheckFailure("capability_missing", f"Missing operation: {operation_id}")
    return str(operation["path"]).replace("{session_id}", session_id)


def _validate_png(path: Path) -> None:
    if not path.is_file():
        raise CheckFailure("missing_frame", f"Missing visual frame: {path}")
    try:
        with Image.open(path) as image:
            image.load()
            width, height = image.size
            colors = image.convert("RGB").getcolors(maxcolors=width * height)
    except Exception as exc:
        raise CheckFailure("invalid_frame", f"Cannot read PNG frame {path}: {exc}") from exc
    if width < 640 or height < 360:
        raise CheckFailure("frame_size", f"Frame is too small: {width}x{height}")
    if colors is None or len(colors) < 8:
        raise CheckFailure("blank_frame", f"Frame does not contain enough visual variation: {path}")


def _scan_forbidden(root: Path, files: Iterable[Path]) -> None:
    for path in files:
        if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".txt", ".log"}:
            continue
        value = path.read_text(encoding="utf-8", errors="replace").casefold()
        for marker in FORBIDDEN_MARKERS:
            if marker in value:
                relative = path.resolve().relative_to(root.resolve())
                raise CheckFailure(
                    "sensitive_marker",
                    f"Sensitive marker {marker!r} found in {relative}",
                )


def _scan_public_value(value: Any, source: str) -> None:
    text = json.dumps(value, ensure_ascii=True, sort_keys=True).casefold()
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            raise CheckFailure(
                "sensitive_marker",
                f"Sensitive marker {marker!r} found in {source}",
            )


def _validate_evidence(
    evidence: Mapping[str, Any],
    *,
    run_id: str,
    session_id: str,
    package_hash: str,
    final_tick: int,
    feedback_decision_mode: str,
    accepted_request_id: str,
    rejected_request_id: str,
    expected_request_ids: Mapping[str, str],
) -> None:
    projection = evidence.get("projection", {})
    if projection.get("session_id") != session_id:
        raise CheckFailure("cross_session_evidence", "Evidence session does not match executor")
    package = evidence.get("package", {})
    if (
        package.get("package_hash") != package_hash
        or projection.get("source_package_hash") != package_hash
    ):
        raise CheckFailure(
            "package_evidence_binding",
            "Fresh evidence is not bound to the package created in this run",
        )
    if package.get("brief", {}).get("seed") != f"godot-{run_id}":
        raise CheckFailure(
            "run_evidence_binding",
            "Fresh evidence package seed is not bound to this challenge",
        )
    if projection.get("tick") != final_tick:
        raise CheckFailure("unexpected_tick", "Final projection tick does not match scenario")
    events = evidence.get("events", [])
    sequences = [item.get("sequence") for item in events]
    if sequences != list(range(1, len(events) + 1)):
        raise CheckFailure("event_sequence", "Event sequence is not contiguous and monotonic")
    if projection.get("event_cursor") != len(events):
        raise CheckFailure("event_cursor", "Projection event cursor does not match event stream")
    diffs = evidence.get("diffs", [])
    if not diffs:
        raise CheckFailure("missing_diffs", "Evidence contains no state diffs")
    for previous, current in zip(diffs, diffs[1:]):
        if previous.get("state_hash_after") != current.get("state_hash_before"):
            raise CheckFailure("diff_hash_chain", "Diff state hash chain is broken")
    if diffs[-1].get("state_hash_after") != projection.get("state_hash"):
        raise CheckFailure("final_state_hash", "Final diff hash does not match projection")
    cycles = evidence.get("agent_cycles", [])
    if len(cycles) < final_tick:
        raise CheckFailure("agent_cycle_count", "Not enough Agent cycles")
    feedback_cycle = cycles[-1]
    prior_cycle = cycles[-2]
    if not feedback_cycle.get("experience_refs_used"):
        raise CheckFailure("agent_continuity", "Later Agent cycle did not use experience")
    feedback_decision = feedback_cycle.get("decision", {})
    if feedback_decision.get("decision_mode") != feedback_decision_mode:
        raise CheckFailure("agent_feedback", "Agent decision did not incorporate feedback")
    if (
        feedback_cycle.get("perception", {}).get("feedback_count", 0) < 1
        or feedback_decision.get("feedback_count", 0) < 1
        or "feedback_count" not in feedback_decision.get("influence_factors", [])
        or feedback_cycle.get("action_request", {}).get("amount")
        == prior_cycle.get("action_request", {}).get("amount")
    ):
        raise CheckFailure("agent_feedback_effect", "Feedback did not change the next action")
    if feedback_cycle.get("action_result", {}).get("status") != "accepted":
        raise CheckFailure("agent_action", "Agent action was not accepted")
    decisions = {
        item.get("request_id"): item for item in evidence.get("direction_decisions", [])
    }
    accepted = decisions.get(accepted_request_id)
    rejected = decisions.get(rejected_request_id)
    if not accepted or accepted.get("status") != "accepted":
        raise CheckFailure("direction_accept", "Bounded direction was not accepted")
    if (
        accepted.get("application_status") != "applied"
        or accepted.get("application_reason_code") != "direction_applied"
        or accepted.get("queued")
        or not accepted.get("application_event_refs")
        or not accepted.get("applied_diff_refs")
    ):
        raise CheckFailure("direction_application", "Accepted direction was not applied later")
    if (
        not rejected
        or rejected.get("status") != "rejected"
        or rejected.get("reason_code") != "direct_final_fact_forbidden"
        or rejected.get("applied_diff_refs")
    ):
        raise CheckFailure("direction_reject", "Direct final fact rejection is invalid")
    correlations = {
        (item.get("operation_id"), item.get("request_id")): item
        for item in evidence.get("request_correlations", [])
        if isinstance(item, dict)
    }
    expected_correlations = {
        "session_create": ("sessions.create", "accepted", False),
        "direction_accept": ("directions.submit", "accepted", True),
        "direction_reject": ("directions.submit", "rejected", False),
        "step": ("sessions.step", "completed", True),
        "action": ("actions.submit", "accepted", True),
        "feedback": ("feedback.submit", "accepted", True),
        "step_after_feedback": ("sessions.step", "completed", True),
    }
    for label, (operation_id, status, requires_diff) in expected_correlations.items():
        correlation = correlations.get((operation_id, expected_request_ids[label]))
        if (
            not correlation
            or correlation.get("status") != status
            or not correlation.get("event_refs")
            or (requires_diff and not correlation.get("diff_refs"))
        ):
            raise CheckFailure(
                "run_request_correlation",
                f"Fresh evidence is missing the challenge-bound request: {label}",
            )
    accepted_correlation = correlations.get(("directions.submit", accepted_request_id))
    if (
        not accepted_correlation
        or accepted_correlation.get("status") != "accepted"
        or accepted_correlation.get("application_status") != "applied"
        or accepted_correlation.get("event_refs")
        != [accepted.get("event_ref"), *accepted.get("application_event_refs", [])]
        or accepted_correlation.get("diff_refs") != accepted.get("applied_diff_refs")
    ):
        raise CheckFailure("direction_correlation", "Applied direction correlation is invalid")
    completeness = evidence.get("completeness", {})
    integrity = completeness.get("integrity", {})
    if integrity.get("status") != "valid":
        raise CheckFailure("evidence_incomplete", "WorldEngine evidence integrity is incomplete")
    if not integrity.get("checks") or not all(integrity["checks"].values()):
        raise CheckFailure("evidence_checks", "WorldEngine evidence checks are not all true")
    coverage = completeness.get("scenario_coverage", {})
    coverage_checks = coverage.get("checks", {})
    if coverage.get("status") != "covered":
        raise CheckFailure("scenario_coverage", "WorldEngine scenario is not fully covered")
    for key in (
        "action",
        "feedback",
        "agent",
        "direction",
        "agent_experience",
        "agent_feedback_influence",
        "accepted_direction_applied",
        "semantic_direction_rejection",
        "same_intervention_window",
    ):
        if not coverage_checks.get(key):
            raise CheckFailure("scenario_coverage", f"Missing scenario coverage: {key}")


def _load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"issued": {}, "consumed": []}
    value = _read_json(path)
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("issued"), dict)
        or not isinstance(value.get("consumed"), list)
        or not all(isinstance(item, str) for item in value["consumed"])
    ):
        raise CheckFailure("invalid_registry", "Consumed-run registry is invalid")
    return value


def _save_registry(path: Path, value: Mapping[str, Any]) -> None:
    normalized = {
        "issued": dict(value["issued"]),
        "consumed": sorted(set(value["consumed"])),
    }
    _write_json(path, normalized)


def verify_run(
    run_dir: Path,
    registry_path: Path,
    *,
    scenario_path: Optional[Path] = None,
    now: Optional[int] = None,
    fetch_json: Callable[[str], Any] = _fetch_json,
    write_outputs: bool = True,
) -> VerificationResult:
    run_dir = run_dir.resolve()
    scenario = _read_json(scenario_path or _default_scenario_path())
    challenge = _read_json(run_dir / "challenge.json")
    summary = _read_json(run_dir / "executor" / "summary.json")
    current_time = int(time.time() if now is None else now)

    if challenge.get("contract_version") != CONTRACT_VERSION:
        raise CheckFailure("contract_version", "Challenge contract version is unsupported")
    run_id = str(challenge.get("run_id", ""))
    if run_dir.name != run_id:
        raise CheckFailure("run_directory_identity", "Run directory name does not match run id")
    created_at = challenge.get("created_at_epoch")
    expires_at = challenge.get("expires_at_epoch")
    if not isinstance(created_at, int) or not isinstance(expires_at, int):
        raise CheckFailure("challenge_time", "Challenge time fields are invalid")
    if current_time < created_at - 30 or current_time > expires_at:
        raise CheckFailure("stale_challenge", "Challenge is not inside its validity window")
    checker_dir = run_dir / "checker"
    if checker_dir.exists():
        raise CheckFailure("prewritten_verdict", "Checker output exists before verification")
    registry = _load_registry(registry_path)
    if run_id in registry["consumed"]:
        raise CheckFailure("reused_run_id", "Run id has already been consumed")
    issued = registry["issued"].get(run_id)
    if not issued:
        raise CheckFailure("unissued_challenge", "Challenge was not issued by this checker")
    if (
        issued.get("nonce_sha256")
        != _sha256_bytes(str(challenge.get("nonce", "")).encode("utf-8"))
        or issued.get("created_at_epoch") != created_at
        or issued.get("expires_at_epoch") != expires_at
        or issued.get("worldengine_api_base")
        != challenge.get("worldengine_api_base")
    ):
        raise CheckFailure("challenge_registry_binding", "Challenge does not match checker state")

    if summary.get("contract_version") != CONTRACT_VERSION:
        raise CheckFailure("summary_contract", "Executor summary contract is invalid")
    if summary.get("producer") != EXECUTOR_PRODUCER:
        raise CheckFailure("summary_producer", "Executor summary producer is invalid")
    if summary.get("outcome") != "completed":
        raise CheckFailure("executor_incomplete", "Executor did not complete the scenario")
    if summary.get("run_id") != run_id or summary.get("nonce") != challenge.get("nonce"):
        raise CheckFailure("challenge_binding", "Executor output is not bound to the challenge")
    forbidden_summary_keys = {"verdict", "classification", "passed", "failed", "score"}
    if forbidden_summary_keys.intersection(summary):
        raise CheckFailure("executor_verdict", "Executor summary contains verdict fields")

    records = _load_operations(run_dir)
    expected = scenario.get("required_operations", [])
    if len(records) != len(expected):
        raise CheckFailure("operation_count", "Executor operation count is incomplete")
    for record, operation in zip(records, expected):
        if record.get("label") != operation.get("label"):
            raise CheckFailure("operation_order", "Executor operation labels are out of order")
        if record.get("operation_id") != operation.get("operation_id"):
            raise CheckFailure("operation_id", "Executor operation id does not match contract")
    expected_request_ids = {
        label: f"{run_id}-{suffix}" for label, suffix in REQUEST_SUFFIXES.items()
    }
    for record in records:
        label = str(record.get("label", ""))
        expected_request_id = expected_request_ids.get(label)
        if record.get("request_id") != expected_request_id:
            raise CheckFailure(
                "operation_request_binding",
                f"Operation request id is not bound to this challenge: {label}",
            )
    if summary.get("operation_count") != len(records):
        raise CheckFailure("summary_operation_count", "Summary operation count is inconsistent")
    payloads = _response_payloads(run_dir, records)

    base_url = _validate_base_url(str(challenge.get("worldengine_api_base", "")))
    fresh_manifest = fetch_json(base_url + "/api/v1/capabilities")
    if fresh_manifest.get("contract_version") != scenario.get(
        "worldengine_contract_version"
    ):
        raise CheckFailure("worldengine_contract", "WorldEngine contract version is unexpected")
    raw_manifest = payloads["capabilities"]
    if raw_manifest.get("instance_id") != fresh_manifest.get("instance_id"):
        raise CheckFailure("worldengine_instance", "WorldEngine instance changed during validation")

    package = payloads["package_create"]
    repeated_package = payloads["package_repeat"]
    if (
        package.get("readiness", {}).get("status") != "ready"
        or package.get("package_hash") != repeated_package.get("package_hash")
        or package.get("brief", {}).get("seed") != f"godot-{run_id}"
    ):
        raise CheckFailure("package_determinism", "Runnable package is not ready/deterministic")
    session = payloads["session_create"]
    session_id = str(session.get("session_id", ""))
    if not session_id or summary.get("session_id") != session_id:
        raise CheckFailure("session_identity", "Executor summary session id is inconsistent")
    if session.get("source_package_hash") != package.get("package_hash"):
        raise CheckFailure("session_package_hash", "Session source package hash is invalid")

    accepted = payloads["direction_accept"]
    rejected = payloads["direction_reject"]
    if accepted.get("status") != "accepted" or not accepted.get("queued"):
        raise CheckFailure("direction_accept", "Bounded direction was not queued")
    if (
        rejected.get("status") != "rejected"
        or rejected.get("reason_code") != "direct_final_fact_forbidden"
        or rejected.get("applied_diff_refs")
    ):
        raise CheckFailure("direction_reject", "Direct final fact was not safely rejected")
    stepped = payloads["step"]
    initial_steps = int(scenario.get("initial_step_count", 0))
    if (
        stepped.get("start_tick") != 0
        or stepped.get("end_tick") != initial_steps
        or stepped.get("step_count") != initial_steps
    ):
        raise CheckFailure("exact_step", "WorldEngine did not advance the initial tick count")
    if payloads["action"].get("status") != "accepted":
        raise CheckFailure("client_action", "Client action was not accepted")
    if (
        payloads["feedback"].get("status") != "accepted"
        or payloads["feedback"].get("projection", {}).get("feedback_count") != 1
    ):
        raise CheckFailure("client_feedback", "Typed feedback was not accepted")
    post_step = payloads["step_after_feedback"]
    post_steps = int(scenario.get("post_feedback_step_count", 0))
    final_tick = int(scenario.get("final_tick", 0))
    if (
        post_step.get("start_tick") != initial_steps
        or post_step.get("end_tick") != final_tick
        or post_step.get("step_count") != post_steps
    ):
        raise CheckFailure("post_feedback_step", "Post-feedback tick progression is invalid")

    evidence_path = _operation_path(fresh_manifest, "evidence.export", session_id)
    fresh_evidence = fetch_json(base_url + evidence_path)
    _scan_public_value(fresh_evidence, "checker-fetched-evidence")
    if payloads["evidence"].get("projection", {}).get("state_hash") != fresh_evidence.get(
        "projection", {}
    ).get("state_hash"):
        raise CheckFailure("evidence_drift", "Executor and checker evidence hashes differ")
    _validate_evidence(
        fresh_evidence,
        run_id=run_id,
        session_id=session_id,
        package_hash=str(package.get("package_hash", "")),
        final_tick=final_tick,
        feedback_decision_mode=str(scenario.get("feedback_decision_mode", "")),
        accepted_request_id=str(accepted.get("request_id", "")),
        rejected_request_id=str(rejected.get("request_id", "")),
        expected_request_ids=expected_request_ids,
    )

    frame_root = run_dir / "executor" / "frames"
    for frame_name in scenario.get("required_frames", []):
        _validate_png(frame_root / frame_name)

    scan_files = [run_dir / "challenge.json", run_dir / "executor" / "summary.json"]
    scan_files.extend((run_dir / "executor" / "raw").rglob("*"))
    _scan_forbidden(run_dir, scan_files)

    checker_dir.mkdir(parents=True, exist_ok=False)
    fetched_path = checker_dir / "fetched-evidence.json"
    _write_json(fetched_path, fresh_evidence)
    input_files = [run_dir / "challenge.json"]
    input_files.extend(
        path
        for path in (run_dir / "executor").rglob("*")
        if path.is_file()
    )
    input_files.append(fetched_path)
    seals = {
        str(path.relative_to(run_dir)): _sha256_file(path)
        for path in sorted(input_files)
    }
    seal_payload = {
        "contract_version": CONTRACT_VERSION,
        "producer": PRODUCER,
        "run_id": run_id,
        "files": seals,
    }
    seal_hash = _sha256_bytes(
        json.dumps(seal_payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    )
    seal_payload["input_seal_sha256"] = seal_hash
    checks = {
        "challenge_bound": True,
        "challenge_request_ids_bound": True,
        "fresh_evidence_run_bound": True,
        "operation_catalog_complete": True,
        "response_hashes_valid": True,
        "worldengine_instance_stable": True,
        "package_deterministic": True,
        "session_package_bound": True,
        "exact_tick_progression": True,
        "feedback_changes_agent_decision": True,
        "bounded_intervention_valid": True,
        "direct_final_fact_rejected": True,
        "client_action_and_feedback_valid": True,
        "event_and_diff_chain_valid": True,
        "evidence_complete": True,
        "visual_frames_nonblank": True,
        "public_redaction_clean": True
    }
    verdict = {
        "contract_version": CONTRACT_VERSION,
        "producer": PRODUCER,
        "run_id": run_id,
        "status": "PASS",
        "session_id": session_id,
        "checks": checks,
        "input_seal_sha256": seal_hash,
    }
    if write_outputs:
        _write_json(checker_dir / "input-seal.json", seal_payload)
        _write_json(checker_dir / "verdict.json", verdict)
        registry["consumed"].append(run_id)
        _save_registry(registry_path, registry)
    else:
        shutil.rmtree(checker_dir)
    return VerificationResult(
        run_id=run_id,
        session_id=session_id,
        checks=checks,
        input_seal_sha256=seal_hash,
    )


def _failed_payload(exc: CheckFailure, run_dir: Path) -> Dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "producer": PRODUCER,
        "run_id": run_dir.name,
        "status": "FAIL",
        "reason_code": exc.code,
        "detail": exc.detail,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="WorldEngine Godot MVP checker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--output-root", type=Path, required=True)
    prepare_parser.add_argument("--base-url", required=True)
    prepare_parser.add_argument("--registry", type=Path, required=True)
    prepare_parser.add_argument("--run-id")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--run-dir", type=Path, required=True)
    verify_parser.add_argument("--registry", type=Path, required=True)
    verify_parser.add_argument("--scenario", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            run_dir = prepare_run(
                args.output_root,
                args.base_url,
                args.registry,
                run_id=args.run_id,
            )
            print(str(run_dir.resolve()))
            return 0
        result = verify_run(
            args.run_dir,
            args.registry,
            scenario_path=args.scenario,
        )
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "run_id": result.run_id,
                    "session_id": result.session_id,
                    "input_seal_sha256": result.input_seal_sha256,
                },
                sort_keys=True,
            )
        )
        return 0
    except CheckFailure as exc:
        run_dir = getattr(args, "run_dir", Path("."))
        print(json.dumps(_failed_payload(exc, run_dir), sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
