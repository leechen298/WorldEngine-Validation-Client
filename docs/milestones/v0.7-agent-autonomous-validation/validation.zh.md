# v0.7 Validation Plan

状态：计划完成 / 待执行

## 验证目标

验证 v0.7 是否建立了可执行的 Agent 自主验证和人工验证交接能力。

## 验证范围

Codex 自主验证应覆盖：

- 文档和路由是否完整。
- `codex-autonomous-validation-master-plan.zh.md` 的前置条件是否满足。
- `cross-repo-validation-gate-matrix.zh.md` 的门禁顺序是否满足。
- WorldEngine public contract 是否满足创建世界和 handoff manifest 要求。
- 后端和前端现有测试是否通过。
- 基础 E2E / UI smoke 是否完成。
- Agent 操作日志是否完整。
- Evidence bundle 是否可下载并与操作日志关联。
- Event/diff 和 snapshot 是否能还原目标 commit point。
- Branch 是否作为独立世界线视图验证，且语义只包含命名、切换、回放和继续推进。
- 另一个 Agent 是否完成只读复核。
- 人工验证交接材料是否完整。

## 非目标

本验证不判断：

- 世界是否最终好玩。
- Agent 是否达到产品级自然行为。
- WorldEngine evaluator 是否权威通过。
- LLM provider 成本是否最终最优。

## Codex 自主验证清单

正式运行时必须按以下 runbook 执行：

```text
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
```

跨仓库门禁先按以下文档检查：

```text
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
```

必须执行：

```bash
git status --short --branch
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/manifest
curl -i http://127.0.0.1:8000/openapi.json
curl -i http://127.0.0.1:8765/health
curl -i http://127.0.0.1:8765/health/worldengine
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

如果 E2E 已实现，还必须执行 E2E 命令并保存 artifact。

## Agent 操作日志检查

检查操作日志是否记录：

- URL。
- 点击。
- 输入。
- API 请求和响应摘要。
- 截图。
- 下载文件。
- evidence bundle manifest。

任何关键步骤缺失，结论不得为 PASS。

## Agent 复核检查

第二个 Agent 必须只读检查：

- 操作日志。
- 截图。
- evidence bundle。
- validation run 文档。

复核结论只能说明是否可以进入人工验证。

## 人工验证清单

人工验证者检查：

- 会话库是否可理解。
- 运行控制台是否能说明世界状态。
- 像素画布和日志是否能互相解释。
- Agent 公开状态是否有观察价值。
- 导演引导是否保持高层方向。
- 回放和 branch 是否清楚。
- evidence bundle 是否能复盘。

## PASS / PARTIAL / BLOCKED / FAIL

- PASS：命令、E2E、日志、Agent 复核、evidence bundle 和人工交接材料全部完成；
  结论只声明“可以进入人工验证”。
- PARTIAL：测试通过但 E2E、日志、复核或人工交接不完整。
- BLOCKED：WorldEngine public contract、provider、浏览器、端口、沙箱或外部依赖阻塞。
- FAIL：测试失败、边界违规、证据泄漏、日志不可复核或 UI 误导为权威结论。

## 运行记录

Codex run 写入：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex.zh.md
```

Codex run 使用模板：

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
```

Agent 操作日志写入：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-agent-run.jsonl
```

第二 Agent 复核使用模板：

```text
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
```

人工 run 写入：

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-human.zh.md
```

人工验证使用模板：

```text
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
```
