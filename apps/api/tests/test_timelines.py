from app.db import get_sessionmaker
from app.models import CommitPoint, Event, Session as DbSession, Snapshot, TimelineBranch


def test_list_branches_has_main_branch(client):
    session = client.post("/sessions", json={"session_name": "Timeline Session"}).json()
    session_id = session["id"]

    response = client.get(f"/sessions/{session_id}/branches")
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["branches"][0]["branch_name"] == "main"
    assert payload["branches"][0]["is_main"] is True
    assert payload["branches"][0]["current_tick"] == 0


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
    assert branch_payload["is_main"] is False
    assert branch_payload["current_tick"] == branch_payload["tick"]

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


def test_list_commit_points_returns_branch_context_and_public_summary(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(session_name="Commit Browser")
        db.add(db_session)
        db.flush()
        snapshot = Snapshot(session_id=db_session.id, tick=2, snapshot_json='{"public":"ok"}')
        event = Event(
            session_id=db_session.id,
            tick=2,
            event_kind="world_change",
            payload_json='{"text":"Market opens","private_prompt":"hidden"}',
        )
        db.add_all([snapshot, event])
        db.flush()
        commit_point = CommitPoint(
            session_id=db_session.id,
            tick=2,
            event_id=event.id,
            snapshot_id=snapshot.id,
            payload_json='{"summary":"Checkpoint ready","private_prompt":"hidden","thought":"secret"}',
        )
        db.add(commit_point)
        db.flush()
        branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="main",
            commit_point_id=commit_point.id,
            tick=2,
            snapshot_reference=snapshot.id,
            is_main=True,
        )
        db.add(branch)
        db.flush()
        snapshot.branch_id = branch.id
        event.branch_id = branch.id
        db.commit()
        session_id = db_session.id
        commit_point_id = commit_point.id
        event_id = event.id
        snapshot_id = snapshot.id
        branch_id = branch.id

    response = client.get(f"/sessions/{session_id}/branches/commit-points")

    assert response.status_code == 200
    payload = response.json()
    assert payload == [
        {
            "id": commit_point_id,
            "session_id": session_id,
            "tick": 2,
            "event_id": event_id,
            "snapshot_id": snapshot_id,
            "payload_summary": "Checkpoint ready",
            "branch_ids": [branch_id],
            "branch_names": ["main"],
            "created_at": payload[0]["created_at"],
        }
    ]
    assert "payload_json" not in payload[0]
    assert "private_prompt" not in str(payload)
    assert "thought" not in str(payload)
