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
    v0_9_validation: str = "not_run"
    v0_9_public_surfaces: Dict[str, str] = Field(default_factory=dict)


class WorldEngineHealthSummary(BaseModel):
    status: str


class WorldEngineManifestSummary(BaseModel):
    version: Optional[str]
    capabilities: List[str] = []


class WorldEngineOpenAPISummary(BaseModel):
    title: Optional[str]
    version: Optional[str]
    world_creation_endpoint: Optional[str]
    v0_9_public_surfaces: Dict[str, Dict[str, Optional[str]]] = Field(default_factory=dict)


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


class EvidenceBundleCounts(BaseModel):
    branches: int
    events: int
    state_diffs: int
    snapshots: int
    commit_points: int
    director_intents: int
    api_traces: int
    validation_runs: int = 0
    operation_log_entries: int = 0
    evaluator_outputs: int = 0
    replay_index: int = 0


class EvidenceBundleRedactionFlags(BaseModel):
    llm_keys_included: bool = False
    private_worldengine_internals_included: bool = False


class EvidenceBundleManifest(BaseModel):
    bundle_schema_version: str
    schema_version: str = "0.8.0"
    bundle_id: str
    scenario: str = "worldengine-full-lifecycle-autonomous"
    result_status: str = "blocked"
    client_role: str = "display_export_only"
    provider_owner: str = "worldengine"
    evaluator_role: str = "worldengine_checker_or_second_agent_review"
    generated_at: datetime
    session_id: str
    session_name: str
    worldengine_world_id: Optional[str]
    world_status: str
    latest_validation_run_id: Optional[str] = None
    evidence_bundle_filename: Optional[str] = None
    counts: EvidenceBundleCounts
    redaction_flags: EvidenceBundleRedactionFlags
    redaction_status: Dict[str, Any] = Field(default_factory=dict)
    artifact_index: List[Dict[str, Any]] = Field(default_factory=list)
    checker_contract: Dict[str, Any] = Field(default_factory=dict)
    unsupported_items: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class EvidenceBundleRecords(BaseModel):
    branches: List[Dict[str, Any]] = Field(default_factory=list)
    commit_points: List[Dict[str, Any]] = Field(default_factory=list)
    events: List[Dict[str, Any]] = Field(default_factory=list)
    state_diffs: List[Dict[str, Any]] = Field(default_factory=list)
    snapshots: List[Dict[str, Any]] = Field(default_factory=list)
    director_intents: List[Dict[str, Any]] = Field(default_factory=list)
    api_traces: List[Dict[str, Any]] = Field(default_factory=list)
    validation_runs: List[Dict[str, Any]] = Field(default_factory=list)
    operation_log_entries: List[Dict[str, Any]] = Field(default_factory=list)
    evaluator_outputs: List[Dict[str, Any]] = Field(default_factory=list)
    replay_index: List[Dict[str, Any]] = Field(default_factory=list)


class EvidenceBundleResponse(BaseModel):
    manifest: EvidenceBundleManifest
    records: EvidenceBundleRecords


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


class ValidationRunCreatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    actor: str = Field(default="codex", min_length=1, max_length=80)
    web_url: Optional[str] = Field(default=None, max_length=500)
    api_base_url: Optional[str] = Field(default=None, max_length=500)
    worldengine_api_base: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=2000)


class ValidationRunResponse(BaseModel):
    id: str
    session_id: str
    actor: str
    status: str
    web_url: Optional[str]
    api_base_url: Optional[str]
    worldengine_api_base: Optional[str]
    evidence_bundle_path: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class OperationLogCreatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: str = Field(default="codex", min_length=1, max_length=80)
    phase: str = Field(default="browser", min_length=1, max_length=80)
    url: Optional[str] = Field(default=None, max_length=500)
    action_type: str = Field(min_length=1, max_length=120)
    target_label: Optional[str] = Field(default=None, max_length=240)
    input_text: Optional[str] = Field(default=None, max_length=5000)
    request_method: Optional[str] = Field(default=None, max_length=20)
    request_path: Optional[str] = Field(default=None, max_length=500)
    response_status: Optional[int] = Field(default=None, ge=100, le=599)
    response_summary: Optional[str] = Field(default=None, max_length=5000)
    visible_result: Optional[str] = Field(default=None, max_length=5000)
    screenshot_path: Optional[str] = Field(default=None, max_length=500)
    downloaded_file: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=2000)


class OperationLogResponse(BaseModel):
    id: str
    run_id: str
    session_id: str
    timestamp: datetime
    actor: str
    phase: str
    url: Optional[str]
    action_type: str
    target_label: Optional[str]
    input_text: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    response_status: Optional[int]
    response_summary: Optional[str]
    visible_result: Optional[str]
    screenshot_path: Optional[str]
    downloaded_file: Optional[str]
    notes: Optional[str]


class OperationLogListResponse(BaseModel):
    run_id: str
    session_id: str
    entries: List[OperationLogResponse]


class ApiSummaryItem(BaseModel):
    method: str
    path: str
    status: Optional[int]
    public_summary: Dict[str, Any]
    error_class: Optional[str]


class ValidationRunApiSummaryResponse(BaseModel):
    run_id: str
    session_id: str
    api_calls: List[ApiSummaryItem]
