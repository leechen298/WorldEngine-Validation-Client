import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { createWorldSession, getSessions, getWorldEngineHealth } from "../api/client";
import { useSessionStore } from "../store/sessionStore";
import { SessionLibrary } from "../pages/SessionLibrary";

vi.mock("../api/client", () => ({
  getHealth: vi.fn().mockResolvedValue({
    status: "ok",
    service: "worldengine-validation-client",
    worldengine_api_base: "http://127.0.0.1:8000",
    database_path: "client.sqlite3",
  }),
  getWorldEngineHealth: vi.fn().mockResolvedValue({
    status: "ok",
    worldengine: {
      reachable: true,
      health: { status: "ok" },
      manifest: { version: "0.1.0" },
      openapi: { title: "WorldEngine", version: "0.2.0", world_creation_endpoint: "/worlds" },
      capabilities: {
        manifest_available: true,
        openapi_available: true,
        world_creation: "available",
      },
      errors: [],
    },
  }),
  getSessions: vi.fn(),
  createSession: vi.fn().mockResolvedValue({
    id: "session-2",
    session_name: "Demo",
    status: "created",
    worldengine_world_id: null,
    public_world_status: null,
    initial_state_summary: null,
    visualization_payload_summary: null,
    branch_count: 1,
    main_branch_id: "branch-2",
    main_commit_point_id: "cp-2",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  }),
  createWorldSession: vi.fn().mockResolvedValue({
    id: "session-2",
    session_name: "World Demo",
    status: "created",
    worldengine_world_id: "world-2",
    public_world_status: "created",
    initial_state_summary: '{"agents":2}',
    visualization_payload_summary: '{"tiles":12}',
    branch_count: 1,
    main_branch_id: "branch-2",
    main_commit_point_id: "cp-2",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  }),
}));

describe("SessionLibrary", () => {
  const sessionListPayload = {
    sessions: [
      {
        id: "session-1",
        session_name: "Demo",
        status: "created",
        worldengine_world_id: "world-1",
        public_world_status: "created",
        initial_state_summary: "{}",
        visualization_payload_summary: "{}",
        branch_count: 1,
        main_branch_id: "branch-1",
        main_commit_point_id: "cp-1",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ],
  };

  beforeEach(() => {
    vi.mocked(getSessions).mockResolvedValue(sessionListPayload);
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      connectionStatus: null,
      lastBranches: {},
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows session list and create action", async () => {
    render(<SessionLibrary onOpenSession={() => null} />);
    expect(await screen.findByText("Demo")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "创建世界" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Session 名称" })).toHaveValue("World Demo");
    expect(screen.getByRole("textbox", { name: "世界观" })).toHaveValue("一个可观察的小型像素世界");
  });

  it("shows degraded WorldEngine status when the remote API is unreachable", async () => {
    vi.mocked(getWorldEngineHealth).mockResolvedValueOnce({
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
        errors: ["health: connection refused"],
      },
    });

    render(<SessionLibrary onOpenSession={() => null} />);

    expect(await screen.findByText("status: degraded")).toBeInTheDocument();
    expect(screen.getByText("health: connection refused")).toBeInTheDocument();
  });

  it("creates a WorldEngine session and opens it", async () => {
    const openSession = vi.fn();
    render(<SessionLibrary onOpenSession={openSession} />);

    fireEvent.change(await screen.findByRole("textbox", { name: "Session 名称" }), {
      target: { value: "Created World" },
    });
    fireEvent.change(screen.getByRole("textbox", { name: "世界观" }), {
      target: { value: "A public world prompt" },
    });
    fireEvent.click(screen.getByRole("button", { name: "创建世界" }));

    expect(await screen.findByText("Demo")).toBeInTheDocument();
    expect(createWorldSession).toHaveBeenCalledWith({
      session_name: "Created World",
      world_prompt: "A public world prompt",
    });
    expect(getSessions).toHaveBeenCalledTimes(2);
    expect(openSession).toHaveBeenCalledWith("session-2");
  });

  it("shows a readable error when world creation fails", async () => {
    vi.mocked(createWorldSession).mockRejectedValueOnce(new Error("WorldEngine public world creation endpoint not found"));
    render(<SessionLibrary onOpenSession={() => null} />);

    fireEvent.click(await screen.findByRole("button", { name: "创建世界" }));

    expect(await screen.findByText("WorldEngine public world creation endpoint not found")).toBeInTheDocument();
  });
});
