import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import {
  appendOperationLog,
  createDirectorIntent,
  createValidationRun,
  downloadEvidenceBundle,
  getEvidenceBundleManifest,
  getCommitPoints,
  getDirectorIntents,
  getReplayView,
  getSessionEvents,
} from "../api/client";
import { useSessionStore } from "../store/sessionStore";
import { RuntimeConsole } from "../pages/RuntimeConsole";

vi.mock("../api/client", () => ({
  appendOperationLog: vi.fn().mockResolvedValue({
    id: "log-1",
    run_id: "run-1",
    session_id: "session-id",
    timestamp: "2026-06-04T00:00:00Z",
    actor: "codex",
    phase: "browser",
    url: "http://localhost",
    action_type: "runtime_console.page_open",
    target_label: "Runtime Console",
    input_text: null,
    request_method: null,
    request_path: null,
    response_status: null,
    response_summary: null,
    visible_result: "runtime console opened",
    screenshot_path: null,
    downloaded_file: null,
    notes: null,
  }),
  createDirectorIntent: vi.fn(),
  createValidationRun: vi.fn().mockResolvedValue({
    id: "run-1",
    session_id: "session-id",
    actor: "codex",
    status: "running",
    web_url: "http://localhost",
    api_base_url: "http://127.0.0.1:8765",
    worldengine_api_base: "http://127.0.0.1:8000",
    evidence_bundle_path: null,
    notes: "v0.7 browser validation run",
    created_at: "2026-06-04T00:00:00Z",
    updated_at: "2026-06-04T00:00:00Z",
  }),
  downloadEvidenceBundle: vi.fn(),
  getEvidenceBundleManifest: vi.fn(),
  getCommitPoints: vi.fn().mockResolvedValue([]),
  getDirectorIntents: vi.fn().mockResolvedValue({ session_id: "session-id", director_intents: [] }),
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
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn().mockReturnValue("blob:evidence-bundle"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    vi.mocked(getCommitPoints).mockClear();
    vi.mocked(getCommitPoints).mockResolvedValue([]);
    vi.mocked(getEvidenceBundleManifest).mockClear();
    vi.mocked(getEvidenceBundleManifest).mockResolvedValue({
      manifest: {
        bundle_schema_version: "0.7.0",
        generated_at: "2026-06-04T00:00:00Z",
        session_id: "session-id",
        session_name: "Evidence Session",
        worldengine_world_id: null,
        world_status: "created",
        latest_validation_run_id: null,
        evidence_bundle_filename: "evidence-bundle-session-id.json",
        counts: {
          branches: 1,
          events: 0,
          state_diffs: 0,
          snapshots: 0,
          commit_points: 1,
          director_intents: 0,
          api_traces: 0,
          validation_runs: 0,
          operation_log_entries: 0,
          evaluator_outputs: 0,
          replay_index: 1,
        },
        redaction_flags: {
          llm_keys_included: false,
          private_worldengine_internals_included: false,
        },
        warnings: ["public evaluator outputs unavailable"],
      },
      records: {
        branches: [],
        commit_points: [],
        events: [],
        state_diffs: [],
        snapshots: [],
        director_intents: [],
        api_traces: [],
        validation_runs: [],
        operation_log_entries: [],
        evaluator_outputs: [],
        replay_index: [],
      },
    });
    vi.mocked(downloadEvidenceBundle).mockClear();
    vi.mocked(downloadEvidenceBundle).mockResolvedValue({
      filename: "evidence-bundle-session-id-2026-06-04.json",
      bundle: {
        manifest: {
          bundle_schema_version: "0.7.0",
          generated_at: "2026-06-04T00:00:00Z",
          session_id: "session-id",
          session_name: "Evidence Session",
          worldengine_world_id: null,
          world_status: "created",
          latest_validation_run_id: null,
          evidence_bundle_filename: "evidence-bundle-session-id.json",
          counts: {
            branches: 1,
            events: 0,
            state_diffs: 0,
            snapshots: 0,
            commit_points: 1,
            director_intents: 0,
            api_traces: 0,
            validation_runs: 0,
            operation_log_entries: 0,
            evaluator_outputs: 0,
            replay_index: 1,
          },
          redaction_flags: {
            llm_keys_included: false,
            private_worldengine_internals_included: false,
          },
          warnings: [],
        },
        records: {
          branches: [],
          commit_points: [],
          events: [],
          state_diffs: [],
          snapshots: [],
          director_intents: [],
          api_traces: [],
          validation_runs: [],
          operation_log_entries: [],
          evaluator_outputs: [],
          replay_index: [],
        },
      },
    });
    vi.mocked(getDirectorIntents).mockClear();
    vi.mocked(getDirectorIntents).mockResolvedValue({ session_id: "session-id", director_intents: [] });
    vi.mocked(getReplayView).mockClear();
    vi.mocked(getReplayView).mockResolvedValue(null as any);
    vi.mocked(getSessionEvents).mockClear();
    vi.mocked(createDirectorIntent).mockClear();
    vi.mocked(createValidationRun).mockClear();
    vi.mocked(appendOperationLog).mockClear();
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

  it("switches branches and creates a branch from the selected commit point", async () => {
    const loadBranches = vi.fn().mockResolvedValue([]);
    const loadCommitPoints = vi.fn().mockResolvedValue([]);
    const loadReplayView = vi.fn().mockResolvedValue(null);
    const createBranch = vi.fn().mockResolvedValue({
      id: "branch-new",
      branch_name: "market-fork",
      commit_point_id: "cp-2",
      tick: 2,
      current_tick: 2,
      snapshot_reference: "snapshot-2",
      is_main: false,
      created_at: "2026-01-01T00:00:03Z",
    });
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
          branch_count: 2,
          main_branch_id: "branch-1",
          main_commit_point_id: "cp-1",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      lastBranches: {
        "session-id": [
          {
            id: "branch-1",
            branch_name: "main",
            commit_point_id: "cp-1",
            tick: 1,
            current_tick: 1,
            snapshot_reference: "snapshot-1",
            is_main: true,
            created_at: "2026-01-01T00:00:01Z",
          },
          {
            id: "branch-2",
            branch_name: "storm-line",
            commit_point_id: "cp-2",
            tick: 2,
            current_tick: 2,
            snapshot_reference: "snapshot-2",
            is_main: false,
            created_at: "2026-01-01T00:00:02Z",
          },
        ],
      },
      commitPointsBySession: {
        "session-id": [
          {
            id: "cp-2",
            session_id: "session-id",
            tick: 2,
            event_id: "event-2",
            snapshot_id: "snapshot-2",
            payload_summary: "Storm begins",
            branch_ids: ["branch-1", "branch-2"],
            branch_names: ["main", "storm-line"],
            created_at: "2026-01-01T00:00:02Z",
          },
        ],
      },
      replayViewBySession: {},
      replayErrorBySession: {},
      selectedBranchBySession: { "session-id": "branch-1" },
      replayTickBySession: { "session-id": 1 },
      runtimeViewBySession: {},
      runtimeErrorBySession: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches,
      loadRuntimeView: async () => null,
      loadCommitPoints,
      loadReplayView,
      createNewSession: async () => {
        throw new Error("not used");
      },
      createWorldEngineSession: async () => {
        throw new Error("not used");
      },
      createBranch,
    } as any);

    render(<RuntimeConsole sessionId="session-id" onBack={() => null} />);

    fireEvent.click(screen.getByRole("button", { name: "切换到 branch storm-line" }));

    expect(loadReplayView).toHaveBeenCalledWith("session-id", { branchId: "branch-2", tick: 2 });

    fireEvent.click(screen.getByRole("button", { name: "跳转到 tick 2 Storm begins" }));
    fireEvent.change(screen.getByLabelText("新 branch 名称"), { target: { value: "market-fork" } });
    fireEvent.click(screen.getByRole("button", { name: "从当前 commit point 创建 branch" }));

    await waitFor(() =>
      expect(createBranch).toHaveBeenCalledWith("session-id", "market-fork", "cp-2"),
    );
    expect(loadBranches).toHaveBeenCalledWith("session-id");
    expect(loadCommitPoints).toHaveBeenCalledWith("session-id");
    expect(loadReplayView).toHaveBeenCalledWith("session-id", { branchId: "branch-new", tick: 2 });
    expect(screen.queryByText(/parent/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/child/i)).not.toBeInTheDocument();
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

  it("loads and creates director intents through the store", async () => {
    vi.mocked(getDirectorIntents).mockResolvedValueOnce({
      session_id: "session-id",
      director_intents: [
        {
          id: "intent-1",
          session_id: "session-id",
          branch_id: "branch-1",
          tick: 2,
          instruction_text: "让市场附近的天气逐渐转晴",
          status: "pending",
          public_explanation: null,
          applied_event_id: null,
          error_message: null,
          created_at: "2026-06-03T00:00:00Z",
        },
      ],
    });
    vi.mocked(createDirectorIntent).mockResolvedValueOnce({
      id: "intent-2",
      session_id: "session-id",
      branch_id: "branch-1",
      tick: 3,
      instruction_text: "让广场附近出现更多公共活动",
      status: "accepted",
      public_explanation: "WorldEngine accepted the public trend",
      applied_event_id: "event-2",
      error_message: null,
      created_at: "2026-06-03T00:01:00Z",
    });
    useSessionStore.setState({
      directorIntentsBySession: {},
      directorIntentErrorBySession: {},
      directorIntentSubmittingBySession: {},
    } as any);

    const loaded = await useSessionStore.getState().loadDirectorIntents("session-id");
    const created = await useSessionStore.getState().createDirectorIntent("session-id", {
      instruction_text: "让广场附近出现更多公共活动",
      branch_id: "branch-1",
      tick: 3,
    });

    expect(getDirectorIntents).toHaveBeenCalledWith("session-id");
    expect(createDirectorIntent).toHaveBeenCalledWith("session-id", {
      instruction_text: "让广场附近出现更多公共活动",
      branch_id: "branch-1",
      tick: 3,
    });
    expect(loaded[0].id).toBe("intent-1");
    expect(created?.status).toBe("accepted");
    expect(useSessionStore.getState().directorIntentsBySession["session-id"].map((item) => item.id)).toEqual([
      "intent-2",
      "intent-1",
    ]);
    expect(useSessionStore.getState().directorIntentErrorBySession["session-id"]).toBe("");
    expect(useSessionStore.getState().directorIntentSubmittingBySession["session-id"]).toBe(false);
  });

  it("records readable director intent submit failures in the store", async () => {
    vi.mocked(createDirectorIntent).mockRejectedValueOnce(new Error("WorldEngine public endpoint unavailable"));
    useSessionStore.setState({
      directorIntentsBySession: {},
      directorIntentErrorBySession: {},
      directorIntentSubmittingBySession: {},
    } as any);

    const created = await useSessionStore.getState().createDirectorIntent("session-id", {
      instruction_text: "让市场附近的天气逐渐转晴",
      tick: 2,
    });

    expect(created).toBeNull();
    expect(useSessionStore.getState().directorIntentErrorBySession["session-id"]).toBe(
      "WorldEngine public endpoint unavailable",
    );
    expect(useSessionStore.getState().directorIntentSubmittingBySession["session-id"]).toBe(false);
  });

  it("loads evidence bundle manifest through the store", async () => {
    useSessionStore.setState({
      evidenceBundleBySession: {},
      evidenceBundleErrorBySession: {},
      evidenceBundleLoadingBySession: {},
    } as any);

    const bundle = await useSessionStore.getState().loadEvidenceBundle("session-id");

    expect(getEvidenceBundleManifest).toHaveBeenCalledWith("session-id");
    expect(bundle?.manifest.counts.branches).toBe(1);
    expect(useSessionStore.getState().evidenceBundleBySession["session-id"]?.manifest.session_id).toBe("session-id");
    expect(useSessionStore.getState().evidenceBundleErrorBySession["session-id"]).toBe("");
    expect(useSessionStore.getState().evidenceBundleLoadingBySession["session-id"]).toBe(false);
  });

  it("records evidence download failures without clearing runtime state", async () => {
    vi.mocked(downloadEvidenceBundle).mockRejectedValueOnce(new Error("Download failed"));
    const runtimeView = {
      session_id: "session-id",
      worldengine_world_id: null,
      world_status: "created",
      tick: 1,
      visualization: {},
      public_agents: [],
      world_log: [],
      agent_life_log: [],
      latest_event: null,
    };
    useSessionStore.setState({
      runtimeViewBySession: { "session-id": runtimeView },
      evidenceBundleErrorBySession: {},
      evidenceBundleLoadingBySession: {},
    } as any);

    const result = await useSessionStore.getState().downloadEvidenceBundle("session-id");

    expect(result).toBeNull();
    expect(useSessionStore.getState().runtimeViewBySession["session-id"]).toBe(runtimeView);
    expect(useSessionStore.getState().evidenceBundleErrorBySession["session-id"]).toBe("Download failed");
    expect(useSessionStore.getState().evidenceBundleLoadingBySession["session-id"]).toBe(false);
  });

  it("shows evidence bundle status and downloads the local evidence bundle", async () => {
    render(<RuntimeConsole sessionId="session-id" onBack={() => null} />);

    expect(await screen.findByText("本地会话证据包")).toBeInTheDocument();
    expect(screen.getByText("branches：1")).toBeInTheDocument();
    expect(screen.getByText("commit points：1")).toBeInTheDocument();
    expect(screen.getByText("脱敏状态：clean")).toBeInTheDocument();
    expect(screen.getByText("public evaluator outputs unavailable")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "下载 evidence bundle" }));

    await waitFor(() => {
      expect(downloadEvidenceBundle).toHaveBeenCalledWith("session-id");
    });
    expect(await screen.findByText("已下载：evidence-bundle-session-id-2026-06-04.json")).toBeInTheDocument();
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:evidence-bundle");
  });

  it("submits director guidance from the runtime console and shows intent status", async () => {
    const loadDirectorIntents = vi.fn().mockResolvedValue([]);
    const createDirectorIntentFromStore = vi.fn().mockResolvedValue({
      id: "intent-2",
      session_id: "session-id",
      branch_id: "branch-1",
      tick: 2,
      instruction_text: "让广场附近出现更多公共活动",
      status: "accepted",
      public_explanation: "WorldEngine accepted the public trend",
      applied_event_id: "event-2",
      error_message: null,
      created_at: "2026-06-03T00:01:00Z",
    });
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
      runtimeViewBySession: {
        "session-id": {
          session_id: "session-id",
          worldengine_world_id: "world-123",
          world_status: "running",
          tick: 2,
          visualization: {},
          public_agents: [],
          world_log: [],
          agent_life_log: [],
          latest_event: null,
        },
      },
      directorIntentsBySession: {
        "session-id": [
          {
            id: "intent-1",
            session_id: "session-id",
            branch_id: "branch-1",
            tick: 2,
            instruction_text: "让市场附近的天气逐渐转晴",
            status: "accepted",
            public_explanation: "WorldEngine accepted the public weather trend",
            applied_event_id: "event-1",
            error_message: null,
            created_at: "2026-06-03T00:00:00Z",
          },
        ],
      },
      directorIntentErrorBySession: {},
      directorIntentSubmittingBySession: {},
      selectedBranchBySession: { "session-id": "branch-1" },
      replayTickBySession: { "session-id": 2 },
      replayViewBySession: {},
      replayErrorBySession: {},
      commitPointsBySession: {},
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => [],
      loadRuntimeView: async () => null,
      loadCommitPoints: async () => [],
      loadReplayView: async () => null,
      loadDirectorIntents,
      createDirectorIntent: createDirectorIntentFromStore,
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

    expect(loadDirectorIntents).toHaveBeenCalledWith("session-id");
    expect(screen.getByText("导演引导状态")).toBeInTheDocument();
    expect(screen.getByText("让市场附近的天气逐渐转晴")).toBeInTheDocument();
    expect(screen.getByText("状态：accepted")).toBeInTheDocument();
    expect(screen.getByText("WorldEngine accepted the public weather trend")).toBeInTheDocument();
    expect(screen.getByText("applied event：event-1")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("高层方向 / 外部世界趋势"), {
      target: { value: "让广场附近出现更多公共活动" },
    });
    fireEvent.click(screen.getByRole("button", { name: "提交引导" }));

    await waitFor(() =>
      expect(createDirectorIntentFromStore).toHaveBeenCalledWith("session-id", {
        instruction_text: "让广场附近出现更多公共活动",
        branch_id: "branch-1",
        tick: 2,
      }),
    );
    expect(loadDirectorIntents).toHaveBeenCalledTimes(2);
    expect(screen.getByLabelText("高层方向 / 外部世界趋势")).toHaveValue("");
  });

  it("keeps director guidance input when submit fails", async () => {
    const createDirectorIntentFromStore = vi.fn().mockImplementation(async () => {
      useSessionStore.setState({
        directorIntentErrorBySession: { "session-id": "WorldEngine public endpoint unavailable" },
        directorIntentSubmittingBySession: { "session-id": false },
      } as any);
      return null;
    });
    useSessionStore.setState({
      sessions: [],
      runtimeViewBySession: {},
      directorIntentsBySession: {},
      directorIntentErrorBySession: {},
      directorIntentSubmittingBySession: {},
      selectedBranchBySession: { "session-id": "branch-1" },
      replayTickBySession: { "session-id": 2 },
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => [],
      loadRuntimeView: async () => null,
      loadCommitPoints: async () => [],
      loadReplayView: async () => null,
      loadDirectorIntents: async () => [],
      createDirectorIntent: createDirectorIntentFromStore,
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

    fireEvent.change(screen.getByLabelText("高层方向 / 外部世界趋势"), {
      target: { value: "让市场附近的天气逐渐转晴" },
    });
    fireEvent.click(screen.getByRole("button", { name: "提交引导" }));

    expect(await screen.findByText("导演引导提交失败：WorldEngine public endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByLabelText("高层方向 / 外部世界趋势")).toHaveValue("让市场附近的天气逐渐转晴");
  });
});
