from __future__ import annotations

import json
from typing import Any, Dict

import httpx

from .config import get_settings


PRIVATE_PAYLOAD_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "file_path",
    "helper",
    "internal",
    "key",
    "oracle",
    "password",
    "path",
    "private",
    "prompt",
    "provider",
    "secret",
    "source_path",
    "token",
)

PRIVATE_ENDPOINT_PARTS = ("/internal", "/private", "/helpers", "/helper")


def _public_payload_summary(value: Any) -> Any:
    if isinstance(value, dict):
        summary = {}
        for key, item in value.items():
            lowered_key = str(key).lower()
            if any(part in lowered_key for part in PRIVATE_PAYLOAD_KEY_PARTS):
                continue
            summary[key] = _public_payload_summary(item)
        return summary
    if isinstance(value, list):
        return [_public_payload_summary(item) for item in value]
    return value


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
        if any(part in normalized_path for part in PRIVATE_ENDPOINT_PARTS):
            continue
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


async def create_world_via_public_api(world_prompt: str) -> Dict[str, Any]:
    base_url = get_settings().worldengine_api_base.rstrip("/")
    async with httpx.AsyncClient(timeout=10.0) as client:
        openapi_resp = await client.get(f"{base_url}/openapi.json")
        openapi_resp.raise_for_status()
        openapi_payload = openapi_resp.json()
        endpoint = _world_creation_endpoint(openapi_payload)
        if endpoint is None:
            raise RuntimeError("WorldEngine public world creation endpoint not found")

        url_path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        create_resp = await client.post(f"{base_url}{url_path}", json={"world_prompt": world_prompt})
        create_resp.raise_for_status()
        payload = create_resp.json()

    world_id = payload.get("world_id") or payload.get("id")
    if not world_id:
        raise RuntimeError("WorldEngine response did not include public world id")
    status = payload.get("status", "created")
    initial_state = _public_payload_summary(payload.get("initial_state") or payload.get("public_initial_state") or {})
    visualization = _public_payload_summary(payload.get("visualization") or payload.get("visualization_payload") or {})
    initial_state_summary = json.dumps(initial_state)
    visualization_payload_summary = json.dumps(visualization)
    response_summary = {"world_id": world_id, "status": status}
    return {
        "world_id": world_id,
        "status": status,
        "initial_state_summary": initial_state_summary,
        "visualization_payload_summary": visualization_payload_summary,
        "snapshot_json": json.dumps({"initial_state": initial_state, "visualization": visualization}),
        "event_payload_json": json.dumps(response_summary),
        "api_trace": {
            "method": "POST",
            "url_path": url_path,
            "status_code": create_resp.status_code,
            "request_summary_json": json.dumps({"world_prompt_length": len(world_prompt)}),
            "response_summary_json": json.dumps(response_summary),
            "error_message": None,
        },
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
            result["reachable"] = True
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

        try:
            openapi_resp = await client.get(f"{base_url}/openapi.json")
            openapi_resp.raise_for_status()
            result["openapi"] = _summarize_openapi(openapi_resp.json())
            result["capabilities"]["openapi_available"] = True
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"openapi: {str(exc)}")

    if result["openapi"] and result["openapi"]["world_creation_endpoint"]:
        result["capabilities"]["world_creation"] = "available"

    return result
