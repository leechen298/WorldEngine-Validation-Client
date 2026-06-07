import { create } from "zustand";
import {
  appendOperationLog,
  createBranch as apiCreateBranch,
  createDirectorIntent as apiCreateDirectorIntent,
  createSession,
  createValidationRun,
  createWorldSession,
  downloadEvidenceBundle as apiDownloadEvidenceBundle,
  getEvidenceBundleManifest,
  getBranches,
  getCommitPoints,
  getDirectorIntents,
  getHealth,
  getReplayView,
  getRuntimeView,
  getSessions,
  getWorldEngineHealth,
} from "../api/client";
import type {
  BranchSummary,
  CommitPointSummary,
  CreateDirectorIntentRequest,
  DirectorIntent,
  EvidenceBundleDownload,
  EvidenceBundleResponse,
  HealthWorldEngineResponse,
  OperationLogRequest,
  ReplayView,
  RuntimeView,
  SessionSummary,
  ValidationRun,
} from "../api/types";

const WEB_URL = typeof window === "undefined" ? null : window.location.origin;
const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || "http://127.0.0.1:8765";

interface SessionState {
  sessions: SessionSummary[];
  isLoading: boolean;
  error: string | null;
  connectionStatus: {
    status: "loading" | "ok" | "degraded" | "error";
    worldengine?: HealthWorldEngineResponse["worldengine"];
    worldengineApiBase?: string;
    healthText?: string;
  } | null;
  lastBranches: Record<string, BranchSummary[]>;
  commitPointsBySession: Record<string, CommitPointSummary[]>;
  runtimeViewBySession: Record<string, RuntimeView>;
  runtimeErrorBySession: Record<string, string>;
  replayViewBySession: Record<string, ReplayView>;
  replayErrorBySession: Record<string, string>;
  selectedBranchBySession: Record<string, string>;
  replayTickBySession: Record<string, number>;
  directorIntentsBySession: Record<string, DirectorIntent[]>;
  directorIntentErrorBySession: Record<string, string>;
  directorIntentSubmittingBySession: Record<string, boolean>;
  evidenceBundleBySession: Record<string, EvidenceBundleResponse>;
  evidenceBundleErrorBySession: Record<string, string>;
  evidenceBundleLoadingBySession: Record<string, boolean>;
  validationRunBySession: Record<string, ValidationRun>;
  loadSessions: () => Promise<void>;
  loadHealth: () => Promise<void>;
  ensureValidationRun: (sessionId: string) => Promise<ValidationRun | null>;
  logOperation: (sessionId: string, payload: OperationLogRequest) => Promise<void>;
  loadBranches: (sessionId: string) => Promise<BranchSummary[]>;
  loadCommitPoints: (sessionId: string) => Promise<CommitPointSummary[]>;
  loadRuntimeView: (sessionId: string) => Promise<RuntimeView | null>;
  loadReplayView: (
    sessionId: string,
    options?: { branchId?: string; tick?: number },
  ) => Promise<ReplayView | null>;
  createNewSession: (name: string) => Promise<SessionSummary>;
  createWorldEngineSession: (name: string, worldPrompt: string) => Promise<SessionSummary>;
  createBranch: (sessionId: string, branchName: string, commitPointId: string) => Promise<BranchSummary>;
  loadDirectorIntents: (sessionId: string) => Promise<DirectorIntent[]>;
  createDirectorIntent: (
    sessionId: string,
    payload: CreateDirectorIntentRequest,
  ) => Promise<DirectorIntent | null>;
  loadEvidenceBundle: (sessionId: string) => Promise<EvidenceBundleResponse | null>;
  downloadEvidenceBundle: (sessionId: string) => Promise<EvidenceBundleDownload | null>;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessions: [],
  isLoading: false,
  error: null,
  connectionStatus: null,
  lastBranches: {},
  commitPointsBySession: {},
  runtimeViewBySession: {},
  runtimeErrorBySession: {},
  replayViewBySession: {},
  replayErrorBySession: {},
  selectedBranchBySession: {},
  replayTickBySession: {},
  directorIntentsBySession: {},
  directorIntentErrorBySession: {},
  directorIntentSubmittingBySession: {},
  evidenceBundleBySession: {},
  evidenceBundleErrorBySession: {},
  evidenceBundleLoadingBySession: {},
  validationRunBySession: {},

