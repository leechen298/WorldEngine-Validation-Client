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
    assert payload["llm_keys_included"] is False
    assert payload["private_worldengine_internals_included"] is False
