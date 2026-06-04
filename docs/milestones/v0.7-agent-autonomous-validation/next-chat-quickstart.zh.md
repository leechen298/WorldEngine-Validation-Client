# v0.7 后续聊天 Quickstart

英文镜像：`next-chat-quickstart.md`。

用途：给后续新聊天直接使用。本文只提供执行顺序和复制用 prompt，不替代
`autonomous-validation-runbook.zh.md`、报告模板或 review 证据。

## 当前状态

当前不能进入人工验证。

已知 blocker：

- WorldEngine 当前缺少 `/manifest`。
- WorldEngine 当前没有 Validation Client 可发现的 world creation endpoint。
- Validation Client `POST /sessions/worldengine` 当前会因为找不到 WorldEngine public
  world creation endpoint 而失败。

因此必须按下面顺序推进。

完整跨仓库门禁以此为准：

```text
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
```

## Step 1: WorldEngine contract implementation

在 WorldEngine 仓库开新聊天，使用：

```text
/goal 实现 0.8.9-external-validation-provider-and-handoff-manifest 的 public handoff manifest 和 world creation contract。

必须先读取：
- AGENTS.md
- docs/project-north-star.md
- docs/product-model.md
- docs/scope-boundaries.md
- docs/roadmap.md
- docs/iterations/README.md
- docs/iterations/AGENTS.md
- docs/iterations/v0.8/README.zh.md
- docs/iterations/v0.8/CURRENT_STATE.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/README.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/technical-design.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/validation-client-contract-handoff.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-task-plan.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-handoff-prompt.zh.md

目标：
- 实现 GET /manifest。
- 实现 OpenAPI 可发现的 POST /worlds。
- 如可行，实现 POST /worlds/{world_id}/director-guidance。
- provider readiness 只输出脱敏 public summary。
- 用 contract-readiness-checklist.zh.md 记录 WORLDENGINE_CONTRACT_READY 或阻塞原因。

不得：
- 修改 Validation Client 仓库。
- 加入具体 demo 世界内容。
- 暴露 key、private prompt、provider raw trace 或 Agent private state。
- 声明 external validation PASS 或 human validation PASS。
```

只有 WorldEngine 结论达到 `WORLDENGINE_CONTRACT_READY`，才进入 Step 2。

## Step 2: Validation Client v0.7 implementation

在 Validation Client 仓库开新聊天，使用：

```text
/goal 开发 v0.7 Agent Autonomous Validation。

必须先读取：
- AGENTS.zh.md
- docs/README.zh.md
- docs/specs/validation-client-design.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
- docs/agent-guides/routing.zh.md
- docs/agent-guides/workflow.zh.md
- docs/agent-guides/validation-workflow.zh.md
- docs/agent-guides/boundaries.zh.md

目标：
- 实现 Agent operation log JSONL。
- 实现可运行的浏览器 E2E / UI smoke 或等价自主验证路径。
- 保存 screenshots、api-summary、downloads/evidence-bundle.json。
- 让 evidence bundle 和本次 run/session 关联。
- review.zh.md 逐 task 记录命令、结果和遗留问题。

不得：
- 管理 LLM key。
- 直接调用 provider。
- 生成权威 evaluator PASS。
- 记录 private prompt、provider raw trace、Agent private memory、private goal、self_state 或 hidden_context。
```

只有 v0.7 实现完成且 review 记录通过，才进入 Step 3。

## Step 3: Codex autonomous validation

在 Validation Client 仓库开新聊天，使用：

```text
/goal 自主验证 v0.7。

必须先读取：
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/agent-guides/validation-workflow.zh.md
- /Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md

按 autonomous-validation-runbook.zh.md 执行：
- 启动 WorldEngine、Validation Client API、Validation Client Web。
- 做 public contract preflight。
- 运行测试和构建。
- 用浏览器完成完整 UI flow。
- 产出 validation-runs/YYYY-MM-DD-codex/agent-run.jsonl。
- 产出 validation-runs/YYYY-MM-DD-codex/codex.zh.md。
- 产出 screenshots/、api-summary.json、downloads/evidence-bundle.json。

结论只能是：
- PASS_READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL

不得声明人工验证通过。
```

只有 Codex 结论为 `PASS_READY_FOR_HUMAN_VALIDATION`，才进入 Step 4。

## Step 4: Second Agent read-only review

开新聊天或使用另一个 Agent，使用：

```text
/goal 复核 v0.7 Codex 自主验证记录。

只读输入：
- 最近一次 validation-runs/YYYY-MM-DD-codex/codex.zh.md
- 最近一次 validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
- 最近一次 validation-runs/YYYY-MM-DD-codex/api-summary.json
- 最近一次 validation-runs/YYYY-MM-DD-codex/screenshots/
- 最近一次 validation-runs/YYYY-MM-DD-codex/downloads/evidence-bundle.json
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md

只读复核：
- Codex 是否按 runbook 操作。
- operation log 是否覆盖关键步骤。
- screenshots 是否覆盖关键界面。
- evidence bundle 是否匹配 run/session。
- redaction scan 是否 clean。
- Codex 是否没有声明 human pass。

输出：
- validation-runs/YYYY-MM-DD-agent-review.zh.md

结论只能是：
- READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL
```

只有第二 Agent 结论为 `READY_FOR_HUMAN_VALIDATION`，才进入 Step 5。

## Step 5: Human validation

人工验证时使用：

```text
/goal 人工验证 v0.7。

必须先读取：
- 最近一次 Codex 自主验证 run。
- 最近一次第二 Agent 复核报告。
- screenshots/
- downloads/evidence-bundle.json
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md

不要重复命令测试。
只判断：
- 世界是否可观察。
- 像素画布、事件日志、公开状态是否能互相解释。
- Agent 公开状态是否像自然生活。
- 导演引导是否保持高层方向。
- replay 和 branch 是否像世界线。
- evidence bundle 是否足够复盘。

输出：
- validation-runs/YYYY-MM-DD-human.zh.md

结论只能是：
- HUMAN_PASS
- HUMAN_PARTIAL
- HUMAN_FAIL
```

只有人类写出 `HUMAN_PASS`，才可以说人工验证通过。
