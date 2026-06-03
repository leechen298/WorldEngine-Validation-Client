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
  const {
    error,
    commitPointsBySession = {},
    createDirectorIntent = async () => null,
    createBranch,
    directorIntentErrorBySession = {},
    directorIntentSubmittingBySession = {},
    directorIntentsBySession = {},
    downloadEvidenceBundle = async () => null,
    evidenceBundleBySession = {},
    evidenceBundleErrorBySession = {},
    evidenceBundleLoadingBySession = {},
    loadBranches,
    loadCommitPoints = async () => [],
    loadDirectorIntents = async () => [],
    loadEvidenceBundle = async () => null,
    loadReplayView = async () => null,
    loadRuntimeView,
    lastBranches,
    replayErrorBySession = {},
    replayTickBySession = {},
    replayViewBySession = {},
    selectedBranchBySession = {},
    runtimeErrorBySession,
    runtimeViewBySession,
    sessions,
  } = useSessionStore();
  const [runtimeState, setRuntimeState] = useState<"running" | "paused">("paused");
  const [branchName, setBranchName] = useState("");
  const [selectedCommitPointId, setSelectedCommitPointId] = useState<string | null>(null);
  const branches = lastBranches[sessionId] || [];
  const session = sessions.find((item) => item.id === sessionId);
  const runtimeView = runtimeViewBySession[sessionId];
  const replayView = replayViewBySession[sessionId];
  const displayView = replayView || runtimeView;
  const runtimeError = runtimeErrorBySession[sessionId];
  const replayError = replayErrorBySession[sessionId];
  const directorIntentError = directorIntentErrorBySession[sessionId];
  const directorIntentSubmitting = directorIntentSubmittingBySession[sessionId] || false;
  const directorIntents = directorIntentsBySession[sessionId] || [];
  const evidenceBundle = evidenceBundleBySession[sessionId];
  const evidenceBundleError = evidenceBundleErrorBySession[sessionId];
  const evidenceBundleLoading = evidenceBundleLoadingBySession[sessionId] || false;
  const runtimeLatestEvent = displayView?.latest_event;
  const commitPoints = commitPointsBySession[sessionId] || [];
  const selectedBranchId =
    selectedBranchBySession[sessionId] ||
    session?.main_branch_id ||
    branches.find((branch) => branch.is_main)?.id ||
    branches[0]?.id ||
    "";
  const maxTick = Math.max(displayView?.tick || 0, ...commitPoints.map((item) => item.tick), 0);
  const targetTick = replayTickBySession[sessionId] ?? displayView?.tick ?? 0;
  const selectedCommitPoint =
    commitPoints.find((item) => item.id === selectedCommitPointId) ||
    commitPoints.find((item) => item.id === session?.main_commit_point_id) ||
    commitPoints[0] ||
    null;
  const evidenceCounts = evidenceBundle?.manifest.counts;
  const evidenceRedactionFlags = evidenceBundle?.manifest.redaction_flags;
  const evidenceClean =
    evidenceRedactionFlags &&
    !evidenceRedactionFlags.llm_keys_included &&
    !evidenceRedactionFlags.private_worldengine_internals_included;
  const [lastEvidenceDownload, setLastEvidenceDownload] = useState("");

  useEffect(() => {
    loadBranches(sessionId);
  }, [loadBranches, sessionId]);

  useEffect(() => {
    loadCommitPoints(sessionId);
  }, [loadCommitPoints, sessionId]);

  useEffect(() => {
    loadRuntimeView(sessionId);
  }, [loadRuntimeView, sessionId]);

  useEffect(() => {
    loadDirectorIntents(sessionId);
  }, [loadDirectorIntents, sessionId]);

  useEffect(() => {
    loadEvidenceBundle(sessionId);
  }, [loadEvidenceBundle, sessionId]);

  const submitDirectorCommand = async (event: FormEvent) => {
    event.preventDefault();
    const instructionText = command.trim();
    if (!instructionText) {
      return;
    }
    const intent = await createDirectorIntent(sessionId, {
      instruction_text: instructionText,
      branch_id: selectedBranchId || null,
      tick: targetTick,
    });
    if (intent) {
      setCommand("");
      await loadDirectorIntents(sessionId);
    }
  };

  const loadReplayAtTick = (tick: number) => {
    loadReplayView(sessionId, {
      branchId: selectedBranchId || undefined,
      tick,
    });
  };

  const selectCommitPoint = (commitPoint: (typeof commitPoints)[number]) => {
    setSelectedCommitPointId(commitPoint.id);
    loadReplayAtTick(commitPoint.tick);
  };

  const selectBranch = (branch: (typeof branches)[number]) => {
    loadReplayView(sessionId, {
      branchId: branch.id,
      tick: branch.current_tick,
    });
  };

  const submitBranchCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (!branchName.trim() || !selectedCommitPoint) {
      return;
    }
    const branch = await createBranch(sessionId, branchName.trim(), selectedCommitPoint.id);
    setBranchName("");
    await loadBranches(sessionId);
    await loadCommitPoints(sessionId);
    await loadReplayView(sessionId, {
      branchId: branch.id,
      tick: branch.current_tick,
    });
  };

  const downloadLocalEvidenceBundle = async () => {
    const download = await downloadEvidenceBundle(sessionId);
    if (!download) {
      return;
    }
    const blob = new Blob([JSON.stringify(download.bundle, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = download.filename;
    anchor.click();
    URL.revokeObjectURL(url);
    setLastEvidenceDownload(download.filename);
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
            <label htmlFor="director-command">高层方向 / 外部世界趋势</label>
            <input id="director-command" value={command} onChange={(event) => setCommand(event.target.value)} />
            <button disabled={directorIntentSubmitting} type="submit" style={{ marginTop: 8 }}>
              提交引导
            </button>
          </form>
        </section>

        <PixelWorldCanvas visualization={displayView?.visualization} />

        <section>
          {error ? <p className="error-text">分支加载失败：{error}</p> : null}
          {runtimeError ? <p className="error-text">运行视图加载失败：{runtimeError}</p> : null}
          {replayError ? <p className="error-text">回放视图加载失败：{replayError}</p> : null}
          {directorIntentError ? <p className="error-text">导演引导提交失败：{directorIntentError}</p> : null}
          {evidenceBundleError ? <p className="error-text">Evidence bundle 失败：{evidenceBundleError}</p> : null}
          <section className="page-card">
            <h3>公开状态摘要</h3>
            <p>WorldEngine world：{session?.worldengine_world_id || "未绑定"}</p>
            <p>公开状态：{session?.public_world_status || session?.status || "unknown"}</p>
            <p>初始状态摘要：{session?.initial_state_summary || "无"}</p>
            <p>Visualization 摘要：{session?.visualization_payload_summary || "无"}</p>
            {displayView ? <p className="tick-chip">Tick {displayView.tick}</p> : null}
          </section>
          <section className="page-card">
            <h3>时间线回放</h3>
            <div className="scrubber-row">
              <label htmlFor="replay-target-tick">目标 tick</label>
              <input
                id="replay-target-tick"
                max={maxTick}
                min={0}
                onChange={(event) => loadReplayAtTick(Number(event.target.value))}
                type="range"
                value={targetTick}
              />
              <span className="tick-chip">Tick {targetTick}</span>
            </div>
            <h4>Commit Points</h4>
            {commitPoints.length ? (
              <ul className="runtime-list">
                {commitPoints.map((commitPoint) => {
                  const summary = commitPoint.payload_summary || `tick ${commitPoint.tick}`;
                  return (
                    <li key={commitPoint.id}>
                      <span>Tick {commitPoint.tick}</span>
                      <strong>{summary}</strong>
                      {commitPoint.branch_names.length ? (
                        <span>{commitPoint.branch_names.map((name) => `branch ${name}`).join(" / ")}</span>
                      ) : null}
                      <button type="button" onClick={() => selectCommitPoint(commitPoint)}>
                        跳转到 tick {commitPoint.tick} {summary}
                      </button>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p>暂无 commit point。</p>
            )}
            <form className="input-stack" onSubmit={submitBranchCreate}>
              <label htmlFor="new-branch-name">新 branch 名称</label>
              <input
                id="new-branch-name"
                onChange={(event) => setBranchName(event.target.value)}
                value={branchName}
              />
              <button type="submit">从当前 commit point 创建 branch</button>
            </form>
          </section>
          <section className="page-card">
            <h3>Agent 公开状态</h3>
            {displayView?.public_agents.length ? (
              <ul className="runtime-list">
                {displayView.public_agents.map((agent) => (
                  <li key={agent.agent_id}>
                    <strong>{agent.display_name || agent.agent_id}</strong>
                    <span>{[agent.location, agent.public_status].filter(Boolean).join(" / ") || "unknown"}</span>
                    {agent.visible_action ? <span>{agent.visible_action}</span> : null}
                  </li>
                ))}
              </ul>
            ) : (
              <p>暂无 Agent 公开状态。</p>
            )}
          </section>
          <section className="page-card">
            <h3>导演引导状态</h3>
            {directorIntents.length ? (
              <ul className="runtime-list">
                {directorIntents.map((intent) => (
                  <li key={intent.id}>
                    <span>
                      branch {intent.branch_id || "main"} / Tick {intent.tick}
                    </span>
                    <strong>{intent.instruction_text}</strong>
                    <span>状态：{intent.status}</span>
                    {intent.public_explanation ? <span>{intent.public_explanation}</span> : null}
                    {intent.applied_event_id ? <span>applied event：{intent.applied_event_id}</span> : null}
                    {intent.error_message ? <span>{intent.error_message}</span> : null}
                  </li>
                ))}
              </ul>
            ) : (
              <p>暂无导演引导。</p>
            )}
          </section>
          <section className="page-card evidence-panel">
            <h3>本地会话证据包</h3>
            {evidenceBundle ? (
              <>
                <div className="evidence-counts">
                  <span>branches：{evidenceCounts?.branches ?? 0}</span>
                  <span>commit points：{evidenceCounts?.commit_points ?? 0}</span>
                  <span>events：{evidenceCounts?.events ?? 0}</span>
                  <span>snapshots：{evidenceCounts?.snapshots ?? 0}</span>
                  <span>api traces：{evidenceCounts?.api_traces ?? 0}</span>
                </div>
                <p>脱敏状态：{evidenceClean ? "clean" : "flagged"}</p>
                {evidenceBundle.manifest.warnings.length ? (
                  <ul className="runtime-list">
                    {evidenceBundle.manifest.warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                ) : null}
              </>
            ) : (
              <p>{evidenceBundleLoading ? "加载中" : "暂无 evidence bundle metadata。"}</p>
            )}
            <button disabled={evidenceBundleLoading} onClick={downloadLocalEvidenceBundle} type="button">
              下载 evidence bundle
            </button>
            {lastEvidenceDownload ? <p>已下载：{lastEvidenceDownload}</p> : null}
          </section>
          <section className="page-card event-bubble-card">
            <h3>最新事件气泡</h3>
            {runtimeLatestEvent ? (
              <div className="event-bubble">
                <span>Tick {runtimeLatestEvent.tick}</span>
                <strong>{runtimeLatestEvent.text}</strong>
              </div>
            ) : (
              <p>暂无事件气泡。</p>
            )}
          </section>
          <section className="page-card">
            <h3>World Log</h3>
            {displayView?.world_log.length ? (
              <ul className="runtime-list">
                {displayView.world_log.map((item) => (
                  <li key={item.id}>
                    <span>Tick {item.tick}</span>
                    <strong>{item.text}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p>暂无 world log。</p>
            )}
          </section>
          <section className="page-card">
            <h3>Agent Life Log</h3>
            {displayView?.agent_life_log.length ? (
              <ul className="runtime-list">
                {displayView.agent_life_log.map((item) => (
                  <li key={item.id}>
                    <span>Tick {item.tick}</span>
                    <strong>{item.text}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p>暂无 Agent life log。</p>
            )}
          </section>
          <TimelineBranchList branches={branches} onSelect={selectBranch} selectedBranchId={selectedBranchId} />
        </section>
      </div>
    </section>
  );
}
