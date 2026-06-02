from __future__ import annotations

from typing import Any, Dict

import httpx

from .config import get_settings


async def check_worldengine_health() -> Dict[str, Any]:
    base_url = get_settings().worldengine_api_base.rstrip("/")
    result = {"reachable": False, "health": None, "manifest": None, "errors": []}

    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            health_resp = await client.get(f"{base_url}/health")
            health_resp.raise_for_status()
            result["health"] = health_resp.json()
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"health: {str(exc)}")
            return result

        try:
            manifest_resp = await client.get(f"{base_url}/manifest")
            manifest_resp.raise_for_status()
            result["manifest"] = manifest_resp.json()
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"manifest: {str(exc)}")
            return result

    result["reachable"] = True
    return result
