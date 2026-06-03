import httpx
import pytest

from app.db import get_sessionmaker
from app.models import ApiTrace, CommitPoint, Event, Session as DbSession, Snapshot, StateDiff, TimelineBranch
from app.worldengine_client import create_world_via_public_api


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


@pytest.mark.asyncio
async def test_worldengine_client_creates_world_via_discovered_public_endpoint(monkeypatch):
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, request.url.path, request.content))
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200,
                json={"paths": {"/worlds": {"post": {"operationId": "createWorld"}}}},
            )
        if request.url.path == "/worlds":
            return httpx.Response(
                201,
                json={
                    "world_id": "world-123",
                    "status": "created",
                    "initial_state": {"agents": 2},
                    "visualization": {"tiles": 12},
                },
            )
        return httpx.Response(404)

    original_async_client = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, timeout):
            self.client = original_async_client(transport=httpx.MockTransport(handler), timeout=timeout)

        async def __aenter__(self):
            return self.client

        async def __aexit__(self, exc_type, exc, tb):
            await self.client.aclose()

    monkeypatch.setenv("WORLDENGINE_API_BASE", "http://worldengine.example")
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    result = await create_world_via_public_api("A small public world")

    assert result["world_id"] == "world-123"
    assert result["status"] == "created"
    assert result["initial_state_summary"] == '{"agents": 2}'
    assert result["visualization_payload_summary"] == '{"tiles": 12}'
    assert requests[0][0:2] == ("GET", "/openapi.json")
    assert requests[1][0:2] == ("POST", "/worlds")
    assert b"A small public world" in requests[1][2]


@pytest.mark.asyncio
async def test_worldengine_client_sanitizes_world_creation_public_summaries(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json={"paths": {"/worlds": {"post": {"operationId": "createWorld"}}}})
        if request.url.path == "/worlds":
            return httpx.Response(
                201,
                json={
                    "world_id": "world-123",
                    "status": "created",
                    "initial_state": {
                        "agents": 2,
                        "key": "hidden",
                        "path": "/private/world",
                        "private_prompt": "hidden",
                        "oracle_internal": "hidden",
                    },
                    "visualization": {
                        "tiles": 12,
                        "source_path": "/tmp/worldengine",
                        "internal_helper": "hidden",
                    },
                },
            )
        return httpx.Response(404)

    original_async_client = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, timeout):
            self.client = original_async_client(transport=httpx.MockTransport(handler), timeout=timeout)

        async def __aenter__(self):
            return self.client

        async def __aexit__(self, exc_type, exc, tb):
            await self.client.aclose()

    monkeypatch.setenv("WORLDENGINE_API_BASE", "http://worldengine.example")
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    result = await create_world_via_public_api("A small public world")

    assert result["initial_state_summary"] == '{"agents": 2}'
    assert result["visualization_payload_summary"] == '{"tiles": 12}'
    assert "key" not in result["snapshot_json"]
    assert "path" not in result["snapshot_json"]
    assert "private_prompt" not in result["snapshot_json"]
    assert "source_path" not in result["snapshot_json"]


@pytest.mark.asyncio
async def test_worldengine_client_rejects_success_response_without_world_id(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json={"paths": {"/worlds": {"post": {"operationId": "createWorld"}}}})
        if request.url.path == "/worlds":
            return httpx.Response(201, json={"status": "created", "initial_state": {}, "visualization": {}})
        return httpx.Response(404)

    original_async_client = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, timeout):
            self.client = original_async_client(transport=httpx.MockTransport(handler), timeout=timeout)

        async def __aenter__(self):
            return self.client

        async def __aexit__(self, exc_type, exc, tb):
            await self.client.aclose()

    monkeypatch.setenv("WORLDENGINE_API_BASE", "http://worldengine.example")
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(RuntimeError, match="did not include public world id"):
        await create_world_via_public_api("A small public world")


