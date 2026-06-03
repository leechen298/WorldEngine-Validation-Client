import type {
  BranchSummary,
  CreateBranchRequest,
  CreateSessionRequest,
  CreateWorldSessionRequest,
  HealthResponse,
  HealthWorldEngineResponse,
  SessionEvent,
  SessionSummary,
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

export async function getBranches(sessionId: string): Promise<{ session_id: string; branches: BranchSummary[] }> {
  return request<{ session_id: string; branches: BranchSummary[] }>(`/sessions/${sessionId}/branches`);
}

export async function createBranch(sessionId: string, payload: CreateBranchRequest): Promise<BranchSummary> {
  return request<BranchSummary>(`/sessions/${sessionId}/branches`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
