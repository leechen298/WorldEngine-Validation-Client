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
    openapi: {
      title: string | null;
      version: string | null;
      world_creation_endpoint: string | null;
      v0_9_public_surfaces?: Record<string, { status: string; method: string | null; path: string | null }>;
    } | null;
    capabilities: {
      manifest_available: boolean;
      openapi_available: boolean;
      world_creation: string;
      v0_9_validation?: string;
      v0_9_public_surfaces?: Record<string, string>;
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
  validation_runs: number;
  operation_log_entries: number;
  evaluator_outputs: number;
  replay_index: number;
}

export interface EvidenceBundleRedactionFlags {
  llm_keys_included: boolean;
  private_worldengine_internals_included: boolean;
}

export interface EvidenceBundleArtifactIndexItem {
  name: string;
  path: string;
  required: boolean;
  displayable: boolean;
  exportable: boolean;
  producer: string;
  schema_version: string;
  status: string;
  redaction_status: string;
}

export interface EvidenceBundleManifest {
  bundle_schema_version: string;
  schema_version?: string;
  bundle_id?: string;
  scenario?: string;
  result_status?: string;
  client_role?: string;
  provider_owner?: string;
  evaluator_role?: string;
  generated_at: string;
  session_id: string;
  session_name: string;
  worldengine_world_id: string | null;
  world_status: string;
  latest_validation_run_id: string | null;
  evidence_bundle_filename: string | null;
  counts: EvidenceBundleCounts;
  redaction_flags: EvidenceBundleRedactionFlags;
  redaction_status?: { status: string; blocking_flags: string[] };
  artifact_index?: EvidenceBundleArtifactIndexItem[];
  checker_contract?: Record<string, unknown>;
  unsupported_items?: string[];
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
  validation_runs: Record<string, unknown>[];
  operation_log_entries: Record<string, unknown>[];
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

export interface EvidenceArtifactsDownload {
  filename: string;
  artifacts: Record<string, unknown>;
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

export interface CreateValidationRunRequest {
  session_id: string;
  actor?: string;
  web_url?: string | null;
  api_base_url?: string | null;
  worldengine_api_base?: string | null;
  notes?: string | null;
}

export interface ValidationRun {
  id: string;
  session_id: string;
  actor: string;
  status: string;
  web_url: string | null;
  api_base_url: string | null;
  worldengine_api_base: string | null;
  evidence_bundle_path: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface OperationLogRequest {
  actor?: string;
  phase?: string;
  url?: string | null;
  action_type: string;
  target_label?: string | null;
  input_text?: string | null;
  request_method?: string | null;
  request_path?: string | null;
  response_status?: number | null;
  response_summary?: string | null;
  visible_result?: string | null;
  screenshot_path?: string | null;
  downloaded_file?: string | null;
  notes?: string | null;
}

export interface OperationLogEntry extends Required<Pick<OperationLogRequest, "action_type">> {
  id: string;
  run_id: string;
  session_id: string;
  timestamp: string;
  actor: string;
  phase: string;
  url: string | null;
  target_label: string | null;
  input_text: string | null;
  request_method: string | null;
  request_path: string | null;
  response_status: number | null;
  response_summary: string | null;
  visible_result: string | null;
  screenshot_path: string | null;
  downloaded_file: string | null;
  notes: string | null;
}

export interface ValidationRunApiSummary {
  run_id: string;
  session_id: string;
  api_calls: {
    method: string;
    path: string;
    status: number | null;
    public_summary: Record<string, unknown>;
    error_class: string | null;
  }[];
}
