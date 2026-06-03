import { create } from "zustand";
import {
  createBranch as apiCreateBranch,
  createDirectorIntent as apiCreateDirectorIntent,
  createSession,
  createWorldSession,
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
  HealthWorldEngineResponse,
  ReplayView,
  RuntimeView,
  SessionSummary,
} from "../api/types";

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
  loadSessions: () => Promise<void>;
  loadHealth: () => Promise<void>;
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
      set({ error: (error as Error).message, isLoading: false });
      return [];
    }
  },

  loadCommitPoints: async (sessionId: string) => {
    try {
      const commitPoints = await getCommitPoints(sessionId);
      set((state) => ({
        commitPointsBySession: {
          ...state.commitPointsBySession,
          [sessionId]: commitPoints,
        },
      }));
      return commitPoints;
    } catch (error) {
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
      set({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  },

  loadDirectorIntents: async (sessionId: string) => {
    try {
      const payload = await getDirectorIntents(sessionId);
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
}));
