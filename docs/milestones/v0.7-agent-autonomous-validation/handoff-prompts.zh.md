# v0.7 Handoff Prompts

本文提供后续聊天可直接使用的 `/goal` prompts。使用前仍需让新聊天读取本目录
的 `README.zh.md`、`validation.zh.md` 和
`implementation-task-plan.zh.md`、
`codex-autonomous-validation-master-plan.zh.md`、
`planning-readiness-checklist.zh.md`。

更短的复制入口见：

```text
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```

完整跨仓库门禁见：

```text
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
```

## 0. 当前状态短结论

当前不能进入人工验证。

实测 blocker：

- WorldEngine 可启动，`/health` 与 `/openapi.json` 可访问。
- WorldEngine 当前缺少 `/manifest`。
- WorldEngine OpenAPI 当前没有 Validation Client 可发现的 world creation endpoint。
- Validation Client `POST /sessions/worldengine` 当前返回 502：
  `WorldEngine public world creation endpoint not found`。

因此执行顺序必须是：

1. 先修 WorldEngine public contract。
2. 再开发 Validation Client v0.7 operation log / autonomous validation。
3. 再运行 Codex 自主验证。
4. 再运行第二 Agent 只读复核。
5. 最后进入人工验证。

## 1. WorldEngine 开发聊天 Prompt

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
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/external-validation-gate-matrix.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-handoff-prompt.zh.md

目标：
- 添加或实现 GET /manifest，返回脱敏 public readiness document。
- 添加 OpenAPI 可识别的 public world creation endpoint，优先 POST /worlds。
- world creation response 必须包含 public world_id、status、public state 和 visualization。
- 如可行，添加 POST /worlds/{world_id}/director-guidance。
- provider readiness 只能公开 provider class/readiness/credential source class/model label，不得暴露 key、private prompt 或 provider raw trace。

边界：
- 不实现 Validation Client。
- 不加入具体 demo 世界内容。
- 不把 external validator 放进 WorldEngine。
- 不暴露 key/private prompt/provider raw trace/private Agent state。
- 不重开 v0.8 final closeout；0.8.9 是 post-closeout addendum。

验证：
- cd backend && .venv/bin/python -m pytest app/tests -q
- git diff --check
- 启动 WorldEngine 后 curl /health、/manifest、/openapi.json、POST /worlds。
- 启动 Validation Client API 后确认 /health/worldengine 报告 world_creation: available。
- 确认 Validation Client POST /sessions/worldengine 成功。

完成条件：
- 记录 review.zh.md。
- 结论只能说明 WorldEngine contract ready for Validation Client autonomous validation。
- 不声明 external validation PASS 或 human validation PASS。
```

## 2. Validation Client 开发聊天 Prompt

```text
/goal 开发 v0.7 Agent Autonomous Validation。

必须先读取：
- AGENTS.zh.md
- docs/README.zh.md
- docs/specs/validation-client-design.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
- docs/agent-guides/routing.zh.md
- docs/agent-guides/workflow.zh.md
- docs/agent-guides/validation-workflow.zh.md
- docs/agent-guides/boundaries.zh.md

目标：
- 实现 Agent operation log JSONL。
- 实现浏览器 E2E / UI smoke 或等价可运行自主验证。
- 保存 screenshots、API summaries、download artifacts。
- evidence bundle 必须和本次 run/session 关联。
- 提供 Codex run report 模板、Agent review report 模板、human validation handoff 模板。

边界：
- 客户端不管理 LLM key。
- 客户端不直接调用 provider。
- 客户端不生成权威 evaluator PASS。
- 不记录 private prompt、provider raw trace、Agent private memory、private goal、self_state 或 hidden_context。

验证：
- pnpm run test
- pnpm run build
- git diff --check
- 敏感词扫描必须分类并记录。
- 如果新增 Playwright，必须运行 E2E 并保存 artifacts。

完成条件：
- review.zh.md 记录每个 task、命令、结果、未解决问题。
- 不能声称人工验证通过。
```

## 3. Codex 自主验证聊天 Prompt

```text
/goal 自主验证 v0.7。

必须先读取：
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/agent-guides/validation-workflow.zh.md

按 autonomous-validation-runbook.zh.md 执行。先做 preflight：
- 确认 WorldEngine /manifest 可访问。
- 确认 WorldEngine OpenAPI 暴露可发现 world creation endpoint。
- 确认 Validation Client /health/worldengine 报告 world_creation: available。
- 确认 Validation Client POST /sessions/worldengine 可成功。

然后启动：
- WorldEngine backend。
- Validation Client API。
- Validation Client Web。

用浏览器执行完整 flow：
- 打开会话库。
- 创建 WorldEngine session。
- 进入运行控制台。
- 查看像素画布、公开状态、Agent 公开状态、World Log、Agent Life Log。
- 提交高层导演引导。
- 使用 replay slider。
- 从 commit point 创建 branch。
- 下载 evidence bundle。

必须产出：
- validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
- validation-runs/YYYY-MM-DD-codex/codex.zh.md
- screenshots/
- downloads/evidence-bundle.json
- api-summary.json

结论只能是：
- PASS_READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL

不得声明世界体验通过，不得声明人工验证通过。
```

## 4. 第二 Agent 复核聊天 Prompt

```text
/goal 复核 v0.7 Codex 自主验证记录。

只读输入：
- 最近一次 validation-runs/YYYY-MM-DD-codex/codex.zh.md
- 最近一次 validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
- screenshots/
- downloads/evidence-bundle.json
- api-summary.json
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md

检查：
- Codex 是否按计划操作。
- operation log 是否覆盖关键步骤。
- API summary 是否能和 UI 可见状态对应。
- evidence bundle 是否匹配 session/run。
- redaction flags 和敏感词扫描是否 clean。
- Codex 结论是否只声明可以进入人工验证。

输出：
- validation-runs/YYYY-MM-DD-agent-review.zh.md

结论只能是：
- READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL

不得重新操作浏览器，不得补写未记录事实，不得替代人工体验判断。
```

## 5. 人工验证聊天 Prompt

```text
/goal 人工验证 v0.7。

必须先读取：
- 最近一次 Codex 自主验证 run。
- 最近一次第二 Agent 复核报告。
- screenshots/
- evidence-bundle.json。
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md。

不要重复命令测试。
只判断：
- 世界是否可观察。
- 像素画布、事件日志、公开状态是否能互相解释。
- Agent 公开状态是否像在自然生活。
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

## 6. 一句话顺序

```text
WorldEngine contract -> Validation Client v0.7 operation log/E2E -> Codex autonomous run -> second Agent review -> human validation
```
