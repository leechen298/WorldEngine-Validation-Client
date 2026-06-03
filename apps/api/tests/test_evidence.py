from app import db as app_db
from app.models import ApiTrace, DirectorIntent, Event, Snapshot, StateDiff


def test_bundle_metadata_counts_commit_points_and_branches(client):
    session = client.post("/sessions", json={"session_name": "Evidence Session"}).json()
    session_id = session["id"]

    response = client.get(f"/sessions/{session_id}/evidence/bundle")
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["session_name"] == "Evidence Session"
    assert payload["branches"] == 1
    assert payload["commit_points"] == 1
    assert payload["api_traces"] == 0
    assert payload["llm_keys_included"] is False
    assert payload["private_worldengine_internals_included"] is False


def test_evidence_bundle_counts_api_traces_after_world_creation(client, monkeypatch):
    async def fake_create_world(world_prompt: str):
        return {
            "world_id": "world-123",
            "status": "created",
            "initial_state_summary": "{}",
            "visualization_payload_summary": "{}",
            "snapshot_json": "{}",
            "event_payload_json": "{}",
            "api_trace": {
                "method": "POST",
                "url_path": "/worlds",
                "status_code": 201,
                "request_summary_json": '{"world_prompt_length": 20}',
                "response_summary_json": '{"world_id": "world-123"}',
                "error_message": None,
            },
        }

    monkeypatch.setattr("app.routes.sessions.create_world_via_public_api", fake_create_world)
    session = client.post(
        "/sessions/worldengine",
        json={"session_name": "Evidence World", "world_prompt": "A small public world"},
    ).json()

    response = client.get(f"/sessions/{session['id']}/evidence/bundle")

    assert response.status_code == 200
    assert response.json()["api_traces"] == 1


def test_evidence_bundle_manifest_preserves_metadata_endpoint_and_reserves_records(client):
    session = client.post("/sessions", json={"session_name": "Manifest Session"}).json()
    session_id = session["id"]

    metadata_response = client.get(f"/sessions/{session_id}/evidence/bundle")
    manifest_response = client.get(f"/sessions/{session_id}/evidence/bundle/manifest")

    assert metadata_response.status_code == 200
    assert manifest_response.status_code == 200
    payload = manifest_response.json()
    assert set(payload.keys()) == {"manifest", "records"}
    assert payload["manifest"]["bundle_schema_version"] == "0.6.0"
    assert payload["manifest"]["session_id"] == session_id
    assert payload["manifest"]["session_name"] == "Manifest Session"
    assert payload["manifest"]["worldengine_world_id"] is None
    assert payload["manifest"]["world_status"] == "created"
    assert payload["manifest"]["counts"]["branches"] == metadata_response.json()["branches"]
    assert payload["manifest"]["counts"]["commit_points"] == metadata_response.json()["commit_points"]
    assert payload["manifest"]["redaction_flags"] == {
        "llm_keys_included": False,
        "private_worldengine_internals_included": False,
    }
    assert payload["manifest"]["warnings"] == ["public evaluator outputs unavailable"]
    assert len(payload["records"]["branches"]) == payload["manifest"]["counts"]["branches"]
    assert len(payload["records"]["commit_points"]) == payload["manifest"]["counts"]["commit_points"]
    assert len(payload["records"]["replay_index"]) == payload["manifest"]["counts"]["commit_points"]
    assert payload["records"] == {
        "branches": payload["records"]["branches"],
        "commit_points": payload["records"]["commit_points"],
        "events": [],
        "state_diffs": [],
        "snapshots": [],
        "director_intents": [],
        "api_traces": [],
        "evaluator_outputs": [],
        "replay_index": payload["records"]["replay_index"],
    }


def test_evidence_bundle_manifest_aggregates_api_trace_redaction_flags(client):
    session = client.post("/sessions", json={"session_name": "Dirty Trace Session"}).json()
    session_id = session["id"]

    SessionLocal = app_db.get_sessionmaker()
    with SessionLocal() as db:
        db.add(
            ApiTrace(
                session_id=session_id,
                method="POST",
                url_path="/worlds",
                status_code=200,
                request_summary_json="{}",
                response_summary_json="{}",
                llm_keys_included=True,
                private_worldengine_internals_included=True,
            )
        )
        db.commit()

    response = client.get(f"/sessions/{session_id}/evidence/bundle/manifest")

    assert response.status_code == 200
    manifest = response.json()["manifest"]
    assert manifest["counts"]["api_traces"] == 1
    assert manifest["redaction_flags"] == {
        "llm_keys_included": True,
        "private_worldengine_internals_included": True,
    }
    assert "api traces include flagged sensitive content" in manifest["warnings"]