@pytest.mark.asyncio
async def test_worldengine_client_rejects_private_world_creation_endpoint(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200,
                json={"paths": {"/internal/worlds": {"post": {"operationId": "createWorld"}}}},
            )
        return httpx.Response(404)

    original_async_client = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, timeout):
            self.client = original_async_client(transport=httpx.MockTransport(handler), timeout=timeout)

        async def __aenter__(self):
            return self.client

        async def __aexit__(self, exc_type, exc, tb):
            await self.client.aclose()

    monkeypatch.setenv("WORLDENGINE_API_BASE", "http://worldengine.example")
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(RuntimeError, match="endpoint not found"):
        await create_world_via_public_api("A small public world")


def test_create_worldengine_session_persists_public_initial_state(client, monkeypatch):
    async def fake_create_world(world_prompt: str):
        assert world_prompt == "A small public world"
        return {
            "world_id": "world-123",
            "status": "created",
            "initial_state_summary": '{"agents": 2}',
            "visualization_payload_summary": '{"tiles": 12}',
            "snapshot_json": '{"initial_state": {"agents": 2}, "visualization": {"tiles": 12}}',
            "event_payload_json": '{"world_id": "world-123", "status": "created"}',
            "api_trace": {
                "method": "POST",
                "url_path": "/worlds",
                "status_code": 201,
                "request_summary_json": '{"world_prompt_length": 20}',
                "response_summary_json": '{"world_id": "world-123", "status": "created"}',
                "error_message": None,
            },
        }

    monkeypatch.setattr("app.routes.sessions.create_world_via_public_api", fake_create_world)

    response = client.post(
        "/sessions/worldengine",
        json={"session_name": "Created World", "world_prompt": "A small public world"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["session_name"] == "Created World"
    assert payload["worldengine_world_id"] == "world-123"
    assert payload["public_world_status"] == "created"
    assert payload["initial_state_summary"] == '{"agents": 2}'
    assert payload["visualization_payload_summary"] == '{"tiles": 12}'

    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        snapshot = db.query(Snapshot).filter(Snapshot.session_id == payload["id"]).one()
        event = db.query(Event).filter(Event.session_id == payload["id"]).one()
        trace = db.query(ApiTrace).filter(ApiTrace.session_id == payload["id"]).one()
        commit_point = db.query(CommitPoint).filter(CommitPoint.session_id == payload["id"]).one()

    assert snapshot.snapshot_json == '{"initial_state": {"agents": 2}, "visualization": {"tiles": 12}}'
    assert event.event_kind == "world_created"
    assert commit_point.event_id == event.id
    assert trace.llm_keys_included is False
    assert trace.private_worldengine_internals_included is False


def test_create_worldengine_session_does_not_persist_when_public_endpoint_missing(client, monkeypatch):
    async def fake_create_world(world_prompt: str):
        raise RuntimeError("WorldEngine public world creation endpoint not found")

    monkeypatch.setattr("app.routes.sessions.create_world_via_public_api", fake_create_world)

    response = client.post(
        "/sessions/worldengine",
        json={"session_name": "Missing Endpoint", "world_prompt": "A small public world"},
    )

    assert response.status_code == 502
    assert client.get("/sessions").json()["sessions"] == []


def test_create_worldengine_session_does_not_persist_when_world_id_missing(client, monkeypatch):
    async def fake_create_world(world_prompt: str):
        raise RuntimeError("WorldEngine response did not include public world id")

    monkeypatch.setattr("app.routes.sessions.create_world_via_public_api", fake_create_world)

    response = client.post(
        "/sessions/worldengine",
        json={"session_name": "Missing World Id", "world_prompt": "A small public world"},
    )

    assert response.status_code == 502
    assert client.get("/sessions").json()["sessions"] == []


def test_runtime_view_returns_public_snapshot_events_and_tick(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(
            session_name="Runtime Session",
            worldengine_world_id="world-123",
            public_world_status="running",
        )
        db.add(db_session)
        db.flush()
        snapshot = Snapshot(
            session_id=db_session.id,
            tick=3,
            snapshot_json=(
                '{"visualization":{"tiles":[{"x":0,"y":0,"terrain":"grass"}],'
                '"entities":[{"id":"agent-1","x":1,"y":2,"sprite":"person"}]},'
                '"initial_state":{"agents":[{"id":"agent-1","display_name":"Ada",'
                '"public_status":"walking","location":"market","visible_action":"trading",'
                '"memory":"private","goal":"private","self_state":"hidden"}]},'
                '"raw_response":{"debug":"hidden"}}'
            ),
        )
        db.add(snapshot)
        db.flush()
        commit_point = CommitPoint(session_id=db_session.id, tick=3, snapshot_id=snapshot.id)
        db.add(commit_point)
        db.flush()
        branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="main",
            commit_point_id=commit_point.id,
            tick=3,
            snapshot_reference=snapshot.id,
            is_main=True,
        )
        db.add(branch)
        db.flush()
        snapshot.branch_id = branch.id
        db.add_all(
            [
                Event(
                    session_id=db_session.id,
                    branch_id=branch.id,
                    tick=2,
                    event_kind="world_weather",
                    payload_json='{"text":"Light rain starts","private_prompt":"hidden","hidden_context":"debug"}',
                ),
                Event(
                    session_id=db_session.id,
                    branch_id=branch.id,
                    tick=3,
                    event_kind="agent_life",
                    payload_json='{"agent_id":"agent-1","text":"Ada opens a stall","thoughts":"hidden","reasoning":"hidden"}',
                ),
            ]
        )
        db.commit()
        session_id = db_session.id

    response = client.get(f"/sessions/{session_id}/runtime-view")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["worldengine_world_id"] == "world-123"
    assert payload["world_status"] == "running"
    assert payload["tick"] == 3
    assert payload["visualization"]["tiles"] == [{"x": 0, "y": 0, "terrain": "grass"}]
    assert payload["visualization"]["entities"] == [{"id": "agent-1", "x": 1, "y": 2, "sprite": "person"}]
    assert "raw_response" not in payload["visualization"]
    assert payload["public_agents"] == [
        {
            "agent_id": "agent-1",
            "display_name": "Ada",
            "location": "market",
            "public_status": "walking",
            "visible_action": "trading",
            "payload": {},
        }
    ]
    assert payload["world_log"][0]["text"] == "Light rain starts"
    assert "private_prompt" not in payload["world_log"][0]["payload"]
    assert "hidden_context" not in payload["world_log"][0]["payload"]
    assert payload["agent_life_log"][0]["agent_id"] == "agent-1"
    assert payload["agent_life_log"][0]["text"] == "Ada opens a stall"
    assert "thoughts" not in payload["agent_life_log"][0]["payload"]
    assert "reasoning" not in payload["agent_life_log"][0]["payload"]
    assert payload["latest_event"]["event_kind"] == "agent_life"


def test_runtime_view_uses_main_branch_snapshot_and_events(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(session_name="Branch Runtime", public_world_status="running")
        db.add(db_session)
        db.flush()

        main_snapshot = Snapshot(
            session_id=db_session.id,
            tick=2,
            snapshot_json='{"visualization":{"tiles":[{"x":0,"y":0,"terrain":"main"}]}}',
        )
        other_snapshot = Snapshot(
            session_id=db_session.id,
            tick=9,
            snapshot_json='{"visualization":{"tiles":[{"x":9,"y":9,"terrain":"other"}]}}',
        )
        db.add_all([main_snapshot, other_snapshot])
        db.flush()

        main_commit = CommitPoint(session_id=db_session.id, tick=2, snapshot_id=main_snapshot.id)
        other_commit = CommitPoint(session_id=db_session.id, tick=9, snapshot_id=other_snapshot.id)
        db.add_all([main_commit, other_commit])
        db.flush()

        main_branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="main",
            commit_point_id=main_commit.id,
            tick=2,
            snapshot_reference=main_snapshot.id,
            is_main=True,
        )
        other_branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="experiment",
            commit_point_id=other_commit.id,
            tick=9,
            snapshot_reference=other_snapshot.id,
            is_main=False,
        )
        db.add_all([main_branch, other_branch])
        db.flush()
        main_snapshot.branch_id = main_branch.id
        other_snapshot.branch_id = other_branch.id
        db.add_all(
            [
                Event(
                    session_id=db_session.id,
                    branch_id=main_branch.id,
                    tick=2,
                    event_kind="world_main",
                    payload_json='{"text":"Main event"}',
                ),
                Event(
                    session_id=db_session.id,
                    branch_id=other_branch.id,
                    tick=9,
                    event_kind="world_other",
                    payload_json='{"text":"Other event"}',
                ),
            ]
        )
        db.commit()
        session_id = db_session.id

    response = client.get(f"/sessions/{session_id}/runtime-view")

    assert response.status_code == 200
    payload = response.json()
    assert payload["tick"] == 2
    assert payload["visualization"]["tiles"] == [{"x": 0, "y": 0, "terrain": "main"}]
    assert [item["event_kind"] for item in payload["world_log"]] == ["world_main"]


def test_runtime_view_without_main_branch_does_not_mix_branch_data(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(session_name="No Main Runtime", public_world_status="created")
        db.add(db_session)
        db.flush()
        snapshot = Snapshot(
            session_id=db_session.id,
            tick=7,
            snapshot_json='{"visualization":{"tiles":[{"x":7,"y":7,"terrain":"orphan"}]}}',
        )
        db.add(snapshot)
        db.flush()
        commit_point = CommitPoint(session_id=db_session.id, tick=7, snapshot_id=snapshot.id)
        db.add(commit_point)
        db.flush()
        branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="experiment",
            commit_point_id=commit_point.id,
            tick=7,
            snapshot_reference=snapshot.id,
            is_main=False,
        )
        db.add(branch)
        db.flush()
        snapshot.branch_id = branch.id
        db.add(
            Event(
                session_id=db_session.id,
                branch_id=branch.id,
                tick=7,
                event_kind="world_orphan",
                payload_json='{"text":"Should not appear"}',
            )
        )
        db.commit()
        session_id = db_session.id

    response = client.get(f"/sessions/{session_id}/runtime-view")

    assert response.status_code == 200
    payload = response.json()
    assert payload["tick"] == 0
    assert payload["visualization"] == {}
    assert payload["world_log"] == []
    assert payload["latest_event"] is None


def test_runtime_view_returns_404_for_missing_session(client):
    response = client.get("/sessions/missing/runtime-view")

    assert response.status_code == 404


def test_replay_view_reconstructs_public_branch_tick_from_snapshot_and_diffs(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(
            session_name="Replay Session",
            worldengine_world_id="world-123",
            public_world_status="running",
        )
        db.add(db_session)
        db.flush()
        snapshot = Snapshot(
            session_id=db_session.id,
            tick=1,
            snapshot_json=(
                '{"visualization":{"tiles":[{"x":0,"y":0,"terrain":"grass"}]},'
                '"initial_state":{"agents":[{"id":"agent-1","display_name":"Ada",'
                '"public_status":"walking","memory":"private"}]}}'
            ),
        )
        db.add(snapshot)
        db.flush()
        commit_point = CommitPoint(session_id=db_session.id, tick=1, snapshot_id=snapshot.id)
        db.add(commit_point)
        db.flush()
        branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="main",
            commit_point_id=commit_point.id,
            tick=3,
            snapshot_reference=snapshot.id,
            is_main=True,
        )
        db.add(branch)
        db.flush()
        snapshot.branch_id = branch.id
        db.add_all(
            [
                StateDiff(
                    session_id=db_session.id,
                    branch_id=branch.id,
                    tick=2,
                    diff_json=(
                        '{"visualization":{"tiles":[{"x":1,"y":0,"terrain":"road",'
                        '"private_path":"/tmp/hidden"}]},'
                        '"initial_state":{"agents":[{"id":"agent-1","display_name":"Ada",'
                        '"public_status":"trading","thought":"hidden"}]},'
                        '"private_prompt":"hidden"}'
                    ),
                ),
                StateDiff(
                    session_id=db_session.id,
                    branch_id=branch.id,
                    tick=4,
                    diff_json='{"visualization":{"tiles":[{"x":4,"y":0,"terrain":"future"}]}}',
                ),
                Event(
                    session_id=db_session.id,
                    branch_id=branch.id,
                    tick=2,
                    event_kind="world_change",
                    payload_json='{"text":"Road appears","secret":"hidden"}',
                ),
                Event(
                    session_id=db_session.id,
                    branch_id=branch.id,
                    tick=4,
                    event_kind="world_future",
                    payload_json='{"text":"Future should not appear"}',
                ),
            ]
        )
        db.commit()
        session_id = db_session.id
        branch_id = branch.id
        snapshot_id = snapshot.id

    response = client.get(f"/sessions/{session_id}/replay-view", params={"branch_id": branch_id, "tick": 3})

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["branch_id"] == branch_id
    assert payload["snapshot_id"] == snapshot_id
    assert payload["tick"] == 3
    assert payload["visualization"]["tiles"] == [{"x": 1, "y": 0, "terrain": "road"}]
    assert payload["public_agents"][0]["public_status"] == "trading"
    assert "memory" not in str(payload)
    assert "thought" not in str(payload)
    assert "private_prompt" not in str(payload)
    assert "private_path" not in str(payload)
    assert payload["world_log"][0]["text"] == "Road appears"
    assert payload["latest_event"]["event_kind"] == "world_change"


def test_replay_view_defaults_to_main_branch_and_rejects_tick_before_snapshot(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(session_name="Replay Main", public_world_status="running")
        db.add(db_session)
        db.flush()
        snapshot = Snapshot(
            session_id=db_session.id,
            tick=5,
            snapshot_json='{"visualization":{"tiles":[{"x":5,"y":0,"terrain":"main"}]}}',
        )
        db.add(snapshot)
        db.flush()
        commit_point = CommitPoint(session_id=db_session.id, tick=5, snapshot_id=snapshot.id)
        db.add(commit_point)
        db.flush()
        main_branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="main",
            commit_point_id=commit_point.id,
            tick=5,
            snapshot_reference=snapshot.id,
            is_main=True,
        )
        db.add(main_branch)
        db.flush()
        snapshot.branch_id = main_branch.id
        db.commit()
        session_id = db_session.id
        branch_id = main_branch.id

    ok_response = client.get(f"/sessions/{session_id}/replay-view", params={"tick": 5})
    early_response = client.get(f"/sessions/{session_id}/replay-view", params={"tick": 4})

    assert ok_response.status_code == 200
    assert ok_response.json()["branch_id"] == branch_id
    assert early_response.status_code == 422
    assert "No replay snapshot" in early_response.json()["detail"]


def test_replay_view_uses_commit_point_snapshot_immediately_after_branch_creation(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(session_name="Fork Replay", public_world_status="running")
        db.add(db_session)
        db.flush()
        snapshot = Snapshot(
            session_id=db_session.id,
            tick=2,
            snapshot_json='{"visualization":{"tiles":[{"x":2,"y":0,"terrain":"market"}]}}',
        )
        db.add(snapshot)
        db.flush()
        commit_point = CommitPoint(session_id=db_session.id, tick=2, snapshot_id=snapshot.id)
        db.add(commit_point)
        db.flush()
        main_branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="main",
            commit_point_id=commit_point.id,
            tick=2,
            snapshot_reference=snapshot.id,
            is_main=True,
        )
        db.add(main_branch)
        db.flush()
        snapshot.branch_id = main_branch.id
        db.add_all(
            [
                StateDiff(
                    session_id=db_session.id,
                    branch_id=main_branch.id,
                    tick=3,
                    diff_json='{"visualization":{"tiles":[{"x":3,"y":0,"terrain":"main-future"}]}}',
                ),
                Event(
                    session_id=db_session.id,
                    branch_id=main_branch.id,
                    tick=3,
                    event_kind="world_main_future",
                    payload_json='{"text":"Main future should not appear"}',
                ),
            ]
        )
        db.commit()
        session_id = db_session.id
        commit_point_id = commit_point.id

    branch_response = client.post(
        f"/sessions/{session_id}/branches",
        json={"branch_name": "market-fork", "commit_point_id": commit_point_id},
    )
    branch_id = branch_response.json()["id"]

    replay_response = client.get(f"/sessions/{session_id}/replay-view", params={"branch_id": branch_id, "tick": 2})

    assert branch_response.status_code == 201
    assert replay_response.status_code == 200
    payload = replay_response.json()
    assert payload["branch_id"] == branch_id
    assert payload["snapshot_id"] == snapshot.id
    assert payload["tick"] == 2
    assert payload["visualization"]["tiles"] == [{"x": 2, "y": 0, "terrain": "market"}]
    assert payload["world_log"] == []
    assert payload["latest_event"] is None

    with SessionLocal() as db:
        db.add_all(
            [
                StateDiff(
                    session_id=session_id,
                    branch_id=branch_id,
                    tick=3,
                    diff_json='{"visualization":{"tiles":[{"x":3,"y":0,"terrain":"fork-road"}]}}',
                ),
                Event(
                    session_id=session_id,
                    branch_id=branch_id,
                    tick=3,
                    event_kind="world_fork_change",
                    payload_json='{"text":"Fork road appears"}',
                ),
            ]
        )
        db.commit()

    branch_replay_response = client.get(
        f"/sessions/{session_id}/replay-view",
        params={"branch_id": branch_id, "tick": 3},
    )

    assert branch_replay_response.status_code == 200
    branch_payload = branch_replay_response.json()
    assert branch_payload["visualization"]["tiles"] == [{"x": 3, "y": 0, "terrain": "fork-road"}]
    assert branch_payload["world_log"][0]["text"] == "Fork road appears"
    assert branch_payload["latest_event"]["event_kind"] == "world_fork_change"
    assert "main-future" not in str(branch_payload)
    assert "Main future should not appear" not in str(branch_payload)


def test_replay_view_prefers_branch_local_snapshot_over_referenced_snapshot(client):
    SessionLocal = get_sessionmaker()
    with SessionLocal() as db:
        db_session = DbSession(session_name="Branch Local Snapshot", public_world_status="running")
        db.add(db_session)
        db.flush()
        source_snapshot = Snapshot(
            session_id=db_session.id,
            tick=2,
            snapshot_json='{"visualization":{"tiles":[{"x":2,"y":0,"terrain":"source"}]}}',
        )
        branch_snapshot = Snapshot(
            session_id=db_session.id,
            tick=2,
            snapshot_json='{"visualization":{"tiles":[{"x":2,"y":1,"terrain":"branch-local"}]}}',
        )
        db.add_all([source_snapshot, branch_snapshot])
        db.flush()
        commit_point = CommitPoint(session_id=db_session.id, tick=2, snapshot_id=source_snapshot.id)
        db.add(commit_point)
        db.flush()
        branch = TimelineBranch(
            session_id=db_session.id,
            branch_name="fork",
            commit_point_id=commit_point.id,
            tick=2,
            snapshot_reference=source_snapshot.id,
            is_main=False,
        )
        db.add(branch)
        db.flush()
        branch_snapshot.branch_id = branch.id
        db.commit()
        session_id = db_session.id
        branch_id = branch.id
        branch_snapshot_id = branch_snapshot.id

    response = client.get(f"/sessions/{session_id}/replay-view", params={"branch_id": branch_id, "tick": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["snapshot_id"] == branch_snapshot_id
    assert payload["visualization"]["tiles"] == [{"x": 2, "y": 1, "terrain": "branch-local"}]
