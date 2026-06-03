export interface HealthResponse {
  status: string;
  service: string;
  worldengine_api_base: string;
  database_path: string;
}

export interface HealthWorldEngineResponse {
  status: "ok" | "degraded";
  worldengine: {
    reachable: boolean;
    health: { status: string } | null;
    manifest: { version: string | null; capabilities: string[] } | null;
    openapi: { title: string | null; version: string | null; world_creation_endpoint: string | null } | null;
    capabilities: {
      manifest_available: boolean;
      openapi_available: boolean;
      world_creation: string;
    };
    errors: string[];
  };
}

export interface SessionSummary {
  id: string;
  session_name: string;
  status: string;
  worldengine_world_id: string | null;
  public_world_status: string | null;
  initial_state_summary: string | null;
  visualization_payload_summary: string | null;
  branch_count: number;
  main_branch_id: string | null;
  main_commit_point_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface BranchSummary {
  id: string;
  branch_name: string;
  commit_point_id: string;
  tick: number;
  snapshot_reference: string | null;
  created_at: string;
}

export interface SessionEvent {
  id: string;
  session_id: string;
  branch_id: string | null;
  tick: number;
  event_kind: string;
  payload_json: string;
  created_at: string;
}

export interface CreateSessionRequest {
  session_name: string;
}

export interface CreateWorldSessionRequest {
  session_name: string;
  world_prompt: string;
}

export interface CreateBranchRequest {
  branch_name: string;
  commit_point_id: string;
}
