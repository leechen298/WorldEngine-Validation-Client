import { create } from "zustand";
import { createBranch as apiCreateBranch, createSession, getBranches, getHealth, getSessions } from "../api/client";
import type { BranchSummary, SessionSummary } from "../api/types";

interface SessionState {
  sessions: SessionSummary[];
  isLoading: boolean;
  error: string | null;
  connectionStatus: {
    status: string;
    worldengine?: { reachable?: boolean };
    worldengineApiBase?: string;
  } | null;
  lastBranches: Record<string, BranchSummary[]>;
  loadSessions: () => Promise<void>;
  loadHealth: () => Promise<void>;
  loadBranches: (sessionId: string) => Promise<BranchSummary[]>;
  createNewSession: (name: string) => Promise<SessionSummary>;
  createBranch: (sessionId: string, branchName: string, commitPointId: string) => Promise<BranchSummary>;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessions: [],
  isLoading: false,
  error: null,
  connectionStatus: null,
  lastBranches: {},

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
      set({
        connectionStatus: {
          status: health.status,
          worldengineApiBase: health.worldengine_api_base,
        },
        isLoading: false,
      });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
    }
  },

  loadBranches: async (sessionId: string) => {
    const payload = await getBranches(sessionId);
    const state = get();
    set({
      lastBranches: {
        ...state.lastBranches,
        [sessionId]: payload.branches,
      },
    });
    return payload.branches;
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

  createBranch: async (sessionId: string, branchName: string, commitPointId: string) => {
    set({ isLoading: true, error: null });
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
  },
}));
