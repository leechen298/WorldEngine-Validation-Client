from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    worldengine_api_base: str
    database_path: str


class HealthWorldEngineResponse(BaseModel):
    status: str
    worldengine: dict


class SessionCreatePayload(BaseModel):
    session_name: str = Field(min_length=1, max_length=120)


class SessionSummary(BaseModel):
    id: str
    session_name: str
    status: str
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
    snapshot_reference: Optional[str]
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


class EvidenceBundleMetadata(BaseModel):
    session_id: str
    session_name: str
    branches: int
    events: int
    state_diffs: int
    snapshots: int
    commit_points: int
    director_intents: int
    llm_keys_included: bool = False
    private_worldengine_internals_included: bool = False


class CommitPointResponse(BaseModel):
    id: str
    session_id: str
    tick: int
    event_id: Optional[str]
    snapshot_id: Optional[str]
    payload_json: Optional[str]
    created_at: datetime
