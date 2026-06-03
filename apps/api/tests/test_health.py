import pytest
import httpx

from app.config import get_settings, _resolve_database_path
from app.worldengine_client import check_worldengine_health


def test_health_route_returns_local_status(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "worldengine-validation-client"
    assert payload["worldengine_api_base"] == get_settings().worldengine_api_base
    assert payload["database_path"] == get_settings().database_path


def test_default_database_path_is_under_api_app(monkeypatch):
    monkeypatch.chdir("/tmp")
    assert _resolve_database_path(".worldengine-validation-client/client.sqlite3").endswith(
        "apps/api/.worldengine-validation-client/client.sqlite3"
    )


@pytest.mark.asyncio
async def test_health_worldengine_route_returns_remote_status(client, monkeypatch):
    async def fake_health():
        return {
            "reachable": True,
            "health": {"status": "ok"},
            "manifest": {"version": "0.0.1"},
            "openapi": {"title": "WorldEngine", "version": None, "world_creation_endpoint": None},
            "capabilities": {
                "manifest_available": True,
                "openapi_available": True,
                "world_creation": "unknown",
            },
            "errors": [],
        }

    monkeypatch.setattr("app.routes.health.check_worldengine_health", fake_health)
    response = client.get("/health/worldengine")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["worldengine"]["reachable"] is True
    assert payload["worldengine"]["manifest"]["version"] == "0.0.1"


@pytest.mark.asyncio
async def test_worldengine_client_fetches_public_health_manifest_and_openapi(monkeypatch):
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/manifest":
            return httpx.Response(200, json={"version": "0.1.0", "capabilities": ["public"]})
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json={"info": {"title": "WorldEngine"}, "paths": {"/worlds": {"post": {}}}})
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

    result = await check_worldengine_health()

    assert result["reachable"] is True
    assert result["health"] == {"status": "ok"}
    assert result["manifest"] == {"version": "0.1.0", "capabilities": ["public"]}
    assert result["openapi"] == {
        "title": "WorldEngine",
        "version": None,
        "world_creation_endpoint": "/worlds",
    }
    assert result["capabilities"] == {
        "manifest_available": True,
        "openapi_available": True,
        "world_creation": "available",
    }
    assert requests == [
        "http://worldengine.example/health",
        "http://worldengine.example/manifest",
        "http://worldengine.example/openapi.json",
    ]


@pytest.mark.asyncio
async def test_worldengine_client_keeps_health_reachable_when_openapi_fails(monkeypatch):
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/manifest":
            return httpx.Response(200, json={"version": "0.1.0"})
        if request.url.path == "/openapi.json":
            return httpx.Response(404, json={"detail": "not found"})
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

    result = await check_worldengine_health()

    assert result["reachable"] is True
    assert result["openapi"] is None
    assert result["capabilities"] == {
        "manifest_available": True,
        "openapi_available": False,
        "world_creation": "unknown",
    }
    assert len(result["errors"]) == 1
    assert result["errors"][0].startswith(
        "openapi: Client error '404 Not Found' for url 'http://worldengine.example/openapi.json'"
    )
    assert requests == [
        "http://worldengine.example/health",
        "http://worldengine.example/manifest",
        "http://worldengine.example/openapi.json",
    ]


@pytest.mark.asyncio
async def test_worldengine_client_keeps_health_reachable_when_manifest_fails(monkeypatch):
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/manifest":
            return httpx.Response(500, json={"detail": "boom"})
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json={"info": {"title": "WorldEngine"}, "paths": {}})
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

    result = await check_worldengine_health()

    assert result["reachable"] is True
    assert result["health"] == {"status": "ok"}
    assert result["manifest"] is None
    assert result["openapi"] == {
        "title": "WorldEngine",
        "version": None,
        "world_creation_endpoint": None,
    }
    assert result["capabilities"] == {
        "manifest_available": False,
        "openapi_available": True,
        "world_creation": "unknown",
    }
    assert len(result["errors"]) == 1
    assert result["errors"][0].startswith(
        "manifest: Server error '500 Internal Server Error' for url 'http://worldengine.example/manifest'"
    )
    assert requests == [
        "http://worldengine.example/health",
        "http://worldengine.example/manifest",
        "http://worldengine.example/openapi.json",
    ]


@pytest.mark.asyncio
async def test_worldengine_client_returns_safe_discovery_summaries(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "api_key": "secret", "internal_helper": "x"})
        if request.url.path == "/manifest":
            return httpx.Response(
                200,
                json={
                    "version": "0.1.0",
                    "capabilities": ["public"],
                    "provider_secret": "secret",
                    "source_path": "/tmp/worldengine",
                },
            )
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200,
                json={
                    "info": {"title": "WorldEngine", "version": "0.2.0"},
                    "paths": {"/worlds": {"post": {"operationId": "createWorld"}}},
                    "private_path": "/tmp/worldengine",
                    "x-internal-helper": "helper",
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

    result = await check_worldengine_health()

    assert result["health"] == {"status": "ok"}
    assert result["manifest"] == {"version": "0.1.0", "capabilities": ["public"]}
    assert result["openapi"] == {
        "title": "WorldEngine",
        "version": "0.2.0",
        "world_creation_endpoint": "/worlds",
    }


@pytest.mark.asyncio
async def test_worldengine_client_does_not_guess_world_creation_from_unrelated_world_post(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/manifest":
            return httpx.Response(200, json={"version": "0.1.0"})
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200,
                json={"paths": {"/world-events": {"post": {"operationId": "createWorldEvent"}}}},
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

    result = await check_worldengine_health()

    assert result["capabilities"]["world_creation"] == "unknown"
    assert result["openapi"]["world_creation_endpoint"] is None


@pytest.mark.asyncio
async def test_worldengine_client_does_not_guess_world_creation_from_summary_only(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/manifest":
            return httpx.Response(200, json={"version": "0.1.0"})
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200,
                json={"paths": {"/events": {"post": {"summary": "Create world event"}}}},
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

    result = await check_worldengine_health()

    assert result["capabilities"]["world_creation"] == "unknown"
    assert result["openapi"]["world_creation_endpoint"] is None
