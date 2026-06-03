# v0.6 Evidence Bundle

状态：文档创建完成 / 实现待开始

## 目标

在 v0.5 Director Guidance 的基础上，交付可下载、可审计、可脱敏检查的本地
session evidence bundle。该 bundle 用于让 Codex、人类评审者或后续 WorldEngine
公开评审流程复核一次验证客户端会话，而不是生成权威 evaluator 结论。

v0.6 的核心是把客户端已经保存的公开 session 元数据、event log、state diff、
snapshot、replay index、director intent、脱敏 API trace 和 WorldEngine 公开
evaluator 输出整理为稳定 bundle 结构，并提供后端导出 API 与前端下载入口。

## 范围

允许实现：

- 后端 evidence bundle schema、manifest 和内容组装。
- 后端导出 endpoint，返回可下载 JSON bundle。
- bundle 中包含 session metadata、timeline branch、commit point、event log、
  state diff、snapshot、replay index、director intent、脱敏 API trace 和可用的
  WorldEngine 公开 evaluator 输出。
- bundle manifest 中记录生成时间、bundle schema 版本、计数、警告和脱敏标志。
- 后端测试覆盖 bundle 内容、排序、计数、缺失 session、脱敏字段和越界 payload
  排除。
- 前端 typed client、store 和运行控制台 evidence panel / 下载入口。
- 前端展示 bundle metadata、计数、脱敏状态、warning 和下载错误。

禁止实现：

- 客户端 LLM API key 管理。
- 客户端直接调用 LLM provider。
- 客户端生成权威世界事实或 evaluator 结论。
- WorldEngine 私有源码、私有路径或内部 helper 依赖。
- 保存或展示 LLM key、provider secret、private prompt、private evaluator oracle
  internals、hidden context、raw private response 或非公开 WorldEngine internals。
- 直接修改 Agent 内部状态、记忆、目标、身份、关系、自我状态或行动决定。
- 把 evidence bundle 导出解释成完整自动化验收报告。
- 实时 tick streaming 或运行推进 API。

## 入口

当用户说 `开发 v0.6`、`实现 v0.6`、`继续 v0.6` 或 `/goal 开发 v0.6`，
先读取：

```text
docs/specs/validation-client-design.zh.md
docs/milestones/v0.6-evidence-bundle/README.zh.md
docs/milestones/v0.6-evidence-bundle/plan.zh.md
docs/milestones/v0.6-evidence-bundle/review.zh.md
docs/adr/0001-tech-stack.zh.md
docs/agent-guides/routing.md
docs/agent-guides/workflow.md
docs/agent-guides/boundaries.md
```

然后严格按 `plan.zh.md` 的 numbered task 顺序执行。每个 numbered task
必须实现、验证、记录到 `review.zh.md` 并提交后，才能进入下一 task。

## 当前结论

v0.6 尚未进入产品代码实现。Task 1 已建立 milestone 文档和计划边界。后续实现
应从后端 bundle schema / manifest 开始，逐步扩展到可下载 JSON bundle、前端
typed client / store、运行控制台 evidence panel，并在最后进行完整验证和 review
收口。
