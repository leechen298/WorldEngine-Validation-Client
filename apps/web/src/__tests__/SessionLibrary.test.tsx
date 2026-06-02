import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { getWorldEngineHealth } from "../api/client";
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
      errors: [],
    },
  }),
  getSessions: vi.fn().mockResolvedValue({
    sessions: [
      {
        id: "session-1",
        session_name: "Demo",
        status: "created",
        branch_count: 1,
        main_branch_id: "branch-1",
        main_commit_point_id: "cp-1",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ],
  }),
  createSession: vi.fn().mockResolvedValue({
    id: "session-2",
    session_name: "Demo",
    status: "created",
    branch_count: 1,
    main_branch_id: "branch-2",
    main_commit_point_id: "cp-2",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  }),
}));

describe("SessionLibrary", () => {
  beforeEach(() => {
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
    expect(screen.getByRole("button", { name: "创建 session" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Session 名称" })).toHaveValue("World Demo");
  });

  it("shows degraded WorldEngine status when the remote API is unreachable", async () => {
    vi.mocked(getWorldEngineHealth).mockResolvedValueOnce({
      status: "degraded",
      worldengine: {
        reachable: false,
        health: null,
        manifest: null,
        errors: ["health: connection refused"],
      },
    });

    render(<SessionLibrary onOpenSession={() => null} />);

    expect(await screen.findByText("status: degraded")).toBeInTheDocument();
    expect(screen.getByText("health: connection refused")).toBeInTheDocument();
  });
});
