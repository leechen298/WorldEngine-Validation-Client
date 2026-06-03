from __future__ import annotations

from typing import Any, Dict

import httpx

from .config import get_settings


def _summarize_health(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": payload.get("status", "unknown")}


def _summarize_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"version": payload.get("version")}
    capabilities = payload.get("capabilities")
    if isinstance(capabilities, list):
        summary["capabilities"] = [str(item) for item in capabilities]
    return summary


def _world_creation_endpoint(openapi: Dict[str, Any] | None) -> str | None:
    if not openapi:
        return None
    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        return None
    for path, methods in paths.items():
        if not isinstance(methods, dict) or "post" not in methods:
            continue
        normalized_path = str(path).rstrip("/").lower()
        operation = methods.get("post")
        operation_id = ""
        tags: list[str] = []
        if isinstance(operation, dict):
            operation_id = str(operation.get("operationId", "")).lower()
            raw_tags = operation.get("tags", [])
            if isinstance(raw_tags, list):
                tags = [str(tag).lower() for tag in raw_tags]
        if normalized_path.endswith("/worlds"):
            return str(path)
        if operation_id in {"createworld", "create_world"}:
            return str(path)
        if "worlds" in tags and "create" in operation_id:
            return str(path)
    return None


def _summarize_openapi(payload: Dict[str, Any]) -> Dict[str, Any]:
    info = payload.get("info") if isinstance(payload.get("info"), dict) else {}
    return {
        "title": info.get("title"),
        "version": info.get("version"),
        "world_creation_endpoint": _world_creation_endpoint(payload),
    }


async def check_worldengine_health() -> Dict[str, Any]:
    base_url = get_settings().worldengine_api_base.rstrip("/")
    result = {
        "reachable": False,
        "health": None,
        "manifest": None,
        "openapi": None,
        "capabilities": {
            "manifest_available": False,
            "openapi_available": False,
            "world_creation": "unknown",
        },
        "errors": [],
    }

    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            health_resp = await client.get(f"{base_url}/health")
            health_resp.raise_for_status()
            result["health"] = _summarize_health(health_resp.json())
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"health: {str(exc)}")
            return result

        try:
            manifest_resp = await client.get(f"{base_url}/manifest")
            manifest_resp.raise_for_status()
            result["manifest"] = _summarize_manifest(manifest_resp.json())
            result["capabilities"]["manifest_available"] = True
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"manifest: {str(exc)}")
            return result

        try:
            openapi_resp = await client.get(f"{base_url}/openapi.json")
            openapi_resp.raise_for_status()
            result["openapi"] = _summarize_openapi(openapi_resp.json())
            result["capabilities"]["openapi_available"] = True
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"openapi: {str(exc)}")

    if result["openapi"] and result["openapi"]["world_creation_endpoint"]:
        result["capabilities"]["world_creation"] = "available"

    result["reachable"] = True
    return result
