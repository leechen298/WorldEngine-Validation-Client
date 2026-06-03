import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { getSessionEvents } from "../api/client";
import { useSessionStore } from "../store/sessionStore";
import { RuntimeConsole } from "../pages/RuntimeConsole";

vi.mock("../api/client", () => ({
  getSessionEvents: vi.fn().mockResolvedValue([]),
}));

describe("RuntimeConsole", () => {
  it("renders runtime controls", async () => {
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      connectionStatus: null,
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => [],
      loadRuntimeView: async () => null,
      createNewSession: async () => {
        throw new Error("not used");
      },
      createWorldEngineSession: async () => {
        throw new Error("not used");
      },
      createBranch: async () => ({
        id: "id",
        branch_name: "branch",
        commit_point_id: "cp",
        tick: 0,
        snapshot_reference: null,
        created_at: "",
      }),
    } as any);

    render(<RuntimeConsole sessionId="session-id" onBack={() => null} />);

    expect(screen.getByRole("button", { name: "Run" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Pause" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Single Tick" })).toBeInTheDocument();
    expect(screen.getByText("PixiJS 像素画布占位")).toBeInTheDocument();
    expect(screen.getByText("分支列表")).toBeInTheDocument();
    expect(await screen.findByText("暂无公开事件。")).toBeInTheDocument();
  });

  it("shows branch load failures in the runtime console", async () => {
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      connectionStatus: null,
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => {
        useSessionStore.setState({ error: "Request failed: 500" });
        return [];
      },
      loadRuntimeView: async () => null,
      createNewSession: async () => {
        throw new Error("not used");
      },
      createWorldEngineSession: async () => {
        throw new Error("not used");
      },
      createBranch: async () => {
        throw new Error("not used");
      },
    } as any);

    render(<RuntimeConsole sessionId="session-id" onBack={() => null} />);

    expect(await screen.findByText("分支加载失败：Request failed: 500")).toBeInTheDocument();
  });

  it("shows public WorldEngine state summaries and latest event", async () => {
    vi.mocked(getSessionEvents).mockResolvedValueOnce([
      {
        id: "event-0",
        session_id: "session-id",
        branch_id: "branch-1",
        tick: 0,
        event_kind: "world_seeded",
        payload_json: '{"world_id":"world-123","status":"seeded"}',
        created_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "event-1",
        session_id: "session-id",
        branch_id: "branch-1",
        tick: 1,
        event_kind: "world_created",
        payload_json: '{"world_id":"world-123","status":"created"}',
        created_at: "2026-01-01T00:00:01Z",
      },
    ]);
    useSessionStore.setState({
      sessions: [
        {
          id: "session-id",
          session_name: "World Session",
          status: "created",
          worldengine_world_id: "world-123",
          public_world_status: "created",
          initial_state_summary: '{"agents":2}',
          visualization_payload_summary: '{"tiles":12}',
          branch_count: 1,
          main_branch_id: "branch-1",
          main_commit_point_id: "cp-1",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      isLoading: false,
      error: null,
      connectionStatus: null,
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => [],
      loadRuntimeView: async () => null,
      createNewSession: async () => {
        throw new Error("not used");
      },
      createWorldEngineSession: async () => {
        throw new Error("not used");
      },
      createBranch: async () => {
        throw new Error("not used");
      },
    } as any);

    render(<RuntimeConsole sessionId="session-id" onBack={() => null} />);

    expect(screen.getByText("WorldEngine world：world-123")).toBeInTheDocument();
    expect(screen.getByText("公开状态：created")).toBeInTheDocument();
    expect(screen.getByText('初始状态摘要：{"agents":2}')).toBeInTheDocument();
    expect(screen.getByText('Visualization 摘要：{"tiles":12}')).toBeInTheDocument();
    expect(await screen.findByText("world_created")).toBeInTheDocument();
    expect(screen.getByText('{"world_id":"world-123","status":"created"}')).toBeInTheDocument();
    expect(screen.queryByText("world_seeded")).not.toBeInTheDocument();
  });

  it("loads runtime view through the store and shows load failures", async () => {
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      runtimeViewBySession: {},
      runtimeErrorBySession: {},
      connectionStatus: null,
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => [],
      loadRuntimeView: async () => {
        useSessionStore.setState({
          runtimeErrorBySession: { "session-id": "Runtime unavailable" },
        });
        return null;
      },
      createNewSession: async () => {
        throw new Error("not used");
      },
      createWorldEngineSession: async () => {
        throw new Error("not used");
      },
      createBranch: async () => {
        throw new Error("not used");
      },
    } as any);

    render(<RuntimeConsole sessionId="session-id" onBack={() => null} />);

    expect(await screen.findByText("运行视图加载失败：Runtime unavailable")).toBeInTheDocument();
  });
});