  ensureValidationRun: async (sessionId: string) => {
    const existing = get().validationRunBySession[sessionId];
    if (existing) {
      return existing;
    }
    try {
      const run = await createValidationRun({
        session_id: sessionId,
        actor: "codex",
        web_url: WEB_URL,
        api_base_url: API_BASE,
        worldengine_api_base: get().connectionStatus?.worldengineApiBase || null,
        notes: "v0.8 WorldEngine v0.9 validation plan optimization run",
      });
      set((state) => ({
        validationRunBySession: {
          ...state.validationRunBySession,
          [sessionId]: run,
        },
      }));
      return run;
    } catch (_error) {
      return null;
    }
  },

  logOperation: async (sessionId: string, payload: OperationLogRequest) => {
    const run = await get().ensureValidationRun(sessionId);
    if (!run) {
      return;
    }
    try {
      await appendOperationLog(run.id, {
        actor: "codex",
        phase: "browser",
        url: typeof window === "undefined" ? null : window.location.href,
        ...payload,
      });
    } catch (_error) {
      // Operation logs are validation evidence; they should not block the UI flow.
    }
  },

  loadSessions: async () => {
    set({ isLoading: true, error: null });
    try {
      const payload = await getSessions();
      set({ sessions: payload.sessions, isLoading: false });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
    }
  },

  loadHealth: async () => {
    set({ isLoading: true, error: null });
    try {
      const health = await getHealth();
      try {
        const worldengineHealth = await getWorldEngineHealth();
        set({
          connectionStatus: {
            status: worldengineHealth.status,
            worldengine: worldengineHealth.worldengine,
            worldengineApiBase: health.worldengine_api_base,
            healthText: worldengineHealth.worldengine.errors.join("; "),
          },
          isLoading: false,
        });
      } catch (worldengineError) {
        set({
          connectionStatus: {
            status: "degraded",
            worldengine: {
              reachable: false,
              health: null,
              manifest: null,
              openapi: null,
              capabilities: {
                manifest_available: false,
                openapi_available: false,
                world_creation: "unknown",
                v0_9_validation: "not_run",
                v0_9_public_surfaces: {},
              },
              errors: [(worldengineError as Error).message],
            },
            worldengineApiBase: health.worldengine_api_base,
            healthText: (worldengineError as Error).message,
          },
          isLoading: false,
        });
      }
    } catch (error) {
      set({
        connectionStatus: {
          status: "error",
          healthText: (error as Error).message,
        },
        error: (error as Error).message,
        isLoading: false,
      });
    }
  },

