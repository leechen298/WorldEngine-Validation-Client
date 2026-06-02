import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { useSessionStore } from "../store/sessionStore";
import { RuntimeConsole } from "../pages/RuntimeConsole";

describe("RuntimeConsole", () => {
  it("renders runtime controls", () => {
    useSessionStore.setState({
      sessions: [],
      isLoading: false,
      error: null,
      connectionStatus: null,
      lastBranches: {},
      loadSessions: async () => {},
      loadHealth: async () => {},
      loadBranches: async () => [],
      createNewSession: async () => {
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
      createNewSession: async () => {
        throw new Error("not used");
      },
      createBranch: async () => {
        throw new Error("not used");
      },
    } as any);

    render(<RuntimeConsole sessionId="session-id" onBack={() => null} />);

    expect(await screen.findByText("分支加载失败：Request failed: 500")).toBeInTheDocument();
  });
});
