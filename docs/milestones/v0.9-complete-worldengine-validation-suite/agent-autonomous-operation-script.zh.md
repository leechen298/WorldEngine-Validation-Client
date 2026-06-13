# Agent Autonomous Operation Script

英文镜像：`agent-autonomous-operation-script.md`。

## 目标

本文件定义 `complete-worldengine-validation-suite` 中 Agent 自主测试的具体操作脚本。

Agent 自主测试不是只运行一个 E2E 文件，也不是只调用 API。它要求 Codex Agent 或
其他自动化 Agent 以普通验证者视角操作 Validation Client Web UI，并把每一步操作、
输入、可见结果、API 结果和证据文件完整保存。

## 执行原则

- Agent 必须优先操作 Web UI。
- direct API harvest 只能用于补充 evidence，不得伪装成用户点击。
- 每个 UI 操作必须写入 `operation-log.jsonl`。
- 每个 API 请求/响应摘要必须写入 `api-log.jsonl` 和 `api-summary.json`。
- 每个阶段结束必须截图，并保存到 `screenshots/`。
- 每个阶段结束必须写入 `transcript.md`，用自然语言说明 Agent 看到什么、做了什么、
  为什么继续或停止。
- 如果某个按钮、输入框、页面或 API 不存在，不能跳过伪造 PASS；必须记录
  `blocked/missing_client_control` 或 `blocked/missing_worldengine_capability`。

## 固定输入

除非测试计划另行指定，Agent 自主测试使用以下固定输入，便于复现：

| 字段 | 值 |
| --- | --- |
| Session 名称 | `complete-suite-autonomous-<timestamp>` |
| 基础世界观 | `一个公开可观察的海港像素世界，有居民、道路、市场、天气、资源流动和日夜变化。居民需要在世界规则约束下生活、等待、休息、互动和响应外部事件。` |
| 第一段方向输入 | `让市场区域在接下来一段时间更容易出现合作、排队或资源流动相关的变化，但不要直接创造物品，不要直接改变任何 Agent 的内部记忆或目标。` |
| 第二段方向输入 | `让天气存在逐渐恶化的可能，并让世界根据位置、天气和规则自行判断是否产生外部风险。不要直接指定任何 Agent 死亡。` |
| Branch 名称 | `autonomous-branch-<timestamp>` |
| 初始运行 tick 数 | `5` |
| 生命周期运行 tick 数 | `20` |
| Agent 深度观察 tick 数 | `30` |
| Replay 目标 tick | `0` |

## Phase 1：基础功能操作脚本

| Step | 操作方式 | UI 目标 | 输入 | 必须记录 |
| --- | --- | --- | --- | --- |
| P1-01 | 打开页面 | 浏览器访问 Validation Client 根路径 | 无 | URL、页面标题、截图 |
| P1-02 | 读取连接状态 | `WorldEngine connection status` 或等价状态区域 | 无 | 可见状态、health API 摘要 |
| P1-03 | 填写 Session 名称 | `Session 名称` 输入框 | 固定 Session 名称 | 输入前后值、控件 label |
| P1-04 | 填写世界观 | `世界观` 输入框 | 固定基础世界观 | 输入文本长度、redacted 文本摘要 |
| P1-05 | 创建世界 | `创建世界` 按钮 | 点击 | click 事件、请求路径、响应状态 |
| P1-06 | 等待运行控制页 | `运行控制` heading | 无 | 页面可见 sections |
| P1-07 | 验证公开世界状态 | `公开状态摘要`、地图、world log | 无 | world id、tick、公开摘要 |
| P1-08 | 设置 tick 数 | `运行 tick 数` 输入框 | `5` | 输入值 |
| P1-09 | 运行 tick | `Run 5 ticks` 或等价按钮 | 点击 | click 事件、runtime API 摘要 |
| P1-10 | 下载基础 evidence | `下载 evidence bundle` 或阶段 evidence 按钮 | 点击 | 下载文件名、artifact index |
| P1-11 | 阶段截图 | 当前页面 | 无 | `screenshots/phase-1.png` |
| P1-12 | 阶段结论 | `result.json` phase entry | `pass/fail/blocked/not_run` | PASS 来源或 blocked taxonomy |

## Phase 2：生命周期操作脚本

