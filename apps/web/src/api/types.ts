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
    health: Record<string, unknown> | null;
    manifest: Record<string, unknown> | null;
    errors: string[];
  };
}

export interface SessionSummary {
  id: string;
  session_name: string;
  status: string;
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

export interface CreateSessionRequest {
  session_name: string;
}

export interface CreateBranchRequest {
  branch_name: string;
  commit_point_id: string;
}
