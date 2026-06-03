import httpx
import pytest

from app.db import get_sessionmaker
from app.models import ApiTrace, CommitPoint, Event, Session as DbSession, Snapshot
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
