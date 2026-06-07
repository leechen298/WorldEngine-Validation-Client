import type {
  BranchSummary,
  CommitPointSummary,
  CreateBranchRequest,
  CreateDirectorIntentRequest,
  CreateSessionRequest,
  CreateValidationRunRequest,
  CreateWorldSessionRequest,
  DirectorIntent,
  EvidenceArtifactsDownload,
  EvidenceBundleDownload,
  EvidenceBundleResponse,
  HealthResponse,
  HealthWorldEngineResponse,
  OperationLogEntry,
  OperationLogRequest,
  ReplayView,
  RuntimeView,
  SessionEvent,
  SessionSummary,
  ValidationRun,
  ValidationRunApiSummary,
} from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || "http://127.0.0.1:8765";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = await response.json();
      if (typeof payload.detail === "string") {
        message = payload.detail;
      }
    } catch (_error) {
      // Keep the status-only fallback when the response body is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export async function getWorldEngineHealth(): Promise<HealthWorldEngineResponse> {
  return request<HealthWorldEngineResponse>("/health/worldengine");
}

export async function getSessions(): Promise<{ sessions: SessionSummary[] }> {
  return request<{ sessions: SessionSummary[] }>("/sessions");
}

export async function createSession(payload: CreateSessionRequest): Promise<SessionSummary> {
  return request<SessionSummary>("/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createWorldSession(payload: CreateWorldSessionRequest): Promise<SessionSummary> {
  return request<SessionSummary>("/sessions/worldengine", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getSessionEvents(sessionId: string): Promise<SessionEvent[]> {
  return request<SessionEvent[]>(`/sessions/${sessionId}/events`);
}

export async function getRuntimeView(sessionId: string): Promise<RuntimeView> {
  return request<RuntimeView>(`/sessions/${sessionId}/runtime-view`);
}

export async function getReplayView(
  sessionId: string,
  options: { branchId?: string; tick?: number } = {},
): Promise<ReplayView> {
  const params = new URLSearchParams();
  if (options.branchId) {
    params.set("branch_id", options.branchId);
  }
  if (options.tick !== undefined) {
    params.set("tick", String(options.tick));
  }
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return request<ReplayView>(`/sessions/${sessionId}/replay-view${suffix}`);
}

export async function getBranches(sessionId: string): Promise<{ session_id: string; branches: BranchSummary[] }> {
  return request<{ session_id: string; branches: BranchSummary[] }>(`/sessions/${sessionId}/branches`);
}

export async function getCommitPoints(sessionId: string): Promise<CommitPointSummary[]> {
  return request<CommitPointSummary[]>(`/sessions/${sessionId}/branches/commit-points`);
}

export async function createBranch(sessionId: string, payload: CreateBranchRequest): Promise<BranchSummary> {
  return request<BranchSummary>(`/sessions/${sessionId}/branches`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getDirectorIntents(
  sessionId: string,
): Promise<{ session_id: string; director_intents: DirectorIntent[] }> {
  return request<{ session_id: string; director_intents: DirectorIntent[] }>(
    `/sessions/${sessionId}/director-intents`,
  );
}

export async function createDirectorIntent(
  sessionId: string,
  payload: CreateDirectorIntentRequest,
): Promise<DirectorIntent> {
  return request<DirectorIntent>(`/sessions/${sessionId}/director-intents`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

function scenarioSuffix(scenario?: string): string {
  if (!scenario) {
    return "";
  }
  const params = new URLSearchParams({ scenario });
  return `?${params.toString()}`;
}

export async function getEvidenceBundleManifest(
  sessionId: string,
  scenario?: string,
): Promise<EvidenceBundleResponse> {
  return request<EvidenceBundleResponse>(`/sessions/${sessionId}/evidence/bundle/manifest${scenarioSuffix(scenario)}`);
}

async function fetchJsonDownload<T>(url: string, fallbackFilename: string): Promise<{ filename: string; payload: T }> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = await response.json();
      if (typeof payload.detail === "string") {
        message = payload.detail;
      }
    } catch (_error) {
      // Keep the status-only fallback when the response body is not JSON.
    }
    throw new Error(message);
  }

  const disposition = response.headers.get("content-disposition") || "";
  const filenameMatch = disposition.match(/filename="([^"]+)"/);
  return {
    filename: filenameMatch?.[1] || fallbackFilename,
    payload: (await response.json()) as T,
  };
}

export async function downloadEvidenceBundle(sessionId: string, scenario?: string): Promise<EvidenceBundleDownload> {
  const download = await fetchJsonDownload<EvidenceBundleResponse>(
    `/sessions/${sessionId}/evidence/bundle/download${scenarioSuffix(scenario)}`,
    `evidence-bundle-${sessionId}.json`,
  );
  return {
    filename: download.filename,
    bundle: download.payload,
  };
}

export async function downloadEvidenceArtifacts(
  sessionId: string,
  scenario?: string,
): Promise<EvidenceArtifactsDownload> {
  const download = await fetchJsonDownload<Record<string, unknown>>(
    `/sessions/${sessionId}/evidence/bundle/artifacts/download${scenarioSuffix(scenario)}`,
    `evidence-artifacts-${sessionId}.json`,
  );
  return {
    filename: download.filename,
    artifacts: download.payload,
  };
}

export async function createValidationRun(payload: CreateValidationRunRequest): Promise<ValidationRun> {
  return request<ValidationRun>("/validation-runs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function appendOperationLog(runId: string, payload: OperationLogRequest): Promise<OperationLogEntry> {
  return request<OperationLogEntry>(`/validation-runs/${runId}/operation-log`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getValidationRunApiSummary(runId: string): Promise<ValidationRunApiSummary> {
  return request<ValidationRunApiSummary>(`/validation-runs/${runId}/api-summary`);
}
