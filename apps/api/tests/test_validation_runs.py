import json

from app import db as app_db
from app.models import ApiTrace


def test_validation_run_operation_log_jsonl_and_evidence_bundle_association(client):
    session = client.post("/sessions", json={"session_name": "Agent Run Session"}).json()
    run_response = client.post(
        "/validation-runs",
        json={
            "session_id": session["id"],
            "actor": "codex",
            "web_url": "http://127.0.0.1:5173",
            "api_base_url": "http://127.0.0.1:8765",
            "worldengine_api_base": "http://127.0.0.1:8000",
            "notes": "smoke run",
        },
    )

    assert run_response.status_code == 201
    run = run_response.json()
    assert run["session_id"] == session["id"]
    assert run["status"] == "running"

    log_response = client.post(
        f"/validation-runs/{run['id']}/operation-log",
        json={
            "actor": "codex",
            "phase": "browser",
            "url": "http://127.0.0.1:5173/sessions",
            "action_type": "click",
            "target_label": "Create WorldEngine Session",
            "input_text": "A public harbor world",
            "request_method": "POST",
            "request_path": "/sessions/worldengine",
            "response_status": 201,
            "response_summary": "session created",
            "visible_result": "Runtime console opened",
            "screenshot_path": "artifacts/screens/session-created.png",
            "downloaded_file": "artifacts/evidence-bundle.json",
            "notes": "visible result matched public session id",
        },
    )

    assert log_response.status_code == 201
    log_entry = log_response.json()
    assert log_entry["run_id"] == run["id"]
    assert log_entry["session_id"] == session["id"]
    assert log_entry["timestamp"]

    jsonl_response = client.get(f"/validation-runs/{run['id']}/operation-log.jsonl")

    assert jsonl_response.status_code == 200
    lines = [json.loads(line) for line in jsonl_response.text.splitlines()]
    assert len(lines) == 1
    assert lines[0]["run_id"] == run["id"]
    assert lines[0]["timestamp"] == log_entry["timestamp"]

    bundle_response = client.get(f"/sessions/{session['id']}/evidence/bundle/manifest")

    assert bundle_response.status_code == 200
    bundle = bundle_response.json()
    assert bundle["manifest"]["latest_validation_run_id"] == run["id"]
    assert bundle["manifest"]["counts"]["validation_runs"] == 1
    assert bundle["manifest"]["counts"]["operation_log_entries"] == 1
    assert bundle["records"]["validation_runs"][0]["id"] == run["id"]
    assert bundle["records"]["operation_log_entries"][0]["run_id"] == run["id"]


def test_operation_log_rejects_forbidden_private_or_secret_content(client):
    session = client.post("/sessions", json={"session_name": "Reject Secret Session"}).json()
    run = client.post("/validation-runs", json={"session_id": session["id"]}).json()

    response = client.post(
        f"/validation-runs/{run['id']}/operation-log",
        json={
            "action_type": "type",
            "target_label": "Director Guidance",
            "input_text": "private_prompt must not be stored",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Operation log contains forbidden private or secret content"


def test_validation_run_api_summary_uses_public_trace_summary(client):
    session = client.post("/sessions", json={"session_name": "API Summary Session"}).json()
    run = client.post("/validation-runs", json={"session_id": session["id"]}).json()

    SessionLocal = app_db.get_sessionmaker()
    with SessionLocal() as database:
        database.add(
            ApiTrace(
                session_id=session["id"],
                method="POST",
                url_path="/worlds",
                status_code=200,
                request_summary_json='{"world_prompt_length": 24}',
                response_summary_json='{"world_id": "world-1", "status": "created"}',
                error_message=None,
                llm_keys_included=False,
                private_worldengine_internals_included=False,
            )
        )
        database.commit()

    response = client.get(f"/validation-runs/{run['id']}/api-summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == run["id"]
    assert payload["session_id"] == session["id"]
    assert payload["api_calls"] == [
        {
            "method": "POST",
            "path": "/worlds",
            "status": 200,
            "public_summary": {"world_id": "world-1", "status": "created"},
            "error_class": None,
        }
    ]
    assert "world_prompt_length" not in str(payload)


def test_validation_run_api_summary_redacts_sensitive_trace_payload(client):
    session = client.post("/sessions", json={"session_name": "API Summary Redaction"}).json()
    run = client.post("/validation-runs", json={"session_id": session["id"]}).json()

    SessionLocal = app_db.get_sessionmaker()
    with SessionLocal() as database:
        database.add(
            ApiTrace(
                session_id=session["id"],
                method="POST",
                url_path="/worlds?api_key=secret-value",
                status_code=200,
                request_summary_json='{"world_prompt_length": 24}',
                response_summary_json='{"world_id": "world-1", "provider_secret": "sk-live"}',
                error_message=None,
                llm_keys_included=False,
                private_worldengine_internals_included=False,
            )
        )
        database.commit()

    response = client.get(f"/validation-runs/{run['id']}/api-summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["api_calls"][0]["path"] == "[redacted]"
    assert payload["api_calls"][0]["public_summary"] == {"world_id": "world-1"}
    assert "secret-value" not in str(payload)
    assert "provider_secret" not in str(payload)
