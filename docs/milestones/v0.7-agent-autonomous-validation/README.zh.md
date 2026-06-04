# v0.7 Agent Autonomous Validation

状态：计划完成 / 待实现

## 目标

v0.7 建立验证客户端自己的 Agent 自主验证工作流：让 Codex 或未来 OpenClaw 等
Agent 以人的视角操作完整客户端，生成足够细的操作日志和证据包，再由另一个
Agent 独立复核，最后把证据交给人类做体验判断。

v0.7 不把验证客户端变成 WorldEngine evaluator，也不让客户端管理 LLM provider
或 API key。WorldEngine 仍负责 LLM provider、世界生成、Agent 行为、运行推进和
公开 evaluator 输出。

## 范围

允许实现或规划：

- 基础 E2E / UI smoke 验证方案。
- Agent 自主测试流程。
- Agent 操作日志格式，细到点击按钮、输入内容、API 请求、响应摘要、截图和下载文件。
- Agent 复核流程，由另一个 Agent 只读审查上一轮操作日志和 evidence bundle。
- 人工验证交接清单。
- validation run 记录目录和报告模板。
- Codex run、第二 Agent 复核和人工验证的可填写模板。
- Codex 自主验证执行 runbook。
- 后续聊天 quickstart。
- Codex 自主验证到人工验证的完整阶段计划。
- 后续 WorldEngine / Validation Client / Codex / Agent / 人工验证聊天的 handoff prompts。
- WorldEngine LLM provider 前置评估文档，明确 Kimi Code subscription、Kimi
  Platform / Moonshot API、DeepSeek pay-as-you-go 的角色和风险。

## 非目标

v0.7 不做：

- 客户端 LLM key 管理。
- 客户端直接调用 LLM provider。
- WorldEngine LLM provider 运行代码实现。
- 客户端生成权威 evaluator 结论。
- 具体世界内容、私有 oracle、私有 prompt 或 Agent 内部状态验证。
- 玩家投放物品、玩家进入世界、玩家直接触发具体事件。
- 长时间真实世界演化质量验收。
- 人工验证结论自动化。

## 职责边界

### WorldEngine

WorldEngine 负责：

- 管理 LLM provider 和 API key。
- 暴露 public health、manifest、OpenAPI、world creation、runtime view、
  director guidance、evaluator outputs 和 redacted evidence。
- 生成世界、推进世界、执行 Agent 行为。

### Validation Client

验证客户端负责：

- 通过公开接口调用 WorldEngine。
- 记录用户视角的操作过程。
- 保存公开状态、脱敏 trace、evidence bundle 和 validation run 记录。
- 帮 Codex / Agent / 人类复盘验证过程。

### Agent

操作 Agent 负责：

- 像人一样操作 Web 客户端。
- 记录每一步操作和可见结果。
- 下载或引用 evidence bundle。

复核 Agent 负责：

- 只读审查操作日志。
- 判断证据是否支持进入人工验证。
- 标记缺口、风险和 blocker。

### 人类

人类负责最终体验判断：

- 世界是否可观察。
- Agent 行为是否自然。
- 导演引导是否保持边界。
- 回放和 branch 是否能被理解为世界线。
- 证据是否足够复盘。

## 入口

当用户说 `开发 v0.7`、`实现 v0.7`、`继续 v0.7`、`自主验证 v0.7` 或
`人工验证 v0.7`，先读取：

```text
docs/specs/validation-client-design.zh.md
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
docs/milestones/v0.7-agent-autonomous-validation/review.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
docs/agent-guides/routing.zh.md
docs/agent-guides/workflow.zh.md
docs/agent-guides/validation-workflow.zh.md
docs/agent-guides/boundaries.zh.md
```

## 完整计划入口

后续实现细化任务：

```text
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.md
```

完整阶段计划：

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.md
```

该文档定义：

- WorldEngine public contract 前置条件。
- Validation Client operation log 要求。
- Codex 浏览器自主验证 flow。
- 第二 Agent 只读复核。
- 人工验证交接。
- 后续聊天建议 prompt。

跨仓库门禁矩阵定义：

- WorldEngine contract readiness。
- Validation Client v0.7 implementation readiness。
- Codex autonomous validation。
- 第二 Agent read-only review。
- human validation。
- 每关 evidence、结论枚举和 stop rules。

Planning readiness checklist 定义：

- 当前计划结论 `PLAN_READY`。
- 当前唯一允许的下一步。
- 尚未完成的实现、Codex run、Agent review 和人工验证。
- 后续聊天 stop rules。

Handoff status 定义：

- 当前状态 `PLAN_READY / WAITING_FOR_WORLDENGINE_GATE_1`。
- 当前 blocker。
- 后续唯一允许的 WorldEngine Gate 1 入口。
- 禁止提前进入的阶段。

后续聊天可直接使用的 prompts：

```text
docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.md
```

验证报告模板：

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.md
```

自主验证执行 runbook：

```text
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.md
```

后续聊天 quickstart：

```text
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.md
```

## 当前结论

v0.7 当前只定义计划和验证文档。实现工作必须由后续聊天按 `plan.zh.md` 的
numbered task 顺序推进。
