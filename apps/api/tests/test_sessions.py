def test_create_session_auto_creates_main_branch(client):
    response = client.post("/sessions", json={"session_name": "First Session"})
    assert response.status_code == 201
    data = response.json()
    assert data["session_name"] == "First Session"
    assert data["main_branch_id"]
    assert data["main_commit_point_id"]


def test_list_sessions_returns_created_session(client):
    client.post("/sessions", json={"session_name": "First Session"})
    response = client.get("/sessions")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["sessions"]) == 1
    assert payload["sessions"][0]["session_name"] == "First Session"
