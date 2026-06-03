from app.db import get_sessionmaker
from app.models import ApiTrace, Session as DbSession


def test_create_session_auto_creates_main_branch(client):
    response = client.post("/sessions", json={"session_name": "First Session"})
    assert response.status_code == 201
    data = response.json()
    assert data["session_name"] == "First Session"
    assert data["main_branch_id"]
    assert data["main_commit_point_id"]
    assert data["worldengine_world_id"] is None
    assert data["public_world_status"] is None
    assert data["initial_state_summary"] is None
    assert data["visualization_payload_summary"] is None


def test_list_sessions_returns_created_session(client):
    client.post("/sessions", json={"session_name": "First Session"})
    response = client.get("/sessions")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["sessions"]) == 1
    assert payload["sessions"][0]["session_name"] == "First Session"


def test_list_sessions_returns_public_world_summaries(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(
            session_name="World Session",
            worldengine_world_id="world-123",
            public_world_status="created",
            initial_state_summary='{"agents": 2}',
            visualization_payload_summary='{"tiles": 12}',
        )
        db.add(db_session)
        db.commit()

    response = client.get("/sessions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["sessions"][0]["worldengine_world_id"] == "world-123"
    assert payload["sessions"][0]["public_world_status"] == "created"
    assert payload["sessions"][0]["initial_state_summary"] == '{"agents": 2}'
    assert payload["sessions"][0]["visualization_payload_summary"] == '{"tiles": 12}'


def test_api_trace_model_stores_redacted_worldengine_call_metadata(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(session_name="Trace Session")
        db.add(db_session)
        db.flush()
        trace = ApiTrace(
            session_id=db_session.id,
            method="POST",
            url_path="/worlds",
            status_code=201,
            request_summary_json='{"world_prompt_length": 20}',
            response_summary_json='{"world_id": "world-123"}',
            error_message=None,
            llm_keys_included=False,
            private_worldengine_internals_included=False,
        )
        db.add(trace)
        db.commit()

        stored = db.get(ApiTrace, trace.id)

    assert stored is not None
    assert stored.session_id == db_session.id
    assert stored.method == "POST"
    assert stored.url_path == "/worlds"
    assert stored.status_code == 201
    assert stored.llm_keys_included is False
    assert stored.private_worldengine_internals_included is False
