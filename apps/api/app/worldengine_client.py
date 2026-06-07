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
    "goal",
    "helper",
    "hidden_context",
    "identity",
    "internal",
    "key",
    "memory",
    "oracle",
    "password",
    "path",
    "private",
    "prompt",
    "provider",
    "relationship",
    "secret",
    "source_path",
    "self_state",
    "thought",
    "token",
)

PRIVATE_ENDPOINT_PARTS = ("/internal", "/private", "/helpers", "/helper")

V0_9_PUBLIC_SURFACE_SPECS: dict[str, tuple[str, str]] = {
    "provider_live_smoke": ("POST", "/provider/live-smoke"),
    "worldview_generation": ("POST", "/world/generation/worldview"),
    "world_creation": ("POST", "/worlds"),
    "runtime_state": ("GET", "/runtime/state"),
    "runtime_step": ("POST", "/runtime/step"),
    "runtime_run": ("POST", "/runtime/run"),
    "runtime_pause": ("POST", "/runtime/pause"),
    "runtime_resume": ("POST", "/runtime/resume"),
    "world_events": ("GET", "/world/events"),
    "world_event_steps": ("GET", "/world/event-steps"),
    "archive_snapshots": ("GET", "/archive/snapshots"),
    "world_params": ("GET", "/world/params"),
    "world_direction": ("POST", "/worlds/{world_id}/direction"),
    "director_guidance": ("POST", "/worlds/{world_id}/director-guidance"),
    "event_legality_evaluate": ("POST", "/worlds/{world_id}/evolution/evaluate-event"),
    "agent_continuity_evaluate": ("POST", "/worlds/{world_id}/agents/{agent_id}/continuity/evaluate"),
    "narrative_project": ("POST", "/worlds/{world_id}/narrative/project"),
    "diagnostic_dialogue_evaluate": (
        "POST",
        "/worlds/{world_id}/agents/{agent_id}/diagnostics/dialogue/evaluate",
    ),
}


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


def _discover_v0_9_public_surfaces(openapi: Dict[str, Any] | None) -> Dict[str, Dict[str, str | None]]:
    if not openapi:
        return {
            name: {"status": "not_run", "method": method, "path": path}
            for name, (method, path) in V0_9_PUBLIC_SURFACE_SPECS.items()
        }
    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        return {
            name: {"status": "blocked", "method": method, "path": path}
            for name, (method, path) in V0_9_PUBLIC_SURFACE_SPECS.items()
        }

    public_paths: dict[str, tuple[str, dict[str, Any]]] = {}
    for raw_path, methods in paths.items():
        path = str(raw_path)
        normalized = path.rstrip("/").lower()
        if any(part in normalized for part in PRIVATE_ENDPOINT_PARTS):
            continue
        if isinstance(methods, dict):
            public_paths[normalized] = (path, methods)

    surfaces: Dict[str, Dict[str, str | None]] = {}
    for name, (method, expected_path) in V0_9_PUBLIC_SURFACE_SPECS.items():
        normalized_expected = expected_path.rstrip("/").lower()
        matched = public_paths.get(normalized_expected)
        status = "blocked"
        actual_path = expected_path
        if matched is not None:
            actual_path, methods = matched
            if method.lower() in {str(item).lower() for item in methods}:
                status = "available"
        surfaces[name] = {"status": status, "method": method, "path": actual_path}
    return surfaces


def _summarize_v0_9_validation_status(surfaces: Dict[str, Dict[str, str | None]], openapi_available: bool) -> str:
    if not openapi_available:
        return "not_run"
    if all(item.get("status") == "available" for item in surfaces.values()):
        return "available"
    return "blocked"


def _director_guidance_endpoint(openapi: Dict[str, Any] | None) -> str | None:
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
        path_mentions_director = "director" in normalized_path
        path_mentions_guidance = "guidance" in normalized_path or "intent" in normalized_path
        operation_mentions_director = "director" in operation_id or "director" in tags
        operation_mentions_guidance = "guidance" in operation_id or "intent" in operation_id
        if path_mentions_director and path_mentions_guidance:
            return str(path)
        if operation_mentions_director and operation_mentions_guidance:
            return str(path)
    return None


def _summarize_openapi(payload: Dict[str, Any]) -> Dict[str, Any]:
    info = payload.get("info") if isinstance(payload.get("info"), dict) else {}
    return {
        "title": info.get("title"),
        "version": info.get("version"),
        "world_creation_endpoint": _world_creation_endpoint(payload),
        "v0_9_public_surfaces": _discover_v0_9_public_surfaces(payload),
    }


def _format_director_guidance_path(endpoint: str, world_id: str) -> str:
    url_path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    return url_path.replace("{world_id}", world_id).replace("{worldId}", world_id)


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


async def submit_director_guidance_via_public_api(
    *,
    world_id: str,
    instruction_text: str,
    branch_id: str | None,
    tick: int,
    public_context: Dict[str, Any],
) -> Dict[str, Any]:
    base_url = get_settings().worldengine_api_base.rstrip("/")
    async with httpx.AsyncClient(timeout=10.0) as client:
        openapi_resp = await client.get(f"{base_url}/openapi.json")
        openapi_resp.raise_for_status()
        openapi_payload = openapi_resp.json()
        endpoint = _director_guidance_endpoint(openapi_payload)
        if endpoint is None:
            raise RuntimeError("WorldEngine public director guidance endpoint not found")

        request_payload = {
            "instruction_text": instruction_text,
            "branch_id": branch_id,
            "tick": tick,
            "public_context": _public_payload_summary(public_context),
        }
        url_path = _format_director_guidance_path(endpoint, world_id)
        submit_resp = await client.post(f"{base_url}{url_path}", json=request_payload)
        submit_resp.raise_for_status()
        payload = _public_payload_summary(submit_resp.json())

    status = str(payload.get("status") or "accepted")
    public_explanation = payload.get("public_explanation") or payload.get("explanation")
    applied_event_id = payload.get("applied_event_id") or payload.get("event_id")
    error_message = payload.get("error_message")
    response_summary = {
        "status": status,
        "public_explanation_length": len(str(public_explanation)) if public_explanation is not None else 0,
        "applied_event_id": applied_event_id,
        "error_message": error_message,
    }
    return {
        "status": status,
        "public_explanation": public_explanation,
        "applied_event_id": applied_event_id,
        "error_message": error_message,
        "api_trace": {
            "method": "POST",
            "url_path": endpoint if endpoint.startswith("/") else f"/{endpoint}",
            "status_code": submit_resp.status_code,
            "request_summary_json": json.dumps(
                {
                    "world_id": world_id,
                    "instruction_text_length": len(instruction_text),
                    "branch_id": branch_id,
                    "tick": tick,
                    "public_context": _public_payload_summary(public_context),
                }
            ),
            "response_summary_json": json.dumps(_public_payload_summary(response_summary)),
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
            "v0_9_validation": "not_run",
            "v0_9_public_surfaces": {
                name: "not_run" for name in V0_9_PUBLIC_SURFACE_SPECS
            },
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
            v0_9_surfaces = result["openapi"]["v0_9_public_surfaces"]
            result["capabilities"]["v0_9_public_surfaces"] = {
                name: str(surface["status"]) for name, surface in v0_9_surfaces.items()
            }
            result["capabilities"]["v0_9_validation"] = _summarize_v0_9_validation_status(
                v0_9_surfaces,
                openapi_available=True,
            )
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"openapi: {str(exc)}")

    if result["openapi"] and result["openapi"]["world_creation_endpoint"]:
        result["capabilities"]["world_creation"] = "available"

    return result
