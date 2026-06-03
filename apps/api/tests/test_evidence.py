from app import db as app_db
from app.models import ApiTrace


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
    assert payload["manifest"]["warnings"] == ["records reserved for Task 3 content export"]
    assert payload["records"] == {
        "branches": [],
        "commit_points": [],
        "events": [],
        "state_diffs": [],
        "snapshots": [],
        "director_intents": [],
        "api_traces": [],
        "evaluator_outputs": [],
        "replay_index": [],
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


def test_evidence_bundle_manifest_returns_404_for_missing_session(client):
    response = client.get("/sessions/missing-session/evidence/bundle/manifest")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
