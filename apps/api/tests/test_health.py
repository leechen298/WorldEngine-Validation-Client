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
async def test_worldengine_client_fetches_public_health_and_manifest(monkeypatch):
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/manifest":
            return httpx.Response(200, json={"version": "0.1.0", "capabilities": ["public"]})
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
    assert requests == ["http://worldengine.example/health", "http://worldengine.example/manifest"]
