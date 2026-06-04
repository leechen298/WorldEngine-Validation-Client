# v0.7 Planning Readiness Checklist

英文镜像：`planning-readiness-checklist.md`。

状态：PLAN_READY

用途：证明 v0.7 Codex 自主验证到人工验证的计划文档已经可交给后续聊天执行。
本文不证明 v0.7 已实现，不证明 Codex 自主验证通过，也不证明人工验证通过。

## 0. 结论

```text
PLAN_READY
```

一句话原因：

```text
Validation Client v0.7 和 WorldEngine 0.8.9 已有跨仓库门禁、实施任务、执行
runbook、报告模板和后续聊天 prompt；当前下一步是 WorldEngine Gate 1 contract
implementation。
```

## 1. 当前允许的下一步

唯一允许的下一步：

```text
在 WorldEngine 仓库实现 0.8.9 public handoff manifest 和 world creation contract。
```

不允许：

- 进入 Validation Client v0.7 实现。
- 进入 Codex 浏览器自主验证。
- 进入第二 Agent 复核。
- 进入人工验证。
- 声称 v0.7 验证通过。

原因：

- WorldEngine 当前缺少 `/manifest`。
- WorldEngine 当前没有 Validation Client 可发现的 world creation endpoint。
- Validation Client 当前不能创建 WorldEngine-backed session。

## 2. 必备文档

Validation Client 侧必须存在：

```text
README.zh.md
plan.zh.md
implementation-task-plan.zh.md
codex-autonomous-validation-master-plan.zh.md
cross-repo-validation-gate-matrix.zh.md
autonomous-validation-runbook.zh.md
next-chat-quickstart.zh.md
handoff-prompts.zh.md
codex-run-report-template.zh.md
agent-review-template.zh.md
human-validation-template.zh.md
validation.zh.md
review.zh.md
planning-readiness-checklist.zh.md
```

WorldEngine 侧必须存在：

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/README.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/technical-design.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/test-plan.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-task-plan.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/validation-client-contract-handoff.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/external-validation-gate-matrix.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-handoff-prompt.zh.md
```

## 3. 覆盖项

计划已覆盖：

- WorldEngine public contract readiness。
- LLM provider 和 API key 归 WorldEngine 控制。
- Validation Client 不直接调用 provider。
- Evaluator 结论归 WorldEngine 控制。
- Codex 以人类视角操作 Web 客户端。
- 用户操作、API 摘要、截图、下载文件和 evidence bundle 的 operation log。
- 每 tick/event 的轻量 event/diff。
- 周期 snapshot。
- 从最近 snapshot 正向应用 diff 到 commit point。
- branch 作为命名世界线、可切换视图和继续推进入口。
- 第二 Agent 只读复核。
- 人工验证只判断体验和世界可观察性。
- 自动化结论不得替代 `HUMAN_PASS`。

## 4. 未完成项

尚未完成：

- WorldEngine 0.8.9 implementation。
- Validation Client v0.7 implementation。
- Codex autonomous validation run。
- 第二 Agent read-only review。
- Human validation。
- Commit / push。

## 5. Stop Rules

后续聊天如果遇到以下任一情况，必须停止并记录非 ready 结论：

- WorldEngine 仍缺 `/manifest`。
- WorldEngine OpenAPI 仍没有可发现 world creation endpoint。
- Validation Client `POST /sessions/worldengine` 仍失败。
- 需要 Validation Client 管理 LLM key。
- 需要 Validation Client 直接调用 LLM provider。
- evidence 泄漏 key、private prompt、provider raw trace 或 Agent private state。
- operation log 无法复核用户视角操作。
- Codex 或第二 Agent 声称人工验证通过。

## 6. 推荐后续聊天

复制使用：

```text
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```

当前交接状态：

```text
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
```

第一个后续聊天必须在 WorldEngine 仓库执行：

```text
/goal 实现 0.8.9-external-validation-provider-and-handoff-manifest 的 public handoff manifest 和 world creation contract。
```

只有 WorldEngine 写出 `WORLDENGINE_CONTRACT_READY`，才进入 Validation Client v0.7
implementation。
