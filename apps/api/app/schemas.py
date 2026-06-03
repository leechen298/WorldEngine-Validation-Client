from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    worldengine_api_base: str
    database_path: str


class WorldEngineCapabilitySummary(BaseModel):
    manifest_available: bool
    openapi_available: bool
    world_creation: str


class WorldEngineHealthSummary(BaseModel):
    status: str


class WorldEngineManifestSummary(BaseModel):
    version: Optional[str]
    capabilities: List[str] = []


class WorldEngineOpenAPISummary(BaseModel):
    title: Optional[str]
    version: Optional[str]
    world_creation_endpoint: Optional[str]


class WorldEngineProbeResponse(BaseModel):
    reachable: bool
    health: Optional[WorldEngineHealthSummary]
    manifest: Optional[WorldEngineManifestSummary]
    openapi: Optional[WorldEngineOpenAPISummary]
    capabilities: WorldEngineCapabilitySummary
    errors: List[str]


class HealthWorldEngineResponse(BaseModel):
    status: str
    worldengine: WorldEngineProbeResponse


class SessionCreatePayload(BaseModel):
    session_name: str = Field(min_length=1, max_length=120)


class WorldEngineSessionCreatePayload(BaseModel):
    session_name: str = Field(min_length=1, max_length=120)
    world_prompt: str = Field(min_length=1, max_length=5000)


class SessionSummary(BaseModel):
    id: str
    session_name: str
    status: str
    worldengine_world_id: Optional[str]
    public_world_status: Optional[str]
    initial_state_summary: Optional[str]
    visualization_payload_summary: Optional[str]
    branch_count: int
    main_branch_id: Optional[str]
    main_commit_point_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class SessionListResponse(BaseModel):
    sessions: List[SessionSummary]


class CommitPointRef(BaseModel):
    id: str
    tick: int
    created_at: datetime


class BranchCreatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_name: str = Field(min_length=1, max_length=120)
    commit_point_id: str = Field(min_length=1)


class BranchResponse(BaseModel):
    id: str
    branch_name: str
    commit_point_id: str
    tick: int
    current_tick: int
    snapshot_reference: Optional[str]
    is_main: bool
    created_at: datetime


class BranchListResponse(BaseModel):
    session_id: str
    branches: List[BranchResponse]


class EventResponse(BaseModel):
    id: str
    session_id: str
    branch_id: Optional[str]
    tick: int
    event_kind: str
    payload_json: str
    created_at: datetime


class DirectorIntentCreatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instruction_text: str = Field(min_length=1, max_length=5000)
    branch_id: Optional[str] = Field(default=None, min_length=1)
    tick: int = Field(default=0, ge=0)


class DirectorIntentResponse(BaseModel):
    id: str
    session_id: str
    branch_id: Optional[str]
    tick: int
    instruction_text: str
    status: str
    public_explanation: Optional[str]
    applied_event_id: Optional[str]
    error_message: Optional[str]
    created_at: datetime


class DirectorIntentListResponse(BaseModel):
    session_id: str
    director_intents: List[DirectorIntentResponse]


class PublicAgentState(BaseModel):
    agent_id: str
    display_name: Optional[str]
    location: Optional[str]
    public_status: Optional[str]
    visible_action: Optional[str]
    payload: Dict[str, Any] = Field(default_factory=dict)


class RuntimeLogItem(BaseModel):
    id: str
    tick: int
    event_kind: str
    text: str
    agent_id: Optional[str]
    payload: Dict[str, Any]
    created_at: datetime


class RuntimeViewResponse(BaseModel):
    session_id: str
    worldengine_world_id: Optional[str]
    world_status: str
    tick: int
    visualization: Dict[str, Any]
    public_agents: List[PublicAgentState]
    world_log: List[RuntimeLogItem]
    agent_life_log: List[RuntimeLogItem]
    latest_event: Optional[RuntimeLogItem]


class ReplayViewResponse(RuntimeViewResponse):
    branch_id: str
    snapshot_id: str


class EvidenceBundleMetadata(BaseModel):
    session_id: str
    session_name: str
    branches: int
    events: int
    state_diffs: int
    snapshots: int
    commit_points: int
    director_intents: int
    api_traces: int
    llm_keys_included: bool = False
    private_worldengine_internals_included: bool = False


class CommitPointResponse(BaseModel):
    id: str
    session_id: str
    tick: int
    event_id: Optional[str]
    snapshot_id: Optional[str]
    payload_summary: Optional[str]
    branch_ids: List[str] = []
    branch_names: List[str] = []
    created_at: datetime
