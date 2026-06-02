import { FormEvent, useEffect, useState } from "react";
import { PixelWorldCanvas } from "../components/PixelWorldCanvas";
import { TimelineBranchList } from "../components/TimelineBranchList";
import { useSessionStore } from "../store/sessionStore";

interface RuntimeConsoleProps {
  sessionId: string;
  onBack: () => void;
}

export function RuntimeConsole({ sessionId, onBack }: RuntimeConsoleProps) {
  const [command, setCommand] = useState("让世界偏向和平互动");
  const { error, loadBranches, lastBranches } = useSessionStore();
  const [runtimeState, setRuntimeState] = useState<"running" | "paused">("paused");
  const branches = lastBranches[sessionId] || [];

  useEffect(() => {
    loadBranches(sessionId);
  }, [loadBranches, sessionId]);

  const submitDirectorCommand = (event: FormEvent) => {
    event.preventDefault();
    setCommand("");
  };

  return (
    <section>
      <div className="status-row" style={{ marginBottom: 12 }}>
        <button type="button" onClick={onBack}>
          返回会话库
        </button>
        <button type="button" onClick={() => setRuntimeState("running")}>
          Run
        </button>
        <button type="button" onClick={() => setRuntimeState("paused")}>
          Pause
        </button>
        <button type="button" onClick={() => void 0}>
          Single Tick
        </button>
        <span>状态：{runtimeState}</span>
      </div>

      <div className="runtime-grid">
        <section className="page-card control-column">
          <h3>运行控制</h3>
          <form onSubmit={submitDirectorCommand}>
            <label htmlFor="director-command">导演引导</label>
            <input id="director-command" value={command} onChange={(event) => setCommand(event.target.value)} />
            <button type="submit" style={{ marginTop: 8 }}>
              发送
            </button>
          </form>
        </section>

        <PixelWorldCanvas />

        <section>
          {error ? <p className="error-text">分支加载失败：{error}</p> : null}
          <TimelineBranchList branches={branches} />
          <section className="page-card">
            <h3>事件日志占位</h3>
            <p>待接入 WorldEngine event stream。</p>
          </section>
        </section>
      </div>
    </section>
  );
}