  loadBranches: async (sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const payload = await getBranches(sessionId);
      await get().logOperation(sessionId, {
        action_type: "api.get_branches",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/branches`,
        response_status: 200,
        response_summary: `${payload.branches.length} branches`,
        visible_result: "branch list refreshed",
      });
      const state = get();
      set({
        lastBranches: {
          ...state.lastBranches,
          [sessionId]: payload.branches,
        },
        isLoading: false,
      });
      return payload.branches;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "api.get_branches.failed",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/branches`,
        response_summary: (error as Error).message,
        visible_result: "branch list failed",
      });
      set({ error: (error as Error).message, isLoading: false });
      return [];
    }
  },

  loadCommitPoints: async (sessionId: string) => {
    try {
      const commitPoints = await getCommitPoints(sessionId);
      await get().logOperation(sessionId, {
        action_type: "api.get_commit_points",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/branches/commit-points`,
        response_status: 200,
        response_summary: `${commitPoints.length} commit points`,
        visible_result: "commit points refreshed",
      });
      set((state) => ({
        commitPointsBySession: {
          ...state.commitPointsBySession,
          [sessionId]: commitPoints,
        },
      }));
      return commitPoints;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "api.get_commit_points.failed",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/branches/commit-points`,
        response_summary: (error as Error).message,
        visible_result: "commit points failed",
      });
      set({ error: (error as Error).message });
      return [];
    }
  },

  loadRuntimeView: async (sessionId: string) => {
    set((state) => ({
      runtimeErrorBySession: {
        ...state.runtimeErrorBySession,
        [sessionId]: "",
      },
    }));
    try {
      const runtimeView = await getRuntimeView(sessionId);
      await get().logOperation(sessionId, {
        action_type: "api.get_runtime_view",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/runtime-view`,
        response_status: 200,
        response_summary: `tick ${runtimeView.tick}`,
        visible_result: "public runtime view refreshed",
      });
      set((state) => ({
        runtimeViewBySession: {
          ...state.runtimeViewBySession,
          [sessionId]: runtimeView,
        },
        runtimeErrorBySession: {
          ...state.runtimeErrorBySession,
          [sessionId]: "",
        },
      }));
      return runtimeView;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "api.get_runtime_view.failed",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/runtime-view`,
        response_summary: (error as Error).message,
        visible_result: "public runtime view failed",
      });
      set((state) => ({
        runtimeErrorBySession: {
          ...state.runtimeErrorBySession,
          [sessionId]: (error as Error).message,
        },
      }));
      return null;
    }
  },

  loadReplayView: async (sessionId: string, options = {}) => {
    set((state) => ({
      selectedBranchBySession: options.branchId
        ? {
            ...state.selectedBranchBySession,
            [sessionId]: options.branchId,
          }
        : state.selectedBranchBySession,
      replayTickBySession:
        options.tick !== undefined
          ? {
              ...state.replayTickBySession,
              [sessionId]: options.tick,
            }
          : state.replayTickBySession,
      replayErrorBySession: {
        ...state.replayErrorBySession,
        [sessionId]: "",
      },
    }));
    try {
      const replayView = await getReplayView(sessionId, options);
      await get().logOperation(sessionId, {
        action_type: "api.get_replay_view",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/replay-view`,
        response_status: 200,
        response_summary: `branch ${replayView.branch_id} tick ${replayView.tick}`,
        visible_result: "replay view refreshed",
      });
      set((state) => ({
        replayViewBySession: {
          ...state.replayViewBySession,
          [sessionId]: replayView,
        },
        selectedBranchBySession: {
          ...state.selectedBranchBySession,
          [sessionId]: replayView.branch_id,
        },
        replayTickBySession: {
          ...state.replayTickBySession,
          [sessionId]: replayView.tick,
        },
        replayErrorBySession: {
          ...state.replayErrorBySession,
          [sessionId]: "",
        },
      }));
      return replayView;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "api.get_replay_view.failed",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/replay-view`,
        response_summary: (error as Error).message,
        visible_result: "replay view failed",
      });
      set((state) => ({
        replayErrorBySession: {
          ...state.replayErrorBySession,
          [sessionId]: (error as Error).message,
        },
      }));
      return null;
    }
  },

  createNewSession: async (name: string) => {
    set({ isLoading: true, error: null });
    try {
      const newSession = await createSession({ session_name: name });
      set({ sessions: [...get().sessions, newSession], isLoading: false });
      return newSession;
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  },

  createWorldEngineSession: async (name: string, worldPrompt: string) => {
    set({ isLoading: true, error: null });
    try {
      const newSession = await createWorldSession({
        session_name: name,
        world_prompt: worldPrompt,
      });
      const payload = await getSessions();
      set({ sessions: payload.sessions, isLoading: false });
      await get().ensureValidationRun(newSession.id);
      await get().logOperation(newSession.id, {
        action_type: "session_library.page_open",
        target_label: "Session Library",
        visible_result: "session library loaded before world creation",
      });
      await get().logOperation(newSession.id, {
        action_type: "worldengine.health_check",
        target_label: "WorldEngine connection status",
        request_method: "GET",
        request_path: "/health/worldengine",
        response_status: get().connectionStatus?.status === "error" ? null : 200,
        response_summary: get().connectionStatus?.status || "unknown",
        visible_result: get().connectionStatus?.healthText || "WorldEngine status displayed",
      });
      await get().logOperation(newSession.id, {
        action_type: "session.create_worldengine.submit",
        target_label: "创建世界",
        input_text: worldPrompt,
        request_method: "POST",
        request_path: "/sessions/worldengine",
        response_status: 201,
        response_summary: `session ${newSession.id} world ${newSession.worldengine_world_id || "local"}`,
        visible_result: "runtime console opened",
      });
      return newSession;
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  },

  createBranch: async (sessionId: string, branchName: string, commitPointId: string) => {
    set({ isLoading: true, error: null });
    try {
      const branch = await apiCreateBranch(sessionId, {
        branch_name: branchName,
        commit_point_id: commitPointId,
      });
      await get().logOperation(sessionId, {
        action_type: "branch.create",
        target_label: "从当前 commit point 创建 branch",
        input_text: branchName,
        request_method: "POST",
        request_path: `/sessions/${sessionId}/branches`,
        response_status: 201,
        response_summary: `branch ${branch.id}`,
        visible_result: `created branch ${branch.branch_name}`,
      });
      const state = get();
      set({
        lastBranches: {
          ...state.lastBranches,
          [sessionId]: [...(state.lastBranches[sessionId] || []), branch],
        },
        isLoading: false,
      });
      return branch;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "branch.create.failed",
        target_label: "从当前 commit point 创建 branch",
        input_text: branchName,
        request_method: "POST",
        request_path: `/sessions/${sessionId}/branches`,
        response_summary: (error as Error).message,
        visible_result: "branch creation failed",
      });
      set({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  },

  loadDirectorIntents: async (sessionId: string) => {
    try {
      const payload = await getDirectorIntents(sessionId);
      await get().logOperation(sessionId, {
        action_type: "api.get_director_intents",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/director-intents`,
        response_status: 200,
        response_summary: `${payload.director_intents.length} director intents`,
        visible_result: "director intent list refreshed",
      });
      set((state) => ({
        directorIntentsBySession: {
          ...state.directorIntentsBySession,
          [sessionId]: payload.director_intents,
        },
        directorIntentErrorBySession: {
          ...state.directorIntentErrorBySession,
          [sessionId]: "",
        },
      }));
      return payload.director_intents;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "api.get_director_intents.failed",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/director-intents`,
        response_summary: (error as Error).message,
        visible_result: "director intent list failed",
      });
      set((state) => ({
        directorIntentErrorBySession: {
          ...state.directorIntentErrorBySession,
          [sessionId]: (error as Error).message,
        },
      }));
      return [];
    }
  },

  createDirectorIntent: async (sessionId: string, payload: CreateDirectorIntentRequest) => {
    set((state) => ({
      directorIntentSubmittingBySession: {
        ...state.directorIntentSubmittingBySession,
        [sessionId]: true,
      },
      directorIntentErrorBySession: {
        ...state.directorIntentErrorBySession,
        [sessionId]: "",
      },
    }));
    try {
      const intent = await apiCreateDirectorIntent(sessionId, payload);
      await get().logOperation(sessionId, {
        action_type: "director_guidance.submit",
        target_label: "提交引导",
        input_text: payload.instruction_text,
        request_method: "POST",
        request_path: `/sessions/${sessionId}/director-intents`,
        response_status: 201,
        response_summary: `intent ${intent.id} ${intent.status}`,
        visible_result: `director intent ${intent.status}`,
      });
      set((state) => ({
        directorIntentsBySession: {
          ...state.directorIntentsBySession,
          [sessionId]: [
            intent,
            ...(state.directorIntentsBySession[sessionId] || []).filter((item) => item.id !== intent.id),
          ],
        },
        directorIntentSubmittingBySession: {
          ...state.directorIntentSubmittingBySession,
          [sessionId]: false,
        },
        directorIntentErrorBySession: {
          ...state.directorIntentErrorBySession,
          [sessionId]: "",
        },
      }));
      return intent;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "director_guidance.submit.failed",
        target_label: "提交引导",
        input_text: payload.instruction_text,
        request_method: "POST",
        request_path: `/sessions/${sessionId}/director-intents`,
        response_summary: (error as Error).message,
        visible_result: "director guidance failed",
      });
      set((state) => ({
        directorIntentSubmittingBySession: {
          ...state.directorIntentSubmittingBySession,
          [sessionId]: false,
        },
        directorIntentErrorBySession: {
          ...state.directorIntentErrorBySession,
          [sessionId]: (error as Error).message,
        },
      }));
      return null;
    }
  },

  loadEvidenceBundle: async (sessionId: string) => {
    set((state) => ({
      evidenceBundleLoadingBySession: {
        ...state.evidenceBundleLoadingBySession,
        [sessionId]: true,
      },
      evidenceBundleErrorBySession: {
        ...state.evidenceBundleErrorBySession,
        [sessionId]: "",
      },
    }));
    try {
      const bundle = await getEvidenceBundleManifest(sessionId);
      await get().logOperation(sessionId, {
        action_type: "evidence.manifest.load",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/evidence/bundle/manifest`,
        response_status: 200,
        response_summary: `bundle ${bundle.manifest.bundle_schema_version}`,
        visible_result: "evidence bundle manifest displayed",
      });
      set((state) => ({
        evidenceBundleBySession: {
          ...state.evidenceBundleBySession,
          [sessionId]: bundle,
        },
        evidenceBundleLoadingBySession: {
          ...state.evidenceBundleLoadingBySession,
          [sessionId]: false,
        },
        evidenceBundleErrorBySession: {
          ...state.evidenceBundleErrorBySession,
          [sessionId]: "",
        },
      }));
      return bundle;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "evidence.manifest.load.failed",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/evidence/bundle/manifest`,
        response_summary: (error as Error).message,
        visible_result: "evidence bundle manifest failed",
      });
      set((state) => ({
        evidenceBundleLoadingBySession: {
          ...state.evidenceBundleLoadingBySession,
          [sessionId]: false,
        },
        evidenceBundleErrorBySession: {
          ...state.evidenceBundleErrorBySession,
          [sessionId]: (error as Error).message,
        },
      }));
      return null;
    }
  },

  downloadEvidenceBundle: async (sessionId: string) => {
    set((state) => ({
      evidenceBundleLoadingBySession: {
        ...state.evidenceBundleLoadingBySession,
        [sessionId]: true,
      },
      evidenceBundleErrorBySession: {
        ...state.evidenceBundleErrorBySession,
        [sessionId]: "",
      },
    }));
    try {
      const download = await apiDownloadEvidenceBundle(sessionId);
      await get().logOperation(sessionId, {
        action_type: "evidence.bundle.download",
        target_label: "下载 evidence bundle",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/evidence/bundle/download`,
        response_status: 200,
        response_summary: download.filename,
        visible_result: "evidence bundle downloaded",
        downloaded_file: download.filename,
      });
      set((state) => ({
        evidenceBundleBySession: {
          ...state.evidenceBundleBySession,
          [sessionId]: download.bundle,
        },
        evidenceBundleLoadingBySession: {
          ...state.evidenceBundleLoadingBySession,
          [sessionId]: false,
        },
        evidenceBundleErrorBySession: {
          ...state.evidenceBundleErrorBySession,
          [sessionId]: "",
        },
      }));
      return download;
    } catch (error) {
      await get().logOperation(sessionId, {
        action_type: "evidence.bundle.download.failed",
        target_label: "下载 evidence bundle",
        request_method: "GET",
        request_path: `/sessions/${sessionId}/evidence/bundle/download`,
        response_summary: (error as Error).message,
        visible_result: "evidence bundle download failed",
      });
      set((state) => ({
        evidenceBundleLoadingBySession: {
          ...state.evidenceBundleLoadingBySession,
          [sessionId]: false,
        },
        evidenceBundleErrorBySession: {
          ...state.evidenceBundleErrorBySession,
          [sessionId]: (error as Error).message,
        },
      }));
      return null;
    }
  },
}));