| Step | 操作方式 | UI 目标 | 输入 | 必须记录 |
| --- | --- | --- | --- | --- |
| P2-01 | 设置运行 tick 数 | `运行 tick 数` 输入框 | `20` | 输入值 |
| P2-02 | 运行世界 | `Run 20 ticks` 按钮 | 点击 | tick 前后、响应状态 |
| P2-03 | 暂停 | `Pause run` 按钮 | 点击 | runtime 状态变化 |
| P2-04 | 继续 | `Resume run` 按钮 | 点击 | runtime 状态变化 |
| P2-05 | 单步 | `Single Tick` 按钮 | 点击 | tick +1 evidence |
| P2-06 | 查看事件 | `World Log` / events panel | 无 | event count、事件摘要 |
| P2-07 | 查看快照 | snapshots / replay panel | 无 | snapshot count、当前 tick |
| P2-08 | 设置 replay tick | `目标 tick` 输入框 | `0` | 输入值 |
| P2-09 | 创建分支 | `新 branch 名称` 输入框和 `从当前 commit point 创建 branch` 按钮 | 固定 Branch 名称 | branch id/name、来源 tick |
| P2-10 | 提交第一段方向 | `高层方向 / 外部世界趋势` 输入框和 `提交引导` 按钮 | 第一段方向输入 | direction id、classification、accepted/blocked |
| P2-11 | 提交第二段方向 | 同上 | 第二段方向输入 | 不允许直接写 Agent internal state |
| P2-12 | 下载 lifecycle evidence | lifecycle / checker handoff 下载按钮 | 点击 | artifact index、coverage matrix |
| P2-13 | 阶段截图 | 当前页面 | 无 | `screenshots/phase-2.png` |
| P2-14 | 阶段结论 | `result.json` phase entry | `pass/fail/blocked/not_run` | PASS 来源或 blocked taxonomy |

## Phase 3：Agent 深度操作脚本

| Step | 操作方式 | UI 目标 | 输入 | 必须记录 |
| --- | --- | --- | --- | --- |
| P3-01 | 打开 Agent 面板 | `Agent Life Log` / Agent public state panel | 无 | Agent 列表、公开状态摘要 |
| P3-02 | 读取 Agent public state | Agent detail / public state area | 无 | agent id、tick、公开状态 |
| P3-03 | 触发 Agent step | `Agent step` / `Observe` / 等价按钮 | 点击 | observe/action/wait/rest 结果 |
| P3-04 | 运行观察 tick | `运行 tick 数` + run button | `30` | 多轮 tick、Agent 状态变化 |
| P3-05 | 记录合法无意图状态 | Agent intent/status area | 无 | intent/action/wait/rest 之一 |
| P3-06 | 查看 memory summary | `Memory Summary` / continuity panel | 无 | public memory summary、禁止 private memory |
| P3-07 | 执行 consolidation | `Consolidate` / rest consolidation control | 点击；若无控件则 blocked | consolidation id/status |
| P3-08 | 运行 narrative projection | `Narrative Projection` control | 点击；输入可为空 | projection 摘要，确认不写 canonical world |
| P3-09 | 运行 diagnostic dialogue | `Diagnostic Dialogue` control | 输入：`请用外部观察者视角说明这个世界是否在持续运行，Agent 是否表现出连续生活迹象。` | diagnostic 摘要，确认不写 Agent memory |
| P3-10 | 下载 Agent evidence | Agent / inspection evidence 下载按钮 | 点击 | `agent-evidence.json`、`memory-continuity-summary.json` |
| P3-11 | 阶段截图 | 当前页面 | 无 | `screenshots/phase-3.png` |
| P3-12 | 阶段结论 | `result.json` phase entry | `pass/fail/blocked/not_run` | PASS 来源或 blocked taxonomy |

## Phase 4：完整自主验证 closeout 操作脚本

| Step | 操作方式 | UI/CLI 目标 | 输入 | 必须记录 |
| --- | --- | --- | --- | --- |
| P4-01 | 导出完整结果目录 | `下载完整 result directory` 或等价按钮 | 点击 | result dir 路径、文件列表 |
| P4-02 | 保存控制台日志 | Browser console / app logs | 无 | `console.log` |
| P4-03 | 保存 transcript | Agent 自身执行记录 | 无 | `transcript.md` |
| P4-04 | 运行 redaction scan | Validation Client 或 WorldEngine checker | result dir | scan command、结果 |
| P4-05 | 运行 WorldEngine checker | WorldEngine checker/scorecard | result dir | command、stdout、exit code |
| P4-06 | 第二 Agent 只读复核 | 新聊天/只读 Agent | result dir | `second-agent-review.md` |
| P4-07 | 汇总结论 | `result.json` / `scorecard-input.json` | 无 | PASS/PARTIAL/BLOCKED/FAIL |

## Stop Rules

- 如果 Agent 无法定位页面控件，必须记录 blocked，不得直接调用 API 伪装成功。
- 如果 API 调用成功但 UI 没有对应可见状态，必须记录 evidence gap。
- 如果 operation log 缺少任一执行过的 UI 操作，最终不能 PASS。
- 如果 api log 缺少任一 WorldEngine / Validation Client 请求摘要，最终不能 PASS。
- 如果截图、console log 或 transcript 缺失，Phase 4 不能 PASS。
- 如果发现 secret/raw/private marker，最终必须 FAIL。

