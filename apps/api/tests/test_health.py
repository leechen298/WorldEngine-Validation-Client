import pytest

from app.config import get_settings


def test_health_route_returns_local_status(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "worldengine-validation-client"
    assert payload["worldengine_api_base"] == get_settings().worldengine_api_base


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
