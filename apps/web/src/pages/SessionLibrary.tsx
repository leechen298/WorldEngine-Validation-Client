import { FormEvent, useEffect, useState } from "react";

import { useSessionStore } from "../store/sessionStore";
import { ConnectionStatus } from "../components/ConnectionStatus";

interface SessionLibraryProps {
  onOpenSession: (sessionId: string) => void;
}

export function SessionLibrary({ onOpenSession }: SessionLibraryProps) {
  const {
    sessions,
    isLoading,
    error,
    connectionStatus,
    loadSessions,
    loadHealth,
    createWorldEngineSession,
  } = useSessionStore();
  const [sessionName, setSessionName] = useState("World Demo");
  const [worldPrompt, setWorldPrompt] = useState("一个可观察的小型像素世界");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadHealth();
    loadSessions();
  }, [loadHealth, loadSessions]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!sessionName.trim() || !worldPrompt.trim()) return;
    setCreating(true);
    try {
      const created = await createWorldEngineSession(sessionName.trim(), worldPrompt.trim());
      onOpenSession(created.id);
    } catch (_error) {
      // 统一通过 store 的全局 error 状态展示，不在页面重复抛错
      return;
    } finally {
      setCreating(false);
    }
  };

  return (
    <section>
      <ConnectionStatus
        status={connectionStatus?.status || (error ? "error" : isLoading ? "loading" : "ok")}
        worldengineBase={connectionStatus?.worldengineApiBase}
        healthText={connectionStatus?.healthText || error || ""}
      />

      <section className="page-card">
        <h2>会话库</h2>
        <form onSubmit={onSubmit}>
          <div className="input-stack">
            <label htmlFor="session-name">Session 名称</label>
            <input id="session-name" value={sessionName} onChange={(event) => setSessionName(event.target.value)} />
            <label htmlFor="world-prompt">世界观</label>
            <textarea
              id="world-prompt"
              value={worldPrompt}
              onChange={(event) => setWorldPrompt(event.target.value)}
              rows={4}
            />
            <button type="submit" disabled={creating}>
              创建世界
            </button>
          </div>
        </form>

        {sessions.length === 0 ? (
          <p>还没有本地会话，点击“创建世界”。</p>
        ) : (
          <ul className="session-list">
            {sessions.map((session) => (
              <li key={session.id}>
                <button className="session-item session-button" type="button" onClick={() => onOpenSession(session.id)}>
                  <strong>{session.session_name}</strong>
                  <span>分支：{session.branch_count}</span>
                  <span>状态：{session.status}</span>
                  {session.worldengine_world_id ? <span>WorldEngine：{session.worldengine_world_id}</span> : null}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </section>
  );
}
