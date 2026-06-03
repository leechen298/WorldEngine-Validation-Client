# v0.5 Director Guidance

状态：实现完成 / 验证通过

## 目标

在 v0.4 的 Replay And Branching 基础上，支持高层自然语言导演引导的本地提交、
状态观察和公开结果记录。v0.5 的核心是让用户可以在运行控制台中把高层方向
提交给 WorldEngine 公开 API，并在客户端侧看到 `pending`、`accepted`、`applied`
或 `rejected` 等状态。

导演引导只表达外部世界环境、事件趋势或氛围方向，不直接修改 Agent 内心、记忆、
目标、身份、自我状态、关系或行动决定。

## 范围

允许实现：

- 后端记录 director intent 的本地模型、状态和公开摘要。
- 后端通过 WorldEngine 公开 API 提交导演引导；没有公开 endpoint 时记录为本地
  `pending`，并返回可读 degraded 状态。
- 后端暴露 director intent 创建、列表和状态更新相关的本地 API。
- 后端保存脱敏 API trace，且不得保存 LLM key、provider secret、私有 prompt 或
  WorldEngine 私有 internals。
- 前端 typed client、Zustand store 和运行控制台支持导演引导提交、状态列表和错误
  展示。
- 前端将导演引导状态与当前 branch / tick 关联展示，便于后续 evidence bundle 导出。

禁止实现：

- 客户端 LLM API key 管理。
- 客户端直接调用 LLM provider。
- 客户端生成权威世界事实。
- WorldEngine 私有源码、私有路径或内部 helper 依赖。
- 直接修改 Agent 内部状态、记忆、目标、身份、关系、自我状态或行为决定。
- 把导演引导解释成玩家角色控制、物品放置或手动事件注入。
- 私有 Agent 内部状态、隐藏推理、私有 prompt 或 evaluator oracle internals 展示。
- 实时 tick streaming。
- 完整 evidence bundle 导出。

## 入口

当用户说 `开发 v0.5`、`实现 v0.5`、`继续 v0.5` 或 `/goal 开发 v0.5`，
先读取：

```text
docs/specs/validation-client-design.zh.md
docs/milestones/v0.5-director-guidance/README.zh.md
docs/milestones/v0.5-director-guidance/plan.zh.md
docs/milestones/v0.5-director-guidance/review.zh.md
docs/adr/0001-tech-stack.zh.md
docs/agent-guides/routing.md
docs/agent-guides/workflow.md
docs/agent-guides/boundaries.md
```

然后严格按 `plan.zh.md` 的 numbered task 顺序执行。每个 numbered task
必须实现、验证、记录到 `review.zh.md` 并提交后，才能进入下一 task。

## 当前结论

v0.5 已完成基础 Director Guidance：后端提供 director intent 本地 API，并在
session 绑定 `worldengine_world_id` 且 WorldEngine public OpenAPI 暴露 director
guidance endpoint 时提交高层导演引导；前端运行控制台支持高层方向 / 外部世界
趋势提交、状态列表、公开解释、applied event id 和失败错误展示。

后续范围仍是实时 tick streaming、运行推进 API 和完整 evidence bundle 导出。
