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
  current_tick: number;
  snapshot_reference: string | null;
  is_main: boolean;
  created_at: string;
}

export interface CommitPointSummary {
  id: string;
  session_id: string;
  tick: number;
  event_id: string | null;
  snapshot_id: string | null;
  payload_summary: string | null;
  branch_ids: string[];
  branch_names: string[];
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

export type DirectorIntentStatus = "pending" | "accepted" | "applied" | "rejected" | "failed" | string;

export interface DirectorIntent {
  id: string;
  session_id: string;
  branch_id: string | null;
  tick: number;
  instruction_text: string;
  status: DirectorIntentStatus;
  public_explanation: string | null;
  applied_event_id: string | null;
  error_message: string | null;
  created_at: string;
}

export interface CreateDirectorIntentRequest {
  instruction_text: string;
  branch_id?: string | null;
  tick?: number;
}

export interface PublicAgentState {
  agent_id: string;
  display_name: string | null;
  location: string | null;
  public_status: string | null;
  visible_action: string | null;
  payload: Record<string, unknown>;
}

export interface RuntimeLogItem {
  id: string;
  tick: number;
  event_kind: string;
  text: string;
  agent_id: string | null;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface RuntimeView {
  session_id: string;
  worldengine_world_id: string | null;
  world_status: string;
  tick: number;
  visualization: Record<string, unknown>;
  public_agents: PublicAgentState[];
  world_log: RuntimeLogItem[];
  agent_life_log: RuntimeLogItem[];
  latest_event: RuntimeLogItem | null;
}

export interface ReplayView extends RuntimeView {
  branch_id: string;
  snapshot_id: string;
}

export type EvidenceBundleWarning = string;

export interface EvidenceBundleCounts {
  branches: number;
  events: number;
  state_diffs: number;
  snapshots: number;
  commit_points: number;
  director_intents: number;
  api_traces: number;
  evaluator_outputs: number;
  replay_index: number;
}

export interface EvidenceBundleRedactionFlags {
  llm_keys_included: boolean;
  private_worldengine_internals_included: boolean;
}

export interface EvidenceBundleManifest {
  bundle_schema_version: string;
  generated_at: string;
  session_id: string;
  session_name: string;
  worldengine_world_id: string | null;
  world_status: string;
  counts: EvidenceBundleCounts;
  redaction_flags: EvidenceBundleRedactionFlags;
  warnings: EvidenceBundleWarning[];
}

export interface EvidenceBundleRecords {
  branches: Record<string, unknown>[];
  commit_points: Record<string, unknown>[];
  events: Record<string, unknown>[];
  state_diffs: Record<string, unknown>[];
  snapshots: Record<string, unknown>[];
  director_intents: Record<string, unknown>[];
  api_traces: Record<string, unknown>[];
  evaluator_outputs: Record<string, unknown>[];
  replay_index: Record<string, unknown>[];
}

export interface EvidenceBundleResponse {
  manifest: EvidenceBundleManifest;
  records: EvidenceBundleRecords;
}

export interface EvidenceBundleDownload {
  filename: string;
  bundle: EvidenceBundleResponse;
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
