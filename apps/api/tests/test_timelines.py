def test_list_branches_has_main_branch(client):
    session = client.post("/sessions", json={"session_name": "Timeline Session"}).json()
    session_id = session["id"]

    response = client.get(f"/sessions/{session_id}/branches")
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["branches"][0]["branch_name"] == "main"


def test_create_branch_from_main_commit_point(client):
    session = client.post("/sessions", json={"session_name": "Branch Session"}).json()
    session_id = session["id"]
    main_commit_point_id = session["main_commit_point_id"]

    response = client.post(
        f"/sessions/{session_id}/branches",
        json={
            "branch_name": "director-handoff",
            "commit_point_id": main_commit_point_id,
        },
    )
    assert response.status_code == 201
    branch_payload = response.json()
    assert branch_payload["branch_name"] == "director-handoff"
    assert branch_payload["commit_point_id"] == main_commit_point_id

    list_response = client.get(f"/sessions/{session_id}/branches")
    assert len(list_response.json()["branches"]) == 2


def test_create_branch_rejects_client_snapshot_reference(client):
    session = client.post("/sessions", json={"session_name": "Snapshot Session"}).json()
    session_id = session["id"]
    main_commit_point_id = session["main_commit_point_id"]

    response = client.post(
        f"/sessions/{session_id}/branches",
        json={
            "branch_name": "branch-with-client-snapshot",
            "commit_point_id": main_commit_point_id,
            "snapshot_reference": "client-supplied-snapshot",
        },
    )

    assert response.status_code == 422


def test_create_branch_rejects_duplicate_name_in_same_session(client):
    session = client.post("/sessions", json={"session_name": "Duplicate Branch Session"}).json()
    session_id = session["id"]
    main_commit_point_id = session["main_commit_point_id"]

    first = client.post(
        f"/sessions/{session_id}/branches",
        json={"branch_name": "director-handoff", "commit_point_id": main_commit_point_id},
    )
    duplicate = client.post(
        f"/sessions/{session_id}/branches",
        json={"branch_name": "director-handoff", "commit_point_id": main_commit_point_id},
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
