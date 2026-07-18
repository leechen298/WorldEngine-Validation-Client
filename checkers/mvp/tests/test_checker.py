from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
from PIL import Image, ImageDraw

from worldengine_mvp_checker import (
    CONTRACT_VERSION,
    REQUEST_SUFFIXES,
    CheckFailure,
    prepare_run,
    verify_run,
)


NOW = 2_000_000_000


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _body(data: Any) -> Dict[str, Any]:
    return {"code": 0, "message": "ok", "data": data}


def _valid_manifest() -> Dict[str, Any]:
    operation_ids = [
        ("capabilities.read", "/api/v1/capabilities"),
        ("world_packages.create", "/api/v1/world-packages"),
        ("sessions.create", "/api/v1/sessions"),
        ("sessions.step", "/api/v1/sessions/{session_id}/steps"),
        ("directions.submit", "/api/v1/sessions/{session_id}/directions"),
        ("actions.submit", "/api/v1/sessions/{session_id}/actions"),
        ("feedback.submit", "/api/v1/sessions/{session_id}/feedback"),
        ("events.poll", "/api/v1/sessions/{session_id}/events"),
        ("projection.read", "/api/v1/sessions/{session_id}/projection"),
        ("evidence.export", "/api/v1/sessions/{session_id}/evidence"),
    ]
    return {
        "contract_version": "engine-v1-mvp",
        "instance_id": "instance-test",
        "operations": [
            {"operation_id": operation_id, "path": path}
            for operation_id, path in operation_ids
        ],
    }


def _valid_evidence(
    session_id: str = "session-test",
    run_id: str = "run-checker-test",
) -> Dict[str, Any]:
    package_hash = "a" * 64
    return {
        "package": {
            "package_hash": package_hash,
            "brief": {"seed": f"godot-{run_id}"},
        },
        "projection": {
            "session_id": session_id,
            "source_package_hash": package_hash,
            "tick": 3,
            "revision": 3,
            "state_hash": "3" * 64,
            "event_cursor": 3,
            "feedback_count": 1,
        },
        "events": [
            {"sequence": 1, "event_id": "event-1"},
            {"sequence": 2, "event_id": "event-2"},
            {"sequence": 3, "event_id": "event-3"},
        ],
        "diffs": [
            {
                "diff_id": "diff-1",
                "state_hash_before": "0" * 64,
                "state_hash_after": "1" * 64,
            },
            {
                "diff_id": "diff-2",
                "state_hash_before": "1" * 64,
                "state_hash_after": "2" * 64,
            },
            {
                "diff_id": "diff-3",
                "state_hash_before": "2" * 64,
                "state_hash_after": "3" * 64,
            },
        ],
        "agent_cycles": [
            {
                "perception": {"feedback_count": 0},
                "experience_refs_used": [],
                "decision": {
                    "decision_mode": "initial_policy",
                    "feedback_count": 0,
                    "influence_factors": ["current_variables"],
                },
                "action_request": {"amount": 1},
                "action_result": {"status": "accepted"},
            },
            {
                "perception": {"feedback_count": 0},
                "experience_refs_used": [{"ref_id": "event-1"}],
                "decision": {
                    "decision_mode": "experience_guided_policy",
                    "feedback_count": 0,
                    "influence_factors": ["current_variables", "experience"],
                },
                "action_request": {"amount": 1},
                "action_result": {"status": "accepted"},
            },
            {
                "perception": {"feedback_count": 1},
                "experience_refs_used": [{"ref_id": "event-2"}],
                "decision": {
                    "decision_mode": "feedback_adjusted_experience_policy",
                    "feedback_count": 1,
                    "influence_factors": [
                        "current_variables",
                        "experience",
                        "feedback_count",
                    ],
                },
                "action_request": {"amount": -1},
                "action_result": {"status": "accepted"},
            },
        ],
        "direction_decisions": [
            {
                "request_id": f"{run_id}-direction-accept",
                "status": "accepted",
                "queued": False,
                "application_status": "applied",
                "application_reason_code": "direction_applied",
                "event_ref": "event-1",
                "application_event_refs": ["event-2"],
                "applied_diff_refs": ["diff-2"],
            },
            {
                "request_id": f"{run_id}-direction-reject",
                "status": "rejected",
                "reason_code": "direct_final_fact_forbidden",
                "applied_diff_refs": [],
            },
        ],
        "request_correlations": [
            {
                "operation_id": "sessions.create",
                "request_id": f"{run_id}-session",
                "status": "accepted",
                "event_refs": ["event-1"],
                "diff_refs": [],
            },
            {
                "operation_id": "directions.submit",
                "request_id": f"{run_id}-direction-accept",
                "status": "accepted",
                "application_status": "applied",
                "event_refs": ["event-1", "event-2"],
                "diff_refs": ["diff-2"],
            },
            {
                "operation_id": "directions.submit",
                "request_id": f"{run_id}-direction-reject",
                "status": "rejected",
                "application_status": "not_applicable",
                "event_refs": ["event-3"],
                "diff_refs": [],
            },
            {
                "operation_id": "sessions.step",
                "request_id": f"{run_id}-step",
                "status": "completed",
                "event_refs": ["event-1"],
                "diff_refs": ["diff-1"],
            },
            {
                "operation_id": "actions.submit",
                "request_id": f"{run_id}-action",
                "status": "accepted",
                "event_refs": ["event-2"],
                "diff_refs": ["diff-2"],
            },
            {
                "operation_id": "feedback.submit",
                "request_id": f"{run_id}-feedback",
                "status": "accepted",
                "event_refs": ["event-2"],
                "diff_refs": ["diff-2"],
            },
            {
                "operation_id": "sessions.step",
                "request_id": f"{run_id}-step-after-feedback",
                "status": "completed",
                "event_refs": ["event-3"],
                "diff_refs": ["diff-3"],
            },
        ],
        "completeness": {
            "integrity": {
                "status": "valid",
                "checks": {"event_diff_integrity": True},
                "failures": [],
            },
            "scenario_coverage": {
                "status": "covered",
                "checks": {
                    "action": True,
                    "feedback": True,
                    "agent": True,
                    "direction": True,
                    "agent_experience": True,
                    "agent_feedback_influence": True,
                    "accepted_direction_applied": True,
                    "semantic_direction_rejection": True,
                    "same_intervention_window": True,
                },
                "missing": [],
            },
        },
    }


