# AGENTS.zh.md

面向 Codex 和其他 AI 编码代理的仓库工作指南。

英文镜像：`AGENTS.md`。

## 项目角色

`WorldEngine-Validation-Client` 是 WorldEngine 的外部验证与观察客户端。它是
独立于 WorldEngine 的仓库，不得成为 WorldEngine 子模块、私有测试夹具或实
现后门。

客户端只能通过公开接口与 WorldEngine 通信：

- `WORLDENGINE_API_BASE`
- 公开 HTTP API
- 公开 schema、manifest 和 OpenAPI 描述
- 公开 event、state、timeline 和 evaluator 输出

## 必读文档

在规划、实现、审核或完成 milestone 工作前，必须读取：

1. `docs/README.zh.md`
2. `docs/roadmap.zh.md`
3. `docs/specs/validation-client-design.zh.md`
4. active milestone 的 `README.zh.md`
5. active milestone 的 `plan.zh.md`
6. active milestone 的 `implementation-task-plan.zh.md`，如果该文件存在
7. active milestone 的 `cross-repo-validation-gate-matrix.zh.md`，如果该文件存在
8. active milestone 的 `planning-readiness-checklist.zh.md`，如果该文件存在
9. active milestone 的 `review.zh.md`
10. `docs/adr/` 下相关 ADR
11. `docs/agent-guides/routing.zh.md`
12. `docs/agent-guides/workflow.zh.md`
13. `docs/agent-guides/boundaries.zh.md`

如果请求是自主验证、Agent 验证或人工验证，还必须读取：

14. active milestone 的 `validation.zh.md`
15. `docs/agent-guides/validation-workflow.zh.md`
16. active milestone 的 `autonomous-validation-runbook.zh.md`，如果该文件存在
17. active milestone 的 `codex-run-report-template.zh.md`，如果该文件存在
18. active milestone 的 `agent-review-template.zh.md`，如果该文件存在
19. active milestone 的 `human-validation-template.zh.md`，如果该文件存在

如果请求是后续聊天交接、下一步、handoff、quickstart 或复制 `/goal` prompt，
还必须读取：

20. active milestone 的 `planning-readiness-checklist.zh.md`，如果该文件存在
21. active milestone 的 `next-chat-quickstart.zh.md`，如果该文件存在

完整 WorldEngine 验证套件的 active milestone 是：

```text
docs/milestones/v0.9-complete-worldengine-validation-suite/
```

## 简短路由

| 用户请求 | 路由 | 主要指南 |
| --- | --- | --- |
| 开发 / 实现 / 继续 vX.Y | `docs/milestones/vX.Y-*/` | `docs/agent-guides/routing.zh.md` |
| 规划 / 生成文档 / 准备 vX.Y | 创建或更新 `docs/milestones/vX.Y-*/` | `docs/agent-guides/routing.zh.md` |
| 审核 / review / 检查 vX.Y | 匹配 milestone 加当前 git diff | `docs/agent-guides/workflow.zh.md` |
| 修改技术栈或架构决策 | `docs/adr/` | `docs/agent-guides/workflow.zh.md` |
| 修改产品边界或总体设计 | `docs/specs/validation-client-design.zh.md` | `docs/agent-guides/boundaries.zh.md` |
| 自主验证 / Agent 验证 vX.Y | 匹配 milestone 加 `validation.zh.md` | `docs/agent-guides/validation-workflow.zh.md` |
| 人工验证 vX.Y | 匹配 milestone、最近 Codex run 和 `validation.zh.md` | `docs/agent-guides/validation-workflow.zh.md` |

触发词只负责路由。它不授权跳过 milestone 文档、任务顺序、验证、review 记录
或 task 级提交。

## 不可协商的执行规则

详细规则在 `docs/agent-guides/workflow.zh.md`。简版如下：

- 严格按 `plan.zh.md` 的 task 顺序执行 milestone 工作。
- 一次只处理一个编号 task。
- 当前 task 未实现、未验证、未写入 `review.zh.md`、未提交前，不得开始下一
  个 task。
- 每个编号 task 必须有独立提交，除非用户在实现前明确批准合并 task。
- 相关实现文件仍有未暂存或未提交改动时，不得标记 milestone 完成。
- 只有当前工作会话实际运行过的检查，才可以声明通过。
- 以 `-local` 结尾的分支只作为本地工作分支。不得 push 任何 `*-local`
  分支；需要共享时，先把 patch 等价提交合入或重放到对应的非 local 目标分
  支，且只有在用户明确要求 push 时才推送该目标分支。

## 边界规则

详细边界在 `docs/agent-guides/boundaries.zh.md`。

验证客户端不得管理 LLM key、直接调用 LLM provider、生成权威世界事实、导入
WorldEngine 源码或修改 Agent 内部状态。Timeline branch 按代码分支建模：
可重建 tick 或 event point 是 commit point；branch 是命名世界线，只表达命名、
切换、回放和继续推进。