def test_evidence_bundle_manifest_exports_records_and_redacts_sensitive_payloads(client):
    session = client.post("/sessions", json={"session_name": "Recorded Evidence"}).json()
    session_id = session["id"]
    branch_id = session["main_branch_id"]

    SessionLocal = app_db.get_sessionmaker()
    with SessionLocal() as db:
        db.add_all(
            [
                Event(
                    session_id=session_id,
                    branch_id=branch_id,
                    tick=2,
                    event_kind="world_event",
                    payload_json=(
                        '{"text": "public market opens", "private_prompt": "hidden", '
                        '"agent": {"name": "Ada", "memory": "hidden"}, "warning": "api_key=hidden"}'
                    ),
                ),
                StateDiff(
                    session_id=session_id,
                    branch_id=branch_id,
                    tick=2,
                    diff_json='{"visualization": {"weather": "rain"}, "source_path": "/private/world"}',
                ),
                Snapshot(
                    session_id=session_id,
                    branch_id=branch_id,
                    tick=2,
                    snapshot_json='{"visualization": {"tiles": []}, "provider_secret": "hidden"}',
                ),
                DirectorIntent(
                    session_id=session_id,
                    branch_id=branch_id,
                    tick=2,
                    instruction_text="Increase public market activity without private_prompt=hidden",
                    status="accepted",
                    public_explanation="Market activity can trend upward.",
                    applied_event_id="event-public",
                    error_message="provider_secret=hidden",
                ),
                ApiTrace(
                    session_id=session_id,
                    method="POST",
                    url_path="/worlds/world-1/director-guidance",
                    status_code=202,
                    request_summary_json='{"instruction_text": "public", "api_key": "hidden"}',
                    response_summary_json='{"status": "accepted", "private_prompt": "hidden"}',
                    error_message=None,
                    llm_keys_included=False,
                    private_worldengine_internals_included=False,
                ),
            ]
        )
        db.commit()

    response = client.get(f"/sessions/{session_id}/evidence/bundle/manifest")

    assert response.status_code == 200
    payload = response.json()
    manifest = payload["manifest"]
    records = payload["records"]
    assert "records reserved for Task 3 content export" not in manifest["warnings"]
    assert "public evaluator outputs unavailable" in manifest["warnings"]
    assert "sensitive content redacted from evidence records" in manifest["warnings"]
    assert manifest["redaction_flags"] == {
        "llm_keys_included": True,
        "private_worldengine_internals_included": True,
    }
    assert manifest["counts"]["events"] == len(records["events"]) == 1
    assert manifest["counts"]["state_diffs"] == len(records["state_diffs"]) == 1
    assert manifest["counts"]["snapshots"] == len(records["snapshots"]) == 1
    assert manifest["counts"]["director_intents"] == len(records["director_intents"]) == 1
    assert manifest["counts"]["api_traces"] == len(records["api_traces"]) == 1
    assert manifest["counts"]["replay_index"] == len(records["replay_index"]) == 1
    assert records["branches"][0]["branch_name"] == "main"
    assert records["commit_points"][0]["tick"] == 0
    assert records["events"][0]["payload"] == {
        "text": "public market opens",
        "agent": {"name": "Ada"},
        "warning": "[redacted]",
    }
    assert records["state_diffs"][0]["diff"] == {"visualization": {"weather": "rain"}}
    assert records["snapshots"][0]["snapshot"] == {"visualization": {"tiles": []}}
    assert records["director_intents"][0]["instruction_text"] == "[redacted]"
    assert records["director_intents"][0]["error_message"] == "[redacted]"
    assert records["api_traces"][0] == {
        "method": "POST",
        "url_path": "/worlds/world-1/director-guidance",
        "status_code": 202,
        "request_summary": {"instruction_text": "public"},
        "response_summary": {"status": "accepted"},
        "error_message": None,
        "llm_keys_included": False,
        "private_worldengine_internals_included": False,
    }
    assert records["evaluator_outputs"] == []
    assert records["replay_index"][0]["tick"] == 0
    assert records["replay_index"][0]["branch_ids"] == [branch_id]
    assert "private_prompt" not in str(payload)
    assert "source_path" not in str(payload)
    assert "provider_secret" not in str(payload)
    assert "api_key" not in str(payload)
    assert "memory" not in str(payload)
    assert "provider_secret" not in str(payload)


def test_evidence_bundle_manifest_returns_404_for_missing_session(client):
    response = client.get("/sessions/missing-session/evidence/bundle/manifest")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_evidence_bundle_download_returns_json_attachment(client):
    session = client.post("/sessions", json={"session_name": "Download Evidence"}).json()
    session_id = session["id"]

    response = client.get(f"/sessions/{session_id}/evidence/bundle/download")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    content_disposition = response.headers["content-disposition"]
    assert "attachment" in content_disposition
    assert session_id in content_disposition
    assert content_disposition.endswith(".json\"")
    payload = response.json()
    assert set(payload.keys()) == {"manifest", "records"}
    assert payload["manifest"]["session_id"] == session_id
    assert payload["records"]["branches"][0]["branch_name"] == "main"


def test_evidence_bundle_download_returns_404_for_missing_session(client):
    response = client.get("/sessions/missing-session/evidence/bundle/download")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