def _payloads(evidence: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    package = {
        "package_id": "package-test",
        "package_hash": "a" * 64,
        "brief": {"seed": f"godot-{run_id}"},
        "readiness": {"status": "ready"},
    }
    projection = evidence["projection"]
    return {
        "capabilities": _valid_manifest(),
        "package_create": package,
        "package_repeat": copy.deepcopy(package),
        "session_create": {
            "session_id": "session-test",
            "source_package_hash": package["package_hash"],
            "projection": {"revision": 0},
        },
        "direction_accept": {
            "request_id": f"{run_id}-direction-accept",
            "status": "accepted",
            "queued": True,
        },
        "direction_reject": {
            "request_id": f"{run_id}-direction-reject",
            "status": "rejected",
            "reason_code": "direct_final_fact_forbidden",
            "applied_diff_refs": [],
        },
        "step": {"start_tick": 0, "end_tick": 2, "step_count": 2},
        "action": {"status": "accepted"},
        "feedback": {
            "status": "accepted",
            "projection": {"feedback_count": 1},
        },
        "step_after_feedback": {"start_tick": 2, "end_tick": 3, "step_count": 1},
        "events": {"items": evidence["events"]},
        "projection": projection,
        "evidence": evidence,
    }


def _create_frame(path: Path) -> None:
    image = Image.new("RGB", (640, 360), "#17251f")
    draw = ImageDraw.Draw(image)
    colors = [
        "#69a06b",
        "#e7c35f",
        "#d45b51",
        "#4e91a8",
        "#f3ead7",
        "#8a6f9e",
        "#d98e47",
        "#5b5f67",
    ]
    for index, color in enumerate(colors):
        x = (index % 4) * 150
        y = 30 + (index // 4) * 165
        draw.rectangle((x, y, x + 120, y + 130), fill=color)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def _create_run(
    root: Path,
    *,
    run_id: str = "run-checker-test",
    evidence: Optional[Dict[str, Any]] = None,
) -> tuple[Path, Dict[str, Any], Dict[str, Any]]:
    run_dir = prepare_run(
        root,
        "http://127.0.0.1:8000",
        root.parent / "registry.json",
        run_id=run_id,
        now=NOW,
    )
    challenge = json.loads((run_dir / "challenge.json").read_text())
    actual_evidence = evidence or _valid_evidence(run_id=run_id)
    payloads = _payloads(actual_evidence, run_id)
    scenario = json.loads(
        (Path(__file__).resolve().parents[3] / "contracts/mvp/scenario.json").read_text()
    )
    operation_lines = []
    for sequence, operation in enumerate(scenario["required_operations"], start=1):
        label = operation["label"]
        relative = f"executor/raw/responses/{sequence:03d}-{label}.json"
        response_path = run_dir / relative
        _write_json(response_path, _body(payloads[label]))
        operation_lines.append(
            {
                "sequence": sequence,
                "producer": "godot-executor",
                "label": label,
                "operation_id": operation["operation_id"],
                "request_id": (
                    f"{run_id}-{REQUEST_SUFFIXES[label]}"
                    if label in REQUEST_SUFFIXES
                    else None
                ),
                "status_code": 200,
                "response_file": relative,
                "response_sha256": hashlib.sha256(response_path.read_bytes()).hexdigest(),
            }
        )
    operations_path = run_dir / "executor/raw/operations.jsonl"
    operations_path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in operation_lines),
        encoding="utf-8",
    )
    _write_json(
        run_dir / "executor/summary.json",
        {
            "contract_version": CONTRACT_VERSION,
            "producer": "godot-executor",
            "outcome": "completed",
            "run_id": run_id,
            "nonce": challenge["nonce"],
            "session_id": "session-test",
            "operation_count": len(operation_lines),
        },
    )
    for frame_name in scenario["required_frames"]:
        _create_frame(run_dir / "executor/frames" / frame_name)
    return run_dir, _valid_manifest(), actual_evidence


