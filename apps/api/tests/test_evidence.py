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
