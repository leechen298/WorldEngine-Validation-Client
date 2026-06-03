import { FormEvent, useEffect, useState } from "react";
import { getSessionEvents } from "../api/client";
import type { SessionEvent } from "../api/types";
import { PixelWorldCanvas } from "../components/PixelWorldCanvas";
import { TimelineBranchList } from "../components/TimelineBranchList";
import { useSessionStore } from "../store/sessionStore";

interface RuntimeConsoleProps {
  sessionId: string;
  onBack: () => void;
}

export function RuntimeConsole({ sessionId, onBack }: RuntimeConsoleProps) {
  const [command, setCommand] = useState("让世界偏向和平互动");
  const { error, loadBranches, lastBranches, sessions } = useSessionStore();
  const [runtimeState, setRuntimeState] = useState<"running" | "paused">("paused");
  const [events, setEvents] = useState<SessionEvent[]>([]);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const branches = lastBranches[sessionId] || [];
  const session = sessions.find((item) => item.id === sessionId);
  const latestEvent = events[events.length - 1] || null;

  useEffect(() => {
    loadBranches(sessionId);
  }, [loadBranches, sessionId]);

  useEffect(() => {
    let isCurrent = true;
    getSessionEvents(sessionId)
      .then((items) => {
        if (isCurrent) {
          setEvents(items);
          setEventsError(null);
        }
      })
      .catch((loadError) => {
        if (isCurrent) {
          setEventsError((loadError as Error).message);
        }
      });
    return () => {
      isCurrent = false;
    };
  }, [sessionId]);

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
          {eventsError ? <p className="error-text">事件加载失败：{eventsError}</p> : null}
          <section className="page-card">
            <h3>公开状态摘要</h3>
            <p>WorldEngine world：{session?.worldengine_world_id || "未绑定"}</p>
            <p>公开状态：{session?.public_world_status || session?.status || "unknown"}</p>
            <p>初始状态摘要：{session?.initial_state_summary || "无"}</p>
            <p>Visualization 摘要：{session?.visualization_payload_summary || "无"}</p>
          </section>
          <TimelineBranchList branches={branches} />
          <section className="page-card">
            <h3>最新公开事件</h3>
            {latestEvent ? (
              <>
                <p>{latestEvent.event_kind}</p>
                <p>{latestEvent.payload_json}</p>
              </>
            ) : (
              <p>暂无公开事件。</p>
            )}
          </section>
        </section>
      </div>
    </section>
  );
}