def _fetcher(manifest: Dict[str, Any], evidence: Dict[str, Any]):
    def fetch(url: str) -> Any:
        if url.endswith("/api/v1/capabilities"):
            return manifest
        if url.endswith("/api/v1/sessions/session-test/evidence"):
            return evidence
        raise AssertionError(f"Unexpected URL: {url}")

    return fetch


def _assert_failure(code: str, callback) -> None:
    with pytest.raises(CheckFailure) as exc_info:
        callback()
    assert exc_info.value.code == code


def test_valid_run_is_independently_verified(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")

    result = verify_run(
        run_dir,
        tmp_path / "registry.json",
        now=NOW + 10,
        fetch_json=_fetcher(manifest, evidence),
    )

    assert all(result.checks.values())
    verdict = json.loads((run_dir / "checker/verdict.json").read_text())
    assert verdict["producer"] == "worldengine-independent-checker"
    assert verdict["status"] == "PASS"


def test_tampered_response_hash_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    response = next((run_dir / "executor/raw/responses").iterdir())
    response.write_bytes(response.read_bytes() + b" ")

    _assert_failure(
        "response_hash_mismatch",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_missing_response_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    next((run_dir / "executor/raw/responses").iterdir()).unlink()

    _assert_failure(
        "missing_response",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_stale_challenge_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")

    _assert_failure(
        "stale_challenge",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 901,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_unissued_challenge_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    registry_path = tmp_path / "registry.json"
    registry = json.loads(registry_path.read_text())
    registry["issued"] = {}
    _write_json(registry_path, registry)

    _assert_failure(
        "unissued_challenge",
        lambda: verify_run(
            run_dir,
            registry_path,
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_forged_nonce_is_rejected_by_registry_binding(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    forged_nonce = "f" * 64
    challenge_path = run_dir / "challenge.json"
    challenge = json.loads(challenge_path.read_text())
    challenge["nonce"] = forged_nonce
    _write_json(challenge_path, challenge)
    summary_path = run_dir / "executor/summary.json"
    summary = json.loads(summary_path.read_text())
    summary["nonce"] = forged_nonce
    _write_json(summary_path, summary)

    _assert_failure(
        "challenge_registry_binding",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_operation_request_id_from_another_run_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    operations_path = run_dir / "executor/raw/operations.jsonl"
    records = [json.loads(line) for line in operations_path.read_text().splitlines()]
    records[1]["request_id"] = "run-other-package"
    operations_path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in records),
        encoding="utf-8",
    )

    _assert_failure(
        "operation_request_binding",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_fresh_evidence_package_from_another_run_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    evidence["package"]["brief"]["seed"] = "godot-run-other"

    _assert_failure(
        "run_evidence_binding",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_fresh_evidence_package_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    evidence["package"]["package_hash"] = "b" * 64

    _assert_failure(
        "package_evidence_binding",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_reused_run_id_is_rejected(tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    first, manifest, evidence = _create_run(tmp_path / "first")
    verify_run(
        first,
        registry,
        now=NOW + 10,
        fetch_json=_fetcher(manifest, evidence),
    )
    second = tmp_path / "second" / first.name
    shutil.copytree(first, second)
    shutil.rmtree(second / "checker")

    _assert_failure(
        "reused_run_id",
        lambda: verify_run(
            second,
            registry,
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_cross_session_evidence_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, _ = _create_run(tmp_path / "runs")
    evidence = _valid_evidence("session-other")

    _assert_failure(
        "cross_session_evidence",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_non_monotonic_events_are_rejected(tmp_path: Path) -> None:
    evidence = _valid_evidence()
    evidence["events"][1]["sequence"] = 3
    run_dir, manifest, _ = _create_run(tmp_path / "runs", evidence=evidence)

    _assert_failure(
        "event_sequence",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_sensitive_marker_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    summary_path = run_dir / "executor/summary.json"
    summary = json.loads(summary_path.read_text())
    summary["note"] = "raw_prompt should never be public"
    _write_json(summary_path, summary)

    _assert_failure(
        "sensitive_marker",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_prewritten_verdict_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    _write_json(run_dir / "checker/verdict.json", {"status": "PASS"})

    _assert_failure(
        "prewritten_verdict",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )


def test_executor_verdict_field_is_rejected(tmp_path: Path) -> None:
    run_dir, manifest, evidence = _create_run(tmp_path / "runs")
    summary_path = run_dir / "executor/summary.json"
    summary = json.loads(summary_path.read_text())
    summary["verdict"] = "PASS"
    _write_json(summary_path, summary)

    _assert_failure(
        "executor_verdict",
        lambda: verify_run(
            run_dir,
            tmp_path / "registry.json",
            now=NOW + 10,
            fetch_json=_fetcher(manifest, evidence),
        ),
    )
