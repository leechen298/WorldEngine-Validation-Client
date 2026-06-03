import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { getCommitPoints, getReplayView, getSessionEvents } from "../api/client";
import { useSessionStore } from "../store/sessionStore";
import { RuntimeConsole } from "../pages/RuntimeConsole";

vi.mock("../api/client", () => ({
  getCommitPoints: vi.fn().mockResolvedValue([]),
  getReplayView: vi.fn().mockResolvedValue(null),
  getSessionEvents: vi.fn().mockResolvedValue([]),
}));

vi.mock("pixi.js", () => {
  class MockApplication {
    canvas = document.createElement("canvas");
    stage = { addChild: vi.fn() };

    async init() {
      return undefined;
    }

    destroy() {
      return undefined;
    }
  }

  class MockContainer {
    addChild = vi.fn();
  }

  class MockGraphics {
    rect() {
      return this;
    }

    circle() {
      return this;
    }

    fill() {
      return this;
    }
  }

  return {
    Application: MockApplication,
    Container: MockContainer,
    Graphics: MockGraphics,
  };
});

const initialSessionStoreState = useSessionStore.getState();

describe("RuntimeConsole", () => {
  beforeEach(() => {
    useSessionStore.setState(initialSessionStoreState, true);
    vi.mocked(getCommitPoints).mockClear();
    vi.mocked(getCommitPoints).mockResolvedValue([]);
    vi.mocked(getReplayView).mockClear();
    vi.mocked(getReplayView).mockResolvedValue(null as any);
    vi.mocked(getSessionEvents).mockClear();
  });

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
    expect(screen.getByText("公开像素地图")).toBeInTheDocument();
    expect(screen.getByText("分支列表")).toBeInTheDocument();
    expect(screen.getByText("暂无事件气泡。")).toBeInTheDocument();
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
      runtimeViewBySession: {
        "session-id": {
          session_id: "session-id",
          worldengine_world_id: "world-123",
          world_status: "created",
          tick: 1,
          visualization: {},
          public_agents: [],
          world_log: [],
          agent_life_log: [],
          latest_event: {
            id: "event-1",
            tick: 1,
            event_kind: "world_created",
            text: "World created",
            agent_id: null,
            payload: {},
            created_at: "2026-01-01T00:00:01Z",
          },
        },
      },
      runtimeErrorBySession: {},
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
    expect(screen.getByText("World created")).toBeInTheDocument();
    expect(screen.queryByText('{"world_id":"world-123","status":"created"}')).not.toBeInTheDocument();
    expect(screen.queryByText("world_seeded")).not.toBeInTheDocument();
  });

  it("does not render raw session event payloads outside runtime view", async () => {
    vi.mocked(getSessionEvents).mockResolvedValueOnce([
      {
        id: "raw-event",
        session_id: "session-id",
        branch_id: "branch-private",
        tick: 99,
        event_kind: "raw_private",
        payload_json: '{"private_prompt":"hidden","hidden_context":"debug","thoughts":"secret"}',
        created_at: "2026-01-01T00:00:01Z",
      },
    ]);
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      runtimeViewBySession: {
        "session-id": {
          session_id: "session-id",
          worldengine_world_id: "world-123",
          world_status: "running",
          tick: 7,
          visualization: {},
          public_agents: [],
          world_log: [
            {
              id: "filtered-world-event",
              tick: 7,
              event_kind: "world_status",
              text: "Filtered public event",
              agent_id: null,
              payload: {},
              created_at: "2026-01-01T00:00:00Z",
            },
          ],
          agent_life_log: [],
          latest_event: {
            id: "filtered-world-event",
            tick: 7,
            event_kind: "world_status",
            text: "Filtered public event",
            agent_id: null,
            payload: {},
            created_at: "2026-01-01T00:00:00Z",
          },
        },
      },
      runtimeErrorBySession: {},
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

    expect(screen.getAllByText("Filtered public event").length).toBeGreaterThan(0);
    await waitFor(() => expect(vi.mocked(getSessionEvents)).not.toHaveBeenCalled());
    expect(screen.queryByText("raw_private")).not.toBeInTheDocument();
    expect(screen.queryByText(/private_prompt/)).not.toBeInTheDocument();
    expect(screen.queryByText(/hidden_context/)).not.toBeInTheDocument();
    expect(screen.queryByText(/thoughts/)).not.toBeInTheDocument();
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

  it("passes runtime visualization data to the pixel canvas", async () => {
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      runtimeViewBySession: {
        "session-id": {
          session_id: "session-id",
          worldengine_world_id: "world-123",
          world_status: "running",
          tick: 4,
          visualization: {
            tiles: [{ x: 0, y: 0, terrain: "grass" }],
            entities: [{ id: "agent-1", x: 1, y: 2, sprite: "person" }],
          },
          public_agents: [],
          world_log: [],
          agent_life_log: [],
          latest_event: null,
        },
      },
      runtimeErrorBySession: {},
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

    expect(screen.getByText("公开像素地图")).toBeInTheDocument();
    expect(screen.getByLabelText("公开可视化画布")).toBeInTheDocument();
    expect(screen.getByText("tiles 1 / entities 1")).toBeInTheDocument();
  });

  it("shows an empty state when runtime visualization is missing", async () => {
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

    expect(screen.getByText("暂无公开可视化数据。")).toBeInTheDocument();
  });

  it("does not infer map positions for visualization items without coordinates", async () => {
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      runtimeViewBySession: {
        "session-id": {
          session_id: "session-id",
          worldengine_world_id: "world-123",
          world_status: "running",
          tick: 4,
          visualization: {
            tiles: [{ terrain: "water" }],
            entities: [{ id: "agent-1", sprite: "person" }],
          },
          public_agents: [],
          world_log: [],
          agent_life_log: [],
          latest_event: null,
        },
      },
      runtimeErrorBySession: {},
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

    expect(screen.getByText("暂无公开可视化数据。")).toBeInTheDocument();
    expect(screen.queryByLabelText("公开可视化画布")).not.toBeInTheDocument();
  });

  it("shows tick, public agents, event bubble, and runtime logs without private state", async () => {
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      runtimeViewBySession: {
        "session-id": {
          session_id: "session-id",
          worldengine_world_id: "world-123",
          world_status: "running",
          tick: 12,
          visualization: {},
          public_agents: [
            {
              agent_id: "agent-1",
              display_name: "Ada",
              location: "market",
              public_status: "walking",
              visible_action: "opening a stall",
              payload: { mood: "calm", memory: "hidden", goal: "hidden" },
            },
          ],
          world_log: [
            {
              id: "world-event",
              tick: 11,
              event_kind: "world_weather",
              text: "Light rain starts",
              agent_id: null,
              payload: { hidden_context: "debug" },
              created_at: "2026-01-01T00:00:00Z",
            },
          ],
          agent_life_log: [
            {
              id: "agent-event",
              tick: 12,
              event_kind: "agent_life",
              text: "Ada greets a visitor",
              agent_id: "agent-1",
              payload: { thought: "hidden" },
              created_at: "2026-01-01T00:00:01Z",
            },
          ],
          latest_event: {
            id: "latest-event",
            tick: 12,
            event_kind: "agent_life",
            text: "Ada greets a visitor",
            agent_id: "agent-1",
            payload: {},
            created_at: "2026-01-01T00:00:01Z",
          },
        },
      },
      runtimeErrorBySession: {},
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

    expect(screen.getAllByText("Tick 12").length).toBeGreaterThan(0);
    expect(screen.getByText("Agent 公开状态")).toBeInTheDocument();
    expect(screen.getByText("Ada")).toBeInTheDocument();
    expect(screen.getByText("market / walking")).toBeInTheDocument();
    expect(screen.getByText("opening a stall")).toBeInTheDocument();
    expect(screen.getByText("最新事件气泡")).toBeInTheDocument();
    expect(screen.getAllByText("Ada greets a visitor").length).toBeGreaterThan(0);
    expect(screen.getByText("World Log")).toBeInTheDocument();
    expect(screen.getByText("Light rain starts")).toBeInTheDocument();
    expect(screen.getByText("Agent Life Log")).toBeInTheDocument();
    expect(screen.queryByText("hidden")).not.toBeInTheDocument();
    expect(screen.queryByText("memory")).not.toBeInTheDocument();
    expect(screen.queryByText("goal")).not.toBeInTheDocument();
    expect(screen.queryByText("thought")).not.toBeInTheDocument();
  });

  it("loads replay view and commit points through the store without raw payloads", async () => {
    vi.mocked(getCommitPoints).mockResolvedValueOnce([
      {
        id: "cp-2",
        session_id: "session-id",
        tick: 2,
        event_id: "event-2",
        snapshot_id: "snapshot-2",
        payload_summary: "Market opens",
        branch_ids: ["branch-1"],
        branch_names: ["main"],
        created_at: "2026-01-01T00:00:02Z",
      },
    ]);
    vi.mocked(getReplayView).mockResolvedValueOnce({
      session_id: "session-id",
      branch_id: "branch-1",
      snapshot_id: "snapshot-2",
      worldengine_world_id: "world-123",
      world_status: "running",
      tick: 2,
      visualization: {},
      public_agents: [],
      world_log: [],
      agent_life_log: [],
      latest_event: null,
    });
    useSessionStore.setState({
      commitPointsBySession: {},
      replayViewBySession: {},
      replayErrorBySession: {},
      selectedBranchBySession: {},
      replayTickBySession: {},
    } as any);

    const commitPoints = await useSessionStore.getState().loadCommitPoints("session-id");
    const replayView = await useSessionStore
      .getState()
      .loadReplayView("session-id", { branchId: "branch-1", tick: 2 });

    expect(getCommitPoints).toHaveBeenCalledWith("session-id");
    expect(getReplayView).toHaveBeenCalledWith("session-id", { branchId: "branch-1", tick: 2 });
    expect(commitPoints[0].payload_summary).toBe("Market opens");
    expect("payload_json" in commitPoints[0]).toBe(false);
    expect(replayView?.branch_id).toBe("branch-1");
    expect(useSessionStore.getState().selectedBranchBySession["session-id"]).toBe("branch-1");
    expect(useSessionStore.getState().replayTickBySession["session-id"]).toBe(2);
    expect(useSessionStore.getState().replayViewBySession["session-id"]?.snapshot_id).toBe("snapshot-2");
    expect(useSessionStore.getState().replayErrorBySession["session-id"]).toBe("");
  });

  it("shows timeline scrubber and loads replay view from selected commit points", async () => {
    const loadCommitPoints = vi.fn().mockResolvedValue([]);
    const loadReplayView = vi.fn().mockResolvedValue(null);
    useSessionStore.setState({
      sessions: [
        {
          id: "session-id",
          session_name: "World Session",
          status: "running",
          worldengine_world_id: "world-123",
          public_world_status: "running",
          initial_state_summary: null,
          visualization_payload_summary: null,
          branch_count: 1,
          main_branch_id: "branch-1",
          main_commit_point_id: "cp-1",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      runtimeViewBySession: {},
      replayViewBySession: {
        "session-id": {
          session_id: "session-id",
          branch_id: "branch-1",
          snapshot_id: "snapshot-2",
          worldengine_world_id: "world-123",
          world_status: "running",
          tick: 2,
          visualization: {},
          public_agents: [],
          world_log: [
            {
              id: "world-event",
              tick: 2,
              event_kind: "world_change",
              text: "Market opens",
              agent_id: null,
              payload: { private_prompt: "hidden" },
              created_at: "2026-01-01T00:00:02Z",
            },
          ],
          agent_life_log: [],
          latest_event: null,
        },
      },
      replayErrorBySession: {},
      selectedBranchBySession: { "session-id": "branch-1" },
      replayTickBySession: { "session-id": 2 },
      commitPointsBySession: {
        "session-id": [
          {
            id: "cp-1",
            session_id: "session-id",
            tick: 1,
            event_id: "event-1",
            snapshot_id: "snapshot-1",
            payload_summary: "World starts",
            branch_ids: ["branch-1"],
            branch_names: ["main"],
            created_at: "2026-01-01T00:00:01Z",
          },
          {
            id: "cp-2",
            session_id: "session-id",
            tick: 2,
            event_id: "event-2",
            snapshot_id: "snapshot-2",
            payload_summary: "Market opens",
            branch_ids: ["branch-1"],
            branch_names: ["main"],
            created_at: "2026-01-01T00:00:02Z",
          },
        ],
      },
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => [],
      loadRuntimeView: async () => null,
      loadCommitPoints,
      loadReplayView,
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

    expect(await screen.findByText("时间线回放")).toBeInTheDocument();
    expect(loadCommitPoints).toHaveBeenCalledWith("session-id");
    expect(screen.getByLabelText("目标 tick")).toHaveValue("2");
    expect(screen.getByText("Commit Points")).toBeInTheDocument();
    expect(screen.getByText("World starts")).toBeInTheDocument();
    expect(screen.getAllByText("Market opens").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("branch main").length).toBe(2);
    expect(screen.queryByText("private_prompt")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "跳转到 tick 1 World starts" }));

    expect(loadReplayView).toHaveBeenCalledWith("session-id", { branchId: "branch-1", tick: 1 });
  });

  it("records readable replay load failures in the store", async () => {
    vi.mocked(getReplayView).mockRejectedValueOnce(new Error("No replay snapshot is available"));
    useSessionStore.setState({
      replayViewBySession: {},
      replayErrorBySession: {},
      selectedBranchBySession: {},
      replayTickBySession: {},
    } as any);

    const replayView = await useSessionStore
      .getState()
      .loadReplayView("session-id", { branchId: "branch-1", tick: 4 });

    expect(replayView).toBeNull();
    expect(useSessionStore.getState().replayErrorBySession["session-id"]).toBe(
      "No replay snapshot is available",
    );
    expect(useSessionStore.getState().selectedBranchBySession["session-id"]).toBe("branch-1");
    expect(useSessionStore.getState().replayTickBySession["session-id"]).toBe(4);
  });
});
